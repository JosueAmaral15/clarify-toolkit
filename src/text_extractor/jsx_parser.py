"""
JSX/HTML Parser
===============

Simple parser for extracting tag hierarchies and attributes from JSX/HTML.

Supports:
- Opening tags: <Tag attr="value">
- Self-closing tags: <Tag attr="value" />
- Closing tags: </Tag>
- Attribute extraction
- Nested tag tracking

Author: Josué Amaral
Date: 2025-11-24
"""
# pylint: disable=broad-exception-caught  # File parsing robustness

import re
from ..utils.logger import get_logger

logger = get_logger(__name__)
from typing import List, Tuple, Optional, Dict


# Standard HTML tags for filtering
STANDARD_HTML_TAGS = {
    'html', 'head', 'title', 'base', 'link', 'meta', 'style', 'script',
    'body', 'section', 'nav', 'article', 'aside', 'h1', 'h2', 'h3', 'h4',
    'h5', 'h6', 'header', 'footer', 'main', 'p', 'hr', 'pre', 'div', 'span',
    'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input',
    'button', 'select', 'option', 'textarea', 'label', 'br', 'strong', 'em'
}


def is_standard_tag(name: str) -> bool:
    """Check if tag name is a standard HTML tag."""
    return name.lower() in STANDARD_HTML_TAGS


class JSXParser:
    """
    Simple JSX/HTML parser for extracting tag hierarchies and attributes.

    Usage:
        parser = JSXParser(content)
        for tag_name, attrs, tag_stack in parser.parse():
            logger.error(f"{tag_stack} -> {tag_name}: {attrs}")
    """

    # Regex patterns
    TAG_OPEN = re.compile(r'<([A-Z][A-Za-z0-9]*)\s*([^>]*)>', re.DOTALL)
    TAG_SELF_CLOSE = re.compile(r'<([A-Z][A-Za-z0-9]*)\s*([^>]*)/>', re.DOTALL)
    TAG_CLOSE = re.compile(r'</([A-Z][A-Za-z0-9]*)>')
    ATTR_PATTERN = re.compile(r'([a-zA-Z_][\w]*)\s*=\s*["\']([^"\']*)["\']')

    def __init__(self, content: str):
        """
        Initialize parser with JSX/HTML content.

        Args:
            content: JSX/HTML source code
        """
        self.content = content
        self.pos = 0
        self.stack: List[str] = []

    def parse(self) -> List[Tuple[str, Dict[str, str], List[str]]]:
        """
        Parse content and yield (tag_name, attributes, tag_stack) tuples.

        Returns:
            List of (tag_name, attributes_dict, current_tag_stack)
        """
        results = []

        while self.pos < len(self.content):
            # Try self-closing tag first
            match = self.TAG_SELF_CLOSE.search(self.content, self.pos)
            if match and match.start() == self.pos:
                tag_name = match.group(1)
                attrs_str = match.group(2)
                attrs = self._parse_attributes(attrs_str)
                results.append((tag_name, attrs, self.stack.copy()))
                self.pos = match.end()
                continue

            # Try opening tag
            match = self.TAG_OPEN.search(self.content, self.pos)
            if match and match.start() == self.pos:
                tag_name = match.group(1)
                attrs_str = match.group(2)
                attrs = self._parse_attributes(attrs_str)
                results.append((tag_name, attrs, self.stack.copy()))
                self.stack.append(tag_name)
                self.pos = match.end()
                continue

            # Try closing tag
            match = self.TAG_CLOSE.search(self.content, self.pos)
            if match and match.start() == self.pos:
                tag_name = match.group(1)
                # Pop from stack if it matches
                if self.stack and self.stack[-1] == tag_name:
                    self.stack.pop()
                self.pos = match.end()
                continue

            # No match, advance position
            self.pos += 1

        return results

    def _parse_attributes(self, attrs_str: str) -> Dict[str, str]:
        """
        Parse attribute string into dict.

        Args:
            attrs_str: Attribute string like 'label="Home" className="nav"'

        Returns:
            Dictionary of attributes
        """
        attrs = {}
        for match in self.ATTR_PATTERN.finditer(attrs_str):
            key = match.group(1)
            value = match.group(2)
            attrs[key] = value
        return attrs


def parse_jsx_file(file_path: str,
                   param_name: Optional[str] = None,
                   drop_standard_tags: bool = True) -> List[Tuple[str, str, List[str]]]:
    """
    Parse JSX file and extract tag information.

    Args:
        file_path: Path to JSX/HTML file
        param_name: Specific attribute to extract (e.g., 'label'). If None, extracts all.
        drop_standard_tags: If True, filter out standard HTML tags from hierarchy

    Returns:
        List of (tag_name, param_value, tag_hierarchy) tuples

    Example:
        >>> parse_jsx_file("App.jsx", param_name="label")
        [("Button", "Submit", ["App", "Form"]), ...]
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    parser = JSXParser(content)
    results = []

    for tag_name, attrs, tag_stack in parser.parse():
        # Filter standard tags from hierarchy if requested
        if drop_standard_tags:
            filtered_stack = [t for t in tag_stack if not is_standard_tag(t)]
        else:
            filtered_stack = tag_stack

        # Extract specific param or all params
        if param_name:
            if param_name in attrs:
                results.append((tag_name, attrs[param_name], filtered_stack))
        else:
            # Include all attributes
            for key, value in attrs.items():
                results.append((tag_name, f"{key}={value}", filtered_stack))

    return results
