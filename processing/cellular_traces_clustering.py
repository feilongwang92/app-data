

import sys, os

## import below only run in 'run' mode, not in 'console mode'
sys.path.append(os.path.dirname(os.getcwd())) 
from incremental_clustering import cluster_incremental
from oscillation_type1 import oscillation_h1_oscill
from util_func import update_duration



def clusterPhone(arg):
    """
    Process cellular traces of one user (one partition of the raw records with uncertainty radius larger than 100 meters):
    cluster some records into stays or identify it as a transient point
    The function first clusters cellular traces then remove oscillation traces. The implementation follows (Wang and Chen 2018.
    On data processing required to derive mobility patterns from passively-generated mobile phone data. TR-C)
    You may also find an introduction of this function in document "Workflow of data processing"

    :param: arg
            a tuple of 3 parameters:
                - user: traces (records) of the user to be processed
                - dur_constr: temporal constraint in seconds to define a stay (e.g., 300 seconds)
                - spat_constr_cell: spatial constraint to define a cellualr stay (e.g., 1.0 Km)

    :return: user (the processed data of the input user)
    """
    # unpack parameter
    user, dur_constr, spat_constr_cell = arg
    # spat_constr_cell = 1.0

    ## Cluster raw cellular locations of one user on multiple days to identify cellular stays.
    ## Incremental clustering method is used, which clusters locations on multiple days based on
    ## a specified spatial threshold such that each outputting cluster of locations represents a potential stay.
    user = cluster_incremental(user, spat_constr_cell)# not passing a duration_constraint means not to cluster stays but original locational records

    ## update duration (whenever some records are clustered into one, we need to check and recalculate update duration of clusters if needed)
    user = update_duration(user, dur_constr)

    ## address oscillation traces in one user's trajectory
    user = oscillation_h1_oscill(user, dur_constr)
    
    # OscillationPairList = oscillation_h1_oscill(user, dur_constr)
    ## find pong in trajactory, and replace it with ping
    ## this part is now integreted into the function itself
    ## OscillationPairList is in format: {, (ping[0], ping[1]): (pong[0], pong[1])}
    # for d in user.keys():
    #     for trace in user[d]:
    #         if (trace[6], trace[7]) in OscillationPairList:
    #             trace[6], trace[7] = OscillationPairList[(trace[6], trace[7])]

    ## update duration (whenever some records are clustered into one, we need to check and recalculate update duration of clusters if needed)
    user = update_duration(user, dur_constr)


    return user