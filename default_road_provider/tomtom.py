import json
import time
from decimal import Decimal
from typing import Tuple, Dict
from urllib.error import HTTPError
from urllib.request import urlopen


class TomTomClient:
    def __init__(self, api_key: str = "4PUqim975O4HaVk292zznuwhgHboq7k4",
                 base_url: str = "api.tomtom.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.count = 0

    def get_segment_data(self, coordinate: Tuple[Decimal, Decimal]) -> Dict[str, str]:
        version = 4
        zoom = 10
        lat, lon = coordinate
        point = "{lat:.5f}%2C{lon:.5f}".format(
            lat=lat,
            lon=lon
        )
        tomtom_url = \
            "https://{base_url}" \
            "/traffic/services/{version}" \
            "/flowSegmentData/absolute/{zoom}/" \
            "json?point={point}&unit={unit}&key={key}" \
                .format(
                base_url=self.base_url,
                version=version,
                zoom=zoom,
                unit="KMPH",
                point=point,
                key=self.api_key
            )
        try:
            self.count = self.count + 1
            tomtom_data = urlopen(tomtom_url).read()
            tomtom_map = json.loads(tomtom_data)
            return tomtom_map['flowSegmentData']
        except HTTPError as ex:
            print(ex)
            if ex.code == 403:
                self.count = 0
                time.sleep(120)
                return self.get_segment_data(coordinate)

            parsed = json.load(ex)
            if parsed['error'] == "Point too far from nearest existing segment.":
                return None

            print(ex)
            print(parsed)
            raise ex

    def get_current_speed(self, coordinate: Tuple[Decimal, Decimal]) -> float:
        try:
            data = self.get_segment_data(coordinate)
            if data is None:
                return None
            return float(data["currentSpeed"])
        except HTTPError:
            return None
