"""Command-line entry point for the flight schedule parser."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB093"
FIRST_NAME = "Sehri"
LAST_NAME = "Sultanli"


def read_json(path: Path) -> object:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")


def write_errors(path: Path, errors: list[str]) -> None:
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler)
    try:
        for error in errors:
            logger.warning("%s", error)
    finally:
        logger.removeHandler(handler)
        handler.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse and query flight schedules.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", type=Path, metavar="FILE")
    source.add_argument("-d", type=Path, metavar="FOLDER")
    source.add_argument("-j", type=Path, metavar="FILE")
    parser.add_argument("-a", type=Path, metavar="FILE")
    parser.add_argument("-o", type=Path, metavar="FILE")
    parser.add_argument("-q", type=Path, metavar="FILE")
    parser.add_argument("-r", type=Path, default=Path("."), metavar="FOLDER")
    try:
        args = parser.parse_args(argv)
        if args.j is None and args.a is None:
            parser.error("-a is required with -i or -d")
        if args.j is not None and args.o is not None:
            parser.error("-o is only allowed with -i or -d")
    except SystemExit as exit_status:
        return exit_status.code

    try:
        if args.j is not None:
            db = read_json(args.j)
            if not isinstance(db, list) or not all(isinstance(row, dict) for row in db):
                raise ValueError("the database must be a JSON array of objects")
        else:
            if args.d is None:
                paths = [str(args.i)]
            else:
                paths = [
                    str(path) for path in sorted(args.d.iterdir(), key=lambda path: path.name)
                    if path.is_file() and path.name.endswith(".csv")
                ]
                if not paths:
                    raise ValueError(f"no .csv files found in {args.d}")
            db, errors = parse_files(paths, load_airports(args.a))
            output = args.o if args.o is not None else Path("db.json")
            write_json(output, db)
            write_errors(output.with_name("errors.log"), errors)

        if args.q is not None:
            queries = read_json(args.q)
            if not isinstance(queries, dict) and (
                not isinstance(queries, list)
                or not all(isinstance(query, dict) for query in queries)
            ):
                raise ValueError("queries must be a JSON object or array of objects")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            write_json(args.r / filename, run_queries(db, queries))
    except (OSError, ValueError) as error:
        message = " ".join(str(error).splitlines())
        print(f"Error: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

