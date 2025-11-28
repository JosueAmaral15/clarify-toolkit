#!/usr/bin/env python3
"""
Comprehensive Module Testing Script
Tests all 7 docks for potential bugs, edge cases, and failure scenarios.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Analysis Results Storage
test_results = {
    "critical": [],
    "warnings": [],
    "info": [],
    "passed": []
}


def log_issue(severity, module, issue, suggestion=""):
    """Log a test issue."""
    test_results[severity].append({
        "module": module,
        "issue": issue,
        "suggestion": suggestion
    })
    symbol = {"critical": "🔴", "warnings": "🟡", "info": "🔵", "passed": "✅"}[severity]
    print(f"{symbol} [{severity.upper()}] {module}: {issue}")
    if suggestion:
        print(f"   💡 Suggestion: {suggestion}")


# ==================== Test 1: Import Analysis ====================

def test_imports():
    """Test all imports and identify missing dependencies."""
    print("\n" + "="*60)
    print("TEST 1: Import Analysis")
    print("="*60)
    
    modules_to_test = [
        "src.gui.base_dock",
        "src.gui.ai_processor_dock",
        "src.gui.text_extractor_dock",
        "src.gui.case_converter_dock",
        "src.gui.json_search_dock",
        "src.gui.placeholder_replacer_dock",
        "src.gui.json_translate_dock",
        "src.gui.json_rewriter_dock",
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            log_issue("passed", module_name, "All imports successful")
        except ImportError as e:
            log_issue("critical", module_name, f"Import failed: {e}",
                     "Check dependencies and module paths")
        except Exception as e:
            log_issue("warnings", module_name, f"Import error: {e}")


# ==================== Test 2: Class Initialization ====================

def test_class_initialization():
    """Test if all dock classes can be instantiated."""
    print("\n" + "="*60)
    print("TEST 2: Class Initialization")
    print("="*60)
    
    # Mock QApplication for Qt widgets
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
    except Exception as e:
        log_issue("critical", "Qt", f"Cannot create QApplication: {e}",
                 "PySide6 may not be installed")
        return
    
    dock_classes = [
        ("base_dock", "BaseDock", {"title": "Test"}),
        ("base_dock", "StandardToolDock", {"title": "Test"}),
        ("ai_processor_dock", "AIProcessorDock", {}),
        ("text_extractor_dock", "TextExtractorDock", {}),
        ("case_converter_dock", "CaseConverterDock", {}),
        ("json_search_dock", "JsonSearchDock", {}),
        ("placeholder_replacer_dock", "PlaceholderReplacerDock", {}),
        ("json_translate_dock", "JsonTranslateDock", {}),
        ("json_rewriter_dock", "JsonRewriterDock", {}),
    ]
    
    for module_name, class_name, kwargs in dock_classes:
        try:
            module = __import__(f"src.gui.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            
            if class_name in ["BaseDock", "StandardToolDock"]:
                # Abstract classes - just check they exist
                log_issue("passed", f"{module_name}.{class_name}",
                         "Class definition OK (abstract)")
            else:
                # Try to instantiate
                instance = cls(**kwargs)
                log_issue("passed", f"{module_name}.{class_name}",
                         "Instance created successfully")
                
        except TypeError as e:
            if "abstract" in str(e).lower():
                log_issue("info", f"{module_name}.{class_name}",
                         "Abstract class (expected)")
            else:
                log_issue("critical", f"{module_name}.{class_name}",
                         f"Initialization failed: {e}",
                         "Check __init__ signature and parent class calls")
        except AttributeError as e:
            log_issue("critical", f"{module_name}.{class_name}",
                     f"Missing attributes: {e}",
                     "Widgets may not be created in _setup_ui()")
        except Exception as e:
            log_issue("warnings", f"{module_name}.{class_name}",
                     f"Initialization error: {e}")


# ==================== Test 3: Edge Cases - File Paths ====================

def test_file_path_edge_cases():
    """Test edge cases for file path handling."""
    print("\n" + "="*60)
    print("TEST 3: File Path Edge Cases")
    print("="*60)
    
    try:
        from src.gui.base_dock import ValidationMixin
        validator = ValidationMixin()
        
        # Test cases: (path, must_exist, expected_valid, description)
        test_cases = [
            ("", True, False, "Empty path"),
            ("   ", True, False, "Whitespace only"),
            ("/nonexistent/path/file.txt", True, False, "Non-existent path"),
            ("/nonexistent/path/file.txt", False, True, "Non-existent (not required)"),
            (__file__, True, True, "Valid existing file"),
            ("/root/protected.txt", True, None, "Permission denied (depends on system)"),
            ("relative/path.txt", True, False, "Relative path (non-existent)"),
            ("./test.txt", False, True, "Relative path (not required to exist)"),
            ("file:///tmp/test.txt", True, False, "File URI (not supported)"),
            ("C:\\Windows\\test.txt" if os.name == 'nt' else "/tmp/test.txt", False, True,
             "Platform-specific path"),
        ]
        
        for path, must_exist, expected, desc in test_cases:
            valid, msg = validator.validate_file_path(path, must_exist)
            
            if expected is None:
                # System-dependent, just check it doesn't crash
                log_issue("info", "ValidationMixin", f"{desc}: {valid} - {msg}")
            elif valid == expected:
                log_issue("passed", "ValidationMixin", f"{desc}: Handled correctly")
            else:
                log_issue("warnings", "ValidationMixin",
                         f"{desc}: Expected {expected}, got {valid}",
                         "Review validation logic")
    
    except Exception as e:
        log_issue("critical", "ValidationMixin", f"Test crashed: {e}")


# ==================== Test 4: Edge Cases - JSON Parsing ====================

def test_json_edge_cases():
    """Test edge cases for JSON handling."""
    print("\n" + "="*60)
    print("TEST 4: JSON Edge Cases")
    print("="*60)
    
    # Create test files
    temp_dir = tempfile.mkdtemp()
    
    test_files = {
        "valid.json": '{"key": "value"}',
        "empty.json": '',
        "invalid.json": '{"key": "value"',  # Missing closing brace
        "nested.json": '{"a": {"b": {"c": "deep"}}}',
        "unicode.json": '{"emoji": "😀", "chinese": "你好"}',
        "large.json": json.dumps({"key" + str(i): "value" + str(i) for i in range(1000)}),
        "duplicate_keys.json": '{"key": "first", "key": "second"}',
        "special_chars.json": '{"key": "value\\nwith\\ttabs\\rand\\"quotes\\""}',
    }
    
    for filename, content in test_files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Test JSON parsing
    for filename in test_files:
        filepath = os.path.join(temp_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if filename in ["valid.json", "nested.json", "unicode.json", "large.json", "special_chars.json"]:
                log_issue("passed", "JSON Parsing", f"{filename}: Parsed successfully")
            elif filename == "empty.json":
                log_issue("warnings", "JSON Parsing",
                         f"{filename}: Should fail but might succeed",
                         "Add validation for empty JSON files")
            elif filename == "duplicate_keys.json":
                log_issue("info", "JSON Parsing",
                         f"{filename}: Python keeps last key (expected behavior)")
        
        except json.JSONDecodeError:
            if filename in ["invalid.json", "empty.json"]:
                log_issue("passed", "JSON Parsing", f"{filename}: Correctly rejected")
            else:
                log_issue("warnings", "JSON Parsing",
                         f"{filename}: Unexpectedly failed to parse")
        except Exception as e:
            log_issue("critical", "JSON Parsing", f"{filename}: Unexpected error: {e}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


# ==================== Test 5: Threading and Interruption ====================

def test_threading():
    """Test threading mechanisms."""
    print("\n" + "="*60)
    print("TEST 5: Threading and Interruption")
    print("="*60)
    
    try:
        from src.gui.base_dock import ProcessorWorkerBase
        from PySide6.QtCore import QCoreApplication
        
        class TestWorker(ProcessorWorkerBase):
            def run(self):
                for i in range(10):
                    if self.check_interrupt():
                        self.emit_progress("Interrupted at " + str(i))
                        return
                    self.emit_progress(f"Step {i}")
                self.emit_success("Complete")
        
        # Test interrupt mechanism
        worker = TestWorker()
        
        # Check initial state
        if not worker.interrupt_requested:
            log_issue("passed", "ProcessorWorkerBase", "Initial state correct")
        else:
            log_issue("warnings", "ProcessorWorkerBase",
                     "Interrupt flag set before starting",
                     "Check initialization")
        
        # Test interrupt request
        worker.request_interrupt()
        if worker.check_interrupt():
            log_issue("passed", "ProcessorWorkerBase", "Interrupt mechanism works")
        else:
            log_issue("critical", "ProcessorWorkerBase",
                     "Interrupt not detected",
                     "Workers won't stop when requested")
        
    except Exception as e:
        log_issue("critical", "Threading", f"Test failed: {e}")


# ==================== Test 6: AI Processor Specific ====================

def test_ai_processor_edge_cases():
    """Test AIProcessorDock edge cases."""
    print("\n" + "="*60)
    print("TEST 6: AI Processor Edge Cases")
    print("="*60)
    
    # Test code fence removal
    test_cases = [
        ('```json\n{"key": "value"}\n```', '{"key": "value"}', "Standard JSON fence"),
        ('```\nplain text\n```', 'plain text', "No language identifier"),
        ('```python\nprint("hi")\n```', 'print("hi")', "Python fence"),
        ('No fences here', 'No fences here', "No fences"),
        ('```nested ```code``` blocks```', '```code``` blocks', "Nested fences (greedy match)"),
        ('', '', "Empty string"),
        ('```incomplete', '```incomplete', "Incomplete fence"),
    ]
    
    try:
        from src.gui.ai_processor_dock import AIProcessorDock
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance() or QApplication(sys.argv)
        dock = AIProcessorDock()
        
        for input_text, expected, desc in test_cases:
            result = dock._strip_code_fences(input_text)
            if result == expected:
                log_issue("passed", "AIProcessorDock._strip_code_fences", desc)
            else:
                log_issue("warnings", "AIProcessorDock._strip_code_fences",
                         f"{desc}: Expected '{expected}', got '{result}'",
                         "Review regex pattern")
    
    except Exception as e:
        log_issue("critical", "AIProcessorDock", f"Test failed: {e}")
    
    # Test token counting edge cases
    try:
        from src.ai_processor import count_tokens
        
        edge_cases = [
            ("", "Empty string"),
            ("a" * 100000, "Very long string"),
            ("😀" * 1000, "Many emojis"),
            ("\n" * 1000, "Many newlines"),
            ("    " * 1000, "Many spaces"),
        ]
        
        for text, desc in edge_cases:
            try:
                tokens = count_tokens(text)
                if tokens >= 0:
                    log_issue("passed", "count_tokens", f"{desc}: {tokens} tokens")
                else:
                    log_issue("warnings", "count_tokens",
                             f"{desc}: Negative token count",
                             "Check token counting logic")
            except Exception as e:
                log_issue("warnings", "count_tokens", f"{desc}: Error: {e}")
    
    except ImportError:
        log_issue("info", "count_tokens", "Module not available (expected if tiktoken not installed)")


# ==================== Test 7: Text Extractor Edge Cases ====================

def test_text_extractor_edge_cases():
    """Test TextExtractorDock edge cases."""
    print("\n" + "="*60)
    print("TEST 7: Text Extractor Edge Cases")
    print("="*60)
    
    try:
        from src.gui.text_extractor_dock import TextExtractorDock
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance() or QApplication(sys.argv)
        dock = TextExtractorDock()
        
        # Test normalization edge cases
        test_cases = [
            ("", {"case_style": "snake", "limit": "all", "uppercase": False, "avoid_cut": False},
             "", "Empty string"),
            ("   ", {"case_style": "snake", "limit": "all", "uppercase": False, "avoid_cut": False},
             "", "Whitespace only"),
            ("Hello World!", {"case_style": "snake", "limit": "all", "uppercase": False, "avoid_cut": False},
             "hello_world", "Basic snake_case"),
            ("Hello World", {"case_style": "camel", "limit": "all", "uppercase": False, "avoid_cut": False},
             "helloWorld", "Basic camelCase"),
            ("hello world", {"case_style": "pascal", "limit": "all", "uppercase": False, "avoid_cut": False},
             "HelloWorld", "Basic PascalCase"),
            ("Hello World", {"case_style": "kebab", "limit": "all", "uppercase": False, "avoid_cut": False},
             "hello-world", "Basic kebab-case"),
            ("123 numbers 456", {"case_style": "snake", "limit": "all", "uppercase": False, "avoid_cut": False},
             "123_numbers_456", "Numbers in text"),
            ("Special!@#$%Characters", {"case_style": "snake", "limit": "all", "uppercase": False, "avoid_cut": False},
             "special_characters", "Special characters"),
            ("Very Long Text That Should Be Truncated", {"case_style": "snake", "limit": "10", "uppercase": False, "avoid_cut": True},
             "very_long", "Truncation with avoid cut"),
            ("Short", {"case_style": "snake", "limit": "100", "uppercase": False, "avoid_cut": False},
             "short", "No truncation needed"),
        ]
        
        for input_text, options, expected, desc in test_cases:
            result = dock._normalize_value(input_text, options)
            if result == expected:
                log_issue("passed", "TextExtractorDock._normalize_value", desc)
            else:
                log_issue("warnings", "TextExtractorDock._normalize_value",
                         f"{desc}: Expected '{expected}', got '{result}'",
                         "Review normalization logic")
        
        # Test standard HTML tag detection
        standard_tags = ["div", "span", "p", "button", "input", "h1", "table"]
        custom_tags = ["MyComponent", "CustomDiv", "React", "Fragment"]
        
        for tag in standard_tags:
            if dock._is_standard_html_tag(tag):
                log_issue("passed", "TextExtractorDock._is_standard_html_tag",
                         f"'{tag}' correctly identified as standard")
            else:
                log_issue("warnings", "TextExtractorDock._is_standard_html_tag",
                         f"'{tag}' not identified as standard",
                         "Add to standard_tags set")
        
        for tag in custom_tags:
            if not dock._is_standard_html_tag(tag):
                log_issue("passed", "TextExtractorDock._is_standard_html_tag",
                         f"'{tag}' correctly identified as custom")
            else:
                log_issue("warnings", "TextExtractorDock._is_standard_html_tag",
                         f"'{tag}' incorrectly identified as standard")
    
    except Exception as e:
        log_issue("critical", "TextExtractorDock", f"Test failed: {e}")


# ==================== Test 8: Memory and Performance ====================

def test_memory_performance():
    """Test memory and performance edge cases."""
    print("\n" + "="*60)
    print("TEST 8: Memory and Performance")
    print("="*60)
    
    # Test large file handling
    temp_dir = tempfile.mkdtemp()
    large_file = os.path.join(temp_dir, "large.txt")
    
    try:
        # Create 10MB file
        with open(large_file, 'w') as f:
            f.write("x" * 10 * 1024 * 1024)
        
        # Try to read it
        with open(large_file, 'r') as f:
            content = f.read()
        
        if len(content) == 10 * 1024 * 1024:
            log_issue("passed", "File I/O", "Can handle 10MB file")
        else:
            log_issue("warnings", "File I/O", "File size mismatch after read")
    
    except MemoryError:
        log_issue("critical", "Memory", "Cannot allocate 10MB",
                 "System may be low on memory")
    except Exception as e:
        log_issue("warnings", "File I/O", f"Large file test failed: {e}")
    finally:
        import shutil
        shutil.rmtree(temp_dir)
    
    # Test recursion depth
    try:
        def deep_nest(n):
            return {"nested": deep_nest(n-1)} if n > 0 else "end"
        
        # Try to create very nested structure
        nested = deep_nest(100)
        log_issue("passed", "Recursion", "Can handle 100-level nesting")
    except RecursionError:
        log_issue("warnings", "Recursion", "Hit recursion limit at 100 levels",
                 "Set sys.setrecursionlimit() if needed")
    except Exception as e:
        log_issue("warnings", "Recursion", f"Nesting test failed: {e}")


# ==================== Test 9: Case Converter Edge Cases ====================

def test_case_converter_edge_cases():
    """Test CaseConverterDock with edge cases."""
    print("\n" + "="*60)
    print("TEST 9: Case Converter Edge Cases")
    print("="*60)
    
    # Check if CaseConverterDock has been fixed
    try:
        from src.gui.case_converter_dock import CaseConverterDock
        import inspect
        
        # Get _convert method source code
        source = inspect.getsource(CaseConverterDock._convert)
        
        # Check if it still references CaseStyle
        if "CaseStyle[" in source:
            log_issue("critical", "CaseConverterDock",
                     "Still references non-existent CaseStyle enum in _convert()",
                     "Replace 'CaseStyle[...]' with string-based style names")
        elif "style_map" in source and "camel" in source:
            log_issue("passed", "CaseConverterDock",
                     "_convert() uses string-based style mapping (fixed)")
        else:
            log_issue("warnings", "CaseConverterDock",
                     "Cannot verify if CaseStyle bug is fixed")
    except NameError as e:
        log_issue("critical", "CaseConverterDock", f"NameError during import: {e}")
    except Exception as e:
        log_issue("warnings", "CaseConverterDock", f"Import issue: {e}")


# ==================== Test 10: Placeholder Replacer Edge Cases ====================

def test_placeholder_replacer_edge_cases():
    """Test PlaceholderReplacerDock edge cases."""
    print("\n" + "="*60)
    print("TEST 10: Placeholder Replacer Edge Cases")
    print("="*60)
    
    # Test various placeholder patterns
    test_cases = [
        ("{t.key}", "Standard placeholder"),
        ("{t.nested.key.deep}", "Deeply nested"),
        ("{t.key}", "No closing brace (invalid)"),
        ("{{t.key}}", "Double braces"),
        ("{t.}", "Empty key"),
        ("{.key}", "Missing root"),
        ("{t.key-with-dash}", "Key with dash"),
        ("{t.key_with_underscore}", "Key with underscore"),
        ("{t.KEY}", "Uppercase key"),
        ("{t.123}", "Numeric key"),
    ]
    
    log_issue("info", "PlaceholderReplacerDock",
             "Placeholder patterns to test: " + str(len(test_cases)))
    log_issue("info", "PlaceholderReplacerDock",
             "Manual testing recommended with actual mapping files")


# ==================== Generate Report ====================

def generate_report():
    """Generate final test report."""
    print("\n" + "="*60)
    print("TEST REPORT SUMMARY")
    print("="*60)
    
    print(f"\n🔴 CRITICAL ISSUES: {len(test_results['critical'])}")
    for item in test_results['critical']:
        print(f"  • {item['module']}: {item['issue']}")
        if item['suggestion']:
            print(f"    💡 {item['suggestion']}")
    
    print(f"\n🟡 WARNINGS: {len(test_results['warnings'])}")
    for item in test_results['warnings'][:10]:  # Show first 10
        print(f"  • {item['module']}: {item['issue']}")
    if len(test_results['warnings']) > 10:
        print(f"  ... and {len(test_results['warnings']) - 10} more")
    
    print(f"\n🔵 INFO: {len(test_results['info'])}")
    print(f"✅ PASSED: {len(test_results['passed'])}")
    
    # Calculate score
    total = sum(len(v) for v in test_results.values())
    passed = len(test_results['passed'])
    score = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 OVERALL SCORE: {score:.1f}% ({passed}/{total} tests passed)")
    
    if score >= 90:
        print("✅ EXCELLENT - Code is production-ready")
    elif score >= 70:
        print("🟡 GOOD - Minor issues to address")
    elif score >= 50:
        print("🟠 FAIR - Several issues need attention")
    else:
        print("🔴 POOR - Major refactoring needed")


# ==================== Main ====================

if __name__ == "__main__":
    print("╔" + "="*58 + "╗")
    print("║" + " CLARIFY COMPREHENSIVE MODULE TESTING ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    try:
        test_imports()
        test_class_initialization()
        test_file_path_edge_cases()
        test_json_edge_cases()
        test_threading()
        test_ai_processor_edge_cases()
        test_text_extractor_edge_cases()
        test_memory_performance()
        test_case_converter_edge_cases()
        test_placeholder_replacer_edge_cases()
        
        generate_report()
        
        # Save detailed report
        report_path = Path(__file__).parent / "test_results.json"
        with open(report_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n🔴 FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
