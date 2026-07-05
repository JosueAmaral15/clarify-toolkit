"""
GUI Safety Tests - Basic Widget Creation (v2.9.53)

Tests SAFE instantiation of docks WITHOUT heavy operations.
Following Protocol Simplicidade 3 - Etapa 9.1: Segurança em Testes.

Author: Josué Amaral
Date: 2025-12-10
"""

import pytest
from PySide6.QtWidgets import QApplication
import sys

# Ensure QApplication exists
if not QApplication.instance():
    app = QApplication(sys.argv)


@pytest.mark.timeout(5)
def test_set_operations_dock_instantiation(qtbot):
    """Test Set Operations Dock can be instantiated safely."""
    from src.gui.set_operations_dock import SetOperationsDock
    
    dock = SetOperationsDock()
    qtbot.addWidget(dock)
    
    # Basic assertions - NO heavy operations
    assert dock.windowTitle() == "JSON Set Operations"
    assert dock.isVisible() is False  # Not shown yet


@pytest.mark.timeout(5)
def test_case_converter_dock_instantiation(qtbot):
    """Test Case Converter Dock can be instantiated safely."""
    from src.gui.case_converter_dock import CaseConverterDock
    
    dock = CaseConverterDock()
    qtbot.addWidget(dock)
    
    assert dock.windowTitle() == "Case Converter"
    assert dock.isVisible() is False


@pytest.mark.timeout(5)
def test_json_search_dock_instantiation(qtbot):
    """Test JSON Search Dock can be instantiated safely."""
    from src.gui.json_search_dock import JsonSearchDock
    
    dock = JsonSearchDock()
    qtbot.addWidget(dock)
    
    assert dock.windowTitle() == "JSON Search"
    assert dock.isVisible() is False


@pytest.mark.timeout(5)
def test_tutorials_dock_instantiation(qtbot):
    """Test Tutorials Dock can be instantiated safely."""
    from src.gui.tutorials_dock import TutorialsDock
    
    dock = TutorialsDock()
    qtbot.addWidget(dock)
    
    assert dock.windowTitle() == "📚 Tutorials"
    assert dock.isVisible() is False


@pytest.mark.timeout(5)
def test_editor_dock_instantiation(qtbot):
    """Test Clarify Editor can be instantiated safely."""
    from src.gui.editor_dock import EditorDock
    
    dock = EditorDock()
    qtbot.addWidget(dock)
    
    assert dock.windowTitle() == "Clarify Editor"
    assert dock.isVisible() is False
