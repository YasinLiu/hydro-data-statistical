from pathlib import Path

from app.config_store import load_or_generate_rules
from app.main import load_or_generate_rules_with_repo


def test_autogen_on_missing_config(tmp_path: Path):
    config_file = tmp_path / "report_rules.json"
    stations = [
        {"station_id": "A001", "ctype": "01"},
        {"station_id": "B001", "ctype": "99"},
    ]

    rules = load_or_generate_rules(config_file, stations)

    assert config_file.exists()
    assert rules["station_daily_expected"]["A001"] == 24
    assert rules["station_daily_expected"]["B001"] == 48


def test_load_or_generate_rules_with_repo(tmp_path: Path):
    config_file = tmp_path / "report_rules.json"

    class FakeRepo:
        def fetch_stations(self):
            return [
                {"station_id": "A001", "ctype": "01"},
                {"station_id": "B001", "ctype": "99"},
            ]

    rules = load_or_generate_rules_with_repo(FakeRepo(), config_file)

    assert config_file.exists()
    assert rules["station_daily_expected"]["A001"] == 24
    assert rules["station_daily_expected"]["B001"] == 48
