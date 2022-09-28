from dataclasses import dataclass
from typing import Any


@dataclass(eq=True, frozen=True)
class GeoLoc:
    country: str
    state: str
    city: str
    zip: str


@dataclass(frozen=True)
class IPNet:
    loc: GeoLoc
    subnet: str

    def __hash__(self) -> int:
        return self.subnet.__hash__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IPNet):
            return False
        return self.subnet == other.subnet

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, IPNet):
            return False
        return self.subnet < other.subnet
