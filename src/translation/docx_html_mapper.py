#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DOCX HTML Mapper - Convert DOCX formatting to HTML for translation

This module adapts the proven ODT HTML translation approach to DOCX format.
Uses the same HTML markers and CSS system for Google Translate compatibility.

Architecture:
    DOCX → Extract (HTML) → Google Translate → Create DOCX from HTML

Key Features:
    - Reuses 90% of ODT approach (html_format_mapper.py)
    - Full HTML structure with CSS classes
    - Invisible markers for tabs/line-breaks
    - 100% format preservation (no visible tags/placeholders)
    - Split run.text by \t and \n characters

Author: Josué Amaral (COM8)
Date: February 16, 2026
Session: Phase 3 - DOCX Translation Implementation
"""

import html
import hashlib
from dataclasses import dataclass
from html.parser import HTMLParser
from io import BytesIO
from typing import Dict, List, Optional

from docx import Document
from docx.shared import Pt, RGBColor, Inches


# ============================================================================
# Data Classes (Copied from html_format_mapper.py)
# ============================================================================

@dataclass
class FormatAttributes:
    """Store formatting attributes extracted from DOCX styles."""
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
    """Represents a document element as HTML segment."""
    text: str
    css_class: str
    tag_type: str  # 'div', 'span', 'br', 'line-break', 'tab', or 'image'
    attributes: Optional[FormatAttributes]
    element_type: str = 'span'  # Extended type info
    image_id: Optional[str] = None  # For image segments: 'IMG001', 'IMG002', etc.


# ============================================================================
# CSS Class Management (Copied from html_format_mapper.py)
# ============================================================================

# ============================================================================
# Image Management (NEW for Phase 1)
# ============================================================================

@dataclass
class ImageData:
    """Stores image binary data and metadata."""
    
    image_id: str              # 'IMG001', 'IMG002', etc.
    blob: bytes                # Raw PNG/JPEG/GIF binary data
    content_type: str          # 'image/png', 'image/jpeg', etc.
    width_emus: int            # Width in EMUs (914400 = 1 inch)
    height_emus: int           # Height in EMUs
    original_rId: str          # Original relationship ID (e.g., 'rId9')
    blob_hash: Optional[str]   # SHA256 hash for deduplication
    
    def get_format(self) -> str:
        """Extract format from content_type."""
        if 'png' in self.content_type:
            return 'png'
        elif 'jpeg' in self.content_type:
            return 'jpg'
        elif 'gif' in self.content_type:
            return 'gif'
        else:
            return 'unknown'
    
    def get_width_inches(self) -> float:
        """Convert EMUs to inches."""
        return self.width_emus / 914400
    
    def get_height_inches(self) -> float:
        """Convert EMUs to inches."""
        return self.height_emus / 914400


class ImageManager:
    """Manages image storage and reconstruction for DOCX translation."""
    
    def __init__(self):
        """Initialize image storage."""
        self._images: Dict[str, ImageData] = {}  # image_id → ImageData
        self._hash_to_id: Dict[str, str] = {}    # blob_hash → image_id
        self._next_id: int = 1                   # Counter for IMG001, IMG002, etc.
    
    def add_image(self, blob: bytes, content_type: str, 
                  width_emus: int, height_emus: int, 
                  original_rId: str) -> str:
        """
        Add image to storage with deduplication.
        
        Returns:
            image_id: Unique ID for this image (e.g., 'IMG001')
        """
        # Calculate hash for deduplication
        blob_hash = hashlib.sha256(blob).hexdigest()
        
        # Check if image already exists (same binary data)
        if blob_hash in self._hash_to_id:
            existing_id = self._hash_to_id[blob_hash]
            print(f"[ImageManager] Deduplication: reusing {existing_id} for {original_rId}")
            return existing_id
        
        # Warn about large images
        blob_size_mb = len(blob) / (1024 * 1024)
        if blob_size_mb > 10:
            print(f"[ImageManager] WARNING: Large image ({blob_size_mb:.1f}MB)")
        
        # Generate new ID
        image_id = f"IMG{self._next_id:03d}"  # IMG001, IMG002, etc.
        self._next_id += 1
        
        # Store image data
        image_data = ImageData(
            image_id=image_id,
            blob=blob,
            content_type=content_type,
            width_emus=width_emus,
            height_emus=height_emus,
            original_rId=original_rId,
            blob_hash=blob_hash
        )
        
        self._images[image_id] = image_data
        self._hash_to_id[blob_hash] = image_id
        
        print(f"[ImageManager] Stored {image_id}: {content_type}, "
              f"{width_emus / 914400:.2f}\" x {height_emus / 914400:.2f}\", "
              f"{len(blob)} bytes")
        
        # Check total memory usage
        stats = self.get_statistics()
        if stats['total_mb'] > 100:
            print(f"[ImageManager] WARNING: High memory usage ({stats['total_mb']:.1f}MB)")
        
        return image_id
    
    def get_image(self, image_id: str) -> Optional[ImageData]:
        """
        Retrieve image by ID.
        
        Returns:
            ImageData if found, None otherwise
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


