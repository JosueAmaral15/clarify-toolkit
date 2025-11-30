"""
Test suite for Task #35 - Skip keys without siblings (v2.9.11)

Tests the skip_keys_without_siblings function that removes serial
hierarchies (chains) where keys don't have siblings.

Examples:
    Serial chain (should remove): {a: {b: {c: "val"}}} -> {}
    With siblings (should keep): {a: {b: "v1", c: "v2"}} -> {a: {b: "v1", c: "v2"}}
"""

import unittest
from src.rewriter.operations import skip_keys_without_siblings
from src.rewriter.types import Obj


class TestSkipNoSiblings(unittest.TestCase):
    """Test cases for skip_keys_without_siblings function."""
    
    def test_serial_chain_removed(self):
        """Serial chain without siblings should be completely removed."""
        # Input: {a: {b: {c: "val"}}}
        # Expected: {} (all removed, no siblings)
        input_obj = Obj([
            ("a", Obj([
                ("b", Obj([
                    ("c", "val")
                ]))
            ]))
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should return empty Obj
        assert isinstance(result, Obj)
        assert len(list(result)) == 0
    
    def test_keys_with_siblings_kept(self):
        """Keys with siblings should be kept."""
        # Input: {a: {b: "v1", c: "v2"}}
        # Expected: {a: {b: "v1", c: "v2"}} (b and c are siblings)
        input_obj = Obj([
            ("a", Obj([
                ("b", "v1"),
                ("c", "v2")
            ]))
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should keep all structure
        assert isinstance(result, Obj)
        items = list(result)
        assert len(items) == 1
        assert items[0][0] == "a"
        
        # Check inner object
        inner = items[0][1]
        assert isinstance(inner, Obj)
        inner_items = list(inner)
        assert len(inner_items) == 2
        assert inner_items[0][0] == "b"
        assert inner_items[1][0] == "c"
    
    def test_mixed_structure_partial_removal(self):
        """Mixed structure: remove chains, keep siblings."""
        # Input: {
        #   a: {b: {c: "val"}},     <- serial chain, remove
        #   d: {e: "v1", f: "v2"}   <- has siblings, keep
        # }
        # Expected: {d: {e: "v1", f: "v2"}}
        input_obj = Obj([
            ("a", Obj([
                ("b", Obj([
                    ("c", "val")
                ]))
            ])),
            ("d", Obj([
                ("e", "v1"),
                ("f", "v2")
            ]))
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should keep only 'd' branch
        assert isinstance(result, Obj)
        items = list(result)
        assert len(items) == 1
        assert items[0][0] == "d"
        
        # Check inner object
        inner = items[0][1]
        assert isinstance(inner, Obj)
        inner_items = list(inner)
        assert len(inner_items) == 2
        assert inner_items[0][0] == "e"
        assert inner_items[1][0] == "f"
    
    def test_nested_serial_chains(self):
        """Multiple nested serial chains should all be removed."""
        # Input: {a: {b: {c: {d: {e: "val"}}}}}
        # Expected: {} (entire chain removed)
        input_obj = Obj([
            ("a", Obj([
                ("b", Obj([
                    ("c", Obj([
                        ("d", Obj([
                            ("e", "val")
                        ]))
                    ]))
                ]))
            ]))
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should return empty Obj
        assert isinstance(result, Obj)
        assert len(list(result)) == 0
    
    def test_empty_object_removed(self):
        """Empty object should be removed."""
        # Input: {a: {}}
        # Expected: {}
        input_obj = Obj([
            ("a", Obj([]))
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should return empty Obj
        assert isinstance(result, Obj)
        assert len(list(result)) == 0
    
    def test_top_level_siblings_kept(self):
        """Top-level keys with siblings should all be kept."""
        # Input: {a: "v1", b: "v2", c: "v3"}
        # Expected: {a: "v1", b: "v2", c: "v3"}
        input_obj = Obj([
            ("a", "v1"),
            ("b", "v2"),
            ("c", "v3")
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should keep all
        assert isinstance(result, Obj)
        items = list(result)
        assert len(items) == 3
        assert items[0][0] == "a"
        assert items[1][0] == "b"
        assert items[2][0] == "c"
    
    def test_single_top_level_key_with_nested_siblings(self):
        """Single top-level key with nested siblings should be kept."""
        # Input: {a: {b: "v1", c: "v2"}}
        # Expected: {a: {b: "v1", c: "v2"}}
        # (Even though 'a' has no siblings, its children do)
        input_obj = Obj([
            ("a", Obj([
                ("b", "v1"),
                ("c", "v2")
            ]))
        ])
        
        result = skip_keys_without_siblings(input_obj)
        
        # Should keep all structure
        assert isinstance(result, Obj)
        items = list(result)
        assert len(items) == 1
        assert items[0][0] == "a"
        
        # Check inner object
        inner = items[0][1]
        assert isinstance(inner, Obj)
        inner_items = list(inner)
        assert len(inner_items) == 2



if __name__ == "__main__":
    unittest.main()
