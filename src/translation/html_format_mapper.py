#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML Format Mapper - Convert ODT formatting to HTML for translation

This module replaces the number tag system with a clean HTML-based approach.
Google Translate preserves HTML structure naturally (proven technology).

Architecture:
    ODT → Extract (HTML) → Google Translate → Create ODT from HTML

Key Features:
    - Full <html><head><style>...</style></head></head><body>...</body></html> structure
    - CSS classes for format preservation (base + modifiers)
    - Automatic memory management (RAM check → JSON fallback)
    - HTML entities for whitespace preservation
    - 100% format preservation (no visible tags/placeholders)

Author: Josué Amaral (COM8)
Date: February 9, 2026
Session: 77 - Complete HTML refactor (Option B)
"""

import html
import hashlib
import json
import os
import psutil
import re
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple
from xml.dom import minidom

from odf import opendocument, text as odf_text, style as odf_style, table as odf_table, draw as odf_draw
from odf.element import Text as ODFText


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FormatAttributes:
    """Store formatting attributes extracted from ODT styles."""
    # Character formatting
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    font_family: Optional[str] = None
    font_size: Optional[int] = None  # in points
    font_color: Optional[str] = None  # hex RGB (e.g., "525252")
    highlight_color: Optional[str] = None  # hex RGB
    
    # Paragraph formatting
    alignment: Optional[str] = None  # L/C/R/J
    line_spacing: Optional[float] = None  # multiplier (e.g., 1.5)
    indent_first: Optional[int] = None  # points
    indent_left: Optional[int] = None  # points
    indent_right: Optional[int] = None  # points
    
    # Special attributes
    heading_level: Optional[int] = None  # 1-6
    is_list_item: bool = False
    list_type: Optional[str] = None  # 'B' (bullet) or 'N' (numbered)
    list_level: Optional[int] = None  # 1-9
    
    def to_css(self) -> str:
        """Convert attributes to CSS declaration."""
        css_parts = []
        
        # Character styles
        if self.bold:
            css_parts.append("font-weight: bold")
        if self.italic:
            css_parts.append("font-style: italic")
        if self.underline:
            css_parts.append("text-decoration: underline")
        if self.strikethrough:
            css_parts.append("text-decoration: line-through")
        if self.font_family:
            css_parts.append(f"font-family: {self.font_family}")
        if self.font_size:
            css_parts.append(f"font-size: {self.font_size}pt")
        if self.font_color:
            css_parts.append(f"color: #{self.font_color}")
        if self.highlight_color:
            css_parts.append(f"background-color: #{self.highlight_color}")
        
        # Paragraph styles
        if self.alignment:
            align_map = {'L': 'left', 'C': 'center', 'R': 'right', 'J': 'justify'}
            css_parts.append(f"text-align: {align_map.get(self.alignment, 'left')}")
        if self.line_spacing:
            css_parts.append(f"line-height: {self.line_spacing}")
        if self.indent_first:
            css_parts.append(f"text-indent: {self.indent_first}pt")
        if self.indent_left:
            css_parts.append(f"margin-left: {self.indent_left}pt")
        if self.indent_right:
            css_parts.append(f"margin-right: {self.indent_right}pt")
        
        return "; ".join(css_parts)
    
    def __hash__(self):
        """Make hashable for deduplication."""
        return hash((
            self.bold, self.italic, self.underline, self.strikethrough,
            self.font_family, self.font_size, self.font_color, self.highlight_color,
            self.alignment, self.line_spacing, self.indent_first, self.indent_left, self.indent_right,
            self.heading_level, self.is_list_item, self.list_type, self.list_level
        ))
    
    def __eq__(self, other):
        """Enable comparison for deduplication."""
        if not isinstance(other, FormatAttributes):
            return False
        return (
            self.bold == other.bold and
            self.italic == other.italic and
            self.underline == other.underline and
            self.strikethrough == other.strikethrough and
            self.font_family == other.font_family and
            self.font_size == other.font_size and
            self.font_color == other.font_color and
            self.highlight_color == other.highlight_color and
            self.alignment == other.alignment and
            self.line_spacing == other.line_spacing and
            self.indent_first == other.indent_first and
            self.indent_left == other.indent_left and
            self.indent_right == other.indent_right and
            self.heading_level == other.heading_level and
            self.is_list_item == other.is_list_item and
            self.list_type == other.list_type and
            self.list_level == other.list_level
        )


@dataclass
class HTMLSegment:
    """Represents a text segment with HTML formatting."""
    text: str
    css_class: str
    tag_type: str  # 'div', 'span', 'br' (paragraph break), 'line-break' (soft break), or 'tab'
    attributes: FormatAttributes


# ============================================================================
# CSS Class Management
# ============================================================================

class CSSClassManager:
    """
    Manages CSS class generation with deduplication.
    
    Strategy: Simple incremental naming (fmt1, fmt2, fmt3...)
    Reuses classes for identical format combinations.
    """
    
    def __init__(self):
        self.format_to_class: Dict[FormatAttributes, str] = {}
        self.class_to_format: Dict[str, FormatAttributes] = {}
        self.counter = 1
    
    def get_or_create_class(self, fmt: FormatAttributes) -> str:
        """Get existing class or create new one for format."""
        if fmt in self.format_to_class:
            return self.format_to_class[fmt]
        
        # Create new class
        class_name = f"fmt{self.counter}"
        self.counter += 1
        
        self.format_to_class[fmt] = class_name
        self.class_to_format[class_name] = fmt
        
        return class_name
    
    def generate_css(self) -> str:
        """Generate complete CSS stylesheet."""
        css_lines = []
        
        for class_name in sorted(self.class_to_format.keys(), key=lambda x: int(x[3:])):
            fmt = self.class_to_format[class_name]
            css_declaration = fmt.to_css()
            if css_declaration:
                css_lines.append(f".{class_name} {{ {css_declaration}; }}")
        
        return "\n".join(css_lines)
    
    def get_format(self, class_name: str) -> Optional[FormatAttributes]:
        """Get format attributes for a CSS class."""
        return self.class_to_format.get(class_name)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'class_to_css': {
                cls: self.class_to_format[cls].to_css()
                for cls in self.class_to_format
            },
            'class_to_attributes': {
                cls: {
                    'bold': fmt.bold,
                    'italic': fmt.italic,
                    'underline': fmt.underline,
                    'strikethrough': fmt.strikethrough,
                    'font_family': fmt.font_family,
                    'font_size': fmt.font_size,
                    'font_color': fmt.font_color,
                    'highlight_color': fmt.highlight_color,
                    'alignment': fmt.alignment,
                    'line_spacing': fmt.line_spacing,
                    'indent_first': fmt.indent_first,
                    'indent_left': fmt.indent_left,
                    'indent_right': fmt.indent_right,
                    'heading_level': fmt.heading_level,
                    'is_list_item': fmt.is_list_item,
                    'list_type': fmt.list_type,
                    'list_level': fmt.list_level,
                }
                for cls, fmt in self.class_to_format.items()
            }
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CSSClassManager':
        """Restore from dictionary."""
        manager = CSSClassManager()
        
        for cls, attrs in data['class_to_attributes'].items():
            fmt = FormatAttributes(**attrs)
            manager.class_to_format[cls] = fmt
            manager.format_to_class[fmt] = cls
            
            # Update counter
            cls_num = int(cls[3:])
            if cls_num >= manager.counter:
                manager.counter = cls_num + 1
        
        return manager


# ============================================================================
# Image Management (NEW for Phase 1 - COM8)
# ============================================================================

@dataclass
class ODTImageData:
    """Stores image binary data and metadata for ODT files."""
    
    image_id: str              # 'IMG001', 'IMG002', etc.
    blob: bytes                # Raw PNG/JPEG/GIF binary data
    format: str                # 'png', 'jpeg', 'gif'
    width_cm: float            # Width in centimeters
    height_cm: float           # Height in centimeters
    original_href: str         # Original path (e.g., 'Pictures/image1.png')
    blob_hash: Optional[str]   # SHA256 hash for deduplication
    
    def get_width_inches(self) -> float:
        """Convert cm to inches (1 inch = 2.54 cm)."""
        return self.width_cm / 2.54
    
    def get_height_inches(self) -> float:
        """Convert cm to inches."""
        return self.height_cm / 2.54


class ODTImageManager:
    """
    Manages image storage and reconstruction for ODT translation.
    
    Adapted from DOCX ImageManager (docx_html_mapper.py).
    Stores images extracted from ODT Pictures/ folder.
    """
    
    def __init__(self):
        """Initialize image storage."""
        self._images: Dict[str, ODTImageData] = {}  # image_id → ODTImageData
        self._hash_to_id: Dict[str, str] = {}       # blob_hash → image_id
        self._next_id: int = 1                      # Counter for IMG001, IMG002, etc.
    
    def add_image(self, blob: bytes, img_format: str, 
                  width_cm: float, height_cm: float, 
                  original_href: str) -> str:
        """
        Add image to storage with deduplication.
        
        Args:
            blob: Raw image binary data
            img_format: Image format ('png', 'jpeg', 'gif')
            width_cm: Image width in centimeters
            height_cm: Image height in centimeters
            original_href: Original href (e.g., 'Pictures/image1.png')
        
        Returns:
            image_id: Unique ID for this image (e.g., 'IMG001')
        """
        # Calculate hash for deduplication
        blob_hash = hashlib.sha256(blob).hexdigest()
        
        # Check if image already exists (same binary data)
        if blob_hash in self._hash_to_id:
            existing_id = self._hash_to_id[blob_hash]
            print(f"[ODTImageManager] Deduplication: reusing {existing_id} for {original_href}")
            return existing_id
        
        # Warn about large images
        blob_size_mb = len(blob) / (1024 * 1024)
        if blob_size_mb > 10:
            print(f"[ODTImageManager] WARNING: Large image ({blob_size_mb:.1f}MB)")
        
        # Generate new ID
        image_id = f"IMG{self._next_id:03d}"  # IMG001, IMG002, etc.
        self._next_id += 1
        
        # Store image data
        image_data = ODTImageData(
            image_id=image_id,
            blob=blob,
            format=img_format,
            width_cm=width_cm,
            height_cm=height_cm,
            original_href=original_href,
            blob_hash=blob_hash
        )
        
        self._images[image_id] = image_data
        self._hash_to_id[blob_hash] = image_id
        
        print(f"[ODTImageManager] Stored {image_id}: {img_format}, "
              f"{width_cm:.2f}cm x {height_cm:.2f}cm, "
              f"{len(blob)} bytes")
        
        # Check total memory usage
        stats = self.get_statistics()
        if stats['total_mb'] > 100:
            print(f"[ODTImageManager] WARNING: High memory usage ({stats['total_mb']:.1f}MB)")
        
        return image_id
    
    def get_image(self, image_id: str) -> Optional[ODTImageData]:
        """
        Retrieve image by ID.
        
        Returns:
            ODTImageData if found, None otherwise
        """
        return self._images.get(image_id)
    
    def generate_placeholder(self, image_id: str) -> str:
        """
        Generate HTML placeholder for image.
        
        Returns:
            HTML string: '<span data-image="IMG001"></span>'
        """
        return f'<span data-image="{image_id}"></span>'
    
    def get_statistics(self) -> dict:
        """
        Get storage statistics for debugging.
        
        Returns:
            Dict with counts and memory usage
        """
        total_images = len(self._images)
        unique_blobs = len(self._hash_to_id)
        total_bytes = sum(len(img.blob) for img in self._images.values())
        
        return {
            'total_images': total_images,
            'unique_blobs': unique_blobs,
            'duplicates': total_images - unique_blobs,
            'total_bytes': total_bytes,
            'total_mb': total_bytes / (1024 * 1024)
        }
    
    def clear(self):
        """Clear all stored images (for memory management)."""
        self._images.clear()
        self._hash_to_id.clear()
        self._next_id = 1


# ============================================================================
# Table Management (Phase 2 - COM8)
# ============================================================================

@dataclass
class ODTTableData:
    """
    Stores metadata for a single ODT table.
    
    Phase 2 - COM8: Adapted from DOCX TableData for ODF format.
    """
    
    table_id: str                     # 'TBL001', 'TBL002', etc.
    rows: int                         # Number of rows
    cols: int                         # Number of columns
    cells: List[List[str]]            # 2D array [row][col] = text
    name: Optional[str] = None        # table:name attribute from ODF
    
    def get_cell(self, row: int, col: int) -> str:
        """
        Get cell text at row, col (0-indexed).
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
        
        Returns:
            Cell text, or empty string if out of bounds
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return ""
    
    def set_cell(self, row: int, col: int, text: str) -> None:
        """
        Set cell text at row, col (0-indexed).
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            text: Cell content
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.cells[row][col] = text
    
    def to_html(self) -> str:
        """
        Convert to HTML table with data-table marker.
        
        Returns:
            HTML <table> element with data-table attribute
        """
        html_parts = [f'<table data-table="{self.table_id}">\n']
        
        for row_idx in range(self.rows):
            html_parts.append('  <tr>\n')
            for col_idx in range(self.cols):
                cell_text = self.cells[row_idx][col_idx]
                # HTML escape special characters
                safe_text = html.escape(cell_text)
                html_parts.append(f'    <td>{safe_text}</td>\n')
            html_parts.append('  </tr>\n')
        
        html_parts.append('</table>')
        return ''.join(html_parts)
    
    def get_dimensions(self) -> tuple:
        """
        Get table dimensions.
        
        Returns:
            Tuple of (rows, cols)
        """
        return (self.rows, self.cols)


class ODTTableManager:
    """
    Manages collection of tables for ODT↔HTML conversion.
    
    Phase 2 - COM8: Adapted from DOCX TableManager for ODF format.
    
    Tables are assigned unique IDs (TBL001, TBL002, etc.) and stored
    with their metadata. During extraction, ODT tables are converted
    to HTML <table> elements. During reconstruction, HTML tables are
    converted back to ODT tables.
    
    Example:
        >>> manager = ODTTableManager()
        >>> table_id = manager.add_table(
        ...     rows=2, cols=2,
        ...     cells=[['A', 'B'], ['C', 'D']]
        ... )
        >>> table_id
        'TBL001'
        >>> table_data = manager.get_table(table_id)
        >>> print(table_data.to_html())
        <table data-table="TBL001">
          <tr><td>A</td><td>B</td></tr>
          <tr><td>C</td><td>D</td></tr>
        </table>
    """
    
    def __init__(self):
        """Initialize empty table manager."""
        self._tables: Dict[str, ODTTableData] = {}
        self._document_order: List[str] = []  # Track table order
        self._next_id: int = 1
    
    def add_table(
        self,
        rows: int,
        cols: int,
        cells: List[List[str]],
        name: Optional[str] = None
    ) -> str:
        """
        Add table to manager and return assigned ID.
        
        Args:
            rows: Number of rows
            cols: Number of columns
            cells: 2D list of cell text [row][col]
            name: ODF table:name attribute (optional)
        
        Returns:
            table_id: Assigned table ID (e.g., "TBL001")
        
        Raises:
            ValueError: If dimensions don't match cells array
        """
        # Validate dimensions
        if len(cells) != rows:
            raise ValueError(f"Expected {rows} rows, got {len(cells)}")
        for row_idx, row in enumerate(cells):
            if len(row) != cols:
                raise ValueError(
                    f"Row {row_idx} has {len(row)} cells, expected {cols}"
                )
        
        # Generate ID
        table_id = f"TBL{self._next_id:03d}"
        self._next_id += 1
        
        # Create and store
        table_data = ODTTableData(
            table_id=table_id,
            rows=rows,
            cols=cols,
            cells=cells,
            name=name
        )
        self._tables[table_id] = table_data
        self._document_order.append(table_id)
        
        print(f"[ODTTableManager] Stored {table_id}: {rows}×{cols} table")
        
        return table_id
    
    def get_table(self, table_id: str) -> Optional[ODTTableData]:
        """
        Get table by ID.
        
        Args:
            table_id: Table identifier (e.g., "TBL001")
        
        Returns:
            ODTTableData if found, None otherwise
        """
        return self._tables.get(table_id)
    
    def has_table(self, table_id: str) -> bool:
        """
        Check if table exists.
        
        Args:
            table_id: Table identifier
        
        Returns:
            True if table exists, False otherwise
        """
        return table_id in self._tables
    
    def get_all_tables(self) -> List[ODTTableData]:
        """
        Get all tables in document order.
        
        Returns:
            List of ODTTableData objects in document order
        """
        return [self._tables[tid] for tid in self._document_order]
    
    def get_statistics(self) -> dict:
        """
        Get storage statistics for debugging.
        
        Returns:
            Dict with counts and table info
        """
        total_cells = sum(
            t.rows * t.cols for t in self._tables.values()
        )
        
        return {
            'total_tables': len(self._tables),
            'table_ids': list(self._document_order),
            'total_cells': total_cells
        }
    
    def clear(self):
        """Clear all stored tables (for memory management)."""
        self._tables.clear()
        self._document_order.clear()
        self._next_id = 1


# ============================================================================
# ODT Extraction to HTML
# ============================================================================

class HTMLFormatMapper:
    """Convert ODT documents to/from HTML for translation."""
    
    @staticmethod
    def extract_html_from_odt(file_path: str) -> Tuple[str, object, Optional['ODTImageManager'], Optional['ODTTableManager']]:
        """
        Extract ODT content as HTML with CSS formatting, images, and tables.
        
        Phase 1 - COM8: Added image extraction support
        Phase 2 - COM8: Added table extraction support
        
        Args:
            file_path: Path to .odt file
            
        Returns:
            Tuple of (html_string, css_manager_or_path, image_manager, table_manager)
            - html_string: Full HTML document with structure, image placeholders, and tables
            - css_manager_or_path: CSSClassManager object OR path to JSON file
              (automatic decision based on available RAM)
            - image_manager: ODTImageManager with extracted images (or None if no images)
            - table_manager: ODTTableManager with extracted tables (or None if no tables)
        """
        doc = opendocument.load(file_path)
        css_manager = CSSClassManager()
        image_manager = ODTImageManager()  # Phase 1: Create image manager
        table_manager = ODTTableManager()  # Phase 2: Create table manager
        segments: List[HTMLSegment] = []
        
        # Build style dictionary
        styles = HTMLFormatMapper._build_style_dict(doc)
        
        # Phase 1: Extract images from ODT Pictures/ folder
        try:
            with zipfile.ZipFile(file_path, 'r') as odt_zip:
                # Get list of image files in Pictures/ folder
                image_files = [f for f in odt_zip.namelist() if f.startswith('Pictures/') and not f.endswith('/')]
                
                if image_files:
                    print(f"[ODT Extract] Found {len(image_files)} image(s) in Pictures/")
                    
                    for img_path in image_files:
                        # Read image binary data
                        with odt_zip.open(img_path) as img_file:
                            blob = img_file.read()
                        
                        # Determine format from extension
                        img_ext = os.path.splitext(img_path)[1].lower()
                        img_format = {
                            '.png': 'png',
                            '.jpg': 'jpeg',
                            '.jpeg': 'jpeg',
                            '.gif': 'gif',
                        }.get(img_ext, 'unknown')
                        
                        # Default size (will be refined when we parse draw:frame)
                        # For now, use default 3in x 2in (7.62cm x 5.08cm)
                        width_cm = 7.62
                        height_cm = 5.08
                        
                        # Add to image manager
                        image_id = image_manager.add_image(
                            blob=blob,
                            img_format=img_format,
                            width_cm=width_cm,
                            height_cm=height_cm,
                            original_href=img_path
                        )
                        
                        print(f"[ODT Extract] Stored {image_id} from {img_path}")
                else:
                    print(f"[ODT Extract] No images found in Pictures/")
        except Exception as e:
            print(f"[ODT Extract] Warning: Could not extract images: {e}")
        
        # Process all text elements (paragraphs, headings, AND tables) in document order
        # Phase 2: Also detect tables
        text_elements = []
        for elem in doc.text.childNodes:
            if hasattr(elem, 'qname'):
                if elem.qname == (odf_text.TEXTNS, 'p'):
                    text_elements.append(('p', elem))
                elif elem.qname == (odf_text.TEXTNS, 'h'):
                    text_elements.append(('h', elem))
                elif elem.qname[1] == 'table':  # Phase 2: Detect table:table
                    text_elements.append(('table', elem))
        
        for i, (elem_type, elem) in enumerate(text_elements):
            if elem_type == 'table':
                # Phase 2 - COM8: Extract table
                table_html = HTMLFormatMapper._extract_table(elem, table_manager)
                # Add as raw HTML segment - HTMLSegment requires all 4 parameters
                segments.append(HTMLSegment(
                    text=table_html,
                    css_class='',
                    tag_type='table',
                    attributes=FormatAttributes()  # Phase 2: Add empty attributes
                ))
            else:
                # Extract paragraph/heading (works for both P and H)
                # Phase 1: Pass image_manager for image marker insertion
                elem_segments = HTMLFormatMapper._extract_paragraph(elem, styles, css_manager, image_manager)
                
                # Skip adding BR if this element is empty (reduces excess blank lines)
                has_content = any(seg.text.strip() for seg in elem_segments if seg.tag_type != 'br')
                
                segments.extend(elem_segments)
        
        # Generate HTML structure
        html = HTMLFormatMapper._generate_html(segments, css_manager)
        
        # Decide storage strategy based on available RAM
        available_ram = psutil.virtual_memory().available
        css_manager_size = sys.getsizeof(css_manager.to_dict())
        
        # Use max 10% of available RAM
        if css_manager_size > available_ram * 0.1:
            # Save to temporary JSON file
            temp_file = tempfile.mktemp(suffix='_css_mapping_COM8.json')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(css_manager.to_dict(), f, indent=2)
            return html, temp_file, image_manager, table_manager  # Phase 2: Return table_manager
        else:
            # Keep in memory
            return html, css_manager, image_manager, table_manager  # Phase 2: Return table_manager
    
    @staticmethod
    def _build_style_dict(doc) -> Dict:
        """Build style dictionary for quick lookup."""
        styles = {}
        for style_element in doc.automaticstyles.childNodes + doc.styles.childNodes:
            if hasattr(style_element, 'getAttribute'):
                try:
                    style_name = style_element.getAttribute('name')
                    if style_name:
                        styles[style_name] = style_element
                except (ValueError, KeyError):
                    continue
        return styles
    
    @staticmethod
    def _extract_paragraph(para, styles: Dict, css_manager: CSSClassManager, 
                          image_manager: Optional['ODTImageManager'] = None) -> List[HTMLSegment]:
        """
        Extract paragraph with formatting and images.
        
        Phase 1 - COM8: Added image_manager parameter for image detection.
        """
        segments = []
        
        # Get paragraph style
        try:
            para_style_name = para.getAttribute('stylename')
        except (ValueError, KeyError):
            para_style_name = None
        
        para_style = styles.get(para_style_name) if para_style_name else None
        
        # Extract paragraph-level formatting
        para_fmt = HTMLFormatMapper._extract_paragraph_format(para, para_style, para_style_name)
        
        # Process paragraph content
        para_text = ""
        current_fmt = para_fmt
        
        for node in para.childNodes:
            if isinstance(node, ODFText):
                # Plain text node
                para_text += str(node)
            elif hasattr(node, 'qname') and node.qname[1] == 'span':
                # Get span format
                span_fmt = HTMLFormatMapper._extract_span_format(node, styles, para_fmt)
                
                # Process span content, handling line-breaks
                for child in node.childNodes:
                    if isinstance(child, ODFText):
                        # Text content
                        if para_text:
                            # Check if format changed
                            if current_fmt != span_fmt:
                                # Save accumulated text with previous format
                                css_class = css_manager.get_or_create_class(current_fmt)
                                tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                                segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                                para_text = ""
                        current_fmt = span_fmt
                        para_text += str(child)
                    elif hasattr(child, 'qname'):
                        elem_type = child.qname[1]
                        if elem_type == 'line-break':
                            # Save current text before line break
                            if para_text:
                                css_class = css_manager.get_or_create_class(current_fmt)
                                tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                                segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                                para_text = ""
                            # Add line-break segment (soft break within paragraph)
                            segments.append(HTMLSegment('\n', '', 'line-break', FormatAttributes()))
                            current_fmt = span_fmt  # Keep format after BR
                        elif elem_type == 'tab':
                            # Save current text before tab
                            if para_text:
                                css_class = css_manager.get_or_create_class(current_fmt)
                                tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                                segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                                para_text = ""
                            # Add tab segment
                            segments.append(HTMLSegment('', '', 'tab', FormatAttributes()))
                        elif elem_type == 's':
                            # Multiple spaces
                            try:
                                count = int(child.getAttribute('c'))
                            except:
                                count = 1
                            para_text += '&nbsp;' * count
            elif hasattr(node, 'qname') and node.qname[1] == 'line-break':
                # Line break within paragraph (soft break)
                if para_text:
                    # Save accumulated text
                    css_class = css_manager.get_or_create_class(current_fmt)
                    tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                    segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                    para_text = ""
                # Add line-break segment (soft break within paragraph)
                segments.append(HTMLSegment('', '', 'line-break', FormatAttributes()))
            elif hasattr(node, 'qname') and node.qname[1] in ['tab', 's']:
                # Tab or space
                if node.qname[1] == 'tab':
                    # Save current text before tab
                    if para_text:
                        css_class = css_manager.get_or_create_class(current_fmt)
                        tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                        segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                        para_text = ""
                    # Add tab segment
                    segments.append(HTMLSegment('', '', 'tab', FormatAttributes()))
                elif node.qname[1] == 's':
                    # Multiple spaces
                    try:
                        count = int(node.getAttribute('c'))
                    except:
                        count = 1
                    para_text += '&nbsp;' * count
            elif hasattr(node, 'qname') and node.qname[0] == odf_draw.DRAWNS and node.qname[1] == 'frame':
                # Phase 1 - COM8: Image frame detected
                if image_manager:
                    # Save accumulated text before image
                    if para_text:
                        css_class = css_manager.get_or_create_class(current_fmt)
                        tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                        segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                        para_text = ""
                    
                    # Find draw:image element inside frame
                    for child in node.childNodes:
                        if hasattr(child, 'qname') and child.qname[0] == odf_draw.DRAWNS and child.qname[1] == 'image':
                            try:
                                # Get image href
                                href = child.getAttribute('href')
                                if href:
                                    # Find corresponding image_id by href
                                    # The image was already stored during zip extraction
                                    # We need to match by href
                                    image_id = None
                                    for img_id, img_data in image_manager._images.items():
                                        if img_data.original_href == href:
                                            image_id = img_id
                                            break
                                    
                                    if image_id:
                                        # Insert image placeholder
                                        placeholder = image_manager.generate_placeholder(image_id)
                                        # Add as special segment (will be converted to HTML marker)
                                        segments.append(HTMLSegment(placeholder, '', 'image', FormatAttributes()))
                                        print(f"[ODT Extract] Inserted placeholder for {image_id} (href: {href})")
                                    else:
                                        print(f"[ODT Extract] Warning: Image href '{href}' not found in ImageManager")
                            except Exception as e:
                                print(f"[ODT Extract] Error processing image: {e}")
                            break  # Only process first image in frame
        
        # Save remaining text
        if para_text:
            css_class = css_manager.get_or_create_class(current_fmt)
            tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
            segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
        
        # Add paragraph separator
        segments.append(HTMLSegment('\n', '', 'br', FormatAttributes()))
        
        return segments
    
    @staticmethod
    def _extract_table(table_elem, table_manager: 'ODTTableManager') -> str:
        """
        Extract table from ODF element and store in TableManager.
        
        Phase 2 - COM8: Table extraction for ODT files.
        
        Args:
            table_elem: odf.table.Table element
            table_manager: ODTTableManager to store table
        
        Returns:
            HTML table string with data-table marker
        """
        from odf import table as odf_table
        from odf.text import P as TextP
        
        # Get table name attribute
        table_name = table_elem.getAttribute('name') if hasattr(table_elem, 'getAttribute') else None
        
        # Extract rows
        rows_elements = []
        for child in table_elem.childNodes:
            if hasattr(child, 'qname') and child.qname[1] == 'table-row':
                rows_elements.append(child)
        
        rows = len(rows_elements)
        
        # Determine columns (from first row)
        cols = 0
        if rows > 0:
            for child in rows_elements[0].childNodes:
                if hasattr(child, 'qname') and child.qname[1] == 'table-cell':
                    cols += 1
        
        # Extract cell text
        cells = []
        for row_elem in rows_elements:
            row_cells = []
            
            for child in row_elem.childNodes:
                if hasattr(child, 'qname') and child.qname[1] == 'table-cell':
                    # Extract text from paragraphs in cell
                    cell_paragraphs = []
                    for cell_child in child.childNodes:
                        if hasattr(cell_child, 'qname') and cell_child.qname[1] == 'p':
                            # Get text content from paragraph
                            para_text = HTMLFormatMapper._get_text_content(cell_child)
                            if para_text.strip():
                                cell_paragraphs.append(para_text)
                    
                    # Join paragraphs with space
                    cell_text = ' '.join(cell_paragraphs)
                    row_cells.append(cell_text)
            
            # Pad row if needed (in case of irregular tables)
            while len(row_cells) < cols:
                row_cells.append('')
            
            cells.append(row_cells)
        
        # Store in manager
        if rows > 0 and cols > 0:
            table_id = table_manager.add_table(
                rows=rows,
                cols=cols,
                cells=cells,
                name=table_name
            )
            
            # Return HTML
            table_data = table_manager.get_table(table_id)
            return table_data.to_html()
        else:
            # Empty table
            return '<table></table>'
    
    @staticmethod
    def _get_text_content(element) -> str:
        """
        Recursively extract text content from ODF element.
        
        Phase 2 - COM8: Helper for table cell text extraction.
        
        Args:
            element: ODF element
        
        Returns:
            Plain text content
        """
        text_parts = []
        
        if hasattr(element, 'data'):
            # Text node
            text_parts.append(element.data)
        
        if hasattr(element, 'childNodes'):
            for child in element.childNodes:
                text_parts.append(HTMLFormatMapper._get_text_content(child))
        
        return ''.join(text_parts)
    
    @staticmethod
    def _extract_paragraph_format(para, para_style, para_style_name: Optional[str]) -> FormatAttributes:
        """Extract paragraph-level formatting attributes."""
        fmt = FormatAttributes()
        
        # Check for heading
        if para_style_name and ('heading' in para_style_name.lower() or 'head' in para_style_name.lower()):
            match = re.search(r'[_\s](\d)(?:[_\s]|$)', para_style_name)
            if match:
                level = int(match.group(1))
                if 1 <= level <= 6:
                    fmt.heading_level = level
        
        # Check for list item
        if hasattr(para, 'parentNode') and para.parentNode is not None:
            parent = para.parentNode
            if hasattr(parent, 'qname') and parent.qname[1] == 'list-item':
                fmt.is_list_item = True
                fmt.list_type = 'B'  # Default bullet
                fmt.list_level = 1
        
        # Extract paragraph properties
        if para_style:
            for prop in para_style.getElementsByType(odf_style.ParagraphProperties):
                try:
                    # Alignment
                    text_align = prop.getAttribute('textalign')
                    if text_align:
                        align_map = {'start': 'L', 'center': 'C', 'end': 'R', 'justify': 'J'}
                        fmt.alignment = align_map.get(text_align, 'L')
                except (ValueError, KeyError):
                    pass
                
                try:
                    # Line height
                    line_height = prop.getAttribute('lineheight')
                    if line_height and '%' in str(line_height):
                        spacing = float(str(line_height).replace('%', '')) / 100.0
                        fmt.line_spacing = spacing
                except (ValueError, KeyError):
                    pass
        
        return fmt
    
    @staticmethod
    def _extract_span_format(span, styles: Dict, para_fmt: FormatAttributes) -> FormatAttributes:
        """Extract span formatting only (not text content)."""
        # Start with paragraph format as base
        fmt = FormatAttributes(
            alignment=para_fmt.alignment,
            line_spacing=para_fmt.line_spacing,
            heading_level=para_fmt.heading_level,
            is_list_item=para_fmt.is_list_item,
            list_type=para_fmt.list_type,
            list_level=para_fmt.list_level
        )
        
        # Get span style
        try:
            span_style_name = span.getAttribute('stylename')
        except (ValueError, KeyError):
            span_style_name = None
        
        span_style = styles.get(span_style_name) if span_style_name else None
        
        # Extract character formatting
        if span_style:
            for text_prop in span_style.getElementsByType(odf_style.TextProperties):
                try:
                    if text_prop.getAttribute('fontweight') == 'bold':
                        fmt.bold = True
                except (ValueError, KeyError):
                    pass
                
                try:
                    if text_prop.getAttribute('fontstyle') == 'italic':
                        fmt.italic = True
                except (ValueError, KeyError):
                    pass
                
                try:
                    underline = text_prop.getAttribute('textunderlinestyle')
                    if underline and underline != 'none':
                        fmt.underline = True
                except (ValueError, KeyError):
                    pass
                
                try:
                    strike = text_prop.getAttribute('textlinethroughstyle')
                    if strike and strike != 'none':
                        fmt.strikethrough = True
                except (ValueError, KeyError):
                    pass
                
                try:
                    font_name = text_prop.getAttribute('fontfamily')
                    if font_name:
                        fmt.font_family = font_name.strip("'\"")
                except (ValueError, KeyError):
                    pass
                
                try:
                    font_size = text_prop.getAttribute('fontsize')
                    if font_size:
                        # Parse size (e.g., "12pt" → 12)
                        size_str = str(font_size).replace('pt', '')
                        fmt.font_size = int(float(size_str))
                except (ValueError, KeyError):
                    pass
                
                try:
                    color = text_prop.getAttribute('color')
                    if color:
                        # Convert #RRGGBB to RRGGBB
                        fmt.font_color = color.lstrip('#')
                except (ValueError, KeyError):
                    pass
        
        return fmt
    
    @staticmethod
    def _extract_span(span, styles: Dict, para_fmt: FormatAttributes) -> Tuple[str, FormatAttributes]:
        """Extract span text and formatting."""
        fmt = HTMLFormatMapper._extract_span_format(span, styles, para_fmt)
        
        # Extract text content (note: does NOT handle line-breaks inside spans!)
        text = ""
        for node in span.childNodes:
            if isinstance(node, ODFText):
                text += str(node)
            elif hasattr(node, 'qname') and node.qname[1] == 'tab':
                text += '&#9;'
            elif hasattr(node, 'qname') and node.qname[1] == 's':
                try:
                    count = int(node.getAttribute('c'))
                except:
                    count = 1
                text += '&nbsp;' * count
        
        return text, fmt
    
    @staticmethod
    def _decide_tag_type(text: str, fmt: FormatAttributes) -> str:
        """
        Decide whether to use <div> or <span> based on context.
        
        Rules:
        - <div>: Text blocks (multiple lines, paragraphs, headings)
        - <span>: Inline text (single line, paragraph part)
        """
        # Headings are always div
        if fmt.heading_level:
            return 'div'
        
        # List items are div
        if fmt.is_list_item:
            return 'div'
        
        # Multiple newlines = block
        if '\n' in text.strip():
            return 'div'
        
        # Paragraph alignment suggests block
        if fmt.alignment:
            return 'div'
        
        # Default to span for inline content
        return 'span'
    
    @staticmethod
    def _generate_html(segments: List[HTMLSegment], css_manager: CSSClassManager) -> str:
        """Generate complete HTML document structure."""
        # Build HTML body
        body_parts = []
        
        for i, segment in enumerate(segments):
            if segment.tag_type == 'br':
                # Hard break (paragraph separator)
                body_parts.append('<br class="brk1">')
            elif segment.tag_type == 'line-break':
                # Soft break (line break within paragraph)
                body_parts.append('<br class="brk2">')
            elif segment.tag_type == 'tab':
                # Tab character - use empty span with data attribute
                body_parts.append('<span data-tab="1"></span>')
            elif segment.tag_type == 'image':
                # Phase 1 - COM8: Image placeholder (already in correct format)
                body_parts.append(segment.text)  # text contains: <span data-image="IMG001"></span>
            elif segment.tag_type == 'table':
                # Phase 2 - COM8: Table (already in HTML format with data-table marker)
                body_parts.append(segment.text)  # text contains: <table data-table="TBL001">...</table>
            elif segment.css_class:
                # Escape HTML special characters in text
                escaped_text = (segment.text
                    .replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;'))
                
                # But preserve our HTML entities
                escaped_text = (escaped_text
                    .replace('&amp;#9;', '&#9;')
                    .replace('&amp;#10;', '&#10;')
                    .replace('&amp;nbsp;', '&nbsp;'))
                
                span_html = f'<{segment.tag_type} class="{segment.css_class}">{escaped_text}</{segment.tag_type}>'
                body_parts.append(span_html)
                
                # Add space after span if next segment is also a span (prevent word merging in Google Translate)
                if i + 1 < len(segments) and segments[i + 1].tag_type not in ('br', 'line-break') and segments[i + 1].css_class:
                    body_parts.append(' ')
            else:
                # No formatting
                body_parts.append(segment.text)
        
        body_html = '\n'.join(body_parts)
        
        # Generate complete HTML document
        css = css_manager.generate_css()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="generator" content="Clarify HTML Format Mapper">
    <meta name="odt-translation" content="true">
    <style>
{css}
    </style>
</head>
<body>
{body_html}
</body>
</html>"""
        
        return html


