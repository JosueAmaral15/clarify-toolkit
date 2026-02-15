"""
Trace where placeholders are getting into final ODT
"""
import sys
sys.path.insert(0, 'src')
from translation.format_mapper import (
    FormatMapper,
    replace_tags_with_placeholders,
    restore_tags_from_placeholders,
    protect_special_whitespace,
    restore_special_whitespace
)

input_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'

print("=== TRACING RESTORATION FLOW ===")
print()

# Step 1: Extract
print("1. Extracting...")
tagged = FormatMapper.extract_formatted_text_from_odt(input_file)
print(f"   Length: {len(tagged)}")
print(f"   Sample: {tagged[:100]}")
print()

# Step 2: Protect format tags
print("2. Protecting format tags...")
text_with_placeholders, mapping = replace_tags_with_placeholders(tagged)
print(f"   Length: {len(text_with_placeholders)}")
print(f"   Sample: {text_with_placeholders[:100]}")
print()

# Step 3: Protect whitespace
print("3. Protecting whitespace...")
protected = protect_special_whitespace(text_with_placeholders)
print(f"   Length: {len(protected)}")
print(f"   Sample: {protected[:100]}")
print()

# Step 4: SIMULATE Google Translate corrupting ONE placeholder
print("4. Simulating Google Translate corruption...")
simulated = protected.replace('【TAB】', '【TA B】', 1)  # Corrupt just ONE
print(f"   Corrupted 1 【TAB】 → 【TA B】")
print(f"   Sample: {simulated[:100]}")
print()

# Step 5: Restore whitespace
print("5. Restoring whitespace...")
restored_ws = restore_special_whitespace(simulated)
print(f"   Length: {len(restored_ws)}")
print(f"   Sample: {restored_ws[:100]}")

# Check if placeholder survived
if '【' in restored_ws:
    count = restored_ws.count('【')
    print(f"   ❌ PROBLEM: Still has {count} 【 characters!")
    
    # Find first one
    idx = restored_ws.find('【')
    print(f"   First at position {idx}: {restored_ws[idx:idx+20]}")
else:
    print(f"   ✅ No 【 remaining (whitespace restored correctly)")
print()

# Step 6: Restore format tags
print("6. Restoring format tags...")
final_tagged = restore_tags_from_placeholders(restored_ws, mapping)
print(f"   Length: {len(final_tagged)}")

if '【' in final_tagged:
    count = final_tagged.count('【')
    print(f"   ❌ PROBLEM: Still has {count} 【 characters!")
    idx = final_tagged.find('【')
    print(f"   First at position {idx}: {final_tagged[idx:idx+20]}")
else:
    print(f"   ✅ No 【 remaining (all restored correctly)")
print()

# Step 7: Parse to segments
print("7. Parsing to segments...")
segments = FormatMapper.parse_tagged_text(final_tagged)
print(f"   Created {len(segments)} segments")

# Check if any segment has placeholders
segments_with_placeholders = [s for s in segments if '【' in str(s)]
if segments_with_placeholders:
    print(f"   ❌ PROBLEM: {len(segments_with_placeholders)} segments still have 【")
    for seg in segments_with_placeholders[:3]:
        print(f"      {seg}")
else:
    print(f"   ✅ No segments with 【")

