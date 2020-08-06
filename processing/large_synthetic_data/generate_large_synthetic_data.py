
"""
    :param numUsers2generate provides the number of users to generate and can be changed.

    # the data include numUsers2generate users, with a period one month.
    # for one day of each user, a trajectory may or may not be generated, with a probability of 0.13 (4 trajectories per user per month as found from real data)
    # if a trajectory needs to be generated, it is randomly pulled from a pool of two trajectories.
    # the two trajectories are manually created, one having 3 trips and the other one having 2 trips.
"""

import csv, copy, numpy

numUsers2generate = 2500

'''
    read two trajectories from files
'''
wkdir = "E:\\ProgramData\\python\\cuebiq_share_git\\app-data\\processing\\visual\\large_synthetic_data\\"

with open(wkdir+'inputs\\traj1.csv') as readfile: # read in one user with two trajectories
    readfile.next()
    readCSV = csv.reader(readfile, delimiter='\t')
    traj1 = [row for row in readCSV]

with open(wkdir+'inputs\\traj2.csv') as readfile: # read in one user with two trajectories
    readfile.next()
    readCSV = csv.reader(readfile, delimiter='\t')
    traj2 = [row for row in readCSV]

traj_pool = [traj1, traj2]


'''
    generate users and write to file
'''
numpy.random.seed(46)
f = open(wkdir+'LargeSyntheticData.csv', 'w')
writeCSV = csv.writer(f, delimiter='\t')
writeCSV.writerow(['Timestamp','ID','ID_Type','Latitude','Longitude','Uncerty_radius','Human_time'])## give column names to records
for userID in range(numUsers2generate): # number of users to generate
    for day in range(1,32): # 31 days in May
        if numpy.random.uniform(0,1) < 0.13: # on average, 4 trajectories per user
            traj_userID_day = copy.deepcopy(traj_pool[numpy.random.choice([0, 1])])#randomly pick up one trajectory from pool
            # modify time and userID
            for trace in traj_userID_day:
                trace[0] = str(int(trace[0]) + (day - 1) * 24 * 3600) # give unix time
                trace[1] = str(userID) # give user ID
                trace[-1] = '20050' + str(day) + trace[-1][6:] if day < 10 else '2005' + str(day) + trace[-1][6:] # give human time
                writeCSV.writerow(trace) # write to file
f.close()

# print 'Finished generating {} users'.format(numUsers2generate)

