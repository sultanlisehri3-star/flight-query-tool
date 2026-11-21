"""Read physical CSV lines and detect duplicates across files."""

import csv
from pathlib import Path

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    seen = set()
    for path in paths:
        filename = Path(path).name
        with open(path, encoding="utf-8", newline="") as file:
            next(file, None)
            for line_number, line in enumerate(file, start=2):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                try:
                    fields = next(csv.reader([line], skipinitialspace=True))
                except csv.Error:
                    error = "WRONG_FIELD_COUNT"
                else:
                    error = validate_row(fields, airports)
                    if error is None:
                        record = to_record(fields)
                        key = (record["flight_id"], record["departure_datetime"])
                        if key not in seen:
                            seen.add(key)
                            records.append(record)
                            continue
                        error = "DUPLICATE_FLIGHT"
                errors.append(f"{filename}:{line_number}: {error} | {stripped}")
    return records, errors

