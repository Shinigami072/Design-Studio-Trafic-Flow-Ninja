from typing import Tuple, List

from road import Road
from road.road_provider import road_provider, RoadProvider

import os
import pickle


class CacheRoadProvider(RoadProvider):
    class CacheRoadId(RoadProvider.RoadId):
        def __init__(self, road_id: int, ref: str, name: str):
            self.road_id = road_id
            self.name = name
            self.ref = ref

        def __eq__(self, other):
            return other.isinstance(CacheRoadProvider) and self.road_id == other.road_id

        def __hash__(self):
            return self.road_id

        def __str__(self):
            return self.name

        def __repr__(self):
            return "[{id}] {name}".format(id=self.road_id, name=self.name)

    def __init__(self):
        self.provider = road_provider("default_road_provider")

    @staticmethod
    def _cache_road(road: Road, radius: float, location: Tuple[float, float]):
        try:
            os.makedirs("cache/" + str(radius))
            with open("cache/" + str(radius) + "/" + str(location) + ".pickle", "wb") as pickle_out:
                pickle.dump(road, pickle_out)
        except IOError:
            print("Cache failed")

    @staticmethod
    def _get_cached_road(radius: float, location: Tuple[float, float]):
        if os.path.exists("cache/" + str(radius) + "/" + str(location) + ".pickle"):
            try:
                with open("cache/" + str(radius) + "/" + str(location) + ".pickle", "rb") as pickle_in:
                    road = pickle.load(pickle_in)[0]
            except IOError:
                print("Getting cache failed")
        return road

    def provide(self, name: CacheRoadId, radius: float, location: Tuple[float, float]) -> Road:
        road = self._get_cached_road(radius, location)

        if road is None:
            road = self.provider.provide(name, radius, location)
            self._cache_road(road, radius, location)

        return road

    def names(self, location: Tuple[float, float]) -> List[CacheRoadId]:
        return self.provider.names(location)


def _create_road_provider() -> RoadProvider:
    return CacheRoadProvider()
