from datetime import datetime

from app.report_logic import build_monthly_report, resolve_daily_expected, slot_index


def test_resolve_daily_expected_ctype_then_override():
    rules = {
        "default_daily_expected": 24,
        "ctype_daily_expected": {"RR": 24, "ZZ": 48},
        "station_overrides": {"A001": 48},
    }

    assert resolve_daily_expected("A001", "RR", rules) == 48
    assert resolve_daily_expected("B001", "ZZ", rules) == 48
    assert resolve_daily_expected("C001", "XX", rules) == 24


def test_slot_index_24_and_48():
    dt = datetime(2026, 3, 1, 10, 45)
    assert slot_index(dt, 24) == 10
    assert slot_index(dt, 48) == 21


def test_build_monthly_report_deduplicates_same_slot_and_computes_rate():
    stations = [
        {"station_id": "A001", "cname": "测试雨量站", "ctype": "RR"},
    ]
    rules = {
        "default_daily_expected": 24,
        "ctype_daily_expected": {"RR": 24},
        "station_overrides": {},
    }
    records = [
        {"station_id": "A001", "datatime": datetime(2026, 3, 1, 0, 5)},
        {"station_id": "A001", "datatime": datetime(2026, 3, 1, 0, 55)},
        {"station_id": "A001", "datatime": datetime(2026, 3, 1, 1, 0)},
    ]

    report = build_monthly_report(stations, records, 2026, 3, rules)

    assert report["days_in_month"] == 31
    row = report["rows"][0]
    assert row["daily_actual"][0] == 2
    assert row["daily_actual"][1] == 0
    assert row["expected_total"] == 24 * 31
    assert row["actual_total"] == 2
    assert row["rate"] == round((2 / (24 * 31)) * 100, 1)
