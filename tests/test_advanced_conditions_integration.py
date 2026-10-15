"""
Tests for Advanced Conditions Integration (Sprint B Feature #1)
================================================================

Tests for:
- src/utils/advanced_conditions.py (shared module)
- Integration with json_rewriter_dock.py
- Auto-detection of JSON files
- QSettings persistence

Test Coverage:
- TestModuleExtraction: Test shared module functions
- TestAutoDetectExtension: Test JSON auto-detection logic
- TestJSONRewriterIntegration: Test GUI integration (mock-based)
- TestIntegration: Integration tests with real Task #51 components
"""

# pylint: disable=no-name-in-module  # Qt exposes dynamic bindings.

import pytest

# Integration tests require longer timeout (60s max)
pytestmark = pytest.mark.timeout(60)
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtWidgets import QComboBox, QLineEdit, QCheckBox
from src.core.filters import Condition
from src.utils.advanced_conditions import get_conditions_from_ui, apply_conditions_to_files


class TestModuleExtraction:
    """Test shared module functions (get_conditions_from_ui, apply_conditions_to_files)."""
    
    def test_get_conditions_from_ui_valid(self):
        """Test extracting valid conditions from UI rows."""
        # Create mock widgets
        combo_field = Mock()
        combo_field.currentText.return_value = "filename"
        
        combo_op = Mock()
        combo_op.currentText.return_value = "contains"
        
        ed_value = Mock()
        ed_value.text.return_value = "test.json"
        
        combo_scope = Mock()
        combo_scope.currentText.return_value = "none"
        
        chk_case = Mock()
        chk_case.isChecked.return_value = True
        
        chk_regex = Mock()
        chk_regex.isChecked.return_value = False
        
        cond_rows = [(combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex)]
        
        # Execute
        conditions = get_conditions_from_ui(cond_rows)
        
        # Verify
        assert len(conditions) == 1
        assert conditions[0].field == "filename"
        assert conditions[0].operator == "contains"
        assert conditions[0].value == "test.json"
        assert conditions[0].case_sensitive is True
        assert conditions[0].use_regex is False
    
    def test_get_conditions_from_ui_empty_rows(self):
        """Test that empty rows are skipped."""
        # Create mock widgets with empty field
        combo_field = Mock()
        combo_field.currentText.return_value = ""  # Empty field
        
        combo_op = Mock()
        combo_op.currentText.return_value = "contains"
        
        ed_value = Mock()
        ed_value.text.return_value = "test"
        
        combo_scope = Mock()
        combo_scope.currentText.return_value = "none"
        
        chk_case = Mock()
        chk_case.isChecked.return_value = True
        
        chk_regex = Mock()
        chk_regex.isChecked.return_value = False
        
        cond_rows = [(combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex)]
        
        # Execute
        conditions = get_conditions_from_ui(cond_rows)
        
        # Verify - empty rows skipped
        assert len(conditions) == 0
    
    def test_apply_conditions_to_files_enabled(self):
        """Test applying conditions when enabled."""
        # Create test files
        with tempfile.TemporaryDirectory() as tmpdir:
            test_json = Path(tmpdir) / "test.json"
            test_txt = Path(tmpdir) / "test.txt"
            test_json.write_text("{}")
            test_txt.write_text("text")
            
            files = [str(test_json), str(test_txt)]
            
            # Create condition: filename contains "json"
            conditions = [
                Condition(
                    field="filename",
                    operator="contains",
                    value="json",
                    case_sensitive=False
                )
            ]
            
            # Execute
            filtered, count = apply_conditions_to_files(files, conditions, "AND", enabled=True)
            
            # Verify
            assert len(filtered) == 1
            assert str(test_json) in filtered
            assert count == 1  # 1 file filtered out
    
    def test_apply_conditions_to_files_disabled(self):
        """Test that filtering is skipped when disabled."""
        files = ["file1.json", "file2.txt"]
        conditions = [Condition(field="ext", operator="equals", value=".json")]
        
        # Execute with enabled=False
        filtered, count = apply_conditions_to_files(files, conditions, "AND", enabled=False)
        
        # Verify - all files returned unchanged
        assert len(filtered) == 2
        assert count == 0
    
    def test_apply_conditions_no_conditions(self):
        """Test that empty conditions list returns all files."""
        files = ["file1.json", "file2.txt"]
        conditions = []
        
        # Execute
        filtered, count = apply_conditions_to_files(files, conditions, "AND", enabled=True)
        
        # Verify - all files returned
        assert len(filtered) == 2
        assert count == 0


class TestAutoDetectExtension:
    """Test JSON file auto-detection logic."""
    
    def test_auto_detect_json_files(self):
        """Test that .json files are detected automatically."""
        json_files = ["test.json", "data.JSON", "config.json"]
        non_json_files = ["test.txt", "script.py", "index.html"]
        
        for file in json_files:
            assert file.endswith(('.json', '.JSON')), f"{file} should be detected as JSON"
        
        for file in non_json_files:
            assert not file.endswith(('.json', '.JSON')), f"{file} should NOT be detected as JSON"
    
    def test_auto_detect_fallback_to_checkbox(self):
        """Test fallback when apply_all_types checkbox is enabled."""
        # When apply_all_types=True, all files should be processed
        # This is tested in integration tests below
        pass


