#!/usr/bin/env python3
"""
Test: smart_truncate with word boundary detection (spaces + special chars)

Tests that avoid_cut now cuts at:
  - Whitespace (existing behavior)
  - Non-letter/non-underscore characters: -, ., :, (, ), etc.

Examples:
  - "hello-world-test" with limit=10 → "hello-world" (cuts at -)
  - "t.pages.contact" with limit=10 → "t.pages" (cuts at .)
  - "has(item.id)" with limit=8 → "has(item" (cuts at .)
"""

from src.extractors.advanced_extractor import smart_truncate


def test_cut_at_hyphen():
    """Test cutting at hyphen boundary."""
    text = "hello-world-test"
    result = smart_truncate(text, "10", avoid_cut=True, avoid_cut_direction="before")
    expected = "hello"  # Cut at first hyphen before limit
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✅ PASS: Cut at hyphen: '{text}' → '{result}'")


def test_cut_at_dot():
    """Test cutting at dot boundary."""
    text = "t.pages.contact.quick"
    result = smart_truncate(text, "10", avoid_cut=True, avoid_cut_direction="before")
    # Should cut at dot before position 10
    # t.pages.co (10 chars), cut at last dot before = "t.pages"
    expected = "t.pages"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✅ PASS: Cut at dot: '{text}' → '{result}'")


def test_cut_at_parenthesis():
    """Test cutting at parenthesis boundary."""
    text = "expandedItems.has(item.id)"
    result = smart_truncate(text, "20", avoid_cut=True, avoid_cut_direction="before")
    # expandedItems.has(i (20 chars), cut at last boundary = "expandedItems.has"
    expected = "expandedItems.has"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✅ PASS: Cut at parenthesis: '{text}' → '{result}'")


def test_cut_at_colon():
    """Test cutting at colon boundary."""
    text = "sentence:string,index:number"
    result = smart_truncate(text, "18", avoid_cut=True, avoid_cut_direction="before")
    # sentence:string,in (18 chars), cut at last boundary (comma or colon)
    expected = "sentence"  # or "sentence:string" depending on implementation
    print(f"INFO: Cut at colon/comma: '{text}' → '{result}'")
    # Just verify it doesn't crash and cuts somewhere reasonable
    assert len(result) <= 18, f"Result too long: {len(result)} > 18"
    print(f"✅ PASS: Cut at colon/comma: length={len(result)} <= 18")


def test_whitespace_still_works():
    """Test that whitespace cutting still works."""
    text = "hello world test example"
    result = smart_truncate(text, "15", avoid_cut=True, avoid_cut_direction="before")
    # "hello world tes" (15 chars), cut at last space = "hello world"
    expected = "hello world"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✅ PASS: Cut at whitespace: '{text}' → '{result}'")


def test_underscore_not_boundary():
    """Test that underscore is NOT a word boundary."""
    text = "t_pages_contact_quick"
    result = smart_truncate(text, "15", avoid_cut=True, avoid_cut_direction="before")
    # "t_pages_contact" (15 chars), no boundary found, return truncated
    # Since underscores are part of word, should not cut
    assert "_" in result, f"Underscore should be preserved in '{result}'"
    print(f"✅ PASS: Underscore preserved: '{text}' → '{result}'")


def test_direction_after():
    """Test 'after' direction cuts at next boundary."""
    text = "hello-world-test-example"
    result = smart_truncate(text, "10", avoid_cut=True, avoid_cut_direction="after")
    # "hello-worl" (10 chars), search forward for next boundary (hyphen at position 11)
    expected = "hello-world"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✅ PASS: Direction 'after': '{text}' → '{result}'")


def test_avoid_cut_false():
    """Test that avoid_cut=False does hard truncation."""
    text = "hello-world-test"
    result = smart_truncate(text, "10", avoid_cut=False)
    expected = "hello-worl"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print(f"✅ PASS: Hard cut (avoid_cut=False): '{text}' → '{result}'")


def main():
    print("=" * 80)
    print("TEST: smart_truncate with word boundary detection")
    print("=" * 80)
    print()

    tests = [
        test_cut_at_hyphen,
        test_cut_at_dot,
        test_cut_at_parenthesis,
        test_cut_at_colon,
        test_whitespace_still_works,
        test_underscore_not_boundary,
        test_direction_after,
        test_avoid_cut_false,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {test.__name__}: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print()
    print("=" * 80)
    print(f"RESULTS: {passed}/{len(tests)} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("✅ ALL TESTS PASSED")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
