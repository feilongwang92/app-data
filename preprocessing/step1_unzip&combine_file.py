
"""
unzip and combine
cuebiq put hundreds of zipped small files in a folder of each day
the codes here unzip and combine them in one file, such that each day is in one file
Note that according to cuebiq's guide, records on one day could still appears in files of other days.
Codes in next file will address this issue.
"""


import gzip, shutil, os


filedaylist = os.listdir('E:\\cuebiq_psrc_201911\\raw')
for fileday in filedaylist:
    print(fileday)
    with open('E:\\cuebiq_psrc_201911\\unzip\\' + fileday[:8] + '.csv', 'wb') as wfd:
        for filename in os.listdir('E:\\cuebiq_psrc_201911\\raw\\' + fileday):
            with gzip.open('E:\\cuebiq_psrc_201911\\raw\\' + fileday + '\\' + filename) as fd:
                shutil.copyfileobj(fd, wfd)

