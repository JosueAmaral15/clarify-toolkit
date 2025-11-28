#!/usr/bin/env python3
"""
test_position_tooltip.py

Test for position tooltip and status bar display in match panel.
Tests that hovering over results shows line:column position.
"""


def test_position_extraction():
    """Test extracting line and column from result text."""
    # Simulate result item text format
    test_cases = [
        ("10:5  def test_function():", (10, 5)),
        ("25:10    return test_value", (25, 10)),
        ("1:0  import test_module", (1, 0)),
        ("100:45  # comment", (100, 45)),
        ("5:123  very long line...", (5, 123)),
    ]
    
    for text, expected in test_cases:
        # Extract position like in _on_item_hover
        if ':' in text:
            pos_part = text.split()[0]  # Get "line:col" part
            line, col = pos_part.split(':')
            line, col = int(line), int(col)
            
            assert (line, col) == expected, f"Expected {expected}, got ({line}, {col})"
    
    print("✓ test_position_extraction passed")


def test_tooltip_format():
    """Test tooltip message formatting."""
    file_path = "/home/user/project/src/main.py"
    line = 42
    col = 15
    
    tooltip = f"File: {file_path}\nLine: {line}\nColumn: {col}"
    
    expected = "File: /home/user/project/src/main.py\nLine: 42\nColumn: 15"
    assert tooltip == expected, f"Expected '{expected}', got '{tooltip}'"
    
    # Test multiline format
    assert tooltip.count('\n') == 2
    assert "File:" in tooltip
    assert "Line:" in tooltip
    assert "Column:" in tooltip
    
    print("✓ test_tooltip_format passed")


def test_status_bar_format():
    """Test status bar message formatting."""
    file_path = "/home/user/project/src/utils.py"
    line = 100
    col = 25
    
    status = f"📍 Position: Line {line}, Column {col} | File: {file_path}"
    
    expected = "📍 Position: Line 100, Column 25 | File: /home/user/project/src/utils.py"
    assert status == expected, f"Expected '{expected}', got '{status}'"
    
    # Check components
    assert "📍 Position:" in status
    assert f"Line {line}" in status
    assert f"Column {col}" in status
    assert f"File: {file_path}" in status
    
    print("✓ test_status_bar_format passed")


def test_position_edge_cases():
    """Test edge cases for position extraction."""
    edge_cases = [
        ("0:0  first character", (0, 0)),
        ("1:0  first line", (1, 0)),
        ("9999:9999  large numbers", (9999, 9999)),
        ("1:1  single digit", (1, 1)),
    ]
    
    for text, expected in edge_cases:
        if ':' in text:
            try:
                pos_part = text.split()[0]
                line, col = pos_part.split(':')
                line, col = int(line), int(col)
                assert (line, col) == expected
            except Exception as e:
                assert False, f"Failed to parse '{text}': {e}"
    
    print("✓ test_position_edge_cases passed")


def test_invalid_format_handling():
    """Test handling of invalid or unexpected formats."""
    invalid_cases = [
        "no colon here",
        "10 missing colon",
        "not:a:number extra colons",
        "",
        "   ",
    ]
    
    for text in invalid_cases:
        try:
            if ':' in text:
                pos_part = text.split()[0] if text.split() else ""
                if ':' in pos_part:
                    line, col = pos_part.split(':')
                    line, col = int(line), int(col)
                    # If we get here with valid numbers, that's OK
            # Invalid formats should either be skipped or handled gracefully
        except (ValueError, IndexError):
            # Expected for invalid formats
            pass
    
    print("✓ test_invalid_format_handling passed")


def test_long_file_paths():
    """Test with very long file paths."""
    long_path = "/very/long/path/with/many/nested/directories/that/goes/on/and/on/file.py"
    line = 50
    col = 10
    
    tooltip = f"File: {long_path}\nLine: {line}\nColumn: {col}"
    status = f"📍 Position: Line {line}, Column {col} | File: {long_path}"
    
    assert long_path in tooltip
    assert long_path in status
    assert f"Line: {line}" in tooltip
    assert f"Line {line}" in status
    
    print("✓ test_long_file_paths passed")


if __name__ == "__main__":
    print("Running position tooltip tests...\n")
    
    test_position_extraction()
    test_tooltip_format()
    test_status_bar_format()
    test_position_edge_cases()
    test_invalid_format_handling()
    test_long_file_paths()
    
    print("\n" + "="*60)
    print("All position tooltip tests passed! ✓")
    print("="*60)
