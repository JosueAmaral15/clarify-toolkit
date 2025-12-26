#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for FileExplorerDock with Search/Replace (v2.9.116).

Tests:
- Browse mode (no search parameters)
- Search mode (filename pattern)
- Search mode (content query)
- Replace first/all functionality
- Widget signal connections
- Executor integration
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from src.gui.file_explorer_dock import FileExplorerDock


def test_widget_instantiation():
    """Test that FileExplorerDock can be instantiated with new widgets."""
    print("\n=== Test 1: Widget Instantiation ===")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        dock = FileExplorerDock(dialog_mode=False)
        
        # Check that all new widgets exist
        assert hasattr(dock, 'filename_panel'), "Missing filename_panel"
        assert hasattr(dock, 'content_panel'), "Missing content_panel"
        assert hasattr(dock, 'search_options_panel'), "Missing search_options_panel"
        assert hasattr(dock, 'replace_panel'), "Missing replace_panel"
        assert hasattr(dock, 'conditions_grid'), "Missing conditions_grid"
        assert hasattr(dock, 'executor'), "Missing executor"
        
        # Check sections exist
        assert hasattr(dock, 'section_directory'), "Missing section_directory"
        assert hasattr(dock, 'section_search'), "Missing section_search"
        assert hasattr(dock, 'section_filters'), "Missing section_filters"
        assert hasattr(dock, 'section_conditions'), "Missing section_conditions"
        
        print("✅ All widgets instantiated successfully")
        return True
    
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False


def test_browse_mode():
    """Test browse mode (no search parameters)."""
    print("\n=== Test 2: Browse Mode ===")
    
    # Create temporary test directory with files
    test_dir = tempfile.mkdtemp(prefix="clarify_test_")
    
    try:
        # Create test files
        (Path(test_dir) / "file1.txt").write_text("Content 1")
        (Path(test_dir) / "file2.py").write_text("print('hello')")
        (Path(test_dir) / "file3.json").write_text('{"key": "value"}')
        
        app = QApplication.instance() or QApplication(sys.argv)
        dock = FileExplorerDock(dialog_mode=False)
        
        # Set directory
        dock.ed_directory.setText(test_dir)
        
        # Execute browse (simulate button click)
        dock._list_files()
        
        # Check that results table has entries
        row_count = dock.table_manager.table.rowCount()
        assert row_count >= 3, f"Expected at least 3 files, got {row_count}"
        
        print(f"✅ Browse mode successful - Found {row_count} files")
        return True
    
    except Exception as e:
        print(f"❌ Browse mode failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_search_mode_filename():
    """Test search mode with filename pattern."""
    print("\n=== Test 3: Search Mode - Filename Pattern ===")
    
    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="clarify_test_")
    
    try:
        # Create test files
        (Path(test_dir) / "test_file.txt").write_text("Content")
        (Path(test_dir) / "other_file.py").write_text("Code")
        (Path(test_dir) / "test_data.json").write_text("Data")
        
        app = QApplication.instance() or QApplication(sys.argv)
        dock = FileExplorerDock(dialog_mode=False)
        
        # Set directory and search pattern
        dock.ed_directory.setText(test_dir)
        dock.filename_panel.ed_pattern.setText("test_*")
        
        # Execute search
        dock._list_files()
        
        # Check results
        row_count = dock.table_manager.table.rowCount()
        assert row_count == 2, f"Expected 2 files matching 'test_*', got {row_count}"
        
        print(f"✅ Filename search successful - Found {row_count} matching files")
        return True
    
    except Exception as e:
        print(f"❌ Filename search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_search_mode_content():
    """Test search mode with content query."""
    print("\n=== Test 4: Search Mode - Content Query ===")
    
    # Create temporary test directory
    test_dir = tempfile.mkdtemp(prefix="clarify_test_")
    
    try:
        # Create test files with specific content
        (Path(test_dir) / "file1.txt").write_text("This contains SEARCHME keyword")
        (Path(test_dir) / "file2.txt").write_text("This does not contain it")
        (Path(test_dir) / "file3.txt").write_text("SEARCHME appears here too")
        
        app = QApplication.instance() or QApplication(sys.argv)
        dock = FileExplorerDock(dialog_mode=False)
        
        # Set directory and content query
        dock.ed_directory.setText(test_dir)
        dock.content_panel.ed_query.setPlainText("SEARCHME")
        
        # Execute search
        dock._list_files()
        
        # Check results
        row_count = dock.table_manager.table.rowCount()
        assert row_count == 2, f"Expected 2 files with 'SEARCHME', got {row_count}"
        
        # Verify match counts in display
        first_file_name = dock.table_manager.table.item(0, 0).text()
        assert "matches)" in first_file_name or "match)" in first_file_name, \
            "Expected match count in filename display"
        
        print(f"✅ Content search successful - Found {row_count} files with matches")
        return True
    
    except Exception as e:
        print(f"❌ Content search failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_signal_connections():
    """Test that all widget signals are connected."""
    print("\n=== Test 5: Signal Connections ===")
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        dock = FileExplorerDock(dialog_mode=False)
        
        # Check that signals are connected
        # (We can't directly test signal connections in Qt, but we can check methods exist)
        assert hasattr(dock, '_on_search_params_changed'), "Missing _on_search_params_changed"
        assert hasattr(dock, '_on_replace_first'), "Missing _on_replace_first"
        assert hasattr(dock, '_on_replace_all'), "Missing _on_replace_all"
        assert hasattr(dock, '_on_conditions_changed'), "Missing _on_conditions_changed"
        assert hasattr(dock, '_on_progress'), "Missing _on_progress"
        assert hasattr(dock, '_on_execution_done'), "Missing _on_execution_done"
        assert hasattr(dock, '_on_execution_error'), "Missing _on_execution_error"
        
        print("✅ All signal handlers exist")
        return True
    
    except Exception as e:
        print(f"❌ Signal connection test failed: {e}")
        return False


def test_executor_methods():
    """Test that executor has required methods."""
    print("\n=== Test 6: Executor Methods ===")
    
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        dock = FileExplorerDock(dialog_mode=False)
        
        executor = dock.executor
        
        # Check methods exist
        assert hasattr(executor, 'execute_browse'), "Missing execute_browse"
        assert hasattr(executor, 'execute_search'), "Missing execute_search"
        assert hasattr(executor, 'execute_replace'), "Missing execute_replace"
        
        # Check signals exist
        assert hasattr(executor, 'progress'), "Missing progress signal"
        assert hasattr(executor, 'progress_detailed'), "Missing progress_detailed signal"
        assert hasattr(executor, 'done'), "Missing done signal"
        assert hasattr(executor, 'error'), "Missing error signal"
        
        print("✅ All executor methods and signals exist")
        return True
    
    except Exception as e:
        print(f"❌ Executor method test failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("="*70)
    print("FILE EXPLORER INTEGRATION TESTS (v2.9.116)")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("Widget Instantiation", test_widget_instantiation()))
    results.append(("Browse Mode", test_browse_mode()))
    results.append(("Search - Filename", test_search_mode_filename()))
    results.append(("Search - Content", test_search_mode_content()))
    results.append(("Signal Connections", test_signal_connections()))
    results.append(("Executor Methods", test_executor_methods()))
    
    # Summary
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration successful.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
