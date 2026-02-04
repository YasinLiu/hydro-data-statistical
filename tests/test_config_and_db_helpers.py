from pathlib import Path

from app.config_store import DEFAULT_RULES, load_rules_from_file, save_rules_to_file
from app.db import month_range


def test_load_rules_from_missing_file_returns_defaults(tmp_path: Path):
    config_file = tmp_path / "missing.json"

    loaded = load_rules_from_file(config_file)

    assert loaded == DEFAULT_RULES


def test_save_then_load_rules_roundtrip(tmp_path: Path):
    config_file = tmp_path / "report_rules.json"
    rules = {
        "default_daily_expected": 24,
        "ctype_daily_expected": {"RR": 24, "ZZ": 48},
        "station_overrides": {"A001": 48},
        "sourcetype_filter": "1",
        "day_start_hour": 9,
    }

    save_rules_to_file(config_file, rules)
    loaded = load_rules_from_file(config_file)

    assert loaded == rules


def test_month_range_for_december_cross_year():
    start, end = month_range(2026, 12, day_start_hour=9)

    assert str(start) == "2026-12-01 09:00:00"
    assert str(end) == "2027-01-01 09:00:00"
