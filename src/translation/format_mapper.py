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
    paragraph_format: int = 0  # Paragraph-level formatting bits
    paragraph_metadata: Optional[str] = None  # Paragraph metadata (alignment, spacing)
    
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
    
    def add_paragraph_format(self, bit: int, metadata: Optional[str] = None):
        """Add paragraph-level format."""
        self.paragraph_format |= bit
        if metadata:
            if self.paragraph_metadata:
                self.paragraph_metadata += f",{metadata}"
            else:
                self.paragraph_metadata = metadata
    
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
            # Detect paragraph-level formatting
            para_metadata_parts = []
            para_format_bits = 0
            
            # Detect alignment
            if paragraph.alignment is not None:
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                para_format_bits |= FormatBit.ALIGNMENT
                # Map alignment to single letter
                alignment_map = {
                    WD_ALIGN_PARAGRAPH.LEFT: 'L',
                    WD_ALIGN_PARAGRAPH.CENTER: 'C',
                    WD_ALIGN_PARAGRAPH.RIGHT: 'R',
                    WD_ALIGN_PARAGRAPH.JUSTIFY: 'J'
                }
                align_code = alignment_map.get(paragraph.alignment, 'L')
                para_metadata_parts.append(align_code)
            
            # Detect line spacing
            if paragraph.paragraph_format.line_spacing:
                para_format_bits |= FormatBit.LINE_SPACING
                spacing = paragraph.paragraph_format.line_spacing
                # Store as multiplier (e.g., 1.5 for 1.5 line spacing)
                para_metadata_parts.append(f"{spacing:.1f}")
            
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
                
                # Store run-level metadata if any
                if metadata_parts:
                    segment.metadata = ",".join(metadata_parts)
                
                # Store paragraph-level formatting
                segment.paragraph_format = para_format_bits
                if para_metadata_parts:
                    segment.paragraph_metadata = ",".join(para_metadata_parts)
                
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
    def extract_formatted_text_from_odt(file_path: str) -> str:
        """
        Extract text from ODT with formatting tags.
        
        Args:
            file_path: Path to .odt file
            
        Returns:
            Text with embedded format tags
        """
        from odf import opendocument, text as odf_text, style as odf_style
        from odf.element import Text as ODFText
        
        doc = opendocument.load(file_path)
        segments: List[TextSegment] = []
        
        # Build style dictionary for quick lookup
        styles = {}
        for style_element in doc.automaticstyles.childNodes + doc.styles.childNodes:
            if hasattr(style_element, 'getAttribute'):
                try:
                    style_name = style_element.getAttribute('name')
                    if style_name:
                        styles[style_name] = style_element
                except (ValueError, KeyError):
                    # Some elements don't have 'name' attribute - skip them
                    continue
        
        # Process all paragraphs
        for para in doc.getElementsByType(odf_text.P):
            try:
                para_style_name = para.getAttribute('stylename')
            except (ValueError, KeyError):
                para_style_name = None
            para_style = styles.get(para_style_name) if para_style_name else None
            
            # Extract paragraph-level formatting
            para_format_bits = 0
            para_metadata_parts = []
            
            if para_style:
                # Check paragraph properties
                for prop in para_style.getElementsByType(odf_style.ParagraphProperties):
                    try:
                        # Alignment
                        text_align = prop.getAttribute('textalign')
                        if text_align:
                            para_format_bits |= FormatBit.ALIGNMENT
                            align_map = {'start': 'L', 'center': 'C', 'end': 'R', 'justify': 'J'}
                            para_metadata_parts.append(align_map.get(text_align, 'L'))
                    except (ValueError, KeyError):
                        pass
                    
                    try:
                        # Line height
                        line_height = prop.getAttribute('lineheight')
                        if line_height:
                            para_format_bits |= FormatBit.LINE_SPACING
                            # Extract numeric value (e.g., "150%" -> "1.5")
                            if '%' in str(line_height):
                                spacing = float(str(line_height).replace('%', '')) / 100.0
                                para_metadata_parts.append(f"{spacing:.1f}")
                    except (ValueError, KeyError):
                        pass
            
            # Process text content (spans and direct text)
            para_text_nodes = []
            
            def extract_text_recursive(element, current_style_name=None):
                """Recursively extract text with formatting from element tree."""
                # Check if this is a Span with its own style
                # Note: odf_text.Span is a factory function, not a class, so we check qname
                if hasattr(element, 'qname') and element.qname[1] == 'span':
                    try:
                        span_style_name = element.getAttribute('stylename')
                        current_style_name = span_style_name if span_style_name else current_style_name
                    except (ValueError, KeyError):
                        pass
                
                # Process child nodes
                for child in element.childNodes:
                    if isinstance(child, ODFText):
                        # This is actual text content
                        text_content = str(child)
                        if text_content:
                            para_text_nodes.append((text_content, current_style_name))
                    elif hasattr(child, 'childNodes'):
                        # Recursively process container elements
                        extract_text_recursive(child, current_style_name)
            
            extract_text_recursive(para)
            
            # Convert extracted text nodes to segments
            for text_content, style_name in para_text_nodes:
                segment = TextSegment(text=text_content)
                metadata_parts = []
                
                # Apply text formatting from style
                if style_name and style_name in styles:
                    text_style = styles[style_name]
                    
                    for text_prop in text_style.getElementsByType(odf_style.TextProperties):
                        try:
                            # Bold - correct attribute name: 'font-weight'
                            font_weight = text_prop.getAttribute('font-weight')
                            if font_weight == 'bold':
                                segment.add_format(FormatBit.BOLD)
                        except (ValueError, KeyError):
                            pass
                        
                        try:
                            # Italic - correct attribute name: 'font-style'
                            font_style = text_prop.getAttribute('font-style')
                            if font_style == 'italic':
                                segment.add_format(FormatBit.ITALIC)
                        except (ValueError, KeyError):
                            pass
                        
                        try:
                            # Underline - correct attribute name: 'text-underline-style'
                            text_underline_style = text_prop.getAttribute('text-underline-style')
                            if text_underline_style and text_underline_style != 'none':
                                segment.add_format(FormatBit.UNDERLINE)
                        except (ValueError, KeyError):
                            pass
                        
                        try:
                            # Font color - attribute name is correct: 'color'
                            color = text_prop.getAttribute('color')
                            if color:
                                segment.add_format(FormatBit.FONT_COLOR)
                                # ODT colors are like "#FF0000" or "#525252", strip the #
                                hex_color = str(color).replace('#', '')
                                metadata_parts.append(hex_color)
                        except (ValueError, KeyError):
                            pass
                        
                        try:
                            # Font size - correct attribute name: 'font-size'
                            font_size = text_prop.getAttribute('font-size')
                            if font_size:
                                segment.add_format(FormatBit.FONT_SIZE)
                                # ODT sizes are like "12pt", strip "pt"
                                size_value = str(font_size).replace('pt', '')
                                metadata_parts.append(size_value)
                        except (ValueError, KeyError):
                            pass
                        
                        try:
                            # Font family - correct attribute name: 'font-name'
                            font_family = text_prop.getAttribute('font-name')
                            if font_family:
                                segment.add_format(FormatBit.FONT_FAMILY)
                                # Remove quotes if present
                                family_name = str(font_family).strip("'\"")
                                metadata_parts.append(family_name)
                        except (ValueError, KeyError):
                            pass
                
                # Store metadata
                if metadata_parts:
                    segment.metadata = ",".join(metadata_parts)
                
                # Store paragraph-level formatting
                segment.paragraph_format = para_format_bits
                if para_metadata_parts:
                    segment.paragraph_metadata = ",".join(para_metadata_parts)
                
                segments.append(segment)
            
            # Add paragraph break
            if para_text_nodes:
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
    def extract_plain_text_from_segments(segments: List[TextSegment]) -> str:
        """
        Extract plain text from segments (no tags, no formatting).
        
        This is a convenience method for getting clean text from segments
        without having to manually join segment.text values.
        
        Args:
            segments: List of TextSegment objects
            
        Returns:
            Plain text string (no tags)
            
        Example:
            segments = [
                TextSegment(text="Hello", format_bits=1),
                TextSegment(text=" world", format_bits=0)
            ]
            result = extract_plain_text_from_segments(segments)
            # Returns: "Hello world" (no tags)
        """
        return ''.join(seg.text for seg in segments)
    
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
        # Handle tags with metadata: < 1 : FF0000 > → <1:FF0000>
        normalized = re.sub(r'<\s*(\d+)\s*:\s*([^>]+)\s*>', r'<\1:\2>', tagged_text)  # With metadata
        normalized = re.sub(r'<\s*(\d+)\s*>', r'<\1>', normalized)  # Without metadata
        normalized = re.sub(r'</\s*(\d+)\s*>', r'</\1>', normalized)  # Closing tags
        
        # Pattern: <tag_id:metadata>text</tag_id> or <tag_id>text</tag_id>
        # Use [\s\S] instead of . to match newlines
        pattern = r'<(\d+)(?::([^>]+))>([\s\S]*?)</\1>'
        
        last_pos = 0
        for match in re.finditer(pattern, normalized, re.DOTALL):
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
        current_para_format = 0
        current_para_metadata = None
        
        for segment in segments:
            # Check if paragraph formatting changed
            if segment.paragraph_format != current_para_format or segment.paragraph_metadata != current_para_metadata:
                # New paragraph with different formatting
                if current_paragraph.text:  # Don't create empty paragraphs
                    current_paragraph = doc.add_paragraph()
                current_para_format = segment.paragraph_format
                current_para_metadata = segment.paragraph_metadata
                # Apply paragraph formatting
                FormatMapper._apply_paragraph_formatting(current_paragraph, current_para_format, current_para_metadata)
            
            # Handle paragraph breaks
            if '\n\n' in segment.text:
                parts = segment.text.split('\n\n')
                for i, part in enumerate(parts):
                    if part:  # Skip empty parts
                        # Safety: Remove any system tags that leaked into segment text
                        clean_part = FormatMapper.remove_tags(part)
                        run = current_paragraph.add_run(clean_part)
                        FormatMapper._apply_formatting(run, segment.format_bits, segment.metadata)
                    
                    # Create new paragraph after each part except the last
                    if i < len(parts) - 1:
                        current_paragraph = doc.add_paragraph()
                        FormatMapper._apply_paragraph_formatting(current_paragraph, current_para_format, current_para_metadata)
            else:
                # Normal text - add as run to current paragraph
                # Safety: Remove any system tags that leaked into segment text
                clean_text = FormatMapper.remove_tags(segment.text)
                run = current_paragraph.add_run(clean_text)
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
    
    @staticmethod
    def _apply_paragraph_formatting(paragraph, format_bits: int, metadata: Optional[str] = None) -> None:
        """
        Apply paragraph-level formatting.
        
        Args:
            paragraph: python-docx Paragraph object
            format_bits: Integer with bit flags for paragraph formatting
            metadata: Optional comma-separated metadata (alignment, spacing)
        """
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        if not format_bits:
            return
        
        # Parse metadata if present
        metadata_parts = metadata.split(",") if metadata else []
        metadata_index = 0
        
        # Apply alignment
        if format_bits & FormatBit.ALIGNMENT and metadata_index < len(metadata_parts):
            align_code = metadata_parts[metadata_index].strip()
            metadata_index += 1
            
            alignment_map = {
                'L': WD_ALIGN_PARAGRAPH.LEFT,
                'C': WD_ALIGN_PARAGRAPH.CENTER,
                'R': WD_ALIGN_PARAGRAPH.RIGHT,
                'J': WD_ALIGN_PARAGRAPH.JUSTIFY
            }
            if align_code in alignment_map:
                paragraph.alignment = alignment_map[align_code]
        
        # Apply line spacing
        if format_bits & FormatBit.LINE_SPACING and metadata_index < len(metadata_parts):
            spacing_str = metadata_parts[metadata_index].strip()
            metadata_index += 1
            try:
                spacing = float(spacing_str)
                paragraph.paragraph_format.line_spacing = spacing
            except ValueError:
                pass  # Skip invalid spacing

    @staticmethod
    def create_odt_from_segments(segments: List[TextSegment], output_path: str) -> None:
        """
        Create an ODT file from text segments with formatting.
        
        Currently supports:
        - Bold (bit 0)
        - Italic (bit 1)
        - Underline (bit 2)
        - Font colors (bit 4, metadata: hex RGB)
        - Font sizes (bit 5, metadata: pt value)
        - Font families (bit 6, metadata: font name)
        
        Args:
            segments: List of TextSegment objects with formatting info
            output_path: Path to save the output ODT file
        """
        from odf.opendocument import OpenDocumentText
        from odf.style import Style, TextProperties
        from odf.text import P, Span
        
        doc = OpenDocumentText()
        
        # Cache for created styles (avoid duplicates)
        style_cache = {}
        
        def get_or_create_style(format_bits: int, metadata: Optional[str]) -> Optional[Style]:
            """Get existing style or create new one for format combination."""
            if format_bits == 0:
                return None  # No formatting
            
            # Create cache key
            cache_key = f"{format_bits}:{metadata or ''}"
            if cache_key in style_cache:
                return style_cache[cache_key]
            
            # Create new style
            style_name = f"Format{format_bits}_{len(style_cache)}"
            style = Style(name=style_name, family="text")
            text_props = TextProperties()
            
            # Parse metadata
            metadata_parts = metadata.split(",") if metadata else []
            metadata_index = 0
            
            # Apply basic formatting
            if format_bits & FormatBit.BOLD:
                text_props.setAttribute("fontweight", "bold")
            
            if format_bits & FormatBit.ITALIC:
                text_props.setAttribute("fontstyle", "italic")
            
            if format_bits & FormatBit.UNDERLINE:
                text_props.setAttribute("textunderlinestyle", "solid")
                text_props.setAttribute("textunderlinewidth", "auto")
                text_props.setAttribute("textunderlinecolor", "font-color")
            
            # Apply font color
            if format_bits & FormatBit.FONT_COLOR and metadata_index < len(metadata_parts):
                hex_color = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("color", f"#{hex_color}")
            
            # Apply font size
            if format_bits & FormatBit.FONT_SIZE and metadata_index < len(metadata_parts):
                size_str = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("fontsize", f"{size_str}pt")
            
            # Apply font family
            if format_bits & FormatBit.FONT_FAMILY and metadata_index < len(metadata_parts):
                font_name = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("fontfamily", font_name)
            
            style.addElement(text_props)
            doc.automaticstyles.addElement(style)
            style_cache[cache_key] = style
            return style
        
        # Create document content
        current_paragraph = P()
        
        for segment in segments:
            # Handle paragraph breaks
            if '\n\n' in segment.text:
                parts = segment.text.split('\n\n')
                for i, part in enumerate(parts):
                    if part:  # Skip empty parts
                        # Safety: Remove any system tags that leaked
                        clean_part = FormatMapper.remove_tags(part)
                        
                        # Get or create style for this format
                        style = get_or_create_style(segment.format_bits, segment.metadata)
                        
                        if style:
                            span = Span(stylename=style)
                            span.addText(clean_part)
                            current_paragraph.addElement(span)
                        else:
                            current_paragraph.addText(clean_part)
                    
                    # Create new paragraph after each part except the last
                    if i < len(parts) - 1:
                        doc.text.addElement(current_paragraph)
                        current_paragraph = P()
            else:
                # Normal text - add to current paragraph
                # Safety: Remove any system tags that leaked
                clean_text = FormatMapper.remove_tags(segment.text)
                
                # Get or create style for this format
                style = get_or_create_style(segment.format_bits, segment.metadata)
                
                if style:
                    span = Span(stylename=style)
                    span.addText(clean_text)
                    current_paragraph.addElement(span)
                else:
                    current_paragraph.addText(clean_text)
        
        # Add final paragraph if not empty
        if current_paragraph.hasChildNodes() or current_paragraph.data:
            doc.text.addElement(current_paragraph)
        
        # Save document
        doc.save(output_path)
