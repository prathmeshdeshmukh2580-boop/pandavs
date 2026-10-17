import json
from pathlib import Path
import pytest

try:
    from apps.api import config
    from apps.api.schema_util import deck_errors, deck_validator
except ImportError:
    import config
    from schema_util import deck_errors, deck_validator

# Only pick up files that are actual decks; exclude reports, etc.
SAMPLES = sorted(p for p in config.SAMPLES_DIR.glob("*.json") if "deck" in p.name)


def test_schema_is_valid_json_schema():
    deck_validator()  # raises if the schema itself is malformed


@pytest.mark.parametrize("path", SAMPLES, ids=[p.name for p in SAMPLES])
def test_sample_decks_validate(path):
    deck = json.loads(path.read_text(encoding="utf-8"))
    assert deck_errors(deck) == []


def test_samples_exist():
    assert SAMPLES, "expected at least one sample deck in samples/"


def test_schema_rejects_bad_deck():
    sample_path = config.SAMPLES_DIR / "sample_deck.json"
    if not sample_path.exists():
        sample_path = config.SAMPLES_DIR / "spring_boot_deck.json"
    deck = json.loads(sample_path.read_text(encoding="utf-8"))
    deck["slides"][0]["bullets"] = ["x"] * 10  # over the bullet cap
    deck["slides"][2]["code"][0]["verified"] = "maybe"  # not an allowed status
    errors = deck_errors(deck)
    assert any("bullets" in e or "verified" in e for e in errors)
