
"""
Scan through all files to obtain the list of unique user IDs and store the list on disk.

User IDs will be used in next step to prevent overflow of computer memory:
We cut the list of user IDs into small batches and deal with batch by batch 
"""

import csv, os, sys

# ##########get name list ##############
usernamelist = set()

## specify work directory
# data_dir = "E:/ProgramData/python/cuebiq_share_git/app-data-master/data" # no hard code
## where we store unzipped files
data_dir = str(sys.argv[1]) # parse command-line arguments that are given from command line

filedaylist = os.listdir(data_dir+'/unzipped') # get all file names in the directory where we store unzipped files
# filedaylist = [fileday for fileday in filedaylist if fileday.startswith('201911')] #you can specify the files you want to process

## scan through all data files to obtain the list of unique user IDs
for fileday in filedaylist:
    print(fileday)
    with open(data_dir + '/unzipped/' + fileday) as readfile:
        readCSV = csv.reader(readfile, delimiter='\t')
        namesINfileday = set([row[1] for row in readCSV])
    usernamelist = usernamelist.union(namesINfileday)


# Write the list of user IDs to disk as a csv file; each row gives one user ID
usernamelist = list(usernamelist)
with open(data_dir + '/usernamelist.csv', 'w') as f:
    for name in usernamelist:
        f.write(name + '\n')

