
"""
remove oscillation traces
:param user:
:param dur_constr:
:return: oscill gps pair list
"""


import sys
sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")


def oscillation_h1_oscill(user, dur_constr):
    user = user#arg[0]
    TimeWindow = dur_constr#arg[1]#5 * 60
    oscillgpspairlist = []

    tracelist = []
    for d in sorted(user.keys()):
        for trace in user[d]:
            dur_i = 1 if int(trace[9]) == -1 else int(trace[9])
            tracelist.append([trace[1], trace[0], dur_i, trace[6], trace[7], trace[8], 1, 1])

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
            oscillation_pairs = list(
                set([(sequence_list[0][0], sequence_list[i][0]) for i in range(1, len(sequence_list))]))
            t_start = suspSequence[-1]  # + 1
        else:
            t_start += 1

    # record locations of oscill pairs
    pinggps = [0, 0]
    ponggps = [0, 0]
    for pair in oscillation_pairs:
        flag_ping = 0
        flag_pong = 0
        for ii in range(len(tracelist)):  # find ping of this pair
            if tracelistno_original[ii] == pair[0]:
                pinggps = [tracelist[ii][3], tracelist[ii][4]]
                flag_ping = 1
            if tracelistno_original[ii] == pair[1]:
                ponggps = [tracelist[ii][3], tracelist[ii][4]]
                flag_pong = 1
            if flag_ping * flag_pong == 1:
                break
        pairgps = [pinggps[0], pinggps[1], ponggps[0], ponggps[1]]
        if pairgps not in oscillgpspairlist: oscillgpspairlist.append(pairgps)
    i=0 # remove -1 in oscillpair
    while i < len(oscillgpspairlist):
        if -1 in oscillgpspairlist[i]:
            del oscillgpspairlist[i]
        else:
            i += 1

    return oscillgpspairlist