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
from .history_dock import HistoryDock
from .file_list_dock import FileListDock
from .tutorials_dock import TutorialsDock
from .editor_dock import EditorDock
from .text_to_json_dock import TextToJsonDock
from .json_editor_tab import JsonEditorTab
from .json_validator import JsonValidator

__all__ = [
    # Base classes
    'BaseDock', 'StandardToolDock', 'ProcessorWorkerBase',
    # Mixins
    'FileInputMixin', 'ResultsOutputMixin', 'ActionButtonsMixin',
    'OptionsGroupMixin', 'ValidationMixin',
    # Tool docks
    'CaseConverterDock', 'PlaceholderReplacerDock', 'JsonSearchDock',
    'TextExtractorDock', 'AIProcessorDock', 'JsonTranslateDock',
    'JsonRewriterDock', 'HistoryDock', 'FileListDock', 'TutorialsDock',
    'EditorDock', 'TextToJsonDock',
    # Editor components
    'JsonEditorTab', 'JsonValidator'
]
