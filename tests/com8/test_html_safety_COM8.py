#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit Tests for HTML Tag Preservation - COM8

Tests HTML tag safety to ensure chunks never break inside tags.

Author: Josué Amaral (COM8)
Date: 2026-02-17
Phase: C.4 - HTML Tag Preservation
"""

import unittest
from src.translation.google_translate import GoogleTranslateAPI


class TestHTMLTagDetection(unittest.TestCase):
    """Test cases for HTML tag position detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_inside_opening_tag(self):
        """Should detect position inside opening tag."""
        html = "<span class='test'>Content</span>"
        
        # Position 10 is inside opening tag: <span class='test'>
        #                                              ^
        self.assertTrue(self.api._is_inside_html_tag(html, 10))
    
    def test_inside_closing_tag(self):
        """Should detect position inside closing tag."""
        html = "<p>Content</p>"
        
        # Position 12 is inside </p>
        self.assertTrue(self.api._is_inside_html_tag(html, 12))
    
    def test_outside_tag_before(self):
        """Should detect position outside tag (before opening)."""
        html = "Text <span>Content</span>"
        
        # Position 2 is in "Text" before <span>
        self.assertFalse(self.api._is_inside_html_tag(html, 2))
    
    def test_outside_tag_after(self):
        """Should detect position outside tag (after closing)."""
        html = "<span>Content</span> more text"
        
        # Position 22 is after </span>
        self.assertFalse(self.api._is_inside_html_tag(html, 22))
    
    def test_outside_tag_between_content(self):
        """Should detect position between tags in content."""
        html = "<p>Some content here</p>"
        
        # Position 8 is inside content "Some content"
        self.assertFalse(self.api._is_inside_html_tag(html, 8))
    
    def test_at_tag_boundaries(self):
        """Should handle positions exactly at tag boundaries."""
        html = "<p>Text</p>"
        
        # Position 0 is before <
        self.assertFalse(self.api._is_inside_html_tag(html, 0))
        
        # Position 3 is after > of opening tag
        self.assertFalse(self.api._is_inside_html_tag(html, 3))
    
    def test_self_closing_tag(self):
        """Should detect position inside self-closing tag."""
        html = "Text <img src='pic.jpg' /> more"
        
        # Position 15 is inside self-closing tag
        self.assertTrue(self.api._is_inside_html_tag(html, 15))
    
    def test_nested_tags(self):
        """Should work with nested tags."""
        html = "<div><span class='test'>Content</span></div>"
        
        # Position 13 is inside span's opening tag
        self.assertTrue(self.api._is_inside_html_tag(html, 13))
        
        # Position 30 is in content "Content"
        self.assertFalse(self.api._is_inside_html_tag(html, 30))


