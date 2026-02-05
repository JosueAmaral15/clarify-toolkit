#!/usr/bin/env python3
"""
Test to trace the complete workflow and find where tags leak into output.
"""
import sys
sys.path.insert(0, 'src')

from translation.format_mapper import FormatMapper, TextSegment, FormatBit

print("="*70)
print("STEP-BY-STEP WORKFLOW TEST")
print("="*70)

# Step 1: Create a segment with formatting
print("\n### STEP 1: Create segment with formatting")
segment = TextSegment(
    text="This is bold and centered text",
    format_bits=FormatBit.BOLD,
    metadata=None,
    paragraph_format=FormatBit.ALIGNMENT,
    paragraph_metadata="C"
)
print(f"Segment created:")
print(f"  .text = '{segment.text}'")
print(f"  .format_bits = {segment.format_bits}")
print(f"  .paragraph_format = {segment.paragraph_format}")

# Step 2: Convert to tagged text (what goes to Google Translate)
print("\n### STEP 2: Convert to tagged text")
tagged_text = segment.to_tagged_text()
print(f"Tagged text (sent to Google Translate):")
print(f"  '{tagged_text}'")

# Step 3: Simulate Google Translate (just return same text)
print("\n### STEP 3: Simulate translation")
translated_tagged_text = tagged_text  # In reality, Google translates content
print(f"Translated tagged text (returned from Google):")
print(f"  '{translated_tagged_text}'")

# Step 4: Parse tagged text back to segments
print("\n### STEP 4: Parse tagged text back to segments")
parsed_segments = FormatMapper.parse_tagged_text(translated_tagged_text)
print(f"Number of segments parsed: {len(parsed_segments)}")
for i, seg in enumerate(parsed_segments):
    print(f"  Segment {i}:")
    print(f"    .text = '{seg.text}'")
    print(f"    .format_bits = {seg.format_bits}")
    print(f"    .paragraph_format = {seg.paragraph_format}")
    print(f"    HAS TAGS IN TEXT? {'<' in seg.text or '>' in seg.text}")

# Step 5: Create ODT from segments
print("\n### STEP 5: Create ODT from segments")
output_path = "/tmp/test_tag_workflow.odt"
try:
    FormatMapper.create_odt_from_segments(parsed_segments, output_path)
    print(f"✅ ODT created: {output_path}")
except Exception as e:
    print(f"❌ ERROR creating ODT: {e}")
    import traceback
    traceback.print_exc()

# Step 6: Verify ODT content
print("\n### STEP 6: Read back the ODT to check for tags")
try:
    from odf import text, teletype
    from odf.opendocument import load
    
    doc = load(output_path)
    all_text = teletype.extractText(doc.text)
    print(f"Text extracted from ODT:")
    print(f"  '{all_text}'")
    print(f"  HAS TAGS IN ODT? {'<' in all_text or '>' in all_text}")
    
    if '<' in all_text or '>' in all_text:
        print("\n❌ PROBLEM FOUND: Tags are visible in ODT file!")
    else:
        print("\n✅ SUCCESS: No tags visible in ODT file")
        
except Exception as e:
    print(f"❌ ERROR reading ODT: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
