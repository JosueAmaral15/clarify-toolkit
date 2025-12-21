#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Template Engine (AI Processor Dynamic Templates).

Tests:
- Basic variable substitution ({{count}}, {{filename}}, etc.)
- Arithmetic operations (+, -, *, /)
- Error handling (undefined vars, division by zero)
- Edge cases (empty template, no variables, malformed expressions)
- Integration with render_prompt convenience function
"""

import pytest
from src.ai_processor.template_engine import (
    TemplateEngine, create_context, render_prompt, 
    has_templates, preview_template
)


class TestTemplateEngine:
    """Test TemplateEngine class."""
    
    def test_simple_variable(self):
        """Test simple variable substitution."""
        engine = TemplateEngine()
        context = {'count': 5, 'total': 10}
        
        result = engine.render("File {{count}}/{{total}}", context)
        assert result == "File 5/10"
    
    def test_filename_and_filepath(self):
        """Test filename and filepath variables."""
        engine = TemplateEngine()
        context = {'filename': 'test.txt', 'filepath': '/path/to/test.txt'}
        
        result = engine.render("Processing {{filename}} ({{filepath}})", context)
        assert result == "Processing test.txt (/path/to/test.txt)"
    
    def test_addition(self):
        """Test addition arithmetic."""
        engine = TemplateEngine()
        context = {'count': 0}
        
        result = engine.render("Chapter {{count+1}}", context)
        assert result == "Chapter 1"
    
    def test_subtraction(self):
        """Test subtraction arithmetic."""
        engine = TemplateEngine()
        context = {'count': 10}
        
        result = engine.render("Index {{count-5}}", context)
        assert result == "Index 5"
    
    def test_multiplication(self):
        """Test multiplication arithmetic."""
        engine = TemplateEngine()
        context = {'count': 3}
        
        result = engine.render("Offset {{count*2}}", context)
        assert result == "Offset 6"
    
    def test_division(self):
        """Test integer division arithmetic."""
        engine = TemplateEngine()
        context = {'count': 10}
        
        result = engine.render("Half {{count/2}}", context)
        assert result == "Half 5"
    
    def test_division_by_zero(self):
        """Test division by zero handling."""
        engine = TemplateEngine()
        context = {'count': 10}
        
        result = engine.render("Error {{count/0}}", context)
        assert "DIVISION_BY_ZERO" in result
    
    def test_undefined_variable(self):
        """Test undefined variable handling."""
        engine = TemplateEngine()
        context = {'count': 5}
        
        result = engine.render("Missing {{missing}}", context)
        assert "UNDEFINED:missing" in result
    
    def test_invalid_expression(self):
        """Test invalid arithmetic expression."""
        engine = TemplateEngine()
        context = {'count': 5}
        
        result = engine.render("Bad {{count++}}", context)
        assert "INVALID" in result or "UNDEFINED" in result
    
    def test_multiple_variables(self):
        """Test multiple variables in one template."""
        engine = TemplateEngine()
        context = {'count': 2, 'total': 10, 'filename': 'data.json'}
        
        result = engine.render(
            "File {{count+1}}/{{total}}: {{filename}}",
            context
        )
        assert result == "File 3/10: data.json"
    
    def test_no_variables(self):
        """Test template without variables."""
        engine = TemplateEngine()
        context = {}
        
        result = engine.render("Just plain text", context)
        assert result == "Just plain text"
    
    def test_empty_template(self):
        """Test empty template."""
        engine = TemplateEngine()
        context = {'count': 5}
        
        result = engine.render("", context)
        assert result == ""


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_create_context(self):
        """Test create_context utility."""
        context = create_context(0, 10, "/path/to/file.txt")
        
        assert context['count'] == 0
        assert context['total'] == 10
        assert context['filename'] == 'file.txt'
        assert context['filepath'] == '/path/to/file.txt'
    
    def test_render_prompt(self):
        """Test render_prompt convenience function."""
        result = render_prompt(
            "Process {{count+1}}/{{total}}: {{filename}}",
            0, 10, "/path/to/test.txt"
        )
        
        assert result == "Process 1/10: test.txt"
    
    def test_has_templates_true(self):
        """Test has_templates with template variables."""
        assert has_templates("File {{count}}")
        assert has_templates("Chapter {{count+1}}/{{total}}")
        assert has_templates("{{filename}}")
    
    def test_has_templates_false(self):
        """Test has_templates without template variables."""
        assert not has_templates("Just plain text")
        assert not has_templates("No variables here")
        assert not has_templates("")
    
    def test_preview_template(self):
        """Test preview_template function."""
        preview = preview_template("Process {{count+1}}/{{total}}", 10)
        
        assert "Preview" in preview
        assert "1/10" in preview
    
    def test_preview_template_no_variables(self):
        """Test preview_template with no variables."""
        preview = preview_template("No variables", 10)
        
        assert preview == "No variables"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_nested_braces(self):
        """Test nested braces handling."""
        engine = TemplateEngine()
        context = {'count': 5}
        
        # Nested braces are not supported (regex matches outermost only)
        result = engine.render("{{{{count}}}}", context)
        # Behavior: treats "{{count}}" as variable name (which is undefined)
        assert "UNDEFINED" in result or "count" in result
    
    def test_arithmetic_with_negative(self):
        """Test arithmetic with negative numbers."""
        engine = TemplateEngine()
        context = {'count': 5}
        
        result = engine.render("Result {{count-10}}", context)
        assert result == "Result -5"
    
    def test_arithmetic_variable_right_side(self):
        """Test arithmetic with variable on right side."""
        engine = TemplateEngine()
        context = {'count': 5, 'offset': 3}
        
        result = engine.render("Sum {{count+offset}}", context)
        assert result == "Sum 8"
    
    def test_whitespace_handling(self):
        """Test whitespace in variable expressions."""
        engine = TemplateEngine()
        context = {'count': 5}
        
        # With spaces
        result1 = engine.render("{{ count + 1 }}", context)
        assert result1 == "6"
        
        # Without spaces
        result2 = engine.render("{{count+1}}", context)
        assert result2 == "6"
    
    def test_string_variable_in_arithmetic(self):
        """Test error when using string in arithmetic."""
        engine = TemplateEngine()
        context = {'filename': 'test.txt'}
        
        result = engine.render("Bad {{filename+1}}", context)
        assert "NOT_A_NUMBER" in result
    
    def test_complex_template(self):
        """Test complex real-world template."""
        engine = TemplateEngine()
        context = {
            'count': 0,
            'total': 50,
            'filename': 'chapter1.md',
            'filepath': '/docs/book/chapter1.md'
        }
        
        template = """
