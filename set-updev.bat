@echo off

echo ===============================
echo Setting up scanX
echo ===============================

python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed.
    pause
    exit /b
)

echo Creating virtual environment...

python -m venv venv

call venv\Scripts\activate

python -m pip install --upgrade pip

pip install -r requirements.txt

if not exist .env (
    if exist .env.example (
        copy .env.example .env
    ) else (
        type nul > .env
    )
)

echo.
echo Setup Complete
echo.
echo Activate using:
echo venv\Scripts\activate
echo.
echo Run:
echo python app.py

pause