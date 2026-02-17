#!/usr/bin/env python3
"""
Test whitespace and HTML entity preservation through Google Translate.
Tests various approaches to preserve tabs and spaces.
"""

import sys
sys.path.insert(0, 'src')

from translation.google_translate import GoogleTranslateAPI
import time

def test_entity_preservation():
    """Test how Google Translate handles different HTML entities and spacing."""
    
    print("="*80)
    print("WHITESPACE PRESERVATION TESTS")
    print("="*80)
    
    translator = GoogleTranslateAPI()
    
    test_cases = [
        # Test 1: Tab entity
        {
            "name": "Tab entity (&#9;)",
            "html": '<span class="a">CAIT</span><span class="b">&#9;</span><span class="c">13/11/12</span>',
            "expected": "Tab preserved as tab or spaces"
        },
        
        # Test 2: Non-breaking space entity
        {
            "name": "Non-breaking space (&#160;)",
            "html": '<span class="a">CAIT</span><span class="b">&#160;</span><span class="c">13/11/12</span>',
            "expected": "Non-breaking space preserved"
        },
        
        # Test 3: Named entity &nbsp;
        {
            "name": "Named entity (&nbsp;)",
            "html": '<span class="a">CAIT</span><span class="b">&nbsp;</span><span class="c">13/11/12</span>',
            "expected": "Non-breaking space preserved"
        },
        
        # Test 4: Multiple non-breaking spaces
        {
            "name": "Multiple &nbsp; (simulating tab)",
            "html": '<span class="a">CAIT</span><span class="b">&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="c">13/11/12</span>',
            "expected": "Multiple spaces preserved"
        },
        
        # Test 5: Regular space in span
        {
            "name": "Regular space",
            "html": '<span class="a">CAIT</span><span class="b"> </span><span class="c">13/11/12</span>',
            "expected": "Single space"
        },
        
        # Test 6: Multiple regular spaces
        {
            "name": "Multiple regular spaces",
            "html": '<span class="a">CAIT</span><span class="b">    </span><span class="c">13/11/12</span>',
            "expected": "Collapsed to single space"
        },
        
        # Test 7: Space between adjacent spans
        {
            "name": "Adjacent spans with space between tags",
            "html": '<span class="a">word1</span> <span class="b">word2</span>',
            "expected": "Space preserved"
        },
        
        # Test 8: Adjacent spans without space
        {
            "name": "Adjacent spans NO space",
            "html": '<span class="a">word1</span><span class="b">word2</span>',
            "expected": "No space - merged"
        },
        
        # Test 9: Unicode tab character
        {
            "name": "Unicode tab (U+0009)",
            "html": '<span class="a">CAIT</span><span class="b">\t</span><span class="c">13/11/12</span>',
            "expected": "Tab or space"
        },
        
        # Test 10: Pre-formatted space
        {
            "name": "Pre tag with spaces",
            "html": '<pre><span>CAIT</span>    <span>13/11/12</span></pre>',
            "expected": "Spaces preserved (pre tag)"
        },
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"Input HTML:\n  {test['html']}")
        print(f"Expected: {test['expected']}")
        
        # Translate (Portuguese text for testing)
        result = translator.translate_text(test['html'], from_lang='en', to_lang='pt')
        
        if result.success:
            output = result.translated_text
            print(f"\nOutput HTML:\n  {output}")
            
            # Analyze whitespace
            input_whitespace = test['html'].count('&#9;') + test['html'].count('&#160;') + test['html'].count('&nbsp;')
            output_whitespace = output.count('&#9;') + output.count('&#160;') + output.count('&nbsp;')
            
            print(f"\nAnalysis:")
            print(f"  Input entities: {input_whitespace}")
            print(f"  Output entities: {output_whitespace}")
            
            # Check if preserved
            if '&#9;' in test['html']:
                preserved = '&#9;' in output
                print(f"  Tab entity preserved: {preserved}")
            elif '&#160;' in test['html']:
                preserved = '&#160;' in output or '&nbsp;' in output
                print(f"  NBSP preserved: {preserved}")
            elif '&nbsp;' in test['html']:
                preserved = '&#160;' in output or '&nbsp;' in output
                print(f"  NBSP preserved: {preserved}")
            
            results.append({
                'test': test['name'],
                'input': test['html'],
                'output': output,
                'success': True
            })
        else:
            print(f"\n❌ Translation FAILED: {result.error_message}")
            results.append({
                'test': test['name'],
                'input': test['html'],
                'output': None,
                'success': False
            })
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r['success'])
    print(f"\nTests completed: {len(results)}")
    print(f"Successful translations: {successful}")
    print(f"Failed translations: {len(results) - successful}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("\nBased on test results:")
    print("1. Best approach for tabs: TBD (see results above)")
    print("2. Best approach for adjacent spans: TBD (see results above)")
    print("3. Entities that work: TBD (see results above)")
    
    return results

if __name__ == '__main__':
    test_entity_preservation()