Process chapter {{count+1}} of {{total}}

File: {{filename}}
Path: {{filepath}}

This is chapter {{count+1}}/{{total}}.
"""
        
        result = engine.render(template, context)
        
        assert "chapter 1 of 50" in result
        assert "File: chapter1.md" in result
        assert "Path: /docs/book/chapter1.md" in result
        assert "This is chapter 1/50" in result


class TestIntegration:
    """Integration tests with realistic scenarios."""
    
    def test_batch_processing_simulation(self):
        """Simulate batch processing with templates."""
        files = [
            "chapter1.txt",
            "chapter2.txt",
            "chapter3.txt"
        ]
        
        template = "Translate chapter {{count+1}} of {{total}}: {{filename}}"
        
        results = []
        for i, file_path in enumerate(files):
            result = render_prompt(template, i, len(files), file_path)
            results.append(result)
        
        assert results[0] == "Translate chapter 1 of 3: chapter1.txt"
        assert results[1] == "Translate chapter 2 of 3: chapter2.txt"
        assert results[2] == "Translate chapter 3 of 3: chapter3.txt"
    
    def test_zero_based_vs_one_based(self):
        """Test zero-based and one-based indexing."""
        # Zero-based (programming style)
        result_zero = render_prompt("Index {{count}}", 0, 10, "file.txt")
        assert result_zero == "Index 0"
        
        # One-based (human-friendly)
        result_one = render_prompt("Chapter {{count+1}}", 0, 10, "file.txt")
        assert result_one == "Chapter 1"
    
    def test_progress_indicator(self):
        """Test progress indicator template."""
        template = "[{{count+1}}/{{total}}] Processing {{filename}}..."
        
        result = render_prompt(template, 4, 20, "data.json")
        assert result == "[5/20] Processing data.json..."


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
