#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Format Mapper - Convert document formatting to numeric tags

Uses binary encoding where each format is a power of 2:
- Bit 0 (2^0 = 1): Bold
- Bit 1 (2^1 = 2): Italic
- Bit 2 (2^2 = 4): Underline
- Bit 3 (2^3 = 8): Strikethrough
- Bit 4 (2^4 = 16): Font color (metadata: hex RGB)
- Bit 5 (2^5 = 32): Font size (metadata: pt value)
- Bit 6 (2^6 = 64): Font family (metadata: font name)
- Bit 7 (2^7 = 128): Highlight color (metadata: hex RGB)
- Bit 8 (2^8 = 256): Alignment (metadata: L/C/R/J)
- Bit 9 (2^9 = 512): Line spacing (metadata: multiplier)
- Bit 10 (2^10 = 1024): Indentation (metadata: pt value)
- Bit 11 (2^11 = 2048): Heading level (metadata: 1-6)

Combined formats add up: Bold + Italic = 1 + 2 = 3
Tag format: <tag_id>text</tag_id> or <tag_id:metadata>text</tag_id>

Author: Josué Amaral (COM8)
Date: January 29, 2026
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re


# Format bit masks (powers of 2)
class FormatBit:
    """Bit positions for different formatting types."""
    BOLD = 1 << 0          # 2^0 = 1
    ITALIC = 1 << 1        # 2^1 = 2
    UNDERLINE = 1 << 2     # 2^2 = 4
    STRIKETHROUGH = 1 << 3 # 2^3 = 8
    FONT_COLOR = 1 << 4    # 2^4 = 16
    FONT_SIZE = 1 << 5     # 2^5 = 32
    FONT_FAMILY = 1 << 6   # 2^6 = 64
    HIGHLIGHT = 1 << 7     # 2^7 = 128
    ALIGNMENT = 1 << 8     # 2^8 = 256
    LINE_SPACING = 1 << 9  # 2^9 = 512
    INDENTATION = 1 << 10  # 2^10 = 1024
    HEADING = 1 << 11      # 2^11 = 2048


@dataclass
class TextSegment:
    """A segment of text with its formatting."""
    text: str
    format_bits: int = 0  # Bitwise combination of FormatBit values
    metadata: Optional[str] = None  # Additional format data (colors, sizes, etc.)
    
    def has_format(self, bit: int) -> bool:
        """Check if segment has specific format."""
        return (self.format_bits & bit) != 0
    
    def add_format(self, bit: int, metadata: Optional[str] = None):
        """Add format to segment."""
        self.format_bits |= bit
        if metadata:
            if self.metadata:
                self.metadata += f",{metadata}"
            else:
                self.metadata = metadata
    
    def to_tagged_text(self) -> str:
        """Convert segment to tagged text."""
        if self.format_bits == 0:
            # No formatting, return plain text
            return self.text
        
        if self.metadata:
            return f"<{self.format_bits}:{self.metadata}>{self.text}</{self.format_bits}>"
        else:
            return f"<{self.format_bits}>{self.text}</{self.format_bits}>"


class FormatMapper:
    """
    Extract formatting from documents and convert to tagged text.
    
    Currently supports DOCX format detection.
    ODT support to be added later.
    """
    
    @staticmethod
    def extract_formatted_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX with formatting tags.
        
        Args:
            file_path: Path to .docx file
            
        Returns:
            Text with embedded format tags
        """
        import docx
        
        doc = docx.Document(file_path)
        segments: List[TextSegment] = []
        
        for paragraph in doc.paragraphs:
            # Process each run (a run is a continuous text with same formatting)
            for run in paragraph.runs:
                if not run.text:
                    continue
                
                segment = TextSegment(text=run.text)
                
                # Detect bold
                if run.bold:
                    segment.add_format(FormatBit.BOLD)
                
                # Detect italic
                if run.italic:
                    segment.add_format(FormatBit.ITALIC)
                
                # Detect underline
                if run.underline:
                    segment.add_format(FormatBit.UNDERLINE)
                
                # TODO: Add more format detection (strikethrough, color, size, etc.)
                
                segments.append(segment)
            
            # Add paragraph break
            if paragraph.text:
                segments.append(TextSegment(text="\n\n"))
        
        # Convert segments to tagged text
        tagged_text = "".join(seg.to_tagged_text() for seg in segments)
        
        # Clean up excessive newlines
        tagged_text = re.sub(r'\n{3,}', '\n\n', tagged_text)
        
        return tagged_text.strip()
    
    @staticmethod
    def remove_tags(tagged_text: str) -> str:
        """
        Remove all format tags from text.
        
        Args:
            tagged_text: Text with format tags
            
        Returns:
            Plain text without tags
        """
        # Remove tags like <123>text</123> or <123:metadata>text</123>
        plain_text = re.sub(r'<\d+(?::[^>]+)?>(.*?)</\d+>', r'\1', tagged_text)
        return plain_text
    
    @staticmethod
    def parse_tagged_text(tagged_text: str) -> List[TextSegment]:
        """
        Parse tagged text back into segments.
        
        Args:
            tagged_text: Text with format tags
            
        Returns:
            List of TextSegment objects
        """
        segments: List[TextSegment] = []
        
        # Pattern: <tag_id:metadata>text</tag_id> or <tag_id>text</tag_id>
        pattern = r'<(\d+)(?::([^>]+))?>(.*?)</\1>'
        
        last_pos = 0
        for match in re.finditer(pattern, tagged_text):
            # Add any plain text before this tag
            if match.start() > last_pos:
                plain = tagged_text[last_pos:match.start()]
                if plain:
                    segments.append(TextSegment(text=plain))
            
            # Add tagged segment
            tag_id = int(match.group(1))
            metadata = match.group(2)
            text = match.group(3)
            segments.append(TextSegment(text=text, format_bits=tag_id, metadata=metadata))
            
            last_pos = match.end()
        
        # Add any remaining plain text
        if last_pos < len(tagged_text):
            plain = tagged_text[last_pos:]
            if plain:
                segments.append(TextSegment(text=plain))
        
        return segments
