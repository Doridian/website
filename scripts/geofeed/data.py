from dataclasses import dataclass


@dataclass(eq=True, frozen=True, order=True)
class GeoLoc:
    country: str
    region: str
    city: str
    zip: str

    def full_region(self) -> str:
        if self.region and "-" not in self.region:
            return f"{self.country}-{self.region}"
        return self.region


@dataclass(eq=True, frozen=True, order=True)
class IPNet:
    loc: GeoLoc
    subnet: str