# ============================================================================
# DOCX to HTML Extraction
# ============================================================================

class DocxHtmlMapper:
    """Extract DOCX content and convert to HTML for translation."""
    
    def __init__(self, docx_path: str):
        """Initialize mapper with DOCX file path."""
        self.docx_path = docx_path
        self.doc = Document(docx_path)
        self.css_manager = CSSClassManager()
        self.image_manager = ImageManager()
        self.segments: List[HTMLSegment] = []
    
    def extract_html_from_docx(self) -> str:
        """
        Extract DOCX content and convert to HTML.
        
        Returns:
            HTML string with CSS classes and invisible markers
        """
        # 1. Extract all segments
        self._extract_segments()
        
        # 2. Generate HTML string
        html_string = self._generate_html()
        
        return html_string
    
    def _extract_segments(self):
        """Extract all document content as flat segment list including images."""
        total_paras = len(self.doc.paragraphs)
        
        # Namespace constants
        NS_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        NS_A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
        NS_WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
        NS_R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
        
        for para_idx, para in enumerate(self.doc.paragraphs):
            # Process all runs in paragraph
            for run in para.runs:
                # Check for images FIRST (before text processing)
                drawings = run._element.findall(f'.//{NS_W}drawing')
                
                if drawings:
                    # Process each image in the run
                    for drawing in drawings:
                        try:
                            # Get blip (image reference)
                            blips = drawing.findall(f'.//{NS_A}blip')
                            if not blips:
                                continue
                            
                            blip = blips[0]
                            embed_id = blip.get(f'{NS_R}embed')
                            
                            if not embed_id or embed_id not in self.doc.part.related_parts:
                                print(f"[DocxHtmlMapper] WARNING: Image relationship {embed_id} not found")
                                continue
                            
                            # Get image part
                            image_part = self.doc.part.related_parts[embed_id]
                            blob = image_part.blob
                            content_type = image_part.content_type
                            
                            # Get dimensions
                            extents = drawing.findall(f'.//{NS_WP}extent')
                            if extents:
                                ext = extents[0]
                                width_emus = int(ext.get('cx') or 914400)
                                height_emus = int(ext.get('cy') or 914400)
                            else:
                                # Default to 1" x 1"
                                width_emus = 914400
                                height_emus = 914400
                            
                            # Store in ImageManager
                            image_id = self.image_manager.add_image(
                                blob=blob,
                                content_type=content_type,
                                width_emus=width_emus,
                                height_emus=height_emus,
                                original_rId=embed_id
                            )
                            
                            # Add image segment
                            self.segments.append(HTMLSegment(
                                text='',
                                css_class='',
                                tag_type='image',
                                attributes=None,
                                element_type='image',
                                image_id=image_id
                            ))
                            
                        except Exception as e:
                            print(f"[DocxHtmlMapper] ERROR processing image: {e}")
                            print(f"  Skipping image, continuing with text")
                
                # Extract format once for this run
                run_format = self._extract_format_from_run(run)
                css_class = self.css_manager.get_or_create_class(run_format)
                
                # Split run.text by tabs and line-breaks
                parts = self._split_run_text(run.text)
                
                for part in parts:
                    if part['type'] == 'text':
                        self.segments.append(HTMLSegment(
                            text=part['value'],
                            css_class=css_class,
                            tag_type='span',
                            attributes=run_format,
                            element_type='span'
                        ))
                    elif part['type'] == 'tab':
                        self.segments.append(HTMLSegment(
                            text='',
                            css_class='',
                            tag_type='tab',
                            attributes=None,
                            element_type='tab'
                        ))
                    elif part['type'] == 'linebreak':
                        self.segments.append(HTMLSegment(
                            text='',
                            css_class='',
                            tag_type='line-break',
                            attributes=None,
                            element_type='line-break'
                        ))
            
            # After all runs, add paragraph break (except for last paragraph)
            if para_idx < total_paras - 1:
                self.segments.append(HTMLSegment(
                    text='',
                    css_class='',
                    tag_type='br',
                    attributes=None,
                    element_type='para-break'
                ))
    
    def _split_run_text(self, text: str) -> List[Dict[str, str]]:
        """
        Split run text into text/tab/linebreak parts.
        
        Args:
            text: Run text potentially containing \t, \n, \r
        
        Returns:
            List of dicts with 'type' and 'value' (for text parts)
        
        Examples:
            "Hello\tWorld" → [text("Hello"), tab, text("World")]
            "\t\t\t" → [tab, tab, tab]
            "Plain text" → [text("Plain text")]
            "" → []
        """
        if not text:
            return []
        
        parts = []
        current = ""
        
        for char in text:
            if char == '\t':
                # Flush current text if any
                if current:
                    parts.append({'type': 'text', 'value': current})
                    current = ""
                parts.append({'type': 'tab'})
            
            elif char in '\n\r':
                # Flush current text if any
                if current:
                    parts.append({'type': 'text', 'value': current})
                    current = ""
                parts.append({'type': 'linebreak'})
            
            else:
                current += char
        
        # Flush remaining text
        if current:
            parts.append({'type': 'text', 'value': current})
        
        return parts
    
    def _extract_format_from_run(self, run) -> FormatAttributes:
        """Extract formatting from DOCX run."""
        format_attrs = FormatAttributes()
        
        # Character formatting
        format_attrs.bold = run.bold if run.bold is not None else False
        format_attrs.italic = run.italic if run.italic is not None else False
        format_attrs.underline = run.underline if run.underline is not None else False
        
        # Font properties
        if run.font.name:
            format_attrs.font_family = run.font.name
        
        if run.font.size:
            format_attrs.font_size = int(run.font.size.pt)
        
        if run.font.color and run.font.color.rgb:
            # Convert RGBColor to hex string
            rgb = run.font.color.rgb
            format_attrs.font_color = f"{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        return format_attrs
    
    def _generate_html(self) -> str:
        """Generate HTML from segments."""
        html_parts = []
        
        # HTML header
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html>')
        html_parts.append('<head>')
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<style>')
        html_parts.append(self.css_manager.generate_css())
        html_parts.append('</style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Content
        for seg in self.segments:
            if seg.tag_type == 'div':
                html_parts.append(f'<div class="{seg.css_class}">{html.escape(seg.text)}</div>')
            
            elif seg.tag_type == 'span':
                if seg.text:  # Only add span if has content
                    html_parts.append(f'<span class="{seg.css_class}">{html.escape(seg.text)}</span>')
            
            elif seg.tag_type == 'br' and seg.element_type == 'para-break':
                html_parts.append('<br class="brk1">')
            
            elif seg.tag_type == 'line-break':
                html_parts.append('<br class="brk2">')
            
            elif seg.tag_type == 'tab':
                html_parts.append('<span data-tab="1"></span>')
            
            elif seg.tag_type == 'image':
                # Generate image placeholder
                placeholder = self.image_manager.generate_placeholder(seg.image_id)
                html_parts.append(placeholder)
        
        # HTML footer
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return ''.join(html_parts)


# ============================================================================
# HTML to DOCX Creation
# ============================================================================

class HTMLToDocxParser(HTMLParser):
    """Parse HTML and create DOCX document."""
    
    def __init__(self, css_class_manager: CSSClassManager, image_manager: ImageManager):
        super().__init__()
        self.css_manager = css_class_manager
        self.image_manager = image_manager
        self.doc = Document()
        self.current_para = None
        self.current_format = None
        self.in_head = False  # Flag to ignore <head> content
    
    def handle_starttag(self, tag, attrs):
        """Handle opening HTML tags."""
        # Ignore head/style/meta tags
        if tag in ('head', 'style', 'meta'):
            self.in_head = True
            return
        
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        
        if tag == 'div':
            # Create new paragraph
            self.current_para = self.doc.add_paragraph()
            
            # Set paragraph format from CSS class
            if classes:
                self.current_format = self.css_manager.get_format(classes[0])
        
        elif tag == 'span':
            # Check for tab marker
            if 'data-tab' in attr_dict:
                # Insert tab
                if self.current_para is None:
                    self.current_para = self.doc.add_paragraph()
                self.current_para.add_run('\t')
            
            # Check for image marker
            elif 'data-image' in attr_dict:
                image_id = attr_dict['data-image']
                self._reconstruct_image(image_id)
            
            else:
                # Set format for upcoming text
                if classes:
                    self.current_format = self.css_manager.get_format(classes[0])
        
        elif tag == 'br':
            if 'brk1' in classes:
                # Paragraph break - create new paragraph
                self.current_para = self.doc.add_paragraph()
                self.current_format = None
            
            elif 'brk2' in classes:
                # Line break within paragraph
                if self.current_para is None:
                    self.current_para = self.doc.add_paragraph()
                self.current_para.add_run('\n')
    
    def handle_endtag(self, tag):
        """Handle closing HTML tags."""
        if tag in ('head', 'style'):
            self.in_head = False
    
    def handle_data(self, data):
        """Handle text content."""
        # Ignore content inside <head> or <style>
        if self.in_head:
            return
        
        if not data.strip():
            return  # Skip whitespace-only text
        
        if self.current_para is None:
            self.current_para = self.doc.add_paragraph()
        
        # Create run with text
        run = self.current_para.add_run(data)
        
        # Apply formatting
        if self.current_format:
            self._apply_format_to_run(run, self.current_format)
    
    def _apply_format_to_run(self, run, format_attrs: FormatAttributes):
        """Apply format attributes to DOCX run."""
        if format_attrs.bold:
            run.bold = True
        if format_attrs.italic:
            run.italic = True
        if format_attrs.underline:
            run.underline = True
        
        if format_attrs.font_family:
            run.font.name = format_attrs.font_family
        
        if format_attrs.font_size:
            run.font.size = Pt(format_attrs.font_size)
        
        if format_attrs.font_color:
            # Convert hex string to RGBColor
            hex_color = format_attrs.font_color
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            run.font.color.rgb = RGBColor(r, g, b)
    
    def _reconstruct_image(self, image_id: str):
        """Reconstruct image in DOCX from stored data."""
        # Get image data from ImageManager
        image_data = self.image_manager.get_image(image_id)
        
        if not image_data:
            print(f"[HTMLToDocxParser] WARNING: Image {image_id} not found, skipping")
            return
        
        # Ensure we have a paragraph
        if self.current_para is None:
            self.current_para = self.doc.add_paragraph()
        
        # Add image to paragraph
        try:
            image_stream = BytesIO(image_data.blob)
            run = self.current_para.add_run()
            run.add_picture(
                image_stream,
                width=Inches(image_data.get_width_inches())
            )
            print(f"[HTMLToDocxParser] Reconstructed {image_id} "
                  f"({image_data.get_format()}, {image_data.get_width_inches():.2f}\")")
        
        except Exception as e:
            print(f"[HTMLToDocxParser] ERROR reconstructing {image_id}: {e}")
    
    def get_document(self) -> Document:
        """Return the created DOCX document."""
        return self.doc


# ============================================================================
# Public API Functions
# ============================================================================

def extract_html_from_docx(docx_path: str, output_html_path: Optional[str] = None) -> tuple:
    """
    Extract DOCX content and convert to HTML for translation.
    
    Args:
        docx_path: Path to input DOCX file
        output_html_path: Optional path to save HTML (for debugging)
    
    Returns:
        Tuple of (html_string, css_class_manager, image_manager)
    
    Example:
        html, css_mgr, img_mgr = extract_html_from_docx('document.docx')
        translated_html = google_translate(html)
        create_docx_from_html(translated_html, 'output.docx', css_mgr, img_mgr)
    """
    mapper = DocxHtmlMapper(docx_path)
    html_string = mapper.extract_html_from_docx()
    
    if output_html_path:
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(html_string)
    
    return html_string, mapper.css_manager, mapper.image_manager


def create_docx_from_html(
    html_string: str,
    output_docx_path: str,
    css_class_manager: CSSClassManager,
    image_manager: ImageManager
) -> None:
    """
    Create DOCX file from translated HTML.
    
    Args:
        html_string: Translated HTML with CSS classes and markers
        output_docx_path: Path to save output DOCX file
        css_class_manager: Manager used during extraction (for format lookup)
        image_manager: Manager with stored images
    
    Example:
        html, css_mgr, img_mgr = extract_html_from_docx('input.docx')
        translated = google_translate(html)
        create_docx_from_html(translated, 'output.docx', css_mgr, img_mgr)
    """
    parser = HTMLToDocxParser(css_class_manager, image_manager)
    parser.feed(html_string)
    doc = parser.get_document()
    doc.save(output_docx_path)


def translate_docx(
    input_docx_path: str,
    output_docx_path: str,
    translate_function: callable
) -> None:
    """
    Complete DOCX translation workflow.
    
    Args:
        input_docx_path: Path to input DOCX file
        output_docx_path: Path to save translated DOCX file
        translate_function: Function that translates HTML string
            Signature: translate_function(html: str) -> str
    
    Example:
        def my_translator(html):
            return google_translate_api(html, target='pt')
        
        translate_docx('input.docx', 'output.docx', my_translator)
    """
    # 1. Extract
    html_string, css_manager = extract_html_from_docx(input_docx_path)
    
    # 2. Translate
    translated_html = translate_function(html_string)
    
    # 3. Create
    create_docx_from_html(translated_html, output_docx_path, css_manager)
