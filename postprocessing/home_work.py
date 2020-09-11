
'''
infer home and work location of users
updated Nov 11, 2019
'''

from __future__ import print_function
import csv, time, psutil, glob
from math import cos, asin, sqrt
from operator import itemgetter
from collections import defaultdict

import sys, os


# parse command-line arguments that are given from command line
# specify the input: a data file containing processed data
file2process = str(sys.argv[1]) # (e.g., "E:/ProgramData/python/cuebiq_share_git/app-data-master/data/processed/processed_00.csv")
batchsize = int(sys.argv[2])  # to prevent memory overflow, split data into batches; each time, read one batch of data into memory and proce (e.g., 1000 users)


def distance(lat1, lon1, lat2, lon2):
    """
    Compute geodesic distance between two locations
    :param lat1: latitude of location 1
    :param lon1: longitude of location 1
    :param lat2: latitude of location 2
    :param lon2: longitude of location 2
    :return: distance between two locations in Km
    """
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))


def find_home_locations(user, weeks):
    # refer alexander 2015 part c
    # user in form {day0:[end0,end1], day1:[end0,end2]}  191101133857
    # weeks  #number of weeks of the study period, used by a rule: at least once a week
    # get destinations
    destinationsList_home = {(trace[6], trace[7]):0 for d in user for trace in user[d]}
    # count visit freq to find home
    for d in user:
        for trace in user[d]: # human time: 0512-00:29
            t_left_h, t_left_m = int(trace[11][6:8]), int(trace[11][8:10])# stay start time
            t_right = (t_left_h * 3600 + t_left_m * 60 + int(trace[9])) % (3600 * 24)#end time; if on 2nd day %(3600*24)
            t_right_h = t_right / 3600
            if (t_left_h >= 22 or t_left_h <= 6) or (t_right_h >= 22 or t_right_h <= 6): # if intersect with 22pm-6am
                destinationsList_home[(trace[6], trace[7])] += 1

    sort_home = sorted(destinationsList_home.items(), key=itemgetter(1), reverse=True)# in form: [(location, #), ()...]
    if len(sort_home)>0 and sort_home[0][1] >= weeks: # sort_home[0] is the first most visited
        return sort_home[0][0]
    else:
        return None


def find_work_locations(arg):
    user, home = arg
    # user in form: {0:[end0,end1], 1:[end0,end2]}

    # count visit freq to find home
    destinationsList = {}
    for d in (sorted(user.keys())):
        destinationsList_d = {}
        for trace in user[d]:
            if (trace[6], trace[7]) in [home]: continue ### exclude home !!
            t_left_h, t_left_m = int(trace[11][6:8]), int(trace[11][8:10])  # stay start time
            t_right = (t_left_h * 3600 + t_left_m * 60 + int(trace[9])) % (3600 * 24)  # end time; if on 2nd day %(3600*24)
            t_right_h, t_right_m = t_right / 3600, t_right % 3600 / 60
            if (t_left_h >= 9 and t_left_h < 16) or (t_right_h >= 9 and t_right_h < 16):
                if (trace[6], trace[7]) not in destinationsList:
                    destinationsList[(trace[6], trace[7])] = 0
                if (trace[6], trace[7]) not in destinationsList_d:
                    destinationsList_d[(trace[6], trace[7])] = 0
                if t_left_h >= 9 and t_right_h < 16:
                    duration2add= int(trace[9])
                elif t_right_h >= 9:
                    duration2add= (int(trace[9]) - 3600 * (9 - 1 - t_left_h) - 60 * (60 - t_left_m))
                elif t_left_h < 16:
                    if t_right_h >= 16:
                        duration2add= (int(trace[9]) - 3600 * (t_right_h - 16) - 60 * t_right_m)
                    else:  ##mid night
                        duration2add= (int(trace[9]) - 3600 * (t_right_h + 24 - 16) - 60 * t_right_m)
                destinationsList_d[(trace[6], trace[7])] += duration2add

        if len(destinationsList_d) > 0: ## find out where the user stay the longest during daytime on this day and add contribution
            sort_dest = sorted(destinationsList_d.items(), key=itemgetter(1), reverse=True)  # in form: [(location, #), ()...]
            destinationsList[sort_dest[0][0]] += (destinationsList_d[sort_dest[0][0]]/60+1)

    if len(destinationsList):
        sort_dur = sorted(destinationsList.items(), key=lambda kv: kv[1], reverse=True)  # in form: [(location, #), ()...]
        return sort_dur[0][0]
    else:
        return None


