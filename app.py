import overpy
import overpy.helper as helper
import sys
import simplejson as json

from urllib.request import urlopen

if __name__ == '__main__':


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
            road = {}
            road["name"] = way.tags.get("name", "n/a")
            road["speed_limit"] = way.tags.get("maxspeed", "n/a")
            nodes = []
            for node in way.nodes:
                nodes.append((node.lat, node.lon))
            road["nodes"] = nodes
            results_list.append(road)

        data = json.dumps(result.ways[0].tags, default=lambda o: o.__dict__)
        with open('data.txt', 'w') as outfile:
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

    results = maxspeed((37.7833, -122.4167), 500)
    results2 = tomtom((37.7802716, -122.4186146))

    intersection = helper.get_intersection(
        "Straße der Nationen",
        "Carolastraße",
        "3600062594"
    )

    print(json.dumps(results, indent=2))
    print(json.dumps(results2, indent=2))


