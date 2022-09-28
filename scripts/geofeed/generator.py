#!/usr/bin/env python3

from datetime import datetime, timezone
from os import stat
from sys import argv, stdout
from typing import TextIO

from validator import IPGeoFeedValidator
from config import subnets, __file__ as config_file


def generate(out: TextIO) -> bool:
    fstat = stat(config_file)
    ftime = datetime.fromtimestamp(fstat.st_mtime, tz=timezone.utc)
    timestr = ftime.isoformat(timespec="seconds")

    lines = [
        "# Doridian network Geofeed according to RFC 8805",
        f"# Last update to the Geofeed: {timestr}",
    ]

    for subnet in subnets:
        lines.append(
            f"{subnet.subnet},{subnet.loc.country},{subnet.loc.state},{subnet.loc.city},{subnet.loc.zip}")

    validator = IPGeoFeedValidator()
    validator.validate(lines)

    if validator.had_errors:
        print("Error(s) during validating generated Geofeed. This is a bug!")
        return False

    out.write("\n".join(lines))
    out.write("\n")
    out.flush()
    return True


if __name__ == "__main__":
    res = False
    if len(argv) > 1:
        with open(argv[1], "w") as fh:
            res = generate(fh)
    else:
        res = generate(stdout)

    if not res:
        exit(1)
