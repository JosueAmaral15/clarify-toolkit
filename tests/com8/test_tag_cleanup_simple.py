#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple Test: Verify tag cleanup fix
Tests that broken tags are properly cleaned from plain text

Programmer: COM8
Date: 2026-02-06
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.format_mapper import FormatMapper

print("=" * 80)
print("SIMPLE TEST: Tag Artifact Cleanup")
print("=" * 80)
print()

# Test cases simulating Google Translate breakage
test_cases = [
    {
        "name": "Broken opening tag (spaces added)",
        "input": "Some text before <113 | broken tag content",
        "expected_clean": "Some text before  broken tag content",  # Tag removed
    },
    {
        "name": "Broken closing tag",
        "input": "Some content</113|65536> more content",
        "expected_clean": "Some content more content",
    },
    {
        "name": "Mixed broken and valid tags",
        "input": "<113|1:B>Valid bold</113|1> normal <114 | broken tag",
        "expected_segments": 2,  # One formatted, one plain (with broken tag cleaned)
    },
    {
        "name": "Complete valid tag",
        "input": "<113|1:B>Complete tag</113|1>",
        "expected_segments": 1,
        "expected_format": 113,
    },
]

print("Testing tag artifact cleanup...")
print()

for i, test in enumerate(test_cases, 1):
    print(f"Test {i}: {test['name']}")
    print(f"Input: {test['input']}")
    
    segments = FormatMapper.parse_tagged_text(test['input'])
    
    print(f"Parsed to {len(segments)} segment(s):")
    for j, seg in enumerate(segments):
        print(f"  Segment {j}: text={repr(seg.text)}, format={seg.format_bits}")
    
    # Check if broken tags were cleaned
    has_artifacts = any('<' in seg.text and ('|' in seg.text or ':' in seg.text) for seg in segments)
    
    if has_artifacts:
        print("❌ FAIL: Broken tags still present in text!")
    else:
        print("✅ PASS: No tag artifacts in output")
    
    print()

print("=" * 80)
print("NOTE: This test shows current behavior BEFORE the fix.")
print("      After implementing the fix, all tests should PASS.")
print("=" * 80)
