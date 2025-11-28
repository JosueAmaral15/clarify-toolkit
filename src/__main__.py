#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clarify - Main Entry Point for Module Execution
------------------------------------------------
Allows running Clarify as a Python module: python -m src

This is the standard Python way to run packages as executables.
"""

import sys
from .app import main

if __name__ == "__main__":
    sys.exit(main())
