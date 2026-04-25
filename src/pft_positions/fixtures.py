"""Bundled fixture corpus helpers."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


def fixture_names() -> list[str]:
    fixture_dir = resources.files("pft_positions.resources.fixtures")
    return sorted(path.name.removesuffix(".json") for path in fixture_dir.iterdir() if path.name.endswith(".json"))


def load_fixture(name: str) -> dict[str, Any]:
    if name.endswith(".json"):
        name = name[:-5]
    if name not in fixture_names():
        choices = ", ".join(fixture_names())
        raise KeyError(f"unknown fixture {name!r}; expected one of: {choices}")
    fixture_path = resources.files("pft_positions.resources.fixtures").joinpath(f"{name}.json")
    return json.loads(fixture_path.read_text(encoding="utf-8"))
