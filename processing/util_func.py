


def update_duration(user, dur_constr):
    """
    This function is to update the duration of stays in the records of a user. 
    The function is called following any procedure involving modifying records. 
    Note that the duration of a stay is defined as the time difference between the first and the last record with in a cluster. 
    For example, after applying incremental clustering in processing gps records, 
    it is possible that some clusters may be changed in terms of records in the clusters. 
    Therefore, this function is called to re-calculate duration for stays, taking as input clustered GPS records of 
    a user (i.e., the output of the previous sub-module incremental clustering). 
    
    :param user: traces (records) of the user to be processed;
                 Each record is either a transient point or a stay.
                 The input data is structured in a python dictionary.
                 A key and its value of the dictionary give a date and the records on the date, respectively.
    :param dur_constr:  temporal constraint in seconds to define a stay (e.g., 300 seconds)
    :return user: The output contains records of the input user ID where durations of stays are updated.
                  This function directly overwrites the input user, and thus the data structure is the same as the input
    """

    ## recall that a trace/record is has 12 columns, including
    # unix_start_t user_ID mark_1 orig_lat orig_long orig_unc stay_lat stay_long stay_unc stay_dur stay_ind human_start_t
    # for example, 1573773245 None 0 47.3874765 -122.2401154 26 -1 -1 -1 -1 -1 191114161405
    # thus trace[9] gives the duration if the trace is a stay
    # trace[6] and trace[7] give the latitude and longitude of the stay (if it is a stay)
    for d in user.keys():
        for trace in user[d]: trace[9] = -1  # clear stay duration needed!
        # basically, we need to identify a sequence of traces that have the same stay locations
        # then the duration is calculated as the time difference between the start and end of the sequence
        i = 0
        j = i
        while i < len(user[d]):
            if j >= len(user[d]):  # take case the case: if the trajectory on one day ends with a stay, j goes beyond the last observation
                dur = str(int(user[d][j - 1][0]) + max(0, int(user[d][j - 1][9])) - int(user[d][i][0])) #compute duration
                for k in range(i, j, 1):
                    user[d][k][9] = dur # write duration
                break
            if user[d][j][6] == user[d][i][6] and user[d][j][7] == user[d][i][7] and j < len(user[d]):
                j += 1
            else:
                dur = str(int(user[d][j - 1][0]) + max(0, int(user[d][j - 1][9])) - int(user[d][i][0]))#compute duration
                for k in range(i, j, 1):
                    user[d][k][9] = dur # write duration
                i = j

    ## if a record is not a stay, we will assign the duration as -1
    for d in user.keys():
        for trace in user[d]:
            # those traces with gps as -1,-1 (not clustered) should not assign a duration
            if float(trace[6]) == -1: trace[9] = -1
            ## our default output format: give -1 to non-stay records
            if float(trace[9]) < dur_constr: # change back keep full trajectory: do not use center for those are not stays
                trace[6], trace[7], trace[8], trace[9] = -1, -1, -1, -1  # for no stay, do not give center

    return user


