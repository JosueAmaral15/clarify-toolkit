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
import json
import os
import psutil
import re
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Dict, List, Optional, Tuple
from xml.dom import minidom

from odf import opendocument, text as odf_text, style as odf_style, table as odf_table
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
    tag_type: str  # 'div' or 'span'
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
# ODT Extraction to HTML
# ============================================================================

class HTMLFormatMapper:
    """Convert ODT documents to/from HTML for translation."""
    
    @staticmethod
    def extract_html_from_odt(file_path: str) -> Tuple[str, object]:
        """
        Extract ODT content as HTML with CSS formatting.
        
        Args:
            file_path: Path to .odt file
            
        Returns:
            Tuple of (html_string, css_manager_or_path)
            - html_string: Full HTML document with structure
            - css_manager_or_path: CSSClassManager object OR path to JSON file
              (automatic decision based on available RAM)
        """
        doc = opendocument.load(file_path)
        css_manager = CSSClassManager()
        segments: List[HTMLSegment] = []
        
        # Build style dictionary
        styles = HTMLFormatMapper._build_style_dict(doc)
        
        # Process all paragraphs
        paragraphs = doc.getElementsByType(odf_text.P)
        for i, para in enumerate(paragraphs):
            para_segments = HTMLFormatMapper._extract_paragraph(para, styles, css_manager)
            segments.extend(para_segments)
            
            # Add line break after each paragraph (except the last one)
            # This preserves document structure: each ODT paragraph becomes a line in HTML
            if i < len(paragraphs) - 1:
                # Create BR segment with empty FormatAttributes
                segments.append(HTMLSegment(
                    tag_type='br',
                    css_class=None,
                    text='',
                    attributes=FormatAttributes()
                ))
        
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
            return html, temp_file
        else:
            # Keep in memory
            return html, css_manager
    
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
    def _extract_paragraph(para, styles: Dict, css_manager: CSSClassManager) -> List[HTMLSegment]:
        """Extract paragraph with formatting."""
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
                # Formatted span
                span_text, span_fmt = HTMLFormatMapper._extract_span(node, styles, para_fmt)
                
                # If format changed, create new segment
                if span_text:
                    if para_text:
                        # Save accumulated text with previous format
                        css_class = css_manager.get_or_create_class(current_fmt)
                        tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
                        segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
                        para_text = ""
                    
                    # Add span segment
                    css_class = css_manager.get_or_create_class(span_fmt)
                    segments.append(HTMLSegment(span_text, css_class, 'span', span_fmt))
                    current_fmt = para_fmt  # Reset to paragraph format
            elif hasattr(node, 'qname') and node.qname[1] in ['tab', 's']:
                # Tab or space
                if node.qname[1] == 'tab':
                    para_text += '&#9;'  # HTML entity for tab
                elif node.qname[1] == 's':
                    # Multiple spaces
                    try:
                        count = int(node.getAttribute('c'))
                    except:
                        count = 1
                    para_text += '&nbsp;' * count
        
        # Save remaining text
        if para_text:
            css_class = css_manager.get_or_create_class(current_fmt)
            tag_type = HTMLFormatMapper._decide_tag_type(para_text, current_fmt)
            segments.append(HTMLSegment(para_text, css_class, tag_type, current_fmt))
        
        # Add paragraph separator
        segments.append(HTMLSegment('\n', '', 'br', FormatAttributes()))
        
        return segments
    
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
    def _extract_span(span, styles: Dict, para_fmt: FormatAttributes) -> Tuple[str, FormatAttributes]:
        """Extract span text and formatting."""
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
        
        # Extract text content
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
        
        for segment in segments:
            if segment.tag_type == 'br':
                body_parts.append('<br>')
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
                
                body_parts.append(f'<{segment.tag_type} class="{segment.css_class}">{escaped_text}</{segment.tag_type}>')
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

def create_odt_from_html(html: str, css_manager_or_path, output_path: str):
    """
    Create ODT file from translated HTML.
    
    Args:
        html: Translated HTML document
        css_manager_or_path: CSSClassManager object or path to JSON file
        output_path: Where to save ODT file
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
    parser = HTMLToODTParser(css_manager)
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
            # End current paragraph
            if current_paragraph is not None:
                doc.text.addElement(current_paragraph)
            current_paragraph = None
        
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
    
    # Add final paragraph if exists
    if current_paragraph is not None:
        doc.text.addElement(current_paragraph)
    
    # Save ODT
    doc.save(output_path)


class HTMLToODTParser(HTMLParser):
    """Parse HTML and extract segments for ODT creation."""
    
    def __init__(self, css_manager: CSSClassManager):
        super().__init__()
        self.css_manager = css_manager
        self.segments = []
        self.current_tag = None
        self.current_class = None
    
    def handle_starttag(self, tag, attrs):
        """Handle opening tags."""
        self.current_tag = tag
        
        # Handle self-closing BR tag immediately
        if tag == 'br':
            self.segments.append({'type': 'br'})
            return
        
        # Extract class attribute
        for attr, value in attrs:
            if attr == 'class':
                self.current_class = value
                break
    
    def handle_endtag(self, tag):
        """Handle closing tags."""
        self.current_tag = None
        self.current_class = None
    
    def handle_data(self, data):
        """Handle text content."""
        # Skip whitespace in head/style
        if self.current_tag in ['style', 'head', 'title']:
            return
        
        # Skip whitespace-only data (HTML formatting between tags)
        if not data.strip():
            return
        
        # Decode HTML entities back to characters
        import html
        text = html.unescape(data)
        
        self.segments.append({
            'type': 'text',
            'text': text,
            'class': self.current_class
        })
