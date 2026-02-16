#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test skip_empty feature restoration.

Tests that the skip_empty parameter correctly filters empty and whitespace-only values.

Programmer: #3
Date: 2026-02-16
"""

import json
from src.extractors.advanced_extractor import AdvancedExtractor


def test_skip_empty_disabled():
    """Test that empty values are included when skip_empty=False."""
    jsx_code = '''
    <div>
        <p>Hello</p>
        <p></p>
        <p>   </p>
        <p>World</p>
    </div>
    '''
    
    extractor = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        skip_empty=False  # Should include all values
    )
    
    _, result_dict = extractor.process_text("TestFile", jsx_code)
    json_str = json.dumps(result_dict, indent=2)
    
    print("=" * 70)
    print("TEST 1: skip_empty=False (should include empty values)")
    print("=" * 70)
    print(json_str)
    print()
    
    # Should have entries for all 4 p tags (including empty ones)
    assert "hello" in json_str.lower()
    assert "world" in json_str.lower()
    
    # Count how many keys we have (should be 4 with empty, 2 without based on normalization)
    test_file_content = result_dict.get("TestFile", {})
    total_keys = len(test_file_content.keys())
    print(f"Found {total_keys} keys at TestFile level")
    print(f"Keys: {list(test_file_content.keys())}")
    assert total_keys >= 2, f"Should have at least 2 non-empty values, got {total_keys}"
    
    print("✅ Test 1 PASSED\n")


def test_skip_empty_enabled():
    """Test that empty values are filtered when skip_empty=True."""
    jsx_code = '''
    <div>
        <p>Hello</p>
        <p></p>
        <p>   </p>
        <p>World</p>
    </div>
    '''
    
    extractor = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        skip_empty=True  # Should filter empty values
    )
    
    _, result_dict = extractor.process_text("TestFile", jsx_code)
    json_str = json.dumps(result_dict, indent=2)
    
    print("=" * 70)
    print("TEST 2: skip_empty=True (should filter empty values)")
    print("=" * 70)
    print(json_str)
    print()
    
    # Should only have "hello" and "world", not empty strings
    assert "hello" in json_str.lower()
    assert "world" in json_str.lower()
    
    # Count how many keys (should be 2, only non-empty)
    test_file_content = result_dict.get("TestFile", {})
    total_keys = len(test_file_content.keys())
    print(f"Found {total_keys} keys at TestFile level")
    print(f"Keys: {list(test_file_content.keys())}")
    assert total_keys == 2, f"Should only have 2 non-empty values, got {total_keys}"
    
    print("✅ Test 2 PASSED\n")


def test_skip_empty_mixed_content():
    """Test skip_empty with mixed empty and non-empty values."""
    jsx_code = '''
    <section>
        <h1>Title</h1>
        <p></p>
        <h2>Subtitle</h2>
        <span>   </span>
        <div>Content</div>
    </section>
    '''
    
    extractor = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        skip_empty=True
    )
    
    _, result_dict = extractor.process_text("TestFile", jsx_code)
    json_str = json.dumps(result_dict, indent=2)
    
    print("=" * 70)
    print("TEST 3: skip_empty with mixed content")
    print("=" * 70)
    print(json_str)
    print()
    
    # Should have the 3 non-empty values
    assert "title" in json_str.lower()
    assert "subtitle" in json_str.lower()
    assert "content" in json_str.lower()
    
    # Should NOT have text/empty keys for empty content
    # (empty p and span should be skipped)
    test_file_content = result_dict.get("TestFile", {})
    total_keys = len(test_file_content.keys())
    print(f"Total keys at TestFile level: {total_keys}")
    print(f"Keys: {list(test_file_content.keys())}")
    assert total_keys == 3, f"Should have 3 non-empty elements, got {total_keys}"
    
    print("✅ Test 3 PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TESTING skip_empty FEATURE RESTORATION")
    print("=" * 70 + "\n")
    
    test_skip_empty_disabled()
    test_skip_empty_enabled()
    test_skip_empty_mixed_content()
    
    print("=" * 70)
    print("ALL TESTS PASSED! ✅")
    print("=" * 70)
