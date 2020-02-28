

import sys
from itertools import combinations

sys.path.append("E:\\ProgramData\\python\\cuebiq_share_git")
from distance import distance


def update_duration(user):
    """

        :param user:
        :return:
        """
    for d in user.keys():
        for trace in user[d]: trace[9] = -1  # clear needed! #modify grid
        i = 0
        j = i
        while i < len(user[d]):
            if j >= len(user[d]):  # a day ending with a stay, j goes beyond the last observation
                dur = str(int(user[d][j - 1][0]) + max(0, int(user[d][j - 1][9])) - int(user[d][i][0]))
                for k in range(i, j, 1):
                    user[d][k][9] = dur
                break
            if user[d][j][6] == user[d][i][6] and user[d][j][7] == user[d][i][7] and j < len(user[d]):
                j += 1
            else:
                dur = str(int(user[d][j - 1][0]) + max(0, int(user[d][j - 1][9])) - int(user[d][i][0]))
                for k in range(i, j, 1):
                    user[d][k][9] = dur
                i = j
    return user


def diameterExceedCnstr(traj,i,j,spat_constr):
    """
    The Diameter function computes the greatest distance between any two locations with in the set traj[i:j]
    and compare the distance with constraint
    remember, computing distance() is costly
    :param traj:
    :param i:
    :param j:
    :param spat_constr:
    :return: Ture or False
    """
    loc = list(set([(round(float(traj[m][3]),5),round(float(traj[m][4]),5))  for m in range(i,j+1)]))# unique locations
    if len(loc) <= 1:
        return False
    if distance(traj[i][3],traj[i][4],traj[j][3],traj[j][4])>spat_constr: # check the first and last trace
        return True
    else:
        # guess the max distance pair; approximate distance
        pairloc = list(combinations(loc, 2))
        max_i = 0
        max_d = 0
        for i in range(len(pairloc)):
            appx_d = abs(pairloc[i][0][0] - pairloc[i][1][0]) \
                     + abs(pairloc[i][0][1] - pairloc[i][1][1])
            if appx_d > max_d:
                max_d = appx_d
                max_i = i
        if distance(pairloc[max_i][0][0], pairloc[max_i][0][1], pairloc[max_i][1][0],
                    pairloc[max_i][1][1]) > spat_constr:
            return True
        else:
            #try to reduce the size of pairloc
            max_ln_lat = (abs(pairloc[max_i][0][0] - pairloc[max_i][1][0]),
                          abs(pairloc[max_i][0][1] - pairloc[max_i][1][1]))
            m = 0
            while m < len(pairloc):
                if abs(pairloc[m][0][0] - pairloc[m][1][0]) < max_ln_lat[0] \
                        and abs(pairloc[m][0][1] - pairloc[m][1][1]) < max_ln_lat[1]:
                    del pairloc[m]
                else:
                    m += 1
            diam_list = [distance(pair[0][0], pair[0][1], pair[1][0], pair[1][1]) for pair in pairloc]
            if max(diam_list) > spat_constr:
                return True
            else:
                return False