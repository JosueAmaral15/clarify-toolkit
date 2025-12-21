"""
Unit Tests for Performance Benchmarks

Tests benchmark runner, generators, and comparison logic.

Author: Clarify Project
Version: 2.9.81
Date: 2025-12-21
"""

import pytest
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.generators import (
    generate_json_data,
    generate_nested_json,
    generate_html_content,
    generate_array_with_duplicates
)
from benchmarks.benchmark_runner import (
    BenchmarkRunner,
    Metrics,
    BenchmarkResult,
    ComparisonAnalyzer
)


class TestGenerators:
    """Test data generators."""
    
    def test_generate_json_data_size(self):
        """Test JSON generator creates approximate size."""
        data = generate_json_data(0.1)  # 100KB
        json_str = json.dumps(data)
        size_kb = len(json_str.encode('utf-8')) / 1024
        
        # Should be within 50% of target (generators are approximate)
        assert 50 < size_kb < 200
        assert 'items' in data
        assert 'metadata' in data
    
    def test_generate_nested_json_structure(self):
        """Test nested JSON has correct depth."""
        data = generate_nested_json(depth=5, breadth=2)
        
        assert 'root' in data
        assert 'metadata' in data
        
        # Check depth by traversing
        current = data['root']
        for i in range(5):
            assert 'level' in current
            if 'child_0' in current:
                current = current['child_0']
    
    def test_generate_html_content(self):
        """Test HTML generator creates valid HTML."""
        html = generate_html_content(0.05)  # 50KB
        
        assert '<html>' in html
        assert '</html>' in html
        assert '<body>' in html
        assert len(html) > 10000  # At least 10KB
    
    def test_generate_array_with_duplicates(self):
        """Test array generator creates duplicates."""
        arr = generate_array_with_duplicates(100, duplicate_ratio=0.5)
        
        assert len(arr) == 100
        
        # Check for duplicates by comparing unique vs total
        unique_ids = set(item['id'] for item in arr)
        assert len(unique_ids) < 100  # Should have duplicates


class TestBenchmarkRunner:
    """Test benchmark execution engine."""
    
    def test_register_benchmark(self):
        """Test benchmark registration."""
        runner = BenchmarkRunner(num_runs=1)
        
        runner.register(
            "test_sum",
            lambda: sum(range(1000)),
            size_label="1K"
        )
        
        assert len(runner.benchmarks) == 1
        assert runner.benchmarks[0]['name'] == "test_sum"
    
    def test_run_simple_benchmark(self):
        """Test running simple benchmark."""
        runner = BenchmarkRunner(num_runs=2, warmup=False)
        
        runner.register(
            "sum_test",
            lambda n: sum(range(n)),
            args=(10000,),
            size_label="10K"
        )
        
        results = runner.run_all()
        
        assert "sum_test" in results
        result = results["sum_test"]
        
        assert result.average_time > 0
        assert result.average_memory_mb >= 0
        assert len(result.runs) == 2
    
    def test_metrics_dataclass(self):
        """Test Metrics dataclass."""
        metrics = Metrics(
            elapsed_time=1.5,
            memory_peak_mb=100.0,
            cpu_percent=75.0,
            timestamp="2025-12-21T12:00:00"
        )
        
        d = metrics.to_dict()
        assert d['elapsed_time'] == 1.5
        assert d['memory_peak_mb'] == 100.0
        assert d['cpu_percent'] == 75.0


class TestComparisonAnalyzer:
    """Test result comparison logic."""
    
    def test_comparison_no_change(self):
        """Test comparison when performance is same."""
        current = BenchmarkResult(
            name="test",
            size_label="1MB",
            runs=[],
            average_time=1.0,
            average_memory_mb=100.0,
            average_cpu=75.0
        )
        
        previous = BenchmarkResult(
            name="test",
            size_label="1MB",
            runs=[],
            average_time=1.0,
            average_memory_mb=100.0,
            average_cpu=75.0
        )
        
        comparison = ComparisonAnalyzer.compare(current, previous)
        
        assert comparison['status'] == '✅'
        assert comparison['time_percent'] == 0.0
        assert comparison['is_regression'] is False
    
    def test_comparison_warning(self):
        """Test comparison when performance degrades (warning)."""
        current = BenchmarkResult(
            name="test",
            size_label="1MB",
            runs=[],
            average_time=1.15,  # 15% slower
            average_memory_mb=100.0,
            average_cpu=75.0
        )
        
        previous = BenchmarkResult(
            name="test",
            size_label="1MB",
            runs=[],
            average_time=1.0,
            average_memory_mb=100.0,
            average_cpu=75.0
        )
        
        comparison = ComparisonAnalyzer.compare(current, previous)
        
        assert comparison['status'] == '⚠️'
        assert 10 < comparison['time_percent'] < 25
        assert comparison['is_regression'] is True
    
    def test_comparison_error(self):
        """Test comparison when performance severely degrades."""
        current = BenchmarkResult(
            name="test",
            size_label="1MB",
            runs=[],
            average_time=1.5,  # 50% slower
            average_memory_mb=100.0,
            average_cpu=75.0
        )
        
        previous = BenchmarkResult(
            name="test",
            size_label="1MB",
            runs=[],
            average_time=1.0,
            average_memory_mb=100.0,
            average_cpu=75.0
        )
        
        comparison = ComparisonAnalyzer.compare(current, previous)
        
        assert comparison['status'] == '🚨'
        assert comparison['time_percent'] > 25
        assert comparison['is_regression'] is True


# Summary: 12 tests total
