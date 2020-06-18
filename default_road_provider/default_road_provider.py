from decimal import Decimal
from typing import Tuple, List

from default_road_provider.tomtom import TomTomClient
from road import Road, Fragment, RoadProvider
import overpy
import math
import overpy.helper
import default_road_provider.polish_roads as pr
import default_road_provider.geo_utils as g_utils


class DefaultRoadProvider(RoadProvider):
    class DefaultRoadId(RoadProvider.RoadId):
        def __init__(self, road_id: int, ref: str, name: str):
            self.road_id = road_id
            self.name = name
            self.ref = ref

        def __eq__(self, other):
            return other.isinstance(DefaultRoadProvider) and self.road_id == other.road_id

        def __hash__(self):
            return self.road_id

        def __str__(self):
            return self.name

        def __repr__(self):
            return "[{id}] {name}".format(id=self.road_id, name=self.name)

    @staticmethod
    def _way_to_id(way: overpy.Way) -> DefaultRoadId:
        return DefaultRoadProvider.DefaultRoadId(way.id, way.tags.get("unsigned_ref", ""),
                                                 str(way.tags.get("name", "")))

    def __init__(self, tomtom_key: str):
        self.api = overpy.Overpass()
        self.tomtom = TomTomClient(tomtom_key)

    @staticmethod
    def _coords_to_length(coords: List[Tuple[Decimal, Decimal]]) -> float:
        return sum([g_utils.coords_to_m(_from, _to) for _from, _to in zip(coords[:-1], coords[1:])])

    @staticmethod
    def _coords_to_bendiness(coords: List[Tuple[Decimal, Decimal]], length: float) -> float:
        total_bend = sum(
            [g_utils.coords_to_bend_deg(_from, _through, _to) for _from, _through, _to in
             zip(coords[:-2], coords[1:-1], coords[2:])])

        return total_bend / (length / 1000)

    @staticmethod
    def _have_shoulder(way: overpy.Way) -> bool:
        return way.tags.get("shoulder", "no") != "no" or way.tags.get("shoulder:both", "no") != "no"

    @staticmethod
    def _way_to_center_coords(way: overpy.Way) -> Tuple[Decimal, Decimal]:
        center_lat = way.center_lat
        nodes: List[overpy.Node] = way.nodes
        node_count = len(nodes)
        if center_lat is None:
            center_lat = sum([n.lat for n in nodes]) / node_count
        center_lon = way.center_lon

        if center_lon is None:
            center_lon = sum([n.lon for n in nodes]) / node_count

        return Decimal(center_lat), Decimal(center_lon)

    @staticmethod
    def _ways_to_number_of_intersections(selected_way: overpy.Way, ways: List[overpy.Way]):
        local_intersections = 0
        for way in ways:
            if selected_way.tags.get("highway") in ["motorway", "motorway_link", "trunk", "trunk_link"]:
                for way in ways:
                    if not way.tags.get("highway") in ["motorway", "motorway_link", "trunk", "trunk_link"] \
                            or (
                            selected_way.tags.get("ref") == way.tags.get("ref") and way.tags.get("ref") is not None):
                        local_intersections += 1
                return math.ceil((len(ways) - local_intersections) / 2)
            else:
                for way in ways:
                    if way.tags.get("surface") != "asphalt" \
                            and (way.tags.get("highway") in ["living_street", "service", "track"]) \
                            or (selected_way.tags.get("ref") == way.tags.get("ref") and way.tags.get("ref") is not None) \
                            or (selected_way.tags.get("name") == way.tags.get("name")):
                        local_intersections += 1
                return len(ways) - local_intersections

    def _way_to_fragments(self, way: overpy.Way) -> List[Fragment]:
        nodes: List[overpy.Node] = way.nodes
        coords: List[Tuple[Decimal, Decimal]] = [(Decimal(c.lat), Decimal(c.lon)) for c in nodes]
        lane_width: float = float(way.tags.get("width", pr.min_width(way)))
        extra_lateral_clearance: float = float(
            way.tags.get("shoulder:width", pr.min_extra_lateral_clearance(way, self._have_shoulder(way))))
        length: float = DefaultRoadProvider._coords_to_length(coords)
        speed: float = self.get_current_speed(coords)
        bendiness: float = DefaultRoadProvider._coords_to_bendiness(coords, length)

        return [Fragment(width=lane_width + extra_lateral_clearance, extra_lateral_clearance=extra_lateral_clearance,
                         speed=speed, length=length, coords=coords, bendiness=bendiness)]

    def get_current_speed(self, coords: List[Tuple[Decimal, Decimal]]):
        speed: float = self.tomtom.get_current_speed(coords[len(coords) // 2])

        if speed is None:
            for c in coords:
                speed = self.tomtom.get_current_speed(c)
                if speed is not None:
                    break
        return speed

    def provide(self, name: DefaultRoadId, radius: float, location: Tuple[float, float]) -> Road:
        lat, lon = location

        result = self.api.query(
            """
                way(id:{id});
                node(w);
                complete {{
                (
                    way(bn)[name="{name}"][unsigned_ref="{ref}"][highway~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track)$"](around:{radius},{lat},{lon});
                    node(w);  	
                );
                
                out meta;
            """.format(id=name.road_id, ref=name.ref, name=name.name, radius=radius, lat=lat, lon=lon)
        )

        ways = sorted(result.ways, key=self._way_to_center_coords)
        road_fragments = [i
                          for way in ways
                          for i in self._way_to_fragments(way)]

        result = self.api.query(
            """
                way(id:{id});
                node(w);
                complete {{
                (
                    way(bn)[name="{name}"][unsigned_ref="{ref}"][highway~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track)$"](around:{radius},{lat},{lon});
                    node(w);  	
                ) -> .searched_way;

                }};
                
                way(around.searched_way:0)[name!="{name}"][highway~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track)$"];
                
                out meta;
            """.format(id=name.road_id, ref=name.ref, name=name.name, radius=radius, lat=lat, lon=lon)
        )
        intersections = self._ways_to_number_of_intersections(ways[0], result.ways)
        return Road(name.name, road_fragments, intersections)

    def names(self, location: Tuple[float, float]) -> List[DefaultRoadId]:
        lat, lon = location

        ways = self.api.query(
            """
                way[highway](around:{radius},{lat},{lon});
                out meta;
            """.format(radius=20, lat=lat, lon=lon)
        ).ways

        return [self._way_to_id(way) for way in ways]


def _create_road_provider(tomtom_key: str) -> RoadProvider:
    return DefaultRoadProvider(tomtom_key)
