@echo off
echo ========================================
echo Job Application Bot - Setup Script
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python found!
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

echo [3/3] Checking configuration...
if not exist config.json (
    echo Creating config.json from example...
    copy config.json.example config.json >nul
    echo.
    echo ========================================
    echo IMPORTANT: Setup Required
    echo ========================================
    echo Please edit config.json and fill in:
    echo   - Your login credentials (Naukri, LinkedIn, Indeed)
    echo   - Your profile information
    echo   - Job search preferences
    echo.
    echo Then run: python run_bot.py
    echo ========================================
) else (
    echo config.json already exists!
    echo.
    echo Setup complete! Run: python run_bot.py
)

echo.
pause
