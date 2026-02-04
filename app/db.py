from __future__ import annotations

from datetime import datetime
from typing import Any


def month_range(year: int, month: int, day_start_hour: int = 9) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, day_start_hour, 0, 0)
    if month == 12:
        end = datetime(year + 1, 1, 1, day_start_hour, 0, 0)
    else:
        end = datetime(year, month + 1, 1, day_start_hour, 0, 0)
    return start, end


def _import_pyodbc():
    try:
        import pyodbc
    except ImportError as exc:  # pragma: no cover - requires runtime dependency
        raise RuntimeError(
            "pyodbc is required. Please run `uv sync` to install dependencies."
        ) from exc
    return pyodbc


class SQLServerRepository:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def _connect(self):
        pyodbc = _import_pyodbc()
        return pyodbc.connect(self.connection_string)

    def fetch_stations(self) -> list[dict[str, Any]]:
        query = """
            SELECT
                RTRIM(StationID) AS station_id,
                RTRIM(Cname) AS cname,
                RTRIM(Ctype) AS ctype
            FROM dbo.Stations
            ORDER BY StationID
        """

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        stations: list[dict[str, Any]] = []
        for row in rows:
            stations.append(
                {
                    "station_id": (row.station_id or "").strip(),
                    "cname": (row.cname or "").strip(),
                    "ctype": (row.ctype or "").strip(),
                }
            )
        return stations

    def fetch_records(
        self,
        start: datetime,
        end: datetime,
        sourcetype_filter: str,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
                RTRIM(stationid) AS station_id,
                datatime
            FROM dbo.OneDayData
            WHERE datatime >= ?
              AND datatime < ?
              AND datatime IS NOT NULL
              AND LTRIM(RTRIM(Sourcetype)) = ?
        """

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, start, end, sourcetype_filter)
            rows = cursor.fetchall()

        records: list[dict[str, Any]] = []
        for row in rows:
            records.append(
                {
                    "station_id": (row.station_id or "").strip(),
                    "datatime": row.datatime,
                }
            )
        return records
