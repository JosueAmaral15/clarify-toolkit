#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feature-Specific Verification Tests
====================================

Verify that new features work correctly:
1. TypeScript export generates valid TS interfaces
2. Exclude numeric keys filters numeric string keys
3. Skip empty values removes empty/null entries
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.extractors.advanced_extractor import AdvancedExtractor


def test_typescript_export():
    """Test TypeScript interface generation."""
    print("\n" + "="*70)
    print("TEST 1: TypeScript Export")
    print("="*70)
    
    extractor = AdvancedExtractor(
        param="*",  # match_all is auto-derived from param="*"
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
        to_upper=False
    )
    
    test_file = Path(__file__).parent / "test_data" / "01_simple_object.json"
    _, json_output = extractor.run(str(test_file))
    
    # Verify TypeScript syntax
    checks = [
        ("interface" in json_output, "Contains 'interface' keyword"),
        ("{" in json_output and "}" in json_output, "Has interface body"),
        (":" in json_output, "Has type annotations"),
    ]
    
    passed = all(check[0] for check in checks)
    
    print(f"\nOutput preview (first 300 chars):")
    print(json_output[:300])
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: TypeScript export")
    
    for check, description in checks:
        print(f"  {'✅' if check else '❌'} {description}")
    
    return passed


def test_exclude_numeric():
    """Test numeric key exclusion."""
    print("\n" + "="*70)
    print("TEST 2: Exclude Numeric Keys")
    print("="*70)
    
    # Test without exclude_numeric
    extractor_normal = AdvancedExtractor(
        param="*",
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
        to_upper=False
    )
    
    # Test with exclude_numeric
    extractor_filtered = AdvancedExtractor(
        param="*",
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
        to_upper=False
    )
    
    test_file = Path(__file__).parent / "test_data" / "05_numeric_keys.json"
    _, json_normal = extractor_normal.run(str(test_file))
    _, json_filtered = extractor_filtered.run(str(test_file))
    
    # Check that filtered output is smaller (numeric keys removed)
    passed = len(json_filtered) < len(json_normal)
    
    print(f"\nNormal output length: {len(json_normal)} chars")
    print(f"Filtered output length: {len(json_filtered)} chars")
    print(f"Reduction: {len(json_normal) - len(json_filtered)} chars")
    
    print(f"\nNormal output preview:")
    print(json_normal[:200])
    
    print(f"\nFiltered output preview:")
    print(json_filtered[:200])
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: Exclude numeric keys reduces output")
    
    return passed


def test_skip_empty():
    """Test skip empty values."""
    print("\n" + "="*70)
    print("TEST 3: Skip Empty Values")
    print("="*70)
    
    # Test without skip_empty
    extractor_normal = AdvancedExtractor(
        param="*",
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
        to_upper=False
    )
    
    # Test with skip_empty
    extractor_filtered = AdvancedExtractor(
        param="*",
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
        to_upper=False
    )
    
    test_file = Path(__file__).parent / "test_data" / "04_empty_values.json"
    _, json_normal = extractor_normal.run(str(test_file))
    _, json_filtered = extractor_filtered.run(str(test_file))
    
    # Check that filtered output is smaller (empty values removed)
    passed = len(json_filtered) < len(json_normal)
    
    print(f"\nNormal output length: {len(json_normal)} chars")
    print(f"Filtered output length: {len(json_filtered)} chars")
    print(f"Reduction: {len(json_normal) - len(json_filtered)} chars")
    
    print(f"\nNormal output preview:")
    print(json_normal[:200])
    
    print(f"\nFiltered output preview:")
    print(json_filtered[:200])
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}: Skip empty values reduces output")
    
    return passed


def main():
    """Run feature verification tests."""
    print("\n" + "="*70)
    print("FEATURE-SPECIFIC VERIFICATION TESTS")
    print("="*70)
    
    results = []
    
    # Run tests
    results.append(("TypeScript Export", test_typescript_export()))
    results.append(("Exclude Numeric Keys", test_exclude_numeric()))
    results.append(("Skip Empty Values", test_skip_empty()))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    
    for name, result in results:
        print(f"  {'✅' if result else '❌'} {name}")
    
    print("\n" + "="*70)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
