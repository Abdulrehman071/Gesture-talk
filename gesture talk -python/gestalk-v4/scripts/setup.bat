@echo off
title GestaTalk v4.1 — Setup
echo ============================================
echo   GestaTalk v4.1 — Setup Script
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    echo         from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

:: Upgrade pip
echo [1/3] Upgrading pip...
python -m pip install --upgrade pip --quiet

:: Install dependencies
echo [2/3] Installing dependencies from requirements.txt...
pip install -r ..\requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Dependency install failed. Check the error above.
    pause
    exit /b 1
)

echo.
echo [3/3] Setup complete!
echo.
echo ============================================
echo   To run GestaTalk:
echo     cd gestalk-v4
echo     python main.py
echo ============================================
echo.
pause
