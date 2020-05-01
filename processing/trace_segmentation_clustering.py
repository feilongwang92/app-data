"""
Trace segmentation method for clustering gps trajectory
:param arg:
:return: modified user traces
"""

import sys
import numpy as np
from itertools import combinations


sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance


def diameterExceedCnstr(traj, i, j, spat_constr):
    """
    for function cluster_traceSegmentation (defined below) use only
    purpose: check the greatest distance between any two locations with in the set traj[i:j]
            and compare the distance with constraint
    remember, computing distance() is costly and this why this function seems so complicated.
    :param traj:
    :param i:
    :param j:
    :param spat_constr:
    :return: Ture or False
    """
    loc = list(set([(round(float(traj[m][3]),5),round(float(traj[m][4]),5))  for m in range(i,j+1)]))# unique locations
    if len(loc) <= 1:
        return False
    if distance(traj[i][3],traj[i][4],traj[j][3],traj[j][4])>spat_constr: # check the first and last trace
        return True
    else:
        # guess the max distance pair; approximate distance
        pairloc = list(combinations(loc, 2))
        max_i = 0
        max_d = 0
        for i in range(len(pairloc)):
            appx_d = abs(pairloc[i][0][0] - pairloc[i][1][0]) \
                     + abs(pairloc[i][0][1] - pairloc[i][1][1])
            if appx_d > max_d:
                max_d = appx_d
                max_i = i
        if distance(pairloc[max_i][0][0], pairloc[max_i][0][1], pairloc[max_i][1][0],
                    pairloc[max_i][1][1]) > spat_constr:
            return True
        else:
            #try to reduce the size of pairloc
            max_ln_lat = (abs(pairloc[max_i][0][0] - pairloc[max_i][1][0]),
                          abs(pairloc[max_i][0][1] - pairloc[max_i][1][1]))
            m = 0
            while m < len(pairloc):
                if abs(pairloc[m][0][0] - pairloc[m][1][0]) < max_ln_lat[0] \
                        and abs(pairloc[m][0][1] - pairloc[m][1][1]) < max_ln_lat[1]:
                    del pairloc[m]
                else:
                    m += 1
            diam_list = [distance(pair[0][0], pair[0][1], pair[1][0], pair[1][1]) for pair in pairloc]
            if max(diam_list) > spat_constr:
                return True
            else:
                return False


def cluster_traceSegmentation(user, spat_constr, dur_constr):
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
    return user