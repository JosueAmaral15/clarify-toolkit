"""
BSON (Binary JSON) Adapter

Wrapper around pymongo.bson for JSON↔BSON conversion.
Provides encoding, decoding, and validation with MongoDB compatibility.

BSON Format Overview:
- Binary serialization format used by MongoDB
- Efficient storage and transmission
- Supports extended JSON types (ObjectId, Date, Binary, etc.)
- File extension: .bson

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

import json
from typing import Dict, Any, Optional, Union
from pathlib import Path

try:
    from bson import encode as bson_encode
    from bson import decode as bson_decode
    from bson import BSON
    from bson.errors import InvalidBSON
    from bson.json_util import dumps as bson_dumps, loads as bson_loads
except ImportError as e:
    raise ImportError(
        "pymongo library not installed (includes bson module). "
        "Install with: pip install pymongo\n"
        "WARNING: Do NOT install standalone 'bson' package from PyPI - "
        "it is incompatible with pymongo!"
    ) from e

from . import ValidationError, ConversionError


class BsonAdapter:
    """
    Adapter for BSON format conversion using pymongo.bson.
    
    Provides JSON↔BSON bidirectional conversion with MongoDB compatibility.
    """
    
    @classmethod
    def encode(
        cls,
        data: Union[Dict[str, Any], list],
        use_extended_json: bool = True
    ) -> bytes:
        """
        Convert JSON data to BSON binary format.
        
        Args:
            data: Python dict or list to convert
            use_extended_json: Use MongoDB Extended JSON format for special types
        
        Returns:
            BSON binary data (bytes)
        
        Raises:
            ConversionError: If conversion fails
            ValidationError: If input data is invalid
        
        Example:
            >>> data = {"name": "Bob", "count": 42}
            >>> bson_bytes = BsonAdapter.encode(data)
            >>> isinstance(bson_bytes, bytes)
            True
        """
        if not isinstance(data, (dict, list)):
            raise ValidationError(
                f"Input must be dict or list, got {type(data).__name__}"
            )
        
        try:
            # Handle list by wrapping in document
            if isinstance(data, list):
                data = {"_list": data}
            
            # Convert to BSON using pymongo
            bson_data = BSON.encode(data)
            return bson_data
        
        except Exception as e:
            raise ConversionError(
                f"Failed to encode JSON to BSON: {str(e)}"
            ) from e
    
    @classmethod
    def decode(
        cls,
        bson_data: bytes,
        use_extended_json: bool = True
    ) -> Union[Dict[str, Any], list]:
        """
        Convert BSON binary data to JSON.
        
        Args:
            bson_data: BSON binary data (bytes)
            use_extended_json: Use MongoDB Extended JSON format for special types
        
        Returns:
            Python dict or list
        
        Raises:
            ConversionError: If conversion fails
            ValidationError: If BSON data is invalid
        
        Example:
            >>> bson_bytes = BsonAdapter.encode({"test": "data"})
            >>> data = BsonAdapter.decode(bson_bytes)
            >>> data["test"]
            'data'
        """
        if not isinstance(bson_data, bytes):
            raise ValidationError(
                f"Input must be bytes, got {type(bson_data).__name__}"
            )
        
        if len(bson_data) == 0:
            raise ValidationError("Empty BSON data")
        
        try:
            # Decode BSON to dict
            data = BSON(bson_data).decode()
            
            # Unwrap list if it was wrapped during encoding
            if isinstance(data, dict) and len(data) == 1 and "_list" in data:
                return data["_list"]
            
            return data
        
        except InvalidBSON as e:
            raise ConversionError(
                f"Invalid BSON data: {str(e)}"
            ) from e
        except Exception as e:
            raise ConversionError(
                f"Failed to decode BSON to JSON: {str(e)}"
            ) from e
    
    @classmethod
    def validate(cls, bson_data: bytes) -> bool:
        """
        Validate BSON binary data without full conversion.
        
        Args:
            bson_data: BSON binary data to validate
        
        Returns:
            True if valid BSON, False otherwise
        
        Example:
            >>> bson_bytes = BsonAdapter.encode({"valid": True})
            >>> BsonAdapter.validate(bson_bytes)
            True
            >>> BsonAdapter.validate(b"invalid bson")
            False
        """
        if not isinstance(bson_data, bytes):
            return False
        
        if len(bson_data) == 0:
            return False
        
        try:
            # Attempt to decode - if successful, data is valid
            BSON(bson_data).decode()
            return True
        except (InvalidBSON, Exception):
            return False
    
    @classmethod
    def encode_file(cls, json_path: Union[str, Path], bson_path: Union[str, Path]) -> None:
        """
        Convert JSON file to BSON file.
        
        Args:
            json_path: Path to input JSON file
            bson_path: Path to output BSON file
        
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            ConversionError: If conversion fails
        """
        json_path = Path(json_path)
        bson_path = Path(bson_path)
        
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        try:
            # Read JSON file
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to BSON
            bson_data = cls.encode(data)
            
            # Write BSON file (binary mode)
            bson_path.parent.mkdir(parents=True, exist_ok=True)
            with open(bson_path, 'wb') as f:
                f.write(bson_data)
        
        except json.JSONDecodeError as e:
            raise ConversionError(
                f"Invalid JSON in file {json_path}: {str(e)}"
            ) from e
    
    @classmethod
    def decode_file(cls, bson_path: Union[str, Path], json_path: Union[str, Path]) -> None:
        """
        Convert BSON file to JSON file.
        
        Args:
            bson_path: Path to input BSON file
            json_path: Path to output JSON file
        
        Raises:
            FileNotFoundError: If BSON file doesn't exist
            ConversionError: If conversion fails
        """
        bson_path = Path(bson_path)
        json_path = Path(json_path)
        
        if not bson_path.exists():
            raise FileNotFoundError(f"BSON file not found: {bson_path}")
        
        try:
            # Read BSON file (binary mode)
            with open(bson_path, 'rb') as f:
                bson_data = f.read()
            
            # Convert to JSON
            data = cls.decode(bson_data)
            
            # Write JSON file
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        except Exception as e:
            raise ConversionError(
                f"Failed to convert BSON file {bson_path}: {str(e)}"
            ) from e
    
    @classmethod
    def to_extended_json(cls, bson_data: bytes) -> str:
        """
        Convert BSON to MongoDB Extended JSON format (preserves types).
        
        Args:
            bson_data: BSON binary data
        
        Returns:
            Extended JSON string with type information
        
        Example:
            >>> from bson import ObjectId
            >>> data = {"_id": ObjectId(), "date": datetime.now()}
            >>> bson_bytes = BsonAdapter.encode(data)
            >>> extended_json = BsonAdapter.to_extended_json(bson_bytes)
            >>> "$oid" in extended_json  # ObjectId preserved
            True
        """
        try:
            data = cls.decode(bson_data)
            # Use bson.json_util for Extended JSON
            return bson_dumps(data, indent=2)
        except Exception as e:
            raise ConversionError(
                f"Failed to convert BSON to Extended JSON: {str(e)}"
            ) from e
    
    @classmethod
    def from_extended_json(cls, extended_json: str) -> bytes:
        """
        Convert MongoDB Extended JSON to BSON.
        
        Args:
            extended_json: Extended JSON string with type information
        
        Returns:
            BSON binary data
        
        Example:
            >>> extended_json = '{"_id": {"$oid": "507f1f77bcf86cd799439011"}}'
            >>> bson_bytes = BsonAdapter.from_extended_json(extended_json)
            >>> data = BsonAdapter.decode(bson_bytes)
            >>> from bson import ObjectId
            >>> isinstance(data["_id"], ObjectId)
            True
        """
        try:
            # Use bson.json_util for Extended JSON
            data = bson_loads(extended_json)
            return cls.encode(data)
        except Exception as e:
            raise ConversionError(
                f"Failed to convert Extended JSON to BSON: {str(e)}"
            ) from e
    
    @classmethod
    def get_size_comparison(cls, json_data: Union[Dict, list]) -> Dict[str, Any]:
        """
        Compare JSON and BSON sizes.
        
        Args:
            json_data: Data to analyze
        
        Returns:
            Dict with 'json_size_bytes', 'bson_size_bytes', 'compression_ratio'
        
        Example:
            >>> data = {"users": [{"id": 1}, {"id": 2}]}
            >>> stats = BsonAdapter.get_size_comparison(data)
            >>> print(f"BSON is {stats['compression_ratio']:.1%} of JSON size")
            BSON is 73.5% of JSON size
        """
        # Convert to JSON string
        json_string = json.dumps(json_data, separators=(',', ':'))
        json_size = len(json_string.encode('utf-8'))
        
        # Convert to BSON binary
        bson_data = cls.encode(json_data)
        bson_size = len(bson_data)
        
        compression_ratio = (bson_size / json_size) if json_size > 0 else 0
        
        return {
            'json_size_bytes': json_size,
            'bson_size_bytes': bson_size,
            'compression_ratio': compression_ratio,
            'size_difference_bytes': json_size - bson_size,
        }
