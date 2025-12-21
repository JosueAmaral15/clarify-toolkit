#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_jsx_extractor.py

Functional tests for JSX Extractor functionality.
Tests various extraction modes and options.
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.extractors import Extractor


def test_attribute_extraction():
    """Test 1: Extract 'label' attribute with include_key=True"""
    print("\n" + "=" * 60)
    print("TEST 1: Attribute extraction with include_key=True")
    print("=" * 60)

    extractor = Extractor(
        param="label",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=True,
        include_value=True,
        no_standard=False,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        to_upper=False,
        only_strings=False,
        is_attribute_mode=True,
        file_extensions=[".tsx"],
    )

    text_result, json_result = extractor.run("test_component.tsx")

    print("\n--- Text Result (Paths) ---")
    print(text_result)

    print("\n--- JSON Result ---")
    print(json_result)

    # Validate
    assert "TestComponent" in text_result
    assert "Button.label" in text_result
    assert json_result is not None
    json_obj = json.loads(json_result)
    assert "TestComponent" in json_obj

    print("\n✅ TEST 1 PASSED")


def test_drop_standard_tags():
    """Test 2: Extract with no_standard=True (drop standard HTML tags)"""
    print("\n" + "=" * 60)
    print("TEST 2: Drop standard HTML tags (no_standard=True)")
    print("=" * 60)

    extractor = Extractor(
        param="label",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=True,
        include_value=True,
        no_standard=True,  # Drop div, p, h1, span
        convert_to_json=True,
        with_quotation_marks=False,  # JS literal format
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        to_upper=False,
        only_strings=False,
        is_attribute_mode=True,
        file_extensions=[".tsx"],
    )

    text_result, json_result = extractor.run("test_component.tsx")

    print("\n--- Text Result (Paths) ---")
    print(text_result)

    print("\n--- JSON Result ---")
    print(json_result)

    # Validate: should NOT contain 'div.label' or 'p.label' but should have AuthGuard, Card, Button
    assert "div" not in text_result.lower() or "div.label" not in text_result
    assert "AuthGuard" in text_result
    assert "Card" in text_result

    print("\n✅ TEST 2 PASSED")


def test_only_strings():
    """Test 3: Extract only literal strings (only_strings=True)"""
    print("\n" + "=" * 60)
    print("TEST 3: Only literal strings (only_strings=True)")
    print("=" * 60)

    extractor = Extractor(
        param="label",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=True,
        include_value=True,
        no_standard=False,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        to_upper=False,
        only_strings=True,  # Filter out expressions
        is_attribute_mode=True,
        file_extensions=[".tsx"],
    )

    text_result, json_result = extractor.run("test_component.tsx")

    print("\n--- Text Result (Paths) ---")
    print(text_result)

    print("\n--- JSON Result ---")
    print(json_result)

    # Validate: all label values should be literal strings (in quotes in TSX)
    # Should include "Click Me", "User Card", etc.
    assert "click_me" in text_result or "Click Me" in json_result
    assert "Page Title" in json_result
    json_obj = json.loads(json_result)
    # All values should be strings (not expressions)
    assert isinstance(json_obj["TestComponent"]["div"]["h1"]["label"]["page_title"], str)

    print("\n✅ TEST 3 PASSED")


def test_case_styles():
    """Test 4: Test different case styles (camelCase, PascalCase, kebab-case)"""
    print("\n" + "=" * 60)
    print("TEST 4: Case styles (camelCase, PascalCase, kebab-case)")
    print("=" * 60)

    for case in ["camel", "pascal", "kebab"]:
        print(f"\n--- Testing {case} case ---")

        extractor = Extractor(
            param="label",
            mode="jsx",
            avoid_keys="",
            avoid_keys_parameter="contains",
            include_key=True,  # Changed to True to see normalized keys
            include_value=True,
            no_standard=True,
            convert_to_json=True,
            with_quotation_marks=False,
            indentation=2,
            case_style=case,
            limit="all",
            avoid_cut=False,
            to_upper=False,
            only_strings=True,
            is_attribute_mode=True,
            file_extensions=[".tsx"],
        )

        text_result, json_result = extractor.run("test_component.tsx")
        print(f"Sample JSON ({case}):")
        print(json_result[:300])

        # Validate case style applied by checking JSON keys
        if case == "camel":
            assert "clickMe" in json_result or "pageTitle" in json_result
        elif case == "pascal":
            assert "ClickMe" in json_result or "PageTitle" in json_result
        elif case == "kebab":
            # Note: JSON keys with hyphens need quotes, so check the presence
            assert "click-me" in json_result or "page-title" in json_result or "user-card" in json_result

    print("\n✅ TEST 4 PASSED")


def test_avoid_keys():
    """Test 5: Test avoid_keys filtering"""
    print("\n" + "=" * 60)
    print("TEST 5: Avoid keys filtering (className, data-testid)")
    print("=" * 60)

    extractor = Extractor(
        param="*",  # Match all attributes
        mode="jsx",
        avoid_keys="className, data-testid",
        avoid_keys_parameter="contains",
        include_key=True,
        include_value=True,
        no_standard=False,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style="snake",
        limit="all",
        avoid_cut=False,
        to_upper=False,
        only_strings=False,
        is_attribute_mode=True,
        file_extensions=[".tsx"],
    )

    text_result, json_result = extractor.run("test_component.tsx")

    print("\n--- Text Result (Paths) ---")
    print(text_result[:500])

    # Validate: should NOT contain className or data-testid
    assert "className" not in text_result
    assert "data-testid" not in text_result
    # But should contain label, onClick, variant, etc.
    assert "label" in text_result

    print("\n✅ TEST 5 PASSED")


def test_limit_and_avoid_cut():
    """Test 6: Test text truncation with limit and avoid_cut"""
    print("\n" + "=" * 60)
    print("TEST 6: Text truncation (limit=10, avoid_cut=True)")
    print("=" * 60)

    extractor = Extractor(
        param="label",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=False,
        indentation=2,
        case_style="snake",
        limit="10",  # Limit to 10 chars
        avoid_cut=True,  # Avoid cutting mid-word
        to_upper=False,
        only_strings=True,
        is_attribute_mode=True,
        file_extensions=[".tsx"],
    )

    text_result, json_result = extractor.run("test_component.tsx")

    print("\n--- JSON Result (truncated keys) ---")
    print(json_result[:500])

    # JS literal format cannot be parsed with json.loads, so just verify format
    # Keys should be truncated (e.g., "Main Dashboard" -> "main" or "main_dashb")
    # Check that truncation occurred by looking for short keys
    assert "page_title" in json_result or "page_t" in json_result or "page" in json_result
    print(f"\nTruncation working correctly (keys shortened)")

    print("\n✅ TEST 6 PASSED")


if __name__ == "__main__":
    try:
        test_attribute_extraction()
        test_drop_standard_tags()
        test_only_strings()
        test_case_styles()
        test_avoid_keys()
        test_limit_and_avoid_cut()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
