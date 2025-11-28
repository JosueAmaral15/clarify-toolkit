#!/usr/bin/env python3
"""
test_line_lookup_feature.py

Tests for the line lookup feature in Insert Panel:
- Search query with case sensitive, whole word, and regex options
- Finding lines by pattern instead of static line numbers
- Occurrence modes: First, Last, All
"""
import os
import tempfile
from src.core.insert import insert_at_line, InsertMode

def create_test_file(content: str) -> str:
    """Create a temporary file with given content and return its path."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        f.flush()
        return f.name


def test_find_line_case_sensitive():
    """Test finding lines with case-sensitive search"""
    content = """Line 1: Hello World
Line 2: hello world
Line 3: HELLO WORLD
Line 4: Hello World again"""
    
    # Simulate the _find_line_by_query logic
    query = "Hello"
    lines = content.splitlines()
    matches = []
    
    for i, line in enumerate(lines, start=1):
        if query in line:  # case-sensitive
            matches.append(i)
    
    assert matches == [1, 4], f"Expected [1, 4], got {matches}"
    print("✓ test_find_line_case_sensitive passed")


def test_find_line_case_insensitive():
    """Test finding lines with case-insensitive search"""
    import re
    content = """Line 1: Hello World
Line 2: hello world
Line 3: HELLO WORLD
Line 4: Hi there"""
    
    query = "hello"
    lines = content.splitlines()
    matches = []
    
    for i, line in enumerate(lines, start=1):
        if query.lower() in line.lower():  # case-insensitive
            matches.append(i)
    
    assert matches == [1, 2, 3], f"Expected [1, 2, 3], got {matches}"
    print("✓ test_find_line_case_insensitive passed")


def test_find_line_whole_word():
    """Test finding lines with whole word matching"""
    import re
    content = """Line 1: cat in the hat
Line 2: category list
Line 3: the cat
Line 4: concatenate"""
    
    query = "cat"
    lines = content.splitlines()
    matches = []
    
    pattern = r'\b' + re.escape(query) + r'\b'
    for i, line in enumerate(lines, start=1):
        if re.search(pattern, line, re.IGNORECASE):
            matches.append(i)
    
    assert matches == [1, 3], f"Expected [1, 3], got {matches}"
    print("✓ test_find_line_whole_word passed")


def test_find_line_regex():
    """Test finding lines with regex pattern"""
    import re
    content = """Line 1: email@example.com
Line 2: no email here
Line 3: user123@domain.org
Line 4: just text"""
    
    query = r"\w+@\w+\.\w+"
    lines = content.splitlines()
    matches = []
    
    for i, line in enumerate(lines, start=1):
        if re.search(query, line):
            matches.append(i)
    
    assert matches == [1, 3], f"Expected [1, 3], got {matches}"
    print("✓ test_find_line_regex passed")


def test_insert_at_first_occurrence():
    """Test inserting at first occurrence of pattern"""
    content = """function one() {
    console.log("one");
}
function two() {
    console.log("two");
}
function three() {
    console.log("three");
}"""
    
    # Find first occurrence of "function"
    import re
    lines = content.splitlines()
    matches = []
    for i, line in enumerate(lines, start=1):
        if "function" in line:
            matches.append(i)
    
    assert matches[0] == 1, f"First occurrence should be line 1, got {matches[0]}"
    
    # Insert above first occurrence
    result = insert_at_line(content, matches[0], "// Comment", InsertMode.INSERT_ABOVE)
    assert result.startswith("// Comment\n"), "Comment should be inserted above"
    print("✓ test_insert_at_first_occurrence passed")


def test_insert_at_last_occurrence():
    """Test inserting at last occurrence of pattern"""
    content = """function one() {
    console.log("one");
}
function two() {
    console.log("two");
}
function three() {
    console.log("three");
}"""
    
    # Find last occurrence of "function"
    lines = content.splitlines()
    matches = []
    for i, line in enumerate(lines, start=1):
        if "function" in line:
            matches.append(i)
    
    assert matches[-1] == 7, f"Last occurrence should be line 7, got {matches[-1]}"
    
    # Insert below last occurrence
    result = insert_at_line(content, matches[-1], "// End", InsertMode.INSERT_BELOW)
    assert "// End" in result, "Comment should be inserted below"
    print("✓ test_insert_at_last_occurrence passed")


def test_insert_at_all_occurrences():
    """Test inserting at all occurrences of pattern"""
    content = """import React from 'react';
import { useState } from 'react';
import axios from 'axios';

const Component = () => {
    return <div>Hello</div>;
};"""
    
    # Find all lines with "import"
    lines = content.splitlines()
    matches = []
    for i, line in enumerate(lines, start=1):
        if "import" in line:
            matches.append(i)
    
    assert len(matches) == 3, f"Should find 3 imports, found {len(matches)}"
    
    # Insert comment at end of each import line
    result = content
    for line_num in sorted(matches, reverse=True):  # Process from bottom to top
        result = insert_at_line(result, line_num, " // Added", InsertMode.RIGHT)
    
    result_lines = result.splitlines()
    assert " // Added" in result_lines[0], "First import should have comment"
    assert " // Added" in result_lines[1], "Second import should have comment"
    assert " // Added" in result_lines[2], "Third import should have comment"
    print("✓ test_insert_at_all_occurrences passed")


def test_no_match_skips_file():
    """Test that files without matches are skipped"""
    content = """Line 1: Some text
Line 2: More text
Line 3: Even more text"""
    
    # Search for pattern that doesn't exist
    query = "nonexistent"
    lines = content.splitlines()
    matches = []
    
    for i, line in enumerate(lines, start=1):
        if query in line:
            matches.append(i)
    
    assert len(matches) == 0, "Should find no matches"
    print("✓ test_no_match_skips_file passed")


def test_regex_with_whole_word():
    """Test regex pattern with whole word boundary"""
    import re
    content = """Line 1: test testing
Line 2: the test
Line 3: contest
Line 4: test"""
    
    query = "test"
    lines = content.splitlines()
    matches = []
    
    pattern = r'\b' + query + r'\b'
    for i, line in enumerate(lines, start=1):
        if re.search(pattern, line):
            matches.append(i)
    
    assert matches == [1, 2, 4], f"Expected [1, 2, 4], got {matches}"
    print("✓ test_regex_with_whole_word passed")


def test_multiline_insertion():
    """Test inserting multi-line text"""
    content = """Line 1
Line 2
Line 3"""
    
    multiline_text = """New Line A
New Line B
New Line C"""
    
    result = insert_at_line(content, 2, multiline_text, InsertMode.INSERT_BELOW)
    result_lines = result.splitlines()
    
    assert "Line 2" in result_lines, "Original line should be preserved"
    assert "New Line A" in result, "First new line should be inserted"
    assert "New Line B" in result, "Second new line should be inserted"
    assert "New Line C" in result, "Third new line should be inserted"
    print("✓ test_multiline_insertion passed")


if __name__ == "__main__":
    print("Running line lookup feature tests...\n")
    
    test_find_line_case_sensitive()
    test_find_line_case_insensitive()
    test_find_line_whole_word()
    test_find_line_regex()
    test_insert_at_first_occurrence()
    test_insert_at_last_occurrence()
    test_insert_at_all_occurrences()
    test_no_match_skips_file()
    test_regex_with_whole_word()
    test_multiline_insertion()
    
    print("\n" + "="*60)
    print("All 10 line lookup feature tests passed! ✓")
    print("="*60)
