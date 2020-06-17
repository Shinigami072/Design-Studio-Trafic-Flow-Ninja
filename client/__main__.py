from typing import Tuple

from controller.Controller import Controller
from model import model
from road.road_provider import road_provider
import argparse
import sys


def main(pos: Tuple[float, float],
         list_roads: bool = False,
         road: int = 0,
         road_provider_name: str = "default_road_provider",
         model_name: str = "default_model"):
    controller = Controller(
        provider=road_provider(road_provider_name),
        c_model=model.model(model_name)
    )
    print("Road Query...")
    roads = controller.query_roads(pos)

    if list_roads:
        for i in range(len(roads)):
            print("road num:", i + 1, " - name:", roads[i])
    elif len(roads) > 1:
        sys.stderr.write("WARNING: multiple roads detected")

    print("cars per hour: ",
          controller.get_result(
              roads[max(0, min(road, len(roads) - 1))]
          )
          )


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Traffic Flow Ninja")
    parser.add_argument("latitude")
    parser.add_argument("longitude")
    parser.add_argument("--list-roads", action='store_true', help="(toggle) List all roads at a certain position")
    parser.add_argument("--road", default=0, help="which road to chose (only has effect if there are multiple roads)")
    parser.add_argument("--road-provider", default="default_road_provider",
                        help="alternate module providing road geometry")
    parser.add_argument("--model", default="default_model",
                        help="alternate module processing road geometry")
    options = parser.parse_args()

    pos = (float(options.latitude), float(options.longitude))
    # pos = (49.66006, 19.26671)  # FOr Testing purposes
    list_roads = options.list_roads is not None
    road = int(options.road)

    main(pos=pos, list_roads=list_roads, road=road, road_provider_name=options.road_provider, model_name=options.model)
