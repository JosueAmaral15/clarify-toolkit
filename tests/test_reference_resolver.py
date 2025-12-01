#!/usr/bin/env python3
"""
Unit tests for Reference Resolver (Sprint A v2.9.29)

Tests:
- create_references(): Delete mode, References mode
- resolve_references(): Expand $ref to values
- Integration: Full pipeline with both modes
"""

import unittest
from src.rewriter.types import Obj
from src.rewriter.reference_resolver import create_references, resolve_references


class TestCreateReferencesDelete(unittest.TestCase):
    """Test create_references() in delete mode (default behavior)."""
    
    def test_delete_mode_removes_duplicates(self):
        """Delete mode should remove duplicate objects entirely."""
        obj = Obj([
            ('user', Obj([('name', 'John'), ('age', 30)])),
            ('author', Obj([('name', 'John'), ('age', 30)])),  # Exact duplicate
            ('admin', Obj([('name', 'Jane'), ('age', 25)])),
        ])
        
        result, stats = create_references(obj, mode='delete')
        
        # Should keep only 2 unique objects (user and admin)
        self.assertEqual(len(list(result)), 2)
        self.assertEqual(stats['deleted'], 1)
        self.assertEqual(stats['kept'], 2)
        self.assertEqual(stats['created'], 0)
    
    def test_delete_mode_preserves_first_occurrence(self):
        """First occurrence (lowest line) should be kept."""
        obj = Obj([
            ('first', Obj([('name', 'John')])),
            ('second', Obj([('name', 'John')])),  # Duplicate
            ('third', Obj([('name', 'John')])),   # Duplicate
        ])
        
        result, stats = create_references(obj, mode='delete')
        
        # Should keep only 'first'
        self.assertEqual(len(list(result)), 1)
        self.assertEqual(list(result)[0][0], 'first')
        self.assertEqual(stats['deleted'], 2)


class TestCreateReferencesMode(unittest.TestCase):
    """Test create_references() in references mode."""
    
    def test_references_mode_creates_refs(self):
        """References mode should replace duplicates with $ref strings."""
        obj = Obj([
            ('user', Obj([('name', 'John')])),
            ('author', Obj([('name', 'John')])),  # Duplicate -> $ref
        ])
        
        result, stats = create_references(obj, mode='references', include_line_numbers=False)
        
        # Should have 2 items: original + reference
        self.assertEqual(len(list(result)), 2)
        self.assertEqual(stats['created'], 1)
        self.assertEqual(stats['deleted'], 0)
        
        # Second item should be a reference
        author_value = list(result)[1][1]
        self.assertTrue(isinstance(author_value, str))
        self.assertTrue(author_value.startswith('$ref:'))
    
    def test_references_with_line_numbers(self):
        """Default format should include line numbers."""
        obj = Obj([
            ('user', Obj([('id', 123)])),
            ('copy', Obj([('id', 123)])),
        ])
        
        result, stats = create_references(obj, mode='references', include_line_numbers=True)
        
        # Reference should have format $ref:path:line
        copy_value = list(result)[1][1]
        self.assertRegex(copy_value, r'^\$ref:root\.user:\d+$')


class TestResolveReferences(unittest.TestCase):
    """Test resolve_references() function."""
    
    def test_resolve_basic_reference(self):
        """Should expand $ref:path to actual value."""
        obj = Obj([
            ('user', Obj([('name', 'John')])),
            ('ref', '$ref:root.user'),
        ])
        
        result, stats = resolve_references(obj)
        
        # Reference should be expanded
        self.assertEqual(stats['resolved'], 1)
        self.assertEqual(stats['invalid'], 0)
        
        ref_value = list(result)[1][1]
        self.assertIsInstance(ref_value, Obj)
        self.assertEqual(list(ref_value)[0][1], 'John')  # name = John
    
    def test_resolve_with_line_number(self):
        """Should resolve $ref:path:123 format."""
        obj = Obj([
            ('original', Obj([('value', 42)])),
            ('copy', '$ref:root.original:10'),
        ])
        
        result, stats = resolve_references(obj)
        
        # Should resolve successfully
        self.assertEqual(stats['resolved'], 1)
        copy_value = list(result)[1][1]
        self.assertIsInstance(copy_value, Obj)
    
    def test_invalid_reference_warning(self):
        """Invalid references should trigger warnings and stay as-is."""
        obj = Obj([
            ('user', Obj([('name', 'John')])),
            ('bad_ref', '$ref:nonexistent.path'),
        ])
        
        result, stats = resolve_references(obj)
        
        # Should count as invalid
        self.assertEqual(stats['invalid'], 1)
        self.assertEqual(stats['resolved'], 0)
        
        # Reference should remain unchanged
        bad_ref_value = list(result)[1][1]
        self.assertEqual(bad_ref_value, '$ref:nonexistent.path')


