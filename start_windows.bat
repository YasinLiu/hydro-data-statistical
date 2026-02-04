@echo off
setlocal EnableExtensions EnableDelayedExpansion

chcp 65001 >nul
cd /d "%~dp0"

echo [INFO] Working directory: %CD%

set "ENV_FILE=.env.windows"
if exist "%ENV_FILE%" (
  call :load_env "%ENV_FILE%"
  echo [INFO] Loaded environment from %ENV_FILE%
)

if not defined APP_HOST set "APP_HOST=0.0.0.0"
if not defined APP_PORT set "APP_PORT=8000"
if not defined RUN_MODE set "RUN_MODE=prod"
if not defined APP_WORKERS set "APP_WORKERS=2"
if not defined LOG_LEVEL set "LOG_LEVEL=info"
if not defined UV_SYNC_ARGS set "UV_SYNC_ARGS=--extra dev"
if not defined SKIP_SYNC set "SKIP_SYNC=0"
if not defined FORCE_SYNC set "FORCE_SYNC=0"

where uv >nul 2>&1
if errorlevel 1 (
  echo [ERROR] uv not found. Install uv first: https://docs.astral.sh/uv/
  exit /b 1
)

if "%SKIP_SYNC%"=="1" goto :skip_sync

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] .venv not found, running dependency installation...
  call uv sync %UV_SYNC_ARGS%
  if errorlevel 1 (
    echo [ERROR] uv sync failed.
    exit /b 1
  )
) else (
  if "%FORCE_SYNC%"=="1" (
    echo [INFO] .venv exists, running dependency sync...
    call uv sync %UV_SYNC_ARGS%
    if errorlevel 1 (
      echo [ERROR] uv sync failed.
      exit /b 1
    )
  )
)

:skip_sync
if not exist "logs" mkdir "logs" >nul 2>&1

if /I "%RUN_MODE%"=="dev" (
  set "UVICORN_MODE_ARGS=--reload --log-level debug"
) else (
  set "UVICORN_MODE_ARGS=--workers %APP_WORKERS% --log-level %LOG_LEVEL%"
)

echo [INFO] Starting service mode=%RUN_MODE% host=%APP_HOST% port=%APP_PORT%
echo [INFO] Open browser: http://127.0.0.1:%APP_PORT%
echo [INFO] Log files: logs\access.log, logs\error.log

call uv run uvicorn app.main:app --host %APP_HOST% --port %APP_PORT% %UVICORN_MODE_ARGS% --proxy-headers 1>>"logs\access.log" 2>>"logs\error.log"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo [ERROR] Service exited with code %EXIT_CODE%.
  echo [ERROR] Check logs\error.log for details.
)

exit /b %EXIT_CODE%

:load_env
for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%~1") do (
  if not "%%~A"=="" (
    set "%%~A=%%~B"
  )
)
exit /b 0
