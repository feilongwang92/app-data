
"""
Env.  Anaconda2-4.0.0-Windows-x86_64; 2019.03 does not work good
gps: trace segmentation clustering
incremental clustering for common places
grid-splitting for oscillation
Cellular: incremental clustering for both stays and oscillations
Combine cellular and gps stays; do another oscillation check via incremental clustering stays
Excluding those having no stays and only having one stays during the entire study period
Improved on 04/18/2019 for efficiency
Modified and tested: 11/2019
Add comments to share with Yuanjie
"""

from __future__ import print_function


workdir = 'E:\\cuebiq_psrc_201911\\'
file2process = 'part201911_01.csv'
output2file = 'trip_identified_part201911_01.csv'



###  Important arguments  ###
# part_num = '00'            # which data part to run
user_num_in_mem = 1000  # read how many users from the data into memory; depending on your PC memory size
dur_constr = 300        # seconds
spat_constr_gps = 0.20 # Km
spat_constr_cell = 1.0#1.0  # Km
spat_cell_split = 100   # meters; for spliting gps and cellular
max_cputime_allocated2aUser = 30*60 # give up a user if processing need more than 30*60 seconds; write user 2 file

import csv, time, os,  copy, psutil, sys #, random,gzip
from multiprocessing import Pool

from multiprocessing import current_process, Lock, cpu_count
from collections import defaultdict
import shutil, glob
import func_timeout

sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from gps_traces_clustering import clusterGPS
from cellular_traces_clustering import clusterPhone
from combine_stays_phone_gps import combineGPSandPhoneStops



cpu_useno = cpu_count()#1
print('cpu number: ', cpu_useno)


def init(l):
    global lock
    lock = l


@func_timeout.func_set_timeout(max_cputime_allocated2aUser) # break if processing need more than max_cputime_allocated2aUser seconds
def process_a_user(arg):
    """
    proccess a user; # break if processing need more than 30*60 seconds
    :param arg:
    :return: user
    """
    name, user, dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, workdir = arg  # unpack arguments
    user_gps = {}
    user_cell = {}
    for d in user.keys():
        user_gps[d] = []
        user_cell[d] = []
        for trace in user[d]:
            if int(trace[5]) <= spat_cell_split:
                user_gps[d].append(trace)
            else:
                user_cell[d].append(trace)

    user_gps = clusterGPS((user_gps, dur_constr, spat_constr_gps))
    user_cell = clusterPhone((user_cell, dur_constr, spat_constr_cell))
    user = combineGPSandPhoneStops((user_gps, user_cell, dur_constr, spat_constr_gps, spat_cell_split))
    return user


def mainfunc_identify_trip_ends(arg):
    '''
    main function: try to process a user;
    write a successfully processed user;
    write down the unsuccessfully processed user for further process;
    :param arg:
    :return:
    '''
    name, user, dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, workdir = arg # unpack arguments

    user_org = copy.deepcopy(user)
    try:
        user = process_a_user(arg) ## if it takes longer than 30*60 seconds to process a name, return an error
        ## write outputs to file; file name is the name of current processor
        filenamewrite = workdir + output2file
        with lock:
            f = open(filenamewrite, 'ab') # target_filename = workdir+'trip_identified_part_'+part_num+'.csv'
            writeCSV = csv.writer(f, delimiter='\t')
            for day in sorted(user.keys()):
                if len(user[day]):
                    for trace in user[day]:
                        trace[1] = name
                        trace[6], trace[7] = round(float(trace[6]), 7), round(float(trace[7]), 7)
                        writeCSV.writerow(trace)
            f.close()
    except:
        ## record user name not processed successfully ## if fails in time, write this user to disk
        ## these users can be processed by setting a longer time threshold and using another machine
        print('user name not processed successfully: ', name)
        with lock:
            f = open(workdir + 'traces_not_processed.csv', 'ab')
            writeCSV = csv.writer(f, delimiter='\t')
            for day in sorted(user_org.keys()):
                if len(user_org[day]):
                    for trace in user_org[day]:
                        trace[1] = name
                        writeCSV.writerow(trace)
            f.close()


