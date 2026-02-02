"""
Clarify - Format Converters Module

Provides bidirectional conversion between JSON, TOON, and BSON formats.
Supports full conversion graph (6 directions): JSON↔TOON↔BSON

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

from enum import Enum
from typing import Union, Dict, Any, List


class Format(Enum):
    """Supported file formats for conversion."""
    JSON = "json"
    TOON = "toon"
    BSON = "bson"

    @classmethod
    def from_string(cls, format_str: str) -> 'Format':
        """
        Convert string to Format enum.

        Args:
            format_str: Format name ('json', 'toon', 'bson')

        Returns:
            Format enum value

        Raises:
            ValueError: If format is not supported
        """
        format_str = format_str.lower().strip()
        try:
            return cls(format_str)
        except ValueError:
            raise ValueError(
                f"Unsupported format: '{format_str}'. "
                f"Supported formats: {', '.join([f.value for f in cls])}"
            )

    @classmethod
    def from_extension(cls, extension: str) -> 'Format':
        """
        Detect format from file extension.

        Args:
            extension: File extension (e.g., '.json', '.toon', '.bson')

        Returns:
            Format enum value

        Raises:
            ValueError: If extension is not recognized
        """
        ext = extension.lower().lstrip('.')
        return cls.from_string(ext)


class ConversionError(Exception):
    """Base exception for conversion errors."""
    pass


class ValidationError(ConversionError):
    """Raised when data validation fails."""
    pass


class FormatDetectionError(ConversionError):
    """Raised when format cannot be automatically detected."""
    pass


# Import main converter classes
from .format_converter import FormatConverter
from .factory import ConverterFactory
from .toon import ToonAdapter
from .bson import BsonAdapter

__all__ = [
    'Format',
    'ConversionError',
    'ValidationError',
    'FormatDetectionError',
    'FormatConverter',
    'ConverterFactory',
    'ToonAdapter',
    'BsonAdapter',
]
