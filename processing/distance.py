"""
calculte distance between two gps points
:param lat1:
:param lon1:
:param lat2:
:param lon2:
:return: distance in Km
"""


from math import cos, asin, sqrt


def distance(lat1, lon1, lat2, lon2):
    # return geodesic((lat1, lon1),(lat2, lon2)).km
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))
# print (distance(47.628,-122.248,47.627,-122.248))