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
                metadata_parts = []
                
                # Detect bold
                if run.bold:
                    segment.add_format(FormatBit.BOLD)
                
                # Detect italic
                if run.italic:
                    segment.add_format(FormatBit.ITALIC)
                
                # Detect underline
                if run.underline:
                    segment.add_format(FormatBit.UNDERLINE)
                
                # Detect font color
                if run.font.color.rgb:
                    segment.add_format(FormatBit.FONT_COLOR)
                    rgb = run.font.color.rgb
                    # Convert RGB to hex string (e.g., FF0000 for red)
                    hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
                    metadata_parts.append(hex_color)
                
                # Detect font size
                if run.font.size:
                    segment.add_format(FormatBit.FONT_SIZE)
                    # Convert EMU (English Metric Units) to points
                    points = run.font.size.pt
                    metadata_parts.append(str(int(points)))
                
                # Detect font family
                if run.font.name:
                    segment.add_format(FormatBit.FONT_FAMILY)
                    metadata_parts.append(run.font.name)
                
                # Store metadata if any
                if metadata_parts:
                    segment.metadata = ",".join(metadata_parts)
                
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
        Parse tagged text back into segments with error recovery.
        
        Handles translation edge cases:
        - Whitespace in tags: < 1>text</ 1>
        - Missing closing tags: <1>text (treats as unformatted)
        - Malformed tags: ignored and treated as plain text
        
        Args:
            tagged_text: Text with format tags
            
        Returns:
            List of TextSegment objects
        """
        segments: List[TextSegment] = []
        
        # Normalize whitespace in tags: < 1> → <1>, </ 1> → </1>
        normalized = re.sub(r'<\s*(\d+)(?:\s*:\s*([^>]+))?\s*>', r'<\1:\2>' if ':' in tagged_text else r'<\1>', tagged_text)
        normalized = re.sub(r'</\s*(\d+)\s*>', r'</\1>', normalized)
        
        # Pattern: <tag_id:metadata>text</tag_id> or <tag_id>text</tag_id>
        pattern = r'<(\d+)(?::([^>]+))?>(.*?)</\1>'
        
        last_pos = 0
        for match in re.finditer(pattern, normalized):
            # Add any plain text before this tag
            if match.start() > last_pos:
                plain = normalized[last_pos:match.start()]
                if plain:
                    segments.append(TextSegment(text=plain))
            
            # Add tagged segment
            tag_id = int(match.group(1))
            metadata = match.group(2) if match.group(2) and match.group(2) != '' else None
            text = match.group(3)
            segments.append(TextSegment(text=text, format_bits=tag_id, metadata=metadata))
            
            last_pos = match.end()
        
        # Add any remaining plain text (includes unclosed tags)
        if last_pos < len(normalized):
            plain = normalized[last_pos:]
            if plain:
                segments.append(TextSegment(text=plain))
        
        return segments
    
    @staticmethod
    def create_docx_from_segments(segments: List[TextSegment], output_path: str) -> None:
        """
        Create a DOCX file from text segments with formatting.
        
        Currently supports:
        - Bold (bit 0)
        - Italic (bit 1)
        - Underline (bit 2)
        
        Args:
            segments: List of TextSegment objects with formatting info
            output_path: Path to save the output DOCX file
        """
        from docx import Document
        
        doc = Document()
        current_paragraph = doc.add_paragraph()
        
        for segment in segments:
            # Handle paragraph breaks
            if '\n\n' in segment.text:
                parts = segment.text.split('\n\n')
                for i, part in enumerate(parts):
                    if part:  # Skip empty parts
                        run = current_paragraph.add_run(part)
                        FormatMapper._apply_formatting(run, segment.format_bits, segment.metadata)
                    
                    # Create new paragraph after each part except the last
                    if i < len(parts) - 1:
                        current_paragraph = doc.add_paragraph()
            else:
                # Normal text - add as run to current paragraph
                run = current_paragraph.add_run(segment.text)
                FormatMapper._apply_formatting(run, segment.format_bits, segment.metadata)
        
        # Save document
        doc.save(output_path)
    
    @staticmethod
    def _apply_formatting(run, format_bits: int, metadata: Optional[str] = None) -> None:
        """
        Apply formatting to a DOCX run based on format bits and metadata.
        
        Args:
            run: python-docx Run object
            format_bits: Integer with bit flags for formatting
            metadata: Optional comma-separated metadata (colors, sizes, fonts)
        """
        from docx.shared import RGBColor, Pt
        
        # Parse metadata if present
        metadata_parts = metadata.split(",") if metadata else []
        metadata_index = 0
        
        # Apply basic formatting
        if format_bits & FormatBit.BOLD:
            run.bold = True
        
        if format_bits & FormatBit.ITALIC:
            run.italic = True
        
        if format_bits & FormatBit.UNDERLINE:
            run.underline = True
        
        # Apply font color (metadata: hex RGB)
        if format_bits & FormatBit.FONT_COLOR and metadata_index < len(metadata_parts):
            hex_color = metadata_parts[metadata_index].strip()
            metadata_index += 1
            try:
                # Convert hex string to RGB (e.g., "FF0000" -> (255, 0, 0))
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                run.font.color.rgb = RGBColor(r, g, b)
            except (ValueError, IndexError):
                pass  # Skip invalid colors
        
        # Apply font size (metadata: points)
        if format_bits & FormatBit.FONT_SIZE and metadata_index < len(metadata_parts):
            size_str = metadata_parts[metadata_index].strip()
            metadata_index += 1
            try:
                points = float(size_str)
                run.font.size = Pt(points)
            except ValueError:
                pass  # Skip invalid sizes
        
        # Apply font family (metadata: font name)
        if format_bits & FormatBit.FONT_FAMILY and metadata_index < len(metadata_parts):
            font_name = metadata_parts[metadata_index].strip()
            metadata_index += 1
            if font_name:
                run.font.name = font_name
