import time

import overpy
import overpy.helper as helper
import sys
import simplejson as json

from urllib.request import urlopen
from controller.Controller import Controller

from road import road_provider


def main():
    # prov = road_provider("default_road_provider")
    coord = (49.66006, 19.26671)
    controller = Controller()
    roads = controller.query_roads(coord)
    if len(roads) == 1:
        print(controller.get_result(roads[0]))
    else:
        print(roads)


if __name__ == "__main__":
    main()
