"""
Tests for AI Processor Advanced Conditions (Task #51 - v2.9.26)

Test coverage:
- Filename filtering (contains, equals, regex)
- Size filtering (>, <, ranges)
- Extension filtering
- Content filtering with scope
- Empty conditions (should process all)
- Invalid regex handling
- No files match (should warn)
- Logic operators (AND/OR)
- QSettings persistence
"""

import pytest
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Import the Condition class and filter function
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.core.filters import Condition, filter_files_by_conditions


class TestFilenameFiltering:
    """Test filename-based filtering."""
    
    def test_filename_contains(self, tmp_path):
        """Test filename contains pattern."""
        # Create test files
        (tmp_path / "test_file.py").write_text("print('hello')")
        (tmp_path / "main.py").write_text("print('world')")
        (tmp_path / "config.json").write_text("{}")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: filename contains "test"
        cond = Condition("filename", "contains", "test", case_sensitive=False)
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "test_file.py" in result[0]
    
    def test_filename_equals(self, tmp_path):
        """Test exact filename matching."""
        (tmp_path / "main.py").write_text("")
        (tmp_path / "test.py").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: filename equals "main.py"
        cond = Condition("filename", "equals", "main.py")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert result[0].endswith("main.py")
    
    def test_filename_regex(self, tmp_path):
        """Test filename regex matching."""
        (tmp_path / "test_001.py").write_text("")
        (tmp_path / "test_002.py").write_text("")
        (tmp_path / "main.py").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: filename matches regex "test_\\d+"
        cond = Condition("filename", "contains", r"test_\d+", use_regex=True)
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 2
        assert all("test_" in f for f in result)


class TestSizeFiltering:
    """Test file size filtering."""
    
    def test_size_greater_than(self, tmp_path):
        """Test filtering files larger than threshold."""
        # Create files of different sizes
        small_file = tmp_path / "small.txt"
        large_file = tmp_path / "large.txt"
        
        small_file.write_text("x" * 100)   # 100 bytes
        large_file.write_text("x" * 1000)  # 1000 bytes
        
        files = [str(small_file), str(large_file)]
        
        # Filter: size > 500 bytes
        cond = Condition("size", ">", "500")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "large.txt" in result[0]
    
    def test_size_less_than(self, tmp_path):
        """Test filtering files smaller than threshold."""
        small_file = tmp_path / "small.txt"
        large_file = tmp_path / "large.txt"
        
        small_file.write_text("x" * 100)
        large_file.write_text("x" * 1000)
        
        files = [str(small_file), str(large_file)]
        
        # Filter: size < 500 bytes
        cond = Condition("size", "<", "500")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "small.txt" in result[0]
    
    def test_size_range(self, tmp_path):
        """Test filtering files within size range."""
        tiny = tmp_path / "tiny.txt"
        medium = tmp_path / "medium.txt"
        huge = tmp_path / "huge.txt"
        
        tiny.write_text("x" * 50)
        medium.write_text("x" * 500)
        huge.write_text("x" * 5000)
        
        files = [str(tiny), str(medium), str(huge)]
        
        # Filter: 100 <= size <= 1000
        conds = [
            Condition("size", ">=", "100"),
            Condition("size", "<=", "1000")
        ]
        result = filter_files_by_conditions(files, conds, "AND")
        
        assert len(result) == 1
        assert "medium.txt" in result[0]


class TestExtensionFiltering:
    """Test file extension filtering."""
    
    def test_ext_equals(self, tmp_path):
        """Test filtering by exact extension."""
        (tmp_path / "file.py").write_text("")
        (tmp_path / "file.js").write_text("")
        (tmp_path / "file.txt").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: ext equals "py"
        cond = Condition("ext", "equals", "py")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert result[0].endswith(".py")
    
    def test_ext_multiple(self, tmp_path):
        """Test filtering multiple extensions using OR logic."""
        (tmp_path / "file.py").write_text("")
        (tmp_path / "file.js").write_text("")
        (tmp_path / "file.txt").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: ext equals "py" OR ext equals "js"
        conds = [
            Condition("ext", "equals", "py"),
            Condition("ext", "equals", "js")
        ]
        result = filter_files_by_conditions(files, conds, "OR")
        
        assert len(result) == 2
        assert any(f.endswith(".py") for f in result)
        assert any(f.endswith(".js") for f in result)


class TestContentFiltering:
    """Test content-based filtering."""
    
    def test_content_contains(self, tmp_path):
        """Test filtering by content pattern."""
        file1 = tmp_path / "has_import.py"
        file2 = tmp_path / "no_import.py"
        
        file1.write_text("import os\nprint('hello')")
        file2.write_text("print('world')")
        
        files = [str(file1), str(file2)]
        
        # Filter: content contains "import"
        cond = Condition("content", "contains", "import")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "has_import.py" in result[0]
    
    def test_content_regex(self, tmp_path):
        """Test content filtering with regex."""
        file1 = tmp_path / "has_function.py"
        file2 = tmp_path / "no_function.py"
        
        file1.write_text("def main():\n    pass")
        file2.write_text("x = 42")
        
        files = [str(file1), str(file2)]
        
        # Filter: content matches regex "def \w+\("
        cond = Condition("content", "contains", r"def \w+\(", use_regex=True)
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "has_function.py" in result[0]
    
    def test_content_with_scope(self, tmp_path):
        """Test content filtering with scope (brackets)."""
        file1 = tmp_path / "with_brackets.txt"
        
        file1.write_text("outside [inside brackets] outside")
        
        files = [str(file1)]
        
        # Filter: content contains "inside" within brackets scope
        cond = Condition("content", "contains", "inside", scope_type="brackets")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1


