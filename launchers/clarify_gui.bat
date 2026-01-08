@echo off
REM Clarify GUI Launcher for Windows
REM Double-click this file to launch Clarify GUI

title Clarify - GUI Launcher

echo ========================================
echo    Clarify - GUI Launcher
echo ========================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
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
    echo The GUI requires PySide6 to run.
    echo.
    echo To install, run:
    echo   pip install PySide6
    echo.
    set /p INSTALL="Would you like to install it now? (y/n): "
    if /i "%INSTALL%"=="y" (
        echo.
        echo Installing PySide6...
        pip install PySide6
        if errorlevel 1 (
            echo.
            echo ERROR: Failed to install PySide6
            echo.
            echo Try running as Administrator or use:
            echo   pip install --user PySide6
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
        pause
        exit /b 1
    )
)

REM Launch Clarify GUI
echo Launching Clarify GUI...
echo.
python -m src

REM If there was an error, pause to see the message
if errorlevel 1 (
    echo.
    echo ERROR: Clarify exited with error code %errorlevel%
    pause
    exit /b 1
)
