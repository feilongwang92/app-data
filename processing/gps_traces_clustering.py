"""
    clustering gps trajectory
:param arg: user, dur_constr, spat_constr
:return: modified user traces
"""

import sys
import numpy as np


sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance
from trace_segmentation_clustering import cluster_traceSegmentation
from incremental_clustering import cluster_incremental
from util_func import update_duration



def clusterGPS(arg):
    user, dur_constr, spat_constr= arg

    ## trace segmentation clustering
    user = cluster_traceSegmentation(user, spat_constr, dur_constr)

    #incremental clustering
    user = cluster_incremental(user, spat_constr, dur_constr=dur_constr) #passing a duration_constraint means to cluster stays, not original locational records

    # update duration
    user = update_duration(user, dur_constr)


    return user