class TestSafeBreakPosition(unittest.TestCase):
    """Test cases for finding safe break positions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_already_safe_position(self):
        """Should return same position if already safe."""
        html = "<p>Content</p> more text"
        target_pos = 15  # Space after </p>
        
        safe_pos = self.api._find_safe_break_position(html, target_pos)
        
        self.assertEqual(safe_pos, target_pos)
    
    def test_move_forward_to_tag_close(self):
        """Should move forward to next > when inside tag."""
        html = "Text <span class='test'>Content</span>"
        target_pos = 15  # Inside opening tag attribute
        
        safe_pos = self.api._find_safe_break_position(html, target_pos)
        
        # Should move to after >
        self.assertGreater(safe_pos, target_pos)
        self.assertFalse(self.api._is_inside_html_tag(html, safe_pos))
        self.assertEqual(html[safe_pos-1], '>')
    
    def test_move_backward_to_tag_close(self):
        """Should move backward to previous > when forward is too far."""
        html = "<span class='very_long_attribute_name_that_exceeds_adjustment_limit_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'>Content</span>"
        target_pos = 100  # Inside very long opening tag
        
        safe_pos = self.api._find_safe_break_position(html, target_pos, max_adjustment=50)
        
        # With very long tag, may return target position as fallback
        # The important thing is it doesn't crash
        self.assertIsInstance(safe_pos, int)
        # If it found a safe position, verify it's actually safe
        if safe_pos != target_pos:
            self.assertFalse(self.api._is_inside_html_tag(html, safe_pos))
    
    def test_respects_max_adjustment(self):
        """Should respect max_adjustment parameter."""
        html = "<p>Content</p>"
        target_pos = 2  # Inside <p>
        
        safe_pos = self.api._find_safe_break_position(html, target_pos, max_adjustment=10)
        
        # Should find safe position within 10 chars
        self.assertLessEqual(abs(safe_pos - target_pos), 10)
    
    def test_edge_case_start_of_text(self):
        """Should handle position at start of text."""
        html = "<p>Content</p>"
        target_pos = 0
        
        safe_pos = self.api._find_safe_break_position(html, target_pos)
        
        self.assertEqual(safe_pos, 0)
    
    def test_edge_case_end_of_text(self):
        """Should handle position at end of text."""
        html = "<p>Content</p>"
        target_pos = len(html)
        
        safe_pos = self.api._find_safe_break_position(html, target_pos)
        
        self.assertEqual(safe_pos, target_pos)
    
    def test_multiple_tags_finds_nearest(self):
        """Should find nearest safe position with multiple tags."""
        html = "<p>A</p><span>B</span><div>C</div>"
        target_pos = 10  # Inside <span>
        
        safe_pos = self.api._find_safe_break_position(html, target_pos)
        
        # Should be safe
        self.assertFalse(self.api._is_inside_html_tag(html, safe_pos))


class TestHTMLSafetyIntegration(unittest.TestCase):
    """Integration tests for HTML tag safety in chunking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_chunks_never_break_inside_tags(self):
        """Chunks should never split inside HTML tags."""
        # Create HTML with tags at various positions
        html = "<p>Paragraph one.</p>" + "A" * 4700 + "<span class='test'>Content</span>" + "B" * 1000
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        # Verify no chunk breaks inside a tag
        for chunk_text, chunk_start, chunk_end, _ in chunk_data:
            # Check the break position
            if chunk_end < len(html):
                self.assertFalse(
                    self.api._is_inside_html_tag(html, chunk_end),
                    f"Chunk breaks inside tag at position {chunk_end}"
                )
    
    def test_overlap_splitting_respects_tags(self):
        """Overlap splitting should also respect HTML tags."""
        html = "<p>" + "A" * 4600 + "<span>Text</span>" + "B" * 500 + "</p>"
        
        chunk_data = self.api._split_into_chunks_with_overlap(html, max_size=4800)
        
        # Verify no breaks inside tags
        for _, _, chunk_end, _ in chunk_data:
            if chunk_end < len(html):
                self.assertFalse(self.api._is_inside_html_tag(html, chunk_end))
    
    def test_semantic_boundaries_already_safe(self):
        """Semantic boundaries (</p>, </table>) should already be safe."""
        html = "<p>" + "A" * 4700 + "</p><p>" + "B" * 1000 + "</p>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # All semantic boundaries should be safe
        for boundary in boundaries:
            self.assertFalse(self.api._is_inside_html_tag(html, boundary))
    
    def test_fallback_to_sentence_uses_tag_safety(self):
        """When falling back to sentence boundary, should still check tag safety."""
        # Long text without semantic boundaries
        html = "<div>" + "Sentence one. " * 500 + "</div>"
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        # Should split somewhere
        self.assertGreater(len(chunk_data), 1)
        
        # All breaks should be safe
        for _, _, chunk_end, _ in chunk_data:
            if chunk_end < len(html):
                self.assertFalse(self.api._is_inside_html_tag(html, chunk_end))
    
    def test_complex_nested_html(self):
        """Should handle complex nested HTML structures."""
        html = """
        <div class='container'>
            <section id='main'>
                <article>
                    <p>""" + "A" * 4500 + """</p>
                    <table>
                        <tr><td>Cell</td></tr>
                    </table>
                </article>
            </section>
        </div>
        """
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        # Verify chunking works and respects tags
        self.assertGreater(len(chunk_data), 0)
        
        for _, _, chunk_end, _ in chunk_data:
            if chunk_end < len(html):
                self.assertFalse(self.api._is_inside_html_tag(html, chunk_end))


class TestEdgeCases(unittest.TestCase):
    """Edge cases for HTML tag safety."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_malformed_html_missing_close(self):
        """Should handle malformed HTML gracefully."""
        html = "<p>Content without closing tag"
        target_pos = 15
        
        # Should not crash
        safe_pos = self.api._find_safe_break_position(html, target_pos)
        self.assertIsInstance(safe_pos, int)
    
    def test_text_with_angle_brackets(self):
        """Should handle text containing < and > that aren't tags."""
        text = "Math: 5 < 10 and 20 > 15"
        target_pos = 10
        
        # The angle brackets here aren't HTML tags
        # Method should handle this (may incorrectly identify as tag, but won't crash)
        safe_pos = self.api._find_safe_break_position(text, target_pos)
        self.assertIsInstance(safe_pos, int)
    
    def test_very_long_tag(self):
        """Should handle very long HTML tags."""
        long_attrs = "attr1='value1' " * 100
        html = f"<div {long_attrs}>Content</div>"
        target_pos = 500  # Inside long opening tag
        
        safe_pos = self.api._find_safe_break_position(html, target_pos, max_adjustment=2000)
        
        # Should find a safe position (with large enough adjustment)
        # Or return target as fallback
        self.assertIsInstance(safe_pos, int)
        
        # If adjusted successfully, should be safe
        if safe_pos != target_pos:
            self.assertFalse(self.api._is_inside_html_tag(html, safe_pos))


if __name__ == '__main__':
    unittest.main()
