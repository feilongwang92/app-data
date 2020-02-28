"""
Kmeans clustering
:param L: a list of clusters of traces
:return: a list of clusters
"""

import sys
import numpy as np


sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance


def K_meansCluster(L):
    uniqMonthGPSList = []
    for c in L:
        uniqMonthGPSList.extend(c.pList)

    Kcluster = [c.pList for c in L]
    while True:
        KcenterList = [(np.mean([p[0] for p in c]), np.mean([p[1] for p in c])) for c in Kcluster]
        Kcluster = [[] for _ in range(len(Kcluster))]

        for point in uniqMonthGPSList:
            closestCluIndex = -1
            closestDist2Clu = 1000000
            for i in range(len(KcenterList)):
                distP2C = distance(KcenterList[i][0], KcenterList[i][1], point[0], point[1])
                if closestDist2Clu > distP2C:
                    closestDist2Clu = distP2C
                    closestCluIndex = i
            Kcluster[closestCluIndex].append(point)

        i = 0
        while i < len(Kcluster):
            if len(Kcluster[i]) == 0:
                del Kcluster[i]
            else:
                i += 1

        FlagChanged = False
        for i in range(len(Kcluster)):
            cent = (np.mean([p[0] for p in Kcluster[i]]), np.mean([p[1] for p in Kcluster[i]]))
            if cent != KcenterList[i]:
                FlagChanged = True
                break

        if FlagChanged == False:
            break

    return L