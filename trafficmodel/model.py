import math


class Model:
    # as in wiki.models Table 2
    CONSTANT_COEFF = 4.846
    SEGMENT_CHARACTERISTIC_COEFF = 4.462
    SD_PAVED_WIDTH__COEFF = -0.15
    AVERAGE_DAILY_TRAFFIC_COEFF = -0.064
    # coefficient that allows use for different speed percentiles
    THETA = 5.947

    # allows divide data from day into multiple periods
    def get_average_daily_traffic(self, speed_in_hours: [(float, float)], sd_paved_width: float, paved_width: float,
                                  extra_lateral_clearance: float, bendiness: float, density_of_intersections: float,
                                  percentile_speed=0.5) -> float:

        measurement_duration = sum(speed_in_hours[1])

        daily_traffic = sum([self.get_traffic_for_time_period(speed_in_hours[i][0], sd_paved_width, paved_width,
                                                              extra_lateral_clearance, bendiness,
                                                              density_of_intersections,
                                                              duration_hours=speed_in_hours[i][1])
                             for i in range(len(speed_in_hours))]) / (measurement_duration/24)

        return daily_traffic

    # as default uses average speed (percentile = 0.5)
    def get_traffic_for_time_period(self, speed: float, sd_paved_width: float, paved_width: float,
                                    extra_lateral_clearance: float,bendiness: float, density_of_intersections: float,
                                    duration_hours=1, percentile_speed=0.5) -> float:

        segment_characteristic = ((paved_width ** 0.079) * (extra_lateral_clearance ** 0.008) *
                                  (bendiness ** (-0.027)) * (density_of_intersections ** (-0.036)))

        # based on wiki.models Equation 1
        return math.exp(((math.log(speed) - (self.CONSTANT_COEFF + self.SEGMENT_CHARACTERISTIC_COEFF *
                                             math.log(segment_characteristic) + self.SD_PAVED_WIDTH__COEFF *
                                             math.log(sd_paved_width) + (1/self.THETA) * math.log(percentile_speed)))
                         / self.AVERAGE_DAILY_TRAFFIC_COEFF)) * (duration_hours/24)


# to be deleted later
def test_traffic_model():
    speeds = [(60, 3), (50, 2), (40, 1)]
    sd_paved_width = 0.5
    paved_width = 4.4
    extra_lateral_clearance = 1.4
    bendiness = 199.3
    density_of_intersections = 4.3
    model = Model()
    return model.get_average_daily_traffic(speeds, sd_paved_width, paved_width, extra_lateral_clearance,
                                            bendiness, density_of_intersections)


print(test_traffic_model())
