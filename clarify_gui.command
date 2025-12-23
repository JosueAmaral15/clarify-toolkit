#!/bin/bash
# Clarify GUI Launcher for macOS
# Make executable: chmod +x clarify_gui.command
# Double-click this file in Finder to launch

echo "========================================"
echo "   Clarify - GUI Launcher (macOS)"
echo "========================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Check if Python 3 is installed (try python3 first, then python)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '(?<=Python )\d+')
    if [ "$PYTHON_VERSION" -ge 3 ]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.10+ from:"
    echo "  • https://www.python.org/downloads/macos/"
    echo "  • Or use Homebrew: brew install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo "Python version:"
$PYTHON_CMD --version
echo ""

# Check if PySide6 is installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import PySide6" 2>/dev/null; then
    echo ""
    echo "WARNING: PySide6 is not installed!"
    echo "The GUI requires PySide6 to run."
    echo ""
    echo "To install, run:"
    echo "  pip3 install PySide6"
    echo ""
    read -p "Would you like to install it now? (y/n): " INSTALL
    if [[ "$INSTALL" == "y" || "$INSTALL" == "Y" ]]; then
        echo ""
        echo "Installing PySide6..."
        pip3 install PySide6
        if [ $? -ne 0 ]; then
            echo ""
            echo "ERROR: Failed to install PySide6"
            echo ""
            echo "Try running:"
            echo "  pip3 install --user PySide6"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
        echo ""
        echo "PySide6 installed successfully!"
        echo ""
    else
        echo ""
        echo "Cannot launch GUI without PySide6"
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Launch Clarify GUI
echo "Launching Clarify GUI..."
echo ""
$PYTHON_CMD -m src

# If there was an error, pause to see the message
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Clarify exited with an error"
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "Clarify closed successfully"
