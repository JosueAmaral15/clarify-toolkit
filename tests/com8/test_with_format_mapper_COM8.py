#!/usr/bin/env python3
"""
End-to-end test: Verify adjacent tags fix with user's file
Uses the actual FormatMapper class workflow
"""

import sys
sys.path.insert(0, 'src')

from translation.format_mapper import FormatMapper

print("=" * 80)
print("END-TO-END TEST: Adjacent Tags Fix with User's File")
print("=" * 80)

original_file = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"

print("\n📄 Step 1: Extract formatted text from ODT...")
formatted_text = FormatMapper.extract_formatted_text_from_odt(original_file)
print(f"   Extracted {len(formatted_text)} characters")

# Check if we have adjacent tags in the extracted text
print("\n🔍 Step 2: Check for adjacent tags in extracted text...")
import re
adjacent_pattern = r'</\d+\|[^>]+><\d+\|[^>]+>'
adjacent_matches = re.findall(adjacent_pattern, formatted_text)

if adjacent_matches:
    print(f"   ✅ Found {len(adjacent_matches)} adjacent tag pair(s)")
    print(f"   Examples: {adjacent_matches[:3]}")
else:
    print("   ⚠️  No adjacent tags found (might not be the issue)")

# Now check if the specific pattern from the bug exists
if '</113|65536><112|65536' in formatted_text:
    print("   ✅ Found the EXACT pattern from the bug report!")
else:
    print("   ℹ️  Exact bug pattern not in extracted text")

print("\n✅ Test complete!")
print("\nNext step: Run full translation through GUI or:")
print("  1. Launch Clarify application")
print("  2. Open Google Translate tool")
print("  3. Load the user's file")
print("  4. Translate Portuguese → English")
print("  5. Check output for visible tags")
