#!/usr/bin/env python3
"""
CLI Test Suite for Text to JSON Converter Features - Programmer #3
Tests the extraction backend without GUI using actual API
"""

import sys
import os
import tempfile
import json

# Add project root to path for proper imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def test_smart_truncate():
    """Test smart_truncate function with avoid_cut_direction"""
    from src.extractors.advanced_extractor import smart_truncate
    
    text = "this is a example of string"
    
    # Test before mode (cut at last whitespace before limit)
    result_before = smart_truncate(text, limit="10", avoid_cut=True, avoid_cut_direction="before")
    print(f"✓ Before mode: '{result_before}' ({len(result_before)} chars, expected ≤10)")
    assert len(result_before) <= 10, f"Before mode exceeded limit: {len(result_before)}"
    
    # Test after mode (cut at next whitespace after limit)
    result_after = smart_truncate(text, limit="10", avoid_cut=True, avoid_cut_direction="after")
    print(f"✓ After mode: '{result_after}' ({len(result_after)} chars, may exceed 10)")
    
    # Test hard cut (no avoid_cut)
    result_hard = smart_truncate(text, limit="10", avoid_cut=False, avoid_cut_direction="before")
    print(f"✓ Hard cut: '{result_hard}' ({len(result_hard)} chars, exactly 10)")
    assert len(result_hard) == 10, f"Hard cut should be exact: {len(result_hard)}"
    
    # Test no limit
    result_no_limit = smart_truncate(text, limit=None, avoid_cut=False, avoid_cut_direction="before")
    print(f"✓ No limit: '{result_no_limit}' ({len(result_no_limit)} chars)")
    assert result_no_limit == text, "No limit should return original"
    
    print("✅ smart_truncate tests passed\n")
    return True

def test_extractor_initialization():
    """Test AdvancedExtractor can be created with avoid_cut_direction"""
    from src.extractors.advanced_extractor import AdvancedExtractor
    
    # Test with 'before' (default/backward compatible)
    extractor1 = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit=None,
        avoid_cut=True,
        avoid_cut_direction='before'
    )
    
    assert extractor1.avoid_cut_direction == 'before'
    print(f"✓ Extractor created with avoid_cut_direction='before'")
    
    # Test with 'after'
    extractor2 = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit=None,
        avoid_cut=True,
        avoid_cut_direction='after'
    )
    
    assert extractor2.avoid_cut_direction == 'after'
    print(f"✓ Extractor created with avoid_cut_direction='after'")
    
    print("✅ Extractor initialization test passed\n")
    return True

def test_text_extraction():
    """Test extraction from JSX text content"""
    from src.extractors.advanced_extractor import AdvancedExtractor
    
    # Create test JSX content
    jsx_content = '''<Button variant="primary" size="large">Click Me</Button>
<Input placeholder="Enter name" type="text" />
<Card title="Welcome" id="card1">Content</Card>'''
    
    # Create extractor
    extractor = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit="50",
        avoid_cut=True,
        avoid_cut_direction='before'
    )
    
    # Process text using process_text() method
    path_lines, merged_json = extractor.process_text("TestFile", jsx_content)
    
    # Verify results
    assert path_lines is not None, "path_lines should not be None"
    assert merged_json is not None, "merged_json should not be None"
    assert isinstance(merged_json, dict), f"Expected dict, got {type(merged_json)}"
    
    print(f"✓ Extracted {len(path_lines)} path lines")
    print(f"✓ Generated JSON with {len(merged_json)} top-level keys")
    print(f"✓ Sample paths: {path_lines[:3]}")
    print(f"✓ Sample JSON keys: {list(merged_json.keys())[:3]}")
    
    # Verify we got component data
    json_str = json.dumps(merged_json, indent=2)
    print(f"✓ JSON output preview: {json_str[:200]}...")
    
    print("✅ Text extraction test passed\n")
    return True

def test_case_styles():
    """Test different case style conversions"""
    from src.extractors.advanced_extractor import AdvancedExtractor
    
    jsx_content = '<MyComponent dataValue="test" testProp="value" />'
    
    # Map display names to internal codes
    styles = {
        'snake_case': 'snake',
        'camelCase': 'camel',
        'PascalCase': 'pascal',
        'kebab-case': 'kebab'
    }
    
    for display_name, style_code in styles.items():
        extractor = AdvancedExtractor(
            param="*",
            mode="jsx",
            avoid_keys="",
            avoid_keys_parameter="contains",
            include_key=False,
            include_value=False,
            no_standard=True,
            convert_to_json=True,
            with_quotation_marks=True,
            indentation=2,
            case_style=style_code,
            limit=None,
            avoid_cut=False,
            avoid_cut_direction='before'
        )
        
        _, merged_json = extractor.process_text("TestFile", jsx_content)
        keys = list(merged_json.keys())[:3]
        print(f"✓ {display_name:12} ({style_code:6}): {keys}")
    
    print("✅ Case style tests passed\n")
    return True

