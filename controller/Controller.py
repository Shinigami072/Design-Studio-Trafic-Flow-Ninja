from typing import Tuple, List

from model.model import Model, model_provider
from road.road_provider import road_provider, RoadProvider


class Controller:

    def __init__(self,
                 provider: RoadProvider = road_provider("default_road_provider"),
                 model: Model = model_provider("default")):
        self.provider = provider
        self.model = model

        # tomtom data
        # other user data (optional)

    def query_roads(self, coordinates: Tuple[float, float]) -> List[RoadProvider.RoadId]:
        return self.provider.names(coordinates)

    def get_result(self, name: RoadProvider.RoadId):
        road = self.provider.provide(name)

        #average_traffic = self.model.get_average_daily_traffic(road)
        hourly_traffic = self.model.get_traffic_for_time_period(road)

        return hourly_traffic
