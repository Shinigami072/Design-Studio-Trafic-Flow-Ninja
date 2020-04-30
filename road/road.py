from typing import List


class Fragment:
    def __init__(self, width: float, speed: float):
        # self.road_width = 1.5
        self.speed = speed
        self.width = width


class Road:
    def __init__(self, name: str, fragments: List[Fragment]):
        self.name = name
        self.fragments = fragments
