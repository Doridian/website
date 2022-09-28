#!/usr/bin/env python3

from dataclasses import dataclass
from datetime import datetime, timezone
from os import stat
from sys import argv

from geofeed_validator import IPGeoFeedValidator

@dataclass(eq=True, frozen=True)
class GeoLoc:
    country: str
    state: str
    city: str
    zip: str

@dataclass(eq=True, frozen=True)
class IPNet:
    loc: GeoLoc
    subnet: str


LOC = GeoLoc(country="US", state="US-WA", city="Seattle", zip="")

SUBNETS = set([
    IPNet(subnet="2a0e:7d44:f000::/40", loc=LOC),
    IPNet(subnet="2a0e:8f02:21c0::/44", loc=LOC),
])

fstat = stat(__file__)
ftime = datetime.fromtimestamp(fstat.st_mtime, tz=timezone.utc)
timestr = ftime.isoformat(timespec="seconds")

lines = [
    "# Doridian network Geofeed according to RFC 8805",
    f"# Last update to the Geofeed: {timestr}",
]

for subnet in SUBNETS:
    lines.append(f"{subnet.subnet},{subnet.loc.country},{subnet.loc.state},{subnet.loc.city},{subnet.loc.zip}")

validator = IPGeoFeedValidator()
validator.Validate(lines)

if validator.CountErrors("ERROR") > 0:
    raise Exception("Error during validating generated Geofeed. This is a bug!")

with open(argv[1], "w") as fh:
    fh.write("\n".join(lines))
    fh.write("\n")
