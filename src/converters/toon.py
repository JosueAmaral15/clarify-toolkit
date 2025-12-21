"""
TOON (Token-Oriented Object Notation) Adapter

Wrapper around toon-llm library for JSON↔TOON conversion.
Provides encoding, decoding, and validation with custom options.

TOON Format Overview:
- 30-60% token reduction vs JSON for LLM prompts
- Indentation-based syntax
- Tabular format for arrays
- Human-readable and parseable

Example TOON:
    users[2]:
      id,name,role
      1,Alice,admin
      2,Bob,user

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

import json
from typing import Dict, Any, Optional, Union
from pathlib import Path

try:
    from toon import encode as toon_encode
    from toon import decode as toon_decode
    from toon.utils import EncodeOptions, DecodeOptions
except ImportError as e:
    raise ImportError(
        "toon-llm library not installed. "
        "Install with: pip install toon-llm"
    ) from e

from . import ValidationError, ConversionError


class ToonAdapter:
    """
    Adapter for TOON format conversion using toon-llm library.
    
    Provides JSON↔TOON bidirectional conversion with validation.
    """
    
    # Default encoding options (matching toon-llm API)
    DEFAULT_ENCODE_OPTIONS = {
        'indent': 2,
        'delimiter': ',',
        'length_marker': False,  # Use # marker for array lengths
        'quote': '"',
    }
    
    # Default decoding options
    DEFAULT_DECODE_OPTIONS = {
        # toon.decode() has no additional options in current version
    }
    
    @classmethod
    def encode(
        cls,
        data: Union[Dict[str, Any], list],
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convert JSON data to TOON format.
        
        Args:
            data: Python dict or list to convert
            options: Custom encoding options (indent, delimiter, length_marker, quote)
        
        Returns:
            TOON-formatted string
        
        Raises:
            ConversionError: If conversion fails
            ValidationError: If input data is invalid
        
        Example:
            >>> data = {"name": "Alice", "age": 30}
            >>> toon_str = ToonAdapter.encode(data)
            >>> print(toon_str)
            name: Alice
            age: 30
        """
        if not isinstance(data, (dict, list)):
            raise ValidationError(
                f"Input must be dict or list, got {type(data).__name__}"
            )
        
        # Merge with default options
        encode_opts = {**cls.DEFAULT_ENCODE_OPTIONS, **(options or {})}
        
        try:
            # Convert to TOON using toon-llm library
            toon_string = toon_encode(data, **encode_opts)
            return toon_string
        
        except Exception as e:
            raise ConversionError(
                f"Failed to encode JSON to TOON: {str(e)}"
            ) from e
    
    @classmethod
    def decode(
        cls,
        toon_string: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], list]:
        """
        Convert TOON format to JSON data.
        
        Args:
            toon_string: TOON-formatted string
            options: Custom decoding options (strict mode, etc.)
        
        Returns:
            Python dict or list
        
        Raises:
            ConversionError: If conversion fails
            ValidationError: If TOON syntax is invalid
        
        Example:
            >>> toon_str = "name: Alice\\nage: 30"
            >>> data = ToonAdapter.decode(toon_str)
            >>> print(data)
            {'name': 'Alice', 'age': 30}
        """
        if not isinstance(toon_string, str):
            raise ValidationError(
                f"Input must be string, got {type(toon_string).__name__}"
            )
        
        if not toon_string.strip():
            raise ValidationError("Empty TOON string")
        
        # Merge with default options
        decode_opts = {**cls.DEFAULT_DECODE_OPTIONS, **(options or {})}
        
        try:
            # Convert from TOON using toon-llm library
            data = toon_decode(toon_string, **decode_opts)
            return data
        
        except Exception as e:
            raise ConversionError(
                f"Failed to decode TOON to JSON: {str(e)}\n"
                f"TOON content preview: {toon_string[:200]}..."
            ) from e
    
    @classmethod
    def validate(cls, toon_string: str) -> bool:
        """
        Validate TOON syntax without full conversion.
        
        Args:
            toon_string: TOON-formatted string to validate
        
        Returns:
            True if valid TOON syntax, False otherwise
        
        Example:
            >>> ToonAdapter.validate("name: Alice")
            True
            >>> ToonAdapter.validate("[3: 1,2,3")  # Missing bracket
            False
        """
        if not isinstance(toon_string, str):
            return False
        
        if not toon_string.strip():
            return False
        
        try:
            # Attempt to decode - if successful, syntax is valid
            cls.decode(toon_string)
            return True
        except (ConversionError, ValidationError):
            return False
    
    @classmethod
    def encode_file(cls, json_path: Union[str, Path], toon_path: Union[str, Path]) -> None:
        """
        Convert JSON file to TOON file.
        
        Args:
            json_path: Path to input JSON file
            toon_path: Path to output TOON file
        
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ConversionError: If conversion fails
        """
        json_path = Path(json_path)
        toon_path = Path(toon_path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        try:
            # Read JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to TOON
            toon_string = cls.encode(data)
            
            # Write TOON file
            toon_path.parent.mkdir(parents=True, exist_ok=True)
            with open(toon_path, 'w', encoding='utf-8') as f:
                f.write(toon_string)
        
        except json.JSONDecodeError as e:
            raise ConversionError(
                f"Invalid JSON in file {json_path}: {str(e)}"
            ) from e
    
    @classmethod
    def decode_file(cls, toon_path: Union[str, Path], json_path: Union[str, Path]) -> None:
        """
        Convert TOON file to JSON file.
        
        Args:
            toon_path: Path to input TOON file
            json_path: Path to output JSON file
        
        Raises:
            FileNotFoundError: If TOON file doesn't exist
            ConversionError: If conversion fails
        """
        toon_path = Path(toon_path)
        json_path = Path(json_path)
        
        if not toon_path.exists():
            raise FileNotFoundError(f"TOON file not found: {toon_path}")
        
        try:
            # Read TOON file
            with open(toon_path, 'r', encoding='utf-8') as f:
                toon_string = f.read()
            
            # Convert to JSON
            data = cls.decode(toon_string)
            
            # Write JSON file
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            raise ConversionError(
                f"Failed to convert TOON file {toon_path}: {str(e)}"
            ) from e
    
    @classmethod
    def get_token_reduction(cls, json_data: Union[Dict, list]) -> Dict[str, Any]:
        """
        Calculate token count reduction when using TOON vs JSON.
        
        Args:
            json_data: Data to analyze
        
        Returns:
            Dict with 'json_tokens', 'toon_tokens', 'reduction_percent'
        
        Example:
            >>> data = {"users": [{"id": 1}, {"id": 2}]}
            >>> stats = ToonAdapter.get_token_reduction(data)
            >>> print(f"Reduction: {stats['reduction_percent']:.1f}%")
            Reduction: 42.3%
        """
        # Convert to JSON string
        json_string = json.dumps(json_data, separators=(',', ':'))
        
        # Convert to TOON string
        toon_string = cls.encode(json_data)
        
        # Simple token estimation (whitespace-separated words)
        # Note: Real LLMs use tokenizers like tiktoken (GPT) or sentencepiece
        json_tokens = len(json_string.split())
        toon_tokens = len(toon_string.split())
        
        reduction = ((json_tokens - toon_tokens) / json_tokens * 100) if json_tokens > 0 else 0
        
        return {
            'json_tokens': json_tokens,
            'toon_tokens': toon_tokens,
            'reduction_percent': reduction,
            'json_size_bytes': len(json_string.encode('utf-8')),
            'toon_size_bytes': len(toon_string.encode('utf-8')),
        }
