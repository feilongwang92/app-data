"""
agglomerative clustering
:param user:
:param Rc:
:return: modified user traces
"""

import sys

sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance
from class_cluster import cluster


def cluster_agglomerative(user, Rc = 0.2):
    L = []
    def findClosestPair(L):
        for c in L: c.updateCenter()
        minDist = 1000000 #km
        for i in range(len(L)-1):#what if only one c
            for j in range(i+1, len(L)):
                distC2C = distance(L[i].center[0],L[i].center[1],L[j].center[0],L[j].center[1])
                # print (i,' ',j,' ',distC2C)
                if distC2C < minDist:
                    minDist = distC2C
                    CaNo = i
                    CbNo = j

        return (CaNo, CbNo)

    def mergeCaCb(CaNo, CbNo):
        Cnew = cluster()
        for p in L[CaNo].pList:
            Cnew.addPoint(p)
        for p in L[CbNo].pList:
            Cnew.addPoint(p)
        return Cnew

    def delCluser(L, CaNo, CbNo):
        L[CaNo].erase()
        L[CbNo].erase()
        while True:
            flag_del = False
            for c in L:
                if c.empty():
                    L.remove(c)
                    flag_del = True
                    break
            if flag_del == False:
                break

    for day in user.keys():
        traj = user[day]
        for trace in traj:
            if float(trace[9]) >= 5 * 60:
                p = [trace[6], trace[7]]
                if len(L) == 0:
                    Cnew = cluster()
                    Cnew.addPoint(p)
                    L.append(Cnew)
                elif not any([c.has(p) for c in L]):
                    Cnew = cluster()
                    Cnew.addPoint(p)
                    L.append(Cnew)

    while True:
        if len(L) < 2:
            break
        closestPair = findClosestPair(L)
        Cnew = mergeCaCb(closestPair[0], closestPair[1])
        if Cnew.radiusC() > Rc:
            break
        else:
            delCluser(L, closestPair[0], closestPair[1])
            L.append(Cnew)

    # cal radius
    radiusPool = [[] for _ in range(len(L))]#L[i].radius = int(1000*L[i].radiusC())
    for day in user.keys():
        for trace in user[day]:
            gps = [trace[6], trace[7]]
            for i in range(len(L)):
                if L[i].has(gps):
                    radiusPool[i].append([trace[3], trace[4]])
                    break
    for c in L:
        c.updateCenter()
    for i in range(len(radiusPool)):
        L[i].radius = 0
        for j in range(len(radiusPool[i])):
            dist_k = int(distance(L[i].center[0], L[i].center[1], radiusPool[i][j][0], radiusPool[i][j][1]) * 1000)
            if dist_k > L[i].radius: L[i].radius = dist_k

    for day in user.keys():
        for trace in user[day]:
            gps = [trace[6], trace[7]]
            for i in range(len(L)):
                if L[i].has(gps):
                    trace[6] = str(L[i].center[0])
                    trace[7] = str(L[i].center[1])
                    trace[8] = L[i].radius
                    trace[10] = 'stay_' + str(i)
                    break
    L = []
    return user