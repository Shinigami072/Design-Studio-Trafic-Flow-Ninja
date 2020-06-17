from typing import Tuple

from controller.Controller import Controller
from road.road_provider import road_provider
import argparse
import sys


def main(pos: Tuple[float, float],
         lookup_range: float,
         list_roads: bool = False,
         road: int = 0,
         road_provider_name: str = "cache_road_provider"):
    controller = Controller(
        provider=road_provider(road_provider_name)
    )
    roads = controller.query_roads(pos)

    if list_roads:
        for i in range(len(roads)):
            print("road num:", i+1, " - name:", roads[i])
    elif len(roads) > 1:
        sys.stderr.write("WARNING: multiple roads detected")

    print("cars per day: ",
        controller.get_result(
            roads[max(0, min(road, len(roads) - 1))], lookup_range/2, pos
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Traffic Flow Ninja")
    parser.add_argument("latitude")
    parser.add_argument("longitude")
    parser.add_argument("--length", default=1000,
                        help="length of road taken into account (real road length will be slightly bigger)")
    parser.add_argument("--list-roads", action='store_true', help="(toggle) List all roads at a certain position")
    parser.add_argument("--road", default=0, help="which road to chose (only has effect if there are multiple roads)")
    parser.add_argument("--road-provider", default="cache_road_provider",
                        help="alternate module providing road geometry")
    options = parser.parse_args()

    pos = (float(options.latitude), float(options.longitude))
    # pos = (49.66006, 19.26671)  # FOr Testing purposes
    lookup_range = int(options.length)
    list_roads = options.list_roads is not None
    road = int(options.road)

    main(pos=pos, lookup_range=lookup_range, list_roads=list_roads, road=road, road_provider_name=options.road_provider)
