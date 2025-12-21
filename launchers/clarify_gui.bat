@echo off
REM Clarify GUI Launcher for Windows
REM Double-click this file to launch Clarify GUI

echo ========================================
echo    Clarify - Text Processing Tool
echo           GUI Mode
echo ========================================
echo.

REM Change to the directory where this script is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Check if PySide6 is installed
echo Checking dependencies...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: PySide6 is not installed!
    echo The GUI will not work without it.
    echo.
    echo To install PySide6, run:
    echo   pip install PySide6
    echo.
    echo Or use Poetry:
    echo   poetry install
    echo.
    set /p INSTALL="Would you like to install it now? (y/n): "
    if /i "%INSTALL%"=="y" (
        echo.
        echo Installing PySide6...
        pip install PySide6
        if errorlevel 1 (
            echo.
            echo ERROR: Failed to install PySide6
            pause
            exit /b 1
        )
        echo.
        echo PySide6 installed successfully!
        echo.
    ) else (
        echo.
        echo Launching CLI mode instead...
        python clarify.py --help
        pause
        exit /b 0
    )
)

REM Launch Clarify GUI
echo Launching Clarify GUI...
echo.
python clarify.py

REM If there was an error, pause to see the message
if errorlevel 1 (
    echo.
    echo ERROR: Clarify exited with error code %errorlevel%
    pause
)
