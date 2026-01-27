"""
Unit Tests for Phase 4: Advanced Conditions Logic Operator (v2.9.116)
=======================================================================

Tests the integration of logic_operator (AND/OR) with File Explorer's
browse and search modes.

Focus: Verify that logic_operator parameter is accepted and passed correctly.

Author: Programmer #8 (Josué Amaral)
Date: 2026-01-22
Protocol: Simplicity Protocol 3 v4.5
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.core.file_explorer_executor import UnifiedFileExplorerExecutor


class TestLogicOperatorIntegration:
    """Test logic_operator parameter in executor methods."""

    def setup_method(self):
        """Create test directory with sample files."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files with different properties
        self.small_py_file = Path(self.test_dir) / "small.py"
        self.small_py_file.write_text("# Small Python file\nprint('hello')")
        
        self.large_py_file = Path(self.test_dir) / "large.py"
        self.large_py_file.write_text("# Large Python file\n" + "x" * 2000)
        
        self.small_txt_file = Path(self.test_dir) / "small.txt"
        self.small_txt_file.write_text("Small text file")
        
        self.large_txt_file = Path(self.test_dir) / "large.txt"
        self.large_txt_file.write_text("Large text file\n" + "y" * 2000)
        
        self.executor = UnifiedFileExplorerExecutor()

    def teardown_method(self):
        """Clean up test directory."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_browse_accepts_logic_operator_parameter(self):
        """Test that execute_browse accepts logic_operator parameter without error."""
        conditions = []
        
        # Should not raise exception
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions,
            logic_operator="AND"
        )
        
        assert "files" in result
        assert "stats" in result
        assert len(result["files"]) == 4  # All 4 files

    def test_browse_accepts_or_logic_operator(self):
        """Test that execute_browse accepts OR logic_operator."""
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=[],
            logic_operator="OR"
        )
        
        assert "files" in result
        assert len(result["files"]) == 4

    def test_search_accepts_logic_operator_parameter(self):
        """Test that execute_search accepts logic_operator parameter without error."""
        conditions = []
        
        # Should not raise exception
        result = self.executor.execute_search(
            directory=self.test_dir,
            filename_pattern="*",
            content_query="",
            search_options={},
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions,
            logic_operator="AND"
        )
        
        assert "files" in result
        assert "stats" in result

    def test_search_accepts_or_logic_operator(self):
        """Test that execute_search accepts OR logic_operator."""
        result = self.executor.execute_search(
            directory=self.test_dir,
            filename_pattern="*",
            content_query="",
            search_options={},
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=[],
            logic_operator="OR"
        )
        
        assert "files" in result

    def test_size_condition_with_and_logic(self):
        """Test that size-based conditions work with AND logic."""
        conditions = [
            {
                "field": "size",
                "operator": ">",
                "value": "1000",
                "scope_type": "none",
                "scope_value": "",
                "case_sensitive": True,
                "whole_word": False,
                "regex": False,
            }
        ]
        
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions,
            logic_operator="AND"
        )
        
        files = result["files"]
        # Should match large.py and large.txt (both > 1000 bytes)
        assert len(files) == 2
        file_names = [f.file_info.name for f in files]
        assert "large.py" in file_names
        assert "large.txt" in file_names

    def test_size_condition_with_or_logic(self):
        """Test that size-based conditions work with OR logic."""
        conditions = [
            {
                "field": "size",
                "operator": ">",
                "value": "1000",
                "scope_type": "none",
                "scope_value": "",
                "case_sensitive": True,
                "whole_word": False,
                "regex": False,
            }
        ]
        
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions,
            logic_operator="OR"
        )
        
        files = result["files"]
        # Should still match large.py and large.txt
        assert len(files) == 2

    def test_browse_defaults_to_and_when_omitted(self):
        """Test that browse defaults to AND when logic_operator is not provided."""
        conditions = [
            {
                "field": "size",
                "operator": ">",
                "value": "1000",
                "scope_type": "none",
                "scope_value": "",
                "case_sensitive": True,
                "whole_word": False,
                "regex": False,
            }
        ]
        
        # Call without logic_operator (should default to AND)
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions
        )
        
        assert "files" in result
        assert len(result["files"]) == 2  # Same as AND logic

    def test_search_defaults_to_and_when_omitted(self):
        """Test that search defaults to AND when logic_operator is not provided."""
        conditions = [
            {
                "field": "size",
                "operator": ">",
                "value": "1000",
                "scope_type": "none",
                "scope_value": "",
                "case_sensitive": True,
                "whole_word": False,
                "regex": False,
            }
        ]
        
        # Call without logic_operator (should default to AND)
        result = self.executor.execute_search(
            directory=self.test_dir,
            filename_pattern="*",
            content_query="",
            search_options={},
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions
        )
        
        assert "files" in result
        assert len(result["files"]) == 2

    def test_empty_conditions_with_logic_operator(self):
        """Test that empty conditions work regardless of logic_operator."""
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=[],
            logic_operator="OR"
        )
        
        # Should return all 4 files
        files = result["files"]
        assert len(files) == 4

    def test_none_conditions_with_logic_operator(self):
        """Test that None conditions work regardless of logic_operator."""
        result = self.executor.execute_browse(
            directory=self.test_dir,
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=None,
            logic_operator="AND"
        )
        
        # Should return all 4 files
        files = result["files"]
        assert len(files) == 4

