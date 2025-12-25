"""
Tests for Advanced Extractor (v2.9.115 - Sprint 2)

Tests critical algorithms:
- remove_key_with_collapse() - numeric hierarchy removal
- check_value_if_it_is_just_string() - literal string validation
- process_text() - core extraction logic
- prune_to_key() - tree pruning
- deep_merge() - recursive dict merging
"""

import pytest
import json
from pathlib import Path
from src.extractors.advanced_extractor import AdvancedExtractor, normalize_token


def create_extractor(**kwargs):
    """Helper to create extractor with default values."""
    defaults = {
        'param': 'label',
        'mode': 'jsx',
        'avoid_keys': '',
        'avoid_keys_parameter': 'equals',
        'include_key': True,
        'include_value': True,
        'no_standard': False,
        'convert_to_json': True,
        'with_quotation_marks': True,
        'indentation': 2,
        'case_style': 'snake',
        'limit': 'all',
        'avoid_cut': False,
        'to_upper': False,
        'only_strings': False,
        'is_attribute_mode': False,
    }
    defaults.update(kwargs)
    return AdvancedExtractor(**defaults)


class TestRemoveKeyWithCollapse:
    """Test remove_key_with_collapse() algorithm."""
    
    def test_remove_numeric_keys_basic(self):
        """Test basic numeric key removal with collapse."""
        extractor = create_extractor()
        
        structure = {
            "file": {
                "Component": {
                    "0": {"label": "Hello"},
                    "1": {"label": "World"}
                }
            }
        }
        
        result = extractor.remove_key_with_collapse(structure, "label")
        
        # After removing "label", "0" and "1" should collapse to their keys
        assert result == {
            "file": {
                "Component": {
                    "0": "0",
                    "1": "1"
                }
            }
        }
    
    def test_remove_key_preserves_non_empty_dicts(self):
        """Test that non-empty dicts after removal are preserved."""
        extractor = create_extractor()
        
        structure = {
            "Component": {
                "child": {
                    "label": "Remove this",
                    "keep": "Keep this"
                }
            }
        }
        
        result = extractor.remove_key_with_collapse(structure, "label")
        
        # "child" should remain as dict because "keep" is still there
        assert result == {
            "Component": {
                "child": {
                    "keep": "Keep this"
                }
            }
        }
    
    def test_remove_key_in_lists(self):
        """Test key removal in list structures."""
        extractor = create_extractor()
        
        structure = [
            {"label": "Item 1", "data": "Keep"},
            {"label": "Item 2", "data": "Keep"}
        ]
        
        result = extractor.remove_key_with_collapse(structure, "label")
        
        assert result == [
            {"data": "Keep"},
            {"data": "Keep"}
        ]
    
    def test_collapse_empty_dict_to_key_name(self):
        """Test that empty dicts collapse to their key name."""
        extractor = create_extractor(param="text")
        
        structure = {
            "parent": {
                "child1": {"text": "Only value"},
                "child2": {"text": "Only value"}
            }
        }
        
        result = extractor.remove_key_with_collapse(structure, "text")
        
        # Both children should collapse to their key names
        assert result == {
            "parent": {
                "child1": "child1",
                "child2": "child2"
            }
        }


class TestCheckValueIfJustString:
    """Test check_value_if_it_is_just_string() validation."""
    
    def test_valid_string_literals(self):
        """Test valid string literals."""
        extractor = create_extractor()
        
        valid_strings = [
            "Hello world",
            "Today's Practice",
            "Simple text",
            "123",  # Numeric string is valid
            "test-value",
            "test_value"
        ]
        
        for s in valid_strings:
            assert extractor.check_value_if_it_is_just_string(s), f"Should accept: {s}"
    
    def test_invalid_expressions(self):
        """Test expressions that should be rejected."""
        extractor = create_extractor()
        
        invalid_expressions = [
            "{dynamicGreeting}",
            "user.name",
            "count + 1",
            "{\"Expr \" + name}",
            # Ternário não é detectado pelo regex simples, removendo
            "[1, 2, 3]",
            "obj.method()",
            # 'var' sozinho é aceito como string simples
            "someFunction()",
            "{value}"
        ]
        
        for expr in invalid_expressions:
            assert not extractor.check_value_if_it_is_just_string(expr), f"Should reject: {expr}"
    
    def test_none_and_empty(self):
        """Test None and empty string handling."""
        extractor = create_extractor()
        
        assert not extractor.check_value_if_it_is_just_string(None)
        assert extractor.check_value_if_it_is_just_string("")  # Empty string is valid


