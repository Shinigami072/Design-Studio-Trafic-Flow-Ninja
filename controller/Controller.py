from road.road_provider import road_provider, RoadProvider
from model.model import Model
from road.road import Road
from typing import Tuple, List
from random import randrange


class Controller:

    def __init__(self, provider: RoadProvider = road_provider("default_road_provider")):
        self.provider = provider
        self.model = Model()

        # tomtom data
        # other user data (optional)

    def query_roads(self, coordinates: Tuple[float, float]) -> List[RoadProvider.RoadId]:
        return self.provider.names(coordinates)

    def get_result(self, name: RoadProvider.RoadId):
        # To be done
        road = self.provider.provide(name)

        average_traffic = self.model.get_average_daily_traffic(road)
        hourly_traffic = self.model.get_traffic_for_time_period(road)

        return [average_traffic, hourly_traffic]
