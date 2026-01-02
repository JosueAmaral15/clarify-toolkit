#!/usr/bin/env python3
"""
Test Advanced Filters in File Explorer - Size Max Bug Fix

Tests the fix for commit 770c508:
- ConditionsGrid now returns technical field names ("size" not "Tamanho")
- Early/late condition separation works correctly
- Size max filter actually filters files

Author: GitHub Copilot (after user feedback)
Date: 2026-01-02
"""

import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.file_explorer_executor import UnifiedFileExplorerExecutor
from src.core.file_list_executor import FileInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


def create_test_files(test_dir: Path) -> list:
    """Create test files with different sizes."""
    test_files = []
    
    # Small files (< 30 KB)
    for i in range(3):
        file_path = test_dir / f"small_{i}.txt"
        file_path.write_text("x" * (10 * 1024))  # 10 KB
        test_files.append(("small", file_path, 10))
    
    # Medium files (~30 KB, exactly at limit)
    file_path = test_dir / "medium_30kb.txt"
    file_path.write_text("x" * (30 * 1024))  # Exactly 30 KB
    test_files.append(("medium", file_path, 30))
    
    # Large files (> 30 KB)
    for i in range(3):
        file_path = test_dir / f"large_{i}.txt"
        file_path.write_text("x" * (50 * 1024 + i * 1024))  # 50+ KB
        test_files.append(("large", file_path, 50 + i))
    
    # HTML files with "html" content (for content search)
    for i in range(2):
        file_path = test_dir / f"page_{i}.html"
        content = "<html><body>Test content html</body></html>"
        file_path.write_text(content * 100)  # ~3 KB
        test_files.append(("html_small", file_path, 3))
    
    # Large HTML (> 30 KB)
    file_path = test_dir / "large_page.html"
    content = "<html><body>Test content html</body></html>" * 1000
    file_path.write_text(content)  # ~40 KB
    test_files.append(("html_large", file_path, 40))
    
    return test_files


def test_conditions_grid_field_names():
    """Test 1: ConditionsGrid returns technical field names."""
    print("\n" + "=" * 70)
    print("TEST 1: ConditionsGrid Field Names (Unit Test)")
    print("=" * 70)
    
    try:
        from PySide6.QtWidgets import QApplication
        from src.gui.widgets.search_widgets import ConditionsGrid
        
        # Create Qt app (required for widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create widget
        grid = ConditionsGrid()
        
        # Add a row and simulate user selecting "Size"
        grid.add_condition_row()
        row = grid.condition_rows[0]
        
        # Set size field (index 3)
        row['field'].setCurrentIndex(3)  # Size
        row['value'].setText("30")
        
        # Get conditions
        conditions = grid.get_conditions()
        
        # Verify
        assert len(conditions) == 1, f"Expected 1 condition, got {len(conditions)}"
        
        field = conditions[0]['field']
        print(f"✓ Condition field: '{field}'")
        
        assert field == "size", f"❌ FAIL: Expected 'size', got '{field}'"
        print("✅ PASS: Field name is technical ('size') not translated")
        
        # Test all fields
        field_map = {
            0: "filename",
            1: "path", 
            2: "ext",
            3: "size",
            4: "mtime",
            5: "content"
        }
        
        all_correct = True
        for idx, expected_field in field_map.items():
            row['field'].setCurrentIndex(idx)
            conds = grid.get_conditions()
            if conds:
                actual = conds[0]['field']
                if actual != expected_field:
                    print(f"❌ Index {idx}: Expected '{expected_field}', got '{actual}'")
                    all_correct = False
                else:
                    print(f"✓ Index {idx}: '{expected_field}' ✓")
        
        if all_correct:
            print("✅ ALL FIELDS PASS: Technical names used correctly")
            return True
        else:
            print("❌ SOME FIELDS FAILED")
            return False
            
    except ImportError as e:
        print(f"⚠️  SKIP: PySide6 not available ({e})")
        return None
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_size_filter_integration():
    """Test 2: Size filter works end-to-end."""
    print("\n" + "=" * 70)
    print("TEST 2: Size Max Filter (Integration Test)")
    print("=" * 70)
    
    # Create test directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_dir = Path(tmp_dir)
        print(f"Test directory: {test_dir}")
        
        # Create test files
        test_files = create_test_files(test_dir)
        print(f"✓ Created {len(test_files)} test files")
        
        # Count files by size
        small_count = sum(1 for cat, _, _ in test_files if cat in ["small", "html_small"])
        large_count = sum(1 for cat, _, _ in test_files if cat in ["large", "html_large"])
        print(f"  - Small files (< 30 KB): {small_count}")
        print(f"  - Large files (> 30 KB): {large_count}")
        print(f"  - At limit (= 30 KB): 1")
        
        # Test 1: Browse without filters
        print("\n--- Test 2a: Browse (no filters) ---")
        executor = UnifiedFileExplorerExecutor()
        result = executor.execute_browse(
            directory=str(test_dir),
            show_hidden=False,
            recursive=False,
            filters={}
        )
        
        total_files = len(result['files'])
        print(f"✓ Found {total_files} files (expected {len(test_files)})")
        assert total_files == len(test_files), f"Expected {len(test_files)}, got {total_files}"
        
        # Test 2: Search with size condition (< 30 KB)
        print("\n--- Test 2b: Search with size < 30 KB ---")
        conditions = [
            {
                'field': 'size',  # Technical name!
                'operator': '<',
                'value': str(30 * 1024),  # 30 KB in bytes
                'case_sensitive': False,
                'regex': False
            }
        ]
        
        result = executor.execute_search(
            directory=str(test_dir),
            filename_pattern=None,
            content_query=None,  # No content search
            search_options={},
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions,
            logic_operator="AND"
        )
        
        found_files = len(result['files'])
        print(f"✓ Found {found_files} files after size filter")
        print(f"  Expected: {small_count} (files < 30 KB)")
        
        # Verify all found files are < 30 KB
        all_small = True
        for search_result in result['files']:
            file_size = search_result.file_info.size
            file_name = search_result.file_info.name
            size_kb = file_size / 1024
            
            if file_size >= 30 * 1024:
                print(f"❌ File too large: {file_name} ({size_kb:.1f} KB)")
                all_small = False
            else:
                print(f"✓ {file_name}: {size_kb:.1f} KB ✓")
        
        if all_small and found_files == small_count:
            print(f"✅ PASS: Size filter works correctly ({found_files}/{small_count} files)")
            return True
        else:
            print(f"❌ FAIL: Expected {small_count} files, got {found_files}")
            return False


