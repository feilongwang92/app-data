"""
cluster cellular trajectory
:param arg:
:return: modified users traces
"""

import sys

sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from incremental_clustering import cluster_incremental
from oscillation_type1 import oscillation_h1_oscill
from util_func import update_duration



def clusterPhone(arg):
    user, dur_constr, spat_constr = arg
    # spat_constr_cell = 1.0

    user = cluster_incremental(user, spat_constr)# not passing a duration_constraint means not to cluster stays but original locational records

    # update duration
    user = update_duration(user, dur_constr)

    #address oscillation
    user = oscillation_h1_oscill(user, dur_constr)
    # OscillationPairList = oscillation_h1_oscill(user, dur_constr)
    ## find pong in trajactory, and replace it with ping
    ## this part is now integreted into the function itself
    ## OscillationPairList is in format: {, (ping[0], ping[1]): (pong[0], pong[1])}
    # for d in user.keys():
    #     for trace in user[d]:
    #         if (trace[6], trace[7]) in OscillationPairList:
    #             trace[6], trace[7] = OscillationPairList[(trace[6], trace[7])]

    # update duration
    user = update_duration(user, dur_constr)


    return user