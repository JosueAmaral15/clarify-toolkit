#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Different HTML Formats with Google Translate (COM8)

This script tests various HTML formatting approaches to find which one
Google Translate preserves best during translation.

Author: COM8
Date: 2026-02-15
Protocol: SIMPLICITY_PROTOCOL_3
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Test output directory
OUTPUT_DIR = Path(".test_outputs/com8/format_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def translate_google(text: str, from_lang: str = "pt", to_lang: str = "en") -> str:
    """
    Call Google Translate free endpoint.
    
    Args:
        text: Text to translate (can be plain or HTML)
        from_lang: Source language code
        to_lang: Target language code
    
    Returns:
        Translated text
    """
    try:
        # Rate limiting
        time.sleep(0.6)
        
        base_url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': from_lang,
            'tl': to_lang,
            'dt': 't',
            'q': text
        }
        
        url = f"{base_url}?" + urllib.parse.urlencode(params)
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        
        # nosec B310: URL is always HTTPS googleapis.com
        with urllib.request.urlopen(req, timeout=10) as response:  # nosec
            data = response.read().decode('utf-8')
        
        # Parse response - it's a JSON array
        result = json.loads(data)
        
        # Extract translated text from nested array structure
        if result and isinstance(result[0], list):
            translations = [item[0] for item in result[0] if item and item[0]]
            return ''.join(translations)
        
        return ""
    
    except Exception as e:
        return f"ERROR: {str(e)}"


def test_format(name: str, source_html: str, description: str) -> dict:
    """
    Test a specific HTML format.
    
    Args:
        name: Test name
        source_html: HTML to translate
        description: What this test is checking
    
    Returns:
        Test result dictionary
    """
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    print(f"Description: {description}")
    print(f"\nSource HTML ({len(source_html)} chars):")
    print(source_html[:200] + ("..." if len(source_html) > 200 else ""))
    
    # Translate
    print("\nTranslating...")
    translated = translate_google(source_html, "pt", "en")
    
    print(f"\nTranslated Result ({len(translated)} chars):")
    print(translated[:200] + ("..." if len(translated) > 200 else ""))
    
    # Analyze preservation
    analysis = {
        'name': name,
        'description': description,
        'source_length': len(source_html),
        'result_length': len(translated),
        'source': source_html,
        'result': translated,
        'has_span_tags': '<span' in translated,
        'has_class_attributes': 'class=' in translated,
        'has_inline_styles': 'style=' in translated,
        'has_data_attributes': 'data-' in translated,
        'has_br_tags': '<br' in translated,
        'has_html_entities': '&#' in translated,
        'error': translated.startswith('ERROR:')
    }
    
    # Check if format was preserved
    if analysis['error']:
        analysis['preserved'] = False
        analysis['quality'] = 'FAIL'
    elif '<span' not in source_html:
        # Test without spans (baseline)
        analysis['preserved'] = 'N/A'
        analysis['quality'] = 'BASELINE'
    elif analysis['has_span_tags']:
        if 'class=' in source_html and analysis['has_class_attributes']:
            analysis['preserved'] = True
            analysis['quality'] = 'EXCELLENT'
        elif 'style=' in source_html and analysis['has_inline_styles']:
            analysis['preserved'] = True
            analysis['quality'] = 'EXCELLENT'
        elif 'data-' in source_html and analysis['has_data_attributes']:
            analysis['preserved'] = True
            analysis['quality'] = 'EXCELLENT'
        else:
            analysis['preserved'] = False
            analysis['quality'] = 'PARTIAL'
    else:
        analysis['preserved'] = False
        analysis['quality'] = 'POOR'
    
    print(f"\n✓ Analysis:")
    print(f"  - Preserved: {analysis['preserved']}")
    print(f"  - Quality: {analysis['quality']}")
    print(f"  - Has <span>: {analysis['has_span_tags']}")
    print(f"  - Has class=: {analysis['has_class_attributes']}")
    print(f"  - Has style=: {analysis['has_inline_styles']}")
    
    # Save to file
    output_file = OUTPUT_DIR / f"{name.lower().replace(' ', '_')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved to: {output_file}")
    
    return analysis


