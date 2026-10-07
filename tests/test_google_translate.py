#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Google Translate API

Tests the translation functionality with mocking to avoid actual API calls.

Author: Josué Amaral
Date: December 21, 2025
Version: 2.9.78
"""

import pytest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch

from src.translation.google_translate import GoogleTranslateAPI, TranslationResult


class TestGoogleTranslateAPI:
    """Test Google Translate API functionality."""
    
    def setup_method(self):
        """Setup test environment with temporary cache directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.api = GoogleTranslateAPI(cache_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test API initialization and cache directory creation."""
        assert self.api.cache_dir.exists()
        assert self.api.cache_file == self.api.cache_dir / 'translations.json'
        assert self.api._cache == {}
    
    def test_language_support(self):
        """Test supported languages."""
        expected_langs = {'en', 'pt', 'es', 'fr', 'de', 'zh', 'ja'}
        actual_langs = set(GoogleTranslateAPI.LANGUAGES.keys())
        assert actual_langs == expected_langs
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        key1 = self.api._get_cache_key("Hello World", "en", "pt")
        key2 = self.api._get_cache_key("hello world", "en", "pt")  # Different case
        key3 = self.api._get_cache_key("Hello World", "en", "es")  # Different target
        
        # Same text (different case) should generate same key
        assert key1 == key2
        # Different target language should generate different key
        assert key1 != key3
    
    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text."""
        result = self.api.translate_text("")
        assert not result.success
        assert "Empty text" in result.error_message
        
        result = self.api.translate_text("   ")
        assert not result.success
        assert "Empty text" in result.error_message
    
    def test_invalid_language_handling(self):
        """Test handling of invalid language codes."""
        result = self.api.translate_text("Hello", "invalid", "pt")
        assert not result.success
        assert "Unsupported source language" in result.error_message
        
        result = self.api.translate_text("Hello", "en", "invalid")
        assert not result.success
        assert "Unsupported target language" in result.error_message
    
    @patch('urllib.request.urlopen')
    def test_successful_translation(self, mock_urlopen):
        """Test successful translation with mocked response."""
        # Mock successful Google Translate response
        mock_response = Mock()
        mock_response.read.return_value = b'[[[\"Ola Mundo\",\"Hello World\",null,null,0]],null,\"en\"]'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.api.translate_text("Hello World", "en", "pt")
        
        assert result.success
        assert result.translated_text == "Ola Mundo"
        assert result.source_language == "en"
        assert result.target_language == "pt"
        assert not result.from_cache
    
    @patch('urllib.request.urlopen')
    def test_translation_caching(self, mock_urlopen):
        """Test translation caching mechanism."""
        # Mock response
        mock_response = Mock()
        mock_response.read.return_value = b'[[[\"Hola Mundo\",\"Hello World\",null,null,0]],null,\"en\"]'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # First translation - should make API call
        result1 = self.api.translate_text("Hello World", "en", "es")
        assert result1.success
        assert not result1.from_cache
        
        # Second translation of same text - should use cache
        result2 = self.api.translate_text("Hello World", "en", "es")
        assert result2.success
        assert result2.from_cache
        assert result2.translated_text == result1.translated_text
        
        # Verify only one API call was made
        assert mock_urlopen.call_count == 1
    
    @patch('urllib.request.urlopen')
    def test_network_error_handling(self, mock_urlopen):
        """Test handling of network errors."""
        mock_urlopen.side_effect = Exception("Network error")
        
        result = self.api.translate_text("Hello World", "en", "pt")
        
        assert not result.success
        assert "Translation request failed" in result.error_message
    
    @patch('urllib.request.urlopen')
    def test_invalid_json_response(self, mock_urlopen):
        """Test handling of invalid JSON responses."""
        mock_response = Mock()
        mock_response.read.return_value = b'Invalid JSON'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.api.translate_text("Hello World", "en", "pt")
        
        assert not result.success
        assert "Failed to parse translation response" in result.error_message
    
    @patch('urllib.request.urlopen')
    def test_retry_mechanism(self, mock_urlopen):
        """Test retry mechanism with eventual success."""
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.read.return_value = b'Invalid JSON'
        
        mock_response_success = Mock()
        mock_response_success.read.return_value = b'[[[\"Ola\",\"Hello\",null,null,0]],null,\"en\"]'
        
        mock_urlopen.return_value.__enter__.side_effect = [
            mock_response_fail,  # First attempt fails
            mock_response_fail,  # Second attempt fails
            mock_response_success  # Third attempt succeeds
        ]
        
        # Mock time.sleep to speed up test
        with patch('time.sleep'):
            result = self.api.translate_text("Hello", "en", "pt")
        
        assert result.success
        assert result.translated_text == "Ola"
        assert mock_urlopen.call_count == 3
    
    @patch('urllib.request.urlopen')
    def test_retry_mechanism_all_failures(self, mock_urlopen):
        """Test retry mechanism when all attempts fail."""
        mock_urlopen.side_effect = Exception("Network error")
        
        # Mock time.sleep to speed up test
        with patch('time.sleep'):
            result = self.api.translate_text("Hello", "en", "pt")
        
        assert not result.success
        assert "Translation failed after 3 attempts" in result.error_message
        assert mock_urlopen.call_count == 3
    
    def test_cache_persistence(self):
        """Test cache persistence to disk."""
        # Manually add to cache
        cache_key = self.api._get_cache_key("Test", "en", "pt")
        self.api._cache[cache_key] = {
            'translated_text': 'Teste',
            'source_language': 'en',
            'target_language': 'pt',
            'timestamp': time.time()
        }
        
        # Save cache
        self.api._save_cache()
        
        # Verify cache file exists
        assert self.api.cache_file.exists()
        
        # Load cache in new instance
        new_api = GoogleTranslateAPI(cache_dir=self.temp_dir)
        assert cache_key in new_api._cache
        assert new_api._cache[cache_key]['translated_text'] == 'Teste'
    
    def test_cache_clearing(self):
        """Test cache clearing functionality."""
        # Add some cache data
        self.api._cache['test_key'] = {'test': 'data'}
        self.api._save_cache()
        
        # Clear cache
        success = self.api.clear_cache()
        
        assert success
        assert len(self.api._cache) == 0
        assert not self.api.cache_file.exists()
    
    def test_cache_info(self):
        """Test cache information retrieval."""
        # Add some cache data
        self.api._cache['key1'] = {'test': 'data1'}
        self.api._cache['key2'] = {'test': 'data2'}
        self.api._save_cache()
        
        info = self.api.get_cache_info()
        
        assert info['entries'] == 2
        assert info['file_size_bytes'] > 0
        assert str(self.api.cache_dir) in info['cache_dir']

    def test_chunked_translation_can_cancel_before_provider_call(self):
        """Cancellation must stop discovery before any provider request."""
        self.api._translate_request = Mock()

        result = self.api.translate_text_chunked(
            "Hello", "en", "pt", cancel_callback=lambda: True
        )

        assert not result.success
        assert result.error_message == "Translation cancelled"
        self.api._translate_request.assert_not_called()

    def test_chunked_translation_stops_after_inflight_provider_call(self):
        """A completed blocking request must not start another chunk after cancel."""
        cancelled = False

        def translate_once(*_args):
            nonlocal cancelled
            cancelled = True
            return TranslationResult(
                success=True,
                translated_text="translated",
                source_language="en",
                target_language="pt",
            )

        self.api._translate_request = Mock(side_effect=translate_once)
        result = self.api.translate_text_chunked(
            "A" * 6000,
            "en",
            "pt",
            max_chunk_size=1000,
            use_overlap=False,
            cancel_callback=lambda: cancelled,
        )

        assert not result.success
        assert result.error_message == "Translation cancelled"
        self.api._translate_request.assert_called_once()


class TestTranslationResult:
    """Test TranslationResult dataclass."""
    
    def test_successful_result(self):
        """Test successful translation result."""
        result = TranslationResult(
            success=True,
            translated_text="Ola Mundo",
            source_language="en",
            target_language="pt",
            from_cache=False
        )
        
        assert result.success
        assert result.translated_text == "Ola Mundo"
        assert result.source_language == "en"
        assert result.target_language == "pt"
        assert not result.from_cache
        assert result.error_message == ""
    
    def test_failed_result(self):
        """Test failed translation result."""
        result = TranslationResult(
            success=False,
            error_message="Network timeout"
        )
        
        assert not result.success
        assert result.error_message == "Network timeout"
        assert result.translated_text == ""
        assert not result.from_cache


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
