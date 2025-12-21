#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for LayoutManager (v2.9.84)

Test coverage:
- Initialization
- Dock registration
- Save/load layouts
- Presets (Compact, Standard, Advanced)
- Custom layouts management
- Delete and reset operations
"""

import pytest
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PySide6.QtCore import Qt, QSettings

from src.layout_manager import LayoutManager


@pytest.fixture
def app(qtbot):
    """Create QApplication instance."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(qtbot, app):
    """Create a MainWindow with mock docks."""
    window = QMainWindow()
    window.setWindowTitle("Test Window")
    window.resize(800, 600)
    
    # Create mock docks
    dock1 = QDockWidget("Editor", window)
    dock2 = QDockWidget("Search", window)
    dock3 = QDockWidget("Rewriter", window)
    
    # Set object names (required for saveState/restoreState)
    dock1.setObjectName("dock_editor")
    dock2.setObjectName("dock_search")
    dock3.setObjectName("dock_rewriter")
    
    window.addDockWidget(Qt.LeftDockWidgetArea, dock1)
    window.addDockWidget(Qt.RightDockWidgetArea, dock2)
    window.addDockWidget(Qt.BottomDockWidgetArea, dock3)
    
    # Show window to make docks visible
    window.show()
    qtbot.waitForWindowShown(window)
    
    # Store docks for easy access
    window.dock_editor = dock1
    window.dock_search = dock2
    window.dock_rewriter = dock3
    
    qtbot.addWidget(window)
    return window


@pytest.fixture
def layout_manager(main_window):
    """Create LayoutManager instance."""
    manager = LayoutManager(main_window)
    
    # Register docks
    manager.register_dock("editor", main_window.dock_editor)
    manager.register_dock("search", main_window.dock_search)
    manager.register_dock("rewriter", main_window.dock_rewriter)
    
    return manager


@pytest.fixture(autouse=True)
def clean_settings():
    """Clean QSettings before and after each test."""
    settings = QSettings("Clarify", "ClarifyApp")
    settings.remove("Layouts")
    settings.remove("LastLayout")
    settings.sync()
    yield
    settings.remove("Layouts")
    settings.remove("LastLayout")
    settings.sync()


def test_layout_manager_initialization(main_window):
    """Test LayoutManager initialization."""
    manager = LayoutManager(main_window)
    
    assert manager.main_window == main_window
    assert isinstance(manager.settings, QSettings)
    assert len(manager.docks) == 0  # No docks registered yet


def test_register_dock(layout_manager, main_window):
    """Test dock registration."""
    assert "editor" in layout_manager.docks
    assert "search" in layout_manager.docks
    assert "rewriter" in layout_manager.docks
    
    assert layout_manager.docks["editor"] == main_window.dock_editor
    assert layout_manager.docks["search"] == main_window.dock_search
    assert layout_manager.docks["rewriter"] == main_window.dock_rewriter


def test_save_and_load_layout(layout_manager, main_window):
    """Test saving and loading a custom layout."""
    # Save current layout
    layout_manager.save_layout("test_layout")
    
    # Modify window state
    main_window.dock_editor.setVisible(False)
    
    # Load saved layout
    result = layout_manager.load_layout("test_layout")
    
    assert result is True
    # Editor should be visible again after restore
    # (Note: exact state depends on what was saved)


def test_load_nonexistent_layout(layout_manager):
    """Test loading a layout that doesn't exist."""
    result = layout_manager.load_layout("nonexistent_layout")
    
    assert result is False


def test_preset_compact(layout_manager, main_window):
    """Test Compact preset application."""
    layout_manager.apply_preset_compact()
    
    # Compact: only editor visible
    assert main_window.dock_editor.isVisible() is True
    assert main_window.dock_search.isVisible() is False
    assert main_window.dock_rewriter.isVisible() is False


