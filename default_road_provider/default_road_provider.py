from decimal import Decimal
from typing import Tuple, List

from default_road_provider.tomtom import TomTomClient
from road import Road, Fragment, RoadProvider
import overpy
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

    def __init__(self):
        self.api = overpy.Overpass()
        self.tomtom = TomTomClient()

    @staticmethod
    def _coords_to_length(coords: List[Tuple[Decimal, Decimal]]) -> float:
        return sum([g_utils.coords_to_m(_from, _to) for _from, _to in zip(coords[:-1], coords[1:])])

    @staticmethod
    def _coords_to_bendiness(coords: List[Tuple[Decimal, Decimal]], length: float) -> float:
        total_bend = sum(
            [g_utils.coords_to_bend_deg(_from, _through, _to) for _from, _through, _to in
             zip(coords[:-2], coords[1:-1], coords[2:])])

        return total_bend / (length / 1000)

    def _way_to_fragments(self, way: overpy.Way) -> List[Fragment]:
        # TODO make this transformation use actual data
        nodes: List[overpy.Node] = way.nodes
        coords: List[Tuple[Decimal, Decimal]] = [(Decimal(c.lat), Decimal(c.lon)) for c in nodes]
        width: float = float(way.tags.get("width", pr.min_width(way)))
        speed: float = self.tomtom.get_current_speed(coords[len(coords) // 2])
        length: float = DefaultRoadProvider._coords_to_length(coords)

        if speed is None:
            for c in coords:
                speed: float = self.tomtom.get_current_speed(c)
                if speed is not None:
                    break
        bendiness: float = DefaultRoadProvider._coords_to_bendiness(coords, length)

        return [Fragment(width=width, speed=speed, length=length, coords=coords, bendiness=bendiness)]

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

    def provide(self, name: DefaultRoadId) -> Road:
        result = self.api.query(
            """
                
                way(id:{id});
                node(w);
                complete {{
                (
                    way(bn)[name="{name}"][unsigned_ref="{ref}"][highway~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track)$"];
                    node(w);  	
                );
                
                out meta;
            """.format(id=name.road_id, ref=name.ref, name=name.name)
        )

        ways = sorted(result.ways, key=self._way_to_center_coords)
        road_fragments = [i
                          for way in ways
                          for i in self._way_to_fragments(way)]

        # This could be handled by overpass - but our api wrapper does not support custom types -> so we have to work
        # around it
        # TODO reduce the ammount of streets detected as intersections
        result = self.api.query(
            """

                way(id:{id});
                node(w);
                complete {{
                (
                    way(bn)[name="{name}"][unsigned_ref="{ref}"][highway~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track)$"];
                    node(w);  	
                ) -> .searched_way;

                }};
                
                way(around.searched_way:0)[name!="{name}"][highway~"^(motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track)$"];
                
                out meta;
            """.format(id=name.road_id, ref=name.ref, name=name.name)
        )
        intersections = len(result.ways)
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


def _create_road_provider() -> RoadProvider:
    return DefaultRoadProvider()
