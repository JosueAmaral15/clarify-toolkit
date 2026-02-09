#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI Test for Google Translate with Number Tags
Tests format preservation feature from Sessions 64-72

Programmer: COM8
Branch: COM8-documentation-reading
Date: 2026-02-06
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.google_translate import GoogleTranslateAPI, TranslationResult


def test_translation_with_tags():
    """Test Google Translate with number tag preservation."""
    
    print("=" * 80)
    print("CLI TEST: Google Translate with Number Tags")
    print("=" * 80)
    print()
    print("NOTE: This tests plain text mode translation.")
    print("      Tags like <113|N:X> will be sent to Google Translate as-is.")
    print("      Google Translate should preserve them or translate around them.")
    print()
    
    # Initialize API
    print("Initializing Google Translate API...")
    api = GoogleTranslateAPI()
    print("✅ API initialized")
    print()
    
    # Test cases from test_translate_tags.txt
    test_cases = [
        {
            "name": "Simple tag in middle",
            "text": "This is a sentence with <113|1:L> a simple tag in the middle.",
            "expected_tags": ["<113|1:L>"]
        },
        {
            "name": "Multiple tags",
            "text": "The quick <113|2:L> brown fox jumps <113|3:L> over the lazy dog.",
            "expected_tags": ["<113|2:L>", "<113|3:L>"]
        },
        {
            "name": "Tag with metadata (Session 70)",
            "text": "Advanced formatting <113|65536:L> requires special handling.",
            "expected_tags": ["<113|65536:L>"]
        },
        {
            "name": "Complex tag pattern",
            "text": "This tests the normalization: <113|4:B:L> with bold and link.",
            "expected_tags": ["<113|4:B:L>"]
        },
        {
            "name": "Tags at different positions",
            "text": "<113|5:L> Starting tag middle tag <113|6:L> continues ending <113|7:L>",
            "expected_tags": ["<113|5:L>", "<113|6:L>", "<113|7:L>"]
        },
    ]
    
    # Run tests
    print("RUNNING TRANSLATION TESTS (English → Portuguese)")
    print("=" * 80)
    print()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("-" * 80)
        
        original_text = test_case['text']
        expected_tags = test_case['expected_tags']
        
        print(f"Original:  {original_text}")
        print(f"Expected Tags: {', '.join(expected_tags)}")
        
        # Translate directly (as plain text mode does)
        print("\n[Translating] Sending to Google Translate...")
        result = api.translate_text(original_text, from_lang='en', to_lang='pt')
        
        if not result.success:
            print(f"❌ Translation failed: {result.error_message}")
            results.append({
                "test": test_case['name'],
                "status": "FAIL",
                "reason": result.error_message
            })
            print()
            continue
        
        translated_text = result.translated_text
        print(f"Translated: {translated_text}")
        print(f"From cache: {result.from_cache}")
        
        # Verify tags preserved
        print("\n[Verifying] Checking tag preservation...")
        all_tags_present = all(tag in translated_text for tag in expected_tags)
        
        if all_tags_present:
            print(f"✅ SUCCESS: All tags preserved!")
            results.append({
                "test": test_case['name'],
                "status": "PASS",
                "original": original_text,
                "translated": translated_text
            })
        else:
            missing_tags = [tag for tag in expected_tags if tag not in translated_text]
            print(f"❌ FAIL: Missing tags: {missing_tags}")
            results.append({
                "test": test_case['name'],
                "status": "FAIL",
                "reason": f"Missing tags: {missing_tags}",
                "original": original_text,
                "translated": translated_text
            })
        
        print()
        print("=" * 80)
        print()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed:      {passed} ✅")
    print(f"Failed:      {failed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    print()
    
    # Detailed results
    if failed > 0:
        print("\nFAILED TESTS:")
        for r in results:
            if r['status'] == 'FAIL':
                print(f"  - {r['test']}: {r.get('reason', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    
    # Return status
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = test_translation_with_tags()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
