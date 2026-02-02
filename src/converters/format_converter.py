"""
Format Converter - Main Facade

Provides high-level API for format conversions.
Implements Facade pattern to simplify access to converter strategies.

Supports:
- Single file conversion
- Batch directory conversion
- Auto format detection
- Roundtrip validation

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

import json
from pathlib import Path
from typing import Union, Dict, Any, List, Optional
import logging

from . import Format, ConversionError, FormatDetectionError
from .factory import ConverterFactory
from .toon import ToonAdapter
from .bson import BsonAdapter

logger = logging.getLogger(__name__)


class FormatConverter:
    """
    Main facade for format conversions.

    Provides simple API for converting between JSON, TOON, and BSON formats.
    Handles file I/O, format detection, and batch operations.
    """

    @classmethod
    def convert(
        cls,
        data: Union[str, bytes, Dict, List],
        source_format: Format,
        target_format: Format
    ) -> Union[str, bytes]:
        """
        Convert data from source format to target format.

        Args:
            data: Input data (string, bytes, or Python object)
            source_format: Source format enum
            target_format: Target format enum

        Returns:
            Converted data (string for JSON/TOON, bytes for BSON)

        Raises:
            ConversionError: If conversion fails

        Example:
            >>> json_data = '{"name": "Alice", "age": 30}'
            >>> toon_str = FormatConverter.convert(json_data, Format.JSON, Format.TOON)
            >>> print(toon_str)
            name: Alice
            age: 30
        """
        # Get appropriate converter
        converter = ConverterFactory.create(source_format, target_format)

        # Perform conversion
        return converter.convert(data)

    @classmethod
    def convert_file(
        cls,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        source_format: Optional[Format] = None,
        target_format: Optional[Format] = None
    ) -> None:
        """
        Convert file from one format to another.

        Args:
            input_path: Path to input file
            output_path: Path to output file
            source_format: Source format (auto-detected from extension if None)
            target_format: Target format (auto-detected from extension if None)

        Raises:
            FileNotFoundError: If input file doesn't exist
            ConversionError: If conversion fails

        Example:
            >>> FormatConverter.convert_file(
            ...     'data.json',
            ...     'data.toon',
            ...     Format.JSON,
            ...     Format.TOON
            ... )
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Auto-detect formats from extensions if not provided
        if source_format is None:
            source_format = Format.from_extension(input_path.suffix)
        if target_format is None:
            target_format = Format.from_extension(output_path.suffix)

        logger.info(f"Converting {input_path} from {source_format.value} to {target_format.value}")

        # Read input file
        if source_format == Format.BSON:
            with open(input_path, 'rb') as f:
                data = f.read()
        else:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = f.read()

        # Convert
        result = cls.convert(data, source_format, target_format)

        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if target_format == Format.BSON:
            with open(output_path, 'wb') as f:
                f.write(result)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)

        logger.info(f"Conversion complete: {output_path}")

    @classmethod
    def batch_convert(
        cls,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        source_format: Format,
        target_format: Format,
        recursive: bool = True
    ) -> Dict[str, Any]:
        """
        Batch convert all files in directory.

        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output files
            source_format: Source format
            target_format: Target format
            recursive: Process subdirectories recursively

        Returns:
            Dict with conversion statistics:
                - 'total': Total files processed
                - 'success': Successfully converted
                - 'failed': Failed conversions
                - 'errors': List of error messages

        Example:
            >>> stats = FormatConverter.batch_convert(
            ...     'json_files/',
            ...     'toon_files/',
            ...     Format.JSON,
            ...     Format.TOON
            ... )
            >>> print(f"Converted {stats['success']}/{stats['total']} files")
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Find all source files
        pattern = f"*.{source_format.value}"
        if recursive:
            files = list(input_dir.rglob(pattern))
        else:
            files = list(input_dir.glob(pattern))

        stats = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'errors': []
        }

        logger.info(f"Batch converting {len(files)} files from {source_format.value} to {target_format.value}")

        for input_file in files:
            # Calculate relative path to preserve directory structure
            rel_path = input_file.relative_to(input_dir)
            output_file = output_dir / rel_path.with_suffix(f".{target_format.value}")

            try:
                cls.convert_file(input_file, output_file, source_format, target_format)
                stats['success'] += 1
            except Exception as e:
                stats['failed'] += 1
                error_msg = f"{input_file}: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(f"Conversion failed: {error_msg}")

        logger.info(f"Batch conversion complete: {stats['success']}/{stats['total']} successful")
        return stats

    @classmethod
    def detect_format(cls, data: Union[str, bytes]) -> Format:
        """
        Auto-detect format from data content.

        Args:
            data: Data to analyze (string or bytes)

        Returns:
            Detected Format enum

        Raises:
            FormatDetectionError: If format cannot be determined

        Example:
            >>> json_str = '{"key": "value"}'
            >>> fmt = FormatConverter.detect_format(json_str)
            >>> print(fmt)
            Format.JSON
        """
        # BSON: binary data
        if isinstance(data, bytes):
            if BsonAdapter.validate(data):
                return Format.BSON
            raise FormatDetectionError("Binary data is not valid BSON")

        # Must be string at this point
        if not isinstance(data, str):
            raise FormatDetectionError(f"Cannot detect format for type: {type(data).__name__}")

        data_stripped = data.strip()

        # Empty string
        if not data_stripped:
            raise FormatDetectionError("Empty string - cannot detect format")

        # JSON: starts with { or [
        if data_stripped[0] in ('{', '['):
            try:
                json.loads(data_stripped)
                return Format.JSON
            except json.JSONDecodeError:
                pass  # Not valid JSON, try other formats

        # TOON: Try to decode
        if ToonAdapter.validate(data_stripped):
            return Format.TOON

        # Last attempt: Try JSON (might be minified or have whitespace)
        try:
            json.loads(data_stripped)
            return Format.JSON
        except json.JSONDecodeError:
            pass

        raise FormatDetectionError(
            "Could not detect format. Data does not match JSON, TOON, or BSON patterns."
        )

    @classmethod
    def validate_roundtrip(
        cls,
        data: Union[str, bytes, Dict, List],
        format_a: Format,
        format_b: Format
    ) -> bool:
        """
        Validate that conversion is lossless (roundtrip test).

        Converts: data → format_b → format_a → compare with original

        Args:
            data: Original data
            format_a: Starting format
            format_b: Intermediate format

        Returns:
            True if roundtrip preserves data exactly

        Example:
            >>> data = {"name": "Alice", "age": 30}
            >>> FormatConverter.validate_roundtrip(data, Format.JSON, Format.TOON)
            True
        """
        try:
            # Convert A → B
            intermediate = cls.convert(data, format_a, format_b)

            # Convert B → A
            restored = cls.convert(intermediate, format_b, format_a)

            # Compare (handle different string formats)
            if isinstance(data, str):
                original_obj = json.loads(data) if format_a == Format.JSON else ToonAdapter.decode(data)
                restored_obj = json.loads(restored) if format_a == Format.JSON else ToonAdapter.decode(restored)
            elif isinstance(data, bytes):
                original_obj = BsonAdapter.decode(data)
                restored_obj = BsonAdapter.decode(restored)
            else:
                # Python object - convert to JSON for comparison
                original_str = json.dumps(data, sort_keys=True)
                if format_a == Format.BSON:
                    restored_obj = BsonAdapter.decode(restored)
                else:
                    restored_obj = json.loads(restored) if format_a == Format.JSON else ToonAdapter.decode(restored)
                restored_str = json.dumps(restored_obj, sort_keys=True)
                return original_str == restored_str

            return original_obj == restored_obj

        except Exception as e:
            logger.error(f"Roundtrip validation failed: {str(e)}")
            return False


__all__ = ['FormatConverter']
