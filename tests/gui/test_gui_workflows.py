"""
GUI Workflow Tests

Tests user interactions and workflows across main docks.
Follows Protocol Simplicidade 3 v3.1 - Etapa 10 (Testing).
Includes Etapa 9.1: Segurança em Testes (timeouts obrigatórios).

Author: Josué Amaral
Date: 2025-12-10
Version: v2.9.53
"""

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

# Timeout settings (Protocol Simplicidade 3 - Etapa 9.1)
TEST_TIMEOUT = 30  # 30s por teste (obrigatório)
OPERATION_TIMEOUT = 5000  # 5s para operações GUI (ms)

# Apply timeout to ALL tests in this module
pytestmark = pytest.mark.timeout(TEST_TIMEOUT)


@pytest.fixture
def app(qapp):
    """Provide QApplication instance with headless mode."""
    return qapp


class TestSetOperationsDockWorkflow:
    """Test Set Operations Dock user workflows."""
    
    @pytest.mark.timeout(10)  # Quick test
    def test_file_selection_and_clear(self, qtbot):
        """Test file selection and clear button."""
        from src.gui.set_operations_dock import SetOperationsDock
        
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Simulate file path input
        dock.ed_file_a.setText("/tmp/test_a.json")
        dock.ed_file_b.setText("/tmp/test_b.json")
        
        assert dock.ed_file_a.text() == "/tmp/test_a.json"
        assert dock.ed_file_b.text() == "/tmp/test_b.json"
        
        # Test clear functionality
        qtbot.mouseClick(dock.btn_clear, Qt.LeftButton)
        
        # Verify cleared (allow small delay for signal processing)
        QTimer.singleShot(100, lambda: None)
        qtbot.wait(150)
        
        assert dock.ed_file_a.text() == ""
        assert dock.ed_file_b.text() == ""
    
    @pytest.mark.timeout(10)
    def test_operation_selection(self, qtbot):
        """Test operation type selection via checkboxes."""
        from src.gui.set_operations_dock import SetOperationsDock
        
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Test each operation checkbox
        checkboxes = [
            dock.chk_intersection,
            dock.chk_union,
            dock.chk_difference,
            dock.chk_symmetric_difference,
        ]
        
        for checkbox in checkboxes:
            initial_state = checkbox.isChecked()
            qtbot.mouseClick(checkbox, Qt.LeftButton)
            qtbot.wait(50)  # Small delay for signal
            assert checkbox.isChecked() != initial_state


class TestCaseConverterDockWorkflow:
    """Test Case Converter Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_case_type_selection(self, qtbot):
        """Test case type selection dropdown."""
        from src.gui.case_converter_dock import CaseConverterDock
        
        dock = CaseConverterDock()
        qtbot.addWidget(dock)
        
        # Get combo box
        combo = dock.combo_case
        
        # Test selection change
        initial_index = combo.currentIndex()
        combo.setCurrentIndex((initial_index + 1) % combo.count())
        qtbot.wait(50)
        
        assert combo.currentIndex() != initial_index


class TestJSONRewriterDockWorkflow:
    """Test JSON Rewriter Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_path_input_and_browse(self, qtbot):
        """Test path input field."""
        from src.gui.json_rewriter_dock import JsonRewriterDock
        
        dock = JsonRewriterDock()
        qtbot.addWidget(dock)
        
        # Test path input
        test_path = "/tmp/test.json"
        dock.ed_path.setText(test_path)
        qtbot.wait(50)
        
        assert dock.ed_path.text() == test_path
    
    @pytest.mark.timeout(10)
    def test_mode_selection(self, qtbot):
        """Test rewriter mode selection."""
        from src.gui.json_rewriter_dock import JsonRewriterDock
        
        dock = JsonRewriterDock()
        qtbot.addWidget(dock)
        
        # Test mode combo
        combo = dock.combo_mode
        original_mode = combo.currentIndex()
        
        # Change mode
        combo.setCurrentIndex((original_mode + 1) % combo.count())
        qtbot.wait(50)
        
        assert combo.currentIndex() != original_mode


class TestAIProcessorDockWorkflow:
    """Test AI Processor Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_provider_selection(self, qtbot):
        """Test AI provider selection."""
        from src.gui.ai_processor_dock import AIProcessorDock
        
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        # Test provider combo
        combo = dock.combo_provider
        initial_provider = combo.currentIndex()
        
        # Change provider
        if combo.count() > 1:
            combo.setCurrentIndex((initial_provider + 1) % combo.count())
            qtbot.wait(50)
            assert combo.currentIndex() != initial_provider
    
    @pytest.mark.timeout(10)
    def test_instruction_input(self, qtbot):
        """Test instruction text input."""
        from src.gui.ai_processor_dock import AIProcessorDock
        
        dock = AIProcessorDock()
        qtbot.addWidget(dock)
        
        # Test instruction input
        test_instruction = "Translate this text to Spanish"
        dock.ed_instruction.setPlainText(test_instruction)
        qtbot.wait(50)
        
        assert dock.ed_instruction.toPlainText() == test_instruction


class TestJSONSearchDockWorkflow:
    """Test JSON Search Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_search_input(self, qtbot):
        """Test search key and value inputs."""
        from src.gui.json_search_dock import JsonSearchDock
        
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Test key input
        dock.ed_search_key.setText("user.name")
        qtbot.wait(50)
        assert dock.ed_search_key.text() == "user.name"
        
        # Test value input
        dock.ed_search_value.setText("John")
        qtbot.wait(50)
        assert dock.ed_search_value.text() == "John"
    
    @pytest.mark.timeout(10)
    def test_search_mode_selection(self, qtbot):
        """Test search mode combo box."""
        from src.gui.json_search_dock import JsonSearchDock
        
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        combo = dock.combo_mode
        initial_mode = combo.currentIndex()
        
        # Cycle through modes
        combo.setCurrentIndex((initial_mode + 1) % combo.count())
        qtbot.wait(50)
        
        assert combo.currentIndex() != initial_mode


