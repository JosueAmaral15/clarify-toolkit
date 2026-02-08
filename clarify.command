#!/bin/bash
# ============================================================================
# Clarify - Main Launcher for macOS
# ============================================================================
# Purpose: Launch Clarify GUI application following Protocolo Simplicidade 3
# Usage: chmod +x clarify.command && double-click in Finder
# Author: Josué Amaral
# Date: 2026-01-07
# ============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "   CLARIFY - JSON Processing Desktop Application (macOS)"
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

# Check if Python 3 is installed (try python3 first, then python)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+' | head -1)
    if [ "$PYTHON_VERSION" -ge 3 ]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3 is not installed"
    echo ""
    echo "Please install Python 3.10+ from:"
    echo "  • Official: https://www.python.org/downloads/macos/"
    echo "  • Homebrew: brew install python3"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Display Python version
echo "Python version:"
$PYTHON_CMD --version
echo ""

# Check Python version (minimum 3.10)
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    CURRENT_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "WARNING: Python version $CURRENT_VERSION detected"
    echo "Clarify requires Python 3.10 or higher"
    echo "Some features may not work correctly"
    echo ""
fi

# Check if Poetry is installed and configured
POETRY_CMD=""
USE_POETRY=false

echo "Checking environment..."

if command -v poetry &> /dev/null; then
    echo "✓ Poetry detected"
    
    # Check if poetry.lock exists (poetry project)
    if [ -f "poetry.lock" ]; then
        echo "✓ Poetry project detected"
        
        # Check if poetry environment is set up
        if poetry env info &> /dev/null; then
            echo "✓ Poetry virtualenv configured"
            USE_POETRY=true
            POETRY_CMD="poetry run"
            
            # Install dependencies if needed
            if ! $POETRY_CMD $PYTHON_CMD -c "import PySide6" 2>/dev/null; then
                echo ""
                echo "Installing dependencies with Poetry..."
                poetry install --no-dev
                echo ""
            fi
        else
            echo "⚠ Poetry virtualenv not configured"
            echo "Run: poetry install"
        fi
    fi
fi

if [ "$USE_POETRY" = false ]; then
    echo "Using system Python"
    
    # Check if PySide6 is installed
    echo "Checking dependencies..."
    if ! $PYTHON_CMD -c "import PySide6" 2>/dev/null; then
        echo ""
        echo "WARNING: PySide6 is not installed!"
        echo "The GUI requires PySide6 to run."
        echo ""
        
        # Suggest poetry if available
        if command -v poetry &> /dev/null && [ -f "pyproject.toml" ]; then
            echo "RECOMMENDED: Install with Poetry"
            echo "  poetry install"
            echo ""
        fi
        
        read -p "Would you like to install it with pip now? (y/n): " INSTALL
        
        if [[ "$INSTALL" == "y" || "$INSTALL" == "Y" ]]; then
            echo ""
            echo "Installing PySide6..."
            
            # Detect pip command
            PIP_CMD=""
            if command -v pip3 &> /dev/null; then
                PIP_CMD="pip3"
            elif command -v pip &> /dev/null; then
                PIP_CMD="pip"
            else
                echo "ERROR: pip not found"
                echo "Please install pip: $PYTHON_CMD -m ensurepip --upgrade"
                read -p "Press Enter to exit..."
                exit 1
            fi
            
            $PIP_CMD install PySide6
            
            # Verify installation
            if [ $? -ne 0 ]; then
                echo ""
                echo "ERROR: Failed to install PySide6"
                echo ""
                echo "Try one of these alternatives:"
                echo "  • poetry install (recommended)"
                echo "  • $PIP_CMD install --user PySide6"
                echo "  • $PYTHON_CMD -m pip install PySide6"
                echo "  • brew install pyside6 (if using Homebrew)"
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
            echo "Install with: poetry install (recommended) or pip3 install PySide6"
            echo ""
            read -p "Press Enter to exit..."
            exit 1
        fi
    fi
fi

# Launch Clarify GUI
echo "Launching Clarify..."
echo ""

# Run the application with appropriate command
if [ "$USE_POETRY" = true ]; then
    echo "Running with Poetry virtualenv..."
    $POETRY_CMD $PYTHON_CMD -m src
else
    echo "Running with system Python..."
    $PYTHON_CMD -m src
fi

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
