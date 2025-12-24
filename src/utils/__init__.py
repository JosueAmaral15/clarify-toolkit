"""Utility functions for file operations, text processing, and TypeScript/JavaScript handling."""

from .file_utils import walk_files, read_text, write_text, safe_backup_file
from .text_utils import (
    parse_exclusion_patterns,
    mask_exclusions,
    unmask_exclusions,
    compile_value_union_regex
)
from .ts_utils import load_ts_object, dump_ts_object, strip_export_default, to_json_ish
from .stats_formatter import format_removal_statistics

__all__ = [
    'walk_files', 'read_text', 'write_text', 'safe_backup_file',
    'parse_exclusion_patterns', 'mask_exclusions', 'unmask_exclusions', 'compile_value_union_regex',
    'load_ts_object', 'dump_ts_object', 'strip_export_default', 'to_json_ish',
    'format_removal_statistics'
]
