import json

import pytest

import config
from schema_util import deck_errors, deck_validator

SAMPLES = sorted(config.SAMPLES_DIR.glob("*.json"))


def test_schema_is_valid_json_schema():
    deck_validator()  # raises if the schema itself is malformed


@pytest.mark.parametrize("path", SAMPLES, ids=[p.name for p in SAMPLES])
def test_sample_decks_validate(path):
    deck = json.loads(path.read_text(encoding="utf-8"))
    assert deck_errors(deck) == []


def test_samples_exist():
    assert SAMPLES, "expected at least one sample deck in samples/"


def test_schema_rejects_bad_deck():
    deck = json.loads((config.SAMPLES_DIR / "sample_deck.json").read_text(encoding="utf-8"))
    deck["slides"][0]["bullets"] = ["x"] * 6  # over the 5-bullet cap
    deck["slides"][2]["code"][0]["verified"] = "maybe"  # not an allowed status
    errors = deck_errors(deck)
    assert any("bullets" in e for e in errors)
    assert any("verified" in e for e in errors)
