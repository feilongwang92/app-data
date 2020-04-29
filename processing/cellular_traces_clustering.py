"""
cluster cellular trajectory
:param arg:
:return: modified users traces
"""

import sys
import numpy as np


sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from class_cluster import cluster
from oscillation_type1 import oscillation_h1_oscill
from kmeans_clustering import K_meansCluster
from util_func import update_duration, diameterExceedCnstr



def clusterPhone(arg):
    user, dur_constr, spat_constr = arg
    # spat_constr_cell = 1.0
    L = []
    # prepare
    MonthGPSList = list(set([(trace[3], trace[4]) for d in user.keys() for trace in user[d]]))  # not Unique, just used as a container

    if len(MonthGPSList) == 0:
        return (user)

    Cnew = cluster()
    Cnew.addPoint(MonthGPSList[0])
    L.append(Cnew)
    Ccurrent = Cnew
    for i in range(1, len(MonthGPSList)):
        if Ccurrent.distance_C_point(MonthGPSList[i]) < spat_constr:
            Ccurrent.addPoint(MonthGPSList[i])
        else:
            Ccurrent = None
            for C in L:
                if C.distance_C_point(MonthGPSList[i]) < spat_constr:
                    C.addPoint(MonthGPSList[i])
                    Ccurrent = C
                    break
            if Ccurrent == None:
                Cnew = cluster()
                Cnew.addPoint(MonthGPSList[i])
                L.append(Cnew)
                Ccurrent = Cnew

    L = K_meansCluster(L)

    uniqMonthGPSList = {}
    for c in L:
        r = int(1000*c.radiusC()) #
        cent = [str(np.mean([p[0] for p in c.pList])), str(np.mean([p[1] for p in c.pList]))]
        for p in c.pList:
            uniqMonthGPSList[(str(p[0]),str(p[1]))] = (cent[0], cent[1], r)
    for d in user.keys():
        for trace in user[d]:
            if (trace[3], trace[4]) in uniqMonthGPSList:
                trace[6], trace[7], trace[8] = uniqMonthGPSList[(trace[3], trace[4])][0],\
                                               uniqMonthGPSList[(trace[3], trace[4])][1],\
                                               max(uniqMonthGPSList[(trace[3], trace[4])][2],int(trace[5]))

    # update duration
    user = update_duration(user)
    for d in user.keys():
        for trace in user[d]:  # those trace with gps as -1,-1 (not clustered) should not assign a duration
            if float(trace[6]) == -1: trace[9] = -1
            if float(trace[9]) == 0: trace[9] = -1

    #oscillation
    OscillationPairList = oscillation_h1_oscill(user, dur_constr) #in format: [, [pinggps[0], pinggps[1], ponggps[0], ponggps[1]]]
    # find all pair[1]s in list, and replace it with pair[0]
    for pair in OscillationPairList:
        for d in user.keys():
            for trace in user[d]:
                if trace[6] == pair[2] and trace[7] == pair[3]:
                    trace[6], trace[7] = pair[0], pair[1]

    # update duration
    user = update_duration(user)
    for d in user.keys():
        for trace in user[d]:  # those trace with gps as -1,-1 (not clustered) should not assign a duration
            if float(trace[6]) == -1: trace[9] = -1
            if float(trace[9]) == 0: trace[9] = -1

    return user