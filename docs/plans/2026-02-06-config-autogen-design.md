# Config Auto-Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add first-run config auto-generation and a "regenerate config" button that builds full per-station daily expected counts based on configurable ctype defaults, with clear UI guidance for non-technical users.

**Architecture:** Extend config schema to include `ctype_defaults` and `station_daily_expected`. On missing config, the server reads stations from SQL Server, generates full station mapping, saves it, and returns it. Add a new API endpoint for manual regeneration with overwrite confirmation from the UI. Update reporting logic to read `station_daily_expected` only.

**Tech Stack:** Python (FastAPI), SQL Server (pyodbc), Jinja2, vanilla JS, pytest.

### Task 1: Update configuration schema + tests

**Files:**
- Modify: `app/config_store.py`
- Modify: `tests/test_config_and_db_helpers.py`

**Step 1: Write the failing test**

```python
def test_normalize_rules_includes_station_daily_expected_and_ctype_defaults():
    rules = {
        "ctype_defaults": {"01": 24, "*": 48},
        "station_daily_expected": {"A001": 24},
    }
    normalized = normalize_rules(rules)
    assert normalized["ctype_defaults"]["01"] == 24
    assert normalized["ctype_defaults"]["*"] == 48
    assert normalized["station_daily_expected"]["A001"] == 24
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config_and_db_helpers.py::test_normalize_rules_includes_station_daily_expected_and_ctype_defaults -v`
Expected: FAIL (missing fields).

**Step 3: Write minimal implementation**

- Extend `DEFAULT_RULES` with `ctype_defaults` and `station_daily_expected`.
- Ensure `normalize_rules()` parses and keeps them.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config_and_db_helpers.py::test_normalize_rules_includes_station_daily_expected_and_ctype_defaults -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add app/config_store.py tests/test_config_and_db_helpers.py
git commit -m "feat: extend config schema for station daily expected"
```

### Task 2: Auto-generate config on first run

**Files:**
- Modify: `app/config_store.py`
- Modify: `app/main.py`
- Test: `tests/test_config_autogen.py` (new)

**Step 1: Write failing test**

```python
def test_autogen_on_missing_config(tmp_path):
    # arrange fake stations and repo
    # assert file is created with station_daily_expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config_autogen.py::test_autogen_on_missing_config -v`
Expected: FAIL (function missing).

**Step 3: Minimal implementation**

- Add `generate_rules_from_stations()` helper.
- Update `load_rules_from_file()` to generate if file missing.
- Call helper in `main.py` when config missing (or via load).

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_config_autogen.py::test_autogen_on_missing_config -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add app/config_store.py app/main.py tests/test_config_autogen.py
git commit -m "feat: auto-generate config from station types"
```

### Task 3: Add regenerate API endpoint + UI button with warning

**Files:**
- Modify: `app/main.py`
- Modify: `templates/index.html`
- Modify: `static/app.js`
- Modify: `static/app.css`
- Test: `tests/test_api_regenerate.py` (new)

**Step 1: Write failing test**

```python
def test_regenerate_endpoint_overwrites_config(tmp_path):
    # setup existing config
    # call POST /api/config/regenerate
    # assert new station_daily_expected matches regenerated data
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_api_regenerate.py::test_regenerate_endpoint_overwrites_config -v`
Expected: FAIL (endpoint missing).

**Step 3: Minimal implementation**

- Add `POST /api/config/regenerate`.
- Frontend: add button, confirm dialog, call endpoint, refresh config textarea.
- Add user-facing explanations for non-technical users.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_api_regenerate.py::test_regenerate_endpoint_overwrites_config -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add app/main.py templates/index.html static/app.js static/app.css tests/test_api_regenerate.py
git commit -m "feat: add regenerate config UI and API"
```

### Task 4: Update reporting logic to use station_daily_expected

**Files:**
- Modify: `app/report_logic.py`
- Modify: `tests/test_report_logic.py`

**Step 1: Write failing test**

```python
def test_report_uses_station_daily_expected():
    rules = {"station_daily_expected": {"A001": 48}, "ctype_defaults": {"*": 24}}
    # assert expected_per_day uses station_daily_expected
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_report_logic.py::test_report_uses_station_daily_expected -v`
Expected: FAIL.

**Step 3: Minimal implementation**

- Resolve expected_per_day from `station_daily_expected` first.
- Fallback to `ctype_defaults` or `default_daily_expected`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_report_logic.py::test_report_uses_station_daily_expected -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add app/report_logic.py tests/test_report_logic.py
git commit -m "feat: use station_daily_expected for reporting"
```

### Task 5: Documentation updates

**Files:**
- Modify: `README.md`

**Step 1: Update docs**

- Explain `ctype_defaults` and `station_daily_expected`.
- Document new regenerate endpoint and UI workflow.

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: explain config autogen and regenerate"
```

### Task 6: Verification

**Step 1: Run full tests**

Run: `pytest -q`
Expected: all green.

**Step 2: Report results**

State test output and any failures.