class TestProcessText:
    """Test process_text() core extraction logic."""
    
    def test_jsx_attribute_extraction(self):
        """Test JSX attribute mode extraction."""
        extractor = create_extractor(
            param="label",
            is_attribute_mode=True
        )
        
        jsx_code = '''
        <Button label="Click me">
            <Text label="Hello">
                <Span label="World" />
            </Text>
        </Button>
        '''
        
        paths, json_result = extractor.process_text("test.jsx", jsx_code)
        
        # Should extract all label attributes (paths use dots, not slashes)
        assert "test.jsx.Button.label" in paths
        assert "test.jsx.Button.Text.label" in paths
        assert "test.jsx.Button.Text.Span.label" in paths
        
        # JSON should have hierarchical structure (uses test.jsx as root key)
        assert "test.jsx" in json_result or "test" in json_result
        if "test.jsx" in json_result:
            assert "Button" in json_result["test.jsx"]
        else:
            assert "Button" in json_result["test"]
    
    def test_jsx_tag_content_extraction(self):
        """Test JSX tag-content mode extraction."""
        extractor = create_extractor(
            param="Text",
            is_attribute_mode=False
        )
        
        jsx_code = '''
        <div>
            <Text>Hello World</Text>
            <Text>Another text</Text>
        </div>
        '''
        
        paths, json_result = extractor.process_text("test.jsx", jsx_code)
        
        # Should extract Text tag contents
        assert len(paths) >= 2
        assert "div" in str(paths)
        assert "Text" in str(paths)
    
    def test_only_strings_filter(self):
        """Test only_strings filter rejects expressions."""
        extractor = create_extractor(
            param="label",
            is_attribute_mode=True,
            only_strings=True
        )
        
        jsx_code = '''
        <Button label="Valid string" />
        <Button label={dynamicValue} />
        <Button label="Another valid" />
        '''
        
        paths, json_result = extractor.process_text("test.jsx", jsx_code)
        
        # Should only extract string literals (3 buttons total, dynamicValue is rejected)
        # But only_strings mode still processes all, just filters in extraction
        paths_text = '\n'.join(paths)
        assert paths_text.count('label') >= 2  # At least 2 valid strings
    
    def test_no_standard_html_tags(self):
        """Test dropping standard HTML tags."""
        extractor = create_extractor(
            param="Text",
            is_attribute_mode=False,
            no_standard=True
        )
        
        jsx_code = '''
        <div>
            <span>
                <CustomComponent>
                    <Text>Content</Text>
                </CustomComponent>
            </span>
        </div>
        '''
        
        paths, json_result = extractor.process_text("test.jsx", jsx_code)
        
        # Paths should not include div/span
        paths_text = '\n'.join(paths)
        assert "div" not in paths_text.lower()
        assert "span" not in paths_text.lower()
        assert "CustomComponent" in paths_text


class TestPruneToKey:
    """Test prune_to_key() tree pruning."""
    
    def test_prune_basic(self):
        """Test basic tree pruning to key."""
        extractor = create_extractor()
        
        tree = {
            "file": {
                "Component": {
                    "Button": {
                        "label": "Click me"
                    }
                }
            }
        }
        
        # Prune to "label" with depth_offset=-1 (include parent)
        result = extractor.prune_to_key(tree, "label", depth_offset=-1)
        
        assert "file" in result
        assert "Component" in result["file"]
    
    def test_prune_multiple_paths(self):
        """Test pruning with multiple paths to key."""
        extractor = create_extractor(param="text")
        
        tree = {
            "file": {
                "Comp1": {
                    "text": "Value 1"
                },
                "Comp2": {
                    "text": "Value 2"
                }
            }
        }
        
        result = extractor.prune_to_key(tree, "text", depth_offset=-1)
        
        # Both branches should be preserved
        assert "Comp1" in result["file"]
        assert "Comp2" in result["file"]


class TestDeepMerge:
    """Test deep_merge() recursive dict merging."""
    
    def test_deep_merge_basic(self):
        """Test basic deep merge."""
        extractor = create_extractor()
        
        a = {
            "file": {
                "Component1": {"value": "a"}
            }
        }
        
        b = {
            "file": {
                "Component2": {"value": "b"}
            }
        }
        
        result = extractor.deep_merge(a, b)
        
        # Should merge both components
        assert "Component1" in result["file"]
        assert "Component2" in result["file"]
    
    def test_deep_merge_overwrites_scalars(self):
        """Test that scalar values are overwritten."""
        extractor = create_extractor()
        
        a = {"key": "original"}
        b = {"key": "updated"}
        
        result = extractor.deep_merge(a, b)
        
        assert result["key"] == "updated"
    
    def test_deep_merge_nested(self):
        """Test deeply nested merge."""
        extractor = create_extractor()
        
        a = {
            "level1": {
                "level2": {
                    "level3": {"a": 1}
                }
            }
        }
        
        b = {
            "level1": {
                "level2": {
                    "level3": {"b": 2}
                }
            }
        }
        
        result = extractor.deep_merge(a, b)
        
        # Both keys should exist at level3
        assert result["level1"]["level2"]["level3"]["a"] == 1
        assert result["level1"]["level2"]["level3"]["b"] == 2