if __name__ == '__main__':
    """
    1. read data and the data structure is: a dictionary UserList contains users; each user is dictionary containing all days; 
       each day is list containing all traces; traces are temporally ordered (ordered in file already);
    2. utilizing parallel computing: each user is processed with an indepedent processor
    """

    # time period covered by the data
    day_list = ['19110' + str(i) if i < 10 else '1911' + str(i) for i in range(1, 31)]

    l = Lock() # parallel computing thread locker
    pool = Pool(cpu_count(), initializer=init, initargs=(l,))

    ## get ID list from file
    with open(workdir + file2process) as csvfile:
        readCSV = csv.reader(csvfile, delimiter='\t')
        usernamelist = set([row[1] for row in readCSV])  # the second colume is userID

    print(len(usernamelist))

    # read data: split usernamelist_infile into several bulks; each has user_num_in_mem=1000 users
    # Then, evey loop, process only 1000 users, otherwise, no enough memory.
    usernamebulks = []
    counti = 0
    namebulk = []
    for name in usernamelist:
        if (counti < user_num_in_mem):
            namebulk.append(name)
            counti += 1
        else:
            usernamebulks.append(namebulk)
            namebulk = []
            namebulk.append(name)
            counti = 1
    usernamebulks.append(namebulk)  # the last one which is smaller than 10000

    usernamelist = None
    print(len(usernamebulks))
    print(sum([len(bulk) for bulk in usernamebulks]))

    ## read and process traces for one bulk
    while (len(usernamebulks)):
        bulkname = usernamebulks.pop()
        print("Start processing bulk: ", len(usernamebulks) + 1,
              ' at time: ', time.strftime("%m%d-%H:%M"), ' memory: ', psutil.virtual_memory().percent)

        # data structure in memory: a dictionary of dictionary: organized by user and then by day
        # UserList = {name0: {day0:[], day1:[]...}, name1:{day0:[], day1:[]...}, ...}
        UserList = {name: defaultdict(list) for name in bulkname}  # {name:{day: [] for day in day_list},name:{}...}

        with open(workdir + file2process) as readfile:  # traces_to_be_processed
            readCSV = csv.reader(readfile, delimiter='\t')
            # next(readCSV)
            for row in readCSV:
                name = row[1]
                if name in UserList:
                    # if row[-1][:6] not in day_list or row[3]=='NaN': continue
                    if row[-1][:6] not in day_list: continue
                    ### each input row is in format: 1573773245 3dd3bc7f67 0 47.3874765 -122.2401154 26	191114161405
                    ### converted and storeed in memory with format (12 col): 1573773245 None 0 47.3874765 -122.2401154 26 -1 -1 -1 -1 -1 191114161405
                    row[1] = None
                    row.extend([-1, -1, -1, -1, -1])  # standardizing data structure; add -1 will be filled by results
                    row[6], row[11] = row[11], row[6]  # put human time to the last col
                    row[5] = int(float(row[5]))
                    # append this record to one day
                    # be careful here! the human time may be different in psrc 2017 and 19 data!
                    if int(row[-1][6:8]) < 3:  # row[-1] is humman time 191114161405: 2019-11-14-16:14
                        whichday = day_list.index(row[-1][:6]) - 1  ## effective day; go to previous day
                        if whichday < 0: continue
                        UserList[name][day_list[whichday]].append(row)
                    else:
                        UserList[name][row[-1][:6]].append(row)

        '''
        sort users and a user having more records takes a cpu core earlier
        '''
        sortednames = {}
        for name in UserList:
            for day in UserList[name]:  # debug a data issue
                i = 0
                while i < len(UserList[name][day]):
                    if '.' not in UserList[name][day][i][3] or '.' not in UserList[name][day][i][4]:
                        del UserList[name][day][i]
                    else:
                        i += 1
            sortednames[name] = sum([len(UserList[name][day]) for day in UserList[name]])  # process easy ones first
        sortednames = sorted(sortednames.items(), key=lambda kv: kv[1], reverse=True)
        sortednames = [item[0] for item in sortednames]

        print("End reading; start calculating...")

        ## parallel processing
        ## each task is to process one user's data, parameter: (name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, workdir)
        tasks = [pool.apply_async(mainfunc_identify_trip_ends, (task,)) for task in
                 [(name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, workdir)
                  for name in sortednames]]
        finishit = [t.get() for t in tasks]
        # map is not a good idea
        # pool.map(func_identify_trip_ends, [(name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell,
        #                                     spat_cell_split, outfile_workdir) for name in sortednames]) # process easy ones first

        print('End processing bulk: ', len(usernamebulks) + 1, ' memory: ', psutil.virtual_memory().percent)

    pool.close()
    pool.join()

    print ('ALL Finished! Thank you!')

