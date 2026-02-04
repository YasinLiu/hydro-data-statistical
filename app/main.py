from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Callable

from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config_store import load_rules_from_file, save_rules_to_file
from app.db import SQLServerRepository, month_range
from app.report_logic import build_monthly_report
from app.settings import SETTINGS, build_sqlserver_connection_string

BASE_DIR = Path(__file__).resolve().parent.parent


class RepositoryProtocol:
    def fetch_stations(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def fetch_records(self, start, end, sourcetype_filter: str) -> list[dict[str, Any]]:
        raise NotImplementedError


def _default_repository_factory() -> SQLServerRepository:
    connection_string = build_sqlserver_connection_string(SETTINGS)
    return SQLServerRepository(connection_string)


def _build_report(repo: RepositoryProtocol, config_path: Path, year: int, month: int) -> dict[str, Any]:
    rules = load_rules_from_file(config_path)
    start, end = month_range(year, month)

    stations = repo.fetch_stations()
    records = repo.fetch_records(start, end, rules["sourcetype_filter"])
    return build_monthly_report(stations, records, year, month, rules)


def _build_excel(report: dict[str, Any]) -> bytes:
    try:
        from openpyxl import Workbook
    except ImportError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "openpyxl is required for export. Please run `uv sync` to install dependencies."
        ) from exc

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "月到报统计"

    header = [
        "站名",
        *[str(day) for day in report["day_headers"]],
        "应到报",
        "实到报",
        "到报率(%)",
    ]
    sheet.append(header)

    for row in report["rows"]:
        sheet.append(
            [
                row["station_name"],
                *row["daily_actual"],
                row["expected_total"],
                row["actual_total"],
                row["rate"],
            ]
        )

    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def create_app(
    config_path: Path | None = None,
    repository_factory: Callable[[], RepositoryProtocol] | None = None,
) -> FastAPI:
    app = FastAPI(title="水情月到报统计")

    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    app.state.config_path = config_path or (BASE_DIR / "config" / "report_rules.json")
    app.state.repository_factory = repository_factory or _default_repository_factory

    @app.get("/")
    def home(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/config")
    def get_config() -> dict[str, Any]:
        return load_rules_from_file(app.state.config_path)

    @app.put("/api/config")
    def update_config(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        return save_rules_to_file(app.state.config_path, payload)

    @app.get("/api/report/monthly")
    def monthly_report(
        year: int = Query(..., ge=2000, le=2100),
        month: int = Query(..., ge=1, le=12),
    ) -> dict[str, Any]:
        try:
            repo = app.state.repository_factory()
            return _build_report(repo, app.state.config_path, year, month)
        except Exception as exc:  # pragma: no cover - integration path
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.get("/api/report/monthly/export")
    def export_monthly_report(
        year: int = Query(..., ge=2000, le=2100),
        month: int = Query(..., ge=1, le=12),
    ) -> StreamingResponse:
        try:
            repo = app.state.repository_factory()
            report = _build_report(repo, app.state.config_path, year, month)
        except Exception as exc:  # pragma: no cover - integration path
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        content = _build_excel(report)
        filename = f"monthly-report-{year}-{month:02d}.xlsx"

        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        raise exc

    return app


app = create_app()
