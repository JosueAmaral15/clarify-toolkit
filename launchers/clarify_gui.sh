#!/bin/bash
# Clarify GUI Launcher for Linux/Unix
# Make executable: chmod +x clarify_gui.sh
# Run: ./clarify_gui.sh or double-click in file manager

echo "========================================"
echo "   Clarify - GUI Launcher"
echo "========================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ from your package manager"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo "Python version:"
python3 --version
echo ""

# Check if PySide6 is installed
echo "Checking dependencies..."
if ! python3 -c "import PySide6" 2>/dev/null; then
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
python3 -m src

# If there was an error, pause to see the message
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Clarify exited with an error"
    read -p "Press Enter to exit..."
    exit 1
fi
