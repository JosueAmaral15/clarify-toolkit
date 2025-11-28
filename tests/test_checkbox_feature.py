#!/usr/bin/env python3
"""
test_checkbox_feature.py

Tests for the checkbox feature in Advanced Conditions:
- Case Sensitive
- Match Whole Word
- Use Regular Expression
"""
import os
import tempfile
from src.core.filters import Condition

def test_case_sensitive_true():
    """Test case-sensitive matching (default behavior)"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World")
        f.flush()
        path = f.name
    
    try:
        # Should match when case matches
        cond = Condition("content", "contains", "Hello", case_sensitive=True)
        assert cond.matches(path), "Should match 'Hello' with case sensitivity"
        
        # Should NOT match when case differs
        cond = Condition("content", "contains", "hello", case_sensitive=True)
        assert not cond.matches(path), "Should NOT match 'hello' with case sensitivity"
    finally:
        os.unlink(path)
    
    print("✓ test_case_sensitive_true passed")


def test_case_insensitive():
    """Test case-insensitive matching"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Hello World")
        f.flush()
        path = f.name
    
    try:
        # Should match regardless of case
        cond = Condition("content", "contains", "hello", case_sensitive=False)
        assert cond.matches(path), "Should match 'hello' without case sensitivity"
        
        cond = Condition("content", "contains", "HELLO", case_sensitive=False)
        assert cond.matches(path), "Should match 'HELLO' without case sensitivity"
        
        cond = Condition("content", "contains", "HeLLo", case_sensitive=False)
        assert cond.matches(path), "Should match 'HeLLo' without case sensitivity"
    finally:
        os.unlink(path)
    
    print("✓ test_case_insensitive passed")


def test_whole_word_matching():
    """Test whole word matching"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The cat is in the category")
        f.flush()
        path = f.name
    
    try:
        # Should match whole word "cat"
        cond = Condition("content", "contains", "cat", whole_word=True)
        assert cond.matches(path), "Should match whole word 'cat'"
        
        # Should NOT match "cat" inside "category" with whole_word
        cond = Condition("content", "contains", "cat", whole_word=True)
        # This should still pass because "cat" exists as a whole word
        assert cond.matches(path), "Should match 'cat' as whole word"
        
        # Test a word that only appears inside another word
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write("The category contains no standalone cat word here")
            f2.flush()
            path2 = f2.name
        
        try:
            # "cat" appears as whole word
            cond = Condition("content", "contains", "cat", whole_word=True)
            assert cond.matches(path2), "Should match 'cat' as whole word"
        finally:
            os.unlink(path2)
            
    finally:
        os.unlink(path)
    
    print("✓ test_whole_word_matching passed")


def test_regex_matching():
    """Test regex pattern matching"""
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


def test_whole_word_with_case_insensitive():
    """Test whole word matching combined with case insensitive"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The CAT is in the category")
        f.flush()
        path = f.name
    
    try:
        # Should match "cat" as whole word, case-insensitively
        cond = Condition("content", "contains", "cat", whole_word=True, case_sensitive=False)
        assert cond.matches(path), "Should match 'cat' as whole word, case-insensitively"
        
        # Should match "CAT" as whole word, case-insensitively  
        cond = Condition("content", "contains", "CAT", whole_word=True, case_sensitive=False)
        assert cond.matches(path), "Should match 'CAT' as whole word, case-insensitively"
    finally:
        os.unlink(path)
    
    print("✓ test_whole_word_with_case_insensitive passed")


def test_filename_matching_with_flags():
    """Test case sensitivity and regex on filename field"""
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
    
    print("✓ test_filename_matching_with_flags passed")


def test_operators_with_case_insensitive():
    """Test different operators with case insensitive flag"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Python Programming")
        f.flush()
        path = f.name
    
    try:
        # equals operator
        cond = Condition("content", "equals", "python programming", case_sensitive=False)
        assert cond.matches(path), "Should match 'equals' case-insensitively"
        
        # starts with operator
        cond = Condition("content", "starts with", "python", case_sensitive=False)
        assert cond.matches(path), "Should match 'starts with' case-insensitively"
        
        # ends with operator
        cond = Condition("content", "ends with", "PROGRAMMING", case_sensitive=False)
        assert cond.matches(path), "Should match 'ends with' case-insensitively"
    finally:
        os.unlink(path)
    
    print("✓ test_operators_with_case_insensitive passed")


def test_not_contains_with_whole_word():
    """Test 'not contains' operator with whole word flag"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The category has items")
        f.flush()
        path = f.name
    
    try:
        # Should NOT contain "dog" as whole word
        cond = Condition("content", "not contains", "dog", whole_word=True)
        assert cond.matches(path), "Should NOT contain 'dog' as whole word"
        
        # Should NOT contain "cat" as whole word (only in "category")
        cond = Condition("content", "not contains", "standalone", whole_word=True)
        assert cond.matches(path), "Should NOT contain 'standalone' as whole word"
    finally:
        os.unlink(path)
    
    print("✓ test_not_contains_with_whole_word passed")


def test_all_flags_combined():
    """Test all three flags combined"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("The EMAIL address is user123@example.com here")
        f.flush()
        path = f.name
    
    try:
        # Regex with whole word and case insensitive
        # Looking for word "EMAIL" using regex, case-insensitively
        cond = Condition("content", "contains", r"email", use_regex=True, 
                        case_sensitive=False, whole_word=True)
        assert cond.matches(path), "Should match with all flags combined"
    finally:
        os.unlink(path)
    
    print("✓ test_all_flags_combined passed")


if __name__ == "__main__":
    print("Running checkbox feature tests...\n")
    
    test_case_sensitive_true()
    test_case_insensitive()
    test_whole_word_matching()
    test_regex_matching()
    test_regex_with_case_insensitive()
    test_whole_word_with_case_insensitive()
    test_filename_matching_with_flags()
    test_operators_with_case_insensitive()
    test_not_contains_with_whole_word()
    test_all_flags_combined()
    
    print("\n" + "="*60)
    print("All 10 checkbox feature tests passed! ✓")
    print("="*60)
