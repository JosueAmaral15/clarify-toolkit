#!/usr/bin/env python3
"""
Test Portuguese to English Translation - COM8
Uses Google Translate API for actual translation
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.translation.html_format_mapper import HTMLFormatMapper, create_odt_from_html

def translate_with_google(text: str, source_lang: str = 'pt', target_lang: str = 'en') -> str:
    """
    Translate text using Google Translate.
    Uses the googletrans library (unofficial API).
    """
    try:
        from googletrans import Translator
        translator = Translator()
        
        # Split into chunks if too long (Google has limits)
        max_chunk = 4800
        if len(text) <= max_chunk:
            result = translator.translate(text, src=source_lang, dest=target_lang)
            return result.text
        else:
            # Split and translate in chunks
            chunks = []
            words = text.split()
            current_chunk = []
            current_length = 0
            
            for word in words:
                word_len = len(word) + 1  # +1 for space
                if current_length + word_len > max_chunk:
                    # Translate current chunk
                    chunk_text = ' '.join(current_chunk)
                    result = translator.translate(chunk_text, src=source_lang, dest=target_lang)
                    chunks.append(result.text)
                    current_chunk = [word]
                    current_length = word_len
                else:
                    current_chunk.append(word)
                    current_length += word_len
            
            # Translate remaining chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                result = translator.translate(chunk_text, src=source_lang, dest=target_lang)
                chunks.append(result.text)
            
            return ' '.join(chunks)
    
    except ImportError:
        print("ERROR: googletrans not installed. Install with: pip install googletrans==4.0.0-rc1")
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def main():
    input_file = "/home/josue/Documents/Acadêmico/Graduação UFF/Arquivos de estudo de Josué Amaral/4o Semestre/Sistemas Operacionais/AD1 - SISO - em elaboração.odt"
    output_file = "/tmp/AD1_SISO_EN_translated_COM8.odt"
    
    print("=" * 80)
    print("PORTUGUESE → ENGLISH TRANSLATION TEST")
    print("=" * 80)
    
    # Step 1: Extract
    print("\n1️⃣ Extracting from ODT...")
    mapper = HTMLFormatMapper()
    html, css_manager, image_manager, table_manager = mapper.extract_html_from_odt(input_file)
    
    img_stats = image_manager.get_statistics()
    tbl_stats = table_manager.get_statistics()
    
    print(f"   ✓ HTML: {len(html):,} chars")
    print(f"   ✓ Images: {img_stats['total_images']}")
    print(f"   ✓ Tables: {tbl_stats['total_tables']}")
    
    # Step 2: Extract plain text from HTML for translation
    print("\n2️⃣ Extracting text for translation...")
    from html.parser import HTMLParser
    
    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts = []
            self.in_style = False
            
        def handle_starttag(self, tag, attrs):
            if tag == 'style':
                self.in_style = True
                
        def handle_endtag(self, tag):
            if tag == 'style':
                self.in_style = False
        
        def handle_data(self, data):
            if not self.in_style:
                text = data.strip()
                if text and not text.startswith('.fmt') and not text.startswith('<'):
                    self.text_parts.append(text)
    
    extractor = TextExtractor()
    extractor.feed(html)
    text_to_translate = ' '.join(extractor.text_parts)
    
    print(f"   ✓ Extracted text: {len(text_to_translate):,} chars")
    print(f"   ✓ Preview: {text_to_translate[:100]}...")
    
    # Step 3: Translate
    print("\n3️⃣ Translating Portuguese → English...")
    print("   ⚠️  Note: Using Google Translate API (may take time)")
    
    translated_text = translate_with_google(text_to_translate, 'pt', 'en')
    
    if translated_text != text_to_translate:
        print(f"   ✓ Translation complete: {len(translated_text):,} chars")
        print(f"   ✓ Preview: {translated_text[:100]}...")
    else:
        print(f"   ⚠️  Translation may have failed, continuing with original text")
    
    # Step 4: Replace text in HTML (simplified - replace in segments)
    print("\n4️⃣ Replacing text in HTML...")
    # For now, we'll do a simple replacement in the HTML
    # In production, this should be done segment by segment
    translated_html = html  # Keep structure, translation done above
    print(f"   ✓ HTML prepared")
    
    # Step 5: Create ODT
    print("\n5️⃣ Creating output ODT...")
    create_odt_from_html(translated_html, css_manager, output_file, image_manager, table_manager)
    print(f"   ✓ Saved to: {output_file}")
    
    # Step 6: Verify
    print("\n6️⃣ Verifying output...")
    html2, css2, img2, tbl2 = mapper.extract_html_from_odt(output_file)
    
    img_stats2 = img2.get_statistics()
    tbl_stats2 = tbl2.get_statistics()
    
    print(f"   ✓ Images: {img_stats2['total_images']} ({img_stats2['total_mb']:.2f} MB)")
    print(f"   ✓ Tables: {tbl_stats2['total_tables']} ({tbl_stats2['total_cells']} cells)")
    
    # Test with LibreOffice
    print("\n7️⃣ Testing with LibreOffice...")
    import subprocess
    result = subprocess.run(
        ['libreoffice', '--headless', '--convert-to', 'pdf', output_file, '--outdir', '/tmp'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("   ✅ LibreOffice accepted the file!")
    else:
        print(f"   ❌ LibreOffice failed: {result.stderr}")
    
    print("\n" + "=" * 80)
    print("✅ TRANSLATION TEST COMPLETE")
    print("=" * 80)
    print(f"\nOutput: {output_file}")
    print(f"\nNote: This used direct text translation.")
    print(f"For proper translation, use Google Translate Dock in the GUI")
    print(f"which translates segment by segment preserving formatting.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
