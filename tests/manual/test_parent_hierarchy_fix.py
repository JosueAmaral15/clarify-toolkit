#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for parent hierarchy fix in FileListTableManager.

Bug: FileListTableManager was instantiated without parent, causing
     _get_main_window() to fail with 'Could not find main window to open editor'.

Fix: Pass parent=self when creating FileListTableManager instances in:
     - file_explorer_dock.py line 254
     - file_list_dock.py line 94

Test validates:
1. FileListTableManager has valid parent after creation
2. Parent chain can traverse up to find main_window
3. _get_main_window() returns correct reference
"""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow

from src.gui.file_explorer_dock import FileExplorerDock
from src.gui.file_list_dock import FileListDock


class MockMainWindow(QMainWindow):
    """Mock main window with dock_editor attribute."""
    def __init__(self):
        super().__init__()
        self.dock_editor = None  # Simulate editor dock attribute


def test_file_explorer_dock_table_manager_has_parent(qtbot):
    """Test that FileExplorerDock sets table_manager parent correctly."""
    # Create dock
    dock = FileExplorerDock(parent=None)
    qtbot.addWidget(dock)
    
    # Validate table_manager has parent
    assert dock.table_manager.parent() is not None
    assert dock.table_manager.parent() == dock


def test_file_list_dock_table_manager_has_parent(qtbot):
    """Test that FileListDock sets table_manager parent correctly."""
    # Create dock
    dock = FileListDock(parent=None)
    qtbot.addWidget(dock)
    
    # Validate table_manager has parent
    assert dock.table_manager.parent() is not None
    assert dock.table_manager.parent() == dock


def test_can_find_main_window_with_parent_chain(qtbot):
    """Test that _get_main_window() can find main window through parent chain."""
    # Create mock main window
    main_window = MockMainWindow()
    qtbot.addWidget(main_window)
    
    # Create dock with main_window as parent
    dock = FileExplorerDock(parent=main_window)
    
    # Add dock to main window (simulate real usage)
    main_window.addDockWidget(1, dock)  # Qt.LeftDockWidgetArea = 1
    
    # Test _get_main_window() method
    found_window = dock.table_manager._get_main_window()
    
    assert found_window is not None
    assert found_window == main_window
    assert hasattr(found_window, 'dock_editor')


def test_parent_chain_traversal(qtbot):
    """Test complete parent chain traversal."""
    # Create hierarchy
    main_window = MockMainWindow()
    qtbot.addWidget(main_window)
    dock = FileExplorerDock(parent=main_window)
    main_window.addDockWidget(1, dock)
    
    # Traverse parent chain manually
    widget = dock.table_manager
    chain = []
    
    while widget is not None:
        chain.append(type(widget).__name__)
        if hasattr(widget, 'dock_editor'):
            break
        widget = widget.parent()
    
    assert len(chain) >= 2
    assert chain[0] == "FileListTableManager"
    assert "MockMainWindow" in chain


def test_error_message_before_fix_simulation(qtbot):
    """Simulate the error condition that would occur without parent."""
    # Create table_manager WITHOUT parent (old buggy behavior)
    from src.gui.widgets.file_list_table_manager import FileListTableManager
    table_manager_no_parent = FileListTableManager(parent=None)
    qtbot.addWidget(table_manager_no_parent)
    
    # Try to find main window
    found = table_manager_no_parent._get_main_window()
    
    # Should return None because no parent chain
    assert found is None
