from decimal import Decimal
from typing import Tuple, List

from road import Road, Fragment, RoadProvider, road_provider
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

    @staticmethod
    def _coords_to_length(coords: List[Tuple[Decimal, Decimal]]) -> float:
        return sum([g_utils.coords_to_m(_from, _to) for _from, _to in zip(coords[:-1], coords[1:])])

    @staticmethod
    def _coords_to_bendiness(coords: List[Tuple[Decimal, Decimal]]) -> float:
        total_bend = sum(
            [g_utils.coords_to_m(_from, _to) for _from, _through, _to in zip(coords[:-2], coords[1:-1], coords[2:])])
        return total_bend

    @staticmethod
    def _way_to_fragments(way: overpy.Way) -> List[Fragment]:
        # TODO make this transformation use actual data
        nodes: List[overpy.Node] = way.nodes
        coords: List[Tuple[Decimal, Decimal]] = [(Decimal(c.lon), Decimal(c.lat)) for c in nodes]
        width: float = way.tags.get("width", pr.min_width(way))
        speed: float = float(way.tags.get("maxspeed", 0))
        length: float = DefaultRoadProvider._coords_to_length(coords)
        bendiness: float = DefaultRoadProvider._coords_to_bendiness(coords)
        return [Fragment(width=width, speed=speed, length=length, coords=coords, bendiness=bendiness)]

    @staticmethod
    def _way_to_primary_coord(way: overpy.Way) -> Tuple[Decimal, Decimal]:
        return Decimal(way.center_lat), Decimal(way.center_lon)

    def provide(self, name: DefaultRoadId) -> Road:
        result = self.api.query(
            """
                (
                  relation(id:{id});
                  way[name="{name}"][unsigned_ref="{ref}"][highway~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|tertiary|unclassified|residential|living_street|service|track"];
                  node(w);
                );
                
                out meta;
            """.format(id=name.road_id, ref=name.ref, name=name.name)
        )
        ways = sorted(result.ways, key=self._way_to_primary_coord)
        road_fragments = [i
                          for way in ways
                          for i in self._way_to_fragments(way)]
        return Road(name.name, road_fragments)

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


if __name__ == "__main__":
    prov = road_provider("default_road_provider")
    for road_id in prov.names((52.2565098, 21.0291088)):
        prov.provide(road_id)
