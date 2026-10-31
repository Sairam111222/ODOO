@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo         SolarFlow 360 — SunPower Solutions ERP
echo ========================================================
echo.

cd /d "%~dp0"

:: Step 1: Ensure .env exists
if not exist ".env" (
    echo [1/3] Creating .env from configuration template...
    copy .env.example .env >nul
) else (
    echo [1/3] Environment configuration verified (.env exists).
)

:: Step 2: Check Docker runtime
echo [2/3] Checking Docker engine status...
where docker >nul 2>&1
if %errorlevel% equ 0 (
    docker ps >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Docker engine is running.
        echo Starting PostgreSQL 15 and Odoo 17 CE containers...
        docker compose up -d
        echo.
        echo [3/3] Opening SolarFlow 360 in browser...
        timeout /t 3 >nul
        start http://localhost:8069
        echo ========================================================
        echo SolarFlow 360 is live at: http://localhost:8069
        echo ========================================================
        pause
        exit /b 0
    )
)

:: Step 3: Standalone Python Gateway fallback
echo.
echo [NOTICE] Docker is not active on this system.
echo Launching SolarFlow 360 Local Gateway & AI Engine on Port 8069...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python311\python.exe"
) else (
    set "PYTHON_EXE=python"
)

start "" http://localhost:8069
"%PYTHON_EXE%" server.py
pause