if __name__ == '__main__':
    ## specify the study period: 191101-191131 means from Nov 1 to Nov 31, 2019
    day_list = ['19110' + str(i) if i < 10 else '1911' + str(i) for i in range(1, 8)]

    # ## get time period covered by the data and user ID from file
    # day_list = set() # time period covered by the data
    # with open(file2process) as csvfile:
    #     csvfile.next()
    #     readCSV = csv.reader(csvfile, delimiter='\t')
    #     for row in readCSV:
    #         day_list.add(row[-1][:6])  # the last colume is humantime, in format 200506082035
    # day_list = sorted(list(day_list))

    day_list = {day:i for i, day in enumerate(day_list)}  # convert string day to int day: 191101->0

    '''
        read data: get username list, split usernamelist into several batches; each has user_num_in_mem=1000 users
        Then, evey loop, process only a batch of users, otherwise, PC may have no enough memory.
    '''
    with open(file2process) as csvfile:
        readCSV = csv.reader(csvfile, delimiter='\t')
        # next(readCSV) # skip the first line if it is a header line
        usernamelist = list(set([row[1] for row in readCSV]))

    # split into user IDs into batches
    def divide_batchs(usernamelist, n):
        for i in range(0, len(usernamelist), n):  # looping till length usernamelist
            yield usernamelist[i:i + n]

    usernamebatches = list(divide_batchs(usernamelist, batchsize))## batchsize: How many elements each batch should have

    print('number of batches to be processed', len(usernamebatches))

    while (len(usernamebatches)):  # evey loop, process only user_num_in_mem users, otherwise, no enough memory.
        bulkname = usernamebatches.pop()
        print("Start processing bulk: ", len(usernamebatches) + 1,
              ' at time: ', time.strftime("%m%d-%H:%M"), ' memory: ', psutil.virtual_memory().percent)

        """ a dictionary of dictionary: 
            UserList = {name0: {day0:[], day1:[]...}, name1:{day0:[], day1:[]...}, ...}
        """
        UserList = {name: defaultdict(list) for name in bulkname}

        with open(file2process) as readfile:
            readCSV = csv.reader(readfile, delimiter='\t')
            next(readCSV)  # skip the first line if it is a header line
            for row in readCSV:
                # 2017data: 1493613023	    40246	1	47.5520818	-122.2782114	5	47.5517786793	-122.278525341	131	3143	stay14	0430-21:30
                # 2019data: 15726614   c670905299	1	47.3594055	-122.6070031	5	47.3603264	-122.6053931	99	20451	stay10	191101133857
                if int(row[9]) < 300: continue  # take only stays not passingby locations
                name = row[1]
                if name in UserList:
                    row[1] = None
                    if row[-1][:6] in day_list:
                        UserList[name][day_list[row[-1][:6]]].append(row)
                    # if int(row[-1][6:8]) < 3:  # effective day
                    #     whichday = day_list[row[-1][:6]] - 1  # go to previous day
                    #     if whichday < 0: continue
                    #     UserList[name][whichday].append(row)
                    # else:
                    #     UserList[name][day_list[row[-1][:6]]].append(row)

        '''
            computing
        '''
        numberOfWeeks = 1 # the length of the study period; this parameter will be used to infer home locations
        homes = {}
        for name in UserList:
            result = find_home_locations(UserList[name], weeks=numberOfWeeks) ## weeks: number of weeks of the study period
            if result:
                homes[name] = result
        with open('homes_inferred.csv', 'ab') as f:
            writeCSV = csv.writer(f, delimiter='\t')
            for name in homes:
                writeCSV.writerow([name, homes[name][0], homes[name][1]])

        ##only users having a home inferred will proceed to infer workplace
        # remove your weekends
        works = {}
        for name in homes:
            result = find_work_locations((UserList[name], homes[name]))
            if result:
                works[name] = result
        with open('workplace_inferred.csv', 'ab') as f:
            writeCSV = csv.writer(f, delimiter='\t')
            for name in works:
                writeCSV.writerow([name, works[name][0], works[name][1]])

    print('End calculation.')

