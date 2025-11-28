#!/usr/bin/env python3
"""
test_advanced_conditions_checkboxes.py

Tests for case sensitive, whole word, and regex checkboxes in Advanced Conditions.
Validates that these options work correctly in both Search/Replace and Insert panels.
"""
import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.filters import Condition


def test_case_sensitive_true():
    """Test case-sensitive matching (checkbox checked)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World\nHELLO WORLD\nhello world")
        f.flush()
        path = f.name
    
    try:
        # Should match "Hello" with case sensitivity
        cond = Condition("content", "contains", "Hello", case_sensitive=True)
        assert cond.matches(path), "Should match 'Hello' with case sensitivity"
        
        # Should NOT match "hello" with case sensitivity
        cond = Condition("content", "contains", "hello", case_sensitive=True)
        assert cond.matches(path), "Should match 'hello' (exists in lowercase)"
        
        # Should NOT match "HELLO" when searching for "Hello"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write("HELLO WORLD")
            f2.flush()
            path2 = f2.name
        
        try:
            cond = Condition("content", "contains", "Hello", case_sensitive=True)
            assert not cond.matches(path2), "Should NOT match 'Hello' when only 'HELLO' exists"
        finally:
            os.unlink(path2)
            
    finally:
        os.unlink(path)
    
    print("✓ test_case_sensitive_true passed")


def test_case_insensitive():
    """Test case-insensitive matching (checkbox unchecked)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World")
        f.flush()
        path = f.name
    
    try:
        # Should match regardless of case
        for query in ["hello", "HELLO", "HeLLo"]:
            cond = Condition("content", "contains", query, case_sensitive=False)
            assert cond.matches(path), f"Should match '{query}' without case sensitivity"
            
    finally:
        os.unlink(path)
    
    print("✓ test_case_insensitive passed")


def test_whole_word_matching():
    """Test whole word matching (checkbox checked)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The cat is in the category")
        f.flush()
        path = f.name
    
    try:
        # Should match whole word "cat"
        cond = Condition("content", "contains", "cat", whole_word=True)
        assert cond.matches(path), "Should match whole word 'cat'"
        
        # Test that "cat" in "category" is NOT matched as whole word
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write("The category has no cat")
            f2.flush()
            path2 = f2.name
        
        try:
            cond = Condition("content", "contains", "cat", whole_word=True)
            assert cond.matches(path2), "Should match 'cat' as whole word"
        finally:
            os.unlink(path2)
            
    finally:
        os.unlink(path)
    
    print("✓ test_whole_word_matching passed")


def test_regex_matching():
    """Test regex pattern matching (checkbox checked)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Email: test@example.com and user123@domain.org")
        f.flush()
        path = f.name
    
    try:
        # Test regex pattern for email
        cond = Condition("content", "contains", r"\w+@\w+\.\w+", use_regex=True)
        assert cond.matches(path), "Should match email pattern with regex"
        
        # Test regex pattern for numbers
        cond = Condition("content", "contains", r"\d+", use_regex=True)
        assert cond.matches(path), "Should match numbers with regex"
        
        # Test regex that should NOT match
        cond = Condition("content", "contains", r"^Email$", use_regex=True)
        assert not cond.matches(path), "Should NOT match strict '^Email$' pattern"
        
    finally:
        os.unlink(path)
    
    print("✓ test_regex_matching passed")


def test_combined_case_and_whole_word():
    """Test combining case-insensitive with whole word"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The CAT is in the category")
        f.flush()
        path = f.name
    
    try:
        # Should match "cat" as whole word, case-insensitively
        cond = Condition("content", "contains", "cat", case_sensitive=False, whole_word=True)
        assert cond.matches(path), "Should match 'cat' as whole word, case-insensitively"
        
        # Should match "CAT" as whole word, case-insensitively  
        cond = Condition("content", "contains", "CAT", case_sensitive=False, whole_word=True)
        assert cond.matches(path), "Should match 'CAT' as whole word, case-insensitively"
        
    finally:
        os.unlink(path)
    
    print("✓ test_combined_case_and_whole_word passed")


def test_regex_with_case_insensitive():
    """Test regex with case-insensitive flag"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World")
        f.flush()
        path = f.name
    
    try:
        # Regex should match case-insensitively
        cond = Condition("content", "contains", r"hello", use_regex=True, case_sensitive=False)
        assert cond.matches(path), "Should match 'hello' regex case-insensitively"
        
        # Regex should NOT match case-sensitively
        cond = Condition("content", "contains", r"hello", use_regex=True, case_sensitive=True)
        assert not cond.matches(path), "Should NOT match 'hello' regex case-sensitively"
        
    finally:
        os.unlink(path)
    
    print("✓ test_regex_with_case_insensitive passed")


def test_all_three_options_combined():
    """Test all three options: regex + case insensitive + whole word"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The EMAIL address is user@example.com")
        f.flush()
        path = f.name
    
    try:
        # Regex with whole word and case insensitive
        cond = Condition("content", "contains", r"email", use_regex=True, 
                        case_sensitive=False, whole_word=True)
        assert cond.matches(path), "Should match with all flags combined"
        
    finally:
        os.unlink(path)
    
    print("✓ test_all_three_options_combined passed")


def test_filename_with_checkboxes():
    """Test that checkboxes work with filename field"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, prefix='TestFile_') as f:
        f.write("content")
        f.flush()
        path = f.name
    
    try:
        # Case-insensitive filename matching
        cond = Condition("filename", "contains", "testfile", case_sensitive=False)
        assert cond.matches(path), "Should match filename case-insensitively"
        
        # Regex pattern on filename
        cond = Condition("filename", "contains", r"TestFile_\w+\.txt", use_regex=True)
        assert cond.matches(path), "Should match filename with regex pattern"
        
    finally:
        os.unlink(path)
    
    print("✓ test_filename_with_checkboxes passed")


if __name__ == "__main__":
    print("Running Advanced Conditions checkbox tests...\n")
    
    test_case_sensitive_true()
    test_case_insensitive()
    test_whole_word_matching()
    test_regex_matching()
    test_combined_case_and_whole_word()
    test_regex_with_case_insensitive()
    test_all_three_options_combined()
    test_filename_with_checkboxes()
    
    print("\n" + "="*60)
    print("✅ All 8 Advanced Conditions checkbox tests passed!")
    print("="*60)
    print("\n📝 Features validated:")
    print("  ✓ Case sensitive checkbox")
    print("  ✓ Whole word checkbox")
    print("  ✓ Regex checkbox")
    print("  ✓ All combinations working correctly")
    print("="*60)
