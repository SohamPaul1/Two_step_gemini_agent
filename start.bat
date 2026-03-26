@echo off
REM Gemini Voice Agent Startup Script for Windows

echo Starting Gemini Voice Agent...

REM Check if .env file exists
if not exist .env (
    echo .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo Please edit .env file and add your GOOGLE_API_KEY
    echo Exiting...
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Start the server
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py

pause
