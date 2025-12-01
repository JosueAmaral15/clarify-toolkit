"""JSON Rewriter: deduplicate, join keys, and process TypeScript/JavaScript objects.

This module includes the CRITICAL BUG FIX for data loss in sanitize_keys_and_values.
"""

from .types import Obj, JSONNode, parse_json_preserving_duplicates_text, freeze
from .ts_parser import (
    find_object_block,
    ts_block_to_json_text,
    strip_bom,
    scan_find_next_lbrace,
    extract_balanced_from,
    strip_comments_code,
    lift_strings_to_placeholders,
    restore_placeholders,
    quote_bare_and_numeric_keys,
    remove_trailing_commas
)
from .operations import dedupe, join_keys, eliminate_duplicates, merge_obj_values, exclude_numeric_keys, skip_empty_values, avoid_duplicate_child_keys, remove_duplicate_array_values, enforce_consistent_case, normalize_escaping, array_to_object_conversion, skip_keys_without_siblings, remove_duplicate_objects
from .serializer import dump_ts_node, dump_ts_obj, dump_ts_array, dump_ts_scalar, collapse_blank_lines
from .rewriter import sanitize_keys_and_values, ts_process_full_preserving, load_translation_dict
from .reference_updater import (
    scan_project_references,
    build_substitution_map_by_value,
    update_references_in_project,
    extract_all_keys_from_obj
)

__all__ = [
    'Obj', 'JSONNode', 'parse_json_preserving_duplicates_text', 'freeze',
    'find_object_block', 'ts_block_to_json_text',
    'dedupe', 'join_keys', 'eliminate_duplicates', 'merge_obj_values', 'exclude_numeric_keys', 'skip_empty_values', 'avoid_duplicate_child_keys', 'remove_duplicate_array_values', 'enforce_consistent_case', 'normalize_escaping', 'array_to_object_conversion', 'skip_keys_without_siblings', 'remove_duplicate_objects',
    'dump_ts_node', 'dump_ts_obj', 'dump_ts_array', 'dump_ts_scalar', 'collapse_blank_lines',
    'sanitize_keys_and_values', 'ts_process_full_preserving', 'load_translation_dict',
    'scan_project_references', 'build_substitution_map_by_value', 'update_references_in_project', 'extract_all_keys_from_obj'
]
