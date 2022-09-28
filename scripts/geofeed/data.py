from dataclasses import dataclass


@dataclass(eq=True, frozen=True, order=True)
class GeoLoc:
    country: str
    region: str
    city: str
    zip: str


@dataclass(eq=True, frozen=True, order=True)
class IPNet:
    loc: GeoLoc
    subnet: str
