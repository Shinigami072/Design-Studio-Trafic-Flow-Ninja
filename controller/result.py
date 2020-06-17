import json

from road.road import Road


class Result:

    def __init__(self,
                 road: Road,
                 average_daily_traffic: float):
        for fragment in road.fragments:
            fragment.coords = [(float(coord[0]), float(coord[1])) for coord in fragment.coords]
        self.road = road
        self.average_daily_traffic = average_daily_traffic

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)
