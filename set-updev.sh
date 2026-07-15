#!/usr/bin/env bash

set -e

echo "================================="
echo "Setting up scanX"
echo "================================="

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed."
    exit 1
fi

echo "Creating virtual environment..."

python3 -m venv venv

echo "Activating venv..."

source venv/bin/activate

echo "Upgrading pip..."

python -m pip install --upgrade pip

echo "Installing dependencies..."

pip install -r requirements.txt

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo ".env created from template."
    else
        touch .env
        echo ".env created."
    fi
fi

echo ""
echo "================================="
echo "Setup Complete"
echo ""
echo "Activate using:"
echo "source venv/bin/activate"
echo ""
echo "Run using:"
echo "python app.py"
echo "================================="