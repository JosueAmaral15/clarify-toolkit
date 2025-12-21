#!/bin/bash
# Clarify GUI Launcher for Linux/Mac
# Make executable: chmod +x clarify_gui.sh
# Double-click or run: ./clarify_gui.sh

echo "========================================"
echo "   Clarify - Text Processing Tool"
echo "          GUI Mode"
echo "========================================"
echo ""

# Change to the directory where this script is located
cd "$(dirname "$0")" || exit 1

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
    echo "The GUI will not work without it."
    echo ""
    echo "To install PySide6, run:"
    echo "  pip3 install PySide6"
    echo ""
    echo "Or use Poetry:"
    echo "  poetry install"
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
        echo "Launching CLI help instead..."
        python3 clarify.py --help
        read -p "Press Enter to exit..."
        exit 0
    fi
fi

# Launch Clarify GUI
echo "Launching Clarify GUI..."
echo ""
python3 clarify.py

# If there was an error, pause to see the message
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Clarify exited with an error"
    read -p "Press Enter to exit..."
fi
