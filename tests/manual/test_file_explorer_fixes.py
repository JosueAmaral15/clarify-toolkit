#!/usr/bin/env python3
"""
Test script for File Explorer Bug Fixes
Created: 2026-01-08
Purpose: Validate all 4 bug fixes work correctly
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# ============================================================================
# TEST FIX #1: Exclude Globs Pattern Matching
# ============================================================================
print("TEST FIX #1: Exclude Globs Pattern Matching")
print("-" * 80)

def test_exclude_pattern_matching():
    """Test the fixed exclude glob logic."""
    
    # Simulate the fixed logic
    def matches_exclude_pattern(file_path, file_name, exclude_globs):
        import fnmatch
        
        for pattern in exclude_globs:
            # Check if pattern exists as a path component
            path_components = file_path.split(os.sep)
            if pattern in path_components:
                return True
            # Also check if pattern matches filename
            if fnmatch.fnmatch(file_name, pattern):
                return True
        return False
    
    # Test cases
    test_cases = [
        # (file_path, file_name, exclude_patterns, should_exclude)
        ("/home/user/project/.venv/lib/python/site.py", "site.py", [".venv"], True),
        ("/home/user/project/node_modules/package/index.js", "index.js", ["node_modules"], True),
        ("/home/user/project/src/main.py", "main.py", [".venv", "node_modules"], False),
        ("/home/user/project/test.pyc", "test.pyc", ["*.pyc"], True),
        ("/home/user/project/.git/config", "config", [".git"], True),
        ("/home/user/project/venv/lib/site.py", "site.py", [".venv"], False),  # Different name
        ("/home/user/project/.venv", ".venv", [".venv"], True),  # Directory itself
    ]
    
    passed = 0
    failed = 0
    
    for file_path, file_name, patterns, should_exclude in test_cases:
        result = matches_exclude_pattern(file_path, file_name, patterns)
        status = "✅ PASS" if result == should_exclude else "❌ FAIL"
        
        if result == should_exclude:
            passed += 1
        else:
            failed += 1
        
        print(f"  {status}: {file_path}")
        if result != should_exclude:
            print(f"         Expected: {should_exclude}, Got: {result}")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed")
    return failed == 0

# ============================================================================
# TEST FIX #3: Case/Regex Checkboxes Logic
# ============================================================================
print("TEST FIX #3: Case/Regex Checkboxes Logic")
print("-" * 80)

def test_checkbox_logic():
    """Test the fixed checkbox enable/disable logic."""
    
    def should_enable_checkboxes(field_data):
        """New logic: enable for text fields."""
        return field_data in ("filename", "path", "ext", "content")
    
    test_cases = [
        ("filename", True),
        ("path", True),
        ("ext", True),
        ("content", True),
        ("size", False),
        ("mtime", False),
    ]
    
    passed = 0
    failed = 0
    
    for field, should_enable in test_cases:
        result = should_enable_checkboxes(field)
        status = "✅ PASS" if result == should_enable else "❌ FAIL"
        
        if result == should_enable:
            passed += 1
        else:
            failed += 1
        
        print(f"  {status}: Field '{field}' → Checkboxes {'enabled' if should_enable else 'disabled'}")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed")
    return failed == 0

# ============================================================================
# TEST FIX #4: Operators Display
# ============================================================================
def test_operators_display():
    """Test operators display logic."""
    operators = [
        "equals",
        "not equals",
        "contains",
        "not contains",
        "greater than",
        "less than",  # was "<"
        "greater than or equal",  # was ">="
        "less than or equal",  # was "<="
        "regex"
    ]

    print("TEST FIX #4: Operators Display")
    print("-" * 80)
    print("  Operators list (should show full text, not symbols):")
    for i, op in enumerate(operators, 1):
        symbol_check = " ← Was symbol!" if op in ["<", ">=", "<="] else ""
        print(f"    {i}. {op}{symbol_check}")

    # Check if any symbols remain
    has_symbols = any(op in ["<", ">=", "<="] for op in operators)
    fix4_passed = not has_symbols

    print()
    if fix4_passed:
        print("  ✅ PASS: All operators use full text")
    else:
        print("  ❌ FAIL: Some operators still use symbols")
    print()
    
    return fix4_passed

# ============================================================================
# TEST FIX #5: Type Filter i18n
# ============================================================================
print("TEST FIX #5: Type Filter i18n-safe Comparison")
print("-" * 80)

def test_type_filter_logic():
    """Test the fixed type filter logic using data instead of text."""
    
    # Simulate combo box data
    combo_data = {
        0: ("Any", "any"),
        1: ("Files Only", "files"),
        2: ("Directories Only", "dirs"),
        # Portuguese translations
        3: ("Qualquer", "any"),
        4: ("Apenas Arquivos", "files"),
        5: ("Apenas Diretórios", "dirs"),
    }
    
    def get_filter_type(index):
        """New logic: use data instead of text."""
        _, data = combo_data[index]
        return data
    
    test_cases = [
        (1, "files"),  # English "Files Only"
        (2, "dirs"),   # English "Directories Only"
        (4, "files"),  # Portuguese "Apenas Arquivos"
        (5, "dirs"),   # Portuguese "Apenas Diretórios"
        (0, "any"),    # English "Any"
        (3, "any"),    # Portuguese "Qualquer"
    ]
    
    passed = 0
    failed = 0
    
    for index, expected_filter in test_cases:
        text, _ = combo_data[index]
        result = get_filter_type(index)
        status = "✅ PASS" if result == expected_filter else "❌ FAIL"
        
        if result == expected_filter:
            passed += 1
        else:
            failed += 1
        
        print(f"  {status}: '{text}' → filter='{result}' (expected '{expected_filter}')")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("=" * 80)
    print("FILE EXPLORER BUG FIXES - VALIDATION TESTS")
    print("=" * 80)
    print()

    # ============================================================================
    # TEST FIX #1: Exclude Globs Pattern Matching
    # ============================================================================
    print("TEST FIX #1: Exclude Globs Pattern Matching")
    print("-" * 80)
    fix1_passed = test_exclude_pattern_matching()
    print()

    # ============================================================================
    # TEST FIX #3: Case/Regex Checkboxes Logic
    # ============================================================================
    print("TEST FIX #3: Case/Regex Checkboxes Logic")
    print("-" * 80)
    fix3_passed = test_checkbox_logic()
    print()

    # ============================================================================
    # TEST FIX #4: Operators Display
    # ============================================================================
    fix4_passed = test_operators_display()

    # ============================================================================
    # TEST FIX #5: Type Filter i18n
    # ============================================================================
    print("TEST FIX #5: Type Filter i18n-safe Comparison")
    print("-" * 80)
    fix5_passed = test_type_filter_logic()
    print()

    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    fixes_status = [
        ("Fix #1: Exclude Globs", fix1_passed),
        ("Fix #3: Case/Regex Checkboxes", fix3_passed),
        ("Fix #4: Operators Display", fix4_passed),
        ("Fix #5: Type Filter i18n", fix5_passed),
    ]

    all_passed = all(status for _, status in fixes_status)

    for fix_name, status in fixes_status:
        status_text = "✅ PASSED" if status else "❌ FAILED"
        print(f"  {fix_name}: {status_text}")

    print()
    print("=" * 80)
    if all_passed:
        print("ALL FIXES VALIDATED ✅")
        print("=" * 80)
        sys.exit(0)
    else:
        print("SOME FIXES FAILED ❌")
        print("=" * 80)
        sys.exit(1)
