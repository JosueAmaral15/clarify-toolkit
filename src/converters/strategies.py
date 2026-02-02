"""
Format Converter Strategies

Implements Strategy pattern for bidirectional format conversions.
Provides 6 converter classes for full graph: JSON↔TOON↔BSON

Each converter handles one specific conversion direction.
For indirect conversions (e.g., TOON→BSON), uses JSON as intermediate.

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List
import json

from .toon import ToonAdapter
from .bson import BsonAdapter
from . import Format, ConversionError


class ConverterStrategy(ABC):
    """
    Abstract base class for format converters (Strategy pattern).

    Each concrete strategy handles one specific conversion direction.
    """

    @abstractmethod
    def convert(self, data: Union[str, bytes, Dict, List]) -> Union[str, bytes]:
        """
        Convert data from source format to target format.

        Args:
            data: Input data in source format

        Returns:
            Output data in target format

        Raises:
            ConversionError: If conversion fails
        """

    @property
    @abstractmethod
    def source_format(self) -> Format:
        """Source format for this converter."""

    @property
    @abstractmethod
    def target_format(self) -> Format:
        """Target format for this converter."""


# ============================================================================
# Direct Converters (4 classes)
# ============================================================================

class JsonToToonConverter(ConverterStrategy):
    """Convert JSON → TOON."""

    source_format = Format.JSON
    target_format = Format.TOON

    def convert(self, data: Union[str, Dict, List]) -> str:
        """
        Convert JSON to TOON format.

        Args:
            data: JSON string or Python dict/list

        Returns:
            TOON formatted string
        """
        # Parse JSON if string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ConversionError(f"Invalid JSON: {str(e)}") from e

        # Convert using ToonAdapter
        return ToonAdapter.encode(data)


class ToonToJsonConverter(ConverterStrategy):
    """Convert TOON → JSON."""

    source_format = Format.TOON
    target_format = Format.JSON

    def convert(self, data: str) -> str:
        """
        Convert TOON to JSON format.

        Args:
            data: TOON formatted string

        Returns:
            JSON string
        """
        # Decode TOON to Python object
        obj = ToonAdapter.decode(data)

        # Convert to JSON string
        return json.dumps(obj, indent=2, ensure_ascii=False)


class JsonToBsonConverter(ConverterStrategy):
    """Convert JSON → BSON."""

    source_format = Format.JSON
    target_format = Format.BSON

    def convert(self, data: Union[str, Dict, List]) -> bytes:
        """
        Convert JSON to BSON format.

        Args:
            data: JSON string or Python dict/list

        Returns:
            BSON binary data
        """
        # Parse JSON if string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ConversionError(f"Invalid JSON: {str(e)}") from e

        # Convert using BsonAdapter
        return BsonAdapter.encode(data)


class BsonToJsonConverter(ConverterStrategy):
    """Convert BSON → JSON."""

    source_format = Format.BSON
    target_format = Format.JSON

    def convert(self, data: bytes) -> str:
        """
        Convert BSON to JSON format.

        Args:
            data: BSON binary data

        Returns:
            JSON string
        """
        # Decode BSON to Python object
        obj = BsonAdapter.decode(data)

        # Convert to JSON string
        return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


# ============================================================================
# Indirect Converters (2 classes) - via JSON intermediate
# ============================================================================

class ToonToBsonConverter(ConverterStrategy):
    """Convert TOON → BSON (via JSON intermediate)."""

    source_format = Format.TOON
    target_format = Format.BSON

    def convert(self, data: str) -> bytes:
        """
        Convert TOON to BSON format via JSON.

        Args:
            data: TOON formatted string

        Returns:
            BSON binary data

        Note:
            Uses JSON as intermediate format:
            TOON → JSON (dict) → BSON
        """
        # Step 1: TOON → JSON (dict)
        obj = ToonAdapter.decode(data)

        # Step 2: JSON (dict) → BSON
        return BsonAdapter.encode(obj)


class BsonToToonConverter(ConverterStrategy):
    """Convert BSON → TOON (via JSON intermediate)."""

    source_format = Format.BSON
    target_format = Format.TOON

    def convert(self, data: bytes) -> str:
        """
        Convert BSON to TOON format via JSON.

        Args:
            data: BSON binary data

        Returns:
            TOON formatted string

        Note:
            Uses JSON as intermediate format:
            BSON → JSON (dict) → TOON
        """
        # Step 1: BSON → JSON (dict)
        obj = BsonAdapter.decode(data)

        # Step 2: JSON (dict) → TOON
        return ToonAdapter.encode(obj)


# ============================================================================
# Export all converter classes
# ============================================================================

__all__ = [
    'ConverterStrategy',
    'JsonToToonConverter',
    'ToonToJsonConverter',
    'JsonToBsonConverter',
    'BsonToJsonConverter',
    'ToonToBsonConverter',
    'BsonToToonConverter',
]
