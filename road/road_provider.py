import road
from abc import ABC
from typing import Tuple, List


class RoadProvider(ABC):
    def provide(self, location: Tuple[float, float], name: str = None) -> road.Road:
        pass

    def names(self, location: Tuple[float, float]) -> List[str]:
        pass
