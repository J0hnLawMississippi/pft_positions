"""Command line interface for the PFT position snapshot reference package."""

from __future__ import annotations

import argparse
import sys

from .canonical import canonical_json
from .fixtures import fixture_names, load_fixture
from .io import dump_json, load_json
from .validate import validate_path, validate_snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pft-positions")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate a snapshot file or fixture directory")
    validate_parser.add_argument("path")

    parse_parser = subparsers.add_parser("parse", help="parse, validate, and print canonical JSON")
    parse_parser.add_argument("path")

    emit_parser = subparsers.add_parser("emit", help="emit a bundled fixture")
    emit_parser.add_argument("name", nargs="?", help="fixture name")
    emit_parser.add_argument("--list", action="store_true", help="list bundled fixture names")

    args = parser.parse_args(argv)

    if args.command == "validate":
        return _validate(args.path)
    if args.command == "parse":
        return _parse(args.path)
    if args.command == "emit":
        return _emit(args.name, args.list)
    return 2


def _validate(path: str) -> int:
    results = validate_path(path)
    failed = False
    for file_path, issues in results.items():
        if issues:
            failed = True
            print(f"FAIL {file_path}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"PASS {file_path}")
    return 1 if failed else 0


def _parse(path: str) -> int:
    snapshot = load_json(path)
    issues = validate_snapshot(snapshot)
    if issues:
        print(f"FAIL {path}", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1
    print(canonical_json(snapshot))
    return 0


def _emit(name: str | None, list_requested: bool) -> int:
    if list_requested:
        for fixture_name in fixture_names():
            print(fixture_name)
        return 0
    if not name:
        print("fixture name required; use --list to see choices", file=sys.stderr)
        return 2
    try:
        fixture = load_fixture(name)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    dump_json(fixture, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
