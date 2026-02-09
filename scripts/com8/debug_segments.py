#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug: Check what segments actually contain
Find where tags leak into segment text

Programmer: COM8
Date: 2026-02-06
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.format_mapper import FormatMapper

input_file = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"

print("="*80)
print("DEBUG: Segment Content Analysis")
print("="*80)
print()

# Extract formatted text
print("Extracting formatted text from ODT...")
formatted_text = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"Length: {len(formatted_text)}")
print()

# Show first 1000 chars
print("First 1000 chars of formatted text:")
print("-"*80)
print(formatted_text[:1000])
print("-"*80)
print()

# Parse to segments
print("Parsing to segments...")
segments = FormatMapper.parse_tagged_text(formatted_text)
print(f"Total segments: {len(segments)}")
print()

# Check for tags in segment text
print("Checking segments for tag leaks...")
print("-"*80)

tag_leak_count = 0
for i, seg in enumerate(segments[:20]):  # Check first 20
    if '<1' in seg.text or '</1' in seg.text:
        tag_leak_count += 1
        print(f"❌ Segment {i} has tag leak:")
        print(f"   text: {repr(seg.text[:100])}...")
        print(f"   format_bits: {seg.format_bits}")
        print(f"   paragraph_format: {seg.paragraph_format}")
        print()

if tag_leak_count == 0:
    print("✅ No tag leaks found in first 20 segments!")
else:
    print(f"⚠️  Found {tag_leak_count} segments with tag leaks")

print()
print("="*80)
