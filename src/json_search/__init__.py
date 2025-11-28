"""
JSON Search Module
==================

Provides functionality to search for keys and values in JSON/TS/TSX files.

Features:
- Index JSON/TS/TSX files from directories or single files
- Flatten nested JSON structures to dot-path notation
- Search with case sensitivity, whole word, and regex support
- Extract TypeScript object literals with json5 parsing
- Line number detection for search results

Components:
- flattener: Flatten nested JSON to dot-paths
- ts_extractor: Extract and parse TS/TSX object literals
- indexer: Build searchable index from files
- query_parser: Parse and execute search queries

Author: Josué Amaral
Date: 2025-11-24
"""

from .flattener import flatten_object
from .ts_extractor import extract_top_level_objects_from_ts, guess_line_number
from .indexer import ProjectIndexer, FlatIndex
from .query_parser import parse_composite_query, resolve_query, match_with_options

__all__ = [
    'flatten_object',
    'extract_top_level_objects_from_ts',
    'guess_line_number',
    'ProjectIndexer',
    'FlatIndex',
    'parse_composite_query',
    'resolve_query',
    'match_with_options',
]
