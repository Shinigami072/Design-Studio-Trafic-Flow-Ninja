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
    D = 7


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
    "unclassified": [PolishRoadClass.L, PolishRoadClass.D],
    "unclassified_link": [PolishRoadClass.L, PolishRoadClass.D],
    "residential": [PolishRoadClass.L],
    "living_street": [PolishRoadClass.L],
    "service": [PolishRoadClass.L],
    "track": [PolishRoadClass.L]
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
    PolishRoadClass.L: 7.75,
    PolishRoadClass.D: 2.50,
}


def min_width(way: Way) -> float:
    """
        minimal legal width of this piece of road in meters
    """
    lanes = float(way.tags.get("lanes", 1))
    return min([_widths[c] for c in _to_polish_class(way)]) * lanes
