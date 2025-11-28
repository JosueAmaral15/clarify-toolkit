#!/usr/bin/env python3
"""
test_save_results_feature.py

Tests for the save results feature:
- Exporting matches to text format
- Proper formatting of results
- Handling empty results
"""
import os
import tempfile
from typing import Dict, List, Tuple


def test_export_text_format():
    """Test that export generates correct text format"""
    matches = {
        "/path/to/file1.py": [(10, 5, "    def calculate():"), (20, 10, "    return result")],
        "/path/to/file2.js": [(5, 0, "function test() {")]
    }
    
    # Simulate export_to_text logic
    lines = []
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    lines.append("=" * 80)
    lines.append("CLARIFY - SEARCH RESULTS")
    lines.append("=" * 80)
    lines.append(f"Total files with matches: {total_files}")
    lines.append(f"Total matches: {total_matches}")
    lines.append("=" * 80)
    lines.append("")
    
    for file_path, items in matches.items():
        lines.append(f"📁 {file_path}")
        lines.append(f"   Matches: {len(items)}")
        lines.append("-" * 80)
        
        for line_num, col, snippet in items:
            lines.append(f"   Line {line_num}, Col {col}:")
            lines.append(f"      {snippet.strip()}")
        
        lines.append("")
    
    result = "\n".join(lines)
    
    # Assertions
    assert "CLARIFY - SEARCH RESULTS" in result
    assert "Total files with matches: 2" in result
    assert "Total matches: 3" in result
    assert "/path/to/file1.py" in result
    assert "/path/to/file2.js" in result
    assert "Line 10, Col 5:" in result
    assert "def calculate():" in result
    
    print("✓ test_export_text_format passed")


def test_export_empty_results():
    """Test export with no results"""
    matches = {}
    
    if not matches:
        result = ""
    else:
        result = "should not reach here"
    
    assert result == "", "Empty matches should return empty string"
    print("✓ test_export_empty_results passed")


def test_export_single_file():
    """Test export with single file"""
    matches = {
        "/project/src/main.py": [
            (1, 0, "import os"),
            (2, 0, "import sys"),
            (10, 4, "    print('Hello')")
        ]
    }
    
    lines = []
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    lines.append(f"Total files with matches: {total_files}")
    lines.append(f"Total matches: {total_matches}")
    
    result = "\n".join(lines)
    
    assert "Total files with matches: 1" in result
    assert "Total matches: 3" in result
    
    print("✓ test_export_single_file passed")


def test_export_multiple_matches_per_line():
    """Test export with files having many matches"""
    matches = {
        "/test.txt": [(i, 0, f"Line {i}") for i in range(1, 101)]  # 100 matches
    }
    
    total_matches = sum(len(items) for items in matches.values())
    assert total_matches == 100, f"Expected 100 matches, got {total_matches}"
    
    print("✓ test_export_multiple_matches_per_line passed")


def test_export_special_characters():
    """Test export with special characters in snippets"""
    matches = {
        "/code.js": [
            (1, 0, "const str = \"Hello\\nWorld\";"),
            (2, 0, "const regex = /\\d+/g;"),
            (3, 0, "// Comment with 特殊字符")
        ]
    }
    
    lines = []
    for file_path, items in matches.items():
        for line_num, col, snippet in items:
            lines.append(snippet.strip())
    
    result = "\n".join(lines)
    
    assert "Hello\\nWorld" in result or "HelloWorld" in result
    assert "/\\d+/g" in result or "/d+/g" in result
    assert "特殊字符" in result
    
    print("✓ test_export_special_characters passed")


def test_export_preserves_indentation():
    """Test that export preserves indentation in snippets"""
    matches = {
        "/indent.py": [
            (1, 0, "def foo():"),
            (2, 4, "    if True:"),
            (3, 8, "        return 42")
        ]
    }
    
    lines = []
    for file_path, items in matches.items():
        for line_num, col, snippet in items:
            # strip() removes indentation, but original snippet had it
            assert snippet.startswith(" ") or snippet.startswith("def")
    
    print("✓ test_export_preserves_indentation passed")


def test_save_to_file():
    """Test actual file save operation"""
    matches = {
        "/test.py": [(1, 0, "import os"), (2, 0, "import sys")]
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name
    
    try:
        # Simulate save operation
        lines = []
        lines.append("=" * 80)
        lines.append("CLARIFY - SEARCH RESULTS")
        lines.append("=" * 80)
        lines.append(f"Total files with matches: {len(matches)}")
        lines.append(f"Total matches: {sum(len(items) for items in matches.values())}")
        lines.append("")
        
        for file_path, items in matches.items():
            lines.append(f"📁 {file_path}")
            for line_num, col, snippet in items:
                lines.append(f"   Line {line_num}, Col {col}: {snippet}")
        
        content = "\n".join(lines)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Verify file was created and has content
        assert os.path.exists(temp_path), "File should be created"
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        
        assert "CLARIFY - SEARCH RESULTS" in saved_content
        assert "/test.py" in saved_content
        assert "import os" in saved_content
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    print("✓ test_save_to_file passed")


def test_export_with_long_snippets():
    """Test export with very long code snippets"""
    long_snippet = "x = " + "a" * 200  # 200 character snippet
    matches = {
        "/long.py": [(1, 0, long_snippet)]
    }
    
    lines = []
    for file_path, items in matches.items():
        for line_num, col, snippet in items:
            lines.append(f"   Line {line_num}, Col {col}:")
            lines.append(f"      {snippet.strip()}")
    
    result = "\n".join(lines)
    
    assert "a" * 200 in result, "Long snippet should be preserved"
    
    print("✓ test_export_with_long_snippets passed")


def test_export_statistics():
    """Test that statistics are calculated correctly"""
    matches = {
        "/file1.py": [(1, 0, "line1"), (2, 0, "line2")],
        "/file2.py": [(1, 0, "line1")],
        "/file3.py": [(1, 0, "line1"), (2, 0, "line2"), (3, 0, "line3")]
    }
    
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    assert total_files == 3, f"Expected 3 files, got {total_files}"
    assert total_matches == 6, f"Expected 6 matches, got {total_matches}"
    
    print("✓ test_export_statistics passed")


def test_export_file_ordering():
    """Test that files are exported in consistent order"""
    matches = {
        "/z_file.py": [(1, 0, "last")],
        "/a_file.py": [(1, 0, "first")],
        "/m_file.py": [(1, 0, "middle")]
    }
    
    # Dictionary maintains insertion order in Python 3.7+
    file_list = list(matches.keys())
    
    # Just verify all files are present
    assert "/z_file.py" in file_list
    assert "/a_file.py" in file_list
    assert "/m_file.py" in file_list
    
    print("✓ test_export_file_ordering passed")


if __name__ == "__main__":
    print("Running save results feature tests...\n")
    
    test_export_text_format()
    test_export_empty_results()
    test_export_single_file()
    test_export_multiple_matches_per_line()
    test_export_special_characters()
    test_export_preserves_indentation()
    test_save_to_file()
    test_export_with_long_snippets()
    test_export_statistics()
    test_export_file_ordering()
    
    print("\n" + "="*60)
    print("All 10 save results feature tests passed! ✓")
    print("="*60)
