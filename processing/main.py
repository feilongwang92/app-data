
"""
Environment:  Anaconda2-4.0.0; the latest version 2019.03 does not work well
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
import sys, os

## specify work directory
work_dir = str(sys.argv[1]) # parse command-line arguments that are given from command line

inputdata_dir = work_dir + '/sorted' # the folder where we store preprocessed files
outputdata_dir = work_dir + '/processed' # the folder where we will store the processed data

# you may need to create the output folder if you do not have it
try:
    os.mkdir(outputdata_dir)
except:
    pass # do nothing when the folder already exists

file2process = inputdata_dir +'/'+ str(sys.argv[2]) # specify the input file: the file should be the output of the pre-processing steps
output2file = outputdata_dir +'/'+ str(sys.argv[3]) # specify where to write after the data of each user is processed

###  Important parameters for data processing; defined them as global arguments
batchsize = int(sys.argv[4])  # read how many users from the data into memory; depending on your PC memory size (e.g., 1000 users)
spat_cell_split = int(sys.argv[5])   # the threshold in meters for partitioning records into gps and cellular traces (e.g., 100 meters)
dur_constr = int(sys.argv[6])        # temporal constraint in seconds to define a stay (e.g., 300 seconds)
spat_constr_gps = float(sys.argv[7]) # spatial constraint in Km to define a gps stay (e.g., 0.2 Km)
spat_constr_cell = float(sys.argv[8])# spatial constraint in Km to define a cellular stay (e.g., 1.0 Km)


#### no hard code
# work_dir = "E:/ProgramData/python/cuebiq_share_git/app-data-master/data" # no hard code
# inputdata_dir = work_dir + '/sorted' # the folder where we store preprocessed files
# outputdata_dir = work_dir + '/processed' # the folder where we will store the processed data
# file2process = inputdata_dir+'sorted_00.csv' # specify the input file: the file should be the output of the pre-processing steps
# output2file = outputdata_dir+'processed_00.csv' # specify where to write after the data of each user is processed

# # part_num = '00'       # which data part to run
# batchsize = 1000  # read how many users from the data into memory; depending on your PC memory size
# dur_constr = 300        # temporal constraint in seconds to define a stay (e.g., 300 seconds)
# spat_constr_gps = 0.20  # spatial constraint in Km to define a gps stay (e.g., 0.2 Km)
# spat_constr_cell = 1.0  # spatial constraint in Km to define a cellular stay (e.g., 1.0 Km)
# spat_cell_split = 100   # the threshold in meters for partitioning records into gps and cellular traces
# # max_cputime_allocated2aUser = 30*60 # stop processing a user if it takes longer than 30*60 seconds; write the user to file


import csv, time,  copy, psutil #, random,gzip
from multiprocessing import Pool

from multiprocessing import current_process, Lock, cpu_count
from collections import defaultdict
import shutil, glob
#import func_timeout

## import functions from files below only run in 'run' mode, encounter error in 'console mode'
sys.path.append(os.path.dirname(os.getcwd()))
from gps_traces_clustering import clusterGPS
from cellular_traces_clustering import clusterPhone
from combine_stays_phone_gps import combineGPSandPhoneStops

cpu_useno = cpu_count() # count number of cpu cores available on the machine; it is used for multi-processing


def init(l):
    """
    standard function to define a thread locker for multi-processing use; (not my codes)
    it is used to lock output file when one of the processors is working on the file
    :param l: Lock() multi-processing locker from package multiprocessing
    :return: no return
    """
    global lock
    lock = l


#@func_timeout.func_set_timeout(max_cputime_allocated2aUser) #break if processing a user need more than max_cputime_allocated2aUser seconds
def process_a_user(arg):
    """
        process a user, following the DCI framework proposed by (Wang et al. 2019). It consists of three steps:
        (1) partitioning data,
        (2) extracting trips from each partition,
            - extracting trips from gps data
            - extracting trips from cellular data
        (3) integrating trips that are extracted from each partition.
        :param: arg
                a tuple of 7 parameters:
                    - name: id of the user to be processed
                    - user: traces (records) of the user to be processed
                    - dur_constr: temporal constraint in seconds to define a stay (e.g., 300 seconds)
                    - spat_constr_gps: spatial constraint to define a gps stay (e.g., 0.2 Km)
                    - spat_constr_cell: spatial constraint to define a cellular stay (e.g., 1.0 Km)
                    - spat_cell_split: the threshold in meters for partitioning records into gps and cellular traces
                    - output2file: the directory where to write the processed data
        :return: user (the precessed data of the input user)
    """
    name, user, dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, output2file = arg  # unpack arguments

    ## step 1: split traces of one user into gps traces and cellular traces; using threshold spat_cell_split
    user_gps = {} # store gps traces; it is a dict of lists and each list stores traces of one day
    user_cell = {} # store cellular traces; it is a dict of lists and each list stores traces of one day
    for day in user.keys():
        user_gps[day] = []
        user_cell[day] = []
        for trace in user[day]:
            if int(trace[5]) <= spat_cell_split: # if accuracy trace[5] of one record is no larger than spat_cell_split
                user_gps[day].append(trace) # the record is a gps record
            else:
                user_cell[day].append(trace) # # the record is a cellular record

    ## step 2: extracting trips from each partition
    user_gps = clusterGPS((user_gps, dur_constr, spat_constr_gps)) # process gps traces
    user_cell = clusterPhone((user_cell, dur_constr, spat_constr_cell)) # process cellular traces
    ## step 3: integrating trips that are extracted from each partition.
    user = combineGPSandPhoneStops((user_gps, user_cell, dur_constr, spat_constr_gps, spat_cell_split)) # intergrate
    return user


def mainfunc_identify_trip_ends(arg):
    '''
        main function:
            1) process a user using function "process_a_user"
            2) write the processed user to disk
        :param: arg
                a tuple of 7 parameters:
                    - name: id of the user to be processed
                    - user: traces (records) of the user to be processed
                    - dur_constr: temporal constraint in seconds to define a stay (e.g., 300 seconds)
                    - spat_constr_gps: spatial constraint to define a gps stay (e.g., 0.2 Km)
                    - spat_constr_cell: spatial constraint to define a cellular stay (e.g., 1.0 Km)
                    - spat_cell_split: the threshold in meters for partitioning records into gps and cellular traces
                    - output2file: the directory where to write the processed data
    :return: no return
    '''
    name, user, dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, output2file = arg # unpack arguments

    # user_org = copy.deepcopy(user)

    # try:
    user = process_a_user(arg)  # process a user
    ## append the processed user to output file: each record is one line in csv file

    with lock:  # since multiple processors work on the same output file, use locker to avoid writing conflict
        f = open(output2file, 'ab')
        writeCSV = csv.writer(f, delimiter='\t')
        for day in sorted(user.keys()): # write days by time order
            if len(user[day]):
                for trace in user[day]:
                    trace[1] = name # give user name (note when read data into the memory, we set user id to None to save space)
                    trace[6], trace[7] = round(float(trace[6]), 7), round(float(trace[7]), 7) #round stay to 7 digits
                    writeCSV.writerow(trace)
        f.close()

    # except: write the unsuccessfully processed user to disk for further process;
    #     ## these users can be processed by setting a longer time threshold and using another machine
    #     print('user name not processed successfully: ', name)
    #     with lock:
    #         f = open('traces_not_processed.csv', 'ab')
    #         writeCSV = csv.writer(f, delimiter='\t')
    #         for day in sorted(user_org.keys()):
    #             if len(user_org[day]):
    #                 for trace in user_org[day]:
    #                     trace[1] = name
    #                     writeCSV.writerow(trace[:6] + [trace[-1]])
    #                     # recover original data structure by taking out inserted 5 columns
    #         f.close()


if __name__ == '__main__':
    """
    1. read data and the data structure is: a dictionary 'UserList' contains users; each user is dictionary containing all days; 
       each day is list containing all traces; traces are temporally ordered (ordered in file already);
       example: UserList = {name0: {date0:[], date1:[]...}, name1:{date0:[], date1:[]...}, ...}
    2. utilizing parallel computing to process data of users in UserList: 
       each user is processed with an indepedent processor
    """
    ## initializing parallel computing using standard commands (not my invention)
    l = Lock() # thread locker; use it to lock output file when one of the processors is working on the file
    pool = Pool(cpu_count(), initializer=init, initargs=(l,)) # initialize multi-processing pool

    ## read input file to get time period covered by the data and obtain unique user ID
    day_list = set() # time period covered by the data
    usernamelist = set() # user names
    with open(file2process) as csvfile:
        # csvfile.next() # skip the first line if it is a header line
        readCSV = csv.reader(csvfile, delimiter='\t')
        for row in readCSV:
            # each record on disk contains 7 columns:
            # unix_time, user_id, phone_type, latitude, longitude, accuracy, human_time
            day_list.add(row[-1][:6])  # the last colume is humantime in format 200506082035; [:6] gets yy-mm-dd
            usernamelist.add(row[1])  # get ID list; the second colume is userID
    day_list = sorted(list(day_list))
    usernamelist = list(usernamelist)

    print('total number of users to be processed: ', len(usernamelist))

    '''
        read data: split usernamelist into several batches; each has batchsize=1000 users
        Then, evey loop, process only a batch of users; otherwise, PC may crash as out of memory.
        You can adjust the batch size according to the size of your PC memory.
    '''
    ##  usernamelist is divided into batches;
    def divide_batches(usernamelist, n):
        for i in range(0, len(usernamelist), n): # looping till length usernamelist
            yield usernamelist[i:i + n]
    # call function to divide namelist to batches
    usernamebatches = list(divide_batches(usernamelist, batchsize))## batchsize: How many elements each batch should have

    print('number of batches to be processed', len(usernamebatches))

    ## read and process traces of users in one batch
    while (len(usernamebatches)):
        namebatch = usernamebatches.pop()
        print("Start processing batch # : ", len(usernamebatches) + 1)

        # in memory, a batch of users is stored as a dictionary of dictionary: organized by user and then by day:
        # UserList = {name0: {date0:[], date1:[]...}, name1:{date0:[], date1:[]...}, ...}
        UserList = {name: defaultdict(list) for name in namebatch}

        # read traces of users in the batch from disk
        with open(file2process) as readfile:
            #readfile.next() # skip the first line if it is a header line
            readCSV = csv.reader(readfile, delimiter='\t')
            for row in readCSV:
                # each record on disk contains 7 columns: unix_time, user_id, phone_type, latitude, longitude, accuracy, human_time
                # for example: 1573773245 3dd3bc7f67 0 47.3874765 -122.2401154 26 191114161405
                # if the record belongs to a user in the batch, append it to the user and the date it belongs
                name = row[1]
                if name in UserList:
                    day = row[-1][:6]
                    UserList[name][day].append(row)

        ## prepare the structure of each record for data processing
        ## original format (7 columns, see comments above)
        ## the prepared format: each record has 12 columns, including (the the dictionary document for their meaning)
        # unix_start_t user_ID mark_1 orig_lat orig_long orig_unc stay_lat stay_long stay_unc stay_dur stay_ind human_start_t
        # for example, 1573773245 None 0 47.3874765 -122.2401154 26 -1 -1 -1 -1 -1 191114161405
        for name in UserList:
            for day in UserList[name]:
                for row in UserList[name][day]:
                    row[1] = None  # save memory: user id is so long that it consumes memory
                    row[5] = int(float(row[5]))  # convert accuracy (uncertainty radius) to integer
                    row.extend([-1, -1, -1, -1, -1])# prepare data structure; the added -1 will be filled by info of stays
                    row[6], row[-1] = row[-1], row[6]  # exchange position: push human_time to the last column

        print("End reading; start calculating...")

        ## give column names to the processed records
        f = open(output2file, 'wb')
        f.write('unix_start_t\tuser_ID\tmark_1\torig_lat\torig_long\torig_unc\tstay_lat\tstay_long\tstay_unc\tstay_dur\tstay_ind\thuman_start_t\n')
        f.close()

        # multi-processing: use pool.apply_async to process multiple tasks
        # each task is to process one user's data using function mainfunc_identify_trip_ends,
        # parameters of each task: (name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, output2file)
        tasks = [pool.apply_async(mainfunc_identify_trip_ends, (task,)) for task in
                 [(name, UserList[name], dur_constr, spat_constr_gps, spat_constr_cell, spat_cell_split, output2file)
                  for name in UserList]]
        finishit = [t.get() for t in tasks] # standard comment to start multi-processing

    pool.close() # standard commands to close pool after multi-processing
    pool.join()

    print ('ALL Finished!')

