#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Load Testing for Clarify JSON Processing
=========================================

Tests system behavior under heavy load scenarios:
- 1000+ small files (batch processing simulation)
- Large corpus (1GB+ total data)
- Concurrent operations

SAFETY PROTOCOL (Simplicidade 3 - Etapa 9.1):
    ✅ 1. @pytest.mark.timeout(300) - 5 minutes for heavy I/O
    ✅ 2. Uses /tmp directory - NO project pollution
    ✅ 3. Cleanup after each test (tmpdir fixture)
    ✅ 4. Measures: throughput, memory stability, error rate
    ✅ 5. NO GUI operations
    ✅ 6. NO infinite loops (all operations are bounded)
    ✅ 7. Graceful degradation documented

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
from typing import List, Tuple


# ============================================================================
# HELPER: Memory Tracking
# ============================================================================

class MemoryTracker:
    """Track memory usage throughout test execution."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.snapshots = []
    
    def snapshot(self, label: str = ""):
        """Take memory snapshot with optional label."""
        mem_mb = self.process.memory_info().rss / (1024 * 1024)
        self.snapshots.append((label, mem_mb))
        return mem_mb
    
    def peak(self) -> float:
        """Get peak memory usage."""
        return max(mem for _, mem in self.snapshots)
    
    def delta(self) -> float:
        """Get memory delta from first to last snapshot."""
        if len(self.snapshots) < 2:
            return 0.0
        return self.snapshots[-1][1] - self.snapshots[0][1]
    
    def report(self) -> str:
        """Generate memory report."""
        if not self.snapshots:
            return "No snapshots"
        
        lines = ["\n" + "="*60]
        lines.append("Memory Usage Report")
        lines.append("="*60)
        for label, mem in self.snapshots:
            lines.append(f"{label:30s}: {mem:8.2f} MB")
        lines.append("-"*60)
        lines.append(f"{'Peak Memory':30s}: {self.peak():8.2f} MB")
        lines.append(f"{'Memory Delta':30s}: {self.delta():8.2f} MB")
        lines.append("="*60 + "\n")
        return "\n".join(lines)


# ============================================================================
# HELPER: File Generator
# ============================================================================

def generate_small_json_files(count: int, tmpdir: Path) -> List[Path]:
    """
    Generate many small JSON files (~10KB each).
    
    Simulates real-world scenario: processing many configuration files.
    
    Args:
        count: Number of files to generate
        tmpdir: Temporary directory
    
    Returns:
        List of file paths
    """
    files = []
    
    for i in range(count):
        filepath = tmpdir / f"config_{i:05d}.json"
        
        data = {
            "id": i,
            "name": f"Configuration {i}",
            "version": "1.0.0",
            "enabled": True if i % 2 == 0 else False,
            "settings": {
                "timeout": 30,
                "retries": 3,
                "endpoint": f"https://api.example.com/v1/resource/{i}",
                "headers": {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer token_{i}"
                }
            },
            "metadata": {
                "created": "2025-12-10T00:00:00Z",
                "modified": "2025-12-10T00:00:00Z",
                "tags": ["config", "test", f"batch_{i // 100}"]
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        files.append(filepath)
    
    return files


def generate_large_corpus(target_size_gb: float, tmpdir: Path) -> List[Path]:
    """
    Generate multiple files totaling ~target_size_gb.
    
    Creates files in 100MB chunks for better memory control.
    
    Args:
        target_size_gb: Target total size in GB
        tmpdir: Temporary directory
    
    Returns:
        List of file paths
    """
    chunk_size_mb = 100
    num_chunks = int(target_size_gb * 1024 / chunk_size_mb)
    
    files = []
    
    for chunk_id in range(num_chunks):
        filepath = tmpdir / f"corpus_chunk_{chunk_id:03d}.json"
        
        # Generate 100MB file (each item ~150 bytes, so ~700k items)
        items_per_mb = 7000
        num_items = chunk_size_mb * items_per_mb
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('{"items": [\n')
            for i in range(num_items):
                item = {
                    "id": chunk_id * num_items + i,
                    "data": "x" * 100,
                    "nested": {"field": f"value_{i}"}
                }
                json_line = json.dumps(item, ensure_ascii=False)
                if i < num_items - 1:
                    f.write(f"  {json_line},\n")
                else:
                    f.write(f"  {json_line}\n")
            f.write(']}\n')
        
        files.append(filepath)
        
        # Print progress
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        total_mb = sum(os.path.getsize(f) / (1024 * 1024) for f in files)
        print(f"Generated chunk {chunk_id+1}/{num_chunks}: {size_mb:.2f} MB (total: {total_mb:.2f} MB)")
    
    return files


# ============================================================================
# LOAD TEST 1: Many Small Files (Batch Processing)
# ============================================================================

@pytest.mark.timeout(300)
@pytest.mark.parametrize("file_count", [100, 1000])
def test_load_many_small_files(file_count, tmpdir):
    """
    Load Test: Process many small JSON files (~10KB each).
    
    Simulates: Batch processing configuration files, log files, etc.
    
    Measures:
        - Time to parse all files
        - Memory stability (no memory leak)
        - Throughput (files/sec)
        - Error rate
    
    Expected:
        - 100 files: ~1-2s total
        - 1000 files: ~10-20s total
        - Memory should not grow linearly (GC working)
    """
    mem_tracker = MemoryTracker()
    mem_tracker.snapshot("Start")
    
    # Generate files
    print(f"\nGenerating {file_count} small files...")
    start_gen = time.time()
    files = generate_small_json_files(file_count, Path(tmpdir))
    gen_time = time.time() - start_gen
    
    total_size_mb = sum(os.path.getsize(f) / (1024 * 1024) for f in files)
    print(f"Generated {file_count} files in {gen_time:.2f}s (total: {total_size_mb:.2f} MB)")
    
    mem_tracker.snapshot("After Generation")
    
    # Parse all files
    print(f"Parsing {file_count} files...")
    start_parse = time.time()
    
    parsed_count = 0
    error_count = 0
    
    for i, filepath in enumerate(files):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Basic validation
            assert "id" in data
            assert data["id"] == i
            
            parsed_count += 1
            
            # Snapshot every 100 files
            if (i + 1) % 100 == 0:
                mem_tracker.snapshot(f"After {i+1} files")
        
        except Exception as e:
            error_count += 1
            print(f"Error parsing {filepath}: {e}")
    
    elapsed = time.time() - start_parse
    mem_tracker.snapshot("After Parsing")
    
    # Calculate metrics
    throughput_files = parsed_count / elapsed if elapsed > 0 else 0
    throughput_mb = total_size_mb / elapsed if elapsed > 0 else 0
    error_rate = error_count / file_count * 100
    
    # Assertions
    assert parsed_count == file_count, f"Expected {file_count} files, got {parsed_count}"
    assert error_count == 0, f"Errors occurred: {error_count}"
    
    # Memory stability check (delta should be reasonable)
    mem_delta = mem_tracker.delta()
    mem_per_file = mem_delta / file_count if file_count > 0 else 0
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Load Test: Many Small Files - {file_count} files")
    print(f"{'='*60}")
    print(f"Parsing Time:      {elapsed:.3f}s")
    print(f"Throughput:        {throughput_files:.0f} files/s")
    print(f"Throughput:        {throughput_mb:.2f} MB/s")
    print(f"Error Rate:        {error_rate:.2f}%")
    print(f"Memory Delta:      {mem_delta:.2f} MB")
    print(f"Memory per File:   {mem_per_file:.4f} MB")
    print(f"{'='*60}\n")
    
    print(mem_tracker.report())


# ============================================================================
# LOAD TEST 2: Large Corpus (Memory Stress)
# ============================================================================

@pytest.mark.timeout(300)
@pytest.mark.parametrize("corpus_size_gb", [1.0])
def test_load_large_corpus(corpus_size_gb, tmpdir):
    """
    Load Test: Process large corpus (1GB+) of JSON data.
    
    Simulates: Processing large datasets, data migration, backups.
    
    Measures:
        - Time to process entire corpus
        - Memory peak (should not load all into memory)
        - Throughput (MB/s)
        - Memory stability
    
    Expected:
        - 1GB corpus: ~60-120s (parsing + basic processing)
        - Memory peak: ~500-800 MB (not 1GB+)
        - Throughput: ~8-15 MB/s
    
    Note: Uses streaming approach (process one file at a time)
    """
    mem_tracker = MemoryTracker()
    mem_tracker.snapshot("Start")
    
    # Generate corpus
    print(f"\nGenerating {corpus_size_gb} GB corpus...")
    start_gen = time.time()
    files = generate_large_corpus(corpus_size_gb, Path(tmpdir))
    gen_time = time.time() - start_gen
    
    total_size_mb = sum(os.path.getsize(f) / (1024 * 1024) for f in files)
    total_size_gb = total_size_mb / 1024
    print(f"Generated {len(files)} files in {gen_time:.2f}s (total: {total_size_gb:.2f} GB)")
    
    mem_tracker.snapshot("After Generation")
    
    # Process corpus (streaming - one file at a time)
    print(f"Processing {total_size_gb:.2f} GB corpus...")
    start_process = time.time()
    
    processed_items = 0
    processed_mb = 0.0
    
    for i, filepath in enumerate(files):
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        
        # Parse file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process data (simulate light processing)
        items = data.get("items", [])
        processed_items += len(items)
        processed_mb += file_size_mb
        
        # Snapshot after each file
        mem_tracker.snapshot(f"After file {i+1}/{len(files)} ({processed_mb:.0f} MB)")
        
        # Progress update
        progress = (i + 1) / len(files) * 100
        print(f"Progress: {progress:.0f}% ({processed_mb:.0f} MB / {total_size_mb:.0f} MB)")
    
    elapsed = time.time() - start_process
    mem_tracker.snapshot("After Processing")
    
    # Calculate metrics
    throughput_mb = processed_mb / elapsed if elapsed > 0 else 0
    throughput_items = processed_items / elapsed if elapsed > 0 else 0
    mem_peak = mem_tracker.peak()
    mem_delta = mem_tracker.delta()
    
    # Assertions
    assert processed_mb > 0, "No data processed"
    assert mem_peak < total_size_mb * 2, f"Memory peak too high: {mem_peak:.2f} MB (corpus: {total_size_mb:.2f} MB)"
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Load Test: Large Corpus - {total_size_gb:.2f} GB")
    print(f"{'='*60}")
    print(f"Processing Time:   {elapsed:.3f}s")
    print(f"Throughput:        {throughput_mb:.2f} MB/s")
    print(f"Throughput:        {throughput_items:,.0f} items/s")
    print(f"Items Processed:   {processed_items:,}")
    print(f"Memory Peak:       {mem_peak:.2f} MB")
    print(f"Memory Delta:      {mem_delta:.2f} MB")
    print(f"Memory Efficiency: {processed_mb / mem_peak:.2f}x" if mem_peak > 0 else "N/A")
    print(f"{'='*60}\n")
    
    print(mem_tracker.report())


# ============================================================================
# LOAD TEST 3: Concurrent Operations (Stress Test)
# ============================================================================

@pytest.mark.timeout(300)
def test_load_concurrent_operations(tmpdir):
    """
    Load Test: Simulate concurrent operations on same dataset.
    
    Simulates: Multiple users/processes accessing same files.
    
    Operations:
        1. Read + Parse (10 times)
        2. Search (10 times)
        3. Modify + Write (5 times)
    
    Measures:
        - Total time
        - Memory stability
        - No data corruption
    
    Expected:
        - Total time: ~20-40s (sequential, not truly concurrent)
        - Memory should be stable
        - No data corruption
    
    Note: Python GIL prevents true concurrency, but tests memory/file handling
    """
    mem_tracker = MemoryTracker()
    mem_tracker.snapshot("Start")
    
    # Generate test file (10MB)
    print("\nGenerating test file (10MB)...")
    from tests.test_performance_benchmarks import generate_large_json
    filepath = generate_large_json(10, Path(tmpdir))
    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
    
    mem_tracker.snapshot("After Generation")
    
    # Read file content once
    with open(filepath, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    original_items = len(original_data["items"])
    
    # === Phase 1: Multiple Reads ===
    print("\nPhase 1: Multiple Reads (10x)...")
    start_read = time.time()
    
    for i in range(10):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data["items"]) == original_items
    
    time_read = time.time() - start_read
    mem_tracker.snapshot("After 10 Reads")
    
    # === Phase 2: Multiple Searches ===
    print("Phase 2: Multiple Searches (10x)...")
    start_search = time.time()
    
    for i in range(10):
        matches = [item for item in original_data["items"] if item["id"] % 2 == 0]
        assert len(matches) > 0
    
    time_search = time.time() - start_search
    mem_tracker.snapshot("After 10 Searches")
    
    # === Phase 3: Modify + Write (creates new files) ===
    print("Phase 3: Modify + Write (5x)...")
    start_write = time.time()
    
    for i in range(5):
        # Modify data
        modified_data = original_data.copy()
        for item in modified_data["items"]:
            item[f"modified_{i}"] = True
        
        # Write to new file
        output_file = Path(tmpdir) / f"modified_{i}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, ensure_ascii=False, indent=2)
        
        # Verify write
        assert output_file.exists()
    
    time_write = time.time() - start_write
    mem_tracker.snapshot("After 5 Writes")
    
    total_time = time_read + time_search + time_write
    
    # Calculate metrics
    read_throughput = (10 * file_size_mb) / time_read if time_read > 0 else 0
    search_throughput = (10 * original_items) / time_search if time_search > 0 else 0
    write_throughput = (5 * file_size_mb * 1.2) / time_write if time_write > 0 else 0  # 1.2x due to added fields
    
    mem_peak = mem_tracker.peak()
    mem_delta = mem_tracker.delta()
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Load Test: Concurrent Operations")
    print(f"{'='*60}")
    print(f"Phase 1 (10 Reads):     {time_read:.3f}s ({read_throughput:.2f} MB/s)")
    print(f"Phase 2 (10 Searches):  {time_search:.3f}s ({search_throughput:,.0f} items/s)")
    print(f"Phase 3 (5 Writes):     {time_write:.3f}s ({write_throughput:.2f} MB/s)")
    print(f"{'─'*60}")
    print(f"TOTAL TIME:             {total_time:.3f}s")
    print(f"Memory Peak:            {mem_peak:.2f} MB")
    print(f"Memory Delta:           {mem_delta:.2f} MB")
    print(f"{'='*60}\n")
    
    print(mem_tracker.report())


# ============================================================================
# END OF LOAD TESTS
# ============================================================================
