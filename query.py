"""Validate and execute flight queries."""

import math
from operator import eq, ge, le

from validator import RECORD_KEYS, valid_datetime

TEXT_KEYS = {"flight_id", "origin", "destination"}
DATE_KEYS = {"departure_datetime", "arrival_datetime"}
PRICE_KEYS = {"price", "min_price"}
COMPARISONS = {
    "flight_id": eq, "origin": eq, "destination": eq,
    "departure_datetime": ge, "arrival_datetime": le,
    "price": le, "min_price": ge,
}


def valid_query(query: dict) -> bool:
    if "order" in query and "sort_by" not in query:
        return False
    for key, value in query.items():
        if key in TEXT_KEYS:
            valid = isinstance(value, str)
        elif key in DATE_KEYS:
            valid = isinstance(value, str) and valid_datetime(value)
        elif key in PRICE_KEYS:
            valid = type(value) is int or (
                type(value) is float and math.isfinite(value)
            )
        elif key == "sort_by":
            valid = value in RECORD_KEYS
        elif key == "order":
            valid = value in ("asc", "desc")
        elif key == "limit":
            valid = type(value) is int and value >= 0
        else:
            return False
        if not valid:
            return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    if not valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    filters = [
        ("price" if key == "min_price" else key, COMPARISONS[key], value)
        for key, value in query.items()
        if key in COMPARISONS
    ]
    matches = [
        record for record in db
        if all(compare(record[key], value) for key, compare, value in filters)
    ]
    if "sort_by" in query:
        sort_key = query["sort_by"]
        matches.sort(
            key=lambda record: record[sort_key],
            reverse=query.get("order") == "desc",
        )
    return {"query": query, "matches": matches[:query.get("limit")]}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    if isinstance(queries, dict):
        queries = [queries]
    return [run_query(db, query) for query in queries]

