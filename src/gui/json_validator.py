#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Validator - Real-time JSON Validation

Provides JSON syntax validation with error reporting (line, column, message).
Uses Strategy pattern for extensibility to other formats (XML, YAML, TOML).

Pattern: Strategy (GoF)
- Encapsulates validation algorithm
- Easy to add new validators (XMLValidator, YAMLValidator)
"""

from __future__ import annotations
from typing import Tuple, Optional
import json
import re


class ValidationResult:
    """
    Encapsulates validation result.
    
    Pattern: Value Object (DDD)
    - Immutable representation of validation state
    """
    
    def __init__(self, is_valid: bool, error_msg: str = "", line: int = -1, col: int = -1):
        self.is_valid = is_valid
        self.error_msg = error_msg
        self.line = line
        self.col = col
    
    def __repr__(self):
        if self.is_valid:
            return "ValidationResult(valid)"
        return f"ValidationResult(invalid, line={self.line}, col={self.col}, error='{self.error_msg}')"


class JsonValidator:
    """
    JSON validator with detailed error reporting.
    
    Pattern: Strategy (GoF)
    - Concrete strategy for JSON validation
    - Can be swapped with XMLValidator, YAMLValidator, etc.
    
    Usage:
        validator = JsonValidator()
        result = validator.validate(text)
        if not result.is_valid:
            print(f"Error at line {result.line}, col {result.col}: {result.error_msg}")
    """
    
    def validate(self, text: str) -> ValidationResult:
        """
        Validate JSON text.
        
        Args:
            text: JSON string to validate
        
        Returns:
            ValidationResult with validity status and error details
        """
        if not text or not text.strip():
            return ValidationResult(False, "Empty JSON", 1, 1)
        
        try:
            json.loads(text)
            return ValidationResult(True)
        except json.JSONDecodeError as e:
            # Extract line and column from error message
            return ValidationResult(
                False,
                error_msg=e.msg,
                line=e.lineno,
                col=e.colno
            )
        except Exception as e:
            # Generic error
            return ValidationResult(False, str(e), 1, 1)
    
    def format_json(self, text: str, indent: int = 2) -> Tuple[bool, str]:
        """
        Format JSON with proper indentation.
        
        Args:
            text: JSON string to format
            indent: Number of spaces for indentation (2 or 4)
        
        Returns:
            Tuple of (success: bool, formatted_text: str or error_msg)
        """
        try:
            obj = json.loads(text)
            formatted = json.dumps(obj, indent=indent, ensure_ascii=False, sort_keys=False)
            return (True, formatted)
        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON at line {e.lineno}, col {e.colno}: {e.msg}")
        except Exception as e:
            return (False, f"Error formatting JSON: {str(e)}")
    
    def minify_json(self, text: str) -> Tuple[bool, str]:
        """
        Minify JSON (remove whitespace).
        
        Args:
            text: JSON string to minify
        
        Returns:
            Tuple of (success: bool, minified_text: str or error_msg)
        """
        try:
            obj = json.loads(text)
            minified = json.dumps(obj, separators=(',', ':'), ensure_ascii=False)
            return (True, minified)
        except json.JSONDecodeError as e:
            return (False, f"Invalid JSON at line {e.lineno}, col {e.colno}: {e.msg}")
        except Exception as e:
            return (False, f"Error minifying JSON: {str(e)}")


class ValidatorFactory:
    """
    Factory for creating validators based on file type.
    
    Pattern: Factory Method (GoF)
    - Encapsulates validator creation logic
    - Easy to extend with new validator types
    """
    
    @staticmethod
    def create_validator(file_type: str) -> Optional[JsonValidator]:
        """
        Create validator for given file type.
        
        Args:
            file_type: File extension (e.g., 'json', 'xml', 'yaml')
        
        Returns:
            Validator instance or None if type not supported
        """
        file_type = file_type.lower().lstrip('.')
        
        if file_type == 'json':
            return JsonValidator()
        # Future: Add XMLValidator, YAMLValidator, TOMLValidator
        # elif file_type == 'xml':
        #     return XMLValidator()
        # elif file_type in ['yaml', 'yml']:
        #     return YAMLValidator()
        
        return None
