
"""
    Cut the list of user names into small batches and dealt with one batch at one time.
    Each time, extract traces of one batch of users, sort them in time order, remove duplicates and write them to disk
"""

import csv, time, os, sys

## specify work directory
# data_dir = "E:/ProgramData/python/cuebiq_share_git/app-data-master/data" # no hard code
## where we store unzipped files
data_dir = str(sys.argv[1]) # parse command-line arguments that are given from command line
batchsize = int(sys.argv[2]) # how many users in one batch (e.g., 5000 users)

inputdata_dir = data_dir + '/unzipped' # the folder where we store unzipped files
outputdata_dir = data_dir + '/sorted' # the folder where we will store the sorted data

# you may need to create the output folder if you do not have it
try:
    os.mkdir(outputdata_dir)
except:
    pass # do nothing when the folder already exists

######## sort data -- remove duplicates #######

## how many user id in total
with open(data_dir + '/usernamelist.csv') as readfile:
    readCSV = csv.reader(readfile, delimiter='\t')
    totalnames = len([row[0] for row in readCSV])
print ('number of users: ', totalnames)

### start of procesing: sort in time order; remove duplicates
### to avoid the computer crashing due to runing of memory, we split user IDs into small batches and process one batch of user IDs in one loop.
whichbatch = 0
numbatches = totalnames / batchsize # total number of batches
print ('number of batches: ', numbatches)

# get file names in the directory where unzipped data are stored
filedaylist = os.listdir(inputdata_dir)
# you can specify the files you want to process if you want, using the following statement
# filedaylist = [fileday for fileday in filedaylist if fileday.startswith('201911')]

while whichbatch <= numbatches: # split the task into totalnames/batchsize tasks
    print ('Processing batch: ', whichbatch, ' of ', numbatches)

    # read user IDs from disk
    with open(data_dir + '/usernamelist.csv') as readfile:
        readCSV = csv.reader(readfile, delimiter='\t')
        names = [row[0] for row in readCSV]

    # names will be preprocessed in this loop: from "batchsize * whichbatch" to "batchsize * (whichbatch+1)"
    batchname = names[batchsize * whichbatch: min(batchsize * (whichbatch+1), totalnames)]

    names = None # save memory

    '''
        Take out traces belongs to users in a batch, and write them in file
        'whichbatch' specifies a batch of user names whose traces we want to take out and sort
    '''
    UserList = {name: [] for name in batchname}
    for fileday in filedaylist:
        with open(inputdata_dir + '/' + fileday) as readfile:
            readCSV = csv.reader(readfile, delimiter='\t')
            for row in readCSV:
                # note each row has 7 columns: unix_time user_id phone_type lat long accuracy timeZoneOffset
                # for example: 1572675161 e89cc76416105bdd94f510733e777eae02583115b03b25ae2409476bba6487e8	0	47.645264	-122.6703395	30	-25200
                if row[5] == '\N': continue # error in accuracy
                if '.' not in row[3] or '.' not in row[4]: continue  # error in lat or long
                if row[1] in UserList:  # row[1] is user id
                    ## convert to human time and overwrite the last column
                    row[6] = time.strftime("%y%m%d%H%M%S", time.gmtime(float(row[0]) + int(row[6])))
                    # to save memory, do not store userID;
                    # then, records in list are: unix_time phone_type lat long accuracy humanTime
                    UserList[row[1]].append([row[0], row[2], row[3], row[4], row[5], row[6]])

    ## sort in time order and remove duplicates
    for name in UserList:
        UserList[name] = sorted(UserList[name], key=lambda trace: int(trace[0])) #sort in time order
        i = 0
        while i < len(UserList[name]) - 1:
            # if unix times of two rows are the same, keep the row with low location uncertainty
            # caution! Now row[4] is uncertainty_radius feild, not row[5]
            if UserList[name][i + 1][0] == UserList[name][i][0]: # unix times of two rows are the same
                if int(UserList[name][i + 1][4]) < int(UserList[name][i][4]): # compare accuracy (location uncertainty)
                    UserList[name][i] = UserList[name][i + 1][:] # cope i+1 row
                del UserList[name][i + 1] # remove i+1 row
            else:
                i += 1

    ## write to file
    filenamewrite = outputdata_dir + "/sorted_0" + str(whichbatch) + ".csv" if whichbatch < 10 else \
        outputdata_dir+"/sorted_" + str(whichbatch) + ".csv"

    with open(filenamewrite, 'ab') as f:
        writeCSV = csv.writer(f, delimiter='\t')
        for name in UserList.keys(): # write user by user
            for trace in UserList[name]:
                # write a record (7 columns): unix_time user_id phone_type lat long accuracy humanTime
                # put user_id back
                writeCSV.writerow([trace[0], name, trace[1], trace[2], trace[3], trace[4], trace[5]])

    whichbatch += 1

