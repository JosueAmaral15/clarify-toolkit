"""
DETAILED FORMATTING COMPARISON: Original vs Translated
User feedback: "blank lines, alignment, and spacing not respected"
Let's compare the ACTUAL formatting
"""
import sys
sys.path.insert(0, 'src')
from translation.format_mapper import FormatMapper
import zipfile
import xml.etree.ElementTree as ET

print("="*80)
print("FORMATTING COMPARISON: Original vs Translated")
print("="*80)
print()

original_file = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
translated_file = 'CAIT_FINAL_TEST_100_PERCENT_COM8.odt'

def analyze_odt_formatting(filepath, label):
    """Analyze ODT structure and formatting"""
    print(f"{'='*80}")
    print(f"{label}: {filepath}")
    print(f"{'='*80}")
    
    with zipfile.ZipFile(filepath, 'r') as z:
        with z.open('content.xml') as f:
            content = f.read().decode('utf-8')
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Namespaces
            ns = {
                'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
                'style': 'urn:oasis:names:tc:opendocument:xmlns:style:1.0',
                'fo': 'urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0'
            }
            
            # Count elements
            paragraphs = root.findall('.//text:p', ns)
            spans = root.findall('.//text:span', ns)
            tabs = root.findall('.//text:tab', ns)
            line_breaks = root.findall('.//text:line-break', ns)
            spaces = root.findall('.//text:s', ns)
            
            print(f"Paragraphs: {len(paragraphs)}")
            print(f"Spans: {len(spans)}")
            print(f"Tabs: {len(tabs)}")
            print(f"Line breaks: {len(line_breaks)}")
            print(f"Multiple spaces: {len(spaces)}")
            print()
            
            # Check paragraph alignments
            alignments = {}
            for p in paragraphs[:20]:  # First 20 paragraphs
                style_name = p.get('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name')
                if style_name:
                    alignments[style_name] = alignments.get(style_name, 0) + 1
            
            if alignments:
                print(f"Paragraph styles found: {len(alignments)}")
                for style, count in list(alignments.items())[:10]:
                    print(f"  {style}: {count} times")
            print()
            
            # Show first 10 paragraphs with their content
            print("First 10 paragraphs:")
            print("-"*80)
            for i, p in enumerate(paragraphs[:10], 1):
                style = p.get('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}style-name', 'none')
                
                # Get text content
                text_content = ''.join(p.itertext())
                text_preview = text_content[:60].replace('\n', '\\n').replace('\t', '\\t')
                
                # Count child elements
                children = len(list(p))
                
                print(f"{i}. Style: {style:<15} Children: {children:<3} Text: {text_preview}...")
            print()
            
            return {
                'paragraphs': len(paragraphs),
                'spans': len(spans),
                'tabs': len(tabs),
                'line_breaks': len(line_breaks),
                'spaces': len(spaces),
                'styles': len(alignments)
            }

# Analyze both files
print("\n")
original_stats = analyze_odt_formatting(original_file, "ORIGINAL FILE")
print("\n")
translated_stats = analyze_odt_formatting(translated_file, "TRANSLATED FILE")

# Compare
print("="*80)
print("COMPARISON SUMMARY")
print("="*80)
print()
print(f"{'Metric':<25} {'Original':<15} {'Translated':<15} {'Status':<15}")
print("-"*70)

for metric in ['paragraphs', 'spans', 'tabs', 'line_breaks', 'spaces', 'styles']:
    orig = original_stats[metric]
    trans = translated_stats[metric]
    status = '✅ Same' if orig == trans else f'❌ Lost {orig-trans}'
    print(f"{metric.capitalize():<25} {orig:<15} {trans:<15} {status:<15}")

print()

# Extract and compare plain text structure
print("="*80)
print("PLAIN TEXT STRUCTURE COMPARISON")
print("="*80)
print()

# Original text
original_tagged = FormatMapper.extract_formatted_text_from_odt(original_file)
import re
original_plain = re.sub(r'<[^>]+>', '', original_tagged)

print("ORIGINAL (first 800 chars):")
print("-"*80)
print(original_plain[:800])
print()

# Translated text  
with zipfile.ZipFile(translated_file, 'r') as z:
    with z.open('content.xml') as f:
        content = f.read().decode('utf-8')
        translated_plain = re.sub(r'<[^>]+>', ' ', content)
        translated_plain = re.sub(r'\s+', ' ', translated_plain).strip()

print("TRANSLATED (first 800 chars):")
print("-"*80)
print(translated_plain[:800])
print()

# Count blank lines
original_blank_lines = original_plain.count('\n\n')
translated_blank_lines = translated_plain.count('\n\n')

print(f"Blank lines (\\n\\n):")
print(f"  Original: {original_blank_lines}")
print(f"  Translated: {translated_blank_lines}")
print()

# Check specific formatting issues
print("="*80)
print("SPECIFIC ISSUES TO CHECK")
print("="*80)
print()

issues_found = []

if translated_stats['tabs'] == 0 and original_stats['tabs'] > 0:
    issues_found.append(f"❌ Tabs lost: {original_stats['tabs']} → 0")
else:
    print(f"✅ Tabs preserved: {original_stats['tabs']} → {translated_stats['tabs']}")

if translated_stats['line_breaks'] < original_stats['line_breaks']:
    issues_found.append(f"❌ Line breaks lost: {original_stats['line_breaks']} → {translated_stats['line_breaks']}")
else:
    print(f"✅ Line breaks preserved: {original_stats['line_breaks']} → {translated_stats['line_breaks']}")

if translated_stats['spaces'] < original_stats['spaces']:
    issues_found.append(f"❌ Multiple spaces lost: {original_stats['spaces']} → {translated_stats['spaces']}")
else:
    print(f"✅ Multiple spaces preserved: {original_stats['spaces']} → {translated_stats['spaces']}")

if translated_stats['paragraphs'] < original_stats['paragraphs']:
    issues_found.append(f"❌ Paragraphs lost: {original_stats['paragraphs']} → {translated_stats['paragraphs']}")
else:
    print(f"✅ Paragraphs preserved: {original_stats['paragraphs']} → {translated_stats['paragraphs']}")

print()

if issues_found:
    print("ISSUES FOUND:")
    print("-"*80)
    for issue in issues_found:
        print(issue)
    print()
    print("These formatting elements are being lost in translation!")
else:
    print("✅ All formatting elements preserved!")

print()
print("="*80)
print("USER FEEDBACK VALIDATION")
print("="*80)
print()
print("User said: 'blank lines, alignment, and spacing not respected'")
print()

if translated_stats['tabs'] == 0 and original_stats['tabs'] > 0:
    print("✅ User is CORRECT about spacing - tabs are lost!")
    
if translated_stats['line_breaks'] < original_stats['line_breaks']:
    print("✅ User is CORRECT about blank lines - line breaks lost!")
    
if translated_stats['paragraphs'] < original_stats['paragraphs']:
    print("✅ User is CORRECT - paragraph structure lost!")

print()
print("Next: Need to investigate WHY these elements are lost!")

