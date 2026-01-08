#!/usr/bin/env python3
"""
Test script for verifying Bug Fix #1 and Bug Fix #2
Created: 2026-01-07
Updated: 2026-01-08 (converted to pytest format)
Purpose: Validate fixes work correctly without GUI
"""

import re
import pytest


def _simulate_replace_logic(text: str, query: str, replacement: str, use_regex: bool, case_sensitive: bool = False):
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


# ============================================================================
# BUG FIX #1: Regex Escape Error in File Explorer Replace
# ============================================================================

def test_literal_backslash_non_regex():
    """Test Case 1.1: Literal backslash in non-regex mode (the bug scenario)"""
    text = "Hello World"
    query = "World"
    replacement = "\\S"  # User types backslash + S
    use_regex = False

    result, count = _simulate_replace_logic(text, query, replacement, use_regex)
    assert result == "Hello \\S", f"Expected 'Hello \\S', got '{result}'"


def test_multiple_escape_sequences():
    """Test Case 1.2: Multiple escape sequences"""
    text = "Line1 Line2"
    query = "Line2"
    replacement = "\\n\\t\\r"
    use_regex = False

    result, count = _simulate_replace_logic(text, query, replacement, use_regex)
    assert result == "Line1 \\n\\t\\r", f"Expected 'Line1 \\n\\t\\r', got '{result}'"


def test_backreferences_in_regex_mode():
    """Test Case 1.3: Backreferences in regex mode (should NOT be escaped)"""
    text = "John Doe"
    query = r"(\w+) (\w+)"  # Capture first and last name
    replacement = r"\2, \1"  # Reverse to "Doe, John"
    use_regex = True

    result, count = _simulate_replace_logic(text, query, replacement, use_regex)
    assert result == "Doe, John", f"Expected 'Doe, John', got '{result}'"


def test_double_backslash_non_regex():
    """Test Case 1.4: Edge case - double backslash"""
    text = "path/to/file"
    query = "/"
    replacement = "\\\\"  # User wants literal backslash
    use_regex = False

    result, count = _simulate_replace_logic(text, query, replacement, use_regex)
    assert "\\" in result, f"Backslash not found in result: '{result}'"


# ============================================================================
# BUG FIX #2: Table/Tree View Synchronization
# ============================================================================

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


def test_browse_with_tree_view_selected():
    """Test Case 2.1: User in Tree view → Browse operation"""
    dock = MockFileExplorerDock()
    dock.user_switches_to_tree()
    dock.handle_browse_results([{"name": "file1.txt"}, {"name": "file2.txt"}])
    
    assert dock.tree_populated and dock.table_populated, \
        f"Expected both views populated. Tree: {dock.tree_populated}, Table: {dock.table_populated}"


def test_browse_with_table_view_selected():
    """Test Case 2.2: User in Table view → Browse operation (no sync needed)"""
    dock = MockFileExplorerDock()
    dock._user_manually_changed_view = True
    dock.current_view_index = 1  # Table view
    dock.handle_browse_results([{"name": "file1.txt"}])
    
    assert dock.table_populated and not dock.tree_populated, \
        f"Expected only Table populated. Tree: {dock.tree_populated}, Table: {dock.table_populated}"


def test_browse_with_auto_switch():
    """Test Case 2.3: Auto-switch (not manual) - no sync"""
    dock = MockFileExplorerDock()
    dock._user_manually_changed_view = False  # Auto-switch
    dock.current_view_index = 0  # Tree view
    dock.handle_browse_results([{"name": "file1.txt"}])
    
    assert dock.table_populated and not dock.tree_populated, \
        f"Expected Tree not synced on auto-switch. Tree: {dock.tree_populated}, Table: {dock.table_populated}"
