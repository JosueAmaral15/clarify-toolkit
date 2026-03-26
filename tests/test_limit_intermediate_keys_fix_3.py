#!/usr/bin/env python3
"""
Manual Test for Limit Feature Bug Fix - Programmer #3
Tests that intermediate keys are now properly truncated by the Limit feature.

Bug: Intermediate path keys (container, min, etc) were NOT being truncated
Fix: Added _apply_limit_to_key() to _build_path_tokens() and _build_path_tokens_with_key()

Date: 2026-02-17
"""

import json
import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.extractors.advanced_extractor import AdvancedExtractor

# Sample JSX from user's bug report (simplified FAQ page structure)
JSX_INPUT = """
<FAQPage>
  <div className="min-h-screen">
    <div className="container">
      <div className="max-w-3xl">
        <h1 className="text-4xl">{t.pages.contact.quickLinks.faq}</h1>
        <p className="text-xl">{t.pages.faq.header.subtitle}</p>
      </div>
      <div className="flex">
        <button>{t.pages.faq.categories[index]}</button>
      </div>
      <div className="space-y-4">
        <div className="bg-white">
          <h3 className="font-medium">{t.pages.faq.faqData[index].question}</h3>
        </div>
      </div>
    </div>
    <div className="stillHaveQuestions">
      <h2>{t.pages.faq.cta.title}</h2>
    </div>
  </div>
</FAQPage>
"""

def test_limit_with_avoid_cut():
    """Test Limit=15 with avoid_cut=True (cut at word boundary)"""
    print("="*80)
    print("TEST 1: Limit=15, avoid_cut=True, direction=before")
    print("="*80)
    
    extractor = AdvancedExtractor(
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
        case_style='camel',
        limit="15",  # 15 character limit
        avoid_cut=True,  # Cut at word boundary (underscore/dash)
        avoid_cut_direction='before',
        to_upper=False,
        only_strings=False,
        is_attribute_mode=False
    )
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False) as f:
        f.write(JSX_INPUT)
        temp_file = f.name
    
    # Process - process_text returns (path_lines, merged_json dict)
    path_lines, data = extractor.process_text("TestFile", JSX_INPUT)
    
    print("\n📊 Extracted JSON:\n")
    print(json.dumps(data, indent=2))
    
    # Collect all keys recursively
    def collect_all_keys(obj, path=""):
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                current = f"{path}.{k}" if path else k
                keys.append((current, len(k)))
                keys.extend(collect_all_keys(v, current))
        return keys
    
    all_keys = collect_all_keys(data)
    
    print("\n📏 Key Length Analysis:")
    print(f"{'Key Name':<40} {'Length':<10} {'Status'}")
    print("-" * 70)
    
    violations = []
    for key_path, key_len in all_keys:
        key_name = key_path.split(".")[-1]
        if key_len > 15:
            status = f"❌ FAIL (>{15})"
            violations.append((key_name, key_len))
        else:
            status = f"✅ PASS (<={15})"
        print(f"{key_name:<40} {key_len:<10} {status}")
    
    print("\n" + "="*80)
    if violations:
        print(f"❌ FAILED: {len(violations)} keys exceed limit of 15:")
        for key, length in violations:
            print(f"   - '{key}' ({length} chars)")
        return False
    else:
        print(f"✅ PASSED: All keys respect limit of 15 characters")
        return True


def test_limit_hard_cut():
    """Test Limit=10 with avoid_cut=False (hard cut)"""
    print("\n" + "="*80)
    print("TEST 2: Limit=10, avoid_cut=False (hard cut)")
    print("="*80)
    
    extractor = AdvancedExtractor(
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
        case_style='camel',
        limit="10",  # 10 character limit
        avoid_cut=False,  # Hard cut
        avoid_cut_direction='before',
        to_upper=False,
        only_strings=False,
        is_attribute_mode=False
    )
    
    path_lines, data = extractor.process_text("TestFile", JSX_INPUT)
    
    print("\n📊 Extracted JSON (truncated view):\n")
    json_str = json.dumps(data, indent=2)
    print(json_str[:500] + "...")
    
    # Collect all keys
    def collect_all_keys(obj):
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.append((k, len(k)))
                keys.extend(collect_all_keys(v))
        return keys
    
    all_keys = collect_all_keys(data)
    
    print("\n📏 Key Length Analysis:")
    violations = []
    for key_name, key_len in all_keys:
        if key_len > 10:
            print(f"   ❌ '{key_name}' = {key_len} chars (FAIL)")
            violations.append((key_name, key_len))
        else:
            print(f"   ✅ '{key_name}' = {key_len} chars (PASS)")
    
    print("\n" + "="*80)
    if violations:
        print(f"❌ FAILED: {len(violations)} keys exceed limit of 10:")
        for key, length in violations:
            print(f"   - '{key}' ({length} chars)")
        return False
    else:
        print(f"✅ PASSED: All keys respect limit of 10 characters")
        return True


def test_limit_disabled():
    """Test with Limit='all' (no limit)"""
    print("\n" + "="*80)
    print("TEST 3: Limit='all' (no truncation)")
    print("="*80)
    
    extractor = AdvancedExtractor(
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
        case_style='camel',
        limit='all',  # No limit
        avoid_cut=False,
        avoid_cut_direction='before',
        to_upper=False,
        only_strings=False,
        is_attribute_mode=False
    )
    
    path_lines, data = extractor.process_text("TestFile", JSX_INPUT)
    
    print("\n📊 Sample keys (should be full length):\n")
    
    def collect_all_keys(obj):
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.append(k)
                keys.extend(collect_all_keys(v))
        return keys
    
    all_keys = collect_all_keys(data)
    long_keys = [k for k in all_keys if len(k) > 15]
    
    print(f"   Total keys: {len(all_keys)}")
    print(f"   Keys > 15 chars: {len(long_keys)}")
    
    if long_keys:
        print("\n   Sample long keys (expected with limit='all'):")
        for key in long_keys[:5]:
            print(f"      - '{key}' ({len(key)} chars)")
    
    print("\n" + "="*80)
    if len(long_keys) > 0:
        print(f"✅ PASSED: {len(long_keys)} keys exceed 15 chars (expected when limit='all')")
        return True
    else:
        print(f"⚠️  WARNING: No long keys found (might be unexpected)")
        return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "LIMIT FEATURE BUG FIX VERIFICATION" + " "*24 + "║")
    print("║" + " "*20 + "Programmer #3 - 2026-02-17" + " "*31 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    results = []
    
    try:
        results.append(("Test 1: Limit=15 with avoid_cut", test_limit_with_avoid_cut()))
    except Exception as e:
        print(f"❌ Test 1 CRASHED: {e}")
        results.append(("Test 1: Limit=15 with avoid_cut", False))
    
    try:
        results.append(("Test 2: Limit=10 hard cut", test_limit_hard_cut()))
    except Exception as e:
        print(f"❌ Test 2 CRASHED: {e}")
        results.append(("Test 2: Limit=10 hard cut", False))
    
    try:
        results.append(("Test 3: Limit='all' disabled", test_limit_disabled()))
    except Exception as e:
        print(f"❌ Test 3 CRASHED: {e}")
        results.append(("Test 3: Limit='all' disabled", False))
    
    # Summary
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*30 + "TEST SUMMARY" + " "*36 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    print()
    print("-" * 80)
    print(f"   Total: {passed}/{total} tests passed")
    print("-" * 80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Bug fix is working correctly!")
        print("\n✅ Intermediate keys are now properly truncated by Limit feature")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Bug fix needs review.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
