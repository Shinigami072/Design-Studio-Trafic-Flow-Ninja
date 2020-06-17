from typing import List, Dict

from overpy import Way
from enum import Enum


class PolishRoadClass(Enum):
    A = 1
    S = 2
    GP = 3
    G = 4
    Z = 5
    L = 6
    LD = 7
    D = 8


_class_mapping: Dict[str, List[PolishRoadClass]] = {
    "motorway": [PolishRoadClass.A],
    "motorway_link": [PolishRoadClass.A],
    "trunk": [PolishRoadClass.S],
    "trunk_link": [PolishRoadClass.S],
    "primary": [PolishRoadClass.G, PolishRoadClass.GP],
    "primary_link": [PolishRoadClass.G, PolishRoadClass.GP],
    "secondary": [PolishRoadClass.G, PolishRoadClass.Z],
    "secondary_link": [PolishRoadClass.G, PolishRoadClass.Z],
    "tertiary": [PolishRoadClass.G, PolishRoadClass.Z],
    "tertiary_link": [PolishRoadClass.G, PolishRoadClass.Z],
    "unclassified": [PolishRoadClass.L, PolishRoadClass.LD],
    "unclassified_link": [PolishRoadClass.L, PolishRoadClass.D],
    "residential": [PolishRoadClass.L, PolishRoadClass.D],
    "living_street": [PolishRoadClass.L, PolishRoadClass.D],
    "service": [PolishRoadClass.L, PolishRoadClass.D],
    "track": [PolishRoadClass.L, PolishRoadClass.D]
}


def _to_polish_class(way: Way) -> List[PolishRoadClass]:
    highway = way.tags["highway"]
    return _class_mapping[highway]


_widths: Dict[PolishRoadClass, float] = {
    PolishRoadClass.A: 3.75,
    PolishRoadClass.S: 3.75,
    PolishRoadClass.GP: 3.50,
    PolishRoadClass.G: 3.50,
    PolishRoadClass.Z: 3.00,
    PolishRoadClass.L: 2.75,
    PolishRoadClass.LD: 2.5,
    PolishRoadClass.D: 2.25,
}

_extra_lateral_clearance: Dict[PolishRoadClass, float] = {
    PolishRoadClass.A: 3.0,
    PolishRoadClass.S: 2.5,
    PolishRoadClass.GP: 1.5,
    PolishRoadClass.G: 1.25,
    PolishRoadClass.Z: 1.0,
    PolishRoadClass.L: 0.75,
    PolishRoadClass.LD: 0.75,
    PolishRoadClass.D: 0.75,
}


def min_width(way: Way) -> float:
    """
        minimal legal width of this piece of road in meters
    """
    lanes = float(way.tags.get("lanes", 1))
    is_oneway = way.tags.get("oneway", "no") == "yes"
    return min([_widths[c] for c in _to_polish_class(way)]) * (lanes/(1 if (is_oneway or lanes == 1) else 2))


def min_extra_lateral_clearance(way: Way, have_shoulder: bool) -> float:
    """
        minimal legal extra lateral clearance of this piece of road in meters
    """
    maxspeed = float(way.tags.get("maxspeed", 1))
    if maxspeed > 100:
        return 3.0
    elif maxspeed <= 100 and (_to_polish_class(way) == PolishRoadClass.A or _to_polish_class(way) == PolishRoadClass.S):
        return 2.5
    elif have_shoulder and not(_to_polish_class(way) == PolishRoadClass.A or
                               _to_polish_class(way) == PolishRoadClass.S):
        return 2.0
    else:
        return min([_extra_lateral_clearance[c] for c in _to_polish_class(way)])
