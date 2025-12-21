"""
CLI Runner for Benchmarks

Entry point for executing performance benchmarks.
Usage: python -m benchmarks.run [--sizes 1,10] [--operations set,search]

Author: Clarify Project
Version: 2.9.81
Date: 2025-12-21
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List

from .benchmark_runner import BenchmarkRunner
from .generators import (
    generate_json_data,
    generate_nested_json,
    generate_array_with_duplicates
)

# Import operations to benchmark
from src.converters import FormatConverter, Format
from src.set_operations import SetOperations


def setup_converter_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register TOON/BSON converter benchmarks."""
    for size_mb in sizes:
        data = generate_json_data(size_mb)
        
        # JSON → TOON
        runner.register(
            name=f"json_to_toon_{int(size_mb)}MB",
            func=FormatConverter.convert,
            args=(data, Format.JSON, Format.TOON),
            size_label=f"{size_mb}MB"
        )
        
        # JSON → BSON → JSON (roundtrip)
        runner.register(
            name=f"json_bson_roundtrip_{int(size_mb)}MB",
            func=lambda d: FormatConverter.convert(
                FormatConverter.convert(d, Format.JSON, Format.BSON),
                Format.BSON,
                Format.JSON
            ),
            args=(data,),
            size_label=f"{size_mb}MB"
        )


def setup_set_operations_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register set operations benchmarks."""
    for size_mb in sizes:
        data1 = generate_json_data(size_mb / 2)
        data2 = generate_json_data(size_mb / 2)
        
        # Union
        runner.register(
            name=f"set_union_{int(size_mb)}MB",
            func=SetOperations.union,
            args=([data1, data2],),
            size_label=f"{size_mb}MB"
        )
        
        # Intersection
        runner.register(
            name=f"set_intersection_{int(size_mb)}MB",
            func=SetOperations.intersection,
            args=([data1, data2],),
            size_label=f"{size_mb}MB"
        )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Clarify Performance Benchmarks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m benchmarks.run                    # Run all benchmarks (1MB, 5MB)
  python -m benchmarks.run --sizes 1,10       # Custom sizes
  python -m benchmarks.run --operations converter  # Only converter benchmarks
  python -m benchmarks.run --runs 5           # 5 runs per benchmark
        """
    )
    
    parser.add_argument(
        '--sizes',
        type=str,
        default='1,5',
        help='Comma-separated list of sizes in MB (default: 1,5)'
    )
    
    parser.add_argument(
        '--operations',
        type=str,
        default='all',
        choices=['all', 'converter', 'set'],
        help='Which operations to benchmark (default: all)'
    )
    
    parser.add_argument(
        '--runs',
        type=int,
        default=3,
        help='Number of runs per benchmark (default: 3)'
    )
    
    parser.add_argument(
        '--no-warmup',
        action='store_true',
        help='Skip warmup run'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='benchmarks/results.json',
        help='Output file for results (default: benchmarks/results.json)'
    )
    
    args = parser.parse_args()
    
    # Parse sizes
    try:
        sizes = [float(s.strip()) for s in args.sizes.split(',')]
    except ValueError:
        print(f"Error: Invalid sizes format: {args.sizes}")
        print("Expected: comma-separated numbers (e.g., '1,10,50')")
        return 1
    
    # Create runner
    runner = BenchmarkRunner(
        num_runs=args.runs,
        warmup=not args.no_warmup
    )
    
    # Register benchmarks
    if args.operations in ['all', 'converter']:
        setup_converter_benchmarks(runner, sizes)
    
    if args.operations in ['all', 'set']:
        setup_set_operations_benchmarks(runner, sizes)
    
    # Run benchmarks
    results = runner.run_all()
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing results if any
    if output_path.exists():
        with open(output_path, 'r') as f:
            all_results = json.load(f)
    else:
        all_results = {}
    
    # Add current results
    version = "v2.9.81"  # Get from CHANGELOG or __version__
    all_results[version] = {
        'timestamp': results[list(results.keys())[0]].runs[0].timestamp if results else None,
        'benchmarks': {name: result.to_dict() for name, result in results.items()}
    }
    
    # Save
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_path}")
    print(f"   Total benchmarks: {len(results)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