def test_size_filter_with_content():
    """Test 3: Size filter + content search (early vs late conditions)."""
    print("\n" + "=" * 70)
    print("TEST 3: Size Filter + Content Search (Early/Late Separation)")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_dir = Path(tmp_dir)
        
        # Create test files
        test_files = create_test_files(test_dir)
        print(f"✓ Created {len(test_files)} test files")
        
        # Count HTML files < 30 KB
        html_small_count = sum(1 for cat, _, _ in test_files if cat == "html_small")
        print(f"  - Small HTML files (< 30 KB): {html_small_count}")
        
        # Test: size < 30 KB AND content contains "html"
        print("\n--- Test 3: size < 30 KB AND content='html' ---")
        
        conditions = [
            {
                'field': 'size',  # Early condition
                'operator': '<',
                'value': str(30 * 1024),
                'case_sensitive': False,
                'regex': False
            }
        ]
        
        executor = UnifiedFileExplorerExecutor()
        result = executor.execute_search(
            directory=str(test_dir),
            filename_pattern=None,
            content_query="html",  # Content search
            search_options={'case_sensitive': False, 'whole_word': False, 'regex': False},
            show_hidden=False,
            recursive=False,
            filters={},
            conditions=conditions,
            logic_operator="AND"
        )
        
        found_files = len(result['files'])
        print(f"✓ Found {found_files} files")
        print(f"  Expected: {html_small_count} (small HTML files)")
        
        # Verify results
        all_correct = True
        for search_result in result['files']:
            file_info = search_result.file_info
            file_name = file_info.name
            file_size = file_info.size
            size_kb = file_size / 1024
            
            # Check size
            if file_size >= 30 * 1024:
                print(f"❌ File too large: {file_name} ({size_kb:.1f} KB)")
                all_correct = False
            
            # Check content matches
            if not search_result.matches:
                print(f"❌ No matches in: {file_name}")
                all_correct = False
            else:
                print(f"✓ {file_name}: {size_kb:.1f} KB, {len(search_result.matches)} matches ✓")
        
        if all_correct and found_files == html_small_count:
            print(f"✅ PASS: Size + Content filter work together ({found_files}/{html_small_count})")
            return True
        else:
            print(f"❌ FAIL: Expected {html_small_count} files, got {found_files}")
            return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("ADVANCED FILTERS TEST SUITE")
    print("Testing commit 770c508 (Size Max Bug Fix)")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Unit test (ConditionsGrid)
    result = test_conditions_grid_field_names()
    results['Unit Test'] = result
    
    # Test 2: Integration test (size filter only)
    result = test_size_filter_integration()
    results['Size Filter'] = result
    
    # Test 3: Integration test (size + content)
    result = test_size_filter_with_content()
    results['Size + Content'] = result
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total = len([r for r in results.values() if r is not None])
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result is True else ("❌ FAIL" if result is False else "⚠️  SKIP")
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {total + skipped} tests")
    print(f"Passed: {passed}/{total} ({100*passed//total if total > 0 else 0}%)")
    print(f"Failed: {failed}/{total}")
    print(f"Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    elif failed > 0:
        print("\n❌ SOME TESTS FAILED")
        return 1
    else:
        print("\n⚠️  NO TESTS RAN")
        return 2


if __name__ == "__main__":
    sys.exit(main())
