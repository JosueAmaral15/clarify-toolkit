"""
Tests for JSON Value Search (Task #48 - v2.9.23)

Tests the new functionality to search JSON values in addition to keys.

Author: Josué Amaral
Date: 2025-12-01
"""

import pytest
from src.json_search.query_parser import (
    resolve_query_by_value,
    resolve_query_with_mode
)


@pytest.fixture
def sample_flat_index():
    """Create a sample flat index for testing."""
    return {
        "pages.home.title": [
            {"file": "en.json", "value": "Welcome", "line": 5}
        ],
        "pages.home.subtitle": [
            {"file": "en.json", "value": "Welcome to our site", "line": 6}
        ],
        "pages.about.title": [
            {"file": "en.json", "value": "About Us", "line": 10}
        ],
        "auth.login.button": [
            {"file": "en.json", "value": "Login", "line": 15}
        ],
        "auth.signup.button": [
            {"file": "en.json", "value": "Sign Up", "line": 16}
        ],
        "user.profile.age": [
            {"file": "data.json", "value": 25, "line": 3}
        ],
        "user.profile.active": [
            {"file": "data.json", "value": True, "line": 4}
        ],
        "user.profile.name": [
            {"file": "data.json", "value": "John Doe", "line": 2}
        ]
    }


class TestResolveQueryByValue:
    """Test value search functionality."""
    
    def test_simple_value_search(self, sample_flat_index):
        """Test simple value search (case-insensitive)."""
        results = resolve_query_by_value(sample_flat_index, "Welcome", False, False)
        
        assert len(results) == 2  # "Welcome" and "Welcome to our site"
        assert all(r["match_type"] == "value" for r in results)
        assert any(r["key"] == "pages.home.title" for r in results)
        assert any(r["key"] == "pages.home.subtitle" for r in results)
    
    def test_value_search_case_sensitive(self, sample_flat_index):
        """Test value search with case sensitivity."""
        results = resolve_query_by_value(sample_flat_index, "welcome", True, False)
        
        assert len(results) == 0  # No match (case-sensitive)
        
        results = resolve_query_by_value(sample_flat_index, "Welcome", True, False)
        assert len(results) == 2  # Exact match
    
    def test_value_search_case_insensitive(self, sample_flat_index):
        """Test value search case-insensitive."""
        results = resolve_query_by_value(sample_flat_index, "login", False, False)
        
        assert len(results) == 1
        assert results[0]["key"] == "auth.login.button"
        assert results[0]["value"] == "Login"
    
    def test_value_search_with_regex(self, sample_flat_index):
        """Test value search with regex pattern."""
        # Search for values starting with "Sign"
        results = resolve_query_by_value(sample_flat_index, r"^Sign", False, True)
        
        assert len(results) == 1
        assert results[0]["key"] == "auth.signup.button"
        assert results[0]["value"] == "Sign Up"
    
    def test_value_search_numeric(self, sample_flat_index):
        """Test search for numeric values."""
        results = resolve_query_by_value(sample_flat_index, "25", False, False)
        
        assert len(results) == 1
        assert results[0]["key"] == "user.profile.age"
        assert results[0]["value"] == 25
    
    def test_value_search_boolean(self, sample_flat_index):
        """Test search for boolean values."""
        results = resolve_query_by_value(sample_flat_index, "True", False, False)
        
        assert len(results) == 1
        assert results[0]["key"] == "user.profile.active"
        assert results[0]["value"] is True
    
    def test_value_search_no_matches(self, sample_flat_index):
        """Test value search with no matches."""
        results = resolve_query_by_value(sample_flat_index, "NonExistent", False, False)
        
        assert len(results) == 0
    
    def test_value_search_partial_match(self, sample_flat_index):
        """Test value search with partial matches."""
        results = resolve_query_by_value(sample_flat_index, "Doe", False, False)
        
        assert len(results) == 1
        assert results[0]["key"] == "user.profile.name"
        assert "Doe" in results[0]["value"]


