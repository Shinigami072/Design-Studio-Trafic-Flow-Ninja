import math

from road import Road


# TODO include injection infrastructure for model
class Model:
    # as in wiki.models Table 2
    CONSTANT_COEFF = 4.846
    SEGMENT_CHARACTERISTIC_COEFF = 4.462
    SD_PAVED_WIDTH__COEFF = -0.15
    AVERAGE_DAILY_TRAFFIC_COEFF = -0.064
    # coefficient that allows use for different speed percentiles
    THETA = 5.947

    @staticmethod
    def _road_to_speed_data(road: Road):
        return [(fragment.speed, 1) for fragment in road.fragments]

    @staticmethod
    def _road_to_speed(road: Road):
        speeds = [(fragment.speed, fragment.length) for fragment in road.fragments]
        mean_speed = sum([speed * length for speed, length in speeds]) / sum([length for _, length in speeds])
        return mean_speed

    @staticmethod
    def _road_to_width(road: Road):
        widths = [(fragment.width, fragment.length) for fragment in road.fragments]
        mean_width = sum([width * length for width, length in widths]) / sum([length for _, length in widths])
        sd_width = math.sqrt(sum([(width - mean_width) ** 2 for width, _ in widths]) / (len(widths) - 1))
        return mean_width, 0.5  # to moze mieć troche za duzy wpływ więc na razie hard code

    @staticmethod
    def _road_to_bendiness(road: Road):
        bends = [(fragment.bendiness, fragment.length) for fragment in road.fragments]
        mean_bendiness = sum([bendiness * length for bendiness, length in bends]) / sum([length for _, length in bends])
        return mean_bendiness

    @staticmethod
    def _road_to_intersection_density(road: Road):
        return road.intersections / (road.length() * 1000)

    # TODO this is an api change to aid with refactor- this should probably be executed with mor forethought
    def get_average_daily_traffic(self, road: Road, percentile_speed=0.5):
        speed_data = Model._road_to_speed_data(road)
        width, sd_width = Model._road_to_width(road)
        bendiness = Model._road_to_bendiness(road)

        density_of_intersections = Model._road_to_intersection_density(road)  # and this is..too powerfull?
        print("density", density_of_intersections)
        print("road:", road,road.length())
        extra_lateral_clearance = 1.4

        return self._get_average_daily_traffic(
            speed_in_hours=speed_data,
            sd_paved_width=sd_width,
            paved_width=width,
            extra_lateral_clearance=extra_lateral_clearance,
            bendiness=bendiness,
            density_of_intersections=density_of_intersections,
            percentile_speed=percentile_speed
        )

    # TODO this is an api change to aid with refactor- this should probably be executed with mor fore thought
    def get_traffic_for_time_period(self, road: Road, duration_hours=1, percentile_speed=0.5):
        speed = road.fragments[0].speed
        width, sd_width = Model._road_to_width(road)
        bendiness = Model._road_to_bendiness(road)

        density_of_intersections = Model._road_to_intersection_density(road)
        extra_lateral_clearance = 1.4

        return self._get_traffic_for_time_period(
            speed=speed,
            sd_paved_width=sd_width,
            paved_width=width,
            extra_lateral_clearance=extra_lateral_clearance,
            bendiness=bendiness,
            density_of_intersections=density_of_intersections,
            duration_hours=duration_hours,
            percentile_speed=percentile_speed
        )

    # allows divide data from day into multiple periods
    def _get_average_daily_traffic(self, speed_in_hours: [(float, float)], sd_paved_width: float,
                                   paved_width: float,
                                   extra_lateral_clearance: float, bendiness: float,
                                   density_of_intersections: float,
                                   percentile_speed=0.5) -> float:
        measurement_duration = sum(x[1] for x in speed_in_hours)

        daily_traffic = sum([self._get_traffic_for_time_period(speed_in_hours[i][0], sd_paved_width, paved_width,
                                                               extra_lateral_clearance, bendiness,
                                                               density_of_intersections,
                                                               duration_hours=speed_in_hours[i][1],
                                                               percentile_speed=percentile_speed)
                             for i in range(len(speed_in_hours))]) / (measurement_duration / 24)

        return daily_traffic

    # as default uses average speed (percentile = 0.5)
    def _get_traffic_for_time_period(self, speed: float, sd_paved_width: float, paved_width: float,
                                     extra_lateral_clearance: float, bendiness: float,
                                     density_of_intersections: float,
                                     duration_hours=1, percentile_speed=0.5) -> float:
        # based on wiki.models Equation 1
        segment_characteristic = ((paved_width ** 0.079) * (extra_lateral_clearance ** 0.008) *
                                  (bendiness ** (-0.027)) * (density_of_intersections ** (-0.036)))

        # based on wiki.models Equation 1
        daily_traffic = math.exp(((math.log(speed) - (self.CONSTANT_COEFF + self.SEGMENT_CHARACTERISTIC_COEFF *
                                                      math.log(
                                                          segment_characteristic) + self.SD_PAVED_WIDTH__COEFF *
                                                      math.log(sd_paved_width) + (1 / self.THETA) * math.log(
                    percentile_speed)))
                                  / self.AVERAGE_DAILY_TRAFFIC_COEFF)) * (duration_hours / 24)

        return daily_traffic


def model_provider(module: str) -> Model:
    return Model()
# # to be deleted later
# def test_traffic_model():
#     speeds = [(60, 3), (50, 2), (40, 1)]
#     sd_paved_width = 0.5
#     paved_width = 4.4
#     extra_lateral_clearance = 1.4
#     bendiness = 199.3
#     density_of_intersections = 4.3
#     model = Model()
#     return model.get_average_daily_traffic(speeds, sd_paved_width, paved_width, extra_lateral_clearance,
#                                            bendiness, density_of_intersections)
#
#     print(test_traffic_model())
