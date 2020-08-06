
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


workdir = 'E:\\ProgramData\\python\cuebiq_share_git\\app-data\\testdata\\test4ian\\'
file2process = 'anExample.csv'
output2file = 'trip_identified_anExample.csv'

## give column names to the processed records
f = open(workdir + output2file, 'wb')
f.write('unix_start_t\tuser_ID\tmark_1\torig_lat\torig_long\torig_unc\tstay_lat\tstay_long\tstay_unc\tstay_dur\tstay_ind\thuman_start_t\n')
f.close()

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

    ## split into gps traces and cellular traces
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

    user_gps = clusterGPS((user_gps, dur_constr, spat_constr_gps)) # process gps traces
    user_cell = clusterPhone((user_cell, dur_constr, spat_constr_cell)) # process cellular traces
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
                        writeCSV.writerow(trace[:6] + [trace[-1]])
                        # recover original data structure by taking out inserted 5 columns
            f.close()


if __name__ == '__main__':
    """
    1. read data and the data structure is: a dictionary UserList contains users; each user is dictionary containing all days; 
       each day is list containing all traces; traces are temporally ordered (ordered in file already);
    2. utilizing parallel computing: each user is processed with an indepedent processor
    """
    ## for parallel computing
    l = Lock() # thread locker
    pool = Pool(cpu_count(), initializer=init, initargs=(l,))


    ## get time period covered by the data and user ID from file
    day_list = set() # time period covered by the data
    usernamelist = set() # user names
    with open(workdir + file2process) as csvfile:
        csvfile.next()
        readCSV = csv.reader(csvfile, delimiter='\t')
        for row in readCSV:
            day_list.add(row[-1][:6])  # the last colume is humantime, in format 200506082035
            usernamelist.add(row[1])  # get ID list; the second colume is userID
    day_list = sorted(list(day_list))
    usernamelist = list(usernamelist)

    print('total number of users to be processed: ', len(usernamelist))

    '''
        read data: split usernamelist_infile into several chunks; each has user_num_in_mem=1000 users
        Then, evey loop, process only a chunk of users, otherwise, PC may have no enough memory.
    '''
    ## chunks from usernamelist.
    def divide_chunks(usernamelist, n):
        for i in range(0, len(usernamelist), n): # looping till length usernamelist
            yield usernamelist[i:i + n]

    ## user_num_in_mem: How many elements each chunk should have
    usernamechunks = list(divide_chunks(usernamelist, user_num_in_mem))

    print('number of chunks to be processed', len(usernamechunks))

    ## read and process traces for one bulk
    while (len(usernamechunks)):
        namechunk = usernamechunks.pop()
        print("Start processing bulk: ", len(usernamechunks) + 1, ' at time: ', time.strftime("%m%d-%H:%M"), ' memory: ', psutil.virtual_memory().percent)

        # data structure in memory: a dictionary of dictionary: organized by user and then by day
        # UserList = {name0: {day0:[], day1:[]...}, name1:{day0:[], day1:[]...}, ...}
        UserList = {name: defaultdict(list) for name in namechunk}

        with open(workdir + file2process) as readfile:
            readfile.next()
            readCSV = csv.reader(readfile, delimiter='\t')
            for row in readCSV:
                if '.' not in row[3] or '.' not in row[4]: continue # debug a data issue: not '.' in lat or long
                name = row[1]
                if name in UserList:
                    ### each input row is in format: 1573773245 3dd3bc7f67 0 47.3874765 -122.2401154 26	191114161405
                    ### append this record to its date
                    UserList[name][row[-1][:6]].append(row)

        ## convert the structure of each record before processing
        ## the original format (7 columns), for exampel, 1573773245 3dd3bc7f67 0 47.3874765 -122.2401154 26	191114161405
        ## format after conversion (12 col): 1573773245 None 0 47.3874765 -122.2401154 26 -1 -1 -1 -1 -1 191114161405
        for name in UserList:
            for day in UserList[name]:
                for row in UserList[name][day]:
                    row[1] = None  # save memory: user id is long and cost memory
                    row[5] = int(float(row[5]))  # convert uncertainty radius to integer
                    row.extend([-1, -1, -1, -1, -1])# standardizing data structure; add -1 will be filled by info of stays
                    row[6], row[-1] = row[-1], row[6]  # push human time to the last column

        print("End reading; start calculating...")

        ## parallel processing
        ## each task is to process one user's data, parameter: (name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, workdir)
        tasks = [pool.apply_async(mainfunc_identify_trip_ends, (task,)) for task in
                 [(name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, workdir)
                  for name in UserList]]
        finishit = [t.get() for t in tasks]

        print('End processing bulk: ', len(usernamechunks) + 1, ' memory: ', psutil.virtual_memory().percent)

    pool.close()
    pool.join()

    print ('ALL Finished! Thank you!')

