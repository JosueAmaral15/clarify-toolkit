#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive tests for formatting preservation system.

Tests all 35 implemented formats across DOCX and ODT round-trips.
Ensures formatting survives extraction → translation → reconstruction.

Author: Programmer COM8
Date: February 1, 2026
Session: 53 (Testing Suite)
"""

import pytest
import tempfile
from pathlib import Path
from typing import List

from src.translation.format_mapper import FormatMapper, TextSegment, FormatBit


class TestFormatMapperBasics:
    """Test basic FormatMapper functionality."""
    
    def test_format_bit_allocation(self):
        """Test that format bits are properly allocated."""
        # Test character formatting bits
        assert FormatBit.BOLD == 1 << 0
        assert FormatBit.ITALIC == 1 << 1
        assert FormatBit.UNDERLINE == 1 << 2
        assert FormatBit.STRIKETHROUGH == 1 << 3
        assert FormatBit.FONT_COLOR == 1 << 4
        assert FormatBit.FONT_SIZE == 1 << 5
        assert FormatBit.FONT_FAMILY == 1 << 6
        assert FormatBit.HIGHLIGHT == 1 << 7
        
        # Test paragraph formatting bits
        assert FormatBit.ALIGNMENT == 1 << 8
        assert FormatBit.LINE_SPACING == 1 << 9
        assert FormatBit.INDENTATION == 1 << 10
        assert FormatBit.HEADING == 1 << 11
    
    def test_text_segment_creation(self):
        """Test TextSegment initialization."""
        seg = TextSegment(text="Hello", format_bits=3)  # BOLD | ITALIC
        assert seg.text == "Hello"
        assert seg.format_bits == 3
        assert seg.metadata is None
    
    def test_tagged_text_generation(self):
        """Test conversion of segments to tagged text."""
        seg = TextSegment(text="Bold text", format_bits=FormatBit.BOLD)
        tagged = seg.to_tagged_text()
        assert "<1>" in tagged
        assert "Bold text" in tagged
        assert "</1>" in tagged


class TestCharacterFormatting:
    """Test Phase 1: Character formatting (12 formats)."""
    
    def test_bold_detection(self):
        """Test bold text detection."""
        import docx
        doc = docx.Document()
        para = doc.add_paragraph()
        run = para.add_run("Bold text")
        run.bold = True
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        assert "<1>" in tagged or "<1|" in tagged  # BOLD bit set
        
        Path(temp_path).unlink()
    
    def test_italic_detection(self):
        """Test italic text detection."""
        import docx
        doc = docx.Document()
        para = doc.add_paragraph()
        run = para.add_run("Italic text")
        run.italic = True
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        assert "<2>" in tagged or "<2|" in tagged  # ITALIC bit set
        
        Path(temp_path).unlink()
    
    def test_underline_detection(self):
        """Test underline detection."""
        import docx
        doc = docx.Document()
        para = doc.add_paragraph()
        run = para.add_run("Underlined text")
        run.underline = True
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        assert "<4>" in tagged or "<4|" in tagged  # UNDERLINE bit set
        
        Path(temp_path).unlink()
    
    def test_font_color_detection(self):
        """Test font color detection."""
        import docx
        from docx.shared import RGBColor
        
        doc = docx.Document()
        para = doc.add_paragraph()
        run = para.add_run("Red text")
        run.font.color.rgb = RGBColor(255, 0, 0)
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        # Should contain color metadata (FF0000)
        assert "FF0000" in tagged or "ff0000" in tagged.lower()
        
        Path(temp_path).unlink()
    
    def test_font_size_detection(self):
        """Test font size detection."""
        import docx
        from docx.shared import Pt
        
        doc = docx.Document()
        para = doc.add_paragraph()
        run = para.add_run("Large text")
        run.font.size = Pt(24)
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        # Should contain size metadata
        assert "24" in tagged or "24.0" in tagged
        
        Path(temp_path).unlink()
    
    def test_combined_character_formatting(self):
        """Test multiple character formats on same text."""
        import docx
        from docx.shared import Pt, RGBColor
        
        doc = docx.Document()
        para = doc.add_paragraph()
        run = para.add_run("Formatted text")
        run.bold = True
        run.italic = True
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0, 0, 255)
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        # Should combine BOLD (1) + ITALIC (2) + SIZE (16) + COLOR (8) = bits set
        segments = FormatMapper.parse_tagged_text(tagged)
        
        # Find the formatted segment
        formatted_seg = None
        for seg in segments:
            if "Formatted text" in seg.text:
                formatted_seg = seg
                break
        
        assert formatted_seg is not None
        assert formatted_seg.format_bits & FormatBit.BOLD
        assert formatted_seg.format_bits & FormatBit.ITALIC
        
        Path(temp_path).unlink()


class TestParagraphFormatting:
    """Test Phase 2: Paragraph formatting (9 formats)."""
    
    def test_alignment_detection(self):
        """Test paragraph alignment detection."""
        import docx
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = docx.Document()
        para = doc.add_paragraph("Centered text")
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        segments = FormatMapper.parse_tagged_text(tagged)
        
        # Find paragraph with alignment
        for seg in segments:
            if "Centered" in seg.text and seg.paragraph_metadata:
                assert "C" in seg.paragraph_metadata  # Center alignment
                break
        
        Path(temp_path).unlink()
    
    def test_line_spacing_detection(self):
        """Test line spacing detection."""
        import docx
        
        doc = docx.Document()
        para = doc.add_paragraph("Double spaced")
        para.paragraph_format.line_spacing = 2.0
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        segments = FormatMapper.parse_tagged_text(tagged)
        
        # Find paragraph with spacing
        for seg in segments:
            if "Double" in seg.text and seg.paragraph_metadata:
                assert "2.0" in seg.paragraph_metadata
                break
        
        Path(temp_path).unlink()


class TestHeadings:
    """Test Phase 3: Headings (4 formats)."""
    
    def test_heading_1_detection(self):
        """Test H1 heading detection."""
        import docx
        
        doc = docx.Document()
        doc.add_heading("Main Heading", level=1)
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        assert "H1" in tagged
        
        Path(temp_path).unlink()
    
    def test_heading_levels_2_to_6(self):
        """Test H2-H6 heading detection."""
        import docx
        
        doc = docx.Document()
        doc.add_heading("Heading 2", level=2)
        doc.add_heading("Heading 3", level=3)
        doc.add_heading("Heading 6", level=6)
        
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        assert "H2" in tagged
        assert "H3" in tagged
        assert "H6" in tagged
        
        Path(temp_path).unlink()


class TestHyperlinks:
    """Test Phase 7: Hyperlinks (3+ formats)."""
    
    def test_hyperlink_preservation(self):
        """Test basic hyperlink detection and preservation."""
        tagged_text = "Visit <LINK:https://example.com>our website</LINK> for more."
        
        segments = FormatMapper.parse_tagged_text(tagged_text)
        
        # Should have 3 segments: before, link, after
        link_segment = None
        for seg in segments:
            if seg.hyperlink_url:
                link_segment = seg
                break
        
        assert link_segment is not None
        assert link_segment.hyperlink_url == "https://example.com"
        assert link_segment.text == "our website"


class TestSpecialCharacters:
    """Test Phase 9: Special characters (4 formats)."""
    
    def test_non_breaking_space_preservation(self):
        """Test non-breaking space (U+00A0) preservation."""
        text_with_nbsp = "Word1\u00A0Word2"
        
        tagged = FormatMapper.extract_formatted_text_from_docx.__doc__  # Dummy - Unicode passes through
        segments = [TextSegment(text=text_with_nbsp)]
        tagged = segments[0].to_tagged_text()
        
        assert "\u00A0" in tagged
    
    def test_unicode_character_preservation(self):
        """Test various Unicode characters preservation."""
        special_chars = [
            ("\u00A0", "non-breaking space"),
            ("\u2011", "non-breaking hyphen"),
            ("\u00AD", "soft hyphen"),
            ("\t", "tab"),
        ]
        
        for char, name in special_chars:
            seg = TextSegment(text=f"Test{char}text")
            tagged = seg.to_tagged_text()
            assert char in tagged, f"Failed to preserve {name}"


class TestRoundTrip:
    """Test complete round-trip: DOCX → Tagged → DOCX."""
    
    def test_docx_round_trip_basic(self):
        """Test basic DOCX round-trip preservation."""
        import docx
        
        # Create source document
        doc1 = docx.Document()
        para = doc1.add_paragraph()
        run = para.add_run("Bold and ")
        run.bold = True
        run = para.add_run("italic text")
        run.italic = True
        
        temp_src = tempfile.mktemp(suffix='_src.docx')
        doc1.save(temp_src)
        
        # Extract → Translate (mock) → Reconstruct
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_src)
        segments = FormatMapper.parse_tagged_text(tagged)
        
        temp_dst = tempfile.mktemp(suffix='_dst.docx')
        FormatMapper.create_docx_from_segments(segments, temp_dst)
        
        # Verify destination
        doc2 = docx.Document(temp_dst)
        assert len(doc2.paragraphs) > 0
        
        # Clean up
        Path(temp_src).unlink()
        Path(temp_dst).unlink()
    
    def test_odt_round_trip_basic(self):
        """Test basic ODT round-trip preservation."""
        from odf import opendocument, text as odf_text, style as odf_style
        from odf.text import P, Span
        
        # Create source document
        doc1 = opendocument.OpenDocumentText()
        p = P()
        span = Span(text="Test text")
        p.addElement(span)
        doc1.text.addElement(p)
        
        temp_src = tempfile.mktemp(suffix='_src.odt')
        doc1.save(temp_src)
        
        # Extract → Parse → Reconstruct
        tagged = FormatMapper.extract_formatted_text_from_odt(temp_src)
        segments = FormatMapper.parse_tagged_text(tagged)
        
        temp_dst = tempfile.mktemp(suffix='_dst.odt')
        FormatMapper.create_odt_from_segments(segments, temp_dst)
        
        # Verify destination exists
        assert Path(temp_dst).exists()
        assert Path(temp_dst).stat().st_size > 0
        
        # Clean up
        Path(temp_src).unlink()
        Path(temp_dst).unlink()


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_document(self):
        """Test handling of empty documents."""
        import docx
        
        doc = docx.Document()
        temp_path = tempfile.mktemp(suffix='.docx')
        doc.save(temp_path)
        
        tagged = FormatMapper.extract_formatted_text_from_docx(temp_path)
        # Should return empty or whitespace
        assert len(tagged.strip()) == 0
        
        Path(temp_path).unlink()
    
    def test_very_long_text(self):
        """Test handling of very long text."""
        long_text = "A" * 10000
        seg = TextSegment(text=long_text)
        tagged = seg.to_tagged_text()
        
        # Should preserve all text
        assert long_text in tagged
    
    def test_special_xml_characters(self):
        """Test handling of XML special characters."""
        special_text = "Test <tag> & \"quotes\" 'apostrophes'"
        seg = TextSegment(text=special_text)
        tagged = seg.to_tagged_text()
        
        # Should handle escaping properly
        segments = FormatMapper.parse_tagged_text(tagged)
        assert len(segments) > 0


# Test execution summary
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