class TestResolveQueryWithMode:
    """Test mode-based search (key, value, both)."""
    
    def test_mode_key_only(self, sample_flat_index):
        """Test search with 'key' mode."""
        results = resolve_query_with_mode(
            sample_flat_index, "title", "", "key", False, False
        )
        
        # Should find: pages.home.title, pages.home.subtitle (substring), pages.about.title
        assert len(results) == 3
        assert all(r["match_type"] == "key" for r in results)
        assert any("title" in r["key"] for r in results)
    
    def test_mode_value_only(self, sample_flat_index):
        """Test search with 'value' mode."""
        results = resolve_query_with_mode(
            sample_flat_index, "", "Welcome", "value", False, False
        )
        
        assert len(results) == 2  # "Welcome" and "Welcome to our site"
        assert all(r["match_type"] == "value" for r in results)
    
    def test_mode_both(self, sample_flat_index):
        """Test search with 'both' mode."""
        results = resolve_query_with_mode(
            sample_flat_index, "button", "Login", "both", False, False
        )
        
        # Should find: auth.login.button (key match) and auth.login.button (value match)
        # But deduplication should keep only one
        assert len(results) >= 1
        keys = [r["key"] for r in results]
        assert "auth.login.button" in keys
    
    def test_mode_both_distinct_results(self, sample_flat_index):
        """Test 'both' mode returns distinct results."""
        results = resolve_query_with_mode(
            sample_flat_index, "auth", "Welcome", "both", False, False
        )
        
        # Should find: auth.*.* (key matches) and pages.home.* (value matches)
        assert len(results) >= 3
        
        # Check we have both types
        match_types = set(r["match_type"] for r in results)
        assert "key" in match_types
        assert "value" in match_types
    
    def test_mode_deduplication(self, sample_flat_index):
        """Test that duplicate results are removed."""
        # Search for same term in key and value
        results = resolve_query_with_mode(
            sample_flat_index, "Login", "Login", "both", False, False
        )
        
        # Even though we search both key and value, should not have duplicates
        keys_files = [(r["key"], r["file"]) for r in results]
        assert len(keys_files) == len(set(keys_files))
    
    def test_mode_empty_queries(self, sample_flat_index):
        """Test behavior with empty search queries."""
        # Empty key in 'key' mode
        results = resolve_query_with_mode(
            sample_flat_index, "", "", "key", False, False
        )
        assert len(results) == 0
        
        # Empty value in 'value' mode
        results = resolve_query_with_mode(
            sample_flat_index, "", "", "value", False, False
        )
        assert len(results) == 0
    
    def test_mode_with_regex(self, sample_flat_index):
        """Test mode-based search with regex enabled."""
        # Regex search in keys
        results = resolve_query_with_mode(
            sample_flat_index, r"\.title$", "", "key", False, True
        )
        assert len(results) == 2  # pages.home.title, pages.about.title
        
        # Regex search in values
        results = resolve_query_with_mode(
            sample_flat_index, "", r"^[A-Z]", "value", False, True
        )
        assert len(results) >= 4  # Values starting with capital letter


class TestIntegration:
    """Integration tests for complete workflow."""
    
    def test_full_workflow_value_search(self, sample_flat_index):
        """Test complete workflow: search value, get results, verify format."""
        # User searches for "Welcome" in values
        results = resolve_query_with_mode(
            sample_flat_index, "", "Welcome", "value", False, False
        )
        
        assert len(results) == 2
        
        for result in results:
            assert "key" in result
            assert "value" in result
            assert "file" in result
            assert "line" in result
            assert "match_type" in result
            assert result["match_type"] == "value"
            assert "Welcome" in str(result["value"])
    
    def test_full_workflow_both_mode(self, sample_flat_index):
        """Test complete workflow with 'both' mode."""
        # Search "login" in both keys and values
        results = resolve_query_with_mode(
            sample_flat_index, "login", "Login", "both", False, False
        )
        
        assert len(results) >= 1
        
        # Should have result with key containing "login"
        assert any("login" in r["key"].lower() for r in results)
    
    def test_edge_case_empty_flat_index(self):
        """Test with empty flat index."""
        empty_index = {}
        
        results = resolve_query_by_value(empty_index, "test", False, False)
        assert len(results) == 0
        
        results = resolve_query_with_mode(empty_index, "test", "test", "both", False, False)
        assert len(results) == 0
    
    def test_edge_case_none_values(self):
        """Test with None values in index."""
        index_with_none = {
            "test.key": [{"file": "test.json", "value": None, "line": 1}]
        }
        
        results = resolve_query_by_value(index_with_none, "None", False, False)
        assert len(results) == 1  # None converted to "None" string
    
    def test_performance_limit_200_results(self):
        """Test that results are limited to 200."""
        # Create large index
        large_index = {
            f"key.{i}": [{"file": "test.json", "value": "test", "line": i}]
            for i in range(300)
        }
        
        results = resolve_query_by_value(large_index, "test", False, False)
        assert len(results) <= 200  # Should be capped at 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
