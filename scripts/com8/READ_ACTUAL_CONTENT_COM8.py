"""
Read ACTUAL content from both files to verify translation quality
"""
import zipfile
import xml.etree.ElementTree as ET
import re

def extract_readable_text(odt_file):
    """Extract human-readable text from ODT"""
    with zipfile.ZipFile(odt_file, 'r') as z:
        with z.open('content.xml') as f:
            content = f.read().decode('utf-8')
            root = ET.fromstring(content)
            ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
            
            paragraphs = []
            for para in root.findall('.//text:p', ns):
                text = ''.join(para.itertext()).strip()
                if text:
                    paragraphs.append(text)
            
            return paragraphs

print("="*80)
print("READING ACTUAL DOCUMENT CONTENT")
print("="*80)
print()

original = '/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt'
translated = 'CAIT_FINAL_VERIFIED_COM8.odt'

print("ORIGINAL (Portuguese):")
print("="*80)
orig_paras = extract_readable_text(original)
for i, para in enumerate(orig_paras[:15], 1):
    print(f"\n{i}. {para}")

print()
print()
print("TRANSLATED (English):")
print("="*80)
trans_paras = extract_readable_text(translated)
for i, para in enumerate(trans_paras[:15], 1):
    print(f"\n{i}. {para}")

print()
print()
print("="*80)
print("CONTENT ANALYSIS")
print("="*80)
print()

# Find major sections
print("Looking for major sections/headers...")
print()

orig_sections = []
for para in orig_paras:
    # Look for headers (all caps with colons, or bold markers)
    if ':' in para and len(para) < 100:
        orig_sections.append(para)

trans_sections = []
for para in trans_paras:
    if ':' in para and len(para) < 100:
        trans_sections.append(para)

print(f"Original sections found: {len(orig_sections)}")
for i, sec in enumerate(orig_sections[:10], 1):
    print(f"  {i}. {sec}")

print()
print(f"Translated sections found: {len(trans_sections)}")
for i, sec in enumerate(trans_sections[:10], 1):
    print(f"  {i}. {sec}")

print()
print("="*80)
print("SIDE-BY-SIDE COMPARISON (First 5 major paragraphs)")
print("="*80)
print()

# Compare substantial paragraphs (>50 chars)
orig_substantial = [p for p in orig_paras if len(p) > 50][:5]
trans_substantial = [p for p in trans_paras if len(p) > 50][:5]

for i in range(max(len(orig_substantial), len(trans_substantial))):
    print(f"\n--- Paragraph {i+1} ---")
    
    if i < len(orig_substantial):
        print(f"ORIGINAL: {orig_substantial[i][:150]}...")
    else:
        print(f"ORIGINAL: (missing)")
    
    if i < len(trans_substantial):
        print(f"ENGLISH:  {trans_substantial[i][:150]}...")
    else:
        print(f"ENGLISH:  (missing)")

print()
print()
print("="*80)
print("QUALITY CHECK")
print("="*80)
print()

# Check if translation makes sense
issues = []

# Check 1: Are there Portuguese words in English?
portuguese_indicators = ['são', 'com', 'para', 'que', 'pela', 'dos', 'das']
for para in trans_paras:
    for word in portuguese_indicators:
        if f' {word} ' in para.lower():
            issues.append(f"Portuguese word '{word}' found in English: {para[:50]}...")
            break

if issues:
    print("⚠️  Potential issues found:")
    for issue in issues[:5]:
        print(f"  - {issue}")
else:
    print("✅ No obvious Portuguese words in English translation")

print()

# Check 2: Do English sentences make grammatical sense?
print("Checking if English is readable...")
english_samples = [p for p in trans_paras if len(p) > 100][:3]
if english_samples:
    print("✅ English text samples found:")
    for i, sample in enumerate(english_samples, 1):
        print(f"\n  Sample {i}:")
        print(f"  {sample[:200]}...")
else:
    print("⚠️  No substantial English text found")

print()

# Check 3: Document structure
print("Document structure:")
print(f"  Original paragraphs: {len(orig_paras)}")
print(f"  Translated paragraphs: {len(trans_paras)}")
print(f"  Difference: {abs(len(orig_paras) - len(trans_paras))} paragraphs")

if abs(len(orig_paras) - len(trans_paras)) <= 10:
    print("  ✅ Paragraph count similar (acceptable)")
else:
    print("  ⚠️  Large difference in paragraph count")

