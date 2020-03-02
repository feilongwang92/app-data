
"""
    cut user names into small bulks
    each time, extract traces of one bulk of users, sort, remove duplicates and write to file in dir '\sort'
"""

import csv, time, os


######## sort data -- remove duplicates #######

## how many user id in total
with open('E:\\cuebiq_psrc_201911\\unzip\\usernamelist_psrc201911_entire.csv') as readfile:
    readCSV = csv.reader(readfile, delimiter='\t')
    totalnames = len([row[0] for row in readCSV])

### start of procesing sort remove_duplicates #####
namepart = 0
partsize = 5000

filedaylist = os.listdir('E:\\cuebiq_psrc_201911\\unzip')
filedaylist = [fileday for fileday in filedaylist if fileday.startswith('201911')]

while namepart <= totalnames/partsize: # split the task into totalnames/partsize tasks
    print ('Processing part: ', namepart, ' of ', totalnames/partsize)

    with open('E:\\cuebiq_psrc_201911\\unzip\\usernamelist_psrc201911_entire.csv') as readfile:
        readCSV = csv.reader(readfile, delimiter='\t')
        names = [row[0] for row in readCSV]

    bulkname = names[partsize * namepart: partsize * (namepart+1)] # names will be preprocessed in this loop

    names = None # save memory

    '''
        Take out traces belongs to users in 'bulkname', and write them in file
        'bulkname' contains a bulk of user names whose traces we want to find out
    '''
    UserList = {name: [] for name in bulkname}
    for fileday in filedaylist:
        with open('E:\\cuebiq_psrc_201911\\unzip\\' + fileday) as readfile:
            readCSV = csv.reader(readfile, delimiter='\t')
            for row in readCSV:
                if row[5] == '\N': continue
                if row[1] in UserList:  # row[1] is user id
                    ## convert to human time and overwrite the last column
                    row[6] = time.strftime("%y%m%d%H%M%S", time.gmtime(float(row[0]) + int(row[6])))
                    # not store userID save memory
                    UserList[row[1]].append([row[0], row[2], row[3], row[4], row[5], row[6]])

    ## sort in time order and remove duplicates
    for name in UserList:
        UserList[name] = sorted(UserList[name], key=lambda trace: int(trace[0])) #sort in time order
        i = 0
        while i < len(UserList[name]) - 1:
            # if times of two rows are the same, keep the row with low uncertainty
            # caution! Now row[4] is uncertainty_radius feild, not row[5]
            if UserList[name][i + 1][0] == UserList[name][i][0]:
                if int(UserList[name][i + 1][4]) < int(UserList[name][i][4]):
                    UserList[name][i] = UserList[name][i + 1][:]
                del UserList[name][i + 1]
            else:
                i += 1


    ## write to file
    filenamewrite = "E:\\cuebiq_psrc_201911\\sorted\\part201911_0" + str(namepart) + ".csv" if namepart < 10 else \
        "E:\\cuebiq_psrc_201911\\sorted\\part201911_" + str(namepart) + ".csv"

    with open(filenamewrite, 'ab') as f:
        writeCSV = csv.writer(f, delimiter='\t')
        for name in UserList.keys():
            for trace in UserList[name]:
                # put user name back
                writeCSV.writerow([trace[0], name, trace[1], trace[2], trace[3], trace[4], trace[5]])

