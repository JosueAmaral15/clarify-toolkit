#!/usr/bin/env python3
"""
Debug Content Loss - COM8
Traces where content disappears in ODT workflow
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html
from odf.opendocument import load
from odf import text, teletype

def count_odt_stats(file_path):
    """Count statistics from ODT file"""
    doc = load(file_path)
    
    paragraphs = len(doc.getElementsByType(text.P))
    all_text = teletype.extractText(doc.text)
    chars = len(all_text)
    words = len(all_text.split())
    
    return {
        'paragraphs': paragraphs,
        'chars': chars,
        'words': words
    }

def main():
    tcc_file = "docs/TCC_THAYS_CRISTINA_FARIAS_VERÇOZA_COSTA_e_JOSUÉ_AMARAL.odt"
    
    print("=" * 80)
    print("CONTENT LOSS INVESTIGATION - TCC FILE")
    print("=" * 80)
    
    # Step 1: Count original
    print("\n[1/5] Reading original ODT...")
    original_stats = count_odt_stats(tcc_file)
    print(f"  Paragraphs: {original_stats['paragraphs']:,}")
    print(f"  Characters: {original_stats['chars']:,}")
    print(f"  Words: {original_stats['words']:,}")
    
    # Step 2: Extract to HTML
    print("\n[2/5] Extracting to HTML...")
    mapper = HTMLFormatMapper()
    html, css_manager, image_manager, table_manager = mapper.extract_html_from_odt(tcc_file)
    
    print(f"  HTML length: {len(html):,} chars")
    
    # Count paragraphs in HTML
    html_paragraphs = html.count('<p') + html.count('<h1') + html.count('<h2') + html.count('<h3')
    print(f"  HTML paragraphs: {html_paragraphs:,}")
    
    # Step 3: Create temp output
    print("\n[3/5] Creating output ODT...")
    temp_output = "/tmp/tcc_debug_output_COM8.odt"
    create_odt_from_html(html, css_manager, temp_output, image_manager, table_manager)
    print(f"  Saved to: {temp_output}")
    
    # Step 4: Count output
    print("\n[4/5] Reading output ODT...")
    output_stats = count_odt_stats(temp_output)
    print(f"  Paragraphs: {output_stats['paragraphs']:,}")
    print(f"  Characters: {output_stats['chars']:,}")
    print(f"  Words: {output_stats['words']:,}")
    
    # Step 5: Analysis
    print("\n[5/5] ANALYSIS:")
    print("=" * 80)
    
    para_loss = original_stats['paragraphs'] - output_stats['paragraphs']
    char_loss = original_stats['chars'] - output_stats['chars']
    word_loss = original_stats['words'] - output_stats['words']
    
    print(f"\nParagraph loss: {para_loss:,} ({para_loss / original_stats['paragraphs'] * 100:.1f}%)")
    print(f"Character loss: {char_loss:,} ({char_loss / original_stats['chars'] * 100:.1f}%)")
    print(f"Word loss: {word_loss:,} ({word_loss / original_stats['words'] * 100:.1f}%)")
    
    # Compare HTML with original
    html_char_diff = original_stats['chars'] - len(html)
    print(f"\n🔍 Character difference (Original ODT vs HTML): {html_char_diff:,}")
    
    if abs(html_char_diff) < 1000:
        print("   ✓ HTML extraction preserves content well")
        print("   → Content loss happens in HTML → ODT conversion")
    else:
        print("   ✗ HTML extraction is losing content")
        print("   → Content loss happens in ODT → HTML conversion")
    
    print("\n" + "=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
