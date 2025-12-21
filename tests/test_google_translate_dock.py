#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Google Translate Dock GUI

Tests the GUI components with mocking to avoid actual API calls.

Author: Josué Amaral
Date: December 21, 2025
Version: 2.9.78
"""

import pytest
import sys
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from src.gui.google_translate_dock import GoogleTranslateDock, TranslationWorker
from src.translation.google_translate import TranslationResult

# Ensure QApplication exists for GUI tests
if not QApplication.instance():
    app = QApplication(sys.argv)


class TestGoogleTranslateDock:
    """Test Google Translate Dock GUI components."""
    
    def setup_method(self):
        """Setup test environment."""
        self.dock = GoogleTranslateDock()
        self.dock.show()  # Show dock to ensure widgets work correctly
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'dock'):
            self.dock.deleteLater()
    
    @pytest.mark.timeout(5)
    def test_dock_initialization(self):
        """Test dock initialization and UI setup."""
        # Title could be in EN or PT-BR depending on environment
        expected_titles = ["Google Translate", "Google Tradutor"]
        assert self.dock.windowTitle() in expected_titles
        assert self.dock.combo_from_lang.count() == 8  # Auto + 7 languages
        assert self.dock.combo_to_lang.count() == 7  # 7 languages
        assert not self.dock.btn_copy_result.isEnabled()  # Initially disabled
        assert not self.dock.btn_cancel.isEnabled()  # Initially disabled
        assert not self.dock.progress_bar.isVisible()  # Initially hidden
    
    @pytest.mark.timeout(5)
    def test_language_combo_population(self):
        """Test language combo box population."""
        # Test from language (includes auto-detect)
        assert self.dock.combo_from_lang.itemText(0) == "Auto-detect"
        assert self.dock.combo_from_lang.itemData(0) == "auto"
        
        # Test to language (default should be Portuguese)
        pt_found = False
        for i in range(self.dock.combo_to_lang.count()):
            if self.dock.combo_to_lang.itemData(i) == "pt":
                pt_found = True
                break
        assert pt_found, "Portuguese not found in target languages"
    
    @pytest.mark.timeout(5)
    def test_file_mode_toggle(self):
        """Test file mode toggle functionality."""
        # Initially in text mode
        assert not self.dock.file_group.isVisible()
        assert not self.dock.text_input.isReadOnly()
        
        # Switch to file mode - test direct method call to ensure functionality works
        self.dock._toggle_file_mode(True)
        
        assert self.dock.file_group.isVisible()
        assert self.dock.text_input.isReadOnly()
        assert "File content will appear here" in self.dock.text_input.placeholderText()
        
        # Switch back to text mode
        self.dock._toggle_file_mode(False)
        
        assert not self.dock.file_group.isVisible()
        assert not self.dock.text_input.isReadOnly()
    
    @pytest.mark.timeout(5)
    def test_clear_functionality(self):
        """Test clear button functionality."""
        # Set some content
        self.dock.text_input.setPlainText("Hello World")
        self.dock.text_output.setPlainText("Olá Mundo")
        self.dock.btn_copy_result.setEnabled(True)
        
        # Clear
        self.dock._clear()
        
        assert self.dock.text_input.toPlainText() == ""
        assert self.dock.text_output.toPlainText() == ""
        assert not self.dock.btn_copy_result.isEnabled()
        assert "Ready to translate" in self.dock.lbl_status.text()
    
    @pytest.mark.timeout(5)
    def test_empty_text_validation(self):
        """Test validation of empty text input."""
        # Clear any existing text
        self.dock.text_input.clear()
        
        # Mock QMessageBox to avoid dialog
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            self.dock._translate()
            mock_warning.assert_called_once()
            assert "No Text" in mock_warning.call_args[0][1]
    
    @pytest.mark.timeout(5)
    def test_same_language_validation(self):
        """Test validation when source and target languages are the same."""
        # Set same language for both (not auto)
        for i in range(self.dock.combo_from_lang.count()):
            if self.dock.combo_from_lang.itemData(i) == "en":
                self.dock.combo_from_lang.setCurrentIndex(i)
                break
        
        for i in range(self.dock.combo_to_lang.count()):
            if self.dock.combo_to_lang.itemData(i) == "en":
                self.dock.combo_to_lang.setCurrentIndex(i)
                break
        
        self.dock.text_input.setPlainText("Hello")
        
        # Mock QMessageBox to avoid dialog
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            self.dock._translate()
            mock_warning.assert_called_once()
            assert "Same Languages" in mock_warning.call_args[0][1]
    
    @pytest.mark.timeout(5)
    def test_cache_info_display(self):
        """Test cache information display."""
        # Mock cache info
        with patch.object(self.dock.api, 'get_cache_info') as mock_cache_info:
            mock_cache_info.return_value = {
                'entries': 5,
                'file_size_bytes': 1024
            }
            
            self.dock._update_cache_info()
            
            cache_text = self.dock.lbl_cache_info.text()
            assert "Cache: 5 translations" in cache_text
            assert "1.0 KB" in cache_text
    
    @patch('src.gui.google_translate_dock.TranslationWorker')
    def test_translation_start(self, mock_worker_class):
        """Test translation process initiation."""
        # Setup mock worker
        mock_worker = Mock()
        mock_worker_class.return_value = mock_worker
        
        # Set valid input
        self.dock.text_input.setPlainText("Hello World")
        
        # Test UI update for translation start directly
        self.dock._start_translation("Hello World", "en", "pt")
        QApplication.processEvents()  # Process Qt events
        
        # Verify worker was created and started
        mock_worker_class.assert_called_once()
        mock_worker.start.assert_called_once()
        
        # Verify UI state during translation
        assert not self.dock.btn_translate.isEnabled()
        assert self.dock.btn_cancel.isEnabled()
        assert self.dock.progress_bar.isVisible()
    
    @pytest.mark.timeout(5)
    def test_translation_completion_success(self):
        """Test successful translation completion."""
        # Simulate translation completion
        self.dock._on_translation_completed(
            "Olá Mundo", True, ""
        )
        
        assert self.dock.text_output.toPlainText() == "Olá Mundo"
        assert self.dock.btn_copy_result.isEnabled()
        assert self.dock.btn_translate.isEnabled()
        assert not self.dock.btn_cancel.isEnabled()
        assert not self.dock.progress_bar.isVisible()
        assert "Translation completed" in self.dock.lbl_status.text()
    
    @pytest.mark.timeout(5)
    def test_translation_completion_failure(self):
        """Test failed translation completion."""
        # Simulate translation failure
        self.dock._on_translation_completed(
            "", False, "Network error"
        )
        
        assert "Translation failed: Network error" in self.dock.text_output.toPlainText()
        assert not self.dock.btn_copy_result.isEnabled()
        assert self.dock.btn_translate.isEnabled()
        assert "Translation failed" in self.dock.lbl_status.text()
    
    @pytest.mark.timeout(5)
    def test_progress_updates(self):
        """Test progress bar updates."""
        self.dock._on_progress_updated(50, "Translating...")
        
        assert self.dock.progress_bar.value() == 50
        assert self.dock.lbl_status.text() == "Translating..."


class TestTranslationWorker:
    """Test TranslationWorker thread."""
    
    @pytest.mark.timeout(5)
    def test_worker_initialization(self):
        """Test worker initialization."""
        api = Mock()
        worker = TranslationWorker(api, "Hello", "en", "pt")
        
        assert worker.api == api
        assert worker.text == "Hello"
        assert worker.from_lang == "en"
        assert worker.to_lang == "pt"
        assert not worker.is_cancelled
    
    @pytest.mark.timeout(5)
    def test_worker_cancellation(self):
        """Test worker cancellation."""
        api = Mock()
        worker = TranslationWorker(api, "Hello", "en", "pt")
        
        worker.cancel()
        assert worker.is_cancelled
    
    @pytest.mark.timeout(10)
    def test_worker_successful_translation(self):
        """Test worker successful translation."""
        # Mock API
        api = Mock()
        mock_result = TranslationResult(
            success=True,
            translated_text="Olá",
            source_language="en",
            target_language="pt"
        )
        api.translate_text.return_value = mock_result
        
        # Create worker
        worker = TranslationWorker(api, "Hello", "en", "pt")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.translation_completed = Mock()
        
        # Run worker (without actual threading for test)
        with patch('time.sleep'):  # Speed up test
            worker.run()
        
        # Verify API was called
        api.translate_text.assert_called_with("Hello", "en", "pt")
        
        # Verify signals were emitted
        worker.translation_completed.emit.assert_called_with("Olá", True, "")
    
    @pytest.mark.timeout(10)
    def test_worker_failed_translation(self):
        """Test worker failed translation."""
        # Mock API with failure
        api = Mock()
        mock_result = TranslationResult(
            success=False,
            error_message="Network error"
        )
        api.translate_text.return_value = mock_result
        
        # Create worker
        worker = TranslationWorker(api, "Hello", "en", "pt")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.translation_completed = Mock()
        
        # Run worker
        with patch('time.sleep'):  # Speed up test
            worker.run()
        
        # Verify failure was handled
        worker.translation_completed.emit.assert_called_with("", False, "Network error")
    
    @pytest.mark.timeout(10)
    def test_worker_large_text_chunking(self):
        """Test worker handles large text by chunking."""
        # Create large text (over 5000 chars) with paragraph breaks for chunking
        large_text = "Hello World!\n\n" * 400  # ~5600 chars total, creating 2+ chunks
        
        # Mock API
        api = Mock()
        mock_result = TranslationResult(
            success=True,
            translated_text="Olá Mundo! ",
            source_language="en",
            target_language="pt"
        )
        api.translate_text.return_value = mock_result
        
        # Create worker
        worker = TranslationWorker(api, large_text, "en", "pt")
        worker.progress_updated = Mock()
        worker.translation_completed = Mock()
        
        # Run worker
        with patch('time.sleep'):  # Speed up test
            worker.run()
        
        # Verify multiple API calls were made (for chunks)
        assert api.translate_text.call_count >= 2
        
        # Verify final result combines chunks
        final_result = worker.translation_completed.emit.call_args[0][0]
        assert len(final_result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])