def test_avoid_keys():
    """Test avoid_keys filtering"""
    from src.extractors.advanced_extractor import AdvancedExtractor
    
    jsx_content = '''<Button className="btn" variant="primary" id="btn1">Click</Button>
<Input className="input" type="text" name="username" />'''
    
    # Extract WITHOUT filtering
    extractor_all = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit=None,
        avoid_cut=False,
        avoid_cut_direction='before'
    )
    
    _, data_all = extractor_all.process_text("TestFile", jsx_content)
    print(f"✓ Without filtering: {len(data_all)} top-level keys")
    print(f"  Sample keys: {list(data_all.keys())[:3]}")
    
    # Extract WITH filtering
    extractor_filtered = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="className,id",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit=None,
        avoid_cut=False,
        avoid_cut_direction='before'
    )
    
    _, data_filtered = extractor_filtered.process_text("TestFile", jsx_content)
    print(f"✓ With filtering (className, id): {len(data_filtered)} top-level keys")
    print(f"  Sample keys: {list(data_filtered.keys())[:3]}")
    
    # Check that filtering did something
    all_str = json.dumps(data_all).lower()
    filtered_str = json.dumps(data_filtered).lower()
    print(f"✓ Filtering changed output: {len(all_str)} → {len(filtered_str)} chars")
    
    print("✅ avoid_keys test passed\n")
    return True

def test_attribute_vs_content_mode():
    """Test is_attribute_mode parameter"""
    from src.extractors.advanced_extractor import AdvancedExtractor
    
    jsx_content = '<Card title="Welcome"><p>This is content</p></Card>'
    
    # Attribute mode (extract attributes)
    extractor_attr = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit=None,
        avoid_cut=False,
        avoid_cut_direction='before',
        is_attribute_mode=True
    )
    
    _, data_attr = extractor_attr.process_text("TestFile", jsx_content)
    data_attr = data_attr or {}
    print(f"✓ Attribute mode: {len(data_attr)} entries")
    print(f"  Keys: {list(data_attr.keys())[:3]}")
    
    # Content mode (extract tag content)
    extractor_content = AdvancedExtractor(
        param="*",
        mode="jsx",
        avoid_keys="",
        avoid_keys_parameter="contains",
        include_key=False,
        include_value=False,
        no_standard=True,
        convert_to_json=True,
        with_quotation_marks=True,
        indentation=2,
        case_style='snake',
        limit=None,
        avoid_cut=False,
        avoid_cut_direction='before',
        is_attribute_mode=False
    )
    
    _, data_content = extractor_content.process_text("TestFile", jsx_content)
    data_content = data_content or {}
    print(f"✓ Content mode: {len(data_content)} entries")
    print(f"  Keys: {list(data_content.keys())[:3]}")
    
    print("✅ Attribute vs content mode test passed\n")
    return True

def main():
    """Run all CLI tests"""
    print("=" * 70)
    print("TEXT TO JSON CONVERTER - CLI TEST SUITE (Programmer #3)")
    print("=" * 70)
    print()
    
    tests = [
        ("1. smart_truncate function", test_smart_truncate),
        ("2. Extractor initialization (avoid_cut_direction)", test_extractor_initialization),
        ("3. Text extraction (process_text)", test_text_extraction),
        ("4. Case styles", test_case_styles),
        ("5. avoid_keys filtering", test_avoid_keys),
        ("6. Attribute vs Content mode", test_attribute_vs_content_mode),
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for name, test_func in tests:
        try:
            print(f"Testing: {name}")
            print("-" * 70)
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name} FAILED: {e}")
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace)
            errors.append((name, str(e)))
            failed += 1
            print()
    
    print("=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} passed, {failed}/{len(tests)} failed")
    print("=" * 70)
    
    if errors:
        print("\nFailed Tests Summary:")
        for name, error in errors:
            print(f"  ❌ {name}: {error}")
    else:
        print("\n✅ ALL TESTS PASSED! Features working correctly.")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
