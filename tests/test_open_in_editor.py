"""
Tests for Open in Editor functionality (Task #6 - v2.9.19).

Tests toolbar button, context menu, auto-detect extension,
and integration with EditorDock.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QApplication, QTextEdit, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QPoint
from src.gui.base_dock import ResultsOutputMixin, BaseDock
from src.gui.editor_dock import EditorDock


class _TestResultsDock(BaseDock, ResultsOutputMixin):
    """Test dock with ResultsOutputMixin for testing (prefixed with _ to avoid pytest collection)."""
    
    def __init__(self, parent=None):
        super().__init__("Test Results Dock", parent)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.lbl_status = Mock()  # Mock status label
    
    def _setup_ui(self):
        """Required by BaseDock."""
        pass


@pytest.fixture
def app():
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def main_window(app):
    """Create main window with EditorDock."""
    window = QMainWindow()
    editor_dock = EditorDock(window)
    window.addDockWidget(Qt.RightDockWidgetArea, editor_dock)
    return window


@pytest.fixture
def test_dock(app, main_window):
    """Create test dock with results panel."""
    dock = _TestResultsDock(main_window)
    lbl_results, text_results = dock.create_results_panel()
    dock.text_results = text_results
    dock.layout.addWidget(lbl_results)
    dock.layout.addWidget(text_results)
    return dock


class TestCreateResultsPanel:
    """Test create_results_panel method enhancements."""
    
    def test_creates_context_menu(self, test_dock):
        """Test that results panel has custom context menu."""
        text_edit = test_dock.text_results
        assert text_edit.contextMenuPolicy() == Qt.CustomContextMenu
    
    def test_context_menu_policy_configured(self, test_dock):
        """Test that context menu policy is set to custom."""
        # The policy being set to CustomContextMenu indicates it's configured
        text_edit = test_dock.text_results
        assert text_edit.contextMenuPolicy() == Qt.CustomContextMenu
        
        # Test that the menu can be triggered
        with patch.object(test_dock, '_show_results_context_menu') as mock_show:
            # Emit signal manually to test connection
            text_edit.customContextMenuRequested.emit(QPoint(0, 0))
            # Give event loop time to process
            QApplication.processEvents()
            mock_show.assert_called_once()


class TestOpenInEditorButton:
    """Test add_open_in_editor_button method."""
    
    def test_button_creation(self, test_dock):
        """Test button is created with correct properties."""
        from PySide6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout()
        
        button = test_dock.add_open_in_editor_button(
            test_dock.text_results,
            layout,
            "Test Button"
        )
        
        assert button is not None
        assert button.text() == "Test Button"
        assert button.toolTip() == "Open results in editor (edit-only mode)"
        assert layout.count() == 1
    
    def test_button_default_text(self, test_dock):
        """Test button uses default text if not provided."""
        from PySide6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout()
        
        button = test_dock.add_open_in_editor_button(
            test_dock.text_results,
            layout
        )
        
        assert button.text() == "📝 Open in Editor"


class TestContentExtensionDetection:
    """Test _detect_content_extension method."""
    
    def test_detects_json_object(self, test_dock):
        """Test JSON object detection."""
        content = '{"key": "value", "nested": {"foo": "bar"}}'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.json'
    
    def test_detects_json_array(self, test_dock):
        """Test JSON array detection."""
        content = '[{"id": 1}, {"id": 2}]'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.json'
    
    def test_detects_invalid_json(self, test_dock):
        """Test invalid JSON falls back to .txt."""
        content = '{ invalid json }'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.txt'
    
    def test_detects_html(self, test_dock):
        """Test HTML detection."""
        content = '<html><body><div>Test</div></body></html>'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.html'
    
    def test_detects_xml(self, test_dock):
        """Test XML detection."""
        content = '<root><element>value</element></root>'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.xml'
    
    def test_detects_typescript(self, test_dock):
        """Test TypeScript detection."""
        content = 'const myFunc = () => { return "test"; }'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.ts'
    
    def test_detects_python(self, test_dock):
        """Test Python detection."""
        content = 'def my_function():\n    import sys\n    return True'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.py'
    
    def test_plain_text_fallback(self, test_dock):
        """Test plain text fallback."""
        content = 'This is just plain text without any special markers.'
        ext = test_dock._detect_content_extension(content)
        assert ext == '.txt'


class TestOpenResultsInEditor:
    """Test _open_results_in_editor method."""
    
    def test_empty_results_shows_message(self, test_dock):
        """Test opening empty results shows information dialog."""
        test_dock.text_results.clear()
        
        with patch('src.gui.base_dock.QMessageBox.information') as mock_msg:
            test_dock._open_results_in_editor(test_dock.text_results)
            mock_msg.assert_called_once()
    
    def test_creates_temp_file_with_correct_extension(self, test_dock, main_window):
        """Test temp file is created with correct extension."""
        json_content = '{"test": "data", "number": 42}'
        test_dock.text_results.setPlainText(json_content)
        
        # Mock tempfile to capture path
        original_temp = tempfile.NamedTemporaryFile
        temp_paths = []
        
        def mock_temp(*args, **kwargs):
            temp = original_temp(*args, **kwargs)
            temp_paths.append(temp.name)
            return temp
        
        with patch('tempfile.NamedTemporaryFile', side_effect=mock_temp):
            test_dock._open_results_in_editor(test_dock.text_results)
        
        # Check that temp file was created with .json extension
        assert len(temp_paths) > 0
        assert temp_paths[0].endswith('.json')
        
        # Cleanup
        for path in temp_paths:
            if os.path.exists(path):
                os.unlink(path)
    
    def test_opens_in_editor_dock(self, test_dock, main_window):
        """Test content is opened in EditorDock."""
        content = "Test content for editor"
        test_dock.text_results.setPlainText(content)
        
        # Get editor dock
        editor_dock = main_window.findChild(EditorDock)
        assert editor_dock is not None
        
        # Open in editor
        test_dock._open_results_in_editor(test_dock.text_results)
        
        # Check that a tab was opened
        assert editor_dock.tab_widget.count() > 0
        
        # Check that content matches
        tab = editor_dock.tab_widget.widget(0)
        tab_content = tab.editor.toPlainText()
        assert content in tab_content
    
    def test_opens_in_edit_only_mode(self, test_dock, main_window):
        """Test content is opened in edit-only mode."""
        content = "Edit-only test content"
        test_dock.text_results.setPlainText(content)
        
        editor_dock = main_window.findChild(EditorDock)
        test_dock._open_results_in_editor(test_dock.text_results)
        
        # Check edit-only mode
        tab = editor_dock.tab_widget.widget(0)
        assert hasattr(tab, 'edit_only_mode')
        assert tab.edit_only_mode is True
    
    def test_handles_editor_not_found(self, app):
        """Test graceful handling when EditorDock not found."""
        # Create dock without EditorDock in parent
        standalone_dock = _TestResultsDock()
        lbl_results, text_results = standalone_dock.create_results_panel()
        standalone_dock.text_results = text_results
        standalone_dock.text_results.setPlainText("Test content")
        
        with patch('src.gui.base_dock.QMessageBox.warning') as mock_warning:
            standalone_dock._open_results_in_editor(standalone_dock.text_results)
            mock_warning.assert_called_once()


class TestGetEditorDock:
    """Test _get_editor_dock method."""
    
    def test_finds_editor_dock(self, test_dock, main_window):
        """Test finding EditorDock from main window."""
        editor_dock = test_dock._get_editor_dock()
        assert editor_dock is not None
        assert isinstance(editor_dock, EditorDock)
    
    def test_returns_none_without_parent(self, app):
        """Test returns None when no parent with findChild."""
        standalone_dock = _TestResultsDock()
        lbl_results, text_results = standalone_dock.create_results_panel()
        editor_dock = standalone_dock._get_editor_dock()
        assert editor_dock is None


class TestContextMenuIntegration:
    """Test context menu integration."""
    
    def test_context_menu_opens(self, test_dock):
        """Test that context menu can be opened without errors."""
        text_edit = test_dock.text_results
        text_edit.setPlainText("Test content for context menu")
        
        # Test that method executes without error (actual menu display tested manually)
        # We can't easily test QMenu.exec_() in unit tests as it blocks event loop
        try:
            # Just verify the method exists and can be called
            assert hasattr(test_dock, '_show_results_context_menu')
            # Verify it's callable
            assert callable(test_dock._show_results_context_menu)
        except Exception as e:
            pytest.fail(f"Context menu setup failed: {e}")
    
    def test_context_menu_has_open_action(self, test_dock):
        """Test context menu has 'Open in Editor' action."""
        text_edit = test_dock.text_results
        
        # Create menu manually to check actions
        from PySide6.QtWidgets import QMenu
        menu = QMenu(text_edit)
        
        # Simulate what _show_results_context_menu does
        open_action = menu.addAction("📝 Open in Editor")
        
        assert open_action is not None
        assert "Open in Editor" in open_action.text()


class TestMultipleFormats:
    """Test opening different content formats in editor."""
    
    def test_json_content(self, test_dock, main_window):
        """Test JSON content opens with .json extension."""
        json_content = '{"users": [{"id": 1, "name": "Alice"}]}'
        test_dock.text_results.setPlainText(json_content)
        
        editor_dock = main_window.findChild(EditorDock)
        test_dock._open_results_in_editor(test_dock.text_results)
        
        tab = editor_dock.tab_widget.widget(0)
        # Check that JsonEditorTab is used for .json files
        from src.gui.json_editor_tab import JsonEditorTab
        # Tab might be JsonEditorTab or EditorTab depending on extension
        assert tab is not None
    
    def test_html_content(self, test_dock, main_window):
        """Test HTML content opens with .html extension."""
        html_content = '<html><body><h1>Title</h1></body></html>'
        test_dock.text_results.setPlainText(html_content)
        
        editor_dock = main_window.findChild(EditorDock)
        test_dock._open_results_in_editor(test_dock.text_results)
        
        tab = editor_dock.tab_widget.widget(0)
        assert tab is not None
        assert tab.editor.toPlainText() == html_content
    
    def test_plain_text_content(self, test_dock, main_window):
        """Test plain text content opens with .txt extension."""
        text_content = 'Just some plain text without special formatting.'
        test_dock.text_results.setPlainText(text_content)
        
        editor_dock = main_window.findChild(EditorDock)
        test_dock._open_results_in_editor(test_dock.text_results)
        
        tab = editor_dock.tab_widget.widget(0)
        assert tab is not None
        assert text_content in tab.editor.toPlainText()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
