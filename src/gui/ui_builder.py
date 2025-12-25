"""
UI Builder for MainWindow

Centralizes UI construction logic from MainWindow._build_ui().
Extracted as part of Phase 3.9 refactoring.

Author: Refactoring Phase 3.9
Date: 2024-12-24
Version: v2.9.114
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import MainWindow

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ..gui.progress import ProgressManager
from ..gui.panels import SearchReplacePanel, InsertPanel


class UIBuilder:
    """
    Builds the main UI components for MainWindow.
    
    Handles creation of:
    - Main container and layout
    - Tab widget with close buttons
    - Progress manager
    - Status bar
    - Search/Replace and Insert panels
    """
    
    @staticmethod
    def build_main_ui(main_window: 'MainWindow') -> None:
        """
        Build the complete main UI for the window.
        
        Args:
            main_window: MainWindow instance
        """
        # Main container widget with vertical layout
        main_container = QWidget()
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Tabs (top area)
        main_window.tabs = QTabWidget()
        
        # Enable close buttons on tabs (v2.9.40 - Task: Tools as tabs)
        main_window.tabs.setTabsClosable(True)
        main_window.tabs.tabCloseRequested.connect(main_window._close_tab)
        
        main_layout.addWidget(main_window.tabs)
        
        # Progress Manager (bottom area - v2.5.0)
        main_window.progress_manager = ProgressManager(main_window)
        main_layout.addWidget(main_window.progress_manager)
        
        # Set main container as central widget
        main_window.setCentralWidget(main_container)
        
        # Force central widget to be visible and updated
        main_container.setVisible(True)
        main_container.update()
        
        # Status bar (Sprint 8 - v1.1.0)
        main_window.statusbar = main_window.statusBar()
        main_window.statusbar.showMessage("Ready", 3000)
    
    @staticmethod
    def build_panels(main_window: 'MainWindow') -> None:
        """
        Build Search/Replace and Insert panels.
        
        Args:
            main_window: MainWindow instance
        """
        # Create panels and pass progress_manager reference
        main_window.tab_search = SearchReplacePanel(
            parent=main_window,
            progress_manager=main_window.progress_manager
        )
        main_window.tab_insert = InsertPanel(
            parent=main_window,
            progress_manager=main_window.progress_manager
        )
        
        # Aliases for backward compatibility
        main_window.search_panel = main_window.tab_search
        main_window.insert_panel = main_window.tab_insert
        
        # Add to tabs
        main_window.tabs.addTab(main_window.tab_search, "Search / Replace")
        main_window.tabs.addTab(main_window.tab_insert, "Insert")
        
        # Mark Search/Replace and Insert as not closeable initially (fixed tabs)
        # They will be marked as closeable when saved to QSettings
        # (v2.9.40 - Task: Tools as tabs)
    
    @staticmethod
    def finalize_ui(main_window: 'MainWindow') -> None:
        """
        Apply final touches to the UI (styling, etc.).
        
        Args:
            main_window: MainWindow instance
        """
        # Apply tab close button styling based on theme
        main_window._apply_tab_close_button_style()
        
        # Docks are created on-demand when user opens them via Tools menu
        # No automatic opening to avoid cluttering the interface at startup
        # (v2.9.40 - Now they open as tabs instead of docks)
    
    @staticmethod
    def build_all(main_window: 'MainWindow') -> None:
        """
        Build complete UI in correct order.
        
        Args:
            main_window: MainWindow instance
        """
        UIBuilder.build_main_ui(main_window)
        UIBuilder.build_panels(main_window)
        UIBuilder.finalize_ui(main_window)
