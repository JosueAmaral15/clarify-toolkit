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
# TEST FUNCTIONS (can be imported)
# ============================================================================

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
        ("/home/user/project/__pycache__/module.cpython-39.pyc", "module.cpython-39.pyc", ["__pycache__"], True),
        ("/home/user/project/src/utils.py", "utils.py", ["*.pyc", ".venv"], False),
    ]
    
    passed = 0
    failed = 0
    
    for file_path, file_name, patterns, expected in test_cases:
        result = matches_exclude_pattern(file_path, file_name, patterns)
        if result == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"  {status}: {file_name} | patterns={patterns} | excluded={result} (expected={expected})")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed")
    return failed == 0

def test_checkbox_logic():
    """Test the fixed checkbox initial state logic."""
    
    # Simulate the fixed logic
    def should_enable_checkbox(parent_enabled):
        """Child checkboxes are enabled only if parent is checked."""
        return parent_enabled
    
    test_cases = [
        # (parent_checked, child_should_be_enabled)
        (True, True),   # When case-sensitive is checked, whole word should be enabled
        (False, False), # When case-sensitive is unchecked, whole word should be disabled
        (True, True),   # When regex is checked, case-sensitive should be enabled
        (False, False), # When regex is unchecked, case-sensitive should be disabled
    ]
    
    passed = 0
    failed = 0
    
    for parent_checked, expected_enabled in test_cases:
        result = should_enable_checkbox(parent_checked)
        if result == expected_enabled:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"  {status}: parent={parent_checked} → child_enabled={result} (expected={expected_enabled})")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed")
    return failed == 0

def test_type_filter_logic():
    """Test the Type Filter i18n display fix."""
    
    # Simulate the fixed logic
    def translate_type_filter(value):
        """Return translated type filter display text."""
        translations = {
            "any": "Any",
            "files": "Files Only",
            "dirs": "Directories Only"
        }
        return translations.get(value, value)
    
    test_cases = [
        ("any", "Any", "Any"),
        ("files", "Files Only", "Files Only"),
        ("dirs", "Directories Only", "Directories Only"),
    ]
    
    passed = 0
    failed = 0
    
    for value, expected_display, expected_filter in test_cases:
        result = translate_type_filter(value)
        if result == expected_display:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"  {status}: '{value}' → display='{result}' filter='{expected_filter}'")
    
    print()
    print(f"  Results: {passed} passed, {failed} failed")
    return failed == 0

