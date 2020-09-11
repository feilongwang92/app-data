"""
    incremental clustering developed in 2018 TRC paper
    together with k-means to correct an order issue related to incremental clustering
:param user:
:param spat_constr:
:param dur_constr:
:return: modified user traces
"""


import sys, os
import numpy as np


## import below only run in 'run' mode, not in 'console mode'
sys.path.append(os.path.dirname(os.getcwd())) 
from distance import distance
from class_cluster import cluster
# from kmeans_clustering import K_meansCluster


def cluster_incremental(user, spat_constr, dur_constr=None):
    """
    This function is to cluster a list of locations. Each location is a pair of latitude and longitude.

    :param user: traces (records) of the user to be processed;
                 we will extract a list of locations from user and do the clustering on the locations
    :param spat_constr: the spatial constraint of the clustering method in kilometers (e.g., 0.2 kilometers)
    :param dur_constr:
            None in default or the temporal constraint that defines the min length of a stay;
            The parameter is used to determine whether we are to cluster stays in user (the 7th and 8th data fields)
            or to cluster original locations that are not clustered (the 4th and 5th data fields)
    :return user: The output contains processed record of the input user.
    """

    ## extract a list of locations that we will cluster.
    ## recall that a trace/record is has 12 columns, including
    # unix_start_t user_ID mark_1 orig_lat orig_long orig_unc stay_lat stay_long stay_unc stay_dur stay_ind human_start_t
    # for example, 1573773245 None 0 47.3874765 -122.2401154 26 -1 -1 -1 -1 -1 191114161405
    if dur_constr:  # cluster locations of stays to obtain aggregated stayes
        loc4cluster = list(set([(trace[6], trace[7]) for d in user for trace in user[d] if int(trace[9]) >= dur_constr]))
    else:  # cluster original locations to obtain stays
        loc4cluster = list(set([(trace[3], trace[4]) for d in user for trace in user[d]]))

    if len(loc4cluster) == 0:
        return (user)

    ## start incremental clustering: the method follows Figure 6 of (Wang and Chen 2018.
    # On data processing required to derive mobility patterns from passively-generated mobile phone data. TR-C)
    L = []
    Cnew = cluster()
    Cnew.addPoint(loc4cluster[0])
    L.append(Cnew)
    Ccurrent = Cnew
    for i in range(1, len(loc4cluster)):
        if Ccurrent.distance_C_point(loc4cluster[i]) < spat_constr:
            Ccurrent.addPoint(loc4cluster[i])
        else:
            Ccurrent = None
            for C in L:
                if C.distance_C_point(loc4cluster[i]) < spat_constr:
                    C.addPoint(loc4cluster[i])
                    Ccurrent = C
                    break
            if Ccurrent == None:
                Cnew = cluster()
                Cnew.addPoint(loc4cluster[i])
                L.append(Cnew)
                Ccurrent = Cnew

    # correct an order issue related to incremental clustering with K-means clustering; refer to section 4.2.3 of 
    # (Wang and Chen 2018. On data processing required to derive mobility patterns from passively-generated mobile phone data. TR-C)
    L = K_meansCluster(L)

    ## compute cluster centers and cluster radius
    mapLocation2cluCenter = {}
    for c in L:
        r = int(1000*c.radiusC()) #
        cent = [str(np.mean([p[0] for p in c.pList])), str(np.mean([p[1] for p in c.pList]))]
        for p in c.pList:
            mapLocation2cluCenter[(str(p[0]),str(p[1]))] = (cent[0], cent[1], r)

    ## overwrite each location that is clustered (replace the location with cluster center)
    if dur_constr:  # if we are clustering stays, overwrite stay locations at (trace[6], trace[7])
        for d in user.keys():
            for trace in user[d]:
                if (trace[6], trace[7]) in mapLocation2cluCenter:
                    # modify locations of stays to aggregated centers of stays
                    trace[6], trace[7], trace[8] = mapLocation2cluCenter[(trace[6], trace[7])][0], \
                                                   mapLocation2cluCenter[(trace[6], trace[7])][1], \
                                                   max(mapLocation2cluCenter[(trace[6], trace[7])][2], int(trace[8]))
    else:  # if we are clustering original locations, record stay locations to (trace[6], trace[7])
        for d in user.keys():
            for trace in user[d]:
                if (trace[3], trace[4]) in mapLocation2cluCenter:
                    trace[6], trace[7], trace[8] = mapLocation2cluCenter[(trace[3], trace[4])][0], \
                                                   mapLocation2cluCenter[(trace[3], trace[4])][1], \
                                                   max(mapLocation2cluCenter[(trace[3], trace[4])][2], int(trace[5]))

    return (user)


def K_meansCluster(L):
    """
    Kmeans clustering algorithm
    It is to correct an order issue related to incremental clustering with K-means clustering; refer to section 4.2.3 of
    (Wang and Chen 2018. On data processing required to derive mobility patterns from passively-generated mobile phone data. TR-C)

    :param L: a list of cluster objects; 
              each cluster contains a list of locations; 
              each location is a pair of latitude and longitude
              The number of cluster objects actually gives the value of K and initial centers for the K-means clustering algorithm
    :return L: a list of cluster objects
    """

    uniqMonthGPSList = []
    for c in L:
        uniqMonthGPSList.extend(c.pList) # c.pList is a list of locations that belong to the cluster

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
    ## convert a list of lists (each list contains locations belonging to a cluster) to a list of cluster objects
    L = []
    for c in Kcluster:
        Cnew = cluster()
        Cnew.pList = c
        L.append(Cnew)
    
    return L