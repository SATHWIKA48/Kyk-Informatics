@echo off
REM One-command setup for the KYK Technologies Django backend + website.
REM Usage: double-click setup.bat, or run it from cmd/PowerShell.

cd /d "%~dp0"

echo == KYK Technologies backend setup ==

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Install it from https://www.python.org/downloads/ first ^(check "Add Python to PATH" during install^), then re-run this script.
    pause
    exit /b 1
)

echo -- Creating virtual environment (venv\) --
python -m venv venv

echo -- Activating virtual environment --
call venv\Scripts\activate.bat

echo -- Installing dependencies --
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

echo -- Setting up the database --
python manage.py migrate

echo.
echo == Setup complete ==
echo Starting the server now at http://127.0.0.1:8000/
echo Press Ctrl+C to stop it. Next time, just run: venv\Scripts\activate ^&^& python manage.py runserver
echo.

python manage.py runserver
