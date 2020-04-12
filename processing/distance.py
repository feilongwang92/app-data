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
    # geodesic distance; in kilometers
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742 * asin(sqrt(a))
# print (distance(47.628,-122.248,47.627,-122.248))
## same if using geopy's function; the function here remove our dependency on geopy, which is a large package to install
# from geopy.distance import geodesic
# geodesic((47.628,-122.248),(47.627,-122.248)).km

# A note: The function computes geodesic distance. The function should not be replaced by
# a simple Euclidean distance function, as latitude and longtitude are not equivalent.
# Specifically, in the Seattle area, the geodesic distance will increase by about 100 meters
# if the latitude increases by 0.001, but the geodesic distance will increase by only about 20 meters
# if the longitude increases by 0.001.
# And this difference between latitude and longitude should be unique in different areas of the Earth.
# tested below

# print (distance(47.628,-122.248,47.627,-122.248)) # 111m
# print (distance(47.629,-122.248,47.627,-122.248)) #increase lat by 0.001: 222m
# print (distance(47.628,-122.249,47.627,-122.248)) #increase lng by 0.001: 134m
