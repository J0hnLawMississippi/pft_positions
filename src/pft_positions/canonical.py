"""Canonical JSON and content hash helpers."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


def snapshot_for_hash(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return a hashable copy with the circular content_hash field omitted."""
    prepared = copy.deepcopy(snapshot)
    provenance = prepared.get("provenance")
    if isinstance(provenance, dict):
        provenance.pop("content_hash", None)
    return prepared


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return canonical_json(value).encode("utf-8")


def content_hash(snapshot: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(snapshot_for_hash(snapshot))).hexdigest()