class TestJSONRewriterIntegration:
    """Test JSON Rewriter integration (mock-based)."""
    
    @patch("src.gui.json_rewriter_dock.QMessageBox.information")
    @patch("src.gui.json_rewriter_dock.QMessageBox.critical")
    @patch("src.gui.json_rewriter_dock.cli_dedupe")
    def test_cli_dedupe_with_filters_applied(
        self, mock_cli_dedupe, mock_critical, _mock_information
    ):
        """Test that cli_dedupe is called with advanced_conditions parameter."""
        from src.gui.json_rewriter_dock import JsonRewriterDock
        from PySide6.QtWidgets import QApplication
        import sys
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create dock
        dock = JsonRewriterDock()
        
        # Set up conditions
        dock.advanced_conditions = [
            Condition(field="filename", operator="contains", value="test")
        ]
        dock.advanced_filters_enabled = True
        dock.chk_apply_all_types.setChecked(False)
        
        # Mock file inputs
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text('{"key": "value"}')
            
            dock.ed_in.setText(str(test_file))
            dock.ed_out.setText(str(test_file))
            
            mock_cli_dedupe.return_value = (
                '{"key": "value"}',
                {},
                {"dedupe": 0},
                {},
            )

            dock._rewrite()

            mock_cli_dedupe.assert_called_once()
            call_args = mock_cli_dedupe.call_args
            assert call_args.kwargs["advanced_conditions"] == dock.advanced_conditions
            assert call_args.kwargs["apply_all_types"] is False
            mock_critical.assert_not_called()
    
    def test_qsettings_persistence(self):
        """Test QSettings persistence for advanced filters."""
        from src.gui.json_rewriter_dock import JsonRewriterDock
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QSettings
        import sys
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create dock
        dock = JsonRewriterDock()
        
        # Set up conditions
        dock.advanced_conditions = [
            Condition(
                field="filename",
                operator="contains",
                value="test",
                case_sensitive=True,
                use_regex=False
            )
        ]
        dock.advanced_filters_enabled = True
        dock.chk_apply_all_types.setChecked(True)
        
        # Save preferences
        dock._save_preferences()
        
        # Create new dock and load preferences
        dock2 = JsonRewriterDock()
        dock2._load_preferences()
        
        # Verify persistence
        assert dock2.advanced_filters_enabled is True
        assert dock2.chk_apply_all_types.isChecked() is True
        assert len(dock2.advanced_conditions) == 1
        assert dock2.advanced_conditions[0].field == "filename"
        assert dock2.advanced_conditions[0].value == "test"


class TestIntegration:
    """Integration tests with real Task #51 components."""
    
    def test_filters_before_remove_duplicates(self):
        """Test that filters are applied BEFORE remove_duplicate_objects()."""
        from src.gui.json_rewriter_dock import cli_dedupe
        import argparse
        
        # Create test JSON file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.json"
            test_file.write_text('{"a": {"x": 1}, "b": {"x": 1}}')  # Contains duplicate object
            
            # Create args
            args = argparse.Namespace(
                input=str(test_file),
                output=str(test_file),
                from_ts=False,
                ts_out=False,
                join_keys=False,
                eliminate_duplicates=False,
                indent=2,
                no_line_break=False,
                exclude_numeric=False,
                skip_empty=False,
                avoid_duplicate_child_keys=False,
                remove_dup_consecutive=False,
                remove_dup_all=False,
                skip_no_siblings=False,
                remove_duplicate_objects=True,
                duplicate_threshold=100,
                include_duplicate_arrays=False,
                duplicate_mode='remove',
                enforce_case=False
            )
            
            # Create filter condition: filename must contain "nonexistent"
            conditions = [
                Condition(field="filename", operator="contains", value="nonexistent")
            ]
            
            # Execute cli_dedupe with filters (file should be filtered out)
            output, sub_map, stats, detailed_stats = cli_dedupe(args, advanced_conditions=conditions, apply_all_types=True)
            
            # Verify - file was filtered out (empty output)
            assert output == ""
            assert stats['advanced_filters_filtered'] == 1
            
            # Now test with passing filter
            conditions2 = [
                Condition(field="filename", operator="contains", value="test")
            ]
            
            output2, sub_map2, stats2, detailed_stats2 = cli_dedupe(args, advanced_conditions=conditions2, apply_all_types=True)
            
            # Verify - file was processed (output not empty)
            assert output2 != ""
            assert stats2['advanced_filters_filtered'] == 0
    
    def test_feedback_message_box(self):
        """Test that feedback includes advanced_filters_filtered stat."""
        from src.gui.json_rewriter_dock import format_removal_statistics
        
        # Test stats with advanced_filters_filtered
        stats = {
            'dedupe': 0,
            'eliminate': 0,
            'numeric_keys': 0,
            'empty_values': 0,
            'duplicate_child': 0,
            'array_duplicates_consecutive': 0,
            'array_duplicates_all': 0,
            'no_siblings': 0,
            'duplicate_objects': 2,
            'advanced_filters_filtered': 1
        }
        
        # Format statistics
        result = format_removal_statistics(stats)
        
        # Verify feedback includes both
        assert "Removed duplicate objects" in result
        assert "Filtered by Advanced Conditions" in result
        assert "2 objects" in result
        assert "1 files" in result
