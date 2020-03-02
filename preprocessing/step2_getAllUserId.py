
"""
following unzip and combine
extract all user ids and store them
user ids will be used in next step to prevent memory overflow,
where we read in and preprocess a fraction of users each time
"""



import csv, os



# ##########get name list ##############
usernamelist = set()
filedaylist = os.listdir('E:\\cuebiq_psrc_201911\\unzip')
filedaylist = [fileday for fileday in filedaylist if fileday.startswith('201911')] #and fileday <= 'unzip20180331.csv'

for fileday in filedaylist:
    print(fileday)
    with open('E:\\cuebiq_psrc_201911\\unzip\\' + fileday) as readfile:
        readCSV = csv.reader(readfile, delimiter='\t')
        namesINfileday = set([row[1] for row in readCSV])
    usernamelist = usernamelist.union(namesINfileday)


# Write to file
usernamelist = list(usernamelist)
with open('E:\\cuebiq_psrc_201911\\unzip\\usernamelist_psrc201911_entire.csv', 'w') as f:
    for name in usernamelist:
        f.write(name + '\n')

