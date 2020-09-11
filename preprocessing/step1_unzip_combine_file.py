
"""
Unzip small files and combine them.

As explained in the document, cuebiq put hundreds of zipped small files in a folder of each day;
The codes here unzip and combine them in one file; this intends to put records on one day in one sigle file.
Note that according to cuebiq's guide, records on one day could still appears in files of other days, 
which is addressed in the third step (codes in gatherTracesOfEachUser_RemoveDuplicate.py)

"""


import gzip, shutil, os, sys

## specify work directory
# work_dir = "E:/ProgramData/python/cuebiq_share_git/app-data-master/data" # no hard code
data_dir = str(sys.argv[1]) # parse command-line arguments that are given from command line

rawdata_dir = data_dir + '/raw' # the folder where the raw data are stored
output_dir = data_dir + '/unzipped' # the folder where to store your output

# you may need to create the output folder if you do not have it
try:
    os.mkdir(output_dir)
except:
    pass # do nothing when the folder already exists

filedaylist = os.listdir(rawdata_dir) # get folder names in the directory where raw data are stored
for fileday in filedaylist: # each folder gives data on one day
    print(fileday)
    with open(output_dir + '/' + fileday[:8] + '.csv', 'wb') as wfd: # for each day, open a csv file where we want to write
        for filename in os.listdir(rawdata_dir + '/' + fileday): # get file names in the folder and scan each file
            with gzip.open(rawdata_dir + '/' + fileday + '/' + filename) as fd: # upzip each file
                shutil.copyfileobj(fd, wfd) # combine the unzipped file to the csv file that we want to write