# ============================================================================
# Whitespace Protection (HTML Entities)
# ============================================================================

def protect_special_whitespace(html: str) -> str:
    """
    Convert special whitespace to HTML entities before translation.
    
    Args:
        html: HTML text
        
    Returns:
        HTML with protected whitespace
    """
    # Tab → &#9;
    html = html.replace('\t', '&#9;')
    
    # Newline → &#10; (but preserve inside tags)
    # Note: This is complex, for now trust HTML structure
    
    return html


def restore_special_whitespace(html: str) -> str:
    """
    Restore HTML entities back to whitespace after translation.
    
    Args:
        html: Translated HTML with entities
        
    Returns:
        HTML with restored whitespace
    """
    # &#9; → Tab
    html = html.replace('&#9;', '\t')
    
    # &#10; → Newline
    html = html.replace('&#10;', '\n')
    
    return html


# ============================================================================
# ODT Creation from HTML
# ============================================================================

def create_odt_from_html(html: str, css_manager_or_path, output_path: str, 
                         image_manager: Optional['ODTImageManager'] = None,
                         table_manager: Optional['ODTTableManager'] = None):
    """
    Create ODT file from translated HTML.
    
    Phase 1 - COM8: Added image_manager parameter for image restoration.
    Phase 2 - COM8: Added table_manager parameter for table restoration.
    
    Args:
        html: Translated HTML document
        css_manager_or_path: CSSClassManager object or path to JSON file
        output_path: Where to save ODT file
        image_manager: Optional ODTImageManager with images to restore
        table_manager: Optional ODTTableManager with tables to restore
    """
    from html.parser import HTMLParser
    from odf.opendocument import OpenDocumentText
    from odf.style import Style, TextProperties, ParagraphProperties
    from odf.text import P, Span
    
    # Load CSS manager
    if isinstance(css_manager_or_path, str):
        # Load from JSON file
        with open(css_manager_or_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        css_manager = CSSClassManager.from_dict(data)
    else:
        css_manager = css_manager_or_path
    
    # Parse HTML
    parser = HTMLToODTParser(css_manager, image_manager, table_manager)  # Phase 2: Pass table_manager
    parser.feed(html)
    
    # Create ODT document
    doc = OpenDocumentText()
    
    # Create styles from CSS classes
    styles_created = {}
    for class_name, fmt in css_manager.class_to_format.items():
        # Create text style
        style = Style(name=f"Style_{class_name}", family="text")
        text_props = TextProperties()
        
        if fmt.bold:
            text_props.setAttribute("fontweight", "bold")
        if fmt.italic:
            text_props.setAttribute("fontstyle", "italic")
        if fmt.underline:
            text_props.setAttribute("textunderlinestyle", "solid")
            text_props.setAttribute("textunderlinewidth", "auto")
        if fmt.strikethrough:
            text_props.setAttribute("textlinethroughstyle", "solid")
        if fmt.font_family:
            text_props.setAttribute("fontfamily", fmt.font_family)
        if fmt.font_size:
            text_props.setAttribute("fontsize", f"{fmt.font_size}pt")
        if fmt.font_color:
            text_props.setAttribute("color", f"#{fmt.font_color}")
        if fmt.highlight_color:
            text_props.setAttribute("backgroundcolor", f"#{fmt.highlight_color}")
        
        style.addElement(text_props)
        doc.automaticstyles.addElement(style)
        styles_created[class_name] = style
        
        # Create paragraph style if needed (for alignment, spacing, etc.)
        if fmt.alignment or fmt.line_spacing or fmt.indent_first or fmt.indent_left or fmt.indent_right:
            para_style = Style(name=f"ParaStyle_{class_name}", family="paragraph")
            para_props = ParagraphProperties()
            
            if fmt.alignment:
                align_map = {'L': 'left', 'C': 'center', 'R': 'right', 'J': 'justify'}
                para_props.setAttribute("textalign", align_map.get(fmt.alignment, 'left'))
            if fmt.line_spacing:
                para_props.setAttribute("lineheight", f"{int(fmt.line_spacing * 100)}%")
            if fmt.indent_first:
                para_props.setAttribute("textindent", f"{fmt.indent_first * 0.0353:.2f}cm")
            if fmt.indent_left:
                para_props.setAttribute("marginleft", f"{fmt.indent_left * 0.0353:.2f}cm")
            if fmt.indent_right:
                para_props.setAttribute("marginright", f"{fmt.indent_right * 0.0353:.2f}cm")
            
            para_style.addElement(para_props)
            doc.automaticstyles.addElement(para_style)
            styles_created[f"para_{class_name}"] = para_style
    
    # Build ODT content from parsed segments
    current_paragraph = None
    
    for segment in parser.segments:
        if segment['type'] == 'br':
            # Hard break - end current paragraph and start new one
            if current_paragraph is not None:
                doc.text.addElement(current_paragraph)
                current_paragraph = None
            else:
                # Consecutive BR = empty paragraph
                empty_para = P()
                doc.text.addElement(empty_para)
        
        elif segment['type'] == 'line-break':
            # Soft break - add line-break element within current paragraph
            if current_paragraph is None:
                current_paragraph = P()
            
            # Add line-break element
            from odf.text import LineBreak
            current_paragraph.addElement(LineBreak())
        
        elif segment['type'] == 'tab':
            # Tab character - add tab element within current paragraph
            if current_paragraph is None:
                current_paragraph = P()
            
            # Add tab element
            from odf.text import Tab
            current_paragraph.addElement(Tab())
        
        elif segment['type'] == 'text':
            # Add text to current or new paragraph
            if current_paragraph is None:
                current_paragraph = P()
            
            text_content = segment['text']
            css_class = segment.get('class')
            
            if css_class and css_class in styles_created:
                # Apply style
                span = Span(stylename=styles_created[css_class], text=text_content)
                current_paragraph.addElement(span)
            else:
                # Plain text
                current_paragraph.addText(text_content)
        
        elif segment['type'] == 'image':
            # Phase 1 - COM8: Handle image restoration
            if current_paragraph is None:
                current_paragraph = P()
            
            image_data = segment['image_data']
            
            # Create draw:frame and draw:image elements
            from odf.draw import Frame, Image
            
            # Convert dimensions back to ODF format (cm)
            width_cm = f"{image_data.width_cm:.2f}cm"
            height_cm = f"{image_data.height_cm:.2f}cm"
            
            # Create frame
            frame = Frame(width=width_cm, height=height_cm, anchortype="as-char")
            
            # Create image reference (will be written to Pictures/ later)
            image_href = f"Pictures/{image_data.image_id}.{image_data.format}"
            img = Image(href=image_href)
            
            frame.addElement(img)
            current_paragraph.addElement(frame)
        
        elif segment['type'] == 'table':
            # Phase 2 - COM8: Handle table restoration
            if current_paragraph is not None:
                doc.text.addElement(current_paragraph)
                current_paragraph = None
            
            table_data = segment['table_data']
            
            # Create ODF table
            from odf.table import Table, TableColumn, TableRow, TableCell
            from odf.text import P as TableP
            
            odt_table = Table(name=table_data.name or f"Table{table_data.table_id}")
            
            # Add column definitions
            for _ in range(table_data.cols):
                odt_table.addElement(TableColumn())
            
            # Add rows and cells
            for row_idx in range(table_data.rows):
                row = TableRow()
                for col_idx in range(table_data.cols):
                    cell = TableCell()
                    cell_text = table_data.get_cell(row_idx, col_idx)
                    p = TableP(text=cell_text)
                    cell.addElement(p)
                    row.addElement(cell)
                odt_table.addElement(row)
            
            doc.text.addElement(odt_table)
    
    # Add final paragraph if exists
    if current_paragraph is not None:
        doc.text.addElement(current_paragraph)
    
    # Save ODT
    doc.save(output_path)
    
    # Phase 1 - COM8: Write images to Pictures/ folder in ODT zip
    if image_manager and image_manager.get_statistics()['total_images'] > 0:
        import zipfile
        import tempfile
        import shutil
        
        # Create temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract ODT to temp dir
            temp_odt = os.path.join(tmpdir, 'temp.odt')
            shutil.copy(output_path, temp_odt)
            
            # Open ODT as zip and add images
            with zipfile.ZipFile(temp_odt, 'a') as odt_zip:
                # Create Pictures/ folder and write images
                for image_id, img_data in image_manager._images.items():
                    image_filename = f"Pictures/{image_id}.{img_data.format}"
                    odt_zip.writestr(image_filename, img_data.blob)
            
            # Replace original with updated ODT
            shutil.move(temp_odt, output_path)


class HTMLToODTParser(HTMLParser):
    """Parse HTML and extract segments for ODT creation.
    
    Phase 1 - COM8: Extended to handle image restoration from data-image attributes.
    Phase 2 - COM8: Extended to handle table restoration from data-table attributes.
    """
    
    def __init__(self, css_manager: CSSClassManager, 
                 image_manager: Optional['ODTImageManager'] = None,
                 table_manager: Optional['ODTTableManager'] = None):
        super().__init__()
        self.css_manager = css_manager
        self.image_manager = image_manager
        self.table_manager = table_manager  # Phase 2: Store table manager
        self.segments = []
        self.current_tag = None
        self.current_class = None
        self.in_table = False  # Phase 2: Track if parsing table
        self.current_table_id = None  # Phase 2: Current table being parsed
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags.
        
        Phase 1 - COM8: Added detection for data-image attributes (image markers).
        Phase 2 - COM8: Added detection for data-table attributes (table markers).
        """
        self.current_tag = tag
        
        # Phase 2: Handle table tags
        if tag == 'table':
            for attr, value in attrs:
                if attr == 'data-table' and self.table_manager:
                    self.in_table = True
                    self.current_table_id = value
                    # Add table segment
                    table_data = self.table_manager.get_table(value)
                    if table_data:
                        self.segments.append({
                            'type': 'table',
                            'table_id': value,
                            'table_data': table_data
                        })
                    return
        
        # Phase 2: Skip content inside tables (handled by table segment)
        if self.in_table and tag in ['tr', 'td', 'th', 'tbody', 'thead']:
            return
        
        # Handle self-closing BR tag immediately
        if tag == 'br':
            # Check class attribute to distinguish paragraph vs line break
            break_type = 'br'  # Default to paragraph break (brk1)
            for attr, value in attrs:
                if attr == 'class' and value == 'brk2':
                    break_type = 'line-break'
                    break
            self.segments.append({'type': break_type})
            return
        
        # Handle span tags - check for tab marker AND image marker
        if tag == 'span':
            # Check for data-tab attribute (tab marker)
            for attr, value in attrs:
                if attr == 'data-tab':
                    self.segments.append({'type': 'tab'})
                    return
                # Phase 1 - COM8: Check for data-image attribute (image marker)
                if attr == 'data-image' and self.image_manager:
                    # Extract image ID and add to segments
                    image_id = value
                    image_data = self.image_manager.get_image(image_id)
                    if image_data:
                        self.segments.append({
                            'type': 'image',
                            'image_id': image_id,
                            'image_data': image_data
                        })
                    return
        
        # Extract class attribute for regular spans
        for attr, value in attrs:
            if attr == 'class':
                self.current_class = value
                break
    
    def handle_endtag(self, tag):
        """Handle closing tags.
        
        Phase 2 - COM8: Added table state tracking.
        """
        # Phase 2: Reset table state
        if tag == 'table':
            self.in_table = False
            self.current_table_id = None
            return
        
        self.current_tag = None
        self.current_class = None
    
    def handle_data(self, data):
        """Handle text content."""
        # Skip whitespace in head/style/title
        if self.current_tag in ['style', 'head', 'title']:
            return
        
        # Keep whitespace-only data if it contains actual spaces (for separation between spans)
        # But skip if it's ONLY newlines (HTML formatting)
        if not data.strip():
            # If contains space or tab, preserve it (between spans)
            if ' ' in data or '\t' in data:
                self.segments.append({
                    'type': 'text',
                    'text': ' ',  # Normalize to single space
                    'class': None
                })
            return
        
        # Decode HTML entities back to characters
        import html
        text = html.unescape(data)
        
        self.segments.append({
            'type': 'text',
            'text': text,
            'class': self.current_class
        })
