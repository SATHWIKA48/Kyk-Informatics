#!/bin/bash
# One-command setup for the KYK Technologies Django backend + website.
# Usage: bash setup.sh

set -e
cd "$(dirname "$0")"

echo "== KYK Technologies backend setup =="

if ! command -v python3 &> /dev/null; then
    echo "Python 3 was not found. Install it from https://www.python.org/downloads/ first, then re-run this script."
    exit 1
fi

echo "-- Creating virtual environment (venv/) --"
python3 -m venv venv

echo "-- Activating virtual environment --"
source venv/bin/activate

echo "-- Installing dependencies --"
pip install --upgrade pip > /dev/null
pip install -r requirements.txt

echo "-- Setting up the database --"
python manage.py migrate

echo ""
echo "== Setup complete =="
echo "Starting the server now at http://127.0.0.1:8000/"
echo "Press Ctrl+C to stop it. Next time, just run: source venv/bin/activate && python manage.py runserver"
echo ""

python manage.py runserver
