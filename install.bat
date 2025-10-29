@echo off
REM Docling OCR Installation Script for Windows

echo ========================================
echo Docling OCR Installation
echo ========================================
echo.

REM Check Python
echo Checking Python version...
python --version 2>nul
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10 or higher
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo.
echo Creating directories...
if not exist "temp" mkdir temp
if not exist "models" mkdir models
if not exist "logs" mkdir logs

REM Copy environment file if not exists
if not exist ".env" (
    echo.
    echo Creating .env file from example...
    copy env.example .env
    echo Please edit .env file to configure the service
)

REM Download models
echo.
echo ========================================
echo Model Download
echo ========================================
set /p download_models="Do you want to download Docling models now? (y/n): "
if /i "%download_models%"=="y" (
    echo Downloading models...
    python scripts\download_models.py -o .\models
) else (
    echo Skipping model download. You can download later with:
    echo   python scripts\download_models.py
)

REM Verify installation
echo.
echo ========================================
echo Verifying Installation
echo ========================================
python scripts\verify_installation.py

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the service:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --host 0.0.0.0 --port 8002
echo.
echo Or use Docker:
echo   docker-compose up -d
echo.
echo Access the web UI at: http://localhost:8002
echo API documentation at: http://localhost:8002/docs
echo.
pause

