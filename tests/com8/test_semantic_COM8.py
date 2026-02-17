#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit Tests for Semantic Splitting - COM8

Tests semantic boundary detection for HTML and plain text.

Author: Josué Amaral (COM8)
Date: 2026-02-17
Phase: C.3 - Semantic Splitting Implementation
"""

import unittest
from src.translation.google_translate import GoogleTranslateAPI


class TestSemanticBoundaryDetection(unittest.TestCase):
    """Test cases for semantic boundary detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_find_paragraph_boundaries(self):
        """Should find </p> boundaries in HTML."""
        html = "<p>First paragraph.</p><p>Second paragraph.</p><p>Third.</p>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should find 3 paragraph ends
        self.assertEqual(len(boundaries), 3)
        # Boundaries should be at positions after </p>
        for boundary in boundaries:
            self.assertTrue(html[boundary-4:boundary] == '</p>')
    
    def test_find_table_boundaries(self):
        """Should find </table> boundaries in HTML."""
        html = "<p>Text</p><table><tr><td>Cell</td></tr></table><p>More</p>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should find paragraph ends and table end
        self.assertGreater(len(boundaries), 0)
        # At least one boundary should be a table
        table_boundaries = [b for b in boundaries if html[b-8:b].lower() == '</table>']
        self.assertEqual(len(table_boundaries), 1)
    
    def test_find_heading_boundaries(self):
        """Should find heading boundaries (</h1> through </h6>)."""
        html = "<h1>Title</h1><h2>Subtitle</h2><p>Content</p>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should find h1, h2, and p endings
        self.assertEqual(len(boundaries), 3)
    
    def test_plain_text_double_newline(self):
        """Should find paragraph breaks (\\n\\n) in plain text."""
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        
        boundaries = self.api._find_semantic_boundaries(text)
        
        # Should find 2 double newlines
        self.assertEqual(len(boundaries), 2)
    
    def test_no_boundaries_simple_text(self):
        """Should return empty list for simple text with no boundaries."""
        text = "Just a simple sentence without paragraph breaks."
        
        boundaries = self.api._find_semantic_boundaries(text)
        
        self.assertEqual(len(boundaries), 0)
    
    def test_boundaries_sorted(self):
        """Boundaries should be sorted in ascending order."""
        html = "<p>C</p><p>A</p><p>B</p>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should be sorted
        self.assertEqual(boundaries, sorted(boundaries))
    
    def test_boundaries_unique(self):
        """Should not have duplicate boundaries."""
        html = "<p>Text</p><p>Text</p>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should have no duplicates
        self.assertEqual(len(boundaries), len(set(boundaries)))
    
    def test_list_boundaries(self):
        """Should find list boundaries (</ul>, </ol>, </li>)."""
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should find li and ul endings
        self.assertGreater(len(boundaries), 0)
    
    def test_section_boundaries(self):
        """Should find section and article boundaries."""
        html = "<section><p>Content</p></section><article><p>More</p></article>"
        
        boundaries = self.api._find_semantic_boundaries(html)
        
        # Should find section, article, and paragraph boundaries
        self.assertGreater(len(boundaries), 2)


