@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   ClauseLens Database One-Click Setup (Windows)
echo ============================================================
echo.

REM Locate psql.exe in PATH or standard PostgreSQL installation directories
set "PSQL_EXE="
where psql >nul 2>nul
if %errorlevel%==0 (
    for /f "delims=" %%I in ('where psql') do (
        set "PSQL_EXE=%%I"
        goto :found_psql
    )
)

for %%V in (17 16 15 14 13) do (
    if exist "C:\Program Files\PostgreSQL\%%V\bin\psql.exe" (
        set "PSQL_EXE=C:\Program Files\PostgreSQL\%%V\bin\psql.exe"
        goto :found_psql
    )
)

echo [ERROR] PostgreSQL (psql.exe) was not found on this PC.
echo Please install PostgreSQL 15+ from: https://www.postgresql.org/download/windows/
echo After installing, run this script again.
pause
exit /b 1

:found_psql
echo [OK] Found PostgreSQL client: "%PSQL_EXE%"
echo.

set /p PG_USER="Enter PostgreSQL superuser name [default: postgres]: "
if "%PG_USER%"=="" set "PG_USER=postgres"

set /p PG_HOST="Enter PostgreSQL host [default: localhost]: "
if "%PG_HOST%"=="" set "PG_HOST=localhost"

set /p PG_PORT="Enter PostgreSQL port [default: 5432]: "
if "%PG_PORT%"=="" set "PG_PORT=5432"

echo.
echo Running ClauseLens full setup (Schema + Demo Data + Verification + Tests)...
echo You will be prompted once by psql for your PostgreSQL password if required.
echo.

set "SCRIPT_DIR=%~dp0"
"%PSQL_EXE%" -h "%PG_HOST%" -p "%PG_PORT%" -U "%PG_USER%" -d postgres -v ON_ERROR_STOP=1 -f "%SCRIPT_DIR%setup_all.sql"

if %errorlevel% neq 0 (
    echo.
    echo [FAILED] Setup encountered an error. Check the output above.
    pause
    exit /b %errorlevel%
)

echo.
echo ============================================================
echo   SUCCESS! Database 'clauselens_db' is ready to use.
echo   You can now inspect it in pgAdmin 4 or connect Django.
echo ============================================================
pause
