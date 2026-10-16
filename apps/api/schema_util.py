"""Schema loading and validation helpers shared by the API and tests."""
from __future__ import annotations

import json
from functools import lru_cache

from jsonschema import Draft202012Validator

import config


@lru_cache(maxsize=1)
def deck_validator() -> Draft202012Validator:
    schema = json.loads(config.SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def deck_errors(deck: dict) -> list[str]:
    """Return human-readable validation errors (empty list = valid)."""
    errors = sorted(deck_validator().iter_errors(deck), key=lambda e: list(e.path))
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