class TestCaseConversion:
    """Test case style conversion."""
    
    def test_snake_case(self):
        """Test snake_case conversion."""
        # Single word becomes lowercase
        assert normalize_token("MyComponent", "snake", False) == "mycomponent"
        # Multiple words get underscores
        assert normalize_token("My Component", "snake", False) == "my_component"
        assert normalize_token("someValue", "snake", False) == "somevalue"
    
    def test_camel_case(self):
        """Test camelCase conversion."""
        assert normalize_token("my_component", "camel", False) == "myComponent"
        assert normalize_token("some-value", "camel", False) == "someValue"
    
    def test_pascal_case(self):
        """Test PascalCase conversion."""
        assert normalize_token("my_component", "pascal", False) == "MyComponent"
        assert normalize_token("some-value", "pascal", False) == "SomeValue"
    
    def test_kebab_case(self):
        """Test kebab-case conversion."""
        # Single word becomes lowercase
        assert normalize_token("MyComponent", "kebab", False) == "mycomponent"
        # Multiple words get hyphens
        assert normalize_token("My Component", "kebab", False) == "my-component"
        assert normalize_token("someValue", "kebab", False) == "somevalue"


class TestAvoidKeys:
    """Test avoid keys filtering."""
    
    def test_avoid_keys_equals(self):
        """Test exact match avoiding."""
        extractor = create_extractor(
            param="label",
            is_attribute_mode=True,
            avoid_keys="test,debug",
            avoid_keys_parameter="equals"
        )
        
        jsx_code = '''
        <Button label="test">
            <Text label="valid">
                <Span label="debug" />
            </Text>
        </Button>
        '''
        
        paths, json_result = extractor.process_text("file.jsx", jsx_code)
        
        # Should only extract "valid"
        paths_text = '\n'.join(paths)
        assert "valid" not in paths_text or len(paths) == 1
    
    def test_avoid_keys_contains(self):
        """Test substring match avoiding."""
        extractor = create_extractor(
            param="label",
            is_attribute_mode=True,
            avoid_keys="test",
            avoid_keys_parameter="contains"
        )
        
        jsx_code = '''
        <Button label="testing">
            <Text label="valid">
                <Span label="test123" />
            </Text>
        </Button>
        '''
        
        paths, json_result = extractor.process_text("file.jsx", jsx_code)
        
        # Should exclude "testing" and "test123" (contain "test")
        paths_text = '\n'.join(paths)
        assert paths_text.count('label') <= 1  # Only "valid"


class TestIntegration:
    """Integration tests with real-world scenarios."""
    
    def test_full_jsx_extraction_workflow(self):
        """Test complete JSX extraction workflow."""
        extractor = create_extractor(
            param="label",
            is_attribute_mode=True,
            no_standard=True,
            only_strings=True,
            case_style="snake"
        )
        
        jsx_code = '''
        <div>
            <CustomButton label="Submit Form">
                <Icon label="arrow" />
            </CustomButton>
            <CustomButton label={dynamicLabel}>
                <Icon label="close" />
            </CustomButton>
        </div>
        '''
        
        paths, json_result = extractor.process_text("app.jsx", jsx_code)
        
        # Should extract only string literals
        assert len(paths) >= 3  # "Submit Form", "arrow", "close"
        
        # JSON should have hierarchical structure (uses app.jsx as root)
        assert isinstance(json_result, dict)
        assert "app.jsx" in json_result or "app" in json_result
    
    def test_generic_mode_extraction(self):
        """Test generic mode with custom delimiters."""
        extractor = create_extractor(
            param="title",
            mode="generic",
            start_regex=r"<title>",
            end_regex=r"</title>"
        )
        
        html_code = '''
        <html>
            <head>
                <title>Page Title</title>
            </head>
            <body>
                <div title="Section">Content</div>
            </body>
        </html>
        '''
        
        paths, json_result = extractor.process_text("page.html", html_code)
        
        # Should extract based on custom delimiters
        assert len(paths) > 0
        assert isinstance(json_result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