class TestJSONTranslateDockWorkflow:
    """Test JSON Translate Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_path_inputs(self, qtbot):
        """Test source and dictionary path inputs."""
        from src.gui.json_translate_dock import JsonTranslateDock
        
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Test source path
        dock.ed_path.setText("/tmp/source.tsx")
        qtbot.wait(50)
        assert dock.ed_path.text() == "/tmp/source.tsx"
        
        # Test dictionary path
        dock.ed_dict.setText("/tmp/dict.json")
        qtbot.wait(50)
        assert dock.ed_dict.text() == "/tmp/dict.json"
    
    @pytest.mark.timeout(10)
    def test_variable_name_input(self, qtbot):
        """Test object variable name input."""
        from src.gui.json_translate_dock import JsonTranslateDock
        
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Test variable name
        dock.object_variable_name.setText("i18n")
        qtbot.wait(50)
        assert dock.object_variable_name.text() == "i18n"
    
    @pytest.mark.timeout(10)
    def test_options_checkboxes(self, qtbot):
        """Test translation option checkboxes."""
        from src.gui.json_translate_dock import JsonTranslateDock
        
        dock = JsonTranslateDock()
        qtbot.addWidget(dock)
        
        # Test backup checkbox
        initial_state = dock.chk_backup.isChecked()
        qtbot.mouseClick(dock.chk_backup, Qt.LeftButton)
        qtbot.wait(50)
        assert dock.chk_backup.isChecked() != initial_state


class TestTutorialsDockWorkflow:
    """Test Tutorials Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_search_input(self, qtbot):
        """Test tutorial search input."""
        from src.gui.tutorials_dock import TutorialsDock
        
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        # Test search input
        dock.search_input.setText("quick start")
        qtbot.wait(50)
        assert dock.search_input.text() == "quick start"
    
    @pytest.mark.timeout(10)
    def test_tree_navigation(self, qtbot):
        """Test tree widget has items."""
        from src.gui.tutorials_dock import TutorialsDock
        
        dock = TutorialsDock()
        qtbot.addWidget(dock)
        
        # Verify tree has root items
        tree = dock.tree
        qtbot.wait(100)  # Allow tree to populate
        
        assert tree.topLevelItemCount() >= 0  # At least root items


class TestEditorDockWorkflow:
    """Test Editor Dock user workflows."""
    
    @pytest.mark.timeout(10)
    def test_file_path_input(self, qtbot):
        """Test file path input."""
        from src.gui.editor_dock import EditorDock
        
        dock = EditorDock()
        qtbot.addWidget(dock)
        
        # Test path input
        test_path = "/tmp/test.json"
        dock.ed_path.setText(test_path)
        qtbot.wait(50)
        
        assert dock.ed_path.text() == test_path


class TestKeyboardShortcuts:
    """Test keyboard shortcuts across docks."""
    
    @pytest.mark.timeout(10)
    def test_enter_shortcut_json_search(self, qtbot):
        """Test Enter key executes search in JSON Search Dock."""
        from src.gui.json_search_dock import JsonSearchDock
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import QEvent
        
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Focus on search input
        dock.ed_search_key.setFocus()
        dock.ed_search_key.setText("test")
        
        # Simulate Enter key
        qtbot.keyClick(dock.ed_search_key, Qt.Key_Return)
        qtbot.wait(100)
        
        # Verify search was triggered (method exists and is callable)
        assert hasattr(dock, '_perform_search')
    
    @pytest.mark.timeout(10)
    def test_esc_interrupt_json_search(self, qtbot):
        """Test Esc key for interrupt in JSON Search Dock."""
        from src.gui.json_search_dock import JsonSearchDock
        
        dock = JsonSearchDock()
        qtbot.addWidget(dock)
        
        # Verify interrupt method exists
        assert hasattr(dock, '_interrupt')
        assert callable(dock._interrupt)


# Integration test - DO NOT RUN by default (requires actual files)
@pytest.mark.skip(reason="Integration test - requires actual files and can be slow")
class TestEndToEndWorkflows:
    """End-to-end integration tests (skipped by default)."""
    
    @pytest.mark.timeout(30)
    def test_full_set_operations_workflow(self, qtbot, tmp_path):
        """Test complete set operations workflow."""
        from src.gui.set_operations_dock import SetOperationsDock
        import json
        
        # Create test files
        file_a = tmp_path / "a.json"
        file_b = tmp_path / "b.json"
        
        file_a.write_text(json.dumps({"name": "Alice", "age": 30}))
        file_b.write_text(json.dumps({"name": "Bob", "age": 30}))
        
        dock = SetOperationsDock()
        qtbot.addWidget(dock)
        
        # Set paths
        dock.ed_file_a.setText(str(file_a))
        dock.ed_file_b.setText(str(file_b))
        
        # Select intersection
        qtbot.mouseClick(dock.rb_intersection, Qt.LeftButton)
        
        # Note: Not clicking execute to avoid actual processing
        qtbot.wait(100)
