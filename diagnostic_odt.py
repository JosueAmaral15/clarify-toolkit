#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnostic: Compare Original vs Translated ODT
Investigate what went wrong in the translation

Programmer: COM8
Date: 2026-02-06
"""

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

def analyze_odt(file_path, label):
    """Extract and analyze ODT content."""
    print(f"\n{'='*80}")
    print(f"{label}: {Path(file_path).name}")
    print('='*80)
    
    with zipfile.ZipFile(file_path, 'r') as odt_zip:
        # Read content.xml
        with odt_zip.open('content.xml') as f:
            content = f.read().decode('utf-8')
        
        # Count elements
        import re
        
        # Count text spans
        spans = len(re.findall(r'<text:span', content))
        # Count paragraphs
        paragraphs = len(re.findall(r'<text:p[>\s]', content))
        # Count tables
        tables = len(re.findall(r'<table:table', content))
        # Count images
        images = len(re.findall(r'<draw:image', content))
        
        print(f"Structure:")
        print(f"  - Paragraphs: {paragraphs}")
        print(f"  - Spans: {spans}")
        print(f"  - Tables: {tables}")
        print(f"  - Images: {images}")
        
        # Extract first 1000 chars of actual text content
        text_only = re.sub(r'<[^>]+>', '', content)
        text_only = ' '.join(text_only.split())  # Clean whitespace
        
        print(f"\nFirst 500 chars of text:")
        print(f"{text_only[:500]}")
        
        # Check for tag artifacts
        tag_artifacts = re.findall(r'&lt;11[23]', content)
        if tag_artifacts:
            print(f"\n⚠️  WARNING: Found {len(tag_artifacts)} tag artifacts (tags not converted back to formatting!)")
            print(f"   Examples: {tag_artifacts[:5]}")
        
        return content


print("="*80)
print("DIAGNOSTIC: ODT Translation Comparison")
print("="*80)

original_file = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"
translated_file = "/home/josue/Documents/Informática/Programação/programming workspace/System Management JSON Files - Clarify project/clarify-COM8/CAIT_Biologia_Translated_COM8.odt"

original_content = analyze_odt(original_file, "ORIGINAL")
translated_content = analyze_odt(translated_file, "TRANSLATED")

print("\n" + "="*80)
print("COMPARISON")
print("="*80)

print(f"\nFile sizes:")
print(f"  Original:   {Path(original_file).stat().st_size / 1024:.1f} KB")
print(f"  Translated: {Path(translated_file).stat().st_size / 1024:.1f} KB")
print(f"  Ratio:      {Path(translated_file).stat().st_size / Path(original_file).stat().st_size * 100:.1f}%")

print(f"\nContent.xml sizes:")
print(f"  Original:   {len(original_content):,} bytes")
print(f"  Translated: {len(translated_content):,} bytes")
print(f"  Ratio:      {len(translated_content) / len(original_content) * 100:.1f}%")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

if '&lt;11' in translated_content:
    print("\n❌ FAILED: Tags were NOT properly converted back to formatting!")
    print("   Tags appear as literal text instead of <text:span> elements.")
    print("   This means the format restoration step failed.")
else:
    print("\n✅ Tags appear to be properly converted.")
    
if Path(translated_file).stat().st_size < Path(original_file).stat().st_size * 0.5:
    print("\n⚠️  WARNING: Output file is suspiciously small (< 50% of original)")
    print("   This suggests content may have been lost.")

print()
