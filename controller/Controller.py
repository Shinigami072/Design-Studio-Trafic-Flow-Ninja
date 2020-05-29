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
        # speeds dont fit model, they should be list of tuples
        # speeds = [(60, 3), (50, 2), (40, 1)]
        # 2nd parameter is time that speed was measured in hours, to be fixed
        speeds = [(fragment.speed, fragment.speed / fragment.length) for fragment in road.fragments]

        # width from roads?
        # temporary road for testing

        paved_width = road.fragments[0].width
        sd_paved_width = 0.5

        extra_lateral_clearance = 1.4

        bendiness = road.fragments[0].bendiness

        density_of_intersections = 4.3

        average_traffic = self.model.get_average_daily_traffic(speeds, sd_paved_width, paved_width,
                                                               extra_lateral_clearance,
                                                               bendiness, density_of_intersections)
        hourly_traffic = self.model.get_traffic_for_time_period(road.fragments[0].speed, sd_paved_width,
                                                                paved_width,
                                                                extra_lateral_clearance, bendiness,
                                                                density_of_intersections)

        return [average_traffic, hourly_traffic]
