"""
incremental clustering developed in 2018 TRC paper
:param user:
:param spat_constr:
:param dur_constr:
:return: modified user traces
"""


import sys
import numpy as np


sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance
from class_cluster import cluster
from kmeans_clustering import K_meansCluster


def cluster_incremental(user, spat_constr, dur_constr):
    L = []

    spat_constr = spat_constr #200.0/1000 #0.2Km
    dur_constr = dur_constr#modify grid

    MonthGPSList = list(set([(trace[6], trace[7]) for d in user.keys() for trace in user[d] if int(trace[9]) >= dur_constr]))# modify grid # only cluster stays

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
            if (trace[6], trace[7]) in uniqMonthGPSList:
                trace[6], trace[7], trace[8] = uniqMonthGPSList[(trace[6], trace[7])][0],\
                                               uniqMonthGPSList[(trace[6], trace[7])][1],\
                                               max(uniqMonthGPSList[(trace[6], trace[7])][2],int(trace[8]))
    return (user)