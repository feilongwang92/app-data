
"""
remove oscillation traces
:param user:
:param dur_constr:
:return: oscill gps pair list
"""


import sys, os
## import below only run in 'run' mode, not in 'console mode'
sys.path.append(os.path.dirname(os.getcwd())) 


def oscillation_h1_oscill(user, dur_constr):
    """
    This function is to address oscillation traces in one user's trajectory;
    Oscillation traces lead to false trips rather than reflecting users' actual movements and thus need to be removed.
    The function implements a time-window-based method to detect and remove observations that are generated
    from the occurrence of the signaling noises.
    Please referred to Wang and Chen (2018) for the time-window-based method

    :param user: a trajectory of one user to be processed; a record in the trajectory is either a transient point or a stay.
                 It is structured in a dict. A key and its value give a date and the records on the date, respectively.
    :param dur_constr: the length of the time window in seconds for identifying oscillation traces which is used in the time-window-based method
    :return user: contains records of the input user ID with oscillation traces removed. The data structure is the same as the input.
    """

    TimeWindow = dur_constr #for example, 5 * 60 seconds

    tracelist = [] # we will be working on tracelist not user
    for d in sorted(user.keys()):
        for trace in user[d]:
            dur_i = 1 if int(trace[9]) == -1 else int(trace[9]) # duration is 1 for passing-by records
            tracelist.append([trace[1], trace[0], dur_i, trace[6], trace[7], trace[8]])
            # format of each record: [ID, time, duration, lat, long, uncertainty_radius]

    # integrate: only one record representing one stay (i-i records)
    i = 0
    while i < len(tracelist) - 1:
        if tracelist[i + 1][2:5] == tracelist[i][2:5]:
            del tracelist[i + 1]
        else:
            i += 1

    flag_ppfound = False
    # get gps list from tracelist
    gpslist = [(trace[3], trace[4]) for trace in tracelist]
    # unique gps list
    uniqList = list(set(gpslist))
    # give uniq code
    tracelistno_original = [uniqList.index(gps) for gps in gpslist]
    # count duration of each gps_no
    gpsno_dur_count = {item: 0 for item in set(tracelistno_original)}
    for t in range(len(tracelist)):
        if int(tracelist[t][2]) == 0:
            gpsno_dur_count[tracelistno_original[t]] += 1
        else:
            gpsno_dur_count[tracelistno_original[t]] += int(tracelist[t][2])

    # All prepared
    oscillation_pairs = []
    t_start = 0

    # replace pong by ping; be aware that "tracelistno_original==tracelist"
    flag_find_circle = False
    while t_start < len(tracelist):
        flag_find_circle = False
        suspSequence = []
        suspSequence.append(t_start)
        for t in range(t_start + 1, len(tracelist)):  # get the suspicious sequence
            if int(tracelist[t][1]) <= int(tracelist[t_start][1]) + int(tracelist[t_start][2]) + TimeWindow:
                suspSequence.append(t)
                if tracelist[t][3:5] == tracelist[t_start][3:5]:
                    flag_find_circle = True
                    break
            else:
                break

        suspSequence_gpsno = [tracelistno_original[t] for t in suspSequence]
        # check circles
        # if len(set(suspSequence_gpsno)) < len(suspSequence_gpsno):  # implying a circle in it
        if flag_find_circle == True and len(set(suspSequence_gpsno)) != 1:  # not itself
            flag_ppfound = True
            sequence_list = [(item, gpsno_dur_count[item]) for item in set(suspSequence_gpsno)]  # ('gpsno','dur')
            sequence_list = sorted(sequence_list, key=lambda x: x[1], reverse=True)
            # get unique pairs
            oscillation_pairs = list(set([(sequence_list[0][0], sequence_list[i][0]) for i in range(1, len(sequence_list))]))
            t_start = suspSequence[-1]  # + 1
        else:
            t_start += 1

    # record locations of oscill pairs
    oscillgpspairlist = {}
    for pair in oscillation_pairs:
        flag_ping = 0
        flag_pong = 0
        for ii in range(len(tracelist)):  # find ping of this pair
            if tracelistno_original[ii] == pair[0]:
                pinggps = (tracelist[ii][3], tracelist[ii][4])
                flag_ping = 1
            if tracelistno_original[ii] == pair[1]:
                ponggps = (tracelist[ii][3], tracelist[ii][4])
                flag_pong = 1
            if flag_ping * flag_pong == 1:
                break
        if flag_ping*flag_pong:
            oscillgpspairlist[ponggps] = pinggps
        # pairgps = [pinggps[0], pinggps[1], ponggps[0], ponggps[1]]
        # if pairgps not in oscillgpspairlist: oscillgpspairlist.append(pairgps)

    # remove -1 in oscillpair
    for pair in oscillgpspairlist.keys():
        if (-1 in pair) or (-1 in oscillgpspairlist[pair]):
            del oscillgpspairlist[pair]

    # find pong in trajactory, and replace it with ping
    # this part is original outside this function
    # OscillationPairList is in format: {, (ping[0], ping[1]): (pong[0], pong[1])}
    for d in user.keys():
        for trace in user[d]:
            if (trace[6], trace[7]) in oscillgpspairlist:
                trace[6], trace[7] = oscillgpspairlist[(trace[6], trace[7])]

    return user #oscillgpspairlist