from typing import Tuple, List

from road import Road, Fragment, RoadProvider, road_provider
import overpy
import overpy.helper


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
        return DefaultRoadProvider.DefaultRoadId(way.id, way.tags.get("unsigned_ref",""), str(way.tags.get("name", "")))

    def __init__(self):
        self.api = overpy.Overpass()

    @staticmethod
    def _way_to_fragments(way: overpy.Way) -> List[Fragment]:
        # TODO make this transformation use actual data
        width: float = 1.5 * int(way.tags.get("lanes", 1))
        speed: float = 1.1 * float(way.tags.get("maxspeed", 0))
        return [Fragment(width=width, speed=speed)]

    def provide(self, name: DefaultRoadId) -> Road:
        #TODO limit results to only car roads
        result = self.api.query(
            """
                (
                  relation(id:{id});
                  way[name="{name}"][unsigned_ref="{ref}"][highway];
                  node(w);
                );
                
                out meta;
            """.format(id=name.road_id, ref=name.ref, name=name.name)
        )

        road_fragments = [i
                          for way in result.ways
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
