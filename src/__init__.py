"""
Clarify - Text Processing & JSON Manipulation Tool
===================================================

A powerful tool for text search/replace and JSON processing with GUI and CLI modes.

Main Modules:
-------------
- core: Search, replace, insert, and filtering operations
- utils: File operations, text processing, and TypeScript utilities
- rewriter: JSON Rewriter with deduplication and key operations
- translators: JSON Translator (in development)
- ui: Graphical User Interface (in development)
- cli: Command Line Interface (in development)

Usage:
------
    # As a module
    python -m src
    
    # Direct entry point
    python clarify.py
    
    # GUI mode
    python clarify.py
    
    # CLI mode
    python clarify.py search <path> --query "text"
    python clarify.py replace <path> --query "old" --replacement "new"
    python clarify.py dedupe <file.ts> --join-keys

Author: Josué Amaral
Date: 2025-11-23
Version: 2.9.44
"""

__version__ = "2.9.44"
__author__ = "Josué Amaral"
__email__ = "josue.amaral@example.com"

# Lazy import of main function to avoid loading GUI dependencies
def main():
    """Main entry point - lazy import to avoid GUI dependencies at module level."""
    from .app import main as app_main
    return app_main()

__all__ = ["main", "__version__", "__author__"]
