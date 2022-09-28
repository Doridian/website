#!/usr/bin/env python3

from datetime import datetime, timezone
from hashlib import sha256
from os import stat
from sys import argv, stdout
from typing import TextIO

from validator import IPGeoFeedValidator
from config import subnets, __file__ as config_file


def generate(out: TextIO) -> bool:
    fstat = stat(config_file)
    ftime = datetime.fromtimestamp(fstat.st_mtime, tz=timezone.utc)
    timestr = ftime.isoformat(timespec="seconds")

    lines = []

    for subnet in sorted(subnets):
        lines.append(
            f"{subnet.subnet},{subnet.loc.country},{subnet.loc.state},{subnet.loc.city},{subnet.loc.zip}")

    validator = IPGeoFeedValidator()
    validator.validate(lines)

    if validator.had_errors:
        print("Error(s) during validating generated Geofeed. This is a bug!")
        return False

    output = ("\n".join(lines)) + "\n"

    hash = sha256()
    hash.update(output.encode("utf-8"))

    out.write(f"# Doridian Network geofeed according to RFC 8805\n")
    out.write(f"# Last update: {timestr}\n")
    out.write(f"# Number of networks: {len(subnets)}\n")
    out.write(f"# Content SHA256 hash (excluding comments): {hash.hexdigest()}\n")
    out.write(output)
    out.write(f"# End of file\n")
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
