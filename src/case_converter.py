#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON/TS/JS Case Converter Module

Converts object keys between different case styles:
- camelCase
- PascalCase
- snake_case
- kebab-case

Supports multiple input formats:
- Pure JSON
- TypeScript/JavaScript modules (export default, module.exports)
- Loose object literals
- Hybrid syntax (unquoted keys, comments, trailing commas)

Author: Josué Amaral (extracted from add/JSON_case_converter)
Date: November 24, 2025
"""

import re
import json
from typing import Any, Dict, List


class JSObjectCaseConverter:
    """
    Converts JavaScript/TypeScript/JSON object keys between case styles.
    Tolerant parser that handles comments, unquoted keys, and various export formats.
    """

    def __init__(self):
        self.case_converters = {
            'camel': self.to_camel,
            'pascal': self.to_pascal,
            'snake': self.to_snake,
            'kebab': self.to_kebab
        }

    # ==================== Case Conversion Methods ====================

    @staticmethod
    def split_token(s: str) -> List[str]:
        """Split a token into words, handling various naming conventions."""
        # Handle kebab-case and snake_case
        s = s.replace('-', ' ').replace('_', ' ')

        # Handle camelCase and PascalCase by inserting spaces before capitals
        s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', s)

        # Split and filter empty strings
        words = [w for w in s.split() if w]
        return words

    def to_camel(self, s: str) -> str:
        """Convert to camelCase."""
        words = self.split_token(s)
        if not words:
            return s
        return words[0].lower() + ''.join(w.capitalize() for w in words[1:])

    def to_pascal(self, s: str) -> str:
        """Convert to PascalCase."""
        words = self.split_token(s)
        if not words:
            return s
        return ''.join(w.capitalize() for w in words)

    def to_snake(self, s: str) -> str:
        """Convert to snake_case."""
        words = self.split_token(s)
        return '_'.join(w.lower() for w in words)

    def to_kebab(self, s: str) -> str:
        """Convert to kebab-case."""
        words = self.split_token(s)
        return '-'.join(w.lower() for w in words)

    # ==================== JSON/TS/JS Parsing ====================

    @staticmethod
    def _strip_comments(source: str) -> str:
        """Remove single-line and multi-line comments from source."""
        # Remove multi-line comments /* ... */
        source = re.sub(r'/\*.*?\*/', '', source, flags=re.DOTALL)
        # Remove single-line comments // ...
        source = re.sub(r'//.*?$', '', source, flags=re.MULTILINE)
        return source

    def _extract_object_literal(self, source: str) -> str:
        """
        Extract the main object literal from source.
        Handles:
        - export default { ... }
        - export default IDENT; (with const IDENT = { ... })
        - Standalone { ... }
        """
        source = self._strip_comments(source)

        # Try: export default { ... }
        m = re.search(r'export\s+default\s*(\{.*\})', source, flags=re.DOTALL)
        if m:
            return self._extract_balanced_braces(source, m.start(1))

        # Try: export default IDENT;
        m = re.search(r'export\s+default\s+([A-Za-z_$][\w$]*)\s*;?', source)
        if m:
            ident = m.group(1)
            # Find: const/let/var IDENT = { ... }
            pattern = rf'(?:const|let|var)\s+{re.escape(ident)}\s*=\s*\{{'
            m2 = re.search(pattern, source)
            if m2:
                brace_start = source.find('{', m2.start())
                return self._extract_balanced_braces(source, brace_start)

        # Fallback: first top-level { ... }
        m = re.search(r'\{', source)
        if m:
            return self._extract_balanced_braces(source, m.start())

        raise ValueError("Could not find object literal in source")

    @staticmethod
    def _extract_balanced_braces(source: str, start: int) -> str:
        """Extract balanced { ... } starting at position `start`."""
        depth = 0
        in_str = None
        escaped = False
        i = start

        while i < len(source):
            ch = source[i]

            if in_str:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == in_str:
                    in_str = None
            else:
                if ch in ('"', "'", '`'):
                    in_str = ch
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return source[start:i+1]
            i += 1

        raise ValueError("Unbalanced braces in object literal")

    def _normalize_to_json(self, obj_literal: str) -> str:
        """
        Convert JS-like object literal to valid JSON.
        Handles:
        - Unquoted keys
        - Single quotes → double quotes
        - Trailing commas
        - Template literals (basic)
        """
        s = obj_literal

        # Remove TS type annotations: 'as const', 'satisfies Type'
        s = re.sub(r'\bas\s+const\b', '', s)
        s = re.sub(r'\bsatisfies\b[^;{},]+', '', s)

        # Handle template literals without ${} → JSON strings
        s = re.sub(r'`([^`$]*)`', lambda m: json.dumps(m.group(1)), s)

        # Convert single quotes to double quotes (safely)
        def replace_single_quotes(match):
            inner = match.group(1)
            inner = inner.replace("\\'", "'")  # unescape single quotes
            return json.dumps(inner)

        s = re.sub(r"'((?:\\'|[^'])*?)'", replace_single_quotes, s)

        # Quote unquoted keys
        # Pattern: { key: or , key: or \n key:
        s = re.sub(r'([{\s,])([A-Za-z_$][\w$]*)\s*:', r'\1"\2":', s)

        # Remove trailing commas
        s = re.sub(r',(\s*[}\]])', r'\1', s)

        return s

    def parse_any(self, source: str) -> Dict[str, Any]:
        """
        Parse JSON/TS/JS source and return Python dict.
        Tolerant of various formats.
        """
        obj_literal = self._extract_object_literal(source)
        json_str = self._normalize_to_json(obj_literal)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse as JSON after normalization: {e}") from e

    # ==================== Key Conversion ====================

    def convert_keys(self, obj: Any, target_case: str) -> Any:
        """
        Recursively convert all keys in obj to target_case.

        Args:
            obj: Python dict/list/scalar
            target_case: 'camel', 'pascal', 'snake', or 'kebab'

        Returns:
            New object with converted keys
        """
        converter = self.case_converters.get(target_case)
        if not converter:
            raise ValueError(f"Unknown case style: {target_case}")

        if isinstance(obj, dict):
            return {converter(k): self.convert_keys(v, target_case) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_keys(item, target_case) for item in obj]
        else:
            return obj

    # ==================== Quote Unquoted Keys ====================

    def quote_unquoted_keys(self, source: str) -> str:
        """
        Add quotes to unquoted keys in JS/TS object literal.
        Useful for making code more JSON-compatible.
        """
        obj_literal = self._extract_object_literal(source)

        # Quote pattern: { key: or , key: or \n key:
        quoted = re.sub(r'([{\s,])([A-Za-z_$][\w$]*)\s*:', r'\1"\2":', obj_literal)

        return quoted

    # ==================== Output Formatting ====================

    @staticmethod
    def format_as_json(obj: Any, indent: int = 2) -> str:
        """Format object as JSON with proper indentation."""
        return json.dumps(obj, ensure_ascii=False, indent=indent)

    @staticmethod
    def format_as_js(obj: Any, indent: int = 2) -> str:
        """
        Format object as JavaScript object literal (unquoted keys).
        """
        def _fmt(v, level):  # pylint: disable=too-many-return-statements
            sp = " " * (indent * level)
            if isinstance(v, dict):
                if not v:
                    return "{}"
                items = []
                for k, vv in v.items():
                    formatted_val = _fmt(vv, level + 1)
                    items.append(f'{sp}{" " * indent}{k}: {formatted_val}')
                return "{\n" + ",\n".join(items) + f"\n{sp}}}"
            elif isinstance(v, list):
                if not v:
                    return "[]"
                items = []
                for vv in v:
                    formatted_val = _fmt(vv, level + 1)
                    items.append(f'{sp}{" " * indent}{formatted_val}')
                return "[\n" + ",\n".join(items) + f"\n{sp}]"
            elif isinstance(v, str):
                return '"' + v.replace('\\', '\\\\').replace('"', '\\"') + '"'
            elif isinstance(v, bool):
                return 'true' if v else 'false'
            elif v is None:
                return 'null'
            else:
                return str(v)

        return _fmt(obj, 0)


# ==================== Convenience Functions ====================

def convert_file(input_path: str, output_path: str, target_case: str,
                 quote_keys: bool = False, output_format: str = 'js') -> None:
    """
    Convert a JSON/TS/JS file to target case style.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        target_case: 'camel', 'pascal', 'snake', or 'kebab'
        quote_keys: If True, add quotes to unquoted keys first
        output_format: 'json' or 'js' (affects key quoting in output)
    """
    converter = JSObjectCaseConverter()

    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()

    if quote_keys:
        source = converter.quote_unquoted_keys(source)

    obj = converter.parse_any(source)
    converted = converter.convert_keys(obj, target_case)

    if output_format == 'json':
        output = converter.format_as_json(converted)
    else:
        output = converter.format_as_js(converted)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)


def convert_string(source: str, target_case: str, output_format: str = 'js') -> str:
    """
    Convert a JSON/TS/JS string to target case style.

    Args:
        source: JSON/TS/JS source string
        target_case: 'camel', 'pascal', 'snake', or 'kebab'
        output_format: 'json' or 'js'

    Returns:
        Converted string
    """
    converter = JSObjectCaseConverter()
    obj = converter.parse_any(source)
    converted = converter.convert_keys(obj, target_case)

    if output_format == 'json':
        return converter.format_as_json(converted)
    else:
        return converter.format_as_js(converted)
