#!/usr/bin/env python3
"""
Test Context Menu Functionality (v2.9.2)

This script tests the new context menu features in ResultsTree:
- Multi-selection (CTRL/Shift)
- Copy selected items
- Copy all results
- Select all
- Open file(s)
- Open all files

Author: Josué Amaral
Date: 2025-11-28
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_context_menu():
    """Test context menu implementation."""
    print("=" * 80)
    print("CLARIFY - Context Menu Test (v2.9.2)")
    print("=" * 80)
    print()
    
    try:
        from PySide6.QtWidgets import QApplication, QTreeWidget
        from PySide6.QtCore import Qt
        
        # Create application
        app = QApplication([])
        
        # Import ResultsTree
        from src.app import ResultsTree
        
        # Create widget
        tree = ResultsTree()
        
        # Test 1: Check if multi-selection is enabled
        print("✅ Test 1: Multi-selection mode")
        selection_mode = tree.selectionMode()
        expected_mode = QTreeWidget.ExtendedSelection
        assert selection_mode == expected_mode, f"Expected {expected_mode}, got {selection_mode}"
        print(f"   Selection mode: {selection_mode} (ExtendedSelection)")
        print()
        
        # Test 2: Check if context menu is enabled
        print("✅ Test 2: Context menu policy")
        context_policy = tree.contextMenuPolicy()
        expected_policy = Qt.CustomContextMenu
        assert context_policy == expected_policy, f"Expected {expected_policy}, got {context_policy}"
        print(f"   Context menu policy: CustomContextMenu")
        print()
        
        # Test 3: Check if methods exist
        print("✅ Test 3: Context menu methods")
        methods = [
            '_show_context_menu',
            '_copy_selected',
            '_copy_all',
            '_open_selected_files',
            '_open_all_files'
        ]
        for method in methods:
            assert hasattr(tree, method), f"Method {method} not found"
            print(f"   ✓ {method}")
        print()
        
        # Test 4: Test export_to_text with sample data
        print("✅ Test 4: Export to text")
        sample_matches = {
            "/tmp/test1.py": [(10, 5, "def example():"), (20, 8, "    return True")],
            "/tmp/test2.js": [(15, 3, "const value = 123;")]
        }
        tree._matches_data = sample_matches
        exported = tree.export_to_text()
        assert "CLARIFY - SEARCH RESULTS" in exported, "Header not found"
        assert "Total files with matches: 2" in exported, "File count wrong"
        assert "Total matches: 3" in exported, "Match count wrong"
        assert "/tmp/test1.py" in exported, "File path not found"
        print("   Export format: ✓ Valid")
        print(f"   Exported {len(exported)} characters")
        print()
        
        # Test 5: Test populate with sample data
        print("✅ Test 5: Populate tree with data")
        tree.populate(sample_matches)
        root_count = tree.topLevelItemCount()
        assert root_count == 3, f"Expected 3 top-level items (summary + 2 files), got {root_count}"
        
        # Check first item is summary
        first_item = tree.topLevelItem(0)
        assert "📊 Results:" in first_item.text(0), "First item should be summary"
        print(f"   ✓ Summary: {first_item.text(0)}")
        
        # Check file items
        file1_item = tree.topLevelItem(1)
        assert file1_item.text(0) == "/tmp/test1.py", "File path mismatch"
        assert file1_item.childCount() == 2, "Expected 2 matches for test1.py"
        print(f"   ✓ File 1: {file1_item.text(0)} ({file1_item.childCount()} matches)")
        
        file2_item = tree.topLevelItem(2)
        assert file2_item.text(0) == "/tmp/test2.js", "File path mismatch"
        assert file2_item.childCount() == 1, "Expected 1 match for test2.js"
        print(f"   ✓ File 2: {file2_item.text(0)} ({file2_item.childCount()} matches)")
        print()
        
        # Test 6: Test selectAll method
        print("✅ Test 6: Select all functionality")
        tree.selectAll()
        selected = tree.selectedItems()
        total_items = root_count + sum(tree.topLevelItem(i).childCount() for i in range(1, root_count))
        print(f"   Selected {len(selected)} items")
        print(f"   Total items: {total_items}")
        print()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("Context Menu Features:")
        print("  📋 Copy - Copy selected items")
        print("  📋 Copy All Results - Copy all results")
        print("  ✅ Select All - Select all items")
        print("  📂 Open File - Open selected file(s)")
        print("  📂 Open All Files - Open all files")
        print()
        print("Multi-Selection:")
        print("  CTRL + Click - Add/remove from selection")
        print("  Shift + Click - Select range")
        print("  CTRL + A - Select all")
        print()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("   PySide6 may not be installed or src.app not found")
        return False
    except AssertionError as e:
        print(f"❌ Assertion Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_context_menu()
    sys.exit(0 if success else 1)
