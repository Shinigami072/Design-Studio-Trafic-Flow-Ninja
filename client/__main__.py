from typing import Tuple

from controller.controller import Controller
from model import model
from road.road_provider import road_provider
import argparse
import sys
import json
import time
import os
from overpy.exception import OverpassGatewayTimeout, OverpassTooManyRequests
from timeout.timeout import TimeoutException


def main(pos: Tuple[float, float],
         tomtom_key: str,
         lookup_range: float,
         timeout: int,
         list_roads: bool,
         road: int,
         file_json:str,
         road_provider_name: str = "default_road_provider",
         model_name: str = "default_model"):
    controller = Controller(
        provider=road_provider(road_provider_name, tomtom_key),
        c_model=model.model(model_name)
    )
    for i in range(3):
        try:
            print("Road Query...")
            roads = controller.query_roads(pos)
        except OverpassGatewayTimeout:
            sys.stderr.write("WARNING: Couldn't list roads. Server load too high\n")
            print("Sleeping for 60s")
            time.sleep(60)
            continue
        except OverpassTooManyRequests:
            sys.stderr.write("WARNING: Couldn't list roads. Too many requests\n")
            print("Sleeping for 60s")
            time.sleep(60)
            continue
        break

    if road is None:
        print("No roads found.")
        exit()

    if list_roads:
        for i in range(len(roads)):
            print("road num:", i + 1, " - name:", roads[i])
    else:
        if len(roads) > 1:
            sys.stderr.write("WARNING: multiple roads detected\n")
        for i in range(len(roads)):
            print("road num:", i + 1, " - name:", roads[i])

        for i in range(3):
            try:
                print("Result Query...")
                result_str: str = controller.get_result(roads[max(0, min(road, len(roads) - 1))],
                                                                lookup_range / 2, pos, timeout)
                if file_json != "":
                    if not os.path.exists("json"):
                        os.makedirs("json")
                    with open("json/" + file_json, "w") as json_out:
                        json_out.write(result_str)

                result: dict = json.loads(result_str)
                road: dict = result.get("road")
                print("road:", road.get("name"))
                print("speed:", sum([fragment.get("speed") for fragment in road.get("fragments")])
                    / len(road.get("fragments")))
                print("extra lateral clearance:", sum([fragment.get("extra_lateral_clearance") for fragment in
                                            road.get("fragments")])
                    / len(road.get("fragments")))
                print("bendiness:", sum([fragment.get("bendiness") for fragment in road.get("fragments")])
                    / len(road.get("fragments")))
                print("width:", sum([fragment.get("width") for fragment in road.get("fragments")])
                    / len(road.get("fragments")))
                print("length:", sum([fragment.get("length") for fragment in road.get("fragments")]))
                print("intersections:", road.get("intersections"))
                print("cars per day: ", result.get("average_daily_traffic"))
            except OverpassGatewayTimeout:
                sys.stderr.write("WARNING: Couldn't get results. Server load too high\n")
                print("Sleeping for 60s")
                time.sleep(60)
                continue
            except OverpassTooManyRequests:
                sys.stderr.write("WARNING: Couldn't get results. Too many requests\n")
                print("Sleeping for 60s")
                time.sleep(60)
                continue
            except TimeoutException:
                sys.stderr.write("ERROR: Road provider timeout. Consider increasing timeout or reducing road length\n")
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Traffic Flow Ninja")
    parser.add_argument("latitude")
    parser.add_argument("longitude")
    parser.add_argument("--tomtom-key", default="EoqyQdOk9WolGiI6qmXDzWfPz3fG3G4X",
                        help="provide tomtom api key")
    parser.add_argument("--length", default=2000,
                        help="length of road taken into account (real road length will be slightly bigger)")
    parser.add_argument("--road", default=1, help="which road to chose (only has effect if there are multiple roads)")
    parser.add_argument("--list-roads", action='store_true', help="(toggle) List all roads at a certain position")
    parser.add_argument("--timeout", default=120,
                        help="timeout for road provider")
    parser.add_argument("--json", default="",
                        help="specify filename you want to dump results to in json format")
    parser.add_argument("--road-provider", default="cache_road_provider",
                        help="alternate module providing road geometry")
    parser.add_argument("--model", default="default_model",
                        help="alternate module processing road geometry")
    options = parser.parse_args()

    pos = (float(options.latitude), float(options.longitude))
    tomtom_key = options.tomtom_key
    lookup_range = int(options.length)
    list_roads = options.list_roads
    timeout = int(options.timeout)
    file_json = options.json
    road = int(options.road) - 1

    main(pos=pos, tomtom_key=tomtom_key, timeout=timeout, lookup_range=lookup_range, list_roads=list_roads, road=road,
         file_json=file_json, road_provider_name=options.road_provider, model_name=options.model)
