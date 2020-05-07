from decimal import Decimal
from typing import List, Tuple


class Fragment:
    def __init__(self,
                 width: float,
                 speed: float,
                 length: float,
                 coords: List[Tuple[Decimal, Decimal]],
                 bendiness: float):
        # self.road_width = 1.5
        self.bendiness = bendiness
        self.coords = coords
        self.speed = speed
        self.width = width
        self.length = length


class Road:
    def __init__(self, name: str, fragments: List[Fragment]):
        self.name = name
        self.fragments = fragments
