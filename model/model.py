from abc import ABC

from road import Road


class Model(ABC):
    def get_average_daily_traffic(self, road: Road, percentile_speed=0.5) -> float:
        pass


def model(module: str) -> Model:
    mod = __import__(module)
    return mod._create_model()
