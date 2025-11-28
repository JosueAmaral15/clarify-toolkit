"""
JSON Translation Module

Provides functionality for translating text using JSON/TS dictionary files.
"""

from .translator import (
    CodeAwareJSONTranslator,
    load_translation_dict,
    flatten_dict_paths,
    translate_replace_texts,
)

from .scope import (
    apply_scoped_translation,
    mask_existing_placeholders,
    unmask_existing_placeholders,
    RE_PLACEHOLDER,
)

from .processor import (
    process_translate_file,
)

__all__ = [
    'CodeAwareJSONTranslator',
    'load_translation_dict',
    'flatten_dict_paths',
    'translate_replace_texts',
    'apply_scoped_translation',
    'mask_existing_placeholders',
    'unmask_existing_placeholders',
    'RE_PLACEHOLDER',
    'process_translate_file',
]
