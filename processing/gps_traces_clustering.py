"""
Trace segmentation method to clustering gps trajectory
:param arg:
:return: modified user traces
"""

import sys
import numpy as np


sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance
from incremental_clustering import cluster_incremental
from util_func import update_duration, diameterExceedCnstr



def clusterGPS(arg):
    user, dur_constr, spat_constr= arg

    for day in user.keys():
        traj = user[day]
        i = 0
        while (i<len(traj)-1):
            j = i
            flag = False
            while (int(traj[j][0])-int(traj[i][0])<dur_constr):#j=min k s.t. traj_k - traj_i >= dur
                j+=1
                if (j==len(traj)):
                    flag = True
                    break
            if flag:
                break
            if diameterExceedCnstr(traj,i,j,spat_constr):
                i += 1
            else:
                j_prime = j
                gps_set = set([(round(float(traj[m][3]),5),round(float(traj[m][4]),5)) for m in range(i,j+1)])
                for k in range(j_prime+1, len(traj),1): # #j: max k subject to Diameter(R,i,k)<=spat_constraint
                    if (round(float(traj[k][3]), 5), round(float(traj[k][4]), 5)) in gps_set:
                        j = k
                    elif not diameterExceedCnstr(traj,i,k, spat_constr):
                        j = k
                        gps_set.add((round(float(traj[k][3]), 5), round(float(traj[k][4]), 5)))
                    else:
                        break
                mean_lat, mean_long = str(np.mean([float(traj[k][3]) for k in range(i,j+1)])), \
                                      str(np.mean([float(traj[k][4]) for k in range(i,j+1)]))
                dur = str(int(traj[j][0]) - int(traj[i][0]))  # give duration
                for k in range(i, j + 1):  # give cluster center
                    traj[k][6], traj[k][7], traj[k][9] = mean_lat, mean_long, dur
                i = j+1
        user[day] = traj

    #incremental clustering
    # user = cluster_agglomerative(user)
    user = cluster_incremental(user, spat_constr, dur_constr)

    #for those not clustered; use grid
    # modify grid
    MonthGPSList = list(set([(trace[6], trace[7], trace[8]) for d in user.keys() for trace in user[d] if int(trace[9]) >= dur_constr]))
    for day in user.keys():  # modify grid
        for trace in user[day]:
            if float(trace[6]) == -1:
                found_stay = False
                for stay_i in MonthGPSList: #first check those observations belong to a gps stay or not
                    if distance(stay_i[0], stay_i[1], trace[3], trace[4]) < spat_constr:
                        trace[6], trace[7], trace[8] = stay_i[0], stay_i[1], stay_i[2]
                        found_stay = True
                        break
                if found_stay == False:
                    trace[6] = trace[3] + '000'  # in case do not have enough digits
                    trace[7] = trace[4] + '000'
                    digits = (trace[6].split('.'))[1]
                    digits = digits[:2] + str(int(digits[2]) / 2)
                    trace[6] = (trace[6].split('.'))[0] + '.' + digits
                    # trace[6] = trace[6][:5] + str(int(trace[6][5]) / 2)  # 49.950 to 49.952 220 meters
                    digits = (trace[7].split('.'))[1]
                    digits = digits[:2] + str(int(digits[2:4]) / 25)
                    trace[7] = (trace[7].split('.'))[0] + '.' + digits
                    # trace[7] = trace[7][:7] + str(int(trace[7][7:9]) / 25)  # -122.3400 to -122.3425  180 meters

    # update duration
    user = update_duration(user)
    for d in user.keys():
        for trace in user[d]:  # those trace with gps as -1,-1 (not clustered) should not assign a duration
            if float(trace[6]) == -1: trace[9] = -1
            if float(trace[9]) == 0: trace[9] = -1


    for d in user.keys():
        for trace in user[d]:
            if float(trace[9]) < dur_constr: # change back keep full trajectory: do not use center for those are not stays
                trace[6], trace[7], trace[8], trace[9] = -1, -1, -1, -1  # for no stay, do not give center

    return user