#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest-qt fixtures for GUI testing.

Provides QApplication, monkeypatched dialogs, and test utilities.
"""
import pytest
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PySide6.QtCore import QCoreApplication, QEvent, Qt
import sys


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Don't quit - session fixture persists


@pytest.fixture
def mock_message_box(monkeypatch):
    """Mock QMessageBox to avoid blocking dialogs during tests."""
    responses = []
    
    def mock_information(*args, **kwargs):
        responses.append(("information", args, kwargs))
        return QMessageBox.Ok
    
    def mock_warning(*args, **kwargs):
        responses.append(("warning", args, kwargs))
        return QMessageBox.Ok
    
    def mock_critical(*args, **kwargs):
        responses.append(("critical", args, kwargs))
        return QMessageBox.Ok
    
    def mock_question(*args, **kwargs):
        responses.append(("question", args, kwargs))
        return QMessageBox.Yes
    
    monkeypatch.setattr(QMessageBox, "information", mock_information)
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)
    monkeypatch.setattr(QMessageBox, "critical", mock_critical)
    monkeypatch.setattr(QMessageBox, "question", mock_question)
    
    yield responses


@pytest.fixture
def mock_file_dialog(monkeypatch):
    """Mock QFileDialog to avoid file selection dialogs during tests."""
    responses = {"files": [], "directory": None, "save": None}
    
    def mock_get_open_file_names(*args, **kwargs):
        return responses["files"], ""
    
    def mock_get_existing_directory(*args, **kwargs):
        return responses["directory"] or ""
    
    def mock_get_save_file_name(*args, **kwargs):
        return responses["save"] or "", ""
    
    monkeypatch.setattr(QFileDialog, "getOpenFileNames", mock_get_open_file_names)
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", mock_get_existing_directory)
    monkeypatch.setattr(QFileDialog, "getSaveFileName", mock_get_save_file_name)
    
    yield responses


@pytest.fixture
def temp_json_file(tmp_path):
    """Create temporary JSON file for testing."""
    test_file = tmp_path / "test.json"
    test_data = {
        "name": "Test User",
        "age": 30,
        "active": True,
        "items": ["item1", "item2", "item3"]
    }
    test_file.write_text(json.dumps(test_data, indent=2))
    return test_file


@pytest.fixture
def temp_text_file(tmp_path):
    """Create temporary text file for testing."""
    test_file = tmp_path / "test.txt"
    content = """Line 1: Hello World
Line 2: Testing Search
Line 3: Replace This
Line 4: More Content
Line 5: Final Line"""
    test_file.write_text(content)
    return test_file


@pytest.fixture
def sample_search_results():
    """Provide sample search results structure."""
    return [
        {
            "file": "/path/to/file1.py",
            "line": 10,
            "column": 5,
            "text": "def search_function():",
            "match": "search"
        },
        {
            "file": "/path/to/file2.py",
            "line": 25,
            "column": 12,
            "text": "    result = search_in_text(query)",
            "match": "search"
        },
        {
            "file": "/path/to/file3.py",
            "line": 42,
            "column": 8,
            "text": "# Search implementation",
            "match": "Search"
        }
    ]


@pytest.fixture
def main_window(qapp, mock_message_box, mock_file_dialog, monkeypatch):
    """Create MainWindow instance for testing.
    
    CRITICAL: Uses mock_message_box to prevent blocking QMessageBox dialogs
    during window.close() cleanup (closeEvent confirmation).
    """
    from src.app import MainWindow

    # Startup update checks use the network and must not outlive a GUI test.
    monkeypatch.setattr(MainWindow, "_auto_check_for_updates", lambda self: None)
    # Fresh settings enable a custom exit dialog using exec(), not question().
    monkeypatch.setattr(QMessageBox, "exec", lambda self: QMessageBox.Yes)
    window = MainWindow(qapp)
    yield window
    window.close()  # Safe now - QMessageBox.question returns QMessageBox.Yes automatically
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()


import json