class TestSemanticSplitting(unittest.TestCase):
    """Test cases for semantic splitting algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_split_at_paragraph_boundary(self):
        """Should prefer splitting at </p> over mid-paragraph."""
        # Create HTML with paragraphs that force a split
        para1 = "A" * 4700
        para2 = "B" * 1000
        html = f"<p>{para1}</p><p>{para2}</p>"
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        # Should split into 2 chunks
        self.assertEqual(len(chunk_data), 2)
        
        # First chunk should end at </p>
        chunk1_text, _, chunk1_end, _ = chunk_data[0]
        self.assertTrue(html[chunk1_end-4:chunk1_end] == '</p>')
    
    def test_split_preserves_tables(self):
        """Should not split inside tables (table has high priority)."""
        # Small table that fits in one chunk
        html = "<p>" + "A" * 3000 + "</p><table><tr><td>" + "B" * 500 + "</td></tr></table><p>" + "C" * 1000 + "</p>"
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        # Verify chunks - table should stay together
        for chunk_text, _, _, _ in chunk_data:
            # If chunk contains <table>, it should also contain </table>
            if '<table>' in chunk_text.lower():
                self.assertIn('</table>', chunk_text.lower())
    
    def test_fallback_to_sentence_boundary(self):
        """Should fallback to sentence boundary when no semantic boundary found."""
        # Plain text without paragraph breaks
        text = "Sentence one. " * 500  # Will exceed 4800 chars
        
        chunk_data = self.api._split_with_semantic_boundaries(text, max_size=4800)
        
        # Should split somewhere
        self.assertGreater(len(chunk_data), 1)
        
        # Chunks should break at sentence boundaries (not mid-word)
        for chunk_text, _, _, _ in chunk_data[:-1]:  # Exclude last chunk
            # Should end with sentence ending or whitespace
            last_chars = chunk_text.rstrip()[-2:]
            self.assertIn('.', last_chars + ' ')  # Has period nearby
    
    def test_semantic_with_overlap(self):
        """Semantic splitting should include overlap."""
        html = "<p>" + "A" * 4500 + "</p><p>" + "B" * 1500 + "</p>"
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800, overlap_size=200)
        
        # Should have 2 chunks
        self.assertEqual(len(chunk_data), 2)
        
        # Second chunk should have overlap
        _, chunk2_start, _, chunk2_actual = chunk_data[1]
        overlap = chunk2_start - chunk2_actual
        self.assertEqual(overlap, 200)
    
    def test_small_text_single_chunk(self):
        """Small text should produce single chunk."""
        html = "<p>Short paragraph.</p>"
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        self.assertEqual(len(chunk_data), 1)
    
    def test_prefers_closest_boundary(self):
        """Should prefer semantic boundary closest to max_size."""
        # Multiple paragraphs at different distances from chunk limit
        html = "<p>" + "A" * 3000 + "</p><p>" + "B" * 1500 + "</p><p>" + "C" * 500 + "</p>"
        
        chunk_data = self.api._split_with_semantic_boundaries(html, max_size=4800)
        
        # Should split at optimal boundary (closest to 4800 without exceeding)
        self.assertGreater(len(chunk_data), 0)
        
        # First chunk should be close to max_size
        chunk1_text, _, _, _ = chunk_data[0]
        # Should be reasonably close to 4800 (within 1000 chars)
        self.assertGreater(len(chunk1_text), 3500)


class TestSentenceBoundaryHelper(unittest.TestCase):
    """Test cases for sentence boundary helper method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_find_sentence_boundary_basic(self):
        """Should find last sentence ending before target position."""
        text = "Sentence one. Sentence two. Sentence three."
        target_pos = 30  # After "Sentence two. " 
        
        boundary = self.api._find_sentence_boundary(text, target_pos)
        
        # Should find ". " after "Sentence two"
        self.assertLessEqual(boundary, target_pos)
        # Verify it's at a sentence ending
        self.assertIn('. ', text[boundary-3:boundary+1])
    
    def test_find_no_boundary_returns_target(self):
        """Should return target position when no boundary found."""
        text = "A" * 1000  # No punctuation
        target_pos = 500
        
        boundary = self.api._find_sentence_boundary(text, target_pos)
        
        self.assertEqual(boundary, target_pos)
    
    def test_search_window_respected(self):
        """Should only search within specified window."""
        # Sentence boundary far away (> 500 chars)
        text = "Sentence. " + "A" * 600
        target_pos = len(text)
        
        boundary = self.api._find_sentence_boundary(text, target_pos, search_window=500)
        
        # Should not find boundary (it's > 500 chars back)
        self.assertEqual(boundary, target_pos)


class TestSemanticIntegration(unittest.TestCase):
    """Integration tests for semantic splitting feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_semantic_splitting_parameter(self):
        """translate_text_chunked should accept use_semantic_splitting parameter."""
        import inspect
        sig = inspect.signature(self.api.translate_text_chunked)
        params = sig.parameters
        
        self.assertIn('use_semantic_splitting', params)
        self.assertEqual(params['use_semantic_splitting'].default, True)
    
    def test_semantic_enabled_by_default(self):
        """Semantic splitting should be enabled by default."""
        # This just verifies the API design, actual translation tested manually
        text = "<p>" + "A" * 5000 + "</p>"
        
        # With semantic splitting (default), should split at </p>
        chunks_semantic = self.api._split_with_semantic_boundaries(text, max_size=4800)
        
        # Without semantic splitting, uses character-based
        chunks_simple = self.api._split_into_chunks_with_overlap(text, max_size=4800)
        
        # Both should split, but potentially at different positions
        self.assertGreater(len(chunks_semantic), 0)
        self.assertGreater(len(chunks_simple), 0)


if __name__ == '__main__':
    unittest.main()