def main():
    """Run all format tests."""
    print("="*80)
    print("GOOGLE TRANSLATE HTML FORMAT TESTS (COM8)")
    print("="*80)
    print("\nTesting different HTML formats to find best preservation...")
    print("Source: Portuguese biology text about GMOs")
    print("Target: English translation")
    
    results = []
    
    # Test 1: Plain text (baseline)
    results.append(test_format(
        "Test 1 - Plain Text",
        "Trabalho de Biologia sobre Transgênicos",
        "Baseline test - no formatting"
    ))
    
    # Test 2: Span with CSS class (current approach)
    results.append(test_format(
        "Test 2 - Span with Class",
        '<span class="fmt5">Trabalho de Biologia</span>',
        "Current approach - CSS classes"
    ))
    
    # Test 3: Span with inline style
    results.append(test_format(
        "Test 3 - Span with Inline Style",
        '<span style="font-weight: bold; font-size: 16pt;">Trabalho de Biologia</span>',
        "Inline CSS styles instead of classes"
    ))
    
    # Test 4: Multiple spans with classes
    results.append(test_format(
        "Test 4 - Multiple Spans Classes",
        '<span class="fmt4">Nome:</span> <span class="fmt2">Josué</span>',
        "Multiple formatted segments with classes"
    ))
    
    # Test 5: Multiple spans with inline styles
    results.append(test_format(
        "Test 5 - Multiple Spans Styles",
        '<span style="font-weight: bold;">Nome:</span> <span style="font-size: 12pt;">Josué</span>',
        "Multiple formatted segments with inline styles"
    ))
    
    # Test 6: Span with data attribute
    results.append(test_format(
        "Test 6 - Span with Data Attr",
        '<span data-fmt="fmt5">Trabalho de Biologia</span>',
        "Data attributes as format markers"
    ))
    
    # Test 7: Semantic tags (b, i)
    results.append(test_format(
        "Test 7 - Semantic Tags",
        '<b>Trabalho de Biologia</b>',
        "Use semantic HTML tags"
    ))
    
    # Test 8: Div with class
    results.append(test_format(
        "Test 8 - Div with Class",
        '<div class="fmt5">Trabalho de Biologia</div>',
        "DIV instead of SPAN"
    ))
    
    # Test 9: Complex HTML with BR and entities
    results.append(test_format(
        "Test 9 - Complex HTML",
        '<span class="fmt4">Nome:</span><span class="fmt2"> Josué&#9;</span><br><span class="fmt4">Turma:</span><span class="fmt2"> 3001</span>',
        "Complex structure with BR tags and HTML entities"
    ))
    
    # Test 10: Full HTML document structure
    results.append(test_format(
        "Test 10 - Full HTML Doc",
        '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
<span class="fmt5">Trabalho de Biologia</span>
</body>
</html>''',
        "Complete HTML document structure"
    ))
    
    # Generate comparison report
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    print("\n{:<30} {:<15} {:<15}".format("Test", "Quality", "Preserved"))
    print("-"*80)
    
    for result in results:
        preserved_str = str(result['preserved'])
        print("{:<30} {:<15} {:<15}".format(
            result['name'][:28],
            result['quality'],
            preserved_str
        ))
    
    # Save summary
    summary_file = OUTPUT_DIR / "test_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Full summary saved to: {summary_file}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    excellent = [r for r in results if r['quality'] == 'EXCELLENT']
    if excellent:
        print("\n✅ EXCELLENT formats (use these):")
        for r in excellent:
            print(f"  - {r['name']}: {r['description']}")
    
    partial = [r for r in results if r['quality'] == 'PARTIAL']
    if partial:
        print("\n⚠️  PARTIAL preservation (use with caution):")
        for r in partial:
            print(f"  - {r['name']}: {r['description']}")
    
    poor = [r for r in results if r['quality'] == 'POOR']
    if poor:
        print("\n❌ POOR formats (avoid these):")
        for r in poor:
            print(f"  - {r['name']}: {r['description']}")
    
    failed = [r for r in results if r['quality'] == 'FAIL']
    if failed:
        print("\n💥 FAILED (errors occurred):")
        for r in failed:
            print(f"  - {r['name']}: {r['result'][:80]}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nResults saved to: {OUTPUT_DIR}")
    print("\nNext steps:")
    print("1. Review test results in JSON files")
    print("2. Choose best format based on preservation quality")
    print("3. Update HTMLFormatMapper to use chosen format")
    print("4. Test end-to-end with actual ODT files")


if __name__ == '__main__':
    main()
