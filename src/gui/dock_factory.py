"""
Dock Factory
Factory pattern for creating and configuring GUI dock widgets.

Refactored from src/app.py MainWindow class (Phase 3.3 - v2.9.114)
Original lines: 1266-1360 (~95 lines of dock creation methods)

This factory centralizes dock creation logic, reducing duplication and
making it easier to manage dock configurations.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QMainWindow, QDockWidget

try:
    from PySide6.QtCore import Qt
except ImportError:
    Qt = None


class DockFactory:
    """
    Factory for creating and configuring dock widgets.
    
    Handles the common pattern of:
    1. Creating a dock instance
    2. Adding it to the main window
    3. Setting initial visibility (hidden by default)
    4. Optionally connecting signals
    """
    
    @staticmethod
    def create_dock(main_window: 'QMainWindow',
                   dock_class,
                   dock_attr_name: str,
                   area: 'Qt.DockWidgetArea' = None,
                   hide: bool = True,
                   signal_connections: Optional[dict] = None,
                   **dock_kwargs) -> 'QDockWidget':
        """
        Create and configure a dock widget.
        
        Args:
            main_window: The main window to add the dock to
            dock_class: The dock widget class to instantiate
            dock_attr_name: Attribute name to store dock in main_window (e.g., 'dock_translate')
            area: Dock area (default: RightDockWidgetArea)
            hide: Whether to hide dock initially (default: True)
            signal_connections: Dict of {signal_name: slot} to connect
            **dock_kwargs: Additional kwargs for dock constructor
            
        Returns:
            The created dock widget
            
        Example:
            >>> dock = DockFactory.create_dock(
            ...     self, JsonTranslateDock, 'dock_translate',
            ...     area=Qt.RightDockWidgetArea
            ... )
        """
        if area is None and Qt is not None:
            area = Qt.RightDockWidgetArea
        
        # Create dock instance (pass parent as keyword argument for consistency)
        dock = dock_class(parent=main_window, **dock_kwargs)
        
        # Store in main window
        setattr(main_window, dock_attr_name, dock)
        
        # Add to main window
        if area is not None:
            main_window.addDockWidget(area, dock)
        
        # Connect signals if provided
        if signal_connections:
            for signal_name, slot in signal_connections.items():
                signal = getattr(dock, signal_name, None)
                if signal is not None:
                    signal.connect(slot)
        
        # Set initial visibility
        if hide:
            dock.hide()
        
        return dock
    
    @staticmethod
    def create_dock_lazy(main_window: 'QMainWindow',
                        dock_class,
                        dock_attr_name: str,
                        area: 'Qt.DockWidgetArea' = None,
                        **dock_kwargs) -> 'QDockWidget':
        """
        Create dock only if it doesn't exist yet (lazy initialization).
        
        Args:
            main_window: The main window
            dock_class: The dock widget class
            dock_attr_name: Attribute name for the dock
            area: Dock area (default: RightDockWidgetArea)
            **dock_kwargs: Additional kwargs for dock constructor
            
        Returns:
            The dock widget (existing or newly created)
        """
        if not hasattr(main_window, dock_attr_name):
            return DockFactory.create_dock(
                main_window, dock_class, dock_attr_name,
                area=area, **dock_kwargs
            )
        return getattr(main_window, dock_attr_name)
    
    # Convenience methods for common dock types
    
    @staticmethod
    def create_json_translate_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create JSON Translate dock."""
        from ..gui import JsonTranslateDock
        return DockFactory.create_dock(
            main_window, JsonTranslateDock, 'dock_translate'
        )
    
    @staticmethod
    def create_json_rewriter_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create JSON Rewriter dock."""
        from ..gui import JsonRewriterDock
        return DockFactory.create_dock(
            main_window, JsonRewriterDock, 'dock_rewriter'
        )
    
    @staticmethod
    def create_text_extractor_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create Text Extractor dock."""
        from ..gui import TextExtractorDock
        return DockFactory.create_dock(
            main_window, TextExtractorDock, 'dock_text_extractor'
        )
    
    @staticmethod
    def create_placeholder_replacer_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create Placeholder Replacer dock."""
        from ..gui import PlaceholderReplacerDock
        return DockFactory.create_dock(
            main_window, PlaceholderReplacerDock, 'dock_placeholder_replacer'
        )
    
    @staticmethod
    def create_ai_processor_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create AI Processor dock."""
        from ..gui import AIProcessorDock
        return DockFactory.create_dock(
            main_window, AIProcessorDock, 'dock_ai_processor'
        )
    
    @staticmethod
    def create_json_search_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create JSON Search dock."""
        from ..gui import JsonSearchDock
        return DockFactory.create_dock(
            main_window, JsonSearchDock, 'dock_json_search'
        )
    
    @staticmethod
    def create_case_converter_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create Case Converter dock."""
        from ..gui import CaseConverterDock
        return DockFactory.create_dock(
            main_window, CaseConverterDock, 'dock_case_converter'
        )
    
    @staticmethod
    def create_jsx_extractor_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create JSX Parameter Extractor dock."""
        from ..gui import JSXExtractorDock
        return DockFactory.create_dock(
            main_window, JSXExtractorDock, 'dock_jsx_extractor'
        )
    
    @staticmethod
    def create_text_to_json_dock(main_window: 'QMainWindow',
                                 signal_connections: Optional[dict] = None) -> 'QDockWidget':
        """Create Text to JSON Converter dock."""
        from ..gui import TextToJsonDock
        return DockFactory.create_dock(
            main_window, TextToJsonDock, 'dock_text_to_json',
            signal_connections=signal_connections
        )
    
    @staticmethod
    def create_file_list_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create File List dock."""
        from ..gui import FileListDock
        return DockFactory.create_dock(
            main_window, FileListDock, 'dock_file_list'
        )
    
    @staticmethod
    def create_history_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create History dock (lazy initialization with special handling)."""
        from ..gui import HistoryDock
        if Qt is not None:
            area = Qt.BottomDockWidgetArea
        else:
            area = None
        return DockFactory.create_dock_lazy(
            main_window, HistoryDock, 'dock_history',
            area=area, max_entries=10
        )
    
    @staticmethod
    def create_tutorials_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create Tutorials dock (lazy initialization)."""
        from ..gui import TutorialsDock
        return DockFactory.create_dock_lazy(
            main_window, TutorialsDock, 'dock_tutorials'
        )
    
    @staticmethod
    def create_editor_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create Editor dock (lazy initialization)."""
        from ..gui import EditorDock
        return DockFactory.create_dock_lazy(
            main_window, EditorDock, 'dock_editor'
        )
    
    @staticmethod
    def create_google_translate_dock(main_window: 'QMainWindow') -> 'QDockWidget':
        """Create Google Translate dock."""
        from ..gui.google_translate_dock import GoogleTranslateDock
        return DockFactory.create_dock(
            main_window, GoogleTranslateDock, 'dock_google_translate'
        )
