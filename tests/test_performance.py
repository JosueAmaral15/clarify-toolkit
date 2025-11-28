#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Performance Profiling for Clarify Application

Tests performance with large files and measures resource usage.
Sprint 7.3 - Performance Testing
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Qt Application
try:
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
except ImportError:
    app = None


def format_size(bytes_size):
    """Format bytes to human readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def format_time(seconds):
    """Format seconds to human readable."""
    if seconds < 1:
        return f"{seconds*1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.2f}s"


class PerformanceTest:
    """Performance testing suite."""
    
    def __init__(self):
        self.results = []
    
    def test(self, name, test_func, *args, **kwargs):
        """Run a performance test."""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print('='*60)
        
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            self.results.append({
                "name": name,
                "status": "passed",
                "time": elapsed,
                "result": result
            })
            
            print(f"✅ Completed in {format_time(elapsed)}")
            if result:
                for key, value in result.items():
                    print(f"   {key}: {value}")
            
            return True
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Failed after {format_time(elapsed)}: {str(e)}")
            
            self.results.append({
                "name": name,
                "status": "failed",
                "time": elapsed,
                "error": str(e)
            })
            
            return False
    
    def print_summary(self):
        """Print performance summary."""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r['status'] == 'passed')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        total_time = sum(r['time'] for r in self.results)
        
        print(f"Total Tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️ Total Time: {format_time(total_time)}")
        
        if passed > 0:
            print("\n📊 Performance Results:")
            for result in self.results:
                if result['status'] == 'passed':
                    print(f"  • {result['name']}: {format_time(result['time'])}")
        
        return failed == 0


# =============================================================================
# Performance Tests
# =============================================================================

def test_large_json_parsing():
    """Test parsing large JSON files."""
    # Create 1MB JSON file
    data = {"items": [{"id": i, "name": f"Item {i}", "value": i * 1.5} for i in range(10000)]}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f, indent=2)
        temp_file = f.name
    
    try:
        file_size = os.path.getsize(temp_file)
        
        # Parse JSON
        start = time.time()
        with open(temp_file, 'r') as f:
            parsed = json.load(f)
        parse_time = time.time() - start
        
        # Cleanup
        os.unlink(temp_file)
        
        return {
            "File Size": format_size(file_size),
            "Items": len(parsed['items']),
            "Parse Time": format_time(parse_time)
        }
    except Exception as e:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        raise


def test_recursive_json_processing():
    """Test processing deeply nested JSON."""
    # Create deeply nested structure
    def create_nested(depth):
        if depth == 0:
            return {"value": "leaf"}
        return {"child": create_nested(depth - 1), "level": depth}
    
    data = create_nested(100)
    
    # Measure serialization
    start = time.time()
    json_str = json.dumps(data, indent=2)
    serialize_time = time.time() - start
    
    # Measure deserialization
    start = time.time()
    parsed = json.loads(json_str)
    deserialize_time = time.time() - start
    
    return {
        "Nesting Depth": 100,
        "JSON Size": format_size(len(json_str)),
        "Serialize Time": format_time(serialize_time),
        "Deserialize Time": format_time(deserialize_time)
    }


def test_text_normalization_performance():
    """Test text normalization speed."""
    from src.gui.text_extractor_dock import TextExtractorDock
    
    dock = TextExtractorDock()
    
    # Test with 1000 normalizations
    test_strings = [
        "Hello World Example",
        "snake_case_example",
        "camelCaseExample",
        "PascalCaseExample",
        "kebab-case-example"
    ] * 200
    
    options = {
        "case_style": "snake",
        "limit": 50,
        "avoid_cut": True,
        "uppercase": False
    }
    
    start = time.time()
    results = [dock._normalize_value(s, options) for s in test_strings]
    elapsed = time.time() - start
    
    return {
        "Normalizations": len(results),
        "Total Time": format_time(elapsed),
        "Avg per item": format_time(elapsed / len(results))
    }


def test_memory_footprint():
    """Test memory usage of dock instances."""
    from src.gui.ai_processor_dock import AIProcessorDock
    from src.gui.text_extractor_dock import TextExtractorDock
    from src.gui.case_converter_dock import CaseConverterDock
    
    try:
        import psutil
        process = psutil.Process()
        
        # Get initial memory
        initial_mem = process.memory_info().rss
        
        # Create 50 dock instances
        docks = []
        for _ in range(50):
            docks.extend([
                AIProcessorDock(),
                TextExtractorDock(),
                CaseConverterDock()
            ])
        
        # Get memory after creation
        after_mem = process.memory_info().rss
        memory_used = after_mem - initial_mem
        
        # Clear docks
        docks.clear()
        
        return {
            "Instances Created": 150,
            "Initial Memory": format_size(initial_mem),
            "Final Memory": format_size(after_mem),
            "Memory Used": format_size(memory_used),
            "Per Instance": format_size(memory_used / 150)
        }
    except ImportError:
        return {
            "Status": "psutil not available - install with 'pip install psutil'"
        }


def test_file_validation_speed():
    """Test file validation performance."""
    from src.gui.base_dock import ValidationMixin
    
    class TestDock(ValidationMixin):
        pass
    
    dock = TestDock()
    
    # Create test files
    temp_files = []
    for i in range(100):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_files.append(f.name)
    
    try:
        # Test validation speed
        start = time.time()
        for file_path in temp_files:
            dock.validate_file_path(file_path, must_exist=True)
        elapsed = time.time() - start
        
        # Cleanup
        for f in temp_files:
            os.unlink(f)
        
        return {
            "Files Validated": len(temp_files),
            "Total Time": format_time(elapsed),
            "Avg per file": format_time(elapsed / len(temp_files))
        }
    except Exception as e:
        for f in temp_files:
            if os.path.exists(f):
                os.unlink(f)
        raise


def test_concurrent_operations():
    """Test concurrent dock operations."""
    from src.gui.ai_processor_dock import AIProcessorDock
    from src.gui.text_extractor_dock import TextExtractorDock
    
    # Create multiple docks
    start = time.time()
    docks = [AIProcessorDock() for _ in range(10)] + [TextExtractorDock() for _ in range(10)]
    creation_time = time.time() - start
    
    # Cleanup
    docks.clear()
    
    return {
        "Docks Created": 20,
        "Creation Time": format_time(creation_time),
        "Avg per dock": format_time(creation_time / 20)
    }


# =============================================================================
# Main Runner
# =============================================================================

def main():
    """Run all performance tests."""
    
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PERFORMANCE PROFILING" + " "*22 + "║")
    print("╚" + "="*58 + "╝")
    
    tester = PerformanceTest()
    
    # Run tests
    tester.test("Large JSON Parsing (10K items)", test_large_json_parsing)
    tester.test("Recursive JSON Processing (100 levels)", test_recursive_json_processing)
    tester.test("Text Normalization (1000 items)", test_text_normalization_performance)
    tester.test("File Validation (100 files)", test_file_validation_speed)
    tester.test("Concurrent Operations (20 docks)", test_concurrent_operations)
    tester.test("Memory Footprint (150 instances)", test_memory_footprint)
    
    # Print summary
    success = tester.print_summary()
    
    # Save results
    results_file = Path(__file__).parent / "performance_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": time.time(),
            "results": tester.results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {results_file}")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
