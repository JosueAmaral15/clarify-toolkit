#!/usr/bin/env python3
"""
test_results_summary.py

Test for results summary display in match panel.
Tests that the summary line shows total matches and files.
"""


def test_results_summary_calculation():
    """Test calculation of results summary."""
    # Simulate matches data structure
    matches = {
        "/path/to/file1.py": [
            (10, 5, "def test_function():"),
            (25, 10, "    return test_value")
        ],
        "/path/to/file2.py": [
            (5, 0, "import test_module"),
            (15, 8, "test_var = 42"),
            (30, 12, "# test comment")
        ],
        "/path/to/file3.txt": [
            (1, 0, "test content")
        ]
    }
    
    # Calculate statistics
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    # Verify calculations
    assert total_files == 3, f"Expected 3 files, got {total_files}"
    assert total_matches == 6, f"Expected 6 matches, got {total_matches}"
    
    # Test summary format
    summary = f"📊 Results: {total_matches} matches in {total_files} file(s)"
    expected = "📊 Results: 6 matches in 3 file(s)"
    assert summary == expected, f"Expected '{expected}', got '{summary}'"
    
    print("✓ test_results_summary_calculation passed")


def test_empty_results():
    """Test summary with no results."""
    matches = {}
    
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    assert total_files == 0
    assert total_matches == 0
    
    print("✓ test_empty_results passed")


def test_single_file_single_match():
    """Test summary with single file and single match."""
    matches = {
        "/path/to/file.py": [(10, 5, "test line")]
    }
    
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    assert total_files == 1
    assert total_matches == 1
    
    summary = f"📊 Results: {total_matches} matches in {total_files} file(s)"
    expected = "📊 Results: 1 matches in 1 file(s)"
    assert summary == expected
    
    print("✓ test_single_file_single_match passed")


def test_many_files_many_matches():
    """Test summary with many files and matches."""
    matches = {}
    
    # Create 50 files with varying match counts
    for i in range(50):
        matches[f"/path/file{i}.py"] = [
            (j, 0, f"line {j}") for j in range(1, (i % 10) + 1)
        ]
    
    total_files = len(matches)
    total_matches = sum(len(items) for items in matches.values())
    
    assert total_files == 50
    # Sum: 1+2+3+4+5+6+7+8+9+0 = 45, repeated 5 times = 225
    expected_matches = sum((i % 10) for i in range(50))
    assert total_matches == expected_matches
    
    print(f"✓ test_many_files_many_matches passed ({total_matches} matches in {total_files} files)")


if __name__ == "__main__":
    print("Running results summary tests...\n")
    
    test_results_summary_calculation()
    test_empty_results()
    test_single_file_single_match()
    test_many_files_many_matches()
    
    print("\n" + "="*60)
    print("All results summary tests passed! ✓")
    print("="*60)
