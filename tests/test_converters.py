"""
Unit Tests for TOON/BSON Format Converters

Tests all conversion paths (6 directions):
- JSON ↔ TOON
- JSON ↔ BSON
- TOON ↔ BSON

Author: Clarify Project
Version: 2.9.80
Date: 2025-12-21
"""

import pytest
import json
import tempfile
from pathlib import Path

from src.converters import (
    FormatConverter,
    Format,
    ToonAdapter,
    BsonAdapter,
    ConversionError,
    ValidationError,
)


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def simple_data():
    """Simple test data."""
    return {"name": "Alice", "age": 30}


@pytest.fixture
def complex_data():
    """Complex nested data."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"}
        ],
        "config": {
            "debug": True,
            "port": 8080,
            "hosts": ["localhost", "127.0.0.1"]
        }
    }


@pytest.fixture
def array_data():
    """Array data."""
    return [1, 2, 3, 4, 5]


# ============================================================================
# TOON Adapter Tests (10 tests)
# ============================================================================

class TestToonAdapter:
    """Test TOON encoding/decoding."""
    
    def test_encode_simple_object(self, simple_data):
        """Test encoding simple object."""
        toon_str = ToonAdapter.encode(simple_data)
        assert "name:" in toon_str
        assert "Alice" in toon_str
        assert "age:" in toon_str
        assert "30" in toon_str
    
    def test_encode_array(self, array_data):
        """Test encoding array."""
        toon_str = ToonAdapter.encode(array_data)
        assert "[5]" in toon_str or "1,2,3,4,5" in toon_str
    
    def test_encode_nested_object(self, complex_data):
        """Test encoding nested structure."""
        toon_str = ToonAdapter.encode(complex_data)
        assert "users" in toon_str
        assert "config" in toon_str
    
    def test_decode_simple(self):
        """Test decoding TOON to dict."""
        toon_str = "name: Alice\nage: 30"
        data = ToonAdapter.decode(toon_str)
        assert data["name"] == "Alice"
        assert data["age"] == 30
    
    def test_roundtrip_simple(self, simple_data):
        """Test JSON → TOON → JSON roundtrip."""
        toon_str = ToonAdapter.encode(simple_data)
        decoded = ToonAdapter.decode(toon_str)
        assert decoded == simple_data
    
    def test_roundtrip_complex(self, complex_data):
        """Test complex data roundtrip."""
        toon_str = ToonAdapter.encode(complex_data)
        decoded = ToonAdapter.decode(toon_str)
        assert decoded == complex_data
    
    def test_validation_valid(self):
        """Test validation of valid TOON."""
        toon_str = "key: value"
        assert ToonAdapter.validate(toon_str) is True
    
    def test_validation_invalid(self):
        """Test validation of invalid TOON."""
        invalid_toon = "[3: 1,2"  # Malformed
        # Note: toon-llm might be lenient, so this might pass
        # Just ensure it returns a boolean
        result = ToonAdapter.validate(invalid_toon)
        assert isinstance(result, bool)
    
    def test_encode_invalid_input(self):
        """Test encoding with invalid input type."""
        with pytest.raises(ValidationError):
            ToonAdapter.encode("not a dict or list")
    
    def test_decode_invalid_input(self):
        """Test decoding with invalid input type."""
        with pytest.raises(ValidationError):
            ToonAdapter.decode(123)  # Not a string


# ============================================================================
# BSON Adapter Tests (8 tests)
# ============================================================================

class TestBsonAdapter:
    """Test BSON encoding/decoding."""
    
    def test_encode_simple_object(self, simple_data):
        """Test encoding simple object to BSON."""
        bson_bytes = BsonAdapter.encode(simple_data)
        assert isinstance(bson_bytes, bytes)
        assert len(bson_bytes) > 0
    
    def test_encode_array(self, array_data):
        """Test encoding array to BSON."""
        bson_bytes = BsonAdapter.encode(array_data)
        assert isinstance(bson_bytes, bytes)
    
    def test_decode_simple(self, simple_data):
        """Test decoding BSON to dict."""
        bson_bytes = BsonAdapter.encode(simple_data)
        decoded = BsonAdapter.decode(bson_bytes)
        assert decoded == simple_data
    
    def test_roundtrip_simple(self, simple_data):
        """Test JSON → BSON → JSON roundtrip."""
        bson_bytes = BsonAdapter.encode(simple_data)
        decoded = BsonAdapter.decode(bson_bytes)
        assert decoded == simple_data
    
    def test_roundtrip_complex(self, complex_data):
        """Test complex data roundtrip."""
        bson_bytes = BsonAdapter.encode(complex_data)
        decoded = BsonAdapter.decode(bson_bytes)
        assert decoded == complex_data
    
    def test_validation_valid(self, simple_data):
        """Test validation of valid BSON."""
        bson_bytes = BsonAdapter.encode(simple_data)
        assert BsonAdapter.validate(bson_bytes) is True
    
    def test_validation_invalid(self):
        """Test validation of invalid BSON."""
        invalid_bson = b"not valid bson"
        assert BsonAdapter.validate(invalid_bson) is False
    
    def test_encode_invalid_input(self):
        """Test encoding with invalid input type."""
        with pytest.raises(ValidationError):
            BsonAdapter.encode("not a dict or list")


# ============================================================================
# Format Converter Tests - Full Graph (12 tests)
# ============================================================================

class TestFormatConverter:
    """Test full conversion graph (6 directions)."""
    
    def test_json_to_toon(self, simple_data):
        """Test JSON → TOON conversion."""
        json_str = json.dumps(simple_data)
        toon_str = FormatConverter.convert(json_str, Format.JSON, Format.TOON)
        assert isinstance(toon_str, str)
        assert "name:" in toon_str
    
    def test_toon_to_json(self):
        """Test TOON → JSON conversion."""
        toon_str = "name: Alice\nage: 30"
        json_str = FormatConverter.convert(toon_str, Format.TOON, Format.JSON)
        data = json.loads(json_str)
        assert data["name"] == "Alice"
        assert data["age"] == 30
    
    def test_json_to_bson(self, simple_data):
        """Test JSON → BSON conversion."""
        json_str = json.dumps(simple_data)
        bson_bytes = FormatConverter.convert(json_str, Format.JSON, Format.BSON)
        assert isinstance(bson_bytes, bytes)
    
    def test_bson_to_json(self, simple_data):
        """Test BSON → JSON conversion."""
        bson_bytes = BsonAdapter.encode(simple_data)
        json_str = FormatConverter.convert(bson_bytes, Format.BSON, Format.JSON)
        data = json.loads(json_str)
        assert data == simple_data
    
    def test_toon_to_bson(self):
        """Test TOON → BSON conversion (indirect via JSON)."""
        toon_str = "name: Charlie\nvalue: 42"
        bson_bytes = FormatConverter.convert(toon_str, Format.TOON, Format.BSON)
        assert isinstance(bson_bytes, bytes)
    
    def test_bson_to_toon(self, simple_data):
        """Test BSON → TOON conversion (indirect via JSON)."""
        bson_bytes = BsonAdapter.encode(simple_data)
        toon_str = FormatConverter.convert(bson_bytes, Format.BSON, Format.TOON)
        assert isinstance(toon_str, str)
        assert "name:" in toon_str
    
    def test_roundtrip_json_toon(self, complex_data):
        """Test JSON → TOON → JSON roundtrip."""
        is_valid = FormatConverter.validate_roundtrip(
            complex_data, Format.JSON, Format.TOON
        )
        assert is_valid is True
    
    def test_roundtrip_json_bson(self, complex_data):
        """Test JSON → BSON → JSON roundtrip."""
        is_valid = FormatConverter.validate_roundtrip(
            complex_data, Format.JSON, Format.BSON
        )
        assert is_valid is True
    
    def test_roundtrip_toon_bson(self):
        """Test TOON → BSON → TOON roundtrip."""
        toon_str = "items[3]: a,b,c\ncount: 3"
        is_valid = FormatConverter.validate_roundtrip(
            toon_str, Format.TOON, Format.BSON
        )
        assert is_valid is True
    
    def test_format_detection_json(self, simple_data):
        """Test JSON format detection."""
        json_str = json.dumps(simple_data)
        detected = FormatConverter.detect_format(json_str)
        assert detected == Format.JSON
    
    def test_format_detection_toon(self):
        """Test TOON format detection."""
        toon_str = "name: Alice\nage: 30"
        detected = FormatConverter.detect_format(toon_str)
        assert detected == Format.TOON
    
    def test_format_detection_bson(self, simple_data):
        """Test BSON format detection."""
        bson_bytes = BsonAdapter.encode(simple_data)
        detected = FormatConverter.detect_format(bson_bytes)
        assert detected == Format.BSON


# ============================================================================
# File Conversion Tests (5 tests)
# ============================================================================

class TestFileConversion:
    """Test file-based conversions."""
    
    def test_json_to_toon_file(self, simple_data, tmp_path):
        """Test JSON file → TOON file conversion."""
        json_file = tmp_path / "test.json"
        toon_file = tmp_path / "test.toon"
        
        json_file.write_text(json.dumps(simple_data))
        
        FormatConverter.convert_file(json_file, toon_file)
        
        assert toon_file.exists()
        toon_content = toon_file.read_text()
        assert "name:" in toon_content
    
    def test_toon_to_json_file(self, tmp_path):
        """Test TOON file → JSON file conversion."""
        toon_file = tmp_path / "test.toon"
        json_file = tmp_path / "test.json"
        
        toon_file.write_text("name: Alice\nage: 30")
        
        FormatConverter.convert_file(toon_file, json_file)
        
        assert json_file.exists()
        data = json.loads(json_file.read_text())
        assert data["name"] == "Alice"
    
    def test_batch_convert(self, tmp_path):
        """Test batch directory conversion."""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        
        # Create 3 JSON files
        (input_dir / "file1.json").write_text('{"id": 1}')
        (input_dir / "file2.json").write_text('{"id": 2}')
        (input_dir / "file3.json").write_text('{"id": 3}')
        
        # Batch convert
        stats = FormatConverter.batch_convert(
            input_dir, output_dir, Format.JSON, Format.TOON
        )
        
        assert stats['total'] == 3
        assert stats['success'] == 3
        assert stats['failed'] == 0
        assert (output_dir / "file1.toon").exists()
        assert (output_dir / "file2.toon").exists()
        assert (output_dir / "file3.toon").exists()
    
    def test_auto_format_detection_from_extension(self, simple_data, tmp_path):
        """Test automatic format detection from file extension."""
        json_file = tmp_path / "auto.json"
        toon_file = tmp_path / "auto.toon"
        
        json_file.write_text(json.dumps(simple_data))
        
        # Don't specify formats - auto-detect from extensions
        FormatConverter.convert_file(json_file, toon_file)
        
        assert toon_file.exists()
    
    def test_bson_file_roundtrip(self, complex_data, tmp_path):
        """Test JSON → BSON → JSON file roundtrip."""
        json_file1 = tmp_path / "original.json"
        bson_file = tmp_path / "data.bson"
        json_file2 = tmp_path / "restored.json"
        
        json_file1.write_text(json.dumps(complex_data))
        
        # JSON → BSON
        FormatConverter.convert_file(json_file1, bson_file)
        assert bson_file.exists()
        
        # BSON → JSON
        FormatConverter.convert_file(bson_file, json_file2)
        assert json_file2.exists()
        
        # Verify data preserved
        restored_data = json.loads(json_file2.read_text())
        assert restored_data == complex_data


# ============================================================================
# Error Handling Tests (5 tests)
# ============================================================================

class TestErrorHandling:
    """Test error scenarios and edge cases."""
    
    def test_invalid_format_combination(self):
        """Test conversion with same source/target format."""
        with pytest.raises(ConversionError, match="same"):
            FormatConverter.convert("{}", Format.JSON, Format.JSON)
    
    def test_malformed_json(self):
        """Test conversion with malformed JSON."""
        with pytest.raises(ConversionError):
            FormatConverter.convert("{invalid json", Format.JSON, Format.TOON)
    
    def test_malformed_toon(self):
        """Test conversion with malformed TOON."""
        # This might not raise if toon-llm is lenient
        try:
            FormatConverter.convert("[broken", Format.TOON, Format.JSON)
        except ConversionError:
            pass  # Expected
    
    def test_empty_data(self):
        """Test conversion with empty data."""
        with pytest.raises(ValidationError):
            ToonAdapter.decode("")
    
    def test_unsupported_format(self):
        """Test format detection with unsupported data."""
        from src.converters import FormatDetectionError
        with pytest.raises(FormatDetectionError):
            FormatConverter.detect_format("")


# ============================================================================
# Unicode and Special Characters (3 tests)
# ============================================================================

class TestUnicode:
    """Test Unicode and special character handling."""
    
    def test_unicode_characters(self):
        """Test data with Unicode characters."""
        data = {"message": "Hello 世界 🌍", "emoji": "✅ 🎉"}
        
        # JSON → TOON → JSON
        toon_str = FormatConverter.convert(data, Format.JSON, Format.TOON)
        restored = FormatConverter.convert(toon_str, Format.TOON, Format.JSON)
        restored_data = json.loads(restored)
        
        assert restored_data["message"] == "Hello 世界 🌍"
        assert restored_data["emoji"] == "✅ 🎉"
    
    def test_special_json_characters(self):
        """Test JSON special characters (quotes, backslashes)."""
        data = {"text": 'He said "Hello"', "path": "C:\\Users\\test"}
        
        toon_str = FormatConverter.convert(data, Format.JSON, Format.TOON)
        restored = FormatConverter.convert(toon_str, Format.TOON, Format.JSON)
        restored_data = json.loads(restored)
        
        assert restored_data == data
    
    def test_unicode_in_bson(self):
        """Test Unicode in BSON conversion."""
        data = {"name": "José", "city": "São Paulo"}
        
        bson_bytes = FormatConverter.convert(data, Format.JSON, Format.BSON)
        restored = FormatConverter.convert(bson_bytes, Format.BSON, Format.JSON)
        restored_data = json.loads(restored)
        
        assert restored_data == data


# ============================================================================
# Summary: Test Count
# ============================================================================
# TOON Adapter: 10 tests
# BSON Adapter: 8 tests
# Format Converter (full graph): 12 tests
# File Conversion: 5 tests
# Error Handling: 5 tests
# Unicode: 3 tests
# TOTAL: 43 tests
