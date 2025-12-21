"""
Benchmark Runner Engine

Core engine for measuring performance metrics (time, memory, CPU).
Executes benchmarks and collects detailed performance data.

Author: Clarify Project
Version: 2.9.81
Date: 2025-12-21
"""

import time
import gc
import psutil
import tracemalloc
from dataclasses import dataclass, asdict
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime
import platform


@dataclass
class Metrics:
    """Performance metrics for a single benchmark run."""
    elapsed_time: float  # seconds
    memory_peak_mb: float  # megabytes
    cpu_percent: float  # 0-100%
    timestamp: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BenchmarkResult:
    """Result of benchmark across multiple runs."""
    name: str
    size_label: str
    runs: List[Metrics]
    average_time: float
    average_memory_mb: float
    average_cpu: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'size': self.size_label,
            'avg_time': round(self.average_time, 3),
            'avg_memory_mb': round(self.average_memory_mb, 1),
            'avg_cpu_percent': round(self.average_cpu, 1),
            'runs': [r.to_dict() for r in self.runs]
        }


class BenchmarkRunner:
    """
    Main benchmark execution engine.
    
    Handles benchmark registration, execution, and metric collection.
    """
    
    def __init__(self, num_runs: int = 3, warmup: bool = True):
        """
        Initialize benchmark runner.
        
        Args:
            num_runs: Number of times to run each benchmark
            warmup: Whether to do warmup run (excluded from results)
        """
        self.num_runs = num_runs
        self.warmup = warmup
        self.benchmarks: List[Dict[str, Any]] = []
        self.results: Dict[str, BenchmarkResult] = {}
        
    def register(
        self,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        size_label: str = "N/A"
    ) -> None:
        """
        Register a benchmark function.
        
        Args:
            name: Benchmark name (e.g., "set_union_1MB")
            func: Function to benchmark
            args: Positional arguments for func
            kwargs: Keyword arguments for func
            size_label: Human-readable size (e.g., "1MB", "10k items")
        
        Example:
            >>> runner = BenchmarkRunner()
            >>> runner.register(
            ...     "test_func",
            ...     my_function,
            ...     args=(data,),
            ...     size_label="1MB"
            ... )
        """
        self.benchmarks.append({
            'name': name,
            'func': func,
            'args': args,
            'kwargs': kwargs or {},
            'size_label': size_label
        })
    
    def run_all(self) -> Dict[str, BenchmarkResult]:
        """
        Execute all registered benchmarks.
        
        Returns:
            Dictionary mapping benchmark names to results
        
        Example:
            >>> runner = BenchmarkRunner(num_runs=3)
            >>> runner.register("test", lambda: sum(range(1000)))
            >>> results = runner.run_all()
            >>> "test" in results
            True
        """
        print(f"\n{'='*60}")
        print(f" Clarify Performance Benchmarks")
        print(f"{'='*60}")
        print(f" Python: {platform.python_version()}")
        print(f" OS: {platform.system()} {platform.release()}")
        print(f" Runs per benchmark: {self.num_runs}")
        print(f" Warmup: {'Yes' if self.warmup else 'No'}")
        print(f"{'='*60}\n")
        
        for i, benchmark in enumerate(self.benchmarks, 1):
            name = benchmark['name']
            size = benchmark['size_label']
            
            print(f"[{i}/{len(self.benchmarks)}] Running: {name} ({size})...")
            
            try:
                result = self._run_benchmark(
                    benchmark['func'],
                    benchmark['args'],
                    benchmark['kwargs'],
                    name,
                    size
                )
                self.results[name] = result
                
                print(f"  ✅ Time: {result.average_time:.3f}s | "
                      f"Memory: {result.average_memory_mb:.1f}MB | "
                      f"CPU: {result.average_cpu:.1f}%")
            
            except Exception as e:
                print(f"  ❌ FAILED: {str(e)}")
                traceback_str = ''.join(traceback.format_exc())
                print(f"     {traceback_str[:200]}...")
        
        print(f"\n{'='*60}")
        print(f" Completed {len(self.results)}/{len(self.benchmarks)} benchmarks")
        print(f"{'='*60}\n")
        
        return self.results
    
    def _run_benchmark(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        name: str,
        size_label: str
    ) -> BenchmarkResult:
        """
        Execute single benchmark multiple times and collect metrics.
        
        Args:
            func: Function to benchmark
            args: Positional arguments
            kwargs: Keyword arguments
            name: Benchmark name
            size_label: Size label
        
        Returns:
            BenchmarkResult with averaged metrics
        """
        runs: List[Metrics] = []
        
        # Warmup run (not included in results)
        if self.warmup:
            gc.collect()
            func(*args, **kwargs)
        
        # Actual benchmark runs
        for run_num in range(self.num_runs):
            gc.collect()  # Clean memory before each run
            time.sleep(0.1)  # Small delay between runs
            
            metrics = self._measure_single_run(func, args, kwargs)
            runs.append(metrics)
        
        # Calculate averages
        avg_time = sum(r.elapsed_time for r in runs) / len(runs)
        avg_memory = sum(r.memory_peak_mb for r in runs) / len(runs)
        avg_cpu = sum(r.cpu_percent for r in runs) / len(runs)
        
        return BenchmarkResult(
            name=name,
            size_label=size_label,
            runs=runs,
            average_time=avg_time,
            average_memory_mb=avg_memory,
            average_cpu=avg_cpu
        )
    
    def _measure_single_run(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict
    ) -> Metrics:
        """
        Measure metrics for a single function execution.
        
        Args:
            func: Function to measure
            args: Positional arguments
            kwargs: Keyword arguments
        
        Returns:
            Metrics object with time, memory, CPU
        """
        # Start memory tracking
        tracemalloc.start()
        
        # Get process for CPU monitoring
        process = psutil.Process()
        cpu_before = process.cpu_percent(interval=None)
        
        # Execute function and measure time
        start_time = time.perf_counter()
        func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        
        # Get CPU usage (sample over execution time)
        cpu_after = process.cpu_percent(interval=0.1)
        cpu_percent = (cpu_before + cpu_after) / 2  # Average
        
        # Get peak memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        memory_peak_mb = peak / (1024 * 1024)  # Convert to MB
        
        return Metrics(
            elapsed_time=elapsed_time,
            memory_peak_mb=memory_peak_mb,
            cpu_percent=cpu_percent,
            timestamp=datetime.now().isoformat()
        )


