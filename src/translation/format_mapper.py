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
    # Character formatting (bits 0-7)
    BOLD = 1 << 0          # 2^0 = 1
    ITALIC = 1 << 1        # 2^1 = 2
    UNDERLINE = 1 << 2     # 2^2 = 4
    STRIKETHROUGH = 1 << 3 # 2^3 = 8
    FONT_COLOR = 1 << 4    # 2^4 = 16
    FONT_SIZE = 1 << 5     # 2^5 = 32
    FONT_FAMILY = 1 << 6   # 2^6 = 64
    HIGHLIGHT = 1 << 7     # 2^7 = 128
    
    # Paragraph formatting (bits 8-11)
    ALIGNMENT = 1 << 8     # 2^8 = 256
    LINE_SPACING = 1 << 9  # 2^9 = 512
    INDENTATION = 1 << 10  # 2^10 = 1024
    HEADING = 1 << 11      # 2^11 = 2048
    
    # Extended character formatting (bits 12-15) - Session 19+
    SUPERSCRIPT = 1 << 12  # 2^12 = 4096
    SUBSCRIPT = 1 << 13    # 2^13 = 8192
    DOUBLE_UNDERLINE = 1 << 14  # 2^14 = 16384
    SMALL_CAPS = 1 << 15   # 2^15 = 32768
    
    # Extended paragraph formatting (bits 16+) - Session 26+
    SPACE_BEFORE_AFTER = 1 << 16  # 2^16 = 65536
    KEEP_LINES_TOGETHER = 1 << 17  # 2^17 = 131072


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
        """Convert segment to tagged text with both character and paragraph formatting."""
        # Build tag with both character and paragraph formats
        has_char_format = self.format_bits != 0
        has_para_format = self.paragraph_format != 0
        
        if not has_char_format and not has_para_format:
            return self.text  # No formatting
        
        # Build format string: "char_bits|para_bits:char_meta|para_meta"
        parts = []
        
        # Character format bits
        parts.append(str(self.format_bits))
        
        # Paragraph format bits (if any)
        if has_para_format:
            parts.append(f"|{self.paragraph_format}")
        
        format_str = "".join(parts)
        
        # Build metadata string
        meta_parts = []
        if self.metadata:
            meta_parts.append(self.metadata)
        if self.paragraph_metadata:
            meta_parts.append(f"|{self.paragraph_metadata}")
        
        if meta_parts:
            metadata_str = "".join(meta_parts)
            return f"<{format_str}:{metadata_str}>{self.text}</{format_str}>"
        else:
            return f"<{format_str}>{self.text}</{format_str}>"



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
            
            # Detect indentation (Session 25)
            # Store as: first_line,left,right in points (e.g., "36,0,0")
            pf = paragraph.paragraph_format
            if pf.first_line_indent or pf.left_indent or pf.right_indent:
                para_format_bits |= FormatBit.INDENTATION
                # Convert EMU to points (914400 EMU = 1 inch = 72 points)
                first_line = int(pf.first_line_indent.pt) if pf.first_line_indent else 0
                left = int(pf.left_indent.pt) if pf.left_indent else 0
                right = int(pf.right_indent.pt) if pf.right_indent else 0
                para_metadata_parts.append(f"{first_line},{left},{right}")
            
            # Detect space before/after paragraphs (Session 26)
            if pf.space_before or pf.space_after:
                para_format_bits |= FormatBit.SPACE_BEFORE_AFTER
                # Convert to points and store as "before,after"
                before = int(pf.space_before.pt) if pf.space_before else 0
                after = int(pf.space_after.pt) if pf.space_after else 0
                para_metadata_parts.append(f"{before},{after}")
            
            # Detect keep lines together (Session 27)
            if pf.keep_together:
                para_format_bits |= FormatBit.KEEP_LINES_TOGETHER
                # Boolean flag, no metadata needed
            
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
                
                # Detect double underline (Session 21)
                # DOCX underline enum: 3 = DOUBLE
                if run.underline == 3:
                    segment.add_format(FormatBit.DOUBLE_UNDERLINE)
                
                # Detect strikethrough (Session 17)
                if run.font.strike:
                    segment.add_format(FormatBit.STRIKETHROUGH)
                
                # Detect font color
                if run.font.color.rgb:
                    segment.add_format(FormatBit.FONT_COLOR)
                    rgb = run.font.color.rgb
                    # Convert RGB to hex string (e.g., FF0000 for red)
                    hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
                    metadata_parts.append(hex_color)
                
                # Detect highlight/background color (Session 18)
                if run.font.highlight_color:
                    segment.add_format(FormatBit.HIGHLIGHT)
                    # DOCX highlight is WD_COLOR_INDEX enum, convert to RGB hex
                    # Map common colors to hex (approximations)
                    highlight_map = {
                        1: 'FFFF00',  # YELLOW
                        2: '00FF00',  # BRIGHT_GREEN
                        3: '00FFFF',  # TURQUOISE
                        4: 'FF00FF',  # PINK
                        5: '0000FF',  # BLUE
                        6: 'FF0000',  # RED
                        7: '800080',  # DARK_BLUE
                        8: '008080',  # TEAL
                        9: '00FF00',  # GREEN
                        10: 'FF00FF', # VIOLET
                        11: '800000', # DARK_RED
                        12: 'FFFF00', # DARK_YELLOW
                        13: '808080', # GRAY_50
                        14: '696969', # GRAY_25
                        15: '000000', # BLACK
                    }
                    highlight_hex = highlight_map.get(run.font.highlight_color, 'FFFF00')
                    metadata_parts.append(highlight_hex)
                
                # Detect superscript (Session 19)
                if run.font.superscript:
                    segment.add_format(FormatBit.SUPERSCRIPT)
                
                # Detect subscript (Session 20)
                if run.font.subscript:
                    segment.add_format(FormatBit.SUBSCRIPT)
                
                # Detect small caps (Session 22)
                if run.font.small_caps:
                    segment.add_format(FormatBit.SMALL_CAPS)
                
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
                    
                    try:
                        # Indentation (Session 25)
                        # ODT uses margin-left, margin-right, text-indent
                        # Helper to convert dimension to points
                        def dim_to_points(dim_str):
                            """Convert ODT dimension (cm, in, pt) to points."""
                            if not dim_str:
                                return 0
                            dim_str = str(dim_str).lower()
                            if 'cm' in dim_str:
                                return int(float(dim_str.replace('cm', '')) * 28.35)  # 1cm = 28.35pt
                            elif 'in' in dim_str:
                                return int(float(dim_str.replace('in', '')) * 72)  # 1in = 72pt
                            elif 'pt' in dim_str:
                                return int(float(dim_str.replace('pt', '')))
                            return 0
                        
                        text_indent = prop.getAttribute('textindent')
                        margin_left = prop.getAttribute('marginleft')
                        margin_right = prop.getAttribute('marginright')
                        
                        if text_indent or margin_left or margin_right:
                            para_format_bits |= FormatBit.INDENTATION
                            first_line = dim_to_points(text_indent) if text_indent else 0
                            left = dim_to_points(margin_left) if margin_left else 0
                            right = dim_to_points(margin_right) if margin_right else 0
                            para_metadata_parts.append(f"{first_line},{left},{right}")
                    except (ValueError, KeyError):
                        pass
                    
                    try:
                        # Space before/after (Session 26)
                        margin_top = prop.getAttribute('margintop')
                        margin_bottom = prop.getAttribute('marginbottom')
                        
                        if margin_top or margin_bottom:
                            para_format_bits |= FormatBit.SPACE_BEFORE_AFTER
                            before = dim_to_points(margin_top) if margin_top else 0
                            after = dim_to_points(margin_bottom) if margin_bottom else 0
                            para_metadata_parts.append(f"{before},{after}")
                    except (ValueError, KeyError):
                        pass
                    
                    try:
                        # Keep lines together (Session 27)
                        # ODT attribute: fo:keep-together = "always"
                        keep_together = prop.getAttribute('keeptogether')
                        if keep_together and str(keep_together).lower() == 'always':
                            para_format_bits |= FormatBit.KEEP_LINES_TOGETHER
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
                        # Helper: Get attribute value ignoring namespace
                        def get_attr(attr_name):
                            """Get attribute value by name, ignoring namespace."""
                            if hasattr(text_prop, 'attributes'):
                                for (ns, name), value in text_prop.attributes.items():
                                    if name == attr_name:
                                        return value
                            return None
                        
                        # Bold
                        font_weight = get_attr('font-weight')
                        if font_weight == 'bold':
                            segment.add_format(FormatBit.BOLD)
                        
                        # Italic
                        font_style = get_attr('font-style')
                        if font_style == 'italic':
                            segment.add_format(FormatBit.ITALIC)
                        
                        # Underline
                        text_underline_style = get_attr('text-underline-style')
                        if text_underline_style and text_underline_style != 'none':
                            segment.add_format(FormatBit.UNDERLINE)
                        
                        # Double underline (Session 21)
                        # ODT uses text-underline-type attribute
                        text_underline_type = get_attr('text-underline-type')
                        if text_underline_type == 'double':
                            segment.add_format(FormatBit.DOUBLE_UNDERLINE)
                        
                        # Strikethrough (Session 17)
                        text_line_through = get_attr('text-line-through-style')
                        if text_line_through and text_line_through != 'none':
                            segment.add_format(FormatBit.STRIKETHROUGH)
                        
                        # Superscript (Session 19)
                        text_position = get_attr('text-position')
                        if text_position and 'super' in str(text_position).lower():
                            segment.add_format(FormatBit.SUPERSCRIPT)
                        
                        # Subscript (Session 20)
                        # Note: Check same text-position attribute but for 'sub'
                        if text_position and 'sub' in str(text_position).lower() and 'super' not in str(text_position).lower():
                            segment.add_format(FormatBit.SUBSCRIPT)
                        
                        # Small caps (Session 22)
                        font_variant = get_attr('font-variant')
                        if font_variant == 'small-caps':
                            segment.add_format(FormatBit.SMALL_CAPS)
                        
                        # Font color
                        color = get_attr('color')
                        if color:
                            segment.add_format(FormatBit.FONT_COLOR)
                            # ODT colors are like "#FF0000" or "#525252", strip the #
                            hex_color = str(color).replace('#', '')
                            metadata_parts.append(hex_color)
                        
                        # Highlight/Background color (Session 18)
                        bg_color = get_attr('background-color')
                        if not bg_color:
                            bg_color = get_attr('text-background-color')
                        if bg_color and bg_color != 'transparent':
                            segment.add_format(FormatBit.HIGHLIGHT)
                            # ODT background colors like "#FFFF00", strip the #
                            hex_bg = str(bg_color).replace('#', '')
                            metadata_parts.append(hex_bg)
                        
                        # Font size
                        font_size = get_attr('font-size')
                        if font_size:
                            segment.add_format(FormatBit.FONT_SIZE)
                            # ODT sizes are like "12pt", strip "pt"
                            size_value = str(font_size).replace('pt', '')
                            metadata_parts.append(size_value)
                        
                        # Font family
                        font_family = get_attr('font-name')
                        if font_family:
                            segment.add_format(FormatBit.FONT_FAMILY)
                            # Remove quotes if present
                            family_name = str(font_family).strip("'\"")
                            metadata_parts.append(family_name)
                
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
        
        # Pattern: <char|para:meta>text</char|para> or variations
        # Format: "char_bits|para_bits:char_meta|para_meta" or simpler combinations
        # Examples:
        #   <1>text</1> - only character format
        #   <1|256>text</1|256> - character + paragraph format
        #   <1:FF0000>text</1> - character format with metadata
        #   <1|256:FF0000|L>text</1|256> - both formats with metadata
        
        # Match patterns like: <1>, <1|256>, <1:meta>, <1|256:meta1|meta2>
        pattern = r'<([\d|]+)(?::([^>]+))>([\s\S]*?)</\1>'
        
        last_pos = 0
        for match in re.finditer(pattern, normalized, re.DOTALL):
            # Add any plain text before this tag
            if match.start() > last_pos:
                plain = normalized[last_pos:match.start()]
                if plain:
                    segments.append(TextSegment(text=plain))
            
            # Parse format bits (char|para or just char)
            format_str = match.group(1)
            char_bits = 0
            para_bits = 0
            if '|' in format_str:
                parts = format_str.split('|')
                char_bits = int(parts[0]) if parts[0] else 0
                para_bits = int(parts[1]) if len(parts) > 1 and parts[1] else 0
            else:
                char_bits = int(format_str)
            
            # Parse metadata (char_meta|para_meta or just char_meta)
            metadata_str = match.group(2) if match.group(2) and match.group(2) != '' else None
            char_meta = None
            para_meta = None
            if metadata_str and '|' in metadata_str:
                meta_parts = metadata_str.split('|', 1)  # Split only on first |
                char_meta = meta_parts[0] if meta_parts[0] else None
                para_meta = meta_parts[1] if len(meta_parts) > 1 and meta_parts[1] else None
            elif metadata_str:
                char_meta = metadata_str
            
            text = match.group(3)
            segments.append(TextSegment(
                text=text,
                format_bits=char_bits,
                metadata=char_meta,
                paragraph_format=para_bits,
                paragraph_metadata=para_meta
            ))
            
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
        
        # Apply double underline (Session 21)
        if format_bits & FormatBit.DOUBLE_UNDERLINE:
            # WD_UNDERLINE.DOUBLE = 3
            run.underline = 3
        
        # Apply strikethrough (Session 17)
        if format_bits & FormatBit.STRIKETHROUGH:
            run.font.strike = True
        
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
        
        # Apply highlight/background color (Session 18)
        if format_bits & FormatBit.HIGHLIGHT and metadata_index < len(metadata_parts):
            hex_bg = metadata_parts[metadata_index].strip()
            metadata_index += 1
            try:
                # Map RGB hex to closest WD_COLOR_INDEX
                from docx.enum.text import WD_COLOR_INDEX
                # Simple mapping based on hex value
                rgb_to_highlight = {
                    'FFFF00': WD_COLOR_INDEX.YELLOW,
                    '00FF00': WD_COLOR_INDEX.BRIGHT_GREEN,
                    '00FFFF': WD_COLOR_INDEX.TURQUOISE,
                    'FF00FF': WD_COLOR_INDEX.PINK,
                    '0000FF': WD_COLOR_INDEX.BLUE,
                    'FF0000': WD_COLOR_INDEX.RED,
                }
                run.font.highlight_color = rgb_to_highlight.get(hex_bg.upper(), WD_COLOR_INDEX.YELLOW)
            except:
                pass  # Skip if mapping fails
        
        # Apply superscript (Session 19)
        if format_bits & FormatBit.SUPERSCRIPT:
            run.font.superscript = True
        
        # Apply subscript (Session 20)
        if format_bits & FormatBit.SUBSCRIPT:
            run.font.subscript = True
        
        # Apply small caps (Session 22)
        if format_bits & FormatBit.SMALL_CAPS:
            run.font.small_caps = True
        
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
        
        # Apply indentation (Session 25)
        if format_bits & FormatBit.INDENTATION and metadata_index < len(metadata_parts):
            indent_str = metadata_parts[metadata_index].strip()
            metadata_index += 1
            try:
                from docx.shared import Pt
                # Parse: "first_line,left,right"
                parts = indent_str.split(',')
                if len(parts) == 3:
                    first_line = int(parts[0])
                    left = int(parts[1])
                    right = int(parts[2])
                    
                    if first_line != 0:
                        paragraph.paragraph_format.first_line_indent = Pt(first_line)
                    if left != 0:
                        paragraph.paragraph_format.left_indent = Pt(left)
                    if right != 0:
                        paragraph.paragraph_format.right_indent = Pt(right)
            except (ValueError, IndexError):
                pass  # Skip invalid indentation
        
        # Apply space before/after (Session 26)
        if format_bits & FormatBit.SPACE_BEFORE_AFTER and metadata_index < len(metadata_parts):
            space_str = metadata_parts[metadata_index].strip()
            metadata_index += 1
            try:
                from docx.shared import Pt
                # Parse: "before,after"
                parts = space_str.split(',')
                if len(parts) == 2:
                    before = int(parts[0])
                    after = int(parts[1])
                    
                    if before != 0:
                        paragraph.paragraph_format.space_before = Pt(before)
                    if after != 0:
                        paragraph.paragraph_format.space_after = Pt(after)
            except (ValueError, IndexError):
                pass  # Skip invalid spacing
        
        # Apply keep lines together (Session 27)
        if format_bits & FormatBit.KEEP_LINES_TOGETHER:
            paragraph.paragraph_format.keep_together = True

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
            
            # Apply double underline (Session 21)
            if format_bits & FormatBit.DOUBLE_UNDERLINE:
                text_props.setAttribute("textunderlinestyle", "solid")
                text_props.setAttribute("textunderlinetype", "double")
                text_props.setAttribute("textunderlinewidth", "auto")
                text_props.setAttribute("textunderlinecolor", "font-color")
            
            # Apply strikethrough (Session 17)
            if format_bits & FormatBit.STRIKETHROUGH:
                text_props.setAttribute("textlinethroughstyle", "solid")
                text_props.setAttribute("textlinethroughwidth", "auto")
                text_props.setAttribute("textlinethroughcolor", "font-color")
            
            # Apply font color
            if format_bits & FormatBit.FONT_COLOR and metadata_index < len(metadata_parts):
                hex_color = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("color", f"#{hex_color}")
            
            # Apply highlight/background color (Session 18)
            if format_bits & FormatBit.HIGHLIGHT and metadata_index < len(metadata_parts):
                hex_bg = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("backgroundcolor", f"#{hex_bg}")
            
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
            
            # Apply superscript (Session 19)
            if format_bits & FormatBit.SUPERSCRIPT:
                text_props.setAttribute("textposition", "super 58%")
            
            # Apply subscript (Session 20)
            if format_bits & FormatBit.SUBSCRIPT:
                text_props.setAttribute("textposition", "sub -58%")
            
            # Apply small caps (Session 22)
            if format_bits & FormatBit.SMALL_CAPS:
                text_props.setAttribute("fontvariant", "small-caps")
            
            style.addElement(text_props)
            doc.automaticstyles.addElement(style)
            style_cache[cache_key] = style
            return style
        
        def get_or_create_para_style(para_format_bits: int, para_metadata: Optional[str]) -> Optional[Style]:
            """Get or create paragraph style for formatting."""
            if para_format_bits == 0:
                return None
            
            cache_key = f"para_{para_format_bits}:{para_metadata or ''}"
            if cache_key in style_cache:
                return style_cache[cache_key]
            
            # Create paragraph style
            style_name = f"ParaFormat{para_format_bits}_{len(style_cache)}"
            style = Style(name=style_name, family="paragraph")
            para_props = ParagraphProperties()
            
            # Parse metadata
            metadata_parts = para_metadata.split(",") if para_metadata else []
            metadata_index = 0
            
            # Apply alignment (Session 23)
            if para_format_bits & FormatBit.ALIGNMENT and metadata_index < len(metadata_parts):
                align_code = metadata_parts[metadata_index].strip()
                metadata_index += 1
                
                align_map = {'L': 'left', 'C': 'center', 'R': 'right', 'J': 'justify'}
                if align_code in align_map:
                    para_props.setAttribute("textalign", align_map[align_code])
            
            # Apply line spacing (Session 24)
            if para_format_bits & FormatBit.LINE_SPACING and metadata_index < len(metadata_parts):
                spacing_str = metadata_parts[metadata_index].strip()
                metadata_index += 1
                try:
                    spacing = float(spacing_str)
                    # ODT uses percentage (1.5 → "150%")
                    para_props.setAttribute("lineheight", f"{int(spacing * 100)}%")
                except ValueError:
                    pass  # Skip invalid spacing
            
            # Apply indentation (Session 25)
            if para_format_bits & FormatBit.INDENTATION and metadata_index < len(metadata_parts):
                indent_str = metadata_parts[metadata_index].strip()
                metadata_index += 1
                try:
                    # Parse: "first_line,left,right" in points
                    parts = indent_str.split(',')
                    if len(parts) == 3:
                        first_line = int(parts[0])
                        left = int(parts[1])
                        right = int(parts[2])
                        
                        # Convert points to cm (1pt = 0.0353cm)
                        if first_line != 0:
                            para_props.setAttribute("textindent", f"{first_line * 0.0353:.2f}cm")
                        if left != 0:
                            para_props.setAttribute("marginleft", f"{left * 0.0353:.2f}cm")
                        if right != 0:
                            para_props.setAttribute("marginright", f"{right * 0.0353:.2f}cm")
                except (ValueError, IndexError):
                    pass  # Skip invalid indentation
            
            # Apply space before/after (Session 26)
            if para_format_bits & FormatBit.SPACE_BEFORE_AFTER and metadata_index < len(metadata_parts):
                space_str = metadata_parts[metadata_index].strip()
                metadata_index += 1
                try:
                    # Parse: "before,after" in points
                    parts = space_str.split(',')
                    if len(parts) == 2:
                        before = int(parts[0])
                        after = int(parts[1])
                        
                        # Convert points to cm (1pt = 0.0353cm)
                        if before != 0:
                            para_props.setAttribute("margintop", f"{before * 0.0353:.2f}cm")
                        if after != 0:
                            para_props.setAttribute("marginbottom", f"{after * 0.0353:.2f}cm")
                except (ValueError, IndexError):
                    pass  # Skip invalid spacing
            
            # Apply keep lines together (Session 27)
            if para_format_bits & FormatBit.KEEP_LINES_TOGETHER:
                para_props.setAttribute("keeptogether", "always")
            
            style.addElement(para_props)
            doc.automaticstyles.addElement(style)
            style_cache[cache_key] = style
            return style
        
        # Create document content
        current_paragraph = P()
        current_para_format = 0
        current_para_metadata = None
        
        for segment in segments:
            # Check if paragraph formatting changed
            if segment.paragraph_format != current_para_format or segment.paragraph_metadata != current_para_metadata:
                # Need to finalize current paragraph and start new one
                if current_paragraph.childNodes or current_paragraph.data:
                    doc.text.addElement(current_paragraph)
                    current_paragraph = P()
                
                current_para_format = segment.paragraph_format
                current_para_metadata = segment.paragraph_metadata
                
                # Apply paragraph style
                para_style = get_or_create_para_style(segment.paragraph_format, segment.paragraph_metadata)
                if para_style:
                    current_paragraph.setAttribute("stylename", para_style)
            
            # Handle paragraph breaks
            if '\n\n' in segment.text:
                parts = segment.text.split('\n\n')
                for i, part in enumerate(parts):
                    # Add text to current paragraph (even if empty)
                    if part:
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
                    
                    # Create new paragraph after each part (including empty ones for blank lines)
                    if i < len(parts) - 1:
                        doc.text.addElement(current_paragraph)
                        current_paragraph = P()
                        # Reapply paragraph style to new paragraph
                        para_style = get_or_create_para_style(current_para_format, current_para_metadata)
                        if para_style:
                            current_paragraph.setAttribute("stylename", para_style)
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
        
        # Add final paragraph (even if empty)
        doc.text.addElement(current_paragraph)
        
        # Save document
        doc.save(output_path)
