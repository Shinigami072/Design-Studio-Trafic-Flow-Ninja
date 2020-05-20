from road.road_provider import road_provider
from model.model import Model
from road.road import Road
from typing import Tuple, List
from random import randrange

class Controller:

    def __init__(self, coordinates: Tuple[float, float]):
        self.provider = road_provider("default_road_provider")
        #tomtom data
        self.client_coords = coordinates
        #other user data (optional)


    def generate_roads(self) -> List[Road]:
        return [self.provider.provide(road_id) for road_id in self.provider.names(self.client_coords)]

    def get_result(self):
        #To be done
        roads = self.generate_roads()
        #speeds dont fit model, they should be list of tuples
        #speeds = [(60, 3), (50, 2), (40, 1)]
        #2nd parameter is time that speed was measured in hours, to be fixed
        speeds = []
        for road in roads:
            # get rid of random
            speeds.append([(fragment.speed, randrange(1, 5)) for fragment in road.fragments])

        #width from roads?
        sd_paved_width = 0.5
        paved_width = 4.4
        extra_lateral_clearance = 1.4
        bendiness = 199.3
        density_of_intersections = 4.3
        model = Model()
        average_traffic = model.get_average_daily_traffic(speeds, sd_paved_width, paved_width, extra_lateral_clearance,
                                               bendiness, density_of_intersections)
        hourly_traffic = model.get_traffic_for_time_period(roads[0].fragments[0].speed, sd_paved_width, paved_width,
                                                           extra_lateral_clearance,bendiness,density_of_intersections)

        return (average_traffic, hourly_traffic)