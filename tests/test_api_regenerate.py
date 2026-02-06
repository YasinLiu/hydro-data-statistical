from pathlib import Path

from app.config_store import save_rules_to_file
from app.main import regenerate_rules_with_repo


def test_regenerate_overwrites_station_daily_expected(tmp_path: Path):
    config_file = tmp_path / "report_rules.json"
    save_rules_to_file(
        config_file,
        {
            "ctype_defaults": {"01": 24, "*": 48},
            "station_daily_expected": {"A001": 48},
            "sourcetype_filter": "1",
        },
    )

    class FakeRepo:
        def fetch_stations(self):
            return [
                {"station_id": "A001", "ctype": "01"},
                {"station_id": "B001", "ctype": "99"},
            ]

    rules = regenerate_rules_with_repo(FakeRepo(), config_file)

    assert rules["station_daily_expected"]["A001"] == 24
    assert rules["station_daily_expected"]["B001"] == 48
