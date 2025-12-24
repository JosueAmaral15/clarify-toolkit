"""
CLI Module
Command-line interface handlers for Clarify application.

Refactored from src/app.py (Phase 3.1 - v2.9.114)
"""

from .commands import (
    cli_search, cli_replace, cli_insert,
    cli_translate, cli_gtranslate, cli_dedupe
)
from .parser import build_parser
from .utils import split_globs, parse_conditions, build_file_list

__all__ = [
    'cli_search', 'cli_replace', 'cli_insert',
    'cli_translate', 'cli_gtranslate', 'cli_dedupe',
    'build_parser',
    'split_globs', 'parse_conditions', 'build_file_list'
]
