"""Core functionality for search, replace, insert, and filtering operations."""

from .search_replace import SearchOptions, preserve_case_like, replace_in_text
from .insert import InsertMode, insert_at_line
from .filters import Condition, filter_files_by_conditions, OPS, extract_scope_content
from .rewriter_cli import cli_dedupe

__all__ = [
    'SearchOptions', 'preserve_case_like', 'replace_in_text',
    'InsertMode', 'insert_at_line',
    'Condition', 'filter_files_by_conditions', 'OPS', 'extract_scope_content',
    'cli_dedupe'
]
