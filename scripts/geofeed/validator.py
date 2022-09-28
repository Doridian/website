from ipaddress import ip_network
from typing import TextIO
from data import ValidationError

class GeoFeedValidator:
    errors: list[ValidationError]
    _line_number: int
    _line: str

    def __init__(self) -> None:
        self.errors = []
        self._line_number = 0
        self._line = ""

    def _report_error(self, err: str) -> None:
        self.errors.append(ValidationError(line=self._line, line_number=self._line_number, error=err))

    def _check_country_code(self, cc: str, name: str) -> None:
        if len(cc) != 2:
            self._report_error(f"{name} must have length of 2 (got {len(cc)})")

        if not cc.isalpha():
            self._report_error(f"{name} must only be alphabetic characters")

        if cc.upper() != cc:
            self._report_error(f"{name} must be all uppercase")

    def _check_line(self, line_number: int, line: str) -> None:
        line = line.rstrip("\r\n")
        if not line or line[0] == "#":
            return

        self._line_number = line_number
        self._line = line

        fields = line.split(",")

        if len(fields) != 5:
            self._report_error(f"Expected 5 fields (got {len(fields)})")

        if len(fields) >= 1:
            try:
                net = ip_network(fields[0])
                if not net.is_global:
                    self._report_error("Subnet is not global")
            except ValueError as e:
                self._report_error(f"Subnet invalid: {e}")

        country = ""
        region = []
        if len(fields) >= 2:
            country = fields[1]
            if country:
                self._check_country_code(country, "Country code")

        if len(fields) >= 3:
            region_str = fields[2]
            if region_str:
                region = region_str.split("-")
                if len(region) == 2:
                    self._check_country_code(region[0], "Region country code")

                    region_code = region[1]
                    if not region_code:
                        self._report_error("Region code missing")
                    else:
                        if not region_code.isalpha():
                            self._report_error(f"Region code must only be alphabetic characters")

                        if region_code.upper() != region_code:
                            self._report_error(f"Region code must be all uppercase")
                else:
                    self._report_error("Region must be of format [country code]-[region code] (ex: US-WA)")

        if len(region) == 2 and country and country != region[0]:
            self._report_error(f"Mismatch between country code ({country}) and region country code ({region[0]})")

    def write_errors(self, out: TextIO):
        for err in self.errors:
            out.write(f"Line {err.line_number} ({err.line}): {err.error}\n")
        out.flush()

    def run(self, output: str) -> bool:
        self.errors = []

        lines = output.splitlines()
        for i, line in enumerate(lines):
            self._check_line(i, line)

        return len(self.errors) == 0
