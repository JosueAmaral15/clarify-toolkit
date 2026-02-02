"""
Template Engine for AI Processor

Provides dynamic variable substitution in prompts with arithmetic support.

Supported variables:
- {{count}} - Current file index (0-based)
- {{count+N}} - Addition
- {{count-N}} - Subtraction
- {{count*N}} - Multiplication
- {{count/N}} - Integer division
- {{filename}} - Current file name (basename)
- {{filepath}} - Current file full path
- {{total}} - Total number of files

Examples:
- "Process chapter {{count+1}} of {{total}}"
  → "Process chapter 1 of 10" (for first file)
- "Analyze {{filename}} (file {{count}}/{{total}})"
  → "Analyze data.json (file 0/10)"

Security:
- Whitelist operators only (+, -, *, /)
- No eval() or arbitrary code execution
- Safe integer arithmetic with error handling
"""
# pylint: disable=broad-exception-caught  # Template parsing robustness

import re
import os
from typing import Dict, Any


class TemplateEngine:
    """
    Template engine for dynamic variable substitution in prompts.

    Pattern: Strategy (GoF) - Different substitution strategies per variable type
    Pattern: Template Method (GoF) - _substitute defines algorithm steps
    """

    # Regex for {{variable}} or {{variable+N}}
    VARIABLE_PATTERN = re.compile(r'\{\{([^}]+)\}\}')

    # Whitelist of safe operators
    SAFE_OPERATORS = ['+', '-', '*', '/']


    def render(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render template with variable substitution.

        Args:
            template: Template string with {{variables}}
            context: Context dictionary with variable values

        Returns:
            Rendered string with substituted values

        Example:
            >>> engine = TemplateEngine()
            >>> context = {'count': 0, 'total': 5, 'filename': 'test.txt'}
            >>> engine.render("File {{count+1}}/{{total}}: {{filename}}", context)
            'File 1/5: test.txt'
        """
        def replace_variable(match):
            """Callback for regex substitution."""
            variable_expr = match.group(1).strip()
            return self._substitute(variable_expr, context)

        return self.VARIABLE_PATTERN.sub(replace_variable, template)

    def _substitute(self, expression: str, context: Dict[str, Any]) -> str:
        """
        Substitute single variable expression.

        Args:
            expression: Variable expression (e.g., "count+1", "filename")
            context: Context dictionary

        Returns:
            Substituted string value
        """
        # Check if expression contains arithmetic
        if any(op in expression for op in self.SAFE_OPERATORS):
            return self._evaluate_arithmetic(expression, context)
        else:
            # Simple variable lookup
            return self._lookup_variable(expression, context)

    def _lookup_variable(self, var_name: str, context: Dict[str, Any]) -> str:
        """
        Look up simple variable in context.

        Args:
            var_name: Variable name
            context: Context dictionary

        Returns:
            String representation of variable value
        """
        value = context.get(var_name)

        if value is None:
            return f"{{{{UNDEFINED:{var_name}}}}}"  # Preserve undefined variables

        return str(value)

    def _evaluate_arithmetic(self, expression: str, context: Dict[str, Any]) -> str:
        """
        Evaluate arithmetic expression safely.

        Args:
            expression: Arithmetic expression (e.g., "count+1", "count*2")
            context: Context dictionary

        Returns:
            String representation of result

        Security:
            - Only whitelisted operators allowed
            - No eval() or exec()
            - Integer arithmetic only
        """
        # Parse expression: "count+1" → ("count", "+", "1")
        operator = None
        for op in self.SAFE_OPERATORS:
            if op in expression:
                operator = op
                break

        if not operator:
            return f"{{{{INVALID_EXPR:{expression}}}}}"

        # Split by operator
        parts = expression.split(operator, 1)
        if len(parts) != 2:
            return f"{{{{INVALID_EXPR:{expression}}}}}"

        left_str, right_str = parts[0].strip(), parts[1].strip()

        # Resolve left side (variable)
        left_value = context.get(left_str)
        if left_value is None:
            return f"{{{{UNDEFINED:{left_str}}}}}"

        # Parse right side (number or variable)
        try:
            if right_str.isdigit() or (right_str.startswith('-') and right_str[1:].isdigit()):
                right_value = int(right_str)
            else:
                # Try as variable
                right_value = context.get(right_str)
                if right_value is None:
                    return f"{{{{UNDEFINED:{right_str}}}}}"
                right_value = int(right_value)
        except (ValueError, TypeError):
            return f"{{{{INVALID_NUMBER:{right_str}}}}}"

        # Convert left to int
        try:
            left_value = int(left_value)
        except (ValueError, TypeError):
            return f"{{{{NOT_A_NUMBER:{left_str}={left_value}}}}}"

        # Perform arithmetic
        try:
            if operator == '+':
                result = left_value + right_value
            elif operator == '-':
                result = left_value - right_value
            elif operator == '*':
                result = left_value * right_value
            elif operator == '/':
                if not right_value:
                    return "{{DIVISION_BY_ZERO}}"
                result = left_value // right_value  # Integer division
            else:
                return f"{{{{INVALID_OP:{operator}}}}}"

            return str(result)
        except Exception as e:
            return f"{{{{EVAL_ERROR:{str(e)}}}}}"


def create_context(file_index: int, total_files: int, file_path: str) -> Dict[str, Any]:
    """
    Create template context for a file.

    Args:
        file_index: Current file index (0-based)
        total_files: Total number of files
        file_path: Current file path

    Returns:
        Context dictionary with standard variables

    Example:
        >>> context = create_context(0, 10, "/path/to/data.json")
        >>> context
        {'count': 0, 'total': 10, 'filename': 'data.json', 'filepath': '/path/to/data.json'}
    """
    return {
        'count': file_index,
        'total': total_files,
        'filename': os.path.basename(file_path),
        'filepath': file_path
    }


def render_prompt(prompt: str, file_index: int, total_files: int, file_path: str) -> str:
    """
    Convenience function to render prompt with file context.

    Args:
        prompt: Template prompt string
        file_index: Current file index (0-based)
        total_files: Total number of files
        file_path: Current file path

    Returns:
        Rendered prompt with substituted variables

    Example:
        >>> render_prompt("Process chapter {{count+1}} of {{total}}", 0, 10, "ch1.txt")
        'Process chapter 1 of 10'
    """
    engine = TemplateEngine()
    context = create_context(file_index, total_files, file_path)
    return engine.render(prompt, context)


def has_templates(text: str) -> bool:
    """
    Check if text contains template variables.

    Args:
        text: Text to check

    Returns:
        True if text contains {{...}} patterns

    Example:
        >>> has_templates("Normal text")
        False
        >>> has_templates("File {{count+1}}")
        True
    """
    return bool(TemplateEngine.VARIABLE_PATTERN.search(text))


def preview_template(prompt: str, total_files: int = 5) -> str:
    """
    Generate preview of template rendering for first file.

    Args:
        prompt: Template prompt
        total_files: Total files (for preview context)

    Returns:
        Preview text showing first file rendering

    Example:
        >>> preview_template("Process {{count+1}}/{{total}}", 10)
        'Preview (first file): Process 1/10'
    """
    if not has_templates(prompt):
        return prompt

    rendered = render_prompt(prompt, 0, total_files, "example.txt")
    return f"Preview (first file): {rendered}"
