import math

from model import model
from road import Road


class Model(model.Model):
    # as in wiki.models Table 2
    CONSTANT_COEFF = 4.846
    SEGMENT_CHARACTERISTIC_COEFF = 4.462
    SD_PAVED_WIDTH_COEFF = -0.15
    AVERAGE_DAILY_TRAFFIC_COEFF = -0.064
    # coefficient that allows use for different speed percentiles
    THETA = 5.947
    SD_PAVED_WIDTH = 0.5

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
        return mean_width

    @staticmethod
    def _road_to_extra_lateral_clearance(road: Road):
        extra_lateral_clearances = [(fragment.extra_lateral_clearance, fragment.length) for fragment in road.fragments]
        mean_extra_lateral_clearance = sum([elc * length for elc, length in extra_lateral_clearances]) / \
                                       sum([length for _, length in extra_lateral_clearances])
        return mean_extra_lateral_clearance

    @staticmethod
    def _road_to_bendiness(road: Road):
        bends = [(fragment.bendiness, fragment.length) for fragment in road.fragments]
        mean_bendiness = sum([bendiness * length for bendiness, length in bends]) / sum([length for _, length in bends])
        return mean_bendiness

    @staticmethod
    def _road_to_intersection_density(road: Road):
        return road.intersections / (road.length() / 1000)

    def get_average_daily_traffic(self, road: Road, percentile_speed=0.5):
        duration_hours = 24
        speed = Model._road_to_speed(road)
        width = Model._road_to_width(road)
        bendiness = Model._road_to_bendiness(road)

        density_of_intersections = Model._road_to_intersection_density(road)
        print("density", density_of_intersections)
        print("road:", road, road.length())
        extra_lateral_clearance = Model._road_to_extra_lateral_clearance(road)

        return self._get_average_daily_traffic(
            speed=speed,
            sd_paved_width=self.SD_PAVED_WIDTH,
            paved_width=width,
            extra_lateral_clearance=extra_lateral_clearance,
            bendiness=bendiness,
            density_of_intersections=density_of_intersections,
            duration_hours=duration_hours,
            percentile_speed=percentile_speed
        )

    # as default uses average speed (percentile = 0.5)
    def _get_average_daily_traffic(self, speed: float, sd_paved_width: float, paved_width: float,
                                     extra_lateral_clearance: float, bendiness: float,
                                     density_of_intersections: float,
                                     duration_hours, percentile_speed) -> float:
        # based on wiki.models Equation 1
        segment_characteristic = ((paved_width ** 0.079) * (extra_lateral_clearance ** 0.008) *
                                  (bendiness ** (-0.027)) * (density_of_intersections ** (-0.036)))

        # based on wiki.models Equation 1
        daily_traffic = math.exp(((math.log(speed) - (self.CONSTANT_COEFF + self.SEGMENT_CHARACTERISTIC_COEFF *
                                                      math.log(
                                                          segment_characteristic) + self.SD_PAVED_WIDTH_COEFF *
                                                      math.log(sd_paved_width) + (1 / self.THETA) * math.log(
                    percentile_speed)))
                                  / self.AVERAGE_DAILY_TRAFFIC_COEFF)) * (duration_hours/24)

        return daily_traffic


def _create_model() -> Model:
    return Model()
