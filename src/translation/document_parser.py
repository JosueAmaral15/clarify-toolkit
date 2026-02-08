#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document Parser Module - Extract text from .docx and .odt files

Supports:
- Microsoft Word (.docx) files
- OpenDocument Text (.odt) files
- Plain text (.txt) files

Part of formatting preservation feature for Google Translate tool.

Author: Josué Amaral (COM8)
Date: January 27, 2026
"""

from pathlib import Path
from typing import Optional
import docx


class DocumentParserError(Exception):
    """Base exception for document parsing errors."""
    pass


class UnsupportedFileTypeError(DocumentParserError):
    """Raised when file type is not supported."""
    pass


class DocumentParser:
    """
    Parse documents and extract text content.
    
    Supports .txt, .docx, and .odt files.
    """
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extract plain text from document file.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Plain text content
            
        Raises:
            FileNotFoundError: If file doesn't exist
            UnsupportedFileTypeError: If file type not supported
            DocumentParserError: If parsing fails
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        
        if suffix == ".txt":
            return DocumentParser._extract_text_from_txt(file_path)
        elif suffix == ".docx":
            return DocumentParser._extract_text_from_docx(file_path)
        elif suffix == ".odt":
            return DocumentParser._extract_text_from_odt(file_path)
        else:
            raise UnsupportedFileTypeError(
                f"Unsupported file type: {suffix}. Supported: .txt, .docx, .odt"
            )
    
    @staticmethod
    def _extract_text_from_txt(file_path: str) -> str:
        """Extract text from .txt file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
    
    @staticmethod
    def _extract_text_from_docx(file_path: str) -> str:
        """
        Extract plain text from .docx file.
        
        Currently extracts only text content, ignoring formatting.
        Future: Will preserve formatting with tags.
        """
        try:
            doc = docx.Document(file_path)
            
            # Extract text from all paragraphs
            paragraphs = []
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:  # Only add non-empty paragraphs
                    paragraphs.append(text)
            
            return "\n\n".join(paragraphs)
            
        except Exception as e:
            raise DocumentParserError(f"Failed to parse .docx file: {str(e)}")
    
    @staticmethod
    def _extract_text_from_odt(file_path: str) -> str:
        """
        Extract plain text from .odt file.
        
        Currently extracts only text content, ignoring formatting.
        Future: Will preserve formatting with tags.
        """
        try:
            from odf import text, teletype
            from odf.opendocument import load
            
            # Load ODT document
            doc = load(file_path)
            
            # Extract all text elements in document order
            paragraphs = []
            
            # Get the main text body
            for element in doc.getElementsByType(text.P) + doc.getElementsByType(text.H):
                text_content = teletype.extractText(element).strip()
                if text_content:  # Only add non-empty content
                    paragraphs.append(text_content)
            
            return "\n\n".join(paragraphs) if paragraphs else ""
            
        except Exception as e:
            raise DocumentParserError(f"Failed to parse .odt file: {str(e)}")


# Convenience function
def extract_text_from_document(file_path: str) -> str:
    """
    Convenience function to extract text from any supported document.
    
    Args:
        file_path: Path to document
        
    Returns:
        Plain text content
    """
    return DocumentParser.extract_text(file_path)
