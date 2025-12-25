"""
Tab Manager for MainWindow

Centralizes tab creation logic for tool docks, reducing MainWindow complexity.
Extracted from MainWindow as part of Phase 3.6 refactoring.

Handles lazy-loaded tool docks shown as tabs with on-demand creation.

Author: Refactoring Phase 3.6
Date: 2024-12-24
Version: v2.9.114
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple, Type

if TYPE_CHECKING:
    from PySide6.QtWidgets import QDockWidget
    from ..app import MainWindow


class TabManager:
    """
    Centralized tab management for tool docks.
    
    Provides factory methods for creating and showing tool docks as tabs.
    Each dock is created on-demand (lazy loading) and added to the tab widget.
    """
    
    # Registry of simple tool docks: (dock_attr, DockClass, tab_title, tab_id)
    SIMPLE_TOOLS: Dict[str, Tuple[str, str, str, str]] = {
        'translate': ('dock_translate', 'JsonTranslateDock', 'JSON Translate', 'translate'),
        'rewriter': ('dock_rewriter', 'JsonRewriterDock', 'JSON Rewriter', 'rewriter'),
        'text_extractor': ('dock_text_extractor', 'TextExtractorDock', 'Text Extractor', 'text_extractor'),
        'placeholder_replacer': ('dock_placeholder_replacer', 'PlaceholderReplacerDock', 'Placeholder Replacer', 'placeholder_replacer'),
        'ai_processor': ('dock_ai_processor', 'AIProcessorDock', 'AI Processor', 'ai_processor'),
        'json_search': ('dock_json_search', 'JsonSearchDock', 'JSON Search', 'json_search'),
        'case_converter': ('dock_case_converter', 'CaseConverterDock', 'Case Converter', 'case_converter'),
        'google_translate': ('dock_google_translate', 'GoogleTranslateDock', 'Google Translate', 'google_translate'),
        'jsx_extractor': ('dock_jsx_extractor', 'JSXExtractorDock', 'JSX Extractor', 'jsx_extractor'),
        'file_explorer': ('dock_file_explorer', 'FileExplorerDock', 'File Explorer', 'file_explorer'),
        'tutorials': ('dock_tutorials', 'TutorialsDock', 'Tutorials', 'tutorials'),
    }
    
    @staticmethod
    def show_tool_tab(main_window, tool_name: str) -> None:
        """
        Show a tool as tab (create on-demand).
        
        Args:
            main_window: MainWindow instance
            tool_name: Tool identifier from SIMPLE_TOOLS registry
        """
        if tool_name not in TabManager.SIMPLE_TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        dock_attr, class_name, tab_title, tab_id = TabManager.SIMPLE_TOOLS[tool_name]
        
        # Create dock if doesn't exist
        if not hasattr(main_window, dock_attr):
            from .. import gui
            dock_class = getattr(gui, class_name)
            setattr(main_window, dock_attr, dock_class(main_window))
        
        # Add to tabs
        dock = getattr(main_window, dock_attr)
        main_window._add_tool_tab(dock, tab_title, tab_id)
    
    @staticmethod
    def show_translate(main_window) -> None:
        """Show JSON Translate as tab."""
        TabManager.show_tool_tab(main_window, 'translate')
    
    @staticmethod
    def show_rewriter(main_window) -> None:
        """Show JSON Rewriter as tab."""
        TabManager.show_tool_tab(main_window, 'rewriter')
    
    @staticmethod
    def show_text_extractor(main_window) -> None:
        """Show Text Extractor as tab."""
        TabManager.show_tool_tab(main_window, 'text_extractor')
    
    @staticmethod
    def show_placeholder_replacer(main_window) -> None:
        """Show Placeholder Replacer as tab."""
        TabManager.show_tool_tab(main_window, 'placeholder_replacer')
    
    @staticmethod
    def show_ai_processor(main_window) -> None:
        """Show AI Processor as tab."""
        TabManager.show_tool_tab(main_window, 'ai_processor')
    
    @staticmethod
    def show_json_search(main_window) -> None:
        """Show JSON Search as tab."""
        TabManager.show_tool_tab(main_window, 'json_search')
    
    @staticmethod
    def show_case_converter(main_window) -> None:
        """Show Case Converter as tab."""
        TabManager.show_tool_tab(main_window, 'case_converter')
    
    @staticmethod
    def show_google_translate(main_window) -> None:
        """Show Google Translate as tab."""
        TabManager.show_tool_tab(main_window, 'google_translate')
    
    @staticmethod
    def show_jsx_extractor(main_window) -> None:
        """Show JSX Parameter Extractor as tab."""
        TabManager.show_tool_tab(main_window, 'jsx_extractor')
    
    @staticmethod
    def show_file_explorer(main_window) -> None:
        """Show File Explorer as tab (unified File List + Advanced Search)."""
        TabManager.show_tool_tab(main_window, 'file_explorer')
    
    @staticmethod
    def show_tutorials(main_window) -> None:
        """Show Tutorials as tab."""
        TabManager.show_tool_tab(main_window, 'tutorials')
