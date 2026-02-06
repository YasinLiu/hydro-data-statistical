from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

DEFAULT_RULES: dict[str, Any] = {
    "default_daily_expected": 24,
    "ctype_daily_expected": {
        "RR": 24,
        "ZZ": 48,
    },
    "ctype_defaults": {"01": 24, "*": 48},
    "station_daily_expected": {},
    "station_overrides": {},
    "sourcetype_filter": "1",
    "day_start_hour": 9,
}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_rules(rules: dict[str, Any] | None) -> dict[str, Any]:
    base = deepcopy(DEFAULT_RULES)
    if not isinstance(rules, dict):
        return base

    try:
        default_daily_expected = int(rules.get("default_daily_expected", base["default_daily_expected"]))
    except (TypeError, ValueError):
        default_daily_expected = base["default_daily_expected"]
    if default_daily_expected <= 0:
        default_daily_expected = base["default_daily_expected"]
    base["default_daily_expected"] = default_daily_expected

    ctype_daily_expected: dict[str, int] = {}
    for key, value in (rules.get("ctype_daily_expected") or {}).items():
        cleaned_key = _clean_text(key)
        if not cleaned_key:
            continue
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            continue
        if int_value > 0:
            ctype_daily_expected[cleaned_key] = int_value
    if ctype_daily_expected:
        base["ctype_daily_expected"] = ctype_daily_expected

    ctype_defaults: dict[str, int] = {}
    for key, value in (rules.get("ctype_defaults") or {}).items():
        cleaned_key = _clean_text(key)
        if not cleaned_key:
            continue
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            continue
        if int_value > 0:
            ctype_defaults[cleaned_key] = int_value
    if ctype_defaults:
        base["ctype_defaults"] = ctype_defaults

    station_daily_expected: dict[str, int] = {}
    for key, value in (rules.get("station_daily_expected") or {}).items():
        cleaned_key = _clean_text(key)
        if not cleaned_key:
            continue
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            continue
        if int_value > 0:
            station_daily_expected[cleaned_key] = int_value
    base["station_daily_expected"] = station_daily_expected

    station_overrides: dict[str, int] = {}
    for key, value in (rules.get("station_overrides") or {}).items():
        cleaned_key = _clean_text(key)
        if not cleaned_key:
            continue
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            continue
        if int_value > 0:
            station_overrides[cleaned_key] = int_value
    base["station_overrides"] = station_overrides

    sourcetype_filter = _clean_text(rules.get("sourcetype_filter", base["sourcetype_filter"]))
    base["sourcetype_filter"] = sourcetype_filter or base["sourcetype_filter"]

    try:
        day_start_hour = int(rules.get("day_start_hour", base["day_start_hour"]))
    except (TypeError, ValueError):
        day_start_hour = base["day_start_hour"]
    if day_start_hour < 0 or day_start_hour > 23:
        day_start_hour = base["day_start_hour"]
    base["day_start_hour"] = day_start_hour

    return base


def _resolve_expected_from_defaults(
    ctype: str, ctype_defaults: dict[str, int], default_daily_expected: int
) -> int:
    if ctype in ctype_defaults:
        return ctype_defaults[ctype]
    if "*" in ctype_defaults:
        return ctype_defaults["*"]
    return default_daily_expected


def generate_rules_from_stations(
    stations: list[dict[str, Any]], base_rules: dict[str, Any] | None = None
) -> dict[str, Any]:
    normalized = normalize_rules(base_rules)
    ctype_defaults = normalized.get("ctype_defaults", {})
    default_daily_expected = normalized.get("default_daily_expected", 24)

    station_daily_expected: dict[str, int] = {}
    for station in stations:
        station_id = _clean_text(station.get("station_id"))
        if not station_id:
            continue
        ctype = _clean_text(station.get("ctype"))
        station_daily_expected[station_id] = _resolve_expected_from_defaults(
            ctype, ctype_defaults, default_daily_expected
        )

    normalized["station_daily_expected"] = station_daily_expected
    return normalized


def load_rules_from_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return deepcopy(DEFAULT_RULES)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return deepcopy(DEFAULT_RULES)

    return normalize_rules(raw if isinstance(raw, dict) else None)


def load_or_generate_rules(path: Path, stations: list[dict[str, Any]]) -> dict[str, Any]:
    if path.exists():
        return load_rules_from_file(path)

    generated = generate_rules_from_stations(stations, DEFAULT_RULES)
    save_rules_to_file(path, generated)
    return generated


def save_rules_to_file(path: Path, rules: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_rules(rules)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return normalized
