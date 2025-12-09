@echo off
REM Start script for Tour Recommendation System (Windows)

echo ============================================================
echo Tour Recommendation System - Starting...
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo.
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/update dependencies
echo Checking dependencies...
pip install -q -r requirements.txt
echo.

REM Check Docker
echo Checking Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Docker is not running!
    echo Please start Docker Desktop and run this script again.
    echo.
    pause
    exit /b 1
)
echo Docker is running.
echo.

REM Check if database is running
docker ps | findstr tour_db >nul 2>&1
if errorlevel 1 (
    echo Database not running. Starting...
    cd docker
    docker-compose up -d
    cd ..
    echo Waiting for database to initialize (20 seconds)...
    timeout /t 20 /nobreak >nul
    echo.
)

REM Run the application
echo Starting application...
echo.
python run.py

REM Cleanup
echo.
echo Application closed.
pause