class TestReferenceResolverIntegration(unittest.TestCase):
    """Integration tests for full pipeline."""
    
    def test_full_pipeline_create_then_resolve(self):
        """Create references, then resolve them back."""
        original = Obj([
            ('user', Obj([('name', 'Alice'), ('age', 30)])),
            ('author', Obj([('name', 'Alice'), ('age', 30)])),  # Duplicate
            ('admin', Obj([('name', 'Bob'), ('age', 25)])),
        ])
        
        # Step 1: Create references
        with_refs, create_stats = create_references(original, mode='references', include_line_numbers=False)
        
        self.assertEqual(create_stats['created'], 1)
        self.assertEqual(create_stats['kept'], 2)
        
        # Step 2: Resolve references
        resolved, resolve_stats = resolve_references(with_refs)
        
        self.assertEqual(resolve_stats['resolved'], 1)
        self.assertEqual(resolve_stats['invalid'], 0)
        
        # Result should have 3 items with actual values (no $ref strings)
        self.assertEqual(len(list(resolved)), 3)
        for key, value in resolved:
            self.assertNotIsInstance(value, str)  # No string refs
            self.assertIsInstance(value, Obj)     # All are objects
    
    def test_stats_accuracy(self):
        """Stats should accurately count created/deleted/resolved refs."""
        obj = Obj([
            ('a', Obj([('x', 1)])),
            ('b', Obj([('x', 1)])),  # Duplicate 1
            ('c', Obj([('y', 2)])),
            ('d', Obj([('x', 1)])),  # Duplicate 2
        ])
        
        result, stats = create_references(obj, mode='references')
        
        # Should create 2 references (b and d)
        self.assertEqual(stats['created'], 2)
        self.assertEqual(stats['kept'], 2)  # a and c
        self.assertEqual(stats['deleted'], 0)
    
    def test_nested_objects_handled(self):
        """Nested objects should be handled correctly."""
        obj = Obj([
            ('config', Obj([
                ('db', Obj([('host', 'localhost'), ('port', 5432)])),
                ('cache', Obj([('host', 'localhost'), ('port', 6379)])),
            ]))
        ])
        
        result, stats = create_references(obj, mode='delete')
        
        # Nested objects with different values should NOT be removed
        config = list(result)[0][1]
        self.assertEqual(len(list(config)), 2)  # Both db and cache


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_object(self):
        """Empty Obj should work without errors."""
        obj = Obj([])
        
        result, stats = create_references(obj, mode='delete')
        
        self.assertEqual(len(list(result)), 0)
        self.assertEqual(stats['deleted'], 0)
        self.assertEqual(stats['kept'], 0)
    
    def test_no_duplicates(self):
        """Objects with no duplicates should pass through unchanged."""
        obj = Obj([
            ('a', Obj([('x', 1)])),
            ('b', Obj([('x', 2)])),
            ('c', Obj([('x', 3)])),
        ])
        
        result, stats = create_references(obj, mode='references')
        
        # Nothing should be created (no duplicates)
        self.assertEqual(stats['created'], 0)
        self.assertEqual(stats['kept'], 3)
    
    def test_primitive_values_ignored(self):
        """Primitive values should not be deduplicated."""
        obj = Obj([
            ('a', 'hello'),
            ('b', 'hello'),  # Same string, but primitives aren't deduplicated
            ('c', 123),
            ('d', 123),
        ])
        
        result, stats = create_references(obj, mode='delete')
        
        # All should be kept (primitives not checked)
        self.assertEqual(len(list(result)), 4)