class ComparisonAnalyzer:
    """
    Analyze and compare benchmark results across versions.
    """
    
    THRESHOLD_WARNING = 0.10  # 10% slower
    THRESHOLD_ERROR = 0.25    # 25% slower
    
    @staticmethod
    def compare(
        current: BenchmarkResult,
        previous: BenchmarkResult
    ) -> Dict[str, Any]:
        """
        Compare current result with previous version.
        
        Args:
            current: Current benchmark result
            previous: Previous benchmark result
        
        Returns:
            Dictionary with comparison data and status
        
        Example:
            >>> current = BenchmarkResult(...)
            >>> previous = BenchmarkResult(...)
            >>> comparison = ComparisonAnalyzer.compare(current, previous)
            >>> comparison['status'] in ['✅', '⚠️', '🚨']
            True
        """
        time_diff = current.average_time - previous.average_time
        time_percent = (time_diff / previous.average_time) * 100
        
        memory_diff = current.average_memory_mb - previous.average_memory_mb
        memory_percent = (memory_diff / previous.average_memory_mb) * 100 if previous.average_memory_mb > 0 else 0
        
        # Determine status
        if abs(time_percent) < ComparisonAnalyzer.THRESHOLD_WARNING * 100:
            status = '✅'  # Good
        elif abs(time_percent) < ComparisonAnalyzer.THRESHOLD_ERROR * 100:
            status = '⚠️'   # Warning
        else:
            status = '🚨'  # Error (regression)
        
        return {
            'status': status,
            'time_diff_s': round(time_diff, 3),
            'time_percent': round(time_percent, 1),
            'memory_diff_mb': round(memory_diff, 1),
            'memory_percent': round(memory_percent, 1),
            'is_regression': time_percent > ComparisonAnalyzer.THRESHOLD_WARNING * 100
        }