def test_preset_standard(layout_manager, main_window):
    """Test Standard preset application."""
    layout_manager.apply_preset_standard()
    
    # Standard: editor, search, rewriter visible
    assert main_window.dock_editor.isVisible() is True
    assert main_window.dock_search.isVisible() is True
    assert main_window.dock_rewriter.isVisible() is True


def test_preset_advanced(layout_manager, main_window):
    """Test Advanced preset application."""
    # Hide all docks first
    main_window.dock_editor.setVisible(False)
    main_window.dock_search.setVisible(False)
    main_window.dock_rewriter.setVisible(False)
    
    layout_manager.apply_preset_advanced()
    
    # Advanced: all docks visible
    assert main_window.dock_editor.isVisible() is True
    assert main_window.dock_search.isVisible() is True
    assert main_window.dock_rewriter.isVisible() is True


def test_apply_preset_by_name(layout_manager):
    """Test applying presets by name."""
    assert layout_manager.apply_preset(LayoutManager.PRESET_COMPACT) is True
    assert layout_manager.apply_preset(LayoutManager.PRESET_STANDARD) is True
    assert layout_manager.apply_preset(LayoutManager.PRESET_ADVANCED) is True
    assert layout_manager.apply_preset("invalid_preset") is False


def test_restore_last_layout(layout_manager):
    """Test restoring last used layout."""
    # Apply a preset
    layout_manager.apply_preset_standard()
    
    # Create new manager (simulates app restart)
    new_manager = LayoutManager(layout_manager.main_window)
    for dock_name, dock_widget in layout_manager.docks.items():
        new_manager.register_dock(dock_name, dock_widget)
    
    # Restore last layout
    result = new_manager.restore_last_layout()
    
    # Should load Standard preset
    assert result is True


def test_get_saved_layouts(layout_manager):
    """Test getting list of saved layouts."""
    # Initially, no custom layouts
    assert len(layout_manager.get_saved_layouts()) == 0
    
    # Save some custom layouts
    layout_manager.save_layout("custom1")
    layout_manager.save_layout("custom2")
    
    # Apply preset (shouldn't appear in custom list)
    layout_manager.apply_preset_standard()
    
    custom_layouts = layout_manager.get_saved_layouts()
    assert "custom1" in custom_layouts
    assert "custom2" in custom_layouts
    assert LayoutManager.PRESET_STANDARD not in custom_layouts


def test_delete_layout(layout_manager):
    """Test deleting a custom layout."""
    # Save a layout
    layout_manager.save_layout("to_delete")
    assert "to_delete" in layout_manager.get_saved_layouts()
    
    # Delete it
    result = layout_manager.delete_layout("to_delete")
    assert result is True
    assert "to_delete" not in layout_manager.get_saved_layouts()


def test_delete_preset_fails(layout_manager):
    """Test that deleting presets is not allowed."""
    result = layout_manager.delete_layout(LayoutManager.PRESET_COMPACT)
    assert result is False


def test_reset_to_defaults(layout_manager):
    """Test resetting all layouts to defaults."""
    # Create some custom layouts
    layout_manager.save_layout("custom1")
    layout_manager.save_layout("custom2")
    
    assert len(layout_manager.get_saved_layouts()) == 2
    
    # Reset
    layout_manager.reset_to_defaults()
    
    # All custom layouts should be gone
    assert len(layout_manager.get_saved_layouts()) == 0


def test_preset_names_constant(layout_manager):
    """Test that preset names are correctly defined."""
    assert LayoutManager.PRESET_COMPACT == "Compact"
    assert LayoutManager.PRESET_STANDARD == "Standard"
    assert LayoutManager.PRESET_ADVANCED == "Advanced"
    
    assert len(LayoutManager.PRESETS) == 3
    assert LayoutManager.PRESET_COMPACT in LayoutManager.PRESETS
    assert LayoutManager.PRESET_STANDARD in LayoutManager.PRESETS
    assert LayoutManager.PRESET_ADVANCED in LayoutManager.PRESETS
