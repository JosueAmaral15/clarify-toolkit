"""
GUI Package for Clarify

Contains all dock widgets and UI components with modular architecture.
"""

# Base classes and mixins
from .base_dock import (
    BaseDock, StandardToolDock, ProcessorWorkerBase,
    FileInputMixin, ResultsOutputMixin, ActionButtonsMixin,
    OptionsGroupMixin, ValidationMixin
)

# Tool docks
from .case_converter_dock import CaseConverterDock
from .placeholder_replacer_dock import PlaceholderReplacerDock
from .json_search_dock import JsonSearchDock
from .text_extractor_dock import TextExtractorDock
from .ai_processor_dock import AIProcessorDock
from .json_translate_dock import JsonTranslateDock
from .json_rewriter_dock import JsonRewriterDock

__all__ = [
    # Base classes
    'BaseDock', 'StandardToolDock', 'ProcessorWorkerBase',
    # Mixins
    'FileInputMixin', 'ResultsOutputMixin', 'ActionButtonsMixin',
    'OptionsGroupMixin', 'ValidationMixin',
    # Tool docks
    'CaseConverterDock', 'PlaceholderReplacerDock', 'JsonSearchDock',
    'TextExtractorDock', 'AIProcessorDock', 'JsonTranslateDock',
    'JsonRewriterDock'
]
