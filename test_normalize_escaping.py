#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for normalize_escaping() function (Task #22 - v2.9.10)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rewriter import Obj, normalize_escaping

def test_normalize_escaping():
    """Test escaping normalization."""
    print("=" * 60)
    print("Testing normalize_escaping() (Task #22 - v2.9.10)")
    print("=" * 60)
    
    # Test 1: Excessive escaping with single quotes
    print("\n1. Test excessive escaping (single quotes):")
    test1 = Obj([
        ("key1", "don\\\\'t"),  # Should stay (only 1 backslash)
        ("key2", "don\\\\\\'t"),  # 2 backslashes → normalize to \'
        ("key3", "don\\\\\\\\'t"),  # 3 backslashes → normalize to \'
    ])
    result1 = normalize_escaping(test1)
    for k, v in result1:
        print(f"   {k}: {repr(v)}")
    
    # Test 2: Excessive escaping with double quotes
    print("\n2. Test excessive escaping (double quotes):")
    test2 = Obj([
        ("key1", 'say \\"hi\\"'),  # Should stay (only 1 backslash)
        ("key2", 'say \\\\\\"hi\\\\\\"'),  # 2 backslashes → normalize to \"
        ("key3", 'say \\\\\\\\\\"hi\\\\\\\\\\"'),  # 4 backslashes → normalize to \"
    ])
    result2 = normalize_escaping(test2)
    for k, v in result2:
        print(f"   {k}: {repr(v)}")
    
    # Test 3: Mixed content
    print("\n3. Test mixed content:")
    test3 = Obj([
        ("text", "It\\\\\\'s ok"),
        ("number", 123),
        ("nested", Obj([
            ("message", "don\\\\\\\\'t do that"),
        ])),
        ("array", ["value\\\\\\'1", "value2"])
    ])
    result3 = normalize_escaping(test3)
    print(f"   text: {repr(result3[0][1])}")
    print(f"   number: {result3[1][1]}")
    print(f"   nested.message: {repr(result3[2][1][0][1])}")
    print(f"   array[0]: {repr(result3[3][1][0])}")
    print(f"   array[1]: {repr(result3[3][1][1])}")
    
    # Test 4: No escaping (should remain unchanged)
    print("\n4. Test normal strings (no changes):")
    test4 = Obj([
        ("normal", "just a normal string"),
        ("with_quote", "it's ok"),  # No backslash
        ("with_escaped", "it\\'s ok"),  # Single backslash (valid, keep it)
    ])
    result4 = normalize_escaping(test4)
    for k, v in result4:
        print(f"   {k}: {repr(v)}")
    
    # Test 5: Real-world example
    print("\n5. Real-world example:")
    real_world = Obj([
        ("error", "The user can\\\\\\'t access this page"),
        ("message", 'Click \\\\\\"OK\\\\\\" to continue'),
        ("description", "This is a normal string without issues")
    ])
    result5 = normalize_escaping(real_world)
    for k, v in result5:
        print(f"   {k}: {repr(v)}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_normalize_escaping()
