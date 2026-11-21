"""Validate CSV fields and convert valid rows to records."""

import math
import re
from datetime import datetime

RECORD_KEYS = (
    "flight_id", "origin", "destination", "departure_datetime",
    "arrival_datetime", "price",
)
FLIGHT_ID = re.compile(r"[A-Za-z0-9]{2,8}")
AIRPORT_CODE = re.compile(r"[A-Z]{3}")
DATETIME = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")


def load_airports(path: str) -> set[str]:
    with open(path, encoding="utf-8") as file:
        codes = (line.strip() for line in file)
        return {code for code in codes if code and not code.startswith("#")}


def valid_datetime(value: str) -> bool:
    if DATETIME.fullmatch(value) is None:
        return False
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    if len(fields) != len(RECORD_KEYS):
        return "WRONG_FIELD_COUNT"
    flight_id, origin, destination, departure, arrival, price_text = (
        field.strip() for field in fields
    )
    if not all((flight_id, origin, destination, departure, arrival, price_text)):
        return "MISSING_FIELD"
    if not FLIGHT_ID.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not AIRPORT_CODE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not AIRPORT_CODE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"
    if not valid_datetime(departure):
        return "INVALID_DEPARTURE"
    if not valid_datetime(arrival):
        return "INVALID_ARRIVAL"
    if arrival <= departure:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"
    try:
        price = float(price_text)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"
    if price <= 0:
        return "NON_POSITIVE_PRICE"
    return None


def to_record(fields: list[str]) -> dict:
    record = dict(zip(RECORD_KEYS, (field.strip() for field in fields)))
    record["price"] = float(record["price"])
    return record

