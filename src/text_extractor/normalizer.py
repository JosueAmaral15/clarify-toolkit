"""
Text Normalizer
===============

Utilities for normalizing and transforming text strings.

Supports:
- Case style conversion (snake_case, camelCase, PascalCase, kebab-case)
- Smart truncation with word boundary preservation
- Uppercase transformation
- Special character handling

Author: Josué Amaral
Date: 2025-11-24
"""

import re
from typing import Optional


def smart_truncate(text: str, limit: Optional[str], avoid_cut: bool = True) -> str:
    """
    Truncate text to a character limit, optionally preserving word boundaries.
    
    Args:
        text: Text to truncate
        limit: Character limit ('all', None, or numeric string)
        avoid_cut: If True, cut at last whitespace boundary <= limit
        
    Returns:
        Truncated text
        
    Example:
        >>> smart_truncate("Hello world", "5", avoid_cut=True)
        "Hello"
        >>> smart_truncate("Hello world", "5", avoid_cut=False)
        "Hello"
    """
    if not text or limit in (None, 'all', 'ALL', 'All'):
        return text
    
    try:
        n = int(limit)
    except (ValueError, TypeError):
        return text

    if n <= 0 or len(text) <= n:
        return text

    sub = text[:n]
    
    if avoid_cut:
        # Find last whitespace
        last_space = sub.rfind(' ')
        if last_space > 0:
            return sub[:last_space]
    
    return sub


def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    # Replace non-alphanumeric with spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Split on whitespace and case boundaries
    words = re.sub(r'([a-z])([A-Z])', r'\1 \2', text).split()
    return '_'.join(w.lower() for w in words if w)


def to_camel_case(text: str) -> str:
    """Convert text to camelCase."""
    text = re.sub(r'[^\w\s]', ' ', text)
    words = re.sub(r'([a-z])([A-Z])', r'\1 \2', text).split()
    if not words:
        return ''
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])


def to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    text = re.sub(r'[^\w\s]', ' ', text)
    words = re.sub(r'([a-z])([A-Z])', r'\1 \2', text).split()
    return ''.join(w.capitalize() for w in words if w)


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case."""
    text = re.sub(r'[^\w\s]', ' ', text)
    words = re.sub(r'([a-z])([A-Z])', r'\1 \2', text).split()
    return '-'.join(w.lower() for w in words if w)


def normalize_text(text: str, 
                   case_style: str = 'snake',
                   uppercase: bool = False,
                   limit: Optional[str] = None,
                   avoid_cut: bool = True) -> str:
    """
    Normalize text with case style, truncation, and uppercase options.
    
    Args:
        text: Text to normalize
        case_style: 'snake', 'camel', 'pascal', or 'kebab'
        uppercase: Convert to uppercase after case transformation
        limit: Character limit for truncation
        avoid_cut: Preserve word boundaries when truncating
        
    Returns:
        Normalized text
        
    Example:
        >>> normalize_text("Hello World", case_style="snake")
        "hello_world"
        >>> normalize_text("Hello World", case_style="camel", uppercase=True)
        "HELLOWORLD"
    """
    if not text:
        return text
    
    # Apply case style
    if case_style == 'snake':
        result = to_snake_case(text)
    elif case_style == 'camel':
        result = to_camel_case(text)
    elif case_style == 'pascal':
        result = to_pascal_case(text)
    elif case_style == 'kebab':
        result = to_kebab_case(text)
    else:
        result = text
    
    # Apply uppercase if requested
    if uppercase:
        result = result.upper()
    
    # Apply truncation
    if limit:
        result = smart_truncate(result, limit, avoid_cut)
    
    return result
