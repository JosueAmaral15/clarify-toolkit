#!/bin/bash
# ============================================================================
# Clarify - Main Launcher for Linux/Unix
# ============================================================================
# Purpose: Launch Clarify GUI application following Protocolo Simplicidade 3
# Usage: ./clarify.sh or double-click in file manager
# Author: Josué Amaral
# Date: 2026-01-07
# ============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "   CLARIFY - JSON Processing Desktop Application"
echo "============================================================================"
echo ""

# Get script directory and navigate to project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || {
    echo "ERROR: Cannot navigate to script directory"
    exit 1
}

# Verify we're in the project root
if [ ! -d "src" ]; then
    echo "ERROR: src/ directory not found"
    echo "This script must be run from the Clarify project root directory"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.10+ from your package manager:"
    echo "  • Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  • Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "  • Arch Linux: sudo pacman -S python python-pip"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo "Python version:"
python3 --version
echo ""

# Check Python version (minimum 3.10)
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "WARNING: Python version $PYTHON_VERSION detected"
    echo "Clarify requires Python $REQUIRED_VERSION or higher"
    echo "Some features may not work correctly"
    echo ""
fi

# Check if PySide6 is installed
echo "Checking dependencies..."
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo ""
    echo "WARNING: PySide6 is not installed!"
    echo "The GUI requires PySide6 to run."
    echo ""
    read -p "Would you like to install it now? (y/n): " INSTALL
    
    if [[ "$INSTALL" == "y" || "$INSTALL" == "Y" ]]; then
        echo ""
        echo "Installing PySide6..."
        
        # Try pip3 first
        if command -v pip3 &> /dev/null; then
            python3 -m pip install PySide6
        else
            echo "ERROR: pip3 not found"
            echo "Install manually: sudo apt install python3-pip"
            read -p "Press Enter to exit..."
            exit 1
        fi
        
        # Verify installation
        if [ $? -ne 0 ]; then
            echo ""
            echo "ERROR: Failed to install PySide6"
            echo ""
            echo "Try one of these alternatives:"
            echo "  • pip3 install --user PySide6"
            echo "  • sudo apt install python3-pyside6.qtwidgets (Ubuntu/Debian)"
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
        echo "Install manually with: pip3 install PySide6"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Launch Clarify GUI
echo "Launching Clarify..."
echo ""

# Run the application
python3 -m src

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "============================================================================"
    echo "ERROR: Clarify exited with error code $EXIT_CODE"
    echo "============================================================================"
    echo ""
    echo "Common issues:"
    echo "  • Missing dependencies: pip3 install -r requirements.txt"
    echo "  • Configuration error: Check config/ directory"
    echo "  • Python version: Requires Python 3.10+"
    echo "  • Display issues: Ensure X11/Wayland is running"
    echo ""
    echo "For support, check: docs/README.md"
    echo ""
    read -p "Press Enter to exit..."
    exit $EXIT_CODE
fi

echo ""
echo "============================================================================"
echo "Clarify closed successfully"
echo "============================================================================"
