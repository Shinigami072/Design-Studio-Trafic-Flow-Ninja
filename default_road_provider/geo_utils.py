from decimal import Decimal
from typing import Tuple
from math import pi, pow, sin, cos, sqrt, atan2

d_pi = Decimal(pi)


def _to_radians(degrees: Decimal) -> Decimal:
    return degrees * d_pi / 180


def coords_to_m(
        coords_from: Tuple[Decimal, Decimal],
        coords_to: Tuple[Decimal, Decimal]) -> float:
    """
    Calculate distance between two coordinates in meters using Haversine algorithm
    :param coords_from: geo-coordinates,from
    :param coords_to: geo-coordinates to
    :return: meters
    """
    long1, lat1 = coords_from
    long2, lat2 = coords_to

    d_long = _to_radians(long2 - long1)
    d_lat = _to_radians(lat2 - lat1)

    a = pow(sin(d_lat / 2), 2) + \
        cos(_to_radians(lat1)) * \
        cos(_to_radians(lat2)) * \
        pow(sin(d_long / 2), 2)

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return 6367_000 * c


def coords_to_bend_deg(
        coords_from: Tuple[Decimal, Decimal],
        coords_through: Tuple[Decimal, Decimal],
        coords_to: Tuple[Decimal, Decimal]) -> float:
    """
    Calculate bend between two coordinates in degrees/m
    :param coords_from: geo-coordinates,from
    :param coords_to: geo-coordinates to
    :return: degrees/m
    """
    # TODO bendiness
    return 0.0
