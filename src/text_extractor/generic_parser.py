"""
Generic Scope Parser
====================

Improved generic parser for extracting content based on custom start/end delimiters.

Supports:
- Regex-based start and end patterns
- Named capture groups for scope identification
- Nested scope tracking
- Attribute extraction within scopes
- Balanced brace/bracket/quote handling

Author: Josué Amaral
Date: 2025-11-25
"""
# pylint: disable=broad-exception-caught  # File parsing robustness

import re
from ..utils.logger import get_logger

logger = get_logger(__name__)
from typing import List, Tuple, Optional, Dict, Iterator


class GenericScopeParser:
    r"""
    Generic scope parser driven by user-defined regex patterns.

    Features:
    - Custom start/end delimiters via regex
    - Named capture group support (?P<name>...)
    - Attribute extraction (key="value", key='value', key={expr})
    - Nested scope handling
    - Quote and brace balancing

    Usage:
        parser = GenericScopeParser(
            param_name="label",
            start_regex=r'<(?P<name>[A-Z]\w*)\b',
            end_regex=r'</(?P<name>[A-Z]\w*)>',
            match_all=False
        )

        for stack, node_name, key, value in parser.parse(content):
            logger.error(f"{stack} -> {node_name}: {key}={value}")
    """

    # Attribute patterns (reusable)
    ATTR_DQ_RE = re.compile(r'([A-Za-z_][\w\-]*)\s*=\s*"([^"]*)"')
    ATTR_SQ_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*'([^']*)'")
    ATTR_BRACE_STRING_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*\{\s*['\"]([^'\"]*)['\"]\\s*\}")
    ATTR_BRACE_EXPR_RE = re.compile(r"([A-Za-z_][\w\-]*)\s*=\s*\{([^}]*)\}")

    def __init__(
        self,
        param_name: str,
        start_regex: str,
        end_regex: str,
        match_all: bool = False
    ):
        """
        Initialize generic scope parser.

        Args:
            param_name: Attribute/parameter name to extract
            start_regex: Regex for scope start (use (?P<name>...) to capture scope name)
            end_regex: Regex for scope end
            match_all: If True, extract all attributes; if False, only param_name
        """
        self.param_name = param_name
        self.match_all = match_all or not param_name or param_name.strip() in ("", "*")

        try:
            self.start_re = re.compile(start_regex, re.DOTALL)
            self.end_re = re.compile(end_regex, re.DOTALL)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}") from e

    def parse(
        self,
        text: str,
        stack: Optional[List[str]] = None
    ) -> Iterator[Tuple[List[str], str, str, Optional[str]]]:
        r"""
        Parse text and yield (stack, node_name, key, value) tuples.

        Args:
            text: Content to parse
            stack: Current stack (for recursive calls)

        Yields:
            Tuple of (stack_path, node_name, attribute_key, attribute_value)

        Example:
            >>> parser = GenericScopeParser("label", r"<(\w+)", r"</(\w+)>")
            >>> for stack, name, key, val in parser.parse(content):
            ...     logger.error(f"{'.'.join(stack + [name])}: {key}={val}")
        """
        if stack is None:
            stack = []

        i = 0
        n = len(text)

        while i < n:
            # Check for end delimiter first
            m_end = self.end_re.match(text, i)
            if m_end:
                # Extract name from end match if captured
                end_name = m_end.groupdict().get("name")

                # Pop from stack if matches
                if stack and end_name:
                    # Pop matching scope
                    for j in range(len(stack) - 1, -1, -1):
                        if stack[j] == end_name:
                            stack = stack[:j]
                            break
                elif stack:
                    # No name captured, just pop last
                    stack = stack[:-1]

                i = m_end.end()
                continue

            # Check for start delimiter
            m_start = self.start_re.match(text, i)
            if m_start:
                # Extract scope name from capture group or use default
                node_name = m_start.groupdict().get("name", "scope")

                # Get text after start delimiter for attribute scanning
                attr_start = m_start.end()
                attr_window = text[attr_start:attr_start + 500]  # Look ahead 500 chars

                # Extract attributes from the window
                found_attrs = self._extract_attributes(attr_window)

                # Filter by param_name if not match_all
                if self.match_all:
                    # Yield all found attributes
                    for key, value in found_attrs.items():
                        yield (list(stack), node_name, key, value)
                else:
                    # Yield only matching param
                    if self.param_name in found_attrs:
                        yield (list(stack), node_name, self.param_name, found_attrs[self.param_name])
                    else:
                        # Yield with None value to indicate scope was found but param wasn't
                        yield (list(stack), node_name, self.param_name, None)

                # Push to stack
                stack.append(node_name)
                i = m_start.end()
                continue

            # No match, advance
            i += 1

    def _extract_attributes(self, text: str) -> Dict[str, str]:
        """
        Extract attributes from text using various patterns.

        Args:
            text: Text to scan for attributes

        Returns:
            Dictionary of {attribute_name: value}
        """
        attrs = {}

        # Try string patterns first (quoted values)
        for pattern in [self.ATTR_DQ_RE, self.ATTR_SQ_RE, self.ATTR_BRACE_STRING_RE]:
            for match in pattern.finditer(text):
                key = match.group(1)
                value = match.group(2)
                if key not in attrs:  # First match wins
                    attrs[key] = value

        # Try brace expressions (non-string values)
        for match in self.ATTR_BRACE_EXPR_RE.finditer(text):
            key = match.group(1)
            expr = match.group(2).strip()
            if key not in attrs:
                attrs[key] = expr

        return attrs

    def _read_balanced_brace_expr(self, text: str, start: int) -> Tuple[str, int]:
        """
        Read balanced brace expression starting at text[start].

        Args:
            text: Source text
            start: Starting position (should be at '{')

        Returns:
            Tuple of (expression_content, end_position)

        Raises:
            ValueError: If braces are unbalanced
        """
        if text[start] != '{':
            raise ValueError("Start position must be at '{'")

        depth = 1
        i = start + 1
        n = len(text)
        in_quote = None

        while i < n and depth > 0:
            ch = text[i]

            # Handle quotes
            if in_quote:
                if ch == '\\':
                    i += 2
                    continue
                if ch == in_quote:
                    in_quote = None
                i += 1
                continue

            # Not in quote
            if ch in ('"', "'"):
                in_quote = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if not depth:
                    return text[start + 1:i], i + 1

            i += 1

        raise ValueError("Unbalanced braces in expression")


def parse_generic_file(
    file_path: str,
    param_name: str,
    start_regex: str,
    end_regex: str,
    match_all: bool = False
) -> List[Tuple[str, str, List[str]]]:
    """
    Parse file using generic scope parser.

    Args:
        file_path: Path to file
        param_name: Parameter/attribute to extract
        start_regex: Start delimiter regex
        end_regex: End delimiter regex
        match_all: Extract all attributes if True

    Returns:
        List of (node_name, param_value, scope_hierarchy) tuples
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    parser = GenericScopeParser(param_name, start_regex, end_regex, match_all)
    results = []

    for stack, node_name, key, value in parser.parse(content):
        if value is not None:
            results.append((node_name, f"{key}={value}", stack))

    return results