class TestFormatReference(unittest.TestCase):
    """Test format_reference() helper (Sprint B Feature #4 v2.9.30)."""
    
    def test_format_ref_with_line(self):
        """Test $ref: format with line number."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', 123, '$ref', False)
        self.assertEqual(result, '$ref:root.users.admin:123')
    
    def test_format_ref_without_line(self):
        """Test $ref: format without line number."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', None, '$ref', False)
        self.assertEqual(result, '$ref:root.users.admin')
    
    def test_format_pointer_with_line(self):
        """Test #/ format (JSON Pointer) with line number."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', 456, '#/', False)
        self.assertEqual(result, '#/root.users.admin:456')
    
    def test_format_pointer_without_line(self):
        """Test #/ format without line number."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', None, '#/', False)
        self.assertEqual(result, '#/root.users.admin')
    
    def test_format_at_with_line(self):
        """Test @ format (compact) with line number."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', 789, '@', False)
        self.assertEqual(result, '@root.users.admin:789')
    
    def test_format_at_without_line(self):
        """Test @ format without line number."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', None, '@', False)
        self.assertEqual(result, '@root.users.admin')
    
    def test_format_relative_path(self):
        """Test relative path (removes 'root.' prefix)."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('root.users.admin', 100, '$ref', True)
        self.assertEqual(result, '$ref:users.admin:100')
    
    def test_format_relative_no_root_prefix(self):
        """Test relative path when path doesn't start with 'root.'."""
        from src.rewriter.reference_resolver import format_reference
        result = format_reference('users.admin', 200, '#/', True)
        self.assertEqual(result, '#/users.admin:200')


class TestResolveMultiFormat(unittest.TestCase):
    """Test resolve_references() with multiple formats (Sprint B Feature #4)."""
    
    def test_resolve_all_three_formats(self):
        """Verify all 3 formats ($ref:, #/, @) are resolved correctly."""
        obj = Obj([
            ('data', Obj([
                ('user', Obj([('name', 'Alice')])),
                ('author', Obj([('name', 'Bob')])),
            ])),
            ('ref1', '$ref:root.data.user'),
            ('ref2', '#/root.data.author'),
            ('ref3', '@root.data.user'),
        ])
        
        result, stats = resolve_references(obj)
        
        # All 3 references should be resolved
        self.assertEqual(stats['resolved'], 3)
        self.assertEqual(stats['invalid'], 0)
        
        # Check resolved values
        result_dict = dict(list(result))
        self.assertEqual(result_dict['ref1'], Obj([('name', 'Alice')]))
        self.assertEqual(result_dict['ref2'], Obj([('name', 'Bob')]))
        self.assertEqual(result_dict['ref3'], Obj([('name', 'Alice')]))
    
    def test_resolve_with_line_numbers(self):
        """Test that references with line numbers are resolved (line is ignored)."""
        obj = Obj([
            ('data', Obj([('value', 42)])),
            ('ref1', '$ref:root.data.value:100'),
            ('ref2', '#/root.data.value:200'),
            ('ref3', '@root.data.value:300'),
        ])
        
        result, stats = resolve_references(obj)
        
        # All should resolve (line numbers are parsed but not used for lookup)
        self.assertEqual(stats['resolved'], 3)
        
        result_dict = dict(list(result))
        self.assertEqual(result_dict['ref1'], 42)
        self.assertEqual(result_dict['ref2'], 42)
        self.assertEqual(result_dict['ref3'], 42)
    
    def test_resolve_relative_paths(self):
        """Test relative path resolution (tries with/without 'root.' prefix)."""
        obj = Obj([
            ('data', Obj([('item', 'test')])),
            ('ref1', '$ref:data.item'),  # Relative (no 'root.' prefix)
            ('ref2', '#/data.item'),
            ('ref3', '@data.item'),
        ])
        
        result, stats = resolve_references(obj)
        
        # All should resolve by adding 'root.' prefix
        self.assertEqual(stats['resolved'], 3)
        
        result_dict = dict(list(result))
        self.assertEqual(result_dict['ref1'], 'test')
        self.assertEqual(result_dict['ref2'], 'test')
        self.assertEqual(result_dict['ref3'], 'test')
    
    def test_resolve_invalid_format(self):
        """Test that invalid reference formats are kept as-is with warnings."""
        obj = Obj([
            ('data', Obj([('value', 1)])),
            ('ref1', '$ref:'),  # Invalid: empty path
            ('ref2', 'random_string'),  # Not a reference
        ])
        
        result, stats = resolve_references(obj)
        
        # Should not resolve (kept as-is)
        self.assertEqual(stats['resolved'], 0)
        self.assertEqual(stats['invalid'], 1)  # Only $ref: counts as invalid format
        
        result_dict = dict(list(result))
        self.assertEqual(result_dict['ref1'], '$ref:')
        self.assertEqual(result_dict['ref2'], 'random_string')


if __name__ == '__main__':
    unittest.main()
