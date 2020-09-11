"""
    clustering gps trajectory
:param arg: user, dur_constr, spat_constr
:return: modified user traces
"""

import sys, os
import numpy as np


## import below only run in 'run' mode, not in 'console mode'
sys.path.append(os.path.dirname(os.getcwd())) 
from distance import distance
from trace_segmentation_clustering import cluster_traceSegmentation
from incremental_clustering import cluster_incremental
from util_func import update_duration



def clusterGPS(arg):
    """
    process gps traces of one user (one partition of the raw records with uncertainty radius smaller than 100 meters):
    cluster some records into stays or identify it as a transient point
    The function includes three steps:
        - trace-segmentation clustering,
        - Incremental clustering,
        - update stay duration.
    Each of them is a implemented by a function as below. They are also explained in document "Workflow of data processing"

    :param: arg
            a tuple of 3 parameters:
                - user: traces (records) of the user to be processed
                - dur_constr: temporal constraint in seconds to define a stay (e.g., 300 seconds)
                - spat_constr_gps: spatial constraint to define a gps stay (e.g., 0.2 Km)

    :return: user (the processed data of the input user)
    """
    user, dur_constr, spat_constr_gps= arg

    ## trace segmentation clustering to identify where the user stayed
    user = cluster_traceSegmentation(user, spat_constr_gps, dur_constr)

    ## incremental clustering to identify common stays that were visited multiple times
    user = cluster_incremental(user, spat_constr_gps, dur_constr=dur_constr) # passing a dur_constr means to cluster stays rather than clustering raw locational records

    ## update duration (when some records are clustered into one, we need to check and recalculate update duration of clusters if needed)
    user = update_duration(user, dur_constr)

    return user