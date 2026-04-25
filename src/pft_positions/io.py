"""JSON file IO helpers for snapshot fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TextIO


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(data: Any, stream: TextIO) -> None:
    json.dump(data, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
