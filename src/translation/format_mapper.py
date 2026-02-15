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


# ============================================================================
# Session 75 - Placeholder Protection System for 100% Tag Preservation
# ============================================================================

def replace_tags_with_placeholders(tagged_text: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Replace format tags with Unicode placeholders before translation.
    
    This prevents Google Translate from corrupting or deleting format tags.
    
    Session 76 FIX: Now handles BOTH paired tags AND adjacent unpaired tags
    
    Example:
        Input:  "<113|65536:Arial|0,0>RISKS</113|65536>"
        Output: ("【FMT001】RISKS【/FMT001】", {mapping})
        
        Input:  "Header</113|65536><112|65536:Arial|0,0>Body"
        Output: ("Header【FMTC001】【FMTO002】Body", {mapping})
    
    Args:
        tagged_text: Text with format tags like <113|65536:Arial|0,0>text</113|65536>
        
    Returns:
        (text_with_placeholders, mapping)
        - text_with_placeholders: Text with 【FMTXXX】 placeholders
        - mapping: Dict mapping IDs to original tag info
        
    Author: COM8 (Sessions 75, 76)
    """
    mapping = {}
    counter = 1
    result = tagged_text
    
    # PASS 1: Match complete tag pairs with content: <opening>text</closing>
    # This handles the majority of normal formatted text
    # BUT: Skip pairs with ONLY whitespace (those are span transitions)
    paired_pattern = r'<(\d+(?:\|\d+)?:[^>]+)>([^<]+?)</(\d+(?:\|\d+)?)>'
    
    def replace_paired_match(match):
        nonlocal counter
        opening_tag = match.group(1)
        text_inside = match.group(2)
        closing_tag = match.group(3)
        
        # Session 76.3 FIX: If content is ONLY whitespace, don't treat as paired
        # These are span transitions and should be handled as individual tags
        if text_inside.strip() == '':
            # Return unchanged - will be caught by Pass 2/3 as individual tags
            return match.group(0)
        
        # Generate unique ID
        fmt_id = f"FMT{counter:03d}"
        counter += 1
        
        # Store original tag info
        mapping[fmt_id] = {
            'type': 'paired',
            'opening': f'<{opening_tag}>',
            'closing': f'</{closing_tag}>',
            'original_text': text_inside
        }
        
        # Return placeholder with Unicode brackets 【】
        return f'【{fmt_id}】{text_inside}【/{fmt_id}】'
    
    # Replace all paired tags first
    result = re.sub(paired_pattern, replace_paired_match, result)
    
    # PASS 2: Match remaining CLOSING tags (individual, unpaired)
    # These appear at span transitions like: "text</TAG1><TAG2>text"
    closing_pattern = r'</(\d+(?:\|\d+)?)>'
    
    def replace_closing_match(match):
        nonlocal counter
        closing_tag = match.group(1)
        
        fmt_id = f"FMTC{counter:03d}"  # C = Close
        counter += 1
        
        mapping[fmt_id] = {
            'type': 'closing',
            'tag': f'</{closing_tag}>'
        }
        
        return f'【{fmt_id}】'
    
    result = re.sub(closing_pattern, replace_closing_match, result)
    
    # PASS 3: Match remaining OPENING tags (individual, unpaired)
    opening_pattern = r'<(\d+(?:\|\d+)?:[^>]+)>'
    
    def replace_opening_match(match):
        nonlocal counter
        opening_tag = match.group(1)
        
        fmt_id = f"FMTO{counter:03d}"  # O = Open
        counter += 1
        
        mapping[fmt_id] = {
            'type': 'opening',
            'tag': f'<{opening_tag}>'
        }
        
        return f'【{fmt_id}】'
    
    result = re.sub(opening_pattern, replace_opening_match, result)
    
    return result, mapping


def restore_tags_from_placeholders(translated_text: str, mapping: Dict[str, Dict[str, str]]) -> str:
    """
    Restore original format tags from placeholders after translation.
    
    Session 76 UPDATE: Now handles 3 placeholder types:
    - Paired: 【FMT001】text【/FMT001】 (normal formatted text)
    - Closing: 【FMTC001】 (unpaired closing tag)
    - Opening: 【FMTO001】 (unpaired opening tag)
    
    Handles severely corrupted placeholders where Google Translate:
    - Added spaces: 【FMT001】 → 【F MT001】
    - Deleted brackets: 【/FMT001】 → 【/FMT001 (missing closing 】)
    
    Example:
        Input:  "【FMT001】RISKS【/FMT001】" or "Header【FMTC001】【FMTO002】Body"
        Output: "<113|65536:Arial|0,0>RISKS</113|65536>" or "Header</113|65536><112|65536>Body"
    
    Args:
        translated_text: Text with 【FMTXXX】 placeholders
        mapping: Dict mapping IDs to original tag info
        
    Returns:
        Text with restored tags
        
    Author: COM8 (Sessions 75, 76)
    """
    result = translated_text
    
    # PASS 1: Restore PAIRED tags (【FMT001】...【/FMT001】)
    # ULTRA-PERMISSIVE: Allows spaces ANYWHERE, handles ASCII brackets too
    # Matches: 【FMT001】, 【F MT007】, [FMT013], [ F M T 0 1 3 ]
    pattern1_unicode = r'【\s*F\s*M\s*T\s*(\d+)\s*】(.*?)【\s*/\s*F\s*M\s*T\s*\1\s*】'
    pattern1_ascii = r'\[\s*F\s*M\s*T\s*(\d+)\s*\](.*?)\[\s*/\s*F\s*M\s*T\s*\1\s*\]'
    
    def restore_paired(match):
        num = match.group(1).replace(' ', '')
        translated_text_inside = match.group(2)
        fmt_id = f"FMT{num}"
        
        if fmt_id not in mapping:
            return match.group(0)
        
        tag_info = mapping[fmt_id]
        if tag_info.get('type') == 'paired':
            return f'{tag_info["opening"]}{translated_text_inside}{tag_info["closing"]}'
        else:
            return match.group(0)
    
    result = re.sub(pattern1_unicode, restore_paired, result, flags=re.DOTALL)
    result = re.sub(pattern1_ascii, restore_paired, result, flags=re.DOTALL)
    
    # PASS 2: Severely corrupted pairs (closing bracket deleted by Google)
    # ULTRA-PERMISSIVE: Spaces anywhere + ASCII brackets
    pattern2_unicode = r'【\s*F\s*M\s*T\s*(\d+)\s*】(.*?)【\s*/\s*F\s*M\s*T\s*\1\s+'
    pattern2_ascii = r'\[\s*F\s*M\s*T\s*(\d+)\s*\](.*?)\[\s*/\s*F\s*M\s*T\s*\1\s+'
    
    def restore_paired_broken(match):
        num = match.group(1).replace(' ', '')
        translated_text_inside = match.group(2)
        fmt_id = f"FMT{num}"
        
        if fmt_id not in mapping:
            return match.group(0)
        
        tag_info = mapping[fmt_id]
        if tag_info.get('type') == 'paired':
            return f'{tag_info["opening"]}{translated_text_inside}{tag_info["closing"]}'
        else:
            return match.group(0)
    
    result = re.sub(pattern2_unicode, restore_paired_broken, result, flags=re.DOTALL)
    result = re.sub(pattern2_ascii, restore_paired_broken, result, flags=re.DOTALL)
    
    # PASS 3: Restore CLOSING tags (【FMTC001】)
    # ULTRA-PERMISSIVE: Handles spaces anywhere + ASCII brackets
    pattern_closing_unicode = r'【\s*F\s*M\s*T\s*C\s*(\d+)\s*[】\s]*'
    pattern_closing_ascii = r'\[\s*F\s*M\s*T\s*C\s*(\d+)\s*[\]\s]*'
    
    def restore_closing(match):
        num = match.group(1).replace(' ', '')
        fmt_id = f"FMTC{num}"
        
        if fmt_id in mapping and mapping[fmt_id].get('type') == 'closing':
            return mapping[fmt_id]['tag']
        else:
            return ''
    
    result = re.sub(pattern_closing_unicode, restore_closing, result)
    result = re.sub(pattern_closing_ascii, restore_closing, result)
    
    # PASS 4: Restore OPENING tags (【FMTO001】)
    # ULTRA-PERMISSIVE: Handles spaces anywhere + ASCII brackets
    pattern_opening_unicode = r'【\s*F\s*M\s*T\s*O\s*(\d+)\s*[】\s]*'
    pattern_opening_ascii = r'\[\s*F\s*M\s*T\s*O\s*(\d+)\s*[\]\s]*'
    
    def restore_opening(match):
        num = match.group(1).replace(' ', '')
        fmt_id = f"FMTO{num}"
        
        if fmt_id in mapping and mapping[fmt_id].get('type') == 'opening':
            return mapping[fmt_id]['tag']
        else:
            return ''
    
    result = re.sub(pattern_opening_unicode, restore_opening, result)
    result = re.sub(pattern_opening_ascii, restore_opening, result)
    
    # PASS 5: Cleanup orphaned paired opening tags (【FMT001】 with no closing)
    # ULTRA-PERMISSIVE: Spaces anywhere + ASCII brackets
    pattern3_unicode = r'【\s*F\s*M\s*T\s*(\d+)\s*】'
    pattern3_ascii = r'\[\s*F\s*M\s*T\s*(\d+)\s*\]'
    
    def restore_orphan_opening(match):
        num = match.group(1).replace(' ', '')
        fmt_id = f"FMT{num}"
        
        if fmt_id in mapping and mapping[fmt_id].get('type') == 'paired':
            # Return just the opening tag (closing was lost)
            return mapping[fmt_id]['opening']
        else:
            # Unknown ID or already processed - remove placeholder
            return ''
    
    result = re.sub(pattern3_unicode, restore_orphan_opening, result)
    result = re.sub(pattern3_ascii, restore_orphan_opening, result)
    
    # PASS 6: Cleanup orphaned paired closing tags (【/FMT001】)
    # ULTRA-PERMISSIVE: Spaces anywhere + ASCII brackets
    pattern4_unicode = r'【\s*/\s*F\s*M\s*T\s*(\d+)\s*[】\s]*'
    pattern4_ascii = r'\[\s*/\s*F\s*M\s*T\s*(\d+)\s*[\]\s]*'
    
    def restore_orphan_closing(match):
        num = match.group(1).replace(' ', '')
        fmt_id = f"FMT{num}"
        
        if fmt_id in mapping and mapping[fmt_id].get('type') == 'paired':
            return mapping[fmt_id]['closing']
        else:
            return ''
    
    result = re.sub(pattern4_unicode, restore_orphan_closing, result)
    result = re.sub(pattern4_ascii, restore_orphan_closing, result)
    
    return result


def protect_special_whitespace(text: str) -> str:
    """
    Protect special whitespace characters from Google Translate conversion.
    
    Google Translate often normalizes whitespace:
    - Tabs (\t) → regular spaces
    - Multiple spaces → single space
    - Line breaks may be removed
    - Non-breaking spaces may be converted
    
    This function replaces them with Unicode placeholders that Google preserves.
    
    Args:
        text: Text with special whitespace characters
        
    Returns:
        Text with whitespace protected by placeholders
        
    Example:
        Input:  "text\t\ttab  spaces\nline"
        Output: "text【TAB】【TAB】tab【SP2】spaces【BR】line"
        
    Author: COM8 (Session 75)
    """
    # Order matters! Process specific patterns before generic ones
    
    # Non-breaking space (U+00A0)
    text = text.replace('\xa0', '【NBSP】')
    
    # Tabs
    text = text.replace('\t', '【TAB】')
    
    # Line breaks (single \n)
    # Note: \n\n will become 【BR】【BR】 which is fine for paragraph breaks
    text = text.replace('\n', '【BR】')
    
    # Multiple consecutive spaces (2 or more)
    # Pattern: "  " → 【SP2】, "   " → 【SP3】, etc.
    def replace_spaces(match):
        count = len(match.group(0))
        return f'【SP{count}】'
    
    text = re.sub(r' {2,}', replace_spaces, text)
    
    return text


def restore_special_whitespace(text: str) -> str:
    """
    Restore special whitespace from placeholders after translation.
    
    Reverses the protection applied by protect_special_whitespace().
    Handles corrupted placeholders where Google Translate added spaces.
    
    Args:
        text: Text with whitespace placeholders
        
    Returns:
        Text with restored whitespace characters
        
    Example:
        Input:  "text【TAB】【TA B】tab【SP2】spaces【BR】line"
        Output: "text\t\ttab  spaces\nline"
        
    Note: Google Translate sometimes adds spaces inside placeholders:
        【TAB】 → 【TA B】, 【BR】 → 【B R】, etc.
        We use regex to handle both exact and corrupted patterns.
        
    Author: COM8 (Session 75, fixed after user caught incomplete testing)
    """
    # Restore in reverse order of protection
    # Use VERY permissive regex to handle Google's creative corruption:
    # - Spaces between letters: 【TA B】
    # - Spaces before/after: 【 TAB】, 【TAB 】
    # - Multiple spaces: 【T  A  B】
    # Strategy: Match the bracket, then any mix of target letters and spaces, then bracket
    
    # Multiple spaces: 【SP2】 or 【S P2】 or 【 SP2】 or 【SP 2】 → "  ", etc.
    def restore_spaces(match):
        count = int(match.group(1))
        return ' ' * count
    
    # Match 【, then S/P/digits with any spaces, then 】
    text = re.sub(r'【[S\s]*P[\ s]*(\d+)[\s]*】', restore_spaces, text)
    
    # Character replacements - match letters in order with any whitespace between/around
    # TAB: Match 【, then T/A/B in order with any spaces, then 】
    text = re.sub(r'【[\s]*T[\s]*A[\s]*B[\s]*】', '\t', text)
    # BR: Match 【, then B/R in order with any spaces, then 】
    text = re.sub(r'【[\s]*B[\s]*R[\s]*】', '\n', text)
    # NBSP: Match 【, then N/B/S/P in order with any spaces, then 】
    text = re.sub(r'【[\s]*N[\s]*B[\s]*S[\s]*P[\s]*】', '\xa0', text)
    
    return text


# ============================================================================
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
    KEEP_WITH_NEXT = 1 << 18  # 2^18 = 262144
    PAGE_BREAK_BEFORE = 1 << 19  # 2^19 = 524288
    WIDOW_ORPHAN_CONTROL = 1 << 20  # 2^20 = 1048576
    BIDI_TEXT = 1 << 21  # 2^21 = 2097152
    LIST_ITEM = 1 << 22  # 2^22 = 4194304
    HYPERLINK = 1 << 23  # 2^23 = 8388608  # Session 44


@dataclass
class TextSegment:
    """A segment of text with its formatting."""
    text: str
    format_bits: int = 0  # Bitwise combination of FormatBit values
    metadata: Optional[str] = None  # Additional format data (colors, sizes, etc.)
    paragraph_format: int = 0  # Paragraph-level formatting bits
    paragraph_metadata: Optional[str] = None  # Paragraph metadata (alignment, spacing)
    hyperlink_url: Optional[str] = None  # URL for hyperlinks (Session 44)
    
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
        # Special handling for hyperlinks (Session 44)
        if self.hyperlink_url:
            # Use clean LINK tag format: <LINK:url>display_text</LINK>
            # URL encoding to handle special characters
            url_encoded = self.hyperlink_url.replace('<', '&lt;').replace('>', '&gt;')
            return f"<LINK:{url_encoded}>{self.text}</LINK>"
        
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


@dataclass
class CellData:
    """Data for a single table cell (Session 56)."""
    text_segments: List[TextSegment]  # Text content with formatting
    row_span: int = 1  # Number of rows this cell spans
    col_span: int = 1  # Number of columns this cell spans
    vertical_alignment: Optional[str] = None  # top, center, bottom
    background_color: Optional[str] = None  # RGB hex color (Session 61)
    borders: Optional[Dict[str, Dict[str, str]]] = None  # Border styles per side (Session 62)
    # borders format: {'top': {'style': 'single', 'width': '8', 'color': 'FF0000'}, ...}
    
    def __init__(self):
        """Initialize empty cell."""
        self.text_segments = []
        self.row_span = 1
        self.col_span = 1
        self.vertical_alignment = None
        self.background_color = None
        self.borders = None


@dataclass
class TableSegment:
    """A table structure with rows and cells (Session 56)."""
    rows: List[List[CellData]]  # 2D array of cells [row][col]
    num_rows: int
    num_cols: int
    table_style: Optional[str] = None  # Table style name
    table_width: Optional[str] = None  # Table width (pt or %)
    column_widths: Optional[List[str]] = None  # Width of each column
    
    def __init__(self, num_rows: int, num_cols: int):
        """Initialize table with given dimensions."""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.rows = [[CellData() for _ in range(num_cols)] for _ in range(num_rows)]
        self.table_style = None
        self.table_width = None
        self.column_widths = None
    
    def get_cell(self, row: int, col: int) -> CellData:
        """Get cell at specific position."""
        return self.rows[row][col]
    
    def set_cell(self, row: int, col: int, cell: CellData):
        """Set cell at specific position."""
        self.rows[row][col] = cell
    
    def to_placeholder(self, table_index: int) -> str:
        """Convert table to placeholder for main text."""
        return f"{{TABLE_{table_index}}}"
    
    def to_tagged_text(self) -> str:
        """
        Convert table to tagged text representation (Session 66 fix).
        
        For translation purposes, we represent the table as a placeholder
        to avoid breaking table structure during translation.
        """
        # Use a generic placeholder that won't be translated
        return "[TABLE]"


class FormatMapper:
    """
    Extract formatting from documents and convert to tagged text.
    
    Currently supports DOCX format detection.
    ODT support to be added later.
    """
    
    @staticmethod
    def _extract_run_formatting(run) -> Tuple[int, List[str]]:
        """
        Extract formatting from a single DOCX run (Session 57).
        
        Args:
            run: A python-docx Run object
            
        Returns:
            Tuple of (format_bits, metadata_list)
        """
        format_bits = 0
        metadata_parts = []
        
        # Detect bold
        if run.bold:
            format_bits |= FormatBit.BOLD
        
        # Detect italic
        if run.italic:
            format_bits |= FormatBit.ITALIC
        
        # Detect underline
        if run.underline:
            format_bits |= FormatBit.UNDERLINE
        
        # Detect double underline
        if run.underline == 3:  # DOUBLE
            format_bits |= FormatBit.DOUBLE_UNDERLINE
        
        # Detect strikethrough
        if run.font.strike:
            format_bits |= FormatBit.STRIKETHROUGH
        
        # Detect font color
        if run.font.color.rgb:
            format_bits |= FormatBit.FONT_COLOR
            rgb = run.font.color.rgb
            hex_color = f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
            metadata_parts.append(hex_color)
        
        # Detect highlight/background color
        if run.font.highlight_color:
            format_bits |= FormatBit.HIGHLIGHT
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
        
        # Detect superscript
        if run.font.superscript:
            format_bits |= FormatBit.SUPERSCRIPT
        
        # Detect subscript
        if run.font.subscript:
            format_bits |= FormatBit.SUBSCRIPT
        
        # Detect small caps
        if run.font.small_caps:
            format_bits |= FormatBit.SMALL_CAPS
        
        # Detect font size
        if run.font.size:
            format_bits |= FormatBit.FONT_SIZE
            points = run.font.size.pt
            metadata_parts.append(str(int(points)))
        
        # Detect font family
        if run.font.name:
            format_bits |= FormatBit.FONT_FAMILY
            metadata_parts.append(run.font.name)
        
        return format_bits, metadata_parts
    
    @staticmethod
    def _extract_span_formatting_odt(text_prop, styles) -> Tuple[int, List[str]]:
        """
        Extract formatting from ODT TextProperties element (Session 58).
        
        Args:
            text_prop: ODF TextProperties element
            styles: Style dictionary for lookups
            
        Returns:
            Tuple of (format_bits, metadata_list)
        """
        from odf import style as odf_style
        
        format_bits = 0
        metadata_parts = []
        
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
            format_bits |= FormatBit.BOLD
        
        # Italic
        font_style = get_attr('font-style')
        if font_style == 'italic':
            format_bits |= FormatBit.ITALIC
        
        # Underline
        text_underline_style = get_attr('text-underline-style')
        if text_underline_style and text_underline_style != 'none':
            format_bits |= FormatBit.UNDERLINE
        
        # Double underline
        text_underline_type = get_attr('text-underline-type')
        if text_underline_type == 'double':
            format_bits |= FormatBit.DOUBLE_UNDERLINE
        
        # Strikethrough
        text_line_through = get_attr('text-line-through-style')
        if text_line_through and text_line_through != 'none':
            format_bits |= FormatBit.STRIKETHROUGH
        
        # Superscript
        text_position = get_attr('text-position')
        if text_position and 'super' in str(text_position).lower():
            format_bits |= FormatBit.SUPERSCRIPT
        
        # Subscript
        if text_position and 'sub' in str(text_position).lower() and 'super' not in str(text_position).lower():
            format_bits |= FormatBit.SUBSCRIPT
        
        # Small caps
        font_variant = get_attr('font-variant')
        if font_variant == 'small-caps':
            format_bits |= FormatBit.SMALL_CAPS
        
        # Font color
        color = get_attr('color')
        if color:
            format_bits |= FormatBit.FONT_COLOR
            hex_color = str(color).replace('#', '')
            metadata_parts.append(hex_color)
        
        # Highlight/Background color
        bg_color = get_attr('background-color')
        if not bg_color:
            bg_color = get_attr('text-background-color')
        if bg_color and bg_color != 'transparent':
            format_bits |= FormatBit.HIGHLIGHT
            hex_bg = str(bg_color).replace('#', '')
            metadata_parts.append(hex_bg)
        
        # Font size
        font_size = get_attr('font-size')
        if font_size:
            format_bits |= FormatBit.FONT_SIZE
            size_value = str(font_size).replace('pt', '')
            metadata_parts.append(size_value)
        
        # Font family
        font_family = get_attr('font-name')
        if font_family:
            format_bits |= FormatBit.FONT_FAMILY
            family_name = str(font_family).strip("'\"")
            metadata_parts.append(family_name)
        
        return format_bits, metadata_parts
    
    @staticmethod
    def _extract_table_from_docx(docx_table) -> TableSegment:
        """
        Extract a single table from DOCX format (Session 56).
        
        Args:
            docx_table: A python-docx Table object
            
        Returns:
            TableSegment with all cells and formatting
        """
        # Get table dimensions
        num_rows = len(docx_table.rows)
        num_cols = len(docx_table.columns) if docx_table.rows else 0
        
        table = TableSegment(num_rows, num_cols)
        
        # Extract each cell
        for row_idx, row in enumerate(docx_table.rows):
            for col_idx, cell in enumerate(row.cells):
                cell_data = CellData()
                
                # Extract text from cell paragraphs with formatting (Session 57)
                for para in cell.paragraphs:
                    # Process each run in the paragraph
                    for run in para.runs:
                        if not run.text:
                            continue
                        
                        # Extract run formatting using helper method
                        format_bits, metadata_parts = FormatMapper._extract_run_formatting(run)
                        
                        # Create text segment with formatting
                        segment = TextSegment(
                            text=run.text,
                            format_bits=format_bits,
                            metadata=",".join(metadata_parts) if metadata_parts else None
                        )
                        cell_data.text_segments.append(segment)
                    
                    # Add paragraph break after each paragraph (except last)
                    if para.text.strip():
                        cell_data.text_segments.append(TextSegment(text="\n"))
                
                # Extract cell-level formatting (Sessions 61-62)
                from docx.oxml.ns import qn
                tc = cell._element
                tcPr = tc.tcPr
                if tcPr is not None:
                    # Get cell shading (background color) - Session 61
                    shd = tcPr.find(qn('w:shd'))
                    if shd is not None:
                        fill = shd.get(qn('w:fill'))
                        if fill and fill != 'auto':
                            cell_data.background_color = fill
                    
                    # Get cell borders - Session 62
                    tcBorders = tcPr.find(qn('w:tcBorders'))
                    if tcBorders is not None:
                        borders = {}
                        for side in ['top', 'bottom', 'left', 'right']:
                            border_elem = tcBorders.find(qn(f'w:{side}'))
                            if border_elem is not None:
                                style = border_elem.get(qn('w:val'))
                                width = border_elem.get(qn('w:sz'))
                                color = border_elem.get(qn('w:color'))
                                if style:  # Only store if border exists
                                    borders[side] = {
                                        'style': style,
                                        'width': width or '8',  # Default 1pt
                                        'color': color or '000000'  # Default black
                                    }
                        if borders:
                            cell_data.borders = borders
                    
                    # Get cell merging - Session 63
                    # Horizontal merge (colspan)
                    hMerge = tcPr.find(qn('w:hMerge'))
                    if hMerge is not None:
                        val = hMerge.get(qn('w:val'))
                        if val == 'restart':
                            # This is the start of a horizontal merge
                            # Count continuation cells to determine colspan
                            colspan = 1
                            for next_col_idx in range(col_idx + 1, num_cols):
                                next_cell = docx_table.rows[row_idx].cells[next_col_idx]
                                next_tcPr = next_cell._element.tcPr
                                if next_tcPr is not None:
                                    next_hMerge = next_tcPr.find(qn('w:hMerge'))
                                    if next_hMerge is not None and next_hMerge.get(qn('w:val')) == 'continue':
                                        colspan += 1
                                    else:
                                        break
                                else:
                                    break
                            cell_data.col_span = colspan
                    
                    # Vertical merge (rowspan)
                    vMerge = tcPr.find(qn('w:vMerge'))
                    if vMerge is not None:
                        val = vMerge.get(qn('w:val'))
                        # 'restart' or no val attribute could mean start
                        # Check if this is truly a restart by seeing if it has val='restart'
                        if val == 'restart' or val is None:
                            # Could be start of merge - need to verify by checking for continuations
                            # Count continuation cells to determine rowspan
                            rowspan = 1
                            for next_row_idx in range(row_idx + 1, num_rows):
                                next_cell = docx_table.rows[next_row_idx].cells[col_idx]
                                next_tcPr = next_cell._element.tcPr
                                if next_tcPr is not None:
                                    next_vMerge = next_tcPr.find(qn('w:vMerge'))
                                    if next_vMerge is not None:
                                        # Any vMerge in next row means continuation
                                        rowspan += 1
                                    else:
                                        break
                                else:
                                    break
                            
                            # Only set if we actually found continuations
                            if rowspan > 1:
                                cell_data.row_span = rowspan
                
                
                # Store cell
                table.set_cell(row_idx, col_idx, cell_data)
        
        return table
    
    @staticmethod
    def _extract_table_from_odt(odt_table, styles) -> TableSegment:
        """
        Extract a single table from ODT format (Session 58).
        
        Args:
            odt_table: An ODF Table element
            styles: Style dictionary for lookups
            
        Returns:
            TableSegment with all cells and formatting
        """
        from odf import text as odf_text, table as odf_table, style as odf_style
        from odf.element import Text as ODFText
        
        # Get table dimensions
        rows = odt_table.getElementsByType(odf_table.TableRow)
        num_rows = len(rows)
        num_cols = 0
        
        # Determine max columns by checking first row
        if num_rows > 0:
            cells = rows[0].getElementsByType(odf_table.TableCell)
            num_cols = len(cells)
        
        table = TableSegment(num_rows, num_cols)
        
        # Extract each cell
        for row_idx, row in enumerate(rows):
            cells = row.getElementsByType(odf_table.TableCell)
            
            for col_idx, cell in enumerate(cells):
                if col_idx >= num_cols:
                    break  # Skip extra cells if row has more than expected
                
                cell_data = CellData()
                
                # Extract text from cell paragraphs with formatting (Session 58)
                paras = cell.getElementsByType(odf_text.P)
                
                for para in paras:
                    # Recursively extract text with span formatting
                    def extract_spans(element, current_style_name=None):
                        """Recursively extract text from spans."""
                        results = []  # List of (text, style_name) tuples
                        
                        # Check if this is a Span with a style
                        if hasattr(element, 'qname') and element.qname[1] == 'span':
                            try:
                                span_style_name = element.getAttribute('stylename')
                                current_style_name = span_style_name if span_style_name else current_style_name
                            except (ValueError, KeyError):
                                pass
                        
                        # Process child nodes
                        for child in element.childNodes:
                            if isinstance(child, ODFText):
                                # Actual text content
                                text_content = str(child)
                                if text_content:
                                    results.append((text_content, current_style_name))
                            elif hasattr(child, 'childNodes'):
                                # Recursively process containers
                                results.extend(extract_spans(child, current_style_name))
                        
                        return results
                    
                    # Extract all text spans with their styles
                    span_data = extract_spans(para)
                    
                    # Convert spans to TextSegments
                    for text_content, style_name in span_data:
                        format_bits = 0
                        metadata_parts = []
                        
                        # Apply formatting from style
                        if style_name and style_name in styles:
                            text_style = styles[style_name]
                            
                            for text_prop in text_style.getElementsByType(odf_style.TextProperties):
                                format_bits, metadata_parts = FormatMapper._extract_span_formatting_odt(
                                    text_prop, styles
                                )
                        
                        # Create segment
                        segment = TextSegment(
                            text=text_content,
                            format_bits=format_bits,
                            metadata=",".join(metadata_parts) if metadata_parts else None
                        )
                        cell_data.text_segments.append(segment)
                    
                    # Add paragraph break after each paragraph
                    if span_data:
                        cell_data.text_segments.append(TextSegment(text="\n"))
                
                # Extract cell-level formatting (Sessions 61-62)
                try:
                    cell_style_name = cell.getAttribute('stylename')
                    if cell_style_name and cell_style_name in styles:
                        cell_style = styles[cell_style_name]
                        cell_props = cell_style.getElementsByType(odf_style.TableCellProperties)
                        
                        if cell_props:
                            props = cell_props[0]
                            if hasattr(props, 'attributes'):
                                borders = {}
                                for (ns, name), value in props.attributes.items():
                                    # Background color - Session 61
                                    if name == 'background-color':
                                        if value and value != 'transparent':
                                            cell_data.background_color = value.replace('#', '')
                                    
                                    # Borders - Session 62
                                    # ODT format: "0.05cm solid #FF0000"
                                    elif name.startswith('border-'):
                                        side = name.replace('border-', '')  # top, bottom, left, right
                                        if value and value != 'none':
                                            # Parse: "width style color"
                                            parts = value.split()
                                            if len(parts) >= 3:
                                                width, style, color = parts[0], parts[1], parts[2]
                                                # Convert ODT to internal format
                                                borders[side] = {
                                                    'style': style,
                                                    'width': width,
                                                    'color': color.replace('#', '')
                                                }
                                if borders:
                                    cell_data.borders = borders
                except (ValueError, KeyError):
                    pass  # No cell style
                
                # Extract cell merging - Session 63
                # Horizontal merge (colspan)
                colspan = cell.getAttribute('numbercolumnsspanned')
                if colspan:
                    try:
                        cell_data.col_span = int(colspan)
                    except (ValueError, TypeError):
                        pass
                
                # Vertical merge (rowspan)
                rowspan = cell.getAttribute('numberrowsspanned')
                if rowspan:
                    try:
                        cell_data.row_span = int(rowspan)
                    except (ValueError, TypeError):
                        pass
                
                # Store cell
                table.set_cell(row_idx, col_idx, cell_data)
        
        return table
    
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
        tables: List[TableSegment] = []  # Session 56: Store extracted tables
        
        # Session 56: Extract all tables first
        for table_idx, docx_table in enumerate(doc.tables):
            table_segment = FormatMapper._extract_table_from_docx(docx_table)
            tables.append(table_segment)
        
        # Track table index as we encounter them in document order
        table_counter = 0
        
        for paragraph in doc.paragraphs:
            # Detect paragraph-level formatting
            para_metadata_parts = []
            para_format_bits = 0
            
            # Detect list items (Session 39)
            # DOCX stores list info in paragraph._element
            try:
                # Check if paragraph is part of a list
                pPr = paragraph._element.pPr
                if pPr is not None:
                    numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                    if numPr is not None:
                        para_format_bits |= FormatBit.LIST_ITEM
                        # Get list level (ilvl element)
                        ilvl = numPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl')
                        level = int(ilvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '0')) + 1 if ilvl is not None else 1
                        
                        # Determine list type from style name or default to bullet
                        # DOCX uses style names like "List Bullet", "List Number"
                        list_type = 'B'  # Default to bullet
                        if 'number' in paragraph.style.name.lower():
                            list_type = 'N'
                        
                        para_metadata_parts.append(f"{list_type},{level}")
            except (AttributeError, ValueError, TypeError) as e:
                logger.debug(f"Paragraph is not a list item: {e}")
                pass  # Not a list item
            
            # Detect heading level (Session 33)
            # DOCX uses style names like "Heading 1", "Heading 2", etc.
            if paragraph.style.name.startswith('Heading'):
                para_format_bits |= FormatBit.HEADING
                # Extract level number from style name (e.g., "Heading 1" → "1")
                try:
                    level = paragraph.style.name.split()[-1]
                    if level.isdigit() and 1 <= int(level) <= 6:
                        para_metadata_parts.append(f"H{level}")
                    else:
                        para_metadata_parts.append("H1")  # Default
                except (AttributeError, IndexError, ValueError):
                    para_metadata_parts.append("H1")  # Default if parsing fails
            
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
            
            # Detect keep with next (Session 28)
            if pf.keep_with_next:
                para_format_bits |= FormatBit.KEEP_WITH_NEXT
                # Boolean flag, no metadata needed
            
            # Detect page break before (Session 29)
            if pf.page_break_before:
                para_format_bits |= FormatBit.PAGE_BREAK_BEFORE
                # Boolean flag, no metadata needed
            
            # Detect widow/orphan control (Session 30)
            if pf.widow_control:
                para_format_bits |= FormatBit.WIDOW_ORPHAN_CONTROL
                # Boolean flag, no metadata needed
            
            # Detect bidirectional text (Session 31)
            try:
                if paragraph.paragraph_format.bidi:
                    para_format_bits |= FormatBit.BIDI_TEXT
                    # Store direction as metadata: R=RTL, L=LTR
                    # DOCX bidi=True means RTL context
                    para_metadata_parts.append('R')
            except AttributeError:
                pass  # bidi attribute not available in this python-docx version
            
            # Detect hyperlinks (Session 44)
            # Process all elements in paragraph, including hyperlinks
            # paragraph.runs doesn't include runs inside hyperlinks, so we need to process _element directly
            from docx.oxml.ns import qn
            from docx.text.run import Run
            
            # Collect all runs (including those inside hyperlinks)
            all_runs = []  # List of (run_object, hyperlink_url or None)
            
            for element in paragraph._element:
                if 'hyperlink' in element.tag:
                    # Extract URL
                    rel_id = element.get(qn('r:id'))
                    url = None
                    if rel_id and rel_id in doc.part.rels:
                        url = doc.part.rels[rel_id].target_ref
                    
                    # Get runs inside hyperlink
                    for run_elem in element:
                        if 'r' in run_elem.tag:
                            try:
                                run_obj = Run(run_elem, paragraph)
                                all_runs.append((run_obj, url))
                            except (AttributeError, ValueError, TypeError) as e:
                                logger.debug(f"Skipping invalid run in hyperlink: {e}")
                                pass  # Skip invalid runs
                elif 'r' in element.tag:
                    # Regular run (not in hyperlink)
                    try:
                        run_obj = Run(element, paragraph)
                        all_runs.append((run_obj, None))
                    except (AttributeError, ValueError, TypeError) as e:
                        logger.debug(f"Skipping invalid run: {e}")
                        pass  # Skip invalid runs
            
            # Process each run (both regular and hyperlink runs)
            for run, hyperlink_url in all_runs:
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
                
                # Store hyperlink URL if this run is part of a hyperlink (Session 44)
                if hyperlink_url:
                    segment.hyperlink_url = hyperlink_url
                
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
        from odf import opendocument, text as odf_text, style as odf_style, table as odf_table
        from odf.element import Text as ODFText
        
        doc = opendocument.load(file_path)
        segments: List[TextSegment] = []
        tables: List[TableSegment] = []  # Session 58: Store extracted tables
        
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
        
        # Session 58: Extract all tables first
        for table_idx, odt_table in enumerate(doc.getElementsByType(odf_table.Table)):
            table_segment = FormatMapper._extract_table_from_odt(odt_table, styles)
            tables.append(table_segment)
        
        # Process all paragraphs
        for para in doc.getElementsByType(odf_text.P):
            try:
                para_style_name = para.getAttribute('stylename')
            except (ValueError, KeyError):
                para_style_name = None
            para_style = styles.get(para_style_name) if para_style_name else None
            
            # Initialize paragraph formatting
            para_format_bits = 0
            para_metadata_parts = []
            
            # Detect list items (Session 39)
            # ODT wraps list items in text:list elements
            # Check if this paragraph's parent is a list
            if hasattr(para, 'parentNode') and para.parentNode is not None:
                parent = para.parentNode
                if hasattr(parent, 'qname') and parent.qname[1] == 'list-item':
                    para_format_bits |= FormatBit.LIST_ITEM
                    # Default to bullet list, level 1
                    # TODO: Detect list type and level from list style
                    para_metadata_parts.append("B,1")
            
            # Detect heading level (Session 33)
            # ODT uses outline-level attribute or style names like "Heading_20_1"
            if para_style_name:
                if 'heading' in para_style_name.lower() or 'head' in para_style_name.lower():
                    para_format_bits |= FormatBit.HEADING
                    # Try to extract level from style name (e.g., "Heading_20_1" → "1")
                    try:
                        match = re.search(r'[_\s](\d)(?:[_\s]|$)', para_style_name)
                        if match:
                            level = match.group(1)
                            if 1 <= int(level) <= 6:
                                para_metadata_parts.append(f"H{level}")
                            else:
                                para_metadata_parts.append("H1")  # Default
                        else:
                            para_metadata_parts.append("H1")  # Default
                    except (AttributeError, IndexError, ValueError):
                        para_metadata_parts.append("H1")  # Default if parsing fails
            
            # Extract paragraph-level formatting
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
                    
                    try:
                        # Keep with next (Session 28)
                        # ODT attribute: fo:keep-with-next = "always"
                        keep_with_next = prop.getAttribute('keepwithnext')
                        if keep_with_next and str(keep_with_next).lower() == 'always':
                            para_format_bits |= FormatBit.KEEP_WITH_NEXT
                    except (ValueError, KeyError):
                        pass
                    
                    try:
                        # Page break before (Session 29)
                        # ODT attribute: fo:break-before = "page"
                        break_before = prop.getAttribute('breakbefore')
                        if break_before and str(break_before).lower() == 'page':
                            para_format_bits |= FormatBit.PAGE_BREAK_BEFORE
                    except (ValueError, KeyError):
                        pass
                    
                    try:
                        # Widow/orphan control (Session 30)
                        # ODT attributes: fo:widows and fo:orphans (numeric values)
                        # If either is set to 2 or more, enable control
                        widows = prop.getAttribute('widows')
                        orphans = prop.getAttribute('orphans')
                        if (widows and int(str(widows)) >= 2) or (orphans and int(str(orphans)) >= 2):
                            para_format_bits |= FormatBit.WIDOW_ORPHAN_CONTROL
                    except (ValueError, KeyError, TypeError):
                        pass
                    
                    try:
                        # Bidirectional text (Session 31)
                        # ODT attribute: style:writing-mode
                        # Values: "lr-tb" (LTR), "rl-tb" (RTL), etc.
                        writing_mode = prop.getAttribute('writingmode')
                        if writing_mode:
                            mode_str = str(writing_mode).lower()
                            if 'rl' in mode_str:
                                para_format_bits |= FormatBit.BIDI_TEXT
                                para_metadata_parts.append('R')  # RTL
                            elif 'lr' in mode_str and para_format_bits & FormatBit.BIDI_TEXT == 0:
                                # Explicitly LTR (only if not already RTL)
                                para_format_bits |= FormatBit.BIDI_TEXT
                                para_metadata_parts.append('L')  # LTR
                    except (ValueError, KeyError):
                        pass
            
            # Process text content (spans and direct text)
            para_text_nodes = []
            
            def extract_text_recursive(element, current_style_name=None, hyperlink_url=None):
                """Recursively extract text with formatting from element tree."""
                # Check if this is a hyperlink (Session 44)
                # ODT hyperlinks use text:a element with xlink:href attribute
                if hasattr(element, 'qname') and element.qname == ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'a'):
                    try:
                        href = element.getAttribute('href')
                        hyperlink_url = href if href else hyperlink_url
                    except (ValueError, KeyError):
                        pass
                
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
                            para_text_nodes.append((text_content, current_style_name, hyperlink_url))
                    # Session 75 Fix: Handle special formatting elements
                    elif hasattr(child, 'qname'):
                        qname = child.qname[1] if isinstance(child.qname, tuple) else str(child.qname)
                        
                        # Tab character
                        if qname == 'tab':
                            para_text_nodes.append(('\t', current_style_name, hyperlink_url))
                        
                        # Line break (soft return within paragraph)
                        elif qname == 'line-break':
                            para_text_nodes.append(('\n', current_style_name, hyperlink_url))
                        
                        # Multiple spaces (text:s with count attribute)
                        elif qname == 's':
                            try:
                                # Get space count from text:c attribute
                                space_count = child.getAttribute('c')
                                count = int(space_count) if space_count else 1
                                para_text_nodes.append((' ' * count, current_style_name, hyperlink_url))
                            except (ValueError, KeyError):
                                # Default to single space if attribute missing
                                para_text_nodes.append((' ', current_style_name, hyperlink_url))
                        
                        # Recursively process other container elements
                        elif hasattr(child, 'childNodes'):
                            extract_text_recursive(child, current_style_name, hyperlink_url)
                    
                    elif hasattr(child, 'childNodes'):
                        # Recursively process container elements
                        extract_text_recursive(child, current_style_name, hyperlink_url)
            
            extract_text_recursive(para)
            
            # Convert extracted text nodes to segments
            for text_content, style_name, hyperlink_url in para_text_nodes:
                segment = TextSegment(text=text_content)
                metadata_parts = []
                
                # Store hyperlink URL if present (Session 44)
                if hyperlink_url:
                    segment.hyperlink_url = hyperlink_url
                
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
        - Hyperlinks: <LINK:url>text</LINK> (Session 44)
        
        Args:
            tagged_text: Text with format tags
            
        Returns:
            List of TextSegment objects
        """
        segments: List[TextSegment] = []
        
        # Normalize whitespace in tags: < 1> → <1>, </ 1> → </1>
        # Handle tags with pipes and metadata: < 113 | 65536 : L > → <113|65536:L>
        # Session 70: Fixed to handle pipe characters in paragraph formatting tags
        def normalize_opening(match):
            bits = match.group(1).replace(' ', '')  # Remove all spaces from bits
            metadata = match.group(2)
            if metadata:
                metadata = metadata.replace(' ', '')  # Remove spaces from metadata
                return f"<{bits}:{metadata}>"
            else:
                return f"<{bits}>"
        
        normalized = re.sub(
            r'<\s*(\d+(?:\s*\|\s*\d+)*)\s*(?::\s*([^>]+))?\s*>',
            normalize_opening,
            tagged_text
        )
        # Closing tags: < / 113 | 65536 > → </113|65536>
        # Handle space after < as well: '< /' or '</'
        normalized = re.sub(
            r'<\s*/\s*(\d+(?:\s*\|\s*\d+)*)\s*>',
            lambda m: f"</{m.group(1).replace(' ', '')}>",
            normalized
        )
        
        # First, extract hyperlinks (Session 44)
        # Pattern: <LINK:url>display_text</LINK>
        # Replace with placeholder to process after regular tags
        hyperlink_pattern = r'<LINK:([^>]+)>([\s\S]*?)</LINK>'
        hyperlink_placeholders = []
        def replace_hyperlink(match):
            url = match.group(1).replace('&lt;', '<').replace('&gt;', '>')  # Decode URL
            text = match.group(2)
            index = len(hyperlink_placeholders)
            hyperlink_placeholders.append({'url': url, 'text': text})
            return f'{{{{HYPERLINK_{index}}}}}'
        normalized = re.sub(hyperlink_pattern, replace_hyperlink, normalized, flags=re.DOTALL)
        
        # Session 72 Fix: Helper to clean broken tag artifacts from Google Translate
        def clean_tag_artifacts(text: str) -> str:
            """
            Remove broken tag artifacts that Google Translate sometimes creates.
            
            Google Translate can corrupt tags by:
            - Adding spaces: <113|meta> → <113 | meta>
            - Removing closing tags entirely: <113|meta>text → <113 | text (no closing tag)
            - Splitting/merging text differently
            
            This function removes:
            1. Incomplete opening tags: <113 |, < 113|, <113:meta (no closing >)
            2. Complete but orphaned opening tags: <113|meta>, <113:meta>
            3. Broken closing tags: </113|65536>, </ 113>
            """
            # Remove incomplete opening tags (no closing >): <113 | (stops at space/newline)
            # Only match the tag token itself, NOT content after it
            cleaned = re.sub(r'<\s*\d+\s*\|[^\s>]*', '', text)
            
            # Remove complete orphaned opening tags: <113|meta>, <113:meta>
            cleaned = re.sub(r'<\s*\d+\s*(?:\|[^>]*)?\s*(?::[^>]*)?\s*>', '', cleaned)
            
            # Remove broken closing tags: </113|65536>, </ 113>
            cleaned = re.sub(r'<\s*/\s*\d+(?:\s*\|\s*\d+)?\s*>', '', cleaned)
            
            return cleaned
        
        # Pattern: <char|para:meta>text</char|para> or variations
        # Format: "char_bits|para_bits:char_meta|para_meta" or simpler combinations
        # Examples:
        #   <1>text</1> - only character format
        #   <1|256>text</1|256> - character + paragraph format
        #   <1:FF0000>text</1> - character format with metadata
        #   <1|256:FF0000|L>text</1|256> - both formats with metadata
        
        # Match patterns like: <1>, <1|256>, <1:meta>, <1|256:meta1|meta2>
        # Fixed in Session 72: Added ? to make metadata optional
        pattern = r'<([\d|]+)(?::([^>]+))?>([\s\S]*?)</\1>'
        
        last_pos = 0
        for match in re.finditer(pattern, normalized, re.DOTALL):
            # Add any plain text before this tag
            if match.start() > last_pos:
                plain = normalized[last_pos:match.start()]
                if plain:
                    # Session 72 Fix: Clean broken tags from plain text
                    cleaned_plain = clean_tag_artifacts(plain)
                    # Session 75 Fix: Don't strip! Preserve \n\n for paragraph breaks
                    if cleaned_plain:  # Keep whitespace/newlines
                        segments.append(TextSegment(text=cleaned_plain))
            
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
                # Session 72 Fix: Clean broken tags from remaining plain text
                cleaned = clean_tag_artifacts(plain)
                # Session 75 Fix: Don't strip! Preserve whitespace and newlines
                if cleaned:  # Keep all whitespace
                    segments.append(TextSegment(text=cleaned))
        
        # Restore hyperlink placeholders (Session 44)
        final_segments = []
        for segment in segments:
            # Check if segment text contains hyperlink placeholders
            hyperlink_placeholder_pattern = r'\{\{HYPERLINK_(\d+)\}\}'
            matches = list(re.finditer(hyperlink_placeholder_pattern, segment.text))
            
            if not matches:
                final_segments.append(segment)
                continue
            
            # Split segment by hyperlink placeholders
            last_pos = 0
            for match in matches:
                # Add text before placeholder
                if match.start() > last_pos:
                    before_text = segment.text[last_pos:match.start()]
                    if before_text:
                        before_seg = TextSegment(
                            text=before_text,
                            format_bits=segment.format_bits,
                            metadata=segment.metadata,
                            paragraph_format=segment.paragraph_format,
                            paragraph_metadata=segment.paragraph_metadata
                        )
                        final_segments.append(before_seg)
                
                # Add hyperlink segment
                index = int(match.group(1))
                if index < len(hyperlink_placeholders):
                    hyperlink_info = hyperlink_placeholders[index]
                    hyperlink_seg = TextSegment(
                        text=hyperlink_info['text'],
                        hyperlink_url=hyperlink_info['url'],
                        format_bits=segment.format_bits,
                        metadata=segment.metadata,
                        paragraph_format=segment.paragraph_format,
                        paragraph_metadata=segment.paragraph_metadata
                    )
                    final_segments.append(hyperlink_seg)
                
                last_pos = match.end()
            
            # Add text after last placeholder
            if last_pos < len(segment.text):
                after_text = segment.text[last_pos:]
                if after_text:
                    after_seg = TextSegment(
                        text=after_text,
                        format_bits=segment.format_bits,
                        metadata=segment.metadata,
                        paragraph_format=segment.paragraph_format,
                        paragraph_metadata=segment.paragraph_metadata
                    )
                    final_segments.append(after_seg)
        
        return final_segments
    
    @staticmethod
    def _reconstruct_table_to_docx(table: TableSegment, doc) -> None:
        """
        Reconstruct a table in DOCX format from TableSegment (Session 59).
        
        Args:
            table: TableSegment with cells and formatting
            doc: python-docx Document object to add table to
            
        Returns:
            The created python-docx Table object
        """
        from docx import Document
        
        # Create table with dimensions
        docx_table = doc.add_table(rows=table.num_rows, cols=table.num_cols)
        
        # Apply table style if specified
        if table.table_style:
            try:
                docx_table.style = table.table_style
            except (ValueError, KeyError, AttributeError) as e:
                logger.warning(f"Table style '{table.table_style}' not found in document: {e}")
                pass  # Style might not exist in document
        
        # Track which cells are covered by merges (to avoid duplicate processing)
        covered = set()
        
        # First pass: Mark covered cells
        for row_idx in range(table.num_rows):
            for col_idx in range(table.num_cols):
                cell_data = table.get_cell(row_idx, col_idx)
                if cell_data.col_span > 1 or cell_data.row_span > 1:
                    # Mark covered cells
                    for r_offset in range(cell_data.row_span):
                        for c_offset in range(cell_data.col_span):
                            if r_offset == 0 and c_offset == 0:
                                continue  # Skip the main cell
                            covered.add((row_idx + r_offset, col_idx + c_offset))
        
        # Populate each cell
        for row_idx in range(table.num_rows):
            for col_idx in range(table.num_cols):
                # Skip covered cells (will be handled by their parent merge cell)
                if (row_idx, col_idx) in covered:
                    continue
                
                cell_data = table.get_cell(row_idx, col_idx)
                docx_cell = docx_table.rows[row_idx].cells[col_idx]
                
                # Clear default paragraph (python-docx creates one empty paragraph by default)
                # We'll reuse it for the first content
                if len(docx_cell.paragraphs) > 0:
                    # Clear the default paragraph's runs
                    p = docx_cell.paragraphs[0]
                    p.clear()
                
                # Add formatted content
                current_paragraph = None
                for segment in cell_data.text_segments:
                    # Handle paragraph breaks
                    if segment.text == "\n":
                        # Start new paragraph
                        current_paragraph = None
                        continue
                    
                    # Create paragraph if needed
                    if current_paragraph is None:
                        if len(docx_cell.paragraphs) > 0 and not docx_cell.paragraphs[0].text:
                            # Reuse first empty paragraph
                            current_paragraph = docx_cell.paragraphs[0]
                        else:
                            current_paragraph = docx_cell.add_paragraph()
                    
                    # Add run with formatting
                    clean_text = FormatMapper.remove_tags(segment.text)
                    if clean_text:
                        run = current_paragraph.add_run(clean_text)
                        FormatMapper._apply_formatting(run, segment.format_bits, segment.metadata)
                
                # Apply cell-level formatting (Sessions 61-62)
                from docx.oxml import OxmlElement
                from docx.oxml.ns import qn
                tcPr = docx_cell._element.get_or_add_tcPr()
                
                # Shading - Session 61
                if cell_data.background_color:
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:fill'), cell_data.background_color)
                    tcPr.append(shd)
                
                # Borders - Session 62
                if cell_data.borders:
                    tcBorders = OxmlElement('w:tcBorders')
                    for side in ['top', 'bottom', 'left', 'right']:
                        if side in cell_data.borders:
                            border_info = cell_data.borders[side]
                            border_elem = OxmlElement(f'w:{side}')
                            border_elem.set(qn('w:val'), border_info['style'])
                            border_elem.set(qn('w:sz'), border_info['width'])
                            border_elem.set(qn('w:color'), border_info['color'])
                            tcBorders.append(border_elem)
                    tcPr.append(tcBorders)
                
                # Cell merging - Session 63
                if cell_data.col_span > 1 or cell_data.row_span > 1:
                    # Horizontal merge (colspan)
                    if cell_data.col_span > 1:
                        hMerge = OxmlElement('w:hMerge')
                        hMerge.set(qn('w:val'), 'restart')
                        tcPr.append(hMerge)
                        
                        # Mark continuation cells
                        for offset in range(1, cell_data.col_span):
                            if col_idx + offset < table.num_cols:
                                cont_cell = docx_table.rows[row_idx].cells[col_idx + offset]
                                cont_tcPr = cont_cell._element.get_or_add_tcPr()
                                cont_hMerge = OxmlElement('w:hMerge')
                                cont_hMerge.set(qn('w:val'), 'continue')
                                cont_tcPr.append(cont_hMerge)
                    
                    # Vertical merge (rowspan)
                    if cell_data.row_span > 1:
                        vMerge = OxmlElement('w:vMerge')
                        vMerge.set(qn('w:val'), 'restart')
                        tcPr.append(vMerge)
                        
                        # Mark continuation cells
                        for offset in range(1, cell_data.row_span):
                            if row_idx + offset < table.num_rows:
                                cont_cell = docx_table.rows[row_idx + offset].cells[col_idx]
                                cont_tcPr = cont_cell._element.get_or_add_tcPr()
                                cont_vMerge = OxmlElement('w:vMerge')
                                # Don't set val attribute - vMerge without val means continue
                                cont_tcPr.append(cont_vMerge)
        
        return docx_table
    
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
            # Handle TableSegment separately (Session 64 fix)
            if isinstance(segment, TableSegment):
                # Ensure current paragraph is added before table
                if current_paragraph.text or not current_paragraph.runs:
                    current_paragraph = doc.add_paragraph()
                
                # Reconstruct table using existing method
                FormatMapper._reconstruct_table_to_docx(segment, doc)
                
                # Start fresh paragraph after table
                current_paragraph = doc.add_paragraph()
                continue
            
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
                        
                        # Handle hyperlinks (Session 44)
                        if segment.hyperlink_url:
                            FormatMapper._add_hyperlink_to_paragraph(
                                current_paragraph, clean_part, segment.hyperlink_url,
                                segment.format_bits, segment.metadata, doc
                            )
                        else:
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
                
                # Handle hyperlinks (Session 44)
                if segment.hyperlink_url:
                    FormatMapper._add_hyperlink_to_paragraph(
                        current_paragraph, clean_text, segment.hyperlink_url,
                        segment.format_bits, segment.metadata, doc
                    )
                else:
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
            except (ValueError, KeyError, AttributeError) as e:
                logger.warning(f"Failed to apply highlight color: {e}")
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
        
        # Apply list item style (Session 39) - Must be before heading
        if format_bits & FormatBit.LIST_ITEM and metadata_index < len(metadata_parts):
            list_info = metadata_parts[metadata_index].strip()
            metadata_index += 1
            # Parse: "TYPE,LEVEL" (e.g., "B,1" or "N,2")
            try:
                parts = list_info.split(',')
                if len(parts) == 2:
                    list_type = parts[0]
                    level = int(parts[1])
                    # Apply list style based on type
                    if list_type == 'B':
                        paragraph.style = 'List Bullet'
                    elif list_type == 'N':
                        paragraph.style = 'List Number'
            except (ValueError, IndexError):
                pass  # Skip if parsing fails
        
        # Apply heading style (Session 33) - Must be first to set style
        if format_bits & FormatBit.HEADING and metadata_index < len(metadata_parts):
            heading_code = metadata_parts[metadata_index].strip()
            metadata_index += 1
            # Parse heading level (e.g., "H1" → "Heading 1")
            if heading_code.startswith('H') and len(heading_code) == 2:
                level = heading_code[1]
                if level.isdigit() and 1 <= int(level) <= 6:
                    paragraph.style = f'Heading {level}'
        
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
        
        # Apply indentation (Session 64 fix)
        if format_bits & FormatBit.INDENTATION and metadata_index + 2 < len(metadata_parts):
            try:
                from docx.shared import Pt
                # Consume 3 metadata parts: first_line, left, right
                first_line = int(metadata_parts[metadata_index].strip())
                left = int(metadata_parts[metadata_index + 1].strip())
                right = int(metadata_parts[metadata_index + 2].strip())
                metadata_index += 3
                
                if first_line != 0:
                    paragraph.paragraph_format.first_line_indent = Pt(first_line)
                if left != 0:
                    paragraph.paragraph_format.left_indent = Pt(left)
                if right != 0:
                    paragraph.paragraph_format.right_indent = Pt(right)
            except (ValueError, IndexError):
                pass  # Skip invalid indentation
        
        # Apply space before/after (Session 64 fix)
        if format_bits & FormatBit.SPACE_BEFORE_AFTER and metadata_index + 1 < len(metadata_parts):
            try:
                from docx.shared import Pt
                # Consume 2 metadata parts: before, after
                before = int(metadata_parts[metadata_index].strip())
                after = int(metadata_parts[metadata_index + 1].strip())
                metadata_index += 2
                
                if before != 0:
                    paragraph.paragraph_format.space_before = Pt(before)
                if after != 0:
                    paragraph.paragraph_format.space_after = Pt(after)
            except (ValueError, IndexError):
                pass  # Skip invalid spacing
        
        # Apply keep lines together (Session 27)
        if format_bits & FormatBit.KEEP_LINES_TOGETHER:
            paragraph.paragraph_format.keep_together = True
        
        # Apply keep with next (Session 28)
        if format_bits & FormatBit.KEEP_WITH_NEXT:
            paragraph.paragraph_format.keep_with_next = True
        
        # Apply page break before (Session 29)
        if format_bits & FormatBit.PAGE_BREAK_BEFORE:
            paragraph.paragraph_format.page_break_before = True
        
        # Apply widow/orphan control (Session 30)
        if format_bits & FormatBit.WIDOW_ORPHAN_CONTROL:
            paragraph.paragraph_format.widow_control = True
        
        # Apply bidirectional text (Session 31)
        if format_bits & FormatBit.BIDI_TEXT and metadata_index < len(metadata_parts):
            direction = metadata_parts[metadata_index].strip()
            metadata_index += 1
            if direction == 'R':
                paragraph.paragraph_format.bidi = True  # RTL
            # Note: LTR is default, no need to explicitly set

    @staticmethod
    def _add_hyperlink_to_paragraph(paragraph, text, url, format_bits=0, metadata=None, doc=None):
        """
        Add a hyperlink to a paragraph (Session 44).
        
        Args:
            paragraph: python-docx Paragraph object
            text: Display text for hyperlink
            url: Target URL
            format_bits: Character formatting bits
            metadata: Character formatting metadata
            doc: Document object (needed for relationship creation)
        """
        from docx.oxml import parse_xml
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
        
        # Create hyperlink relationship
        r_id = doc.part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
        
        # Create hyperlink XML element
        hyperlink = OxmlElement('w:hyperlink')
        hyperlink.set(qn('r:id'), r_id)
        
        # Create a run inside the hyperlink
        run_elem = OxmlElement('w:r')
        
        # Create text element
        t_elem = OxmlElement('w:t')
        t_elem.text = text
        run_elem.append(t_elem)
        
        # Add run to hyperlink
        hyperlink.append(run_elem)
        
        # Add hyperlink to paragraph
        paragraph._element.append(hyperlink)
        
        # Now apply formatting to the run we created
        # We need to wrap it in a Run object to use _apply_formatting
        from docx.text.run import Run
        run_obj = Run(run_elem, paragraph)
        FormatMapper._apply_formatting(run_obj, format_bits, metadata)

    @staticmethod
    def _reconstruct_table_to_odt(table: TableSegment, doc) -> None:
        """
        Reconstruct a table in ODT format from TableSegment (Session 60).
        
        Args:
            table: TableSegment with cells and formatting
            doc: ODF OpenDocumentText object to add table to
            
        Returns:
            The created ODF Table object
        """
        from odf.table import Table, TableRow, TableCell
        from odf.text import P, Span
        from odf.style import Style, TextProperties, TableCellProperties
        from odf import style as odf_style
        
        # Create style cache for this table
        style_cache = {}
        
        def get_or_create_style(format_bits: int, metadata: Optional[str]) -> Optional[Style]:
            """Get existing style or create new one for format combination."""
            if format_bits == 0:
                return None
            
            cache_key = f"{format_bits}:{metadata or ''}"
            if cache_key in style_cache:
                return style_cache[cache_key]
            
            # Create new style
            style_name = f"TableCell{format_bits}_{len(style_cache)}"
            style = Style(name=style_name, family="text")
            text_props = TextProperties()
            
            # Parse metadata
            metadata_parts = metadata.split(",") if metadata else []
            metadata_index = 0
            
            # Apply formatting (same as create_odt_from_segments)
            if format_bits & FormatBit.BOLD:
                text_props.setAttribute("fontweight", "bold")
            
            if format_bits & FormatBit.ITALIC:
                text_props.setAttribute("fontstyle", "italic")
            
            if format_bits & FormatBit.UNDERLINE:
                text_props.setAttribute("textunderlinestyle", "solid")
            
            if format_bits & FormatBit.DOUBLE_UNDERLINE:
                text_props.setAttribute("textunderlinetype", "double")
            
            if format_bits & FormatBit.STRIKETHROUGH:
                text_props.setAttribute("textlinethroughstyle", "solid")
            
            if format_bits & FormatBit.SUPERSCRIPT:
                text_props.setAttribute("textposition", "super 58%")
            
            if format_bits & FormatBit.SUBSCRIPT:
                text_props.setAttribute("textposition", "sub 58%")
            
            if format_bits & FormatBit.SMALL_CAPS:
                text_props.setAttribute("fontvariant", "small-caps")
            
            if format_bits & FormatBit.FONT_COLOR and metadata_index < len(metadata_parts):
                hex_color = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("color", f"#{hex_color}")
            
            if format_bits & FormatBit.HIGHLIGHT and metadata_index < len(metadata_parts):
                hex_bg = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("backgroundcolor", f"#{hex_bg}")
            
            if format_bits & FormatBit.FONT_SIZE and metadata_index < len(metadata_parts):
                size_str = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("fontsize", f"{size_str}pt")
            
            if format_bits & FormatBit.FONT_FAMILY and metadata_index < len(metadata_parts):
                font_name = metadata_parts[metadata_index].strip()
                metadata_index += 1
                text_props.setAttribute("fontname", font_name)
            
            style.addElement(text_props)
            doc.automaticstyles.addElement(style)
            style_cache[cache_key] = style
            return style
        
        # Create table
        odt_table = Table()
        
        # Track covered cells for proper placeholder insertion
        # covered_cells[row][col] = True if cell is covered by a merge
        covered_cells = {}
        for r in range(table.num_rows):
            covered_cells[r] = {}
            for c in range(table.num_cols):
                covered_cells[r][c] = False
        
        # Mark cells covered by merges
        for row_idx in range(table.num_rows):
            for col_idx in range(table.num_cols):
                cell_data = table.get_cell(row_idx, col_idx)
                if cell_data.col_span > 1 or cell_data.row_span > 1:
                    # Mark covered cells
                    for r_offset in range(cell_data.row_span):
                        for c_offset in range(cell_data.col_span):
                            if r_offset == 0 and c_offset == 0:
                                continue  # Skip the main cell
                            r = row_idx + r_offset
                            c = col_idx + c_offset
                            if r < table.num_rows and c < table.num_cols:
                                covered_cells[r][c] = True
        
        # Create rows and cells
        for row_idx in range(table.num_rows):
            odt_row = TableRow()
            
            for col_idx in range(table.num_cols):
                # Check if this cell is covered by a merge
                if covered_cells[row_idx][col_idx]:
                    # Add covered cell placeholder
                    from odf.table import CoveredTableCell
                    odt_row.addElement(CoveredTableCell())
                    continue
                
                cell_data = table.get_cell(row_idx, col_idx)
                odt_cell = TableCell()
                
                # Add cell content
                current_paragraph = None
                for segment in cell_data.text_segments:
                    # Handle paragraph breaks
                    if segment.text == "\n":
                        current_paragraph = None
                        continue
                    
                    # Create paragraph if needed
                    if current_paragraph is None:
                        current_paragraph = P()
                        odt_cell.addElement(current_paragraph)
                    
                    # Add formatted text
                    clean_text = FormatMapper.remove_tags(segment.text)
                    if clean_text:
                        if segment.format_bits == 0:
                            # Plain text
                            current_paragraph.addText(clean_text)
                        else:
                            # Formatted text - use span
                            style = get_or_create_style(segment.format_bits, segment.metadata)
                            span = Span(stylename=style)
                            span.addText(clean_text)
                            current_paragraph.addElement(span)
                
                # Ensure cell has at least one paragraph
                if len(odt_cell.childNodes) == 0:
                    odt_cell.addElement(P())
                
                # Apply cell-level formatting (Sessions 61-62)
                if cell_data.background_color or cell_data.borders:
                    # Create cell style with background color and/or borders
                    cell_style = odf_style.Style(name=f"cell_{row_idx}_{col_idx}", family="table-cell")
                    cell_props = odf_style.TableCellProperties()
                    
                    # Background color - Session 61
                    if cell_data.background_color:
                        cell_props.setAttribute("backgroundcolor", f"#{cell_data.background_color}")
                    
                    # Borders - Session 62
                    if cell_data.borders:
                        for side in ['top', 'bottom', 'left', 'right']:
                            if side in cell_data.borders:
                                border_info = cell_data.borders[side]
                                # Convert DOCX format to ODT format
                                # DOCX: width in 1/8 pt, style name, color hex
                                # ODT: "width style #color" (e.g., "0.05cm solid #FF0000")
                                
                                # Convert width from 1/8 pt to cm (rough approximation)
                                width_eighths = int(border_info['width'])
                                width_pt = width_eighths / 8.0
                                width_cm = width_pt * 0.0353  # 1 pt ≈ 0.0353 cm
                                
                                # Map DOCX styles to ODT styles
                                style_map = {
                                    'single': 'solid',
                                    'thick': 'solid',
                                    'double': 'double',
                                    'dashed': 'dashed',
                                    'dotted': 'dotted'
                                }
                                odt_style = style_map.get(border_info['style'], 'solid')
                                
                                border_value = f"{width_cm:.3f}cm {odt_style} #{border_info['color']}"
                                cell_props.setAttribute(f"border{side}", border_value)
                    
                    cell_style.addElement(cell_props)
                    doc.automaticstyles.addElement(cell_style)
                    odt_cell.setAttribute("stylename", cell_style)
                
                # Cell merging - Session 63
                if cell_data.col_span > 1:
                    odt_cell.setAttribute("numbercolumnsspanned", str(cell_data.col_span))
                
                if cell_data.row_span > 1:
                    odt_cell.setAttribute("numberrowsspanned", str(cell_data.row_span))
                
                odt_row.addElement(odt_cell)
            
            odt_table.addElement(odt_row)
        
        # Add table to document
        doc.text.addElement(odt_table)
        return odt_table

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
        from odf.style import Style, TextProperties, ParagraphProperties
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
            
            # Apply list item (Session 39)
            # Note: Full ODT list support requires wrapping in text:list elements
            # For now, just apply list-style indentation
            if para_format_bits & FormatBit.LIST_ITEM and metadata_index < len(metadata_parts):
                list_info = metadata_parts[metadata_index].strip()
                metadata_index += 1
                # Parse: "TYPE,LEVEL" and apply indentation
                try:
                    parts = list_info.split(',')
                    if len(parts) == 2:
                        level = int(parts[1])
                        # Apply indentation based on level (0.5cm per level)
                        indent_cm = level * 0.5
                        para_props.setAttribute("marginleft", f"{indent_cm:.1f}cm")
                except (ValueError, IndexError):
                    pass  # Skip if parsing fails
            
            # Apply heading level (Session 33)
            # Note: ODT headings use outline-level attribute
            if para_format_bits & FormatBit.HEADING and metadata_index < len(metadata_parts):
                heading_code = metadata_parts[metadata_index].strip()
                metadata_index += 1
                # Parse heading level (e.g., "H1" → outline-level="1")
                if heading_code.startswith('H') and len(heading_code) == 2:
                    level = heading_code[1]
                    if level.isdigit() and 1 <= int(level) <= 6:
                        para_props.setAttribute("outlinelevel", level)
            
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
            
            # Apply keep with next (Session 28)
            if para_format_bits & FormatBit.KEEP_WITH_NEXT:
                para_props.setAttribute("keepwithnext", "always")
            
            # Apply page break before (Session 29)
            if para_format_bits & FormatBit.PAGE_BREAK_BEFORE:
                para_props.setAttribute("breakbefore", "page")
            
            # Apply widow/orphan control (Session 30)
            if para_format_bits & FormatBit.WIDOW_ORPHAN_CONTROL:
                # Set both widows and orphans to 2 (standard value)
                para_props.setAttribute("widows", "2")
                para_props.setAttribute("orphans", "2")
            
            # Apply bidirectional text (Session 31)
            if para_format_bits & FormatBit.BIDI_TEXT and metadata_index < len(metadata_parts):
                direction = metadata_parts[metadata_index].strip()
                metadata_index += 1
                if direction == 'R':
                    para_props.setAttribute("writingmode", "rl-tb")  # RTL
                elif direction == 'L':
                    para_props.setAttribute("writingmode", "lr-tb")  # LTR
            
            style.addElement(para_props)
            doc.automaticstyles.addElement(style)
            style_cache[cache_key] = style
            return style
        
        # Create document content
        current_paragraph = P()
        current_para_format = 0
        current_para_metadata = None
        
        for segment in segments:
            # Handle TableSegment separately (Session 64 fix)
            if isinstance(segment, TableSegment):
                # Finalize current paragraph before table
                if current_paragraph.childNodes or hasattr(current_paragraph, 'data'):
                    doc.text.addElement(current_paragraph)
                    current_paragraph = P()
                
                # Reconstruct table using existing method
                FormatMapper._reconstruct_table_to_odt(segment, doc)
                
                # Start fresh paragraph after table
                current_paragraph = P()
                continue
            
            # Check if paragraph formatting changed
            if segment.paragraph_format != current_para_format or segment.paragraph_metadata != current_para_metadata:
                # Need to finalize current paragraph and start new one
                if current_paragraph.childNodes or hasattr(current_paragraph, 'data'):
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
                        
                        # Handle hyperlinks (Session 44)
                        if segment.hyperlink_url:
                            from odf.text import A
                            link = A(href=segment.hyperlink_url)
                            
                            # Apply formatting to link content if needed
                            style = get_or_create_style(segment.format_bits, segment.metadata)
                            if style:
                                span = Span(stylename=style)
                                span.addText(clean_part)
                                link.addElement(span)
                            else:
                                link.addText(clean_part)
                            
                            current_paragraph.addElement(link)
                        else:
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
                
                # Session 75: Handle line breaks (\n) and tabs (\t) in text
                # Split by \n to insert line breaks
                if '\n' in clean_text or '\t' in clean_text:
                    from odf.text import LineBreak, Tab
                    
                    # Process character by character to handle \n and \t
                    i = 0
                    while i < len(clean_text):
                        if clean_text[i] == '\n':
                            # Insert line break
                            current_paragraph.addElement(LineBreak())
                            i += 1
                        elif clean_text[i] == '\t':
                            # Insert tab
                            current_paragraph.addElement(Tab())
                            i += 1
                        else:
                            # Collect regular text until next special char
                            j = i
                            while j < len(clean_text) and clean_text[j] not in '\n\t':
                                j += 1
                            
                            text_part = clean_text[i:j]
                            if text_part:
                                # Handle hyperlinks (Session 44)
                                if segment.hyperlink_url:
                                    from odf.text import A
                                    link = A(href=segment.hyperlink_url)
                                    
                                    # Apply formatting to link content if needed
                                    style = get_or_create_style(segment.format_bits, segment.metadata)
                                    if style:
                                        span = Span(stylename=style)
                                        span.addText(text_part)
                                        link.addElement(span)
                                    else:
                                        link.addText(text_part)
                                    
                                    current_paragraph.addElement(link)
                                else:
                                    # Get or create style for this format
                                    style = get_or_create_style(segment.format_bits, segment.metadata)
                                    
                                    if style:
                                        span = Span(stylename=style)
                                        span.addText(text_part)
                                        current_paragraph.addElement(span)
                                    else:
                                        current_paragraph.addText(text_part)
                            
                            i = j
                else:
                    # No special characters - add text directly
                    # Handle hyperlinks (Session 44)
                    if segment.hyperlink_url:
                        from odf.text import A
                        link = A(href=segment.hyperlink_url)
                        
                        # Apply formatting to link content if needed
                        style = get_or_create_style(segment.format_bits, segment.metadata)
                        if style:
                            span = Span(stylename=style)
                            span.addText(clean_text)
                            link.addElement(span)
                        else:
                            link.addText(clean_text)
                        
                        current_paragraph.addElement(link)
                    else:
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
