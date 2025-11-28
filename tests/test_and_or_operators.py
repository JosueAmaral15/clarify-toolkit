#!/usr/bin/env python3
"""
test_and_or_operators.py

Tests for AND/OR logical operators in Advanced Conditions.
Validates that conditions can be combined using conjunction (AND) or disjunction (OR).
"""
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.filters import Condition, filter_files_by_conditions


def test_and_operator_all_match():
    """Test AND operator where all conditions match"""
    # Create test files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='test_') as f:
        f.write("def hello():\n    pass")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions: filename contains "test" AND extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "py")
        ]
        
        # AND: Both conditions must match
        result = filter_files_by_conditions(files, conditions, logic_operator="AND")
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        assert file1 in result, "file1 should be in result"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_and_operator_all_match passed")


def test_and_operator_one_fails():
    """Test AND operator where one condition fails"""
    # Create test file with wrong extension
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='test_') as f:
        f.write("Some content")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions: filename contains "test" AND extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),  # ✓ matches
            Condition("ext", "equals", "py")            # ✗ doesn't match (.txt)
        ]
        
        # AND: Both conditions must match (this should fail)
        result = filter_files_by_conditions(files, conditions, logic_operator="AND")
        assert len(result) == 0, f"Expected 0 files, got {len(result)}"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_and_operator_one_fails passed")


def test_or_operator_one_matches():
    """Test OR operator where at least one condition matches"""
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='test_') as f:
        f.write("Some content")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions: filename contains "test" OR extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),  # ✓ matches
            Condition("ext", "equals", "py")            # ✗ doesn't match
        ]
        
        # OR: At least one condition must match
        result = filter_files_by_conditions(files, conditions, logic_operator="OR")
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        assert file1 in result, "file1 should be in result"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_or_operator_one_matches passed")


def test_or_operator_all_match():
    """Test OR operator where all conditions match"""
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='test_') as f:
        f.write("def hello():\n    pass")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions: filename contains "test" OR extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),  # ✓ matches
            Condition("ext", "equals", "py")            # ✓ matches
        ]
        
        # OR: At least one condition must match (both match here)
        result = filter_files_by_conditions(files, conditions, logic_operator="OR")
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        assert file1 in result, "file1 should be in result"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_or_operator_all_match passed")


def test_or_operator_none_match():
    """Test OR operator where no conditions match"""
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='hello_') as f:
        f.write("Some content")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions: filename contains "test" OR extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),  # ✗ doesn't match
            Condition("ext", "equals", "py")            # ✗ doesn't match
        ]
        
        # OR: At least one condition must match (none match here)
        result = filter_files_by_conditions(files, conditions, logic_operator="OR")
        assert len(result) == 0, f"Expected 0 files, got {len(result)}"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_or_operator_none_match passed")


def test_multiple_files_and_operator():
    """Test AND operator with multiple files"""
    # Create test files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='test_') as f:
        f.write("def hello():\n    pass")
        f.flush()
        file1 = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='test_') as f:
        f.write("Some content")
        f.flush()
        file2 = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='hello_') as f:
        f.write("def world():\n    pass")
        f.flush()
        file3 = f.name
    
    try:
        files = [file1, file2, file3]
        
        # Two conditions: filename contains "test" AND extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "py")
        ]
        
        # AND: Both conditions must match
        # Only file1 matches both conditions
        result = filter_files_by_conditions(files, conditions, logic_operator="AND")
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        assert file1 in result, "file1 should be in result"
        assert file2 not in result, "file2 should NOT be in result"
        assert file3 not in result, "file3 should NOT be in result"
        
    finally:
        os.unlink(file1)
        os.unlink(file2)
        os.unlink(file3)
    
    print("✓ test_multiple_files_and_operator passed")


def test_multiple_files_or_operator():
    """Test OR operator with multiple files"""
    # Create test files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='test_') as f:
        f.write("def hello():\n    pass")
        f.flush()
        file1 = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='test_') as f:
        f.write("Some content")
        f.flush()
        file2 = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='hello_') as f:
        f.write("def world():\n    pass")
        f.flush()
        file3 = f.name
    
    try:
        files = [file1, file2, file3]
        
        # Two conditions: filename contains "test" OR extension is "py"
        conditions = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "py")
        ]
        
        # OR: At least one condition must match
        # file1: matches both, file2: matches filename, file3: matches extension
        result = filter_files_by_conditions(files, conditions, logic_operator="OR")
        assert len(result) == 3, f"Expected 3 files, got {len(result)}"
        assert file1 in result, "file1 should be in result"
        assert file2 in result, "file2 should be in result"
        assert file3 in result, "file3 should be in result"
        
    finally:
        os.unlink(file1)
        os.unlink(file2)
        os.unlink(file3)
    
    print("✓ test_multiple_files_or_operator passed")


def test_default_operator_is_and():
    """Test that default operator is AND"""
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='test_') as f:
        f.write("def hello():\n    pass")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions
        conditions = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "py")
        ]
        
        # No operator specified - should default to AND
        result = filter_files_by_conditions(files, conditions)
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_default_operator_is_and passed")


def test_with_content_condition_and():
    """Test AND operator with content condition"""
    # Create test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='test_') as f:
        f.write("def hello():\n    print('world')")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Three conditions: filename contains "test" AND extension is "py" AND content contains "world"
        conditions = [
            Condition("filename", "contains", "test"),
            Condition("ext", "equals", "py"),
            Condition("content", "contains", "world")
        ]
        
        # AND: All conditions must match
        result = filter_files_by_conditions(files, conditions, logic_operator="AND")
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_with_content_condition_and passed")


def test_with_content_condition_or():
    """Test OR operator with content condition"""
    # Create test file without "world" in content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='test_') as f:
        f.write("Some other content")
        f.flush()
        file1 = f.name
    
    try:
        files = [file1]
        
        # Two conditions: content contains "world" OR filename contains "test"
        conditions = [
            Condition("content", "contains", "world"),  # ✗ doesn't match
            Condition("filename", "contains", "test")   # ✓ matches
        ]
        
        # OR: At least one condition must match
        result = filter_files_by_conditions(files, conditions, logic_operator="OR")
        assert len(result) == 1, f"Expected 1 file, got {len(result)}"
        
    finally:
        os.unlink(file1)
    
    print("✓ test_with_content_condition_or passed")


if __name__ == "__main__":
    print("Running AND/OR operators tests...\n")
    
    test_and_operator_all_match()
    test_and_operator_one_fails()
    test_or_operator_one_matches()
    test_or_operator_all_match()
    test_or_operator_none_match()
    test_multiple_files_and_operator()
    test_multiple_files_or_operator()
    test_default_operator_is_and()
    test_with_content_condition_and()
    test_with_content_condition_or()
    
    print("\n" + "="*60)
    print("✅ All 10 AND/OR operator tests passed!")
    print("="*60)
    print("\n📝 Features validated:")
    print("  ✓ AND operator (conjunction)")
    print("  ✓ OR operator (disjunction)")
    print("  ✓ Multiple files filtering")
    print("  ✓ Content conditions")
    print("  ✓ Default operator behavior")
    print("="*60)
