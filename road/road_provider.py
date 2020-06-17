from abc import ABC
from typing import Tuple, List

import road


class RoadProvider(ABC):
    class RoadId(ABC):
        pass

    def get_current_speed(self, coords: List[Tuple[float, float]]) -> float:
        raise NotImplementedError

    def provide(self, name: RoadId, radius: float, location: Tuple[float, float]) -> road.Road:
        raise NotImplementedError

    def names(self, location: Tuple[float, float]) -> List[RoadId]:
        raise NotImplementedError


def road_provider(module: str, tomtom_key: str) -> RoadProvider:
    mod = __import__(module)
    return mod._create_road_provider(tomtom_key)
