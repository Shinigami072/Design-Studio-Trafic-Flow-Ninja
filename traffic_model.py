import math


def traffic_model(v_max, sd_paved_width, paved_width, extra_lateral_clearance, bendiness, density_of_intersections):
    a_0 = 4.846
    a_1 = 4.462
    a_2 = -0.125
    a_3 = -0.064
    theta = 5.947
    sc = paved_width**0.079 * extra_lateral_clearance**0.008 * bendiness**(-0.027) * density_of_intersections**(-0.036)
    test = (math.log(v_max) - (a_0 + a_1 * math.log(sc) + a_2 * math.log(sd_paved_width)))/a_3
    test2 = math.exp(a_0 + a_1 * math.log(sc) + a_2 * math.log(sd_paved_width) + a_3 * math.log(6193))
    return math.exp((math.log(v_max) - (a_0 + a_1 * math.log(sc) + a_2 * math.log(sd_paved_width)))/a_3)

def test_traffic_model():
    v_max = 60
    sd_paved_width = 0.5
    paved_width = 4.4
    extra_lateral_clearance = 1.4
    bendiness = 199.3
    density_of_intersections = 4.3
    return traffic_model(v_max, sd_paved_width, paved_width, extra_lateral_clearance, bendiness, density_of_intersections)


print(test_traffic_model())