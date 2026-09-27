"""
JSON Translation Module

Provides functionality for translating text using JSON/TS dictionary files.

Refactored from src/app.py (Phase 3.2 - v2.9.114)
"""

from .json_translate_helpers import (
    _escape_variants_for_quotes,
    _compile_value_union_regex,
    _apply_scoped_translation_tag_balanced,
    mask_existing_placeholders,
    unmask_existing_placeholders,
    apply_scoped_translation,
    apply_scoped_translations,
    process_translate_file,
    load_translation_dict,
    flatten_dict_paths,
    translate_replace_texts,
    read_translation_dict,
    RE_PLACEHOLDER,
)

__all__ = [
    '_escape_variants_for_quotes',
    '_compile_value_union_regex',
    '_apply_scoped_translation_tag_balanced',
    'load_translation_dict',
    'flatten_dict_paths',
    'translate_replace_texts',
    'apply_scoped_translation',
    'apply_scoped_translations',
    'mask_existing_placeholders',
    'unmask_existing_placeholders',
    'RE_PLACEHOLDER',
    'process_translate_file',
    'read_translation_dict',
]
