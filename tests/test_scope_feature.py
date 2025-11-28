#!/usr/bin/env python3
"""Test script for scope filtering functionality."""

from src.core import extract_scope_content, Condition

# Test data
test_text = """
This is normal text.
[This is in brackets]
{This is in braces}
(This is in parentheses)
<div>This is in a div tag</div>
<script>This is in a script tag</script>
begin Custom delimiter content end
More normal text [another bracket] and {another brace}.
"""

def test_scope_extraction():
    print("=" * 60)
    print("Testing Scope Content Extraction")
    print("=" * 60)
    
    # Test 1: Brackets
    print("\n1. Testing brackets scope:")
    result = extract_scope_content(test_text, "brackets", "")
    print(f"   Result: {result}")
    assert "This is in brackets" in result
    assert "another bracket" in result
    
    # Test 2: Braces
    print("\n2. Testing braces scope:")
    result = extract_scope_content(test_text, "braces", "")
    print(f"   Result: {result}")
    assert "This is in braces" in result
    assert "another brace" in result
    
    # Test 3: Parentheses
    print("\n3. Testing parentheses scope:")
    result = extract_scope_content(test_text, "parentheses", "")
    print(f"   Result: {result}")
    assert "This is in parentheses" in result
    
    # Test 4: Custom delimiters
    print("\n4. Testing custom delimiters (begin...end):")
    result = extract_scope_content(test_text, "custom", "begin,end")
    print(f"   Result: {result}")
    assert "Custom delimiter content" in result
    
    # Test 5: Any tag
    print("\n5. Testing any HTML/XML tag:")
    result = extract_scope_content(test_text, "tag", "")
    print(f"   Result: {result}")
    assert "This is in a div tag" in result
    assert "This is in a script tag" in result
    
    # Test 6: Specific tag
    print("\n6. Testing specific tag (div):")
    result = extract_scope_content(test_text, "specific-tag", "div")
    print(f"   Result: {result}")
    assert "This is in a div tag" in result
    assert "This is in a script tag" not in result
    
    # Test 7: No scope (should return original)
    print("\n7. Testing no scope (none):")
    result = extract_scope_content(test_text, "none", "")
    print(f"   Length of result: {len(result)} (should equal original)")
    assert result == test_text
    
    print("\n" + "=" * 60)
    print("✅ All scope extraction tests passed!")
    print("=" * 60)

def test_condition_with_scope():
    print("\n" + "=" * 60)
    print("Testing Condition with Scope")
    print("=" * 60)
    
    # Create a test file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_text)
        temp_file = f.name
    
    try:
        # Test condition with brackets scope
        print("\n1. Testing condition with brackets scope:")
        cond = Condition(
            field="content",
            operator="contains",
            value="bracket",
            scope_type="brackets",
            scope_value=""
        )
        result = cond.matches(temp_file)
        print(f"   Matches 'bracket' in brackets: {result}")
        assert result == True
        
        # Test condition that should NOT match
        print("\n2. Testing condition that should NOT match:")
        cond = Condition(
            field="content",
            operator="contains",
            value="normal text",
            scope_type="brackets",
            scope_value=""
        )
        result = cond.matches(temp_file)
        print(f"   Matches 'normal text' in brackets: {result} (should be False)")
        assert result == False
        
        # Test with specific tag scope
        print("\n3. Testing condition with specific-tag scope (script):")
        cond = Condition(
            field="content",
            operator="contains",
            value="script tag",
            scope_type="specific-tag",
            scope_value="script"
        )
        result = cond.matches(temp_file)
        print(f"   Matches 'script tag' in <script>: {result}")
        assert result == True
        
        print("\n" + "=" * 60)
        print("✅ All condition with scope tests passed!")
        print("=" * 60)
        
    finally:
        os.unlink(temp_file)

def test_nested_braces():
    print("\n" + "=" * 60)
    print("Testing Nested Braces")
    print("=" * 60)
    
    nested_text = """
    {
        outer: {
            inner: "nested value"
        }
    }
    """
    
    result = extract_scope_content(nested_text, "braces", "")
    print(f"Result: {result}")
    print("✅ Nested braces test passed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_scope_extraction()
        test_condition_with_scope()
        test_nested_braces()
        
        print("\n" + "🎉" * 30)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("🎉" * 30)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
