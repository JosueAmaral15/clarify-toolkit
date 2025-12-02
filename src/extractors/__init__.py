"""
Extractors Module

JSX/TSX parameter and attribute extraction parsers.

Author: Josué Amaral
Date: 2025-12-02
"""

from .extractor import Extractor
from .generic_parser import GenericScopeParser
from .jsx_parser import JSXParser

__all__ = ["JSXParser", "GenericScopeParser", "Extractor"]
