#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test removal counter functionality (Task v2.9.22)

Tests all 8 operations that remove items and verify counters are correct.
"""

import pytest
from src.rewriter.types import Obj
from src.rewriter.operations import (
    dedupe,
    join_keys,
    eliminate_duplicates,
    exclude_numeric_keys,
    skip_empty_values,
    avoid_duplicate_child_keys,
    remove_duplicate_array_values,
    skip_keys_without_siblings
)


class TestDedupeCounter:
    """Test dedupe() removal counter."""
    
    def test_dedupe_removes_duplicates(self):
        """Test that dedupe removes duplicate key-value pairs and counts them."""
        obj = Obj([
            ('a', 'value1'),
            ('a', 'value1'),  # duplicate
            ('b', 'value2'),
            ('a', 'value1'),  # duplicate
        ])
        result, count = dedupe(obj)
        
        assert count == 2  # 2 duplicates removed
        assert len(result) == 2  # Only 2 unique pairs remain
    
    def test_dedupe_no_duplicates(self):
        """Test that dedupe returns 0 when no duplicates exist."""
        obj = Obj([
            ('a', 'value1'),
            ('b', 'value2'),
            ('c', 'value3'),
        ])
        result, count = dedupe(obj)
        
        assert count == 0
        assert len(result) == 3
    
    def test_dedupe_nested(self):
        """Test dedupe counter in nested structures."""
        obj = Obj([
            ('parent', Obj([
                ('child', 'val'),
                ('child', 'val'),  # duplicate in nested
            ]))
        ])
        result, count = dedupe(obj)
        
        assert count == 1  # 1 duplicate in nested object


class TestEliminateDuplicatesCounter:
    """Test eliminate_duplicates() removal counter."""
    
    def test_eliminate_global_duplicates(self):
        """Test that eliminate_duplicates counts removed values."""
        obj = Obj([
            ('a', 'value1'),
            ('b', 'value1'),  # duplicate value (different key)
            ('c', 'value2'),
            ('d', 'value1'),  # another duplicate
        ])
        result, count = eliminate_duplicates(obj)
        
        assert count == 2  # 2 duplicate values removed
        assert len(result) == 2  # Only first occurrences kept
    
    def test_eliminate_no_duplicates(self):
        """Test eliminate_duplicates with unique values."""
        obj = Obj([
            ('a', 'value1'),
            ('b', 'value2'),
            ('c', 'value3'),
        ])
        result, count = eliminate_duplicates(obj)
        
        assert count == 0
        assert len(result) == 3


class TestExcludeNumericKeysCounter:
    """Test exclude_numeric_keys() removal counter."""
    
    def test_exclude_numeric_keys(self):
        """Test that numeric keys are counted."""
        obj = Obj([
            ('name', 'John'),
            ('0', 'zero'),  # numeric
            ('age', '30'),
            ('123', 'numeric'),  # numeric
            ('456', 'another'),  # numeric
        ])
        result, count = exclude_numeric_keys(obj)
        
        assert count == 3  # 3 numeric keys removed
        assert len(result) == 2
    
    def test_exclude_no_numeric(self):
        """Test when no numeric keys exist."""
        obj = Obj([
            ('name', 'John'),
            ('age', '30'),
        ])
        result, count = exclude_numeric_keys(obj)
        
        assert count == 0
        assert len(result) == 2


class TestSkipEmptyValuesCounter:
    """Test skip_empty_values() removal counter."""
    
    def test_skip_empty_strings(self):
        """Test that empty values are counted."""
        obj = Obj([
            ('name', 'John'),
            ('empty1', ''),  # empty
            ('age', '30'),
            ('empty2', '   '),  # whitespace only
            ('null_val', None),  # None
        ])
        result, count = skip_empty_values(obj)
        
        assert count == 3  # 3 empty values removed
        assert len(result) == 2
    
    def test_skip_no_empty(self):
        """Test when no empty values exist."""
        obj = Obj([
            ('name', 'John'),
            ('age', '30'),
        ])
        result, count = skip_empty_values(obj)
        
        assert count == 0
        assert len(result) == 2


class TestAvoidDuplicateChildKeysCounter:
    """Test avoid_duplicate_child_keys() removal counter."""
    
    def test_avoid_duplicate_child(self):
        """Test that duplicate child hierarchies are counted."""
        obj = Obj([
            ('pages', Obj([
                ('home', Obj([
                    ('home', Obj([
                        ('home', 'Welcome')  # duplicate chain
                    ]))
                ]))
            ]))
        ])
        result, count = avoid_duplicate_child_keys(obj)
        
        assert count == 2  # 2 levels of duplication collapsed
    
    def test_avoid_no_duplicates(self):
        """Test when no duplicate child keys exist."""
        obj = Obj([
            ('pages', Obj([
                ('home', 'Welcome'),
                ('about', 'About Us')
            ]))
        ])
        result, count = avoid_duplicate_child_keys(obj)
        
        assert count == 0


class TestRemoveDuplicateArrayValuesCounter:
    """Test remove_duplicate_array_values() removal counter."""
    
    def test_remove_consecutive_duplicates(self):
        """Test consecutive duplicate removal counter."""
        obj = Obj([
            ('items', ['a', 'a', 'b', 'c', 'c', 'c'])
        ])
        result, count = remove_duplicate_array_values(obj, consecutive_only=True)
        
        assert count == 3  # 3 consecutive duplicates removed
        items = result[0][1]
        assert items == ['a', 'b', 'c']
    
    def test_remove_all_duplicates(self):
        """Test all duplicate removal counter."""
        obj = Obj([
            ('items', ['a', 'b', 'a', 'c', 'b'])
        ])
        result, count = remove_duplicate_array_values(obj, consecutive_only=False)
        
        assert count == 2  # 2 duplicates removed (second 'a' and second 'b')
        items = result[0][1]
        assert items == ['a', 'b', 'c']
    
    def test_remove_no_duplicates(self):
        """Test when no duplicates exist."""
        obj = Obj([
            ('items', ['a', 'b', 'c'])
        ])
        result, count = remove_duplicate_array_values(obj, consecutive_only=False)
        
        assert count == 0


class TestSkipKeysWithoutSiblingsCounter:
    """Test skip_keys_without_siblings() removal counter."""
    
    def test_skip_orphan_chain(self):
        """Test that orphan chains are counted."""
        obj = Obj([
            ('a', Obj([
                ('b', Obj([
                    ('c', 'value')  # Serial chain with no siblings
                ]))
            ]))
        ])
        result, count = skip_keys_without_siblings(obj)
        
        assert count == 1  # 1 orphan chain removed
        assert len(result) == 0  # Entire chain removed
    
    def test_skip_with_siblings(self):
        """Test when siblings exist (nothing removed)."""
        obj = Obj([
            ('a', Obj([
                ('b', 'value1'),
                ('c', 'value2')  # b and c are siblings
            ]))
        ])
        result, count = skip_keys_without_siblings(obj)
        
        assert count == 0  # Nothing removed
        assert len(result) == 1


class TestJoinKeysCounter:
    """Test join_keys() - should always return 0 (doesn't remove)."""
    
    def test_join_keys_no_removal(self):
        """Test that join_keys doesn't count as removal."""
        obj = Obj([
            ('a', 'value1'),
            ('a', 'value2'),  # Duplicate key (will be joined)
        ])
        result, count = join_keys(obj)
        
        assert count == 0  # join_keys doesn't "remove", it merges
        assert len(result) == 1  # Keys are joined


class TestIntegrationMultipleOperations:
    """Test multiple operations together."""
    
    def test_combined_operations(self):
        """Test that counters work correctly when multiple operations are applied."""
        # Start with complex object
        obj = Obj([
            ('name', 'John'),
            ('name', 'John'),  # duplicate (dedupe: +1)
            ('0', 'zero'),  # numeric key (+1)
            ('empty', ''),  # empty value (+1)
            ('items', ['a', 'a', 'b']),  # array with consecutive dup (+1)
        ])
        
        # Apply dedupe
        obj, dedupe_count = dedupe(obj)
        assert dedupe_count == 1
        
        # Apply exclude numeric
        obj, numeric_count = exclude_numeric_keys(obj)
        assert numeric_count == 1
        
        # Apply skip empty
        obj, empty_count = skip_empty_values(obj)
        assert empty_count == 1
        
        # Apply array dedup
        obj, array_count = remove_duplicate_array_values(obj, consecutive_only=True)
        assert array_count == 1
        
        # Total: 4 items removed
        total = dedupe_count + numeric_count + empty_count + array_count
        assert total == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
