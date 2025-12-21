"""
CLI Runner para Load Testing System

Executa testes de carga via linha de comando com configurações personalizáveis.

Usage:
    python -m load_tests --scenario batch_processing --workers 8
    python -m load_tests --scenario set_operations --files 100
    python -m load_tests --all

Author: Josué Amaral
Date: 21/12/2024
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from load_tests import (
    LoadRunner,
    LoadConfig,
    Scenarios,
    ReportGenerator
)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Clarify Load Testing System - v2.9.82",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run batch processing scenario with 100 files
  python -m load_tests --scenario batch_processing --files 100

  # Run set operations with 50 files
  python -m load_tests --scenario set_operations --files 50

  # Run all scenarios
  python -m load_tests --all

  # Custom configuration
  python -m load_tests --scenario batch_processing --workers 8 --sustain 60
        """
    )
    
    parser.add_argument(
        "--scenario",
        type=str,
        choices=["batch_processing", "set_operations", "mixed_operations"],
        help="Scenario to run"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios"
    )
    
    parser.add_argument(
        "--files",
        type=int,
        default=100,
        help="Number of files to process (default: 100)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    
    parser.add_argument(
        "--warmup",
        type=float,
        default=5.0,
        help="Warmup duration in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--rampup",
        type=float,
        default=10.0,
        help="Ramp-up duration in seconds (default: 10.0)"
    )
    
    parser.add_argument(
        "--sustain",
        type=float,
        default=30.0,
        help="Sustain duration in seconds (default: 30.0)"
    )
    
    parser.add_argument(
        "--cooldown",
        type=float,
        default=5.0,
        help="Cooldown duration in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file path (default: load_tests/results/vX.X.XX_YYYYMMDD.json)"
    )
    
    parser.add_argument(
        "--markdown",
        type=str,
        default=None,
        help="Generate markdown report (default: docs/PERFORMANCE.md)"
    )
    
    return parser.parse_args()


def run_batch_processing(config: LoadConfig, num_files: int):
    """Execute batch processing scenario"""
    runner = LoadRunner(config)
    
    analysis = runner.run_scenario(
        scenario_func=Scenarios.batch_file_processing,
        scenario_name=f"Batch Processing ({num_files} files)",
        scenario_args={"num_files": num_files}
    )
    
    return analysis


def run_set_operations(config: LoadConfig, num_files: int):
    """Execute set operations scenario"""
    runner = LoadRunner(config)
    
    analysis = runner.run_scenario(
        scenario_func=Scenarios.set_operations_stress,
        scenario_name=f"Set Operations Union ({num_files} files)",
        scenario_args={"num_files": num_files, "operation": "union"}
    )
    
    return analysis


def run_mixed_operations(config: LoadConfig, num_iterations: int):
    """Execute mixed operations scenario"""
    runner = LoadRunner(config)
    
    analysis = runner.run_scenario(
        scenario_func=Scenarios.mixed_operations,
        scenario_name=f"Mixed Operations ({num_iterations} iterations)",
        scenario_args={"num_iterations": num_iterations}
    )
    
    return analysis


def main():
    """Main entry point"""
    args = parse_args()
    
    # Validate arguments
    if not args.all and not args.scenario:
        print("❌ Error: Must specify --scenario or --all")
        sys.exit(1)
    
    # Create config
    config = LoadConfig(
        num_workers=args.workers,
        warmup_duration=args.warmup,
        rampup_duration=args.rampup,
        sustain_duration=args.sustain,
        cooldown_duration=args.cooldown
    )
    
    # Determine output paths
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.output:
        output_json = Path(args.output)
    else:
        output_dir = Path(__file__).parent / "results"
        output_dir.mkdir(exist_ok=True)
        output_json = output_dir / f"v2.9.82_{timestamp}.json"
    
    if args.markdown:
        output_md = Path(args.markdown)
    else:
        output_md = Path(__file__).parent.parent / "docs" / "PERFORMANCE.md"
    
    # Run scenarios
    results = []
    
    if args.all or args.scenario == "batch_processing":
        print("\n" + "="*70)
        analysis = run_batch_processing(config, args.files)
        ReportGenerator.to_console(analysis)
        results.append(analysis)
    
    if args.all or args.scenario == "set_operations":
        print("\n" + "="*70)
        analysis = run_set_operations(config, args.files)
        ReportGenerator.to_console(analysis)
        results.append(analysis)
    
    if args.all or args.scenario == "mixed_operations":
        print("\n" + "="*70)
        # Mixed operations usa num_iterations ao invés de num_files
        num_iterations = max(10, args.files // 10)
        analysis = run_mixed_operations(config, num_iterations)
        ReportGenerator.to_console(analysis)
        results.append(analysis)
    
    # Save results
    print("\n" + "="*70)
    print("💾 Salvando resultados...")
    
    for analysis in results:
        # Save JSON
        scenario_slug = analysis.scenario_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        json_path = output_json.parent / f"{output_json.stem}_{scenario_slug}.json"
        ReportGenerator.to_json(analysis, json_path)
        
        # Append to markdown
        ReportGenerator.to_markdown(analysis, output_md, append=True)
    
    print(f"\n✅ Load testing concluído!")
    print(f"   Resultados JSON: {output_json.parent}")
    print(f"   Relatório Markdown: {output_md}")


if __name__ == "__main__":
    main()
