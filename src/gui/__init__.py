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

# Dock Factory (v2.9.114 - Phase 3.3)
from .dock_factory import DockFactory

# Menu Builder (v2.9.114 - Phase 3.4)
from .menu_builder import MenuBuilder

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
from .jsx_extractor_dock import JSXExtractorDock
from .json_editor_tab import JsonEditorTab
from .json_validator import JsonValidator
from .set_operations_dock import SetOperationsDock
from .shortcuts_dialog import ShortcutsDialog
from .google_translate_dock import GoogleTranslateDock
from .formula_dock import FormulaDock

__all__ = [
    # Base classes
    'BaseDock', 'StandardToolDock', 'ProcessorWorkerBase',
    # Mixins
    'FileInputMixin', 'ResultsOutputMixin', 'ActionButtonsMixin',
    'OptionsGroupMixin', 'ValidationMixin',
    # Dock Factory (Phase 3.3)
    'DockFactory',
    # Menu Builder (Phase 3.4)
    'MenuBuilder',
    # Tool docks
    'CaseConverterDock', 'PlaceholderReplacerDock', 'JsonSearchDock',
    'TextExtractorDock', 'AIProcessorDock', 'JsonTranslateDock',
    'JsonRewriterDock', 'HistoryDock', 'FileListDock', 'TutorialsDock',
    'EditorDock', 'TextToJsonDock', 'JSXExtractorDock', 'SetOperationsDock',
    'GoogleTranslateDock', 'FormulaDock',
    # Editor components
    'JsonEditorTab', 'JsonValidator',
    # Dialogs
    'ShortcutsDialog'
]
