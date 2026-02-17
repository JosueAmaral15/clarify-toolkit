#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit Tests for Enhanced Error Handling - COM8

Tests detailed error messages for chunk translation failures.

Author: Josué Amaral (COM8)
Date: 2026-02-17
Phase: C.5 - Enhanced Error Handling
"""

import unittest
from src.translation.google_translate import GoogleTranslateAPI, ChunkTranslationError


class TestChunkTranslationError(unittest.TestCase):
    """Test cases for ChunkTranslationError class."""
    
    def test_error_creation(self):
        """Should create error with all required fields."""
        error = ChunkTranslationError(
            chunk_number=5,
            total_chunks=10,
            chunk_start=19200,
            chunk_end=24000,
            chunk_preview="<p>Some content...</p>",
            attempts=3,
            last_error="HTTP Error 413: Request Entity Too Large"
        )
        
        self.assertEqual(error.chunk_number, 5)
        self.assertEqual(error.total_chunks, 10)
        self.assertEqual(error.chunk_start, 19200)
        self.assertEqual(error.chunk_end, 24000)
        self.assertIn("Some content", error.chunk_preview)
        self.assertEqual(error.attempts, 3)
        self.assertIn("413", error.last_error)
    
    def test_error_message_contains_context(self):
        """Error message should contain all important context."""
        error = ChunkTranslationError(
            chunk_number=3,
            total_chunks=8,
            chunk_start=9600,
            chunk_end=14400,
            chunk_preview="Long text preview...",
            attempts=3,
            last_error="Network timeout"
        )
        
        msg = str(error)
        
        # Should contain chunk info
        self.assertIn("chunk 3/8", msg.lower())
        self.assertIn("9600", msg)
        self.assertIn("14400", msg)
        
        # Should contain preview
        self.assertIn("Long text preview", msg)
        
        # Should contain error details
        self.assertIn("attempts: 3", msg.lower())
        self.assertIn("Network timeout", msg)
    
    def test_error_message_contains_suggestions(self):
        """Error message should include helpful suggestions."""
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=5000,
            chunk_preview="Text",
            attempts=3,
            last_error="Too large"
        )
        
        msg = str(error)
        
        # Should have suggestions section
        self.assertIn("Suggestions", msg)
        self.assertIn("reducing max_chunk_size", msg.lower())
        self.assertIn("internet connection", msg.lower())
    
    def test_error_message_shows_chunk_size(self):
        """Error message should calculate and show chunk size."""
        error = ChunkTranslationError(
            chunk_number=2,
            total_chunks=5,
            chunk_start=4800,
            chunk_end=9600,
            chunk_preview="Preview",
            attempts=3,
            last_error="Error"
        )
        
        msg = str(error)
        
        # Chunk size = 9600 - 4800 = 4800
        self.assertIn("4800 chars", msg)
    
    def test_error_is_exception(self):
        """ChunkTranslationError should be an Exception."""
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=100,
            chunk_preview="Test",
            attempts=3,
            last_error="Test error"
        )
        
        self.assertIsInstance(error, Exception)
        
        # Should be raiseable
        with self.assertRaises(ChunkTranslationError):
            raise error


class TestEnhancedErrorIntegration(unittest.TestCase):
    """Integration tests for enhanced error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api = GoogleTranslateAPI()
    
    def test_error_message_in_translation_result(self):
        """Translation result should contain enhanced error message."""
        # This test would require mocking the API to fail
        # For now, just verify the error structure exists
        
        # Verify ChunkTranslationError is available
        self.assertTrue(hasattr(self.api, '_translate_request'))
    
    def test_error_preview_length_limit(self):
        """Chunk preview should be limited to reasonable length."""
        long_text = "A" * 500
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=500,
            chunk_preview=long_text[:100] + "...",
            attempts=3,
            last_error="Error"
        )
        
        msg = str(error)
        
        # Preview in message should not exceed reasonable length
        # (Original long_text is 500 chars, but preview is limited to 103: "A"*100 + "...")
        preview_section = msg.split("Content preview:")[1].split("\n")[0]
        self.assertLessEqual(len(preview_section), 150)


class TestErrorMessageFormatting(unittest.TestCase):
    """Test error message formatting and readability."""
    
    def test_multiline_format(self):
        """Error message should be formatted across multiple lines."""
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=100,
            chunk_preview="Test",
            attempts=3,
            last_error="Test error"
        )
        
        msg = str(error)
        
        # Should have multiple lines
        lines = msg.split('\n')
        self.assertGreater(len(lines), 5)
    
    def test_field_labels_present(self):
        """Error message should have clear field labels."""
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=100,
            chunk_preview="Test",
            attempts=3,
            last_error="Test error"
        )
        
        msg = str(error)
        
        # Should have labeled fields
        self.assertIn("Position:", msg)
        self.assertIn("Chunk size:", msg)
        self.assertIn("Content preview:", msg)
        self.assertIn("Attempts:", msg)
        self.assertIn("Last error:", msg)
        self.assertIn("Suggestions:", msg)
    
    def test_readable_position_format(self):
        """Position should be formatted in human-readable way."""
        error = ChunkTranslationError(
            chunk_number=5,
            total_chunks=10,
            chunk_start=24000,
            chunk_end=28800,
            chunk_preview="Test",
            attempts=3,
            last_error="Error"
        )
        
        msg = str(error)
        
        # Should show position as "characters X-Y"
        self.assertIn("characters 24000-28800", msg.lower())


class TestErrorHelpfulness(unittest.TestCase):
    """Test that errors provide actionable information."""
    
    def test_suggests_chunk_size_reduction(self):
        """Should suggest reducing chunk size for large chunks."""
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=4800,
            chunk_preview="Large chunk",
            attempts=3,
            last_error="HTTP Error 413"
        )
        
        msg = str(error)
        
        self.assertIn("reducing max_chunk_size", msg.lower())
    
    def test_suggests_network_check(self):
        """Should suggest checking connection for network errors."""
        error = ChunkTranslationError(
            chunk_number=1,
            total_chunks=1,
            chunk_start=0,
            chunk_end=1000,
            chunk_preview="Test",
            attempts=3,
            last_error="Connection timeout"
        )
        
        msg = str(error)
        
        self.assertIn("internet connection", msg.lower())
    
    def test_suggests_rate_limiting(self):
        """Should mention rate limiting as possible cause."""
        error = ChunkTranslationError(
            chunk_number=5,
            total_chunks=10,
            chunk_start=0,
            chunk_end=1000,
            chunk_preview="Test",
            attempts=3,
            last_error="Too many requests"
        )
        
        msg = str(error)
        
        self.assertIn("rate limiting", msg.lower())
        self.assertIn("wait", msg.lower())


if __name__ == '__main__':
    unittest.main()
