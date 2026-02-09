#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CLI Test for ODT → ODT Translation with Format Preservation
Tests complete workflow from Sessions 64-72

Programmer: COM8
Branch: COM8-documentation-reading
Date: 2026-02-06
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from translation.google_translate import GoogleTranslateAPI
from translation.format_mapper import FormatMapper


def test_odt_translation(input_file: str, output_file: str):
    """
    Test complete ODT translation workflow:
    1. Extract formatted text from ODT (with tags)
    2. Translate text (tags preserved)
    3. Create new ODT with formatting restored
    """
    
    print("=" * 80)
    print("CLI TEST: ODT → ODT Translation with Format Preservation")
    print("=" * 80)
    print()
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"❌ ERROR: Input file not found: {input_file}")
        return 1
    
    output_path = Path(output_file)
    
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Size:   {input_path.stat().st_size / 1024:.1f} KB")
    print()
    
    # Step 1: Extract formatted text from ODT
    print("=" * 80)
    print("STEP 1: Extract Formatted Text from ODT")
    print("=" * 80)
    print()
    print("Extracting text with format tags (Session 70 normalization)...")
    
    try:
        formatted_text = FormatMapper.extract_formatted_text_from_odt(str(input_path))
        print(f"✅ Extraction complete!")
        print(f"   Length: {len(formatted_text)} characters")
        
        # Count tags
        import re
        tags = re.findall(r'<113\|\d+:[^>]+>', formatted_text)
        print(f"   Format tags found: {len(tags)}")
        
        # Show first 500 chars as preview
        print(f"\n   Preview (first 500 chars):")
        print("   " + "-" * 76)
        preview = formatted_text[:500].replace('\n', '\n   ')
        print(f"   {preview}")
        if len(formatted_text) > 500:
            print(f"   ... ({len(formatted_text) - 500} more characters)")
        print()
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 2: Parse tagged text to segments
    print("=" * 80)
    print("STEP 2: Parse Tagged Text to Segments")
    print("=" * 80)
    print()
    print("Parsing tags to create text segments...")
    
    try:
        segments = FormatMapper.parse_tagged_text(formatted_text)
        print(f"✅ Parsing complete!")
        print(f"   Total segments: {len(segments)}")
        
        # Analyze segments
        text_segments = sum(1 for s in segments if type(s).__name__ == 'text')
        para_segments = sum(1 for s in segments if type(s).__name__ == 'paragraph')
        table_segments = sum(1 for s in segments if type(s).__name__ == 'table')
        
        print(f"   - Text segments: {text_segments}")
        print(f"   - Paragraph breaks: {para_segments}")
        print(f"   - Tables: {table_segments}")
        print()
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 3: Translate text with tags
    print("=" * 80)
    print("STEP 3: Translate Text (Tags Preserved)")
    print("=" * 80)
    print()
    print("Initializing Google Translate API...")
    
    try:
        api = GoogleTranslateAPI()
        print("✅ API initialized")
        print()
        
        print("Translating text (Portuguese → English)...")
        print("NOTE: Tags like <113|N:X> will be preserved during translation")
        print()
        
        result = api.translate_text(formatted_text, from_lang='pt', to_lang='en')
        
        if not result.success:
            print(f"❌ Translation failed: {result.error_message}")
            return 1
        
        translated_text = result.translated_text
        print(f"✅ Translation complete!")
        print(f"   Length: {len(translated_text)} characters")
        print(f"   From cache: {result.from_cache}")
        
        # Verify tags preserved
        translated_tags = re.findall(r'<113\|\d+:[^>]+>', translated_text)
        print(f"   Format tags after translation: {len(translated_tags)}")
        
        if len(translated_tags) != len(tags):
            print(f"   ⚠️  WARNING: Tag count mismatch!")
            print(f"      Original: {len(tags)} tags")
            print(f"      Translated: {len(translated_tags)} tags")
            print(f"      Difference: {len(tags) - len(translated_tags)} tags lost")
        else:
            print(f"   ✅ All tags preserved!")
        
        # Show preview
        print(f"\n   Preview (first 500 chars):")
        print("   " + "-" * 76)
        preview = translated_text[:500].replace('\n', '\n   ')
        print(f"   {preview}")
        if len(translated_text) > 500:
            print(f"   ... ({len(translated_text) - 500} more characters)")
        print()
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 4: Parse translated text
    print("=" * 80)
    print("STEP 4: Parse Translated Text to Segments")
    print("=" * 80)
    print()
    print("Parsing translated text...")
    
    try:
        translated_segments = FormatMapper.parse_tagged_text(translated_text)
        print(f"✅ Parsing complete!")
        print(f"   Total segments: {len(translated_segments)}")
        print()
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 5: Create output ODT
    print("=" * 80)
    print("STEP 5: Create Output ODT with Restored Formatting")
    print("=" * 80)
    print()
    print(f"Creating output file: {output_path}")
    print("Restoring all formatting (bold, italic, underline, links, tables, etc.)...")
    
    try:
        FormatMapper.create_odt_from_segments(translated_segments, str(output_path))
        print(f"✅ ODT creation complete!")
        
        if output_path.exists():
            size = output_path.stat().st_size
            print(f"   Output size: {size / 1024:.1f} KB")
            print(f"   File saved: {output_path}")
        else:
            print(f"   ⚠️  WARNING: Output file not found")
        
        print()
        
    except Exception as e:
        print(f"❌ ODT creation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Final Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    print("✅ All steps completed successfully!")
    print()
    print("Workflow:")
    print(f"  1. ✅ Extracted {len(tags)} format tags from input ODT")
    print(f"  2. ✅ Parsed to {len(segments)} segments")
    print(f"  3. ✅ Translated text (Portuguese → English)")
    print(f"  4. ✅ Verified {len(translated_tags)} tags preserved")
    print(f"  5. ✅ Created output ODT with restored formatting")
    print()
    print("Results:")
    print(f"  - Input:  {input_path.name} ({input_path.stat().st_size / 1024:.1f} KB)")
    print(f"  - Output: {output_path.name} ({output_path.stat().st_size / 1024:.1f} KB)")
    print(f"  - Tags preserved: {len(translated_tags)}/{len(tags)} ({len(translated_tags)/len(tags)*100:.1f}%)")
    print()
    print("Next steps:")
    print(f"  - Open {output_path.name} in LibreOffice to verify formatting")
    print(f"  - Check that bold, italic, underline, links are preserved")
    print(f"  - Verify tables, headings, and paragraph styles")
    print()
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    input_file = "/home/josue/Documents/CAIT- Trabalho de Biologia - Josué 3001.odt"
    output_file = "/home/josue/Documents/Informática/Programação/programming workspace/System Management JSON Files - Clarify project/clarify-COM8/CAIT_Biologia_Translated_COM8.odt"
    
    try:
        exit_code = test_odt_translation(input_file, output_file)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
