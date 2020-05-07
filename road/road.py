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

    def __str__(self):
        return "[bendiness = {bendiness}, " \
               "speed = {speed:.2f}km/h, " \
               "width = {width:.2f}m, " \
               "length = {length:.2f}m]" \
            .format(bendiness=self.bendiness,
                    speed=self.speed if self.speed is not None else 0,
                    width=self.width if self.width is not None else 0,
                    length=self.length if self.length is not None else 0
                    )

    def __repr__(self):
        return self.__str__()


class Road:
    def __init__(self, name: str, fragments: List[Fragment]):
        self.name = name
        self.fragments = fragments

    def __str__(self):
        return "{name}: {fragments}".format(
            name=self.name,
            fragments=self.fragments)

    def __repr__(self):
        return self.__str__()
