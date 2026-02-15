@echo off
REM ============================================================================
REM Clarify - Main Launcher for Windows
REM ============================================================================
REM Purpose: Launch Clarify GUI application following Protocolo Simplicidade 3
REM Usage: Double-click this file or run from command prompt
REM Author: Josué Amaral
REM Date: 2026-01-07
REM ============================================================================

title Clarify - Application Launcher

echo ============================================================================
echo    CLARIFY - JSON Processing Desktop Application
echo ============================================================================
echo.

REM Verify we're in the project root
if not exist "src\" (
    echo ERROR: src\ directory not found
    echo This script must be run from the Clarify project root directory
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Check if Poetry is installed and configured
set USE_POETRY=false
set POETRY_CMD=

echo Checking environment...

where poetry >nul 2>&1
if not errorlevel 1 (
    echo - Poetry detected
    
    REM Check if poetry.lock exists (poetry project)
    if exist "poetry.lock" (
        echo - Poetry project detected
        
        REM Check if poetry environment is set up
        poetry env info >nul 2>&1
        if not errorlevel 1 (
            echo - Poetry virtualenv configured
            set USE_POETRY=true
            set POETRY_CMD=poetry run
            
            REM Install dependencies if needed
            poetry run python -c "import PySide6" >nul 2>&1
            if errorlevel 1 (
                echo.
                echo Installing dependencies with Poetry...
                poetry install --no-dev
                echo.
            )
        ) else (
            echo ! Poetry virtualenv not configured
            echo   Run: poetry install
        )
    )
)

if "%USE_POETRY%"=="false" (
    echo Using system Python
    
    REM Check if PySide6 is installed
    echo Checking dependencies...
    python -c "import PySide6" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo WARNING: PySide6 is not installed!
        echo The GUI requires PySide6 to run.
        echo.
        
        REM Suggest poetry if available
        where poetry >nul 2>&1
        if not errorlevel 1 (
            if exist "pyproject.toml" (
                echo RECOMMENDED: Install with Poetry
                echo   poetry install
                echo.
            )
        )
        
        set /p INSTALL="Would you like to install it with pip now? (y/n): "
        if /i "%INSTALL%"=="y" (
            echo.
            echo Installing PySide6...
            python -m pip install PySide6
            if errorlevel 1 (
                echo.
                echo ERROR: Failed to install PySide6
                echo.
                echo Try running as Administrator or install with:
                echo   - poetry install (recommended)
                echo   - pip install --user PySide6
                echo.
                pause
                exit /b 1
            )
            echo.
            echo PySide6 installed successfully!
            echo.
        ) else (
            echo.
            echo Cannot launch GUI without PySide6
            echo Install with: poetry install (recommended) or pip install PySide6
            echo.
            pause
            exit /b 1
        )
    )
)

REM Launch Clarify GUI
echo Launching Clarify...
echo.

REM Run the application with appropriate command
if "%USE_POETRY%"=="true" (
    echo Running with Poetry virtualenv...
    poetry run python -m src
) else (
    echo Running with system Python...
    python -m src
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo ============================================================================
    echo ERROR: Clarify exited with an error
    echo ============================================================================
    echo.
    echo Common issues:
    echo   - Missing dependencies: pip install -r requirements.txt
    echo   - Configuration error: Check config/ directory
    echo   - Python version: Requires Python 3.10+
    echo.
    echo For support, check: docs/README.md
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo Clarify closed successfully
echo ============================================================================
