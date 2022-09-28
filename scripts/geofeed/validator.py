#!/usr/bin/python
#
# Copyright (c) 2012 IETF Trust and the persons identified as
# authors of the code.  All rights reserved.  Redistribution and use
# in source and binary forms, with or without modification, is
# permitted pursuant to, and subject to the license terms contained
# in, the Simplified BSD License set forth in Section 4.c of the
# IETF Trust"s Legal Provisions Relating to IETF
# Documents (http://trustee.ietf.org/license-info).

"""Simple format validator for self-published ipgeo feeds.

    This tool reads CSV data in the self-published ipgeo feed format
    from the standard input and performs basic validation.  It is
    intended for use by feed publishers before launching a feed.
    """

import csv
import ipaddress
import sys
from typing import Iterable, TextIO


class IPGeoFeedValidator:
    line_number: int
    output_stream: TextIO
    is_correct_line: bool
    had_errors: bool

    def __init__(self) -> None:
        self.line_number = 0
        self.is_correct_line = False
        self.had_errors = False
        self.set_output_stream(sys.stderr)

    def validate(self, feed: Iterable[str]) -> None:
        """Check validity of an IPGeo feed.

        Args:
          feed: iterable with feed lines
        """

        self.line_number = 0
        self.had_errors = False

        for line in feed:
            self._validate_line(line)

    def set_output_stream(self, logfile: TextIO) -> None:
        """Controls where the output messages go do (STDERR by default).

        Use None to disable logging.

        Args:
          logfile: a file object (e.g., sys.stdout) or None.
        """
        self.output_stream = logfile

    ############################################################
    def _validate_line(self, line: str) -> bool:
        line = line.rstrip("\r\n")
        self.line_number += 1
        self.line = line.split("#")[0]
        self.is_correct_line = True

        if self._should_ignore_line(line):
            return

        fields = [field for field in csv.reader([line])][0]

        res = self._validate_fields(fields)
        self._flush_output_stream()
        return res

    def _should_ignore_line(self, line: str) -> bool:
        line = line.strip()
        if line.startswith("#"):
            return True
        return len(line) == 0

    ############################################################
    def _validate_fields(self, fields: list[str]) -> bool:
        is_correct = True

        if len(fields) > 0 and not self._is_ip_address_or_prefix_correct(fields[0]):
            is_correct = False

        if len(fields) > 1 and not self._is_alpha2_code_correct(fields[1]):
            is_correct = False

        if len(fields) > 2 and not self._is_region_code_correct(fields[2]):
            is_correct = False

        if len(fields) != 5:
            is_correct = False
            self._report_error(f"5 fields were expected (got {len(fields)})")

        return is_correct

    ############################################################
    def _is_ip_address_or_prefix_correct(self, field: str) -> bool:
        if "/" in field:
            return self._is_cidr_correct(field)
        return self._is_ip_address_correct(field)

    def _is_cidr_correct(self, cidr: str) -> bool:
        try:
            ipprefix = ipaddress.ip_network(cidr)
            if ipprefix.is_private:
                self._report_error("IP Address must not be private")
                return False
        except ValueError as e:
            self._report_error(f"Invalid IP Network: {e}")
            return False
        return True

    def _is_ip_address_correct(self, ip_str: str) -> bool:
        try:
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private:
                self._report_error("IP Address must not be private")
                return False
        except ValueError as e:
            self._report_error(f"Invalid IP Address: {e}")
            return False
        return True

    ############################################################
    def _is_alpha2_code_correct(self, alpha2_code: str) -> bool:
        if len(alpha2_code) == 0:
            return True

        if len(alpha2_code) != 2 or not alpha2_code.isalpha():
            self._report_error("Alpha 2 code must be in the ISO 3166-1 alpha 2 format")
            return False
        return True

    def _is_region_code_correct(self, region_code: str) -> bool:
        if len(region_code) == 0:
            return True

        if "-" not in region_code:
            self._report_error("Region code must be in ISO 3166-2 format")
            return False

        parts = region_code.split("-")
        if len(parts) != 2 or not self._is_alpha2_code_correct(parts[0]):
            return False
        return True

    ############################################################
    def _report_error(self, message: str) -> None:
        self.had_errors = True
        if self.is_correct_line:
            self._write_line(f"line {self.line_number}: {self.line}")
        self.is_correct_line = False

        self._write_line(f"    ERROR: {message}")

    def _flush_output_stream(self) -> None:
        if self.is_correct_line:
            return
        self._write_line("", flush=True)

    def _write_line(self, line: str, flush: bool = False) -> None:
        if self.output_stream is None:
            return

        self.output_stream.write(f"{line}\n")
        if flush:
            self.output_stream.flush()


############################################################

def main() -> None:
    feed_validator = IPGeoFeedValidator()
    feed_validator.validate(sys.stdin)

    if feed_validator.had_errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
