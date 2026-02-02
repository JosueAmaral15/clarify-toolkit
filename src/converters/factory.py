"""
Converter Factory

Factory pattern for creating converter instances based on source/target formats.
Maps (source, target) pairs to appropriate converter strategies.

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

from typing import Dict, Tuple

from . import Format, ConversionError
from .strategies import (
    ConverterStrategy,
    JsonToToonConverter,
    ToonToJsonConverter,
    JsonToBsonConverter,
    BsonToJsonConverter,
    ToonToBsonConverter,
    BsonToToonConverter,
)


class ConverterFactory:
    """
    Factory for creating converter instances.

    Maps (source_format, target_format) to appropriate converter class.
    Implements full conversion graph (6 directions).
    """

    # Conversion mapping: (source, target) → Converter class
    _CONVERTERS: Dict[Tuple[Format, Format], type[ConverterStrategy]] = {
        # Direct JSON conversions
        (Format.JSON, Format.TOON): JsonToToonConverter,
        (Format.TOON, Format.JSON): ToonToJsonConverter,
        (Format.JSON, Format.BSON): JsonToBsonConverter,
        (Format.BSON, Format.JSON): BsonToJsonConverter,

        # Indirect conversions (via JSON)
        (Format.TOON, Format.BSON): ToonToBsonConverter,
        (Format.BSON, Format.TOON): BsonToToonConverter,
    }

    @classmethod
    def create(cls, source: Format, target: Format) -> ConverterStrategy:
        """
        Create converter instance for source→target conversion.

        Args:
            source: Source format enum
            target: Target format enum

        Returns:
            Converter strategy instance

        Raises:
            ConversionError: If conversion is not supported

        Example:
            >>> converter = ConverterFactory.create(Format.JSON, Format.TOON)
            >>> toon_str = converter.convert('{"name": "Alice"}')
            >>> print(toon_str)
            name: Alice
        """
        # Check for same format (no conversion needed)
        if source == target:
            raise ConversionError(
                f"Source and target formats are the same: {source.value}. "
                "No conversion needed."
            )

        # Lookup converter class
        converter_class = cls._CONVERTERS.get((source, target))

        if converter_class is None:
            raise ConversionError(
                f"Conversion from {source.value} to {target.value} is not supported. "
                f"Supported conversions: {cls.get_supported_conversions()}"
            )

        # Instantiate and return
        return converter_class()

    @classmethod
    def get_supported_conversions(cls) -> list[tuple[str, str]]:
        """
        Get list of all supported (source, target) conversions.

        Returns:
            List of (source_format, target_format) string tuples

        Example:
            >>> conversions = ConverterFactory.get_supported_conversions()
            >>> print(conversions)
            [('json', 'toon'), ('toon', 'json'), ('json', 'bson'), ...]
        """
        return [
            (source.value, target.value)
            for source, target in cls._CONVERTERS.keys()
        ]

    @classmethod
    def is_conversion_supported(cls, source: Format, target: Format) -> bool:
        """
        Check if conversion from source to target is supported.

        Args:
            source: Source format
            target: Target format

        Returns:
            True if conversion is supported, False otherwise

        Example:
            >>> ConverterFactory.is_conversion_supported(Format.JSON, Format.TOON)
            True
            >>> ConverterFactory.is_conversion_supported(Format.JSON, Format.JSON)
            False
        """
        if source == target:
            return False
        return (source, target) in cls._CONVERTERS


__all__ = ['ConverterFactory']
