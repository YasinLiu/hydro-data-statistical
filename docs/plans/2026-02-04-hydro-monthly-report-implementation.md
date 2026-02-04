# Hydro Monthly Report Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a FastAPI web app that computes monthly report receipt counts per station (daily actual counts, monthly expected/actual, receipt rate), supports SQL Server data source, JSON-based rules (Ctype default + station override), and Excel export.

**Architecture:** Use a thin FastAPI HTTP layer with a pure-Python reporting core for deterministic calculations and tests. Data access reads station metadata and month data from SQL Server, applies `Sourcetype=1`, deduplicates by station/day/slot, then renders JSON for a browser table and XLSX for export.

**Tech Stack:** Python 3.11+, FastAPI, Jinja2, openpyxl, pyodbc, uv, pytest.

### Task 1: Project scaffold and config model

**Files:**
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `app/settings.py`
- Create: `app/config_store.py`
- Create: `config/report_rules.json`

**Step 1: Write failing test**
- Create config-load test that expects valid defaults from local JSON.

**Step 2: Run test to verify fail**
- Run: `pytest tests/test_config_store.py -v`
- Expected: FAIL because module/file missing.

**Step 3: Minimal implementation**
- Implement settings + config load/save logic with Pydantic validation.

**Step 4: Re-run test**
- Expected: PASS.

### Task 2: Reporting core (TDD)

**Files:**
- Create: `tests/test_report_logic.py`
- Create: `app/report_logic.py`

**Step 1: Write failing tests**
- Resolve daily expected by Ctype and station override.
- Deduplicate same slot data.
- Build monthly totals and rates with daily columns.

**Step 2: Run tests to verify fail**
- Run: `pytest tests/test_report_logic.py -v`
- Expected: FAIL because functions missing.

**Step 3: Minimal implementation**
- Implement pure functions: slot index, expectation resolve, report assembly.

**Step 4: Re-run tests**
- Expected: PASS.

### Task 3: SQL Server repository layer

**Files:**
- Create: `app/db.py`

**Step 1: Write failing test (unit-level helper)**
- Validate date-range helper for month boundaries.

**Step 2: Run test to verify fail**
- Run targeted helper test, expect missing code failure.

**Step 3: Minimal implementation**
- Build pyodbc connection helper and fetch functions:
  - stations (`StationID`, `Cname`, `Ctype`)
  - raw data (`stationid`, `datatime`) filtered by month and `Sourcetype=1`.

**Step 4: Re-run tests**
- Expected: helper tests pass.

### Task 4: FastAPI routes + UI + export

**Files:**
- Create: `app/main.py`
- Create: `app/schemas.py`
- Create: `templates/index.html`
- Create: `static/app.js`
- Create: `static/app.css`

**Step 1: Write failing API tests**
- Basic endpoint tests for `/api/report/monthly` validation and shape.

**Step 2: Run tests to verify fail**
- Expected: FAIL due missing endpoints.

**Step 3: Minimal implementation**
- Implement routes:
  - `GET /` page
  - `GET /api/report/monthly`
  - `GET /api/report/monthly/export`
  - `GET /api/config`
  - `PUT /api/config`
- Implement client rendering and config editor.

**Step 4: Re-run tests**
- Expected: PASS for API validation tests.

### Task 5: Verification and usage docs

**Files:**
- Create: `README.md`

**Step 1: Run verification commands**
- `pytest -q`
- optional smoke: `uv run uvicorn app.main:app --reload`

**Step 2: Document run steps**
- uv sync, env vars, JSON config usage, known assumptions.

**Step 3: Confirm output**
- Ensure no failing tests before claiming completion.
