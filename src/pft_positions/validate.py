"""Snapshot validation for the v0 reference schema."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .canonical import content_hash
from .io import load_json
from .schema import load_schema


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def validate_snapshot(snapshot: dict[str, Any]) -> list[ValidationIssue]:
    schema = load_schema()
    issues = list(_validate_schema(snapshot, schema, schema, ""))
    provenance = snapshot.get("provenance")
    expected = provenance.get("content_hash") if isinstance(provenance, dict) else None
    if isinstance(expected, str):
        computed = content_hash(snapshot)
        if expected != computed:
            issues.append(
                ValidationIssue(
                    "/provenance/content_hash",
                    f"hash mismatch: expected {expected}, computed {computed}",
                )
            )
    return issues


def validate_file(path: str | Path) -> list[ValidationIssue]:
    try:
        snapshot = load_json(path)
    except json.JSONDecodeError as exc:
        return [ValidationIssue("/", f"invalid JSON: {exc.msg}")]
    if not isinstance(snapshot, dict):
        return [ValidationIssue("/", "snapshot must be a JSON object")]
    return validate_snapshot(snapshot)


def validate_path(path: str | Path) -> dict[Path, list[ValidationIssue]]:
    target = Path(path)
    if target.is_dir():
        files = sorted(target.glob("*.json"))
    else:
        files = [target]
    return {file_path: validate_file(file_path) for file_path in files}


def _validate_schema(value: Any, schema: dict[str, Any], root: dict[str, Any], path: str) -> Iterable[ValidationIssue]:
    if "$ref" in schema:
        schema = _resolve_ref(root, schema["$ref"])

    if "const" in schema and value != schema["const"]:
        yield ValidationIssue(path or "/", f"expected const {schema['const']!r}")
        return

    if "enum" in schema and value not in schema["enum"]:
        choices = ", ".join(repr(choice) for choice in schema["enum"])
        yield ValidationIssue(path or "/", f"expected one of {choices}")
        return

    schema_type = schema.get("type")
    if schema_type and not _matches_type(value, schema_type):
        yield ValidationIssue(path or "/", f"expected {schema_type}")
        return

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                yield ValidationIssue(_join(path, required), "required property missing")
        if schema.get("additionalProperties") is False:
            for key in sorted(set(value) - set(properties)):
                yield ValidationIssue(_join(path, key), "additional property not allowed")
        for key, subschema in properties.items():
            if key in value:
                yield from _validate_schema(value[key], subschema, root, _join(path, key))

    if isinstance(value, list):
        min_items = schema.get("minItems")
        if min_items is not None and len(value) < min_items:
            yield ValidationIssue(path or "/", f"expected at least {min_items} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                yield from _validate_schema(item, item_schema, root, f"{path}/{index}" if path else f"/{index}")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if min_length is not None and len(value) < min_length:
            yield ValidationIssue(path or "/", f"expected minLength {min_length}")
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, value):
            yield ValidationIssue(path or "/", f"does not match pattern {pattern!r}")
        if schema.get("format") == "date-time" and not _is_date_time(value):
            yield ValidationIssue(path or "/", "expected RFC3339 date-time")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if minimum is not None and value < minimum:
            yield ValidationIssue(path or "/", f"expected minimum {minimum}")
        if maximum is not None and value > maximum:
            yield ValidationIssue(path or "/", f"expected maximum {maximum}")

    for subschema in schema.get("allOf", []):
        if "if" in subschema and "then" in subschema:
            if _condition_matches(value, subschema["if"]):
                yield from _validate_schema(value, subschema["then"], root, path)
        else:
            yield from _validate_schema(value, subschema, root, path)


def _matches_type(value: Any, schema_type: str) -> bool:
    if schema_type == "object":
        return isinstance(value, dict)
    if schema_type == "array":
        return isinstance(value, list)
    if schema_type == "string":
        return isinstance(value, str)
    if schema_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if schema_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if schema_type == "boolean":
        return isinstance(value, bool)
    return True


def _resolve_ref(root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported ref {ref!r}")
    current: Any = root
    for part in ref[2:].split("/"):
        current = current[part]
    return current


def _condition_matches(value: Any, condition: dict[str, Any]) -> bool:
    if not isinstance(value, dict):
        return False
    for key, subschema in condition.get("properties", {}).items():
        if key in value and "const" in subschema and value[key] != subschema["const"]:
            return False
    return True


def _is_date_time(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _join(path: str, key: str) -> str:
    escaped = key.replace("~", "~0").replace("/", "~1")
    return f"{path}/{escaped}" if path else f"/{escaped}"
