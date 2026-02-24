@echo off
REM Quick start script for MCP Git Server (Windows)
REM Runs the Flask HTTP server for local git operations

setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM Colors (Windows doesn't support ANSI, so we'll use simple text)
echo.
echo ============================================
echo   MCP Git Server - Quick Start (Windows)
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3 from https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Flask not installed. Installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
) else (
    echo [INFO] Flask is already installed
)

REM Set default git timeout
set "GIT_TIMEOUT=240"

REM Get command line arguments
set "HOST=127.0.0.1"
set "PORT=5000"
set "DEBUG="

if not "%~1"=="" set "HOST=%~1"
if not "%~2"=="" set "PORT=%~2"
if not "%~3"=="" set "DEBUG=%~3"

REM Load .env file if it exists
if exist ".env" (
    echo [INFO] Loading .env file...
    for /f "delims== tokens=1,*" %%a in (.env) do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set "%%a=%%b"
        )
    )
)

cls
echo.
echo ============================================
echo   MCP Git Server - Starting Flask Server
echo ============================================
echo.
echo Host: !HOST!
echo Port: !PORT!
echo Debug: !DEBUG:~0,0!
echo.
echo Server will be available at: http://!HOST!!PORT!
echo Health check endpoint: http://!HOST!!PORT!/api/health
echo.
echo To use with Copilot in VS Code:
echo 1. Configure MCP settings in VS Code
echo 2. Keep this Flask server running
echo 3. MCP requests will be forwarded to this server
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
if not "!DEBUG!"=="" (
    python run_server.py --host !HOST! --port !PORT! --debug
) else (
    python run_server.py --host !HOST! --port !PORT!
)

endlocal
pause
