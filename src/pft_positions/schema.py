"""Schema loading helpers."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any


def load_schema() -> dict[str, Any]:
    package_schema = resources.files("pft_positions.resources.schema").joinpath(
        "position-snapshot.v0.schema.json"
    )
    if package_schema.is_file():
        return json.loads(package_schema.read_text(encoding="utf-8"))

    repo_schema = Path(__file__).resolve().parents[2] / "schema" / "position-snapshot.v0.schema.json"
    return json.loads(repo_schema.read_text(encoding="utf-8"))