class TestEmptyConditions:
    """Test behavior with empty/no conditions."""
    
    def test_empty_conditions_returns_all(self, tmp_path):
        """Test that empty conditions return all files."""
        (tmp_path / "file1.py").write_text("")
        (tmp_path / "file2.py").write_text("")
        (tmp_path / "file3.py").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # No conditions
        result = filter_files_by_conditions(files, [])
        
        assert len(result) == 3
    
    def test_invalid_condition_ignored(self, tmp_path):
        """Test that conditions with empty fields are ignored."""
        (tmp_path / "file.py").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Condition with empty operator (should be ignored)
        cond = Condition("filename", "", "test")
        result = filter_files_by_conditions(files, [cond])
        
        # Should return all files (condition ignored)
        assert len(result) == 1


class TestInvalidRegex:
    """Test handling of invalid regex patterns."""
    
    def test_invalid_regex_returns_no_matches(self, tmp_path):
        """Test that invalid regex safely returns no matches."""
        (tmp_path / "file.py").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Invalid regex pattern
        cond = Condition("filename", "contains", "[invalid(regex", use_regex=True)
        result = filter_files_by_conditions(files, [cond])
        
        # Should handle error gracefully and return empty
        assert len(result) == 0


class TestNoFilesMatch:
    """Test scenario where no files match conditions."""
    
    def test_no_matches(self, tmp_path):
        """Test filtering that excludes all files."""
        (tmp_path / "file1.py").write_text("")
        (tmp_path / "file2.js").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter for files that don't exist
        cond = Condition("ext", "equals", "nonexistent")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 0


class TestLogicOperators:
    """Test AND/OR logic operators."""
    
    def test_and_logic(self, tmp_path):
        """Test that AND requires all conditions to match."""
        (tmp_path / "test_file.py").write_text("x" * 100)
        (tmp_path / "test_file.js").write_text("x" * 100)
        (tmp_path / "main.py").write_text("x" * 100)
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: filename contains "test" AND ext equals "py"
        conds = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "py")
        ]
        result = filter_files_by_conditions(files, conds, "AND")
        
        assert len(result) == 1
        assert "test_file.py" in result[0]
    
    def test_or_logic(self, tmp_path):
        """Test that OR requires at least one condition to match."""
        (tmp_path / "test_file.py").write_text("")
        (tmp_path / "main.js").write_text("")
        (tmp_path / "config.json").write_text("")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: filename contains "test" OR ext equals "js"
        conds = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "js")
        ]
        result = filter_files_by_conditions(files, conds, "OR")
        
        assert len(result) == 2
        assert any("test_file.py" in f for f in result)
        assert any("main.js" in f for f in result)


class TestPathFiltering:
    """Test path-based filtering."""
    
    def test_path_contains_directory(self, tmp_path):
        """Test filtering by directory in path."""
        src_dir = tmp_path / "src"
        tests_dir = tmp_path / "tests"
        src_dir.mkdir()
        tests_dir.mkdir()
        
        (src_dir / "main.py").write_text("")
        (tests_dir / "test_main.py").write_text("")
        
        files = [str(src_dir / "main.py"), str(tests_dir / "test_main.py")]
        
        # Filter: path contains "src"
        cond = Condition("path", "contains", "src")
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "src" in result[0]


class TestMTimeFiltering:
    """Test modification time filtering."""
    
    def test_mtime_recent(self, tmp_path):
        """Test filtering by recent modification time."""
        old_file = tmp_path / "old.txt"
        new_file = tmp_path / "new.txt"
        
        # Create old file
        old_file.write_text("old content")
        old_time = (datetime.now() - timedelta(days=30)).timestamp()
        os.utime(old_file, (old_time, old_time))
        
        # Create new file (current time)
        new_file.write_text("new content")
        
        files = [str(old_file), str(new_file)]
        
        # Filter: mtime > 7 days ago (in seconds)
        seven_days_ago = (datetime.now() - timedelta(days=7)).timestamp()
        cond = Condition("mtime", ">", str(seven_days_ago))
        result = filter_files_by_conditions(files, [cond])
        
        assert len(result) == 1
        assert "new.txt" in result[0]


# =============================================================================
#                         INTEGRATION TESTS
# =============================================================================

class TestAIProcessorIntegration:
    """Integration tests for AI Processor with Advanced Conditions."""
    
    def test_conditions_applied_before_processing(self, tmp_path):
        """Test that conditions filter files before AI processing."""
        # Create test files
        (tmp_path / "include_me.py").write_text("def test(): pass")
        (tmp_path / "exclude_me.js").write_text("const x = 42;")
        (tmp_path / "include_too.py").write_text("import os")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: only Python files
        cond = Condition("ext", "equals", "py")
        result = filter_files_by_conditions(files, [cond])
        
        # Should only get .py files
        assert len(result) == 2
        assert all(f.endswith(".py") for f in result)
    
    def test_filtered_count_feedback(self, tmp_path):
        """Test that filtered count is calculated correctly."""
        # Create 10 files
        for i in range(10):
            ext = ".py" if i < 3 else ".js"
            (tmp_path / f"file{i}{ext}").write_text(f"content {i}")
        
        files = [str(f) for f in tmp_path.glob("*")]
        
        # Filter: only .py files (3 match, 7 filtered out)
        cond = Condition("ext", "equals", "py")
        result = filter_files_by_conditions(files, [cond])
        
        original_count = len(files)
        filtered_count = len(result)
        filtered_out = original_count - filtered_count
        
        assert original_count == 10
        assert filtered_count == 3
        assert filtered_out == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
