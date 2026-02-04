from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    db_host: str = os.getenv("DB_HOST", "10.6.34.16")
    db_port: str = os.getenv("DB_PORT", "1433")
    db_name: str = os.getenv("DB_NAME", "CSRRDB")
    db_user: str = os.getenv("DB_USER", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "xiangsiersheng")
    db_driver: str = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")


SETTINGS = Settings()


def build_sqlserver_connection_string(settings: Settings = SETTINGS) -> str:
    return (
        f"DRIVER={{{settings.db_driver}}};"
        f"SERVER={settings.db_host},{settings.db_port};"
        f"DATABASE={settings.db_name};"
        f"UID={settings.db_user};"
        f"PWD={settings.db_password};"
        "TrustServerCertificate=yes;"
    )
