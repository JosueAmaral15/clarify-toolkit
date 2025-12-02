#!/usr/bin/env python3
"""
Unit tests for Detailed Statistics (Sprint B Feature #3 v2.9.31)

Tests:
- DetailedStatsCollector: Enable/disable, add entries, get entries
- Integration with dedupe operation
"""

import unittest
from src.rewriter.detailed_stats import DetailedStatsCollector, DetailedStatEntry, get_global_collector
from src.rewriter.types import Obj
from src.rewriter.operations import dedupe


class TestDetailedStatsCollector(unittest.TestCase):
    """Test DetailedStatsCollector class."""
    
    def setUp(self):
        """Reset collector before each test."""
        self.collector = DetailedStatsCollector()
        self.collector.clear()
    
    def test_collector_disabled_by_default(self):
        """Collector should not collect entries when disabled."""
        self.assertFalse(self.collector.enabled)
        self.collector.add_entry('test', 'key1', 'key2')
        self.assertEqual(len(self.collector.get_entries()), 0)
    
    def test_collector_enable_disable(self):
        """Test enable/disable functionality."""
        self.collector.enable()
        self.assertTrue(self.collector.enabled)
        self.collector.disable()
        self.assertFalse(self.collector.enabled)
    
    def test_add_entry_when_enabled(self):
        """When enabled, collector should store entries."""
        self.collector.enable()
        self.collector.add_entry('dedupe', 'root.user', 'root.admin', 100.0, '1, 2')
        entries = self.collector.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].operation, 'dedupe')
        self.assertEqual(entries[0].original_key, 'root.user')
        self.assertEqual(entries[0].kept_key, 'root.admin')
    
    def test_multiple_entries(self):
        """Test adding multiple entries."""
        self.collector.enable()
        self.collector.add_entry('dedupe', 'key1', 'key2')
        self.collector.add_entry('eliminate', 'key3', '')
        self.collector.add_entry('numeric_keys', 'key4', '')
        self.assertEqual(len(self.collector.get_entries()), 3)
    
    def test_clear_entries(self):
        """Test clearing all entries."""
        self.collector.enable()
        self.collector.add_entry('dedupe', 'key1', 'key2')
        self.collector.add_entry('eliminate', 'key3', '')
        self.collector.clear()
        self.assertEqual(len(self.collector.get_entries()), 0)
    
    def test_get_summary(self):
        """Test summary count by operation type."""
        self.collector.enable()
        self.collector.add_entry('dedupe', 'key1', 'key2', count=1)
        self.collector.add_entry('dedupe', 'key3', 'key4', count=1)
        self.collector.add_entry('eliminate', 'key5', '', count=2)
        
        summary = self.collector.get_summary()
        self.assertEqual(summary['dedupe'], 2)
        self.assertEqual(summary['eliminate'], 2)


class TestDetailedStatEntry(unittest.TestCase):
    """Test DetailedStatEntry class."""
    
    def test_entry_creation(self):
        """Test creating a DetailedStatEntry."""
        entry = DetailedStatEntry(
            operation='dedupe',
            original_key='root.user.name',
            kept_key='root.admin.name',
            similarity=100.0,
            line_numbers='10, 25',
            count=1
        )
        self.assertEqual(entry.operation, 'dedupe')
        self.assertEqual(entry.original_key, 'root.user.name')
    
    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = DetailedStatEntry(
            operation='dedupe',
            original_key='root.user',
            kept_key='root.admin',
            similarity=100.0,
            line_numbers='1, 2',
            count=1
        )
        d = entry.to_dict()
        self.assertEqual(d['operation'], 'dedupe')
        self.assertEqual(d['original_key'], 'root.user')
        self.assertEqual(d['kept_key'], 'root.admin')
        self.assertEqual(d['similarity'], '100.0%')


class TestDedupeWithDetailedStats(unittest.TestCase):
    """Test dedupe operation with detailed stats collection."""
    
    def setUp(self):
        """Reset global collector before each test."""
        collector = get_global_collector()
        collector.clear()
        collector.disable()
    
    def test_dedupe_collects_stats_when_enabled(self):
        """Dedupe should collect detailed stats when collector is enabled."""
        collector = get_global_collector()
        collector.enable()
        
        # Note: dedupe removes duplicate (key, value) PAIRS, not just values
        # So we need same key AND same value to trigger duplicate detection
        obj = Obj([
            ('user', Obj([('name', 'John'), ('age', 30)])),
            ('user', Obj([('name', 'John'), ('age', 30)])),  # Exact duplicate (same key+value)
            ('admin', Obj([('name', 'Jane'), ('age', 25)])),
        ])
        
        result, count = dedupe(obj)
        
        # Should have collected 1 entry for the duplicate
        entries = collector.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].operation, 'dedupe')
        self.assertEqual(entries[0].original_key, 'root.user')
        self.assertEqual(entries[0].kept_key, 'root.user')
        self.assertEqual(entries[0].similarity, 100.0)
        
        collector.disable()
    
    def test_dedupe_no_stats_when_disabled(self):
        """Dedupe should not collect stats when collector is disabled."""
        collector = get_global_collector()
        # Collector is disabled by default
        
        obj = Obj([
            ('user', Obj([('name', 'John')])),
            ('author', Obj([('name', 'John')])),  # Duplicate
        ])
        
        result, count = dedupe(obj)
        
        # Should have no entries (collector disabled)
        entries = collector.get_entries()
        self.assertEqual(len(entries), 0)


if __name__ == '__main__':
    unittest.main()
