#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performance Benchmarks for Clarify JSON Processing
===================================================

Tests performance with 1MB, 10MB, and 50MB JSON files.

SAFETY PROTOCOL (Simplicidade 3 - Etapa 9.1):
    ✅ 1. @pytest.mark.timeout(60) - Generous timeout for I/O operations
    ✅ 2. Uses /tmp directory - NO project pollution
    ✅ 3. Cleanup after each test (tmpdir fixture)
    ✅ 4. Measures: parsing time, memory delta, file I/O
    ✅ 5. NO GUI operations
    ✅ 6. NO infinite loops (all operations are finite)
    ✅ 7. Baseline metrics documented in docstrings

Author: Josué Amaral
Date: 2025-12-10
Version: 1.0
"""

import pytest
import json
import time
import os
import psutil
from pathlib import Path


# ============================================================================
# HELPER: JSON Generator
# ============================================================================

def generate_large_json(target_size_mb: float, tmpdir: Path) -> Path:
    """
    Generate a JSON file with approximate size in MB.
    
    Structure: {"items": [{"id": 1, "name": "Item 1", "data": "x" * 100}, ...]}
    Each item is ~150 bytes, so:
        - 1MB ≈ 7,000 items
        - 10MB ≈ 70,000 items
        - 50MB ≈ 350,000 items
    
    Returns: Path to generated file
    """
    items_per_mb = 7000
    num_items = int(target_size_mb * items_per_mb)
    
    filepath = tmpdir / f"benchmark_{target_size_mb}mb.json"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('{"items": [\n')
        for i in range(num_items):
            item = {
                "id": i,
                "name": f"Item {i}",
                "description": f"This is item number {i} with some data",
                "data": "x" * 100,  # Padding to increase size
                "nested": {
                    "field1": f"value_{i}",
                    "field2": i * 2,
                    "field3": True if i % 2 == 0 else False
                }
            }
            json_line = json.dumps(item, ensure_ascii=False)
            if i < num_items - 1:
                f.write(f"  {json_line},\n")
            else:
                f.write(f"  {json_line}\n")
        f.write(']}\n')
    
    # Verify size
    actual_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"Generated {filepath.name}: {actual_size_mb:.2f} MB ({num_items} items)")
    
    return filepath


# ============================================================================
# HELPER: Memory Measurement
# ============================================================================

def get_memory_usage_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


# ============================================================================
# BENCHMARK 1: JSON Parsing (stdlib json.loads)
# ============================================================================

@pytest.mark.timeout(60)
@pytest.mark.parametrize("size_mb", [1, 10, 50])
def test_benchmark_json_parsing(size_mb, tmpdir):
    """
    Benchmark: Parse JSON files with Python stdlib json.loads.
    
    Measures:
        - Parsing time (seconds)
        - Memory delta (MB)
        - Throughput (MB/s)
    
    Expected baseline (approximate):
        - 1MB: ~0.05-0.1s, ~2MB memory
        - 10MB: ~0.5-1s, ~20MB memory
        - 50MB: ~3-5s, ~100MB memory
    """
    # Generate test file
    filepath = generate_large_json(size_mb, Path(tmpdir))
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    # Measure parsing
    mem_before = get_memory_usage_mb()
    start_time = time.time()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    elapsed = time.time() - start_time
    mem_after = get_memory_usage_mb()
    mem_delta = mem_after - mem_before
    throughput = file_size_mb / elapsed if elapsed > 0 else 0
    
    # Assertions (sanity checks)
    assert isinstance(data, dict)
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0
    
    # Print metrics
    print(f"\n{'='*60}")
    print(f"JSON Parsing Benchmark - {file_size_mb:.2f} MB")
    print(f"{'='*60}")
    print(f"Parsing Time:   {elapsed:.3f}s")
    print(f"Memory Delta:   {mem_delta:.2f} MB")
    print(f"Throughput:     {throughput:.2f} MB/s")
    print(f"Items Parsed:   {len(data['items']):,}")
    print(f"{'='*60}\n")


# ============================================================================
# BENCHMARK 2: JSON Parsing with Duplicate Preservation (Clarify Rewriter)
# ============================================================================

@pytest.mark.timeout(60)
@pytest.mark.parametrize("size_mb", [1, 10, 50])
def test_benchmark_rewriter_parsing(size_mb, tmpdir):
    """
    Benchmark: Parse JSON with Clarify's duplicate-preserving parser.
    
    Uses: parse_json_preserving_duplicates_text from src.rewriter.types
    
    Measures:
        - Parsing time vs stdlib (overhead factor)
        - Memory delta
        - Throughput
    
    Expected: 1.1-1.3x slower than stdlib due to object_pairs_hook
    """
    from src.rewriter.types import parse_json_preserving_duplicates_text
    
    # Generate test file
    filepath = generate_large_json(size_mb, Path(tmpdir))
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    # Read file content
    with open(filepath, 'r', encoding='utf-8') as f:
        json_text = f.read()
    
    # Measure parsing
    mem_before = get_memory_usage_mb()
    start_time = time.time()
    
    data = parse_json_preserving_duplicates_text(json_text)
    
    elapsed = time.time() - start_time
    mem_after = get_memory_usage_mb()
    mem_delta = mem_after - mem_before
    throughput = file_size_mb / elapsed if elapsed > 0 else 0
    
    # Assertions
    assert data is not None
    
    # Print metrics
    print(f"\n{'='*60}")
    print(f"Rewriter Parsing Benchmark - {file_size_mb:.2f} MB")
    print(f"{'='*60}")
    print(f"Parsing Time:   {elapsed:.3f}s")
    print(f"Memory Delta:   {mem_delta:.2f} MB")
    print(f"Throughput:     {throughput:.2f} MB/s")
    print(f"{'='*60}\n")


# ============================================================================
# BENCHMARK 3: JSON Search (find all items with specific criteria)
# ============================================================================

@pytest.mark.timeout(60)
@pytest.mark.parametrize("size_mb", [1, 10, 50])
def test_benchmark_json_search(size_mb, tmpdir):
    """
    Benchmark: Search for items in large JSON structures.
    
    Task: Find all items where id is even number
    
    Measures:
        - Search time
        - Number of matches found
        - Search throughput (items/sec)
    
    Expected:
        - 1MB (~7k items): ~0.01-0.02s
        - 10MB (~70k items): ~0.1-0.2s
        - 50MB (~350k items): ~0.5-1s
    """
    # Generate and parse test file
    filepath = generate_large_json(size_mb, Path(tmpdir))
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items = data["items"]
    total_items = len(items)
    
    # Measure search
    start_time = time.time()
    
    matches = [item for item in items if item["id"] % 2 == 0]
    
    elapsed = time.time() - start_time
    search_throughput = total_items / elapsed if elapsed > 0 else 0
    
    # Assertions
    assert len(matches) > 0
    assert all(item["id"] % 2 == 0 for item in matches)
    
    # Print metrics
    print(f"\n{'='*60}")
    print(f"JSON Search Benchmark - {total_items:,} items")
    print(f"{'='*60}")
    print(f"Search Time:    {elapsed:.3f}s")
    print(f"Matches Found:  {len(matches):,} ({len(matches)/total_items*100:.1f}%)")
    print(f"Throughput:     {search_throughput:,.0f} items/s")
    print(f"{'='*60}\n")


# ============================================================================
# BENCHMARK 4: JSON Write/Save
# ============================================================================

@pytest.mark.timeout(60)
@pytest.mark.parametrize("size_mb", [1, 10, 50])
def test_benchmark_json_write(size_mb, tmpdir):
    """
    Benchmark: Write JSON data to file.
    
    Measures:
        - Write time
        - Throughput (MB/s)
    
    Expected:
        - 1MB: ~0.1-0.2s
        - 10MB: ~1-2s
        - 50MB: ~5-10s
    """
    # Generate data structure (not file yet)
    items_per_mb = 7000
    num_items = int(size_mb * items_per_mb)
    
    data = {
        "items": [
            {
                "id": i,
                "name": f"Item {i}",
                "description": f"This is item number {i} with some data",
                "data": "x" * 100,
                "nested": {
                    "field1": f"value_{i}",
                    "field2": i * 2,
                    "field3": True if i % 2 == 0 else False
                }
            }
            for i in range(num_items)
        ]
    }
    
    output_file = Path(tmpdir) / f"write_benchmark_{size_mb}mb.json"
    
    # Measure write
    start_time = time.time()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    throughput = file_size_mb / elapsed if elapsed > 0 else 0
    
    # Assertions
    assert output_file.exists()
    assert os.path.getsize(output_file) > 0
    
    # Print metrics
    print(f"\n{'='*60}")
    print(f"JSON Write Benchmark - {file_size_mb:.2f} MB")
    print(f"{'='*60}")
    print(f"Write Time:     {elapsed:.3f}s")
    print(f"Throughput:     {throughput:.2f} MB/s")
    print(f"Items Written:  {num_items:,}")
    print(f"{'='*60}\n")


# ============================================================================
# BENCHMARK 5: Round-trip (Read → Parse → Modify → Write)
# ============================================================================

@pytest.mark.timeout(60)
@pytest.mark.parametrize("size_mb", [1, 10])
def test_benchmark_roundtrip(size_mb, tmpdir):
    """
    Benchmark: Complete round-trip operation.
    
    Task:
        1. Read JSON file
        2. Parse JSON
        3. Modify data (add field to each item)
        4. Write back to file
    
    Measures:
        - Total time
        - Breakdown: read, parse, modify, write
    
    Expected:
        - 1MB: ~0.2-0.5s total
        - 10MB: ~2-5s total
    
    Note: 50MB excluded to keep test suite under 60s total
    """
    # Generate test file
    filepath = generate_large_json(size_mb, Path(tmpdir))
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    # === PHASE 1: Read ===
    start_read = time.time()
    with open(filepath, 'r', encoding='utf-8') as f:
        json_text = f.read()
    time_read = time.time() - start_read
    
    # === PHASE 2: Parse ===
    start_parse = time.time()
    data = json.loads(json_text)
    time_parse = time.time() - start_parse
    
    # === PHASE 3: Modify ===
    start_modify = time.time()
    for item in data["items"]:
        item["processed"] = True
        item["timestamp"] = "2025-12-10T00:00:00Z"
    time_modify = time.time() - start_modify
    
    # === PHASE 4: Write ===
    output_file = Path(tmpdir) / f"roundtrip_{size_mb}mb.json"
    start_write = time.time()
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    time_write = time.time() - start_write
    
    total_time = time_read + time_parse + time_modify + time_write
    
    # Assertions
    assert output_file.exists()
    output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    assert output_size_mb > file_size_mb  # Should be larger (added fields)
    
    # Print metrics
    print(f"\n{'='*60}")
    print(f"Round-trip Benchmark - {file_size_mb:.2f} MB")
    print(f"{'='*60}")
    print(f"Read:           {time_read:.3f}s ({time_read/total_time*100:.1f}%)")
    print(f"Parse:          {time_parse:.3f}s ({time_parse/total_time*100:.1f}%)")
    print(f"Modify:         {time_modify:.3f}s ({time_modify/total_time*100:.1f}%)")
    print(f"Write:          {time_write:.3f}s ({time_write/total_time*100:.1f}%)")
    print(f"{'─'*60}")
    print(f"TOTAL:          {total_time:.3f}s")
    print(f"Output Size:    {output_size_mb:.2f} MB")
    print(f"Items:          {len(data['items']):,}")
    print(f"{'='*60}\n")


# ============================================================================
# END OF BENCHMARKS
# ============================================================================
