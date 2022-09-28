#!/usr/bin/env python3

from datetime import datetime, timezone
from hashlib import sha256
from os import stat
from sys import argv, stdout
from typing import TextIO

from validator import GeoFeedValidator
from config import subnets, __file__ as config_file


def generate(out: TextIO) -> bool:
    fstat = stat(config_file)
    ftime = datetime.fromtimestamp(fstat.st_mtime, tz=timezone.utc)
    timestr = ftime.isoformat(timespec="seconds")

    lines: list[str] = []

    for subnet in sorted(subnets):
        lines.append(
            f"{subnet.subnet},{subnet.loc.country},{subnet.loc.full_region()},{subnet.loc.city},{subnet.loc.zip}")

    output = ("\n".join(lines)) + "\n"

    hash = sha256()
    hash.update(output.encode("utf-8"))

    full_output = f"""# Doridian Network geofeed according to RFC 8805
# Last update: {timestr}
# Number of networks: {len(subnets)}
# Content SHA256 hash (excluding comments): {hash.hexdigest()}
{output}# End of file
"""

    validator = GeoFeedValidator()
    if not validator.run(full_output):
        print("Error(s) during validating generated Geofeed. This is a bug!")
        validator.write_errors(stdout)
        return False

    out.write(full_output)
    out.flush()
    return True


if __name__ == "__main__":
    ok = False
    if len(argv) > 1:
        with open(argv[1], "w") as fh:
            ok = generate(fh)
    else:
        ok = generate(stdout)

    if not ok:
        exit(1)
