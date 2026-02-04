from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Any


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_int_mapping(raw: Any) -> dict[str, int]:
    mapping: dict[str, int] = {}
    if not isinstance(raw, dict):
        return mapping
    for key, value in raw.items():
        normalized_key = _clean_text(key)
        if not normalized_key:
            continue
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            continue
        if int_value > 0:
            mapping[normalized_key] = int_value
    return mapping


def resolve_daily_expected(station_id: str, ctype: str, rules: dict[str, Any]) -> int:
    station_overrides = _normalize_int_mapping(rules.get("station_overrides"))
    ctype_daily_expected = _normalize_int_mapping(rules.get("ctype_daily_expected"))

    station_key = _clean_text(station_id)
    ctype_key = _clean_text(ctype)

    if station_key in station_overrides:
        return station_overrides[station_key]
    if ctype_key in ctype_daily_expected:
        return ctype_daily_expected[ctype_key]

    default_daily_expected = rules.get("default_daily_expected", 24)
    try:
        parsed_default = int(default_daily_expected)
    except (TypeError, ValueError):
        parsed_default = 24

    return parsed_default if parsed_default > 0 else 24


def resolve_day_start_hour(rules: dict[str, Any]) -> int:
    raw = rules.get("day_start_hour", 9)
    try:
        parsed = int(raw)
    except (TypeError, ValueError):
        return 9
    if 0 <= parsed <= 23:
        return parsed
    return 9


def slot_index(data_time: datetime, reports_per_day: int, day_start_hour: int = 0) -> int:
    if reports_per_day <= 0:
        raise ValueError("reports_per_day must be a positive integer")

    minute_of_day = (((data_time.hour - day_start_hour) % 24) * 60) + data_time.minute
    slot_minutes = 1440 / reports_per_day
    index = int(minute_of_day // slot_minutes)
    return min(index, reports_per_day - 1)


def build_monthly_report(
    stations: list[dict[str, Any]],
    records: list[dict[str, Any]],
    year: int,
    month: int,
    rules: dict[str, Any],
) -> dict[str, Any]:
    days_in_month = calendar.monthrange(year, month)[1]
    day_start_hour = resolve_day_start_hour(rules)

    normalized_stations: list[dict[str, str]] = []
    station_expected_per_day: dict[str, int] = {}

    for station in stations:
        station_id = _clean_text(station.get("station_id"))
        if not station_id:
            continue

        station_name = _clean_text(station.get("cname")) or station_id
        ctype = _clean_text(station.get("ctype"))
        expected_per_day = resolve_daily_expected(station_id, ctype, rules)

        normalized_stations.append(
            {
                "station_id": station_id,
                "cname": station_name,
                "ctype": ctype,
            }
        )
        station_expected_per_day[station_id] = expected_per_day

    arrived_slots: dict[tuple[str, int], set[int]] = {}
    valid_station_ids = set(station_expected_per_day)

    for record in records:
        station_id = _clean_text(record.get("station_id"))
        if station_id not in valid_station_ids:
            continue

        data_time = record.get("datatime")
        if not isinstance(data_time, datetime):
            continue

        shifted_time = data_time - timedelta(hours=day_start_hour)
        if shifted_time.year != year or shifted_time.month != month:
            continue

        day = shifted_time.day
        expected_per_day = station_expected_per_day[station_id]
        slot = slot_index(data_time, expected_per_day, day_start_hour=day_start_hour)

        key = (station_id, day)
        if key not in arrived_slots:
            arrived_slots[key] = set()
        arrived_slots[key].add(slot)

    rows: list[dict[str, Any]] = []
    for station in normalized_stations:
        station_id = station["station_id"]
        expected_per_day = station_expected_per_day[station_id]

        daily_actual: list[int] = []
        for day in range(1, days_in_month + 1):
            daily_actual.append(len(arrived_slots.get((station_id, day), set())))

        expected_total = expected_per_day * days_in_month
        actual_total = sum(daily_actual)
        rate = round((actual_total / expected_total) * 100, 1) if expected_total else 0.0

        rows.append(
            {
                "station_id": station_id,
                "station_name": station["cname"],
                "ctype": station["ctype"],
                "expected_per_day": expected_per_day,
                "daily_actual": daily_actual,
                "expected_total": expected_total,
                "actual_total": actual_total,
                "rate": rate,
            }
        )

    return {
        "year": year,
        "month": month,
        "day_start_hour": day_start_hour,
        "days_in_month": days_in_month,
        "day_headers": list(range(1, days_in_month + 1)),
        "rows": rows,
    }
