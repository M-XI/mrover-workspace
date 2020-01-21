# this file is a math utilities file. any functions strictly
# math related are here so simHandler doesn't get plugged up
# with too much crap
# NEEDS TO BE TESTED BC THIS MATH IS NASTY AND IDK IF IT WORKS YET

# Math Utilities File
# Primarily distance estimation for GPS coordinates
# Given as solving geodesics on an ellipsoid involves line integrals
# approximations have been made, and work well on these scales
import math

# Constants:
# Unsure whether this should be a const as 
# https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
# suggests that the meters of a degree of latitude varies on latitude
# METER_LAT_DEG = 111, 200
# METER_LAT_MINUTES = 1853

SEMI_MAJOR_A = 6378137.0
SEMI_MAJOR_B = 6356752.314245


def degreeToRadian(degree, minute=0):  # optional minute arg
    return math.pi / 180 * (degree + minute / 60)


def radianToDegree(radian):
    return radian * 180 / math.pi


# gets change in degrees from one location to another
def deltaDeg(sim, object_origin, object_dest):
    olat_deg, olat_min, olon_deg, olon_min = object_dest.get_coords()
    rlat_deg, rlat_min, rlon_deg, rlon_min = object_origin.get_coords()
    # gets change in degrees from object_origin to object_dest
    dlat_deg = olat_deg - rlat_deg
    dlat_min = olat_min - rlat_min
    dlon_deg = olon_deg - rlon_deg
    dlon_min = olon_min - rlon_min

    return dlat_deg, dlat_min, dlon_deg, dlon_min

def metersPerLat(degree) {
    lon_deg_length = (
        111412.84 * math.cos(2 * degree)
        - 93.5 * math.cos(3 * degree)
        + 0.118 * math.cos(5 * degree)
    )

    return lon_deg_length
}

def metersPerLon(degree) {
    lat_deg_length = (
        111132.92
        - 559.83 * cos(2 * degree)
        + 1.175 * cos(4 * degree)
        - 0.0023 * cos(6 * degree)
    )

    return lat_deg_length
}

# Approximation of the geodesic between two coordinates
# https://en.wikipedia.org/wiki/Geodesics_on_an_ellipsoid
def deg2meters(sim, object_origin, object_dest):
    # given an object, calculates the degrees to meters conversion
    # between the rover and an object, returns meters

    olat_deg, olat_min, olon_deg, olon_min = object_dest.get_coords()
    rlat_deg, rlat_min, rlon_deg, rlon_min = object_origin.get_coords()
    dlat_deg, dlat_min, dlon_deg, dlon_min = deltaDeg(
        sim, object_origin, object_dest)

    # see note on METER_LAT_DEG
    # lat_meters = dlat_deg * METER_LAT_DEG + dlat_min * METER_LAT_MINUTES

    lon_deg_length = metersPerLat((olat_deg + rlat_deg) / 2)
    lat_deg_length = metersPerLon((olon_deg + rlon_deg) / 2)    
    
    # the average was used, as we expect the values to be close
    # https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree

    lon_meters = lon_deg_length * dlon_deg + lon_deg_length * (dlon_min / 60)
    lat_meters = lat_deg_length * dlat_deg + lat_deg_length * (dlat_min / 60)

    # returns a scalar in meters
    return math.hypot(lat_meters, lon_meters)

# Approximation of the inverse coord arrived after traveling
# distance meters at angle angle from with respect to the coord system
def meters2deg(sim, distance, angle):
    # TODO: Change implementation depending on the coord system, unclear
    #       if deflection from the horizontal or the vertical

    # angle should be relative to the 0th degree of the coord system,
    #   NOT the rover or another object
    # returns the delta of degrees and minutes from meters
    # first need to get length of longitudinal degree,
    #   using the rover's coords as a reference
    lat_deg, lat_min, lon_deg, lon_min = sim.rover.get_coords()

    lon_deg_length = metersPerLon(lon_deg + lon_min / 60)
    lat_deg_length = metersPerLat(lat_deg + lat_min / 60)

    # component of meters in the up and down m80
    meters_lon = distance * math.sin(angle)
    # component of meters in the left and right boyo
    meters_lat = distance * math.cos(angle)

    # TODO: Check formatting of minutes and degrees, fractional or not
    lon_deg = meters_lon // lon_deg_length
    lon_min = 60 * (meters_lon % lon_deg_length) / lon_deg_length
    lat_deg = meters_lat // lat_deg_length
    lat_min = 60 * (meters_lat % lat_deg_length) / lat_deg_length

    return lat_deg, lat_min, lon_deg, lon_min
