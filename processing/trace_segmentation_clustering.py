"""
define function cluster_traceSegmentation: it implements trace segmentation method for clustering gps trajectory
:param arg:
:return: modified user traces
"""

import sys, os
import numpy as np
from itertools import combinations


## import below only run in 'run' mode, not in 'console mode'
sys.path.append(os.path.dirname(os.getcwd())) 
from distance import distance



def cluster_traceSegmentation(user, spat_constr, dur_constr):
    """
    This function is to cluster raw GPS locations of one user to identify GPS stays using trace segmentation method.
    It scans through the user's trajectories to identify where the user stayed for a while to do activities.
    A GPS stay is a cluster of records that satisfy both spatial and temporal constraints.
    The implementation here follows the algorithm in Figure 16 of (Wang et al. 2019.
    Extracting trips from multi-sourced data for mobility pattern analysis: An app-based data example. TR-C)
    
    :param user: It is structured in a python dictionary containing records of multiple days for one user. 
                A key and its value of the dictionary give a date and the raw GPS records on the date, respectively.
                The records on one date is stored in a list.
                for example: {date0:[record, record], date1:[record, record]...}
    :param spat_constr: the spatial constraint of the clustering method in Km (e.g., 0.2 kilometers).
    :param dur_constr: the temporal constraint of the clustering method in seconds (e.g., 300 seconds).
    :return user: The output gives potential stays in GPS records of the input user ID.
                  Similar to input data, the output data is structured in a python dictionary.
                  A key gives a date, and its value gives a list of integrated, clustered records on the date.
    """
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


def diameterExceedCnstr(traj, s, e, spat_constr):
    """
    This is a helper function that is called in cluster_traceSegmentation (defined above)
    Purpose: compute the greatest distance between any two locations within a set of locations "traj[i:j]"
            and check whether the distance is larger than spatial constraint "spat_constr": return True if Yes.
    Remember, computing distance() between any two locations is costly and we avoid exhaustively compute the distance
    between any two locations in the set. This why this function seems unnecessarily complicated.
    :param traj: the trajectory we will be working on; it is a list of time ordered records.
    :param s: The starting point of the trajectory segment we want to check
    :param e: The ending point of the trajectory segment we want to check
    :param spat_constr: spatial constraint in Km that serves as the threshold
    :return: Ture or False (reture Ture if the greatest distance is larger than spat_constr; otherwise, return False)
    """
    loc = list(set([(round(float(traj[m][3]),5),round(float(traj[m][4]),5)) for m in range(s,e+1)])) # unique locations
    if len(loc) <= 1:
        return False
    if distance(traj[s][3],traj[s][4],traj[e][3],traj[e][4])>spat_constr: # check the distance between the first and last trace
        return True
    else:
        # guess the max distance pair; approximate distance
        pairloc = list(combinations(loc, 2)) # the pairs of any two locations: an exhaustive combination
        ## find the pair of locations having the largest Manhattan distance
        max_d = 0  # store the max Manhattan distance
        max_i = 0 # store the index of the pair of locations that has the max Manhattan distance
        for i in range(len(pairloc)): # pairloc[i] is a pair of locations: [(lat0, long0), (lat1, long1)]
            # check Manhattan distance between the pair of locations
            Manh_d = abs(pairloc[i][0][0] - pairloc[i][1][0]) + abs(pairloc[i][0][1] - pairloc[i][1][1]) # difference of latitudes + difference of longitudes
            if Manh_d > max_d:
                max_d = Manh_d
                max_i = i
        if distance(pairloc[max_i][0][0], pairloc[max_i][0][1], pairloc[max_i][1][0], pairloc[max_i][1][1]) > spat_constr: # check Euclidean distance
            return True
        else:
            # try to reduce the size of pairloc
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