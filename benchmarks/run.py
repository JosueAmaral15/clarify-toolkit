"""
CLI Runner for Benchmarks

Entry point for executing performance benchmarks.
Usage: python -m benchmarks.run [--sizes 1,10] [--operations set,search]

Author: Clarify Project
Version: 2.9.83
Date: 2024-12-21
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
    generate_array_with_duplicates,
    generate_html_content
)

# Import operations to benchmark
try:
    from src.converters import FormatConverter, Format
    HAS_CONVERTERS = True
except ImportError:
    HAS_CONVERTERS = False

from src import set_operations

try:
    from src.rewriter import operations as rewriter_ops
    HAS_REWRITER = True
except ImportError:
    HAS_REWRITER = False

try:
    from src.json_search import flatten_object, ProjectIndexer
    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False

try:
    from src.text_extractor import extract_from_file
    HAS_EXTRACTOR = True
except ImportError:
    HAS_EXTRACTOR = False


def setup_converter_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register TOON/BSON converter benchmarks."""
    if not HAS_CONVERTERS:
        print("⚠️  Skipping converter benchmarks (converters not available)")
        return
    
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
            func=set_operations.union,
            args=([data1, data2],),
            size_label=f"{size_mb}MB"
        )
        
        # Intersection
        runner.register(
            name=f"set_intersection_{int(size_mb)}MB",
            func=set_operations.intersection,
            args=([data1, data2],),
            size_label=f"{size_mb}MB"
        )


def setup_rewriter_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register JSON rewriter benchmarks."""
    if not HAS_REWRITER:
        print("⚠️  Skipping rewriter benchmarks (rewriter not available)")
        return
    
    for size_mb in sizes:
        # Generate data with duplicates for dedupe benchmark
        data_with_dupes = generate_array_with_duplicates(
            size=int(size_mb * 1000),
            duplicate_ratio=0.3
        )
        
        # Deduplicate
        runner.register(
            name=f"rewriter_dedupe_{int(size_mb)}MB",
            func=rewriter_ops.dedupe,
            args=({"items": data_with_dupes},),
            size_label=f"{size_mb}MB"
        )


def setup_search_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register JSON search benchmarks."""
    if not HAS_SEARCH:
        print("⚠️  Skipping search benchmarks (json_search not available)")
        return
    
    for size_mb in sizes:
        # Generate nested data for search
        data = generate_nested_json(depth=5, breadth=int(size_mb * 10))
        
        # Flatten (prepare for search)
        runner.register(
            name=f"search_flatten_{int(size_mb)}MB",
            func=flatten_object,
            args=(data,),
            size_label=f"{size_mb}MB"
        )


def setup_extractor_benchmarks(runner: BenchmarkRunner, sizes: List[float]):
    """Register text extractor benchmarks."""
    if not HAS_EXTRACTOR:
        print("⚠️  Skipping extractor benchmarks (text_extractor not available)")
        return
    
    import tempfile
    from pathlib import Path as PathLib
    
    for size_mb in sizes:
        # Generate HTML content
        html_content = generate_html_content(size_mb)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        try:
            # Extract from HTML
            runner.register(
                name=f"extract_html_{int(size_mb)}MB",
                func=lambda p=temp_path: extract_from_file(p, param_name=None),
                args=(),
                size_label=f"{size_mb}MB"
            )
        finally:
            # Cleanup temp file
            PathLib(temp_path).unlink(missing_ok=True)


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
        choices=['all', 'converter', 'set', 'rewriter', 'search', 'extractor'],
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
    
    if args.operations in ['all', 'rewriter']:
        setup_rewriter_benchmarks(runner, sizes)
    
    if args.operations in ['all', 'search']:
        setup_search_benchmarks(runner, sizes)
    
    if args.operations in ['all', 'extractor']:
        setup_extractor_benchmarks(runner, sizes)
    
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
