#!/usr/bin/env python3
"""
Test script for verifying Bug Fix #1 and Bug Fix #2
Created: 2026-01-07
Purpose: Validate fixes work correctly without GUI
"""

import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 80)
print("BUG FIX VALIDATION TESTS")
print("=" * 80)
print()

# ============================================================================
# BUG FIX #1: Regex Escape Error in File Explorer Replace
# ============================================================================
print("TEST 1: Bug Fix #1 - Regex Escape Error")
print("-" * 80)

def test_replace_logic(text: str, query: str, replacement: str, use_regex: bool, case_sensitive: bool = False):
    """Simulate the fixed replacement logic from file_explorer_executor.py"""
    
    # Build pattern (lines 463-470)
    if use_regex:
        pattern = query
    else:
        pattern = re.escape(query)
    
    # Compile regex (lines 473-478)
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return None, f"Regex error: {e}"
    
    # BUG FIX: Escape backslashes in non-regex mode (lines 483-489)
    if not use_regex:
        safe_replacement = replacement.replace("\\", "\\\\")
    else:
        safe_replacement = replacement
    
    # Perform replacement (lines 492-496)
    try:
        new_text = regex.sub(safe_replacement, text)
        count = len(regex.findall(text))
        return new_text, count
    except Exception as e:
        return None, f"Replacement error: {e}"

# Test Case 1.1: Literal backslash in non-regex mode (the bug scenario)
print("Test 1.1: Literal backslash \\S in non-regex mode")
text = "Hello World"
query = "World"
replacement = "\\S"  # User types backslash + S
use_regex = False

result, count = test_replace_logic(text, query, replacement, use_regex)
if result == "Hello \\S":
    print("  ✅ PASS: Literal \\S correctly replaced")
    print(f"     Input: '{text}' → Output: '{result}'")
else:
    print(f"  ❌ FAIL: Expected 'Hello \\S', got '{result}'")

# Test Case 1.2: Multiple escape sequences
print("\nTest 1.2: Multiple escape sequences \\n \\t \\r")
text = "Line1 Line2"
query = "Line2"
replacement = "\\n\\t\\r"
use_regex = False

result, count = test_replace_logic(text, query, replacement, use_regex)
if result == "Line1 \\n\\t\\r":
    print("  ✅ PASS: Multiple escape sequences handled correctly")
    print(f"     Input: '{text}' → Output: '{result}'")
else:
    print(f"  ❌ FAIL: Expected 'Line1 \\n\\t\\r', got '{result}'")

# Test Case 1.3: Backreferences in regex mode (should NOT be escaped)
print("\nTest 1.3: Backreferences \\1 \\2 in regex mode")
text = "John Doe"
query = r"(\w+) (\w+)"  # Capture first and last name
replacement = r"\2, \1"  # Reverse to "Doe, John"
use_regex = True

result, count = test_replace_logic(text, query, replacement, use_regex)
if result == "Doe, John":
    print("  ✅ PASS: Backreferences work correctly in regex mode")
    print(f"     Input: '{text}' → Output: '{result}'")
else:
    print(f"  ❌ FAIL: Expected 'Doe, John', got '{result}'")

# Test Case 1.4: Edge case - double backslash
print("\nTest 1.4: Double backslash \\\\ in non-regex mode")
text = "path/to/file"
query = "/"
replacement = "\\\\"  # User wants literal backslash
use_regex = False

result, count = test_replace_logic(text, query, replacement, use_regex)
if "\\" in result:
    print("  ✅ PASS: Double backslash handled correctly")
    print(f"     Input: '{text}' → Output: '{result}'")
else:
    print(f"  ❌ FAIL: Backslash not found in result: '{result}'")

print("\n" + "=" * 80)

# ============================================================================
# BUG FIX #2: Table/Tree View Synchronization
# ============================================================================
print("TEST 2: Bug Fix #2 - Table/Tree View Synchronization")
print("-" * 80)

class MockFileExplorerDock:
    """Mock class to simulate the fixed view sync logic"""
    
    def __init__(self):
        self.last_browse_results = []
        self.last_was_search = False
        self._user_manually_changed_view = False
        self.current_view_index = 1  # 0=Tree, 1=Table
        self.tree_populated = False
        self.table_populated = False
    
    def handle_search_results(self, files_data):
        """Simulate search mode result handling (lines 960-996)"""
        self.last_browse_results = files_data
        self.last_was_search = True
        self.table_populated = True
        
        # Original logic: sync to table if user is in table view
        if self._user_manually_changed_view and self.current_view_index == 1:
            # Sync to table (already there)
            pass
    
    def handle_browse_results(self, files_data):
        """Simulate browse mode result handling WITH BUG FIX (lines 1038-1096)"""
        self.last_browse_results = files_data
        self.last_was_search = False
        self.table_populated = True
        
        # BUGFIX v2.9.119: If user is in tree view, also populate tree
        if self._user_manually_changed_view and self.current_view_index == 0:
            self.tree_populated = True  # Simulate _sync_browse_to_tree()
    
    def user_switches_to_tree(self):
        """User manually switches to tree view"""
        self._user_manually_changed_view = True
        self.current_view_index = 0

# Test Case 2.1: User in Tree view → Browse operation
print("Test 2.1: User manually switches to Tree, then browses")
dock = MockFileExplorerDock()
dock.user_switches_to_tree()
dock.handle_browse_results([{"name": "file1.txt"}, {"name": "file2.txt"}])

if dock.tree_populated and dock.table_populated:
    print("  ✅ PASS: Both Tree and Table populated after browse")
    print(f"     Tree populated: {dock.tree_populated}")
    print(f"     Table populated: {dock.table_populated}")
else:
    print(f"  ❌ FAIL: Tree: {dock.tree_populated}, Table: {dock.table_populated}")

# Test Case 2.2: User in Table view → Browse operation (no sync needed)
print("\nTest 2.2: User in Table view, then browses")
dock2 = MockFileExplorerDock()
dock2._user_manually_changed_view = True
dock2.current_view_index = 1  # Table view
dock2.handle_browse_results([{"name": "file1.txt"}])

if dock2.table_populated and not dock2.tree_populated:
    print("  ✅ PASS: Only Table populated (Tree not synced unnecessarily)")
    print(f"     Tree populated: {dock2.tree_populated}")
    print(f"     Table populated: {dock2.table_populated}")
else:
    print(f"  ❌ FAIL: Tree: {dock2.tree_populated}, Table: {dock2.table_populated}")

# Test Case 2.3: Auto-switch (not manual) - no sync
print("\nTest 2.3: Auto-switch to Tree (not manual), then browses")
dock3 = MockFileExplorerDock()
dock3._user_manually_changed_view = False  # Auto-switch
dock3.current_view_index = 0  # Tree view
dock3.handle_browse_results([{"name": "file1.txt"}])

if dock3.table_populated and not dock3.tree_populated:
    print("  ✅ PASS: Tree not synced on auto-switch (only manual triggers sync)")
    print(f"     Tree populated: {dock3.tree_populated}")
    print(f"     Table populated: {dock3.table_populated}")
else:
    print(f"  ❌ FAIL: Tree: {dock3.tree_populated}, Table: {dock3.table_populated}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED")
print("=" * 80)
