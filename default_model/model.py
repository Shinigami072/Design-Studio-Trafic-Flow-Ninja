import math

from model import model
from road import Road
import sys


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

    @staticmethod
    def print_warning(speed: float, bendiness: float, density_of_intersections: float, length: float):
        if speed < 42.0:
            sys.stderr.write(
                "WARNING: The speed was below the range the model was calibrated for (40.0). "
                "The result  might be too high due to overfitting on the range edges. Please try "
                "increasing --length parameter to eliminate this problem. Also make sure there are no traffic light "
                "on the road as this will invalidate the results.\n")
        if bendiness < 39.0:
            sys.stderr.write(
                "WARNING: The bendiness was below the range the model was calibrated for (39.0). "
                "The result too low due to overfitting on the range edges. "
                "Please try increasing --length parameter to eliminate this problem.\n")
        if bendiness > 682.3:
            sys.stderr.write(
                "WARNING: The bendiness was below the range the model was calibrated for (682.3). "
                "The result might too low due to overfitting on the range edges. "
                "Please try increasing --length parameter to eliminate this problem.\n")
        if density_of_intersections < 0.5:
            sys.stderr.write(
                "WARNING: The density of intersections was below the range the model was calibrated for (0.5). "
                "The result might be too high to overfitting on the "
                "range edges. Please try increasing --length parameter to eliminate this problem.\n")
        if density_of_intersections > 7.0:
            sys.stderr.write(
                "WARNING: The density of intersections was above the range the model was calibrated for (7.0). "
                "The result might be too low due to overfitting on the "
                "range edges. Please try increasing --length parameter to eliminate this problem.\n")
        if length < 1000:
            sys.stderr.write(
                "WARNING: Using road fragments longer then 1000m is recommended. "
                "The result might be incorrect\n")

    def get_average_daily_traffic(self, road: Road, percentile_speed=0.5):
        duration_hours = 24
        speed = Model._road_to_speed(road)
        width = Model._road_to_width(road)
        bendiness = Model._road_to_bendiness(road)

        density_of_intersections = Model._road_to_intersection_density(road)
        extra_lateral_clearance = Model._road_to_extra_lateral_clearance(road)

        self.print_warning(speed, bendiness, density_of_intersections, road.length())

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
