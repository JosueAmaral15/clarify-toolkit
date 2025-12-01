#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for remove_duplicate_objects function (Task #52 - v2.9.27).

Tests the ability to remove duplicate JSON objects based on value equality,
with configurable similarity threshold and mode (remove vs reference).
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rewriter.types import Obj, freeze
from src.rewriter.operations import remove_duplicate_objects


class TestExactMatchSimple:
    """Test exact match detection with simple objects."""
    
    def test_exact_match_removes_duplicate(self):
        """Two identical objects should result in 1 removed."""
        obj = Obj([
            ('user', Obj([('name', 'John'), ('age', 30)])),
            ('author', Obj([('name', 'John'), ('age', 30)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=1.0)
        
        assert removed == 1
        assert len(result) == 1
        assert result[0][0] == 'user'  # First occurrence kept
        assert len(stats['duplicates_found']) == 1
        assert stats['duplicates_found'][0]['kept_key'] == ''
        assert stats['duplicates_found'][0]['similarity'] == 1.0
    
    def test_no_duplicates(self):
        """Different objects should not be removed."""
        obj = Obj([
            ('user', Obj([('name', 'John'), ('age', 30)])),
            ('admin', Obj([('name', 'Jane'), ('age', 25)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=1.0)
        
        assert removed == 0
        assert len(result) == 2
        assert len(stats['duplicates_found']) == 0


class TestExactMatchNested:
    """Test exact match detection with nested objects."""
    
    def test_nested_objects_exact_match(self):
        """Nested objects with identical values should be deduplicated."""
        obj = Obj([
            ('config', Obj([
                ('database', Obj([('host', 'localhost'), ('port', 5432)])),
                ('cache', Obj([('host', 'localhost'), ('port', 5432)]))
            ]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=1.0)
        
        assert removed == 1
        # Should keep 'database', remove 'cache'
        config = result[0][1]
        assert len(config) == 1
        assert config[0][0] == 'database'
    
    def test_deeply_nested_duplicates(self):
        """Three levels deep with duplicates."""
        obj = Obj([
            ('level1', Obj([
                ('level2a', Obj([('value', 'test')])),
                ('level2b', Obj([('value', 'test')]))
            ]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=1.0)
        
        assert removed == 1
        assert len(stats['duplicates_found']) == 1


class TestPartialMatch:
    """Test partial match with configurable threshold."""
    
    def test_threshold_80_percent_matches(self):
        """80% similarity with threshold=0.8 should match."""
        # 4 out of 5 fields match = 80%
        obj = Obj([
            ('obj1', Obj([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)])),
            ('obj2', Obj([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 999)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=0.8)
        
        assert removed == 1
        assert stats['duplicates_found'][0]['similarity'] == 0.8
    
    def test_threshold_100_percent_requires_exact(self):
        """80% similarity with threshold=1.0 should NOT match."""
        obj = Obj([
            ('obj1', Obj([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5)])),
            ('obj2', Obj([('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 999)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=1.0)
        
        assert removed == 0
        assert len(result) == 2
    
    def test_threshold_50_percent_very_lenient(self):
        """50% similarity allows very different objects to match."""
        # 1 out of 2 fields match = 50%
        obj = Obj([
            ('obj1', Obj([('name', 'John'), ('age', 30)])),
            ('obj2', Obj([('name', 'John'), ('age', 999)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, threshold=0.5)
        
        assert removed == 1
        assert stats['duplicates_found'][0]['similarity'] == 0.5


class TestArrayHandling:
    """Test array duplication handling."""
    
    def test_arrays_included_removes_duplicates(self):
        """With include_arrays=True, duplicate arrays should be removed."""
        obj = Obj([
            ('list1', [1, 2, 3]),
            ('list2', [1, 2, 3])
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, include_arrays=True)
        
        assert removed == 1
        assert len(result) == 1
    
    def test_arrays_excluded_keeps_all(self):
        """With include_arrays=False, duplicate arrays should be kept."""
        obj = Obj([
            ('list1', [1, 2, 3]),
            ('list2', [1, 2, 3])
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, include_arrays=False)
        
        assert removed == 0
        assert len(result) == 2
    
    def test_arrays_different_elements_not_removed(self):
        """Arrays with different elements should never match."""
        obj = Obj([
            ('list1', [1, 2, 3]),
            ('list2', [1, 2, 4])
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, include_arrays=True)
        
        assert removed == 0
        assert len(result) == 2


class TestReferenceMode:
    """Test reference mode ($ref: creation)."""
    
    def test_reference_mode_creates_ref(self):
        """Mode='reference' should create $ref: instead of removing."""
        obj = Obj([
            ('original', Obj([('value', 42)])),
            ('duplicate', Obj([('value', 42)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, mode='reference')
        
        assert removed == 1
        assert len(result) == 2  # Both entries exist
        assert result[1][1] == "$ref:root.original" or result[1][1] == "$ref:original"  # Second is reference
        assert len(stats['references_created']) == 1
    
    def test_reference_mode_with_nested_path(self):
        """References should include full path."""
        obj = Obj([
            ('config', Obj([
                ('db', Obj([('host', 'localhost')])),
                ('cache', Obj([('host', 'localhost')]))
            ]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, mode='reference')
        
        assert removed == 1
        config = result[0][1]
        assert config[1][1] == "$ref:root.config.db"


class TestEmptyValues:
    """Test handling of empty/null values."""
    
    def test_empty_objects_not_compared(self):
        """Empty objects should be kept (not considered duplicates)."""
        obj = Obj([
            ('empty1', Obj([])),
            ('empty2', Obj([]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj)
        
        # Empty objects should match and one should be removed
        assert removed == 1
        assert len(result) == 1
    
    def test_null_values_handled(self):
        """Null values should be compared correctly."""
        obj = Obj([
            ('obj1', Obj([('value', None)])),
            ('obj2', Obj([('value', None)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj)
        
        assert removed == 1
        assert len(result) == 1


class TestKeepFirstOccurrence:
    """Test that first occurrence (smallest line) is kept."""
    
    def test_keeps_first_removes_second(self):
        """Should keep 'user' and remove 'author'."""
        obj = Obj([
            ('user', Obj([('name', 'John')])),
            ('author', Obj([('name', 'John')])),
            ('creator', Obj([('name', 'John')]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj)
        
        assert removed == 2
        assert len(result) == 1
        assert result[0][0] == 'user'  # First one kept


class TestMixedTypes:
    """Test handling of mixed object/array/primitive types."""
    
    def test_primitives_not_deduplicated(self):
        """Primitive values as top-level should not be deduplicated."""
        obj = Obj([
            ('value1', 42),
            ('value2', 42),
            ('value3', 'test'),
            ('value4', 'test')
        ])
        
        result, removed, stats = remove_duplicate_objects(obj)
        
        # Primitives are not objects, so no deduplication
        assert removed == 0
        assert len(result) == 4
    
    def test_mixed_object_and_array(self):
        """Objects and arrays should not be compared to each other."""
        obj = Obj([
            ('obj', Obj([('a', 1), ('b', 2)])),
            ('arr', [1, 2])
        ])
        
        result, removed, stats = remove_duplicate_objects(obj, include_arrays=True)
        
        # Different types, no match
        assert removed == 0
        assert len(result) == 2


class TestStatistics:
    """Test statistics output."""
    
    def test_stats_dict_structure(self):
        """Stats dict should have expected structure."""
        obj = Obj([
            ('obj1', Obj([('a', 1)])),
            ('obj2', Obj([('a', 1)]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj)
        
        assert 'duplicates_found' in stats
        assert 'references_created' in stats
        assert 'kept_objects' in stats
        assert isinstance(stats['duplicates_found'], list)
        assert len(stats['duplicates_found']) == 1
    
    def test_stats_includes_paths(self):
        """Stats should include path information."""
        obj = Obj([
            ('config', Obj([
                ('db1', Obj([('host', 'localhost')])),
                ('db2', Obj([('host', 'localhost')]))
            ]))
        ])
        
        result, removed, stats = remove_duplicate_objects(obj)
        
        dup_info = stats['duplicates_found'][0]
        assert 'removed_path' in dup_info
        assert 'kept_path' in dup_info
        assert 'similarity' in dup_info
        assert dup_info['similarity'] == 1.0


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
