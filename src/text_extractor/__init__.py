"""
Text to JSON Extractor Module
==============================

Extracts structured data from HTML/JSX files and converts to JSON.

Features:
- Parse JSX/HTML tags and extract attributes
- Build hierarchical paths from tag structure
- Normalize text (case styles, truncation)
- Output flat paths or nested JSON
- Filter standard HTML tags

Components:
- jsx_parser: Parse JSX/HTML tag structures
- normalizer: Text normalization utilities
- path_builder: Build hierarchical paths from tag stacks
- extractor: Main extraction logic

Author: Josué Amaral
Date: 2025-11-24
"""

from .jsx_parser import JSXParser, parse_jsx_file
from .normalizer import normalize_text, smart_truncate
from .path_builder import PathBuilder, build_nested_json
from .extractor import extract_from_file, extract_from_directory
from .generic_parser import GenericScopeParser, parse_generic_file

__all__ = [
    'JSXParser',
    'parse_jsx_file',
    'normalize_text',
    'smart_truncate',
    'PathBuilder',
    'build_nested_json',
    'extract_from_file',
    'extract_from_directory',
    'GenericScopeParser',
    'parse_generic_file',
]
