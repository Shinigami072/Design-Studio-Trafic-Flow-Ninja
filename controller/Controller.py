from typing import Tuple, List

from model.model import Model, model_provider
from road.road_provider import road_provider, RoadProvider


class Controller:

    def __init__(self,
                 provider: RoadProvider = road_provider("cache_road_provider"),
                 model: Model = model_provider("default")):
        self.provider = provider
        self.model = model

    def query_roads(self, coordinates: Tuple[float, float]) -> List[RoadProvider.RoadId]:
        return self.provider.names(coordinates)

    def get_result(self, name: RoadProvider.RoadId, radius: float, coordinates: Tuple[float, float]):
        road = self.provider.provide(name, radius, coordinates)

        hourly_traffic = self.model.get_traffic_per_day(road)

        return hourly_traffic
