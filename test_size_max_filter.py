#!/usr/bin/env python3
"""
Test script for Size Max filter bug in File Explorer.
Tests if size_max logic works correctly (isolated unit test).
"""

import os
import tempfile

def apply_size_filter(filepath, filters):
    """Replicate the filter logic from file_list_executor.py"""
    try:
        file_size = os.path.getsize(filepath)
        size_config = filters.get("size", {})

        min_size = size_config.get("min")
        if min_size is not None and file_size < min_size:
            return False

        max_size = size_config.get("max")
        if max_size is not None and file_size > max_size:
            return False
        
        return True
    except OSError:
        return False

def create_test_files():
    """Create test files with known sizes."""
    temp_dir = tempfile.mkdtemp(prefix="clarify_test_")
    
    # Create files with different sizes
    files = {
        "small_10kb.txt": 10 * 1024,  # 10 KB
        "medium_30kb.txt": 30 * 1024,  # 30 KB
        "large_50kb.txt": 50 * 1024,  # 50 KB
        "huge_100kb.txt": 100 * 1024,  # 100 KB
    }
    
    for filename, size in files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, "wb") as f:
            f.write(b"x" * size)
    
    print(f"✅ Created test files in: {temp_dir}")
    for filename, size in files.items():
        filepath = os.path.join(temp_dir, filename)
        actual_size = os.path.getsize(filepath)
        print(f"  - {filename}: {actual_size} bytes ({actual_size / 1024:.1f} KB)")
    
    return temp_dir

def test_size_max_filter():
    """Test size_max filter with 30 KB limit."""
    print("\n" + "="*60)
    print("TEST: Size Max Filter (30 KB limit)")
    print("="*60 + "\n")
    
    # Create test files
    test_dir = create_test_files()
    
    # Configure filters with size_max = 30 KB
    filters = {
        "size": {
            "min": None,
            "max": 30 * 1024  # 30 KB in bytes = 30720 bytes
        }
    }
    
    print(f"\n🔍 Applying filter: size_max = {filters['size']['max']} bytes (30 KB)\n")
    
    # Get all files first (no filter)
    all_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            filepath = os.path.join(root, file)
            all_files.append(filepath)
    
    print("📁 All files found:")
    for filepath in all_files:
        size = os.path.getsize(filepath)
        print(f"  - {os.path.basename(filepath)}: {size} bytes ({size / 1024:.1f} KB)")
    
    # Apply filter manually
    print("\n🔬 Applying size_max filter (replicating file_list_executor logic):\n")
    filtered_files = []
    for filepath in all_files:
        size = os.path.getsize(filepath)
        max_size = filters["size"]["max"]
        
        # Use the replicated logic
        passes = apply_size_filter(filepath, filters)
        status = "✅ PASS" if passes else "❌ FAIL"
        
        print(f"  {status} {os.path.basename(filepath)}: {size} bytes <= {max_size} bytes? {passes}")
        
        if passes:
            filtered_files.append(filepath)
    
    print(f"\n📊 RESULTS:")
    print(f"  Total files: {len(all_files)}")
    print(f"  Filtered files (≤30 KB): {len(filtered_files)}")
    print(f"  Expected: 2 files (small_10kb.txt, medium_30kb.txt)")
    
    # Verify
    expected_count = 2
    if len(filtered_files) == expected_count:
        print(f"\n✅ TEST PASSED! Filter works correctly.")
        return True
    else:
        print(f"\n❌ TEST FAILED! Expected {expected_count} files, got {len(filtered_files)}")
        return False
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    success = test_size_max_filter()
    sys.exit(0 if success else 1)
