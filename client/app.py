import time

import overpy
import overpy.helper as helper
import sys
import simplejson as json

from urllib.request import urlopen

from road import road_provider


def main():
    prov = road_provider("default_road_provider")
    coord = (52.2565098, 21.0291088)
    try:
        for road_id in prov.names(coord):
            print(prov.provide(road_id))
    except overpy.exception.OverpassTooManyRequests:
        print("TooManyReqests")
        time.sleep(180)
        main()


if __name__ == "__main__":
    main()

if __name__ == '__main__' and False:

    # pip install overpy
    # python overpass_speed.py 37.7833 -122.4167 500

    def maxspeed(coordinates, radius):
        lat, lon = coordinates
        api = overpy.Overpass()

        # fetch all ways and nodes
        result = api.query("""
                way(around:""" + str(radius) + """,""" + str(lat) + """,""" + str(lon) + """) ["maxspeed"];
                    (._;>;);
                        out body;
                            """)
        results_list = []
        for way in result.ways:
            road = {"name": way.tags.get("name", "n/a"), "speed_limit": way.tags.get("maxspeed", "n/a")}
            nodes = []
            for node in way.nodes:
                nodes.append((node.lat, node.lon))
            road["nodes"] = nodes
            results_list.append(road)

        data = json.dumps(result.ways[0].tags, default=lambda o: o.__dict__)
        with open('data.json', 'w') as outfile:
            outfile.write(str(data))

        return results_list


    def tomtom(coordinates):

        # URL to the tomtom api
        apiURL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10"
        # apiKey
        apiKey = "4PUqim975O4HaVk292zznuwhgHboq7k4 "

        # [coordinates]
        lat, lon = coordinates

        tomtomURL = "%s/json?point=%s%%2C%s&unit=KMPH&key=%s" % (apiURL, lat, lon, apiKey)

        getData = urlopen(tomtomURL).read()
        jsonTomTomString = json.loads(getData)

        result = jsonTomTomString['flowSegmentData']

        return result


    results = maxspeed((52.235086, 20.965497), 500)
    results2 = tomtom((52.235086, 20.965497))

    intersection = helper.get_intersection(
        "Straße der Nationen",
        "Carolastraße",
        "3600062594"
    )

    print(json.dumps(results, indent=2))
    print(json.dumps(results2, indent=2))
