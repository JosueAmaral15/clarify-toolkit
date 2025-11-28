#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clarify - Convenience Entry Point
----------------------------------
This file exists ONLY for user convenience and compatibility.

WHY THIS FILE EXISTS:
    Users expect to run: "python clarify.py"
    This is a thin wrapper that delegates to the real application in src/

THE REAL APPLICATION IS IN:
    src/app.py - Main application code (~2,700 lines)
    src/__main__.py - Standard Python module entry point

RECOMMENDED USAGE:
    python clarify.py              # This file (convenience wrapper)
    python -m src                  # Standard Python way (recommended)
    ./clarify_gui.sh               # GUI launcher script (Linux/Mac)
    clarify_gui.bat                # GUI launcher script (Windows)

CLI COMMANDS:
    python clarify.py search ...   # Search files
    python clarify.py replace ...  # Replace text
    python clarify.py insert ...   # Insert text
    python clarify.py translate ...# JSON translation
    python clarify.py dedupe ...   # JSON deduplication
    python clarify.py --help       # Show help

DEVELOPER NOTE:
    This is a THIN WRAPPER - all logic is in src/
    To understand the code, look at:
        - src/app.py (main application)
        - src/core/ (search, replace, insert)
        - src/utils/ (utilities)
        - src/rewriter/ (JSON processing)

Author: Josué Amaral
Date: 2025-11-23
Version: 2.1.0
"""

import sys
import os

# Ensure current directory is in path for src/ import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# This is just a wrapper - the real main() is in src/__init__.py
# which lazy-loads from src/app.py to avoid GUI dependencies at import
if __name__ == "__main__":
    from src import main
    sys.exit(main())
