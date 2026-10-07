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
import json
from types import SimpleNamespace
from unittest.mock import ANY, Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

from src.gui.google_translate_dock import (
    GoogleTranslateDock,
    NotebookTranslationWorker,
    TranslationWorker,
)
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
    
    @patch('src.gui.google_translate_dock.thread_manager.start_thread', return_value=True)
    @patch('src.gui.google_translate_dock.TranslationWorker')
    def test_translation_start(self, mock_worker_class, mock_start_thread):
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
        mock_start_thread.assert_called_once()
        mock_worker.start.assert_called_once()
        
        # Verify UI state during translation
        assert not self.dock.btn_translate.isEnabled()
        assert self.dock.btn_cancel.isEnabled()
        assert self.dock.progress_bar.isVisible()

        finished_callback = mock_worker.finished.connect.call_args.args[0]
        self.dock.translation_worker = None
        with patch.object(self.dock, "_on_worker_finished") as on_finished:
            finished_callback()
        on_finished.assert_called_once_with(mock_worker)
    
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

    def test_browse_notebook_previews_only_markdown(self, tmp_path):
        notebook_path = tmp_path / "sample.ipynb"
        notebook_path.write_text(
            json.dumps(
                {
                    "cells": [
                        {"cell_type": "markdown", "metadata": {}, "source": ["Hello\n"]},
                        {
                            "cell_type": "code",
                            "metadata": {},
                            "source": ["print('secret')"],
                            "outputs": [],
                            "execution_count": None,
                        },
                    ],
                    "metadata": {},
                    "nbformat": 4,
                    "nbformat_minor": 5,
                }
            ),
            encoding="utf-8",
        )
        self.dock.recent_paths = Mock()
        self.dock.recent_paths.get.return_value = []

        with patch(
            "src.gui.google_translate_dock.QFileDialog.getOpenFileName",
            return_value=(str(notebook_path), "Jupyter Notebooks (*.ipynb)"),
        ):
            self.dock._browse_file()

        assert self.dock.text_input.toPlainText() == "Hello\n"
        assert "secret" not in self.dock.text_input.toPlainText()
        assert "1 Markdown cell" in self.dock.lbl_status.text()

    def test_notebook_translation_routes_to_dedicated_worker(self, tmp_path):
        notebook_path = tmp_path / "sample.ipynb"
        notebook_path.write_text(
            json.dumps(
                {
                    "cells": [{"cell_type": "markdown", "metadata": {}, "source": "Hello"}],
                    "metadata": {},
                    "nbformat": 4,
                    "nbformat_minor": 5,
                }
            ),
            encoding="utf-8",
        )
        self.dock.recent_paths = Mock()
        self.dock.recent_paths.get.return_value = []
        self.dock.chk_file_mode.setChecked(True)
        self.dock.ed_file_path.setCurrentText(str(notebook_path))

        with patch.object(self.dock, "_start_notebook_translation") as start:
            self.dock._translate()

        start.assert_called_once()
        notebook, from_lang, to_lang = start.call_args.args
        assert notebook["cells"][0]["source"] == "Hello"
        assert from_lang == "auto"
        assert to_lang == "pt"

    def test_save_translated_notebook_as_ipynb(self, tmp_path):
        output = tmp_path / "translated"
        self.dock._translated_notebook = {
            "cells": [{"cell_type": "markdown", "metadata": {}, "source": "Olá"}],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        self.dock.text_output.setPlainText("Olá")

        with patch(
            "src.gui.google_translate_dock.QFileDialog.getSaveFileName",
            return_value=(str(output), "Jupyter Notebooks (*.ipynb)"),
        ):
            self.dock._save_as()

        saved = json.loads((tmp_path / "translated.ipynb").read_text(encoding="utf-8"))
        assert saved["cells"][0]["source"] == "Olá"

    def test_browse_pdf_shows_bounded_text_preview(self, tmp_path):
        pdf_path = tmp_path / "report.pdf"
        pdf_path.write_bytes(b"%PDF-test")
        self.dock.recent_paths = Mock()
        self.dock.recent_paths.get.return_value = []

        with (
            patch(
                "src.gui.google_translate_dock.QFileDialog.getOpenFileName",
                return_value=(str(pdf_path), "PDF Documents (*.pdf)"),
            ),
            patch(
                "src.gui.google_translate_dock.extract_pdf_text",
                return_value=SimpleNamespace(text="Extracted PDF text", page_count=3),
            ) as extract,
        ):
            self.dock._browse_file()

        extract.assert_called_once_with(str(pdf_path))
        assert self.dock.text_input.toPlainText() == "Extracted PDF text"
        assert "3 page(s)" in self.dock.lbl_status.text()
        assert "not preserved" in self.dock.lbl_status.text()

    def test_pdf_translation_routes_extracted_text_to_plain_worker(self, tmp_path):
        pdf_path = tmp_path / "report.pdf"
        pdf_path.write_bytes(b"%PDF-test")
        self.dock.recent_paths = Mock()
        self.dock.recent_paths.get.return_value = []
        self.dock.chk_file_mode.setChecked(True)
        self.dock.ed_file_path.setCurrentText(str(pdf_path))

        with (
            patch(
                "src.gui.google_translate_dock.extract_pdf_text",
                return_value=SimpleNamespace(text="Full PDF text", page_count=2),
            ),
            patch.object(self.dock, "_start_translation") as start,
        ):
            self.dock._translate()

        start.assert_called_once_with("Full PDF text", "auto", "pt")

    def test_open_result_in_editor_emits_reviewable_text_and_name(self):
        emitted = []
        self.dock.open_in_editor_requested.connect(
            lambda content, name: emitted.append((content, name))
        )
        self.dock._source_file_path = "/tmp/report.pdf"
        self.dock._on_translation_completed("Translated PDF", True, "")

        assert self.dock.btn_open_in_editor.isEnabled()
        self.dock._open_result_in_editor()

        assert emitted == [("Translated PDF", "report_translated.txt")]

    def test_reverse_translation_swaps_languages_and_starts_automatically(self):
        self.dock.combo_from_lang.setCurrentIndex(
            self.dock.combo_from_lang.findData("en")
        )
        self.dock.combo_to_lang.setCurrentIndex(
            self.dock.combo_to_lang.findData("pt")
        )
        self.dock.text_output.setPlainText("Olá")

        with patch.object(self.dock, "_start_translation") as start:
            self.dock._reverse_translation()

        assert self.dock.text_input.toPlainText() == "Olá"
        assert self.dock.combo_from_lang.currentData() == "pt"
        assert self.dock.combo_to_lang.currentData() == "en"
        start.assert_called_once_with("Olá", "pt", "en")

    def test_reverse_translation_uses_detected_source_language(self):
        self.dock._last_detected_lang = "en"
        self.dock.text_output.setPlainText("Olá")

        with patch.object(self.dock, "_start_translation") as start:
            self.dock._reverse_translation()

        assert self.dock.combo_from_lang.currentData() == "pt"
        assert self.dock.combo_to_lang.currentData() == "en"
        start.assert_called_once_with("Olá", "pt", "en")

    def test_reverse_translation_requires_a_recognized_detected_language(self):
        self.dock._last_detected_lang = "auto"
        self.dock.text_output.setPlainText("Olá")

        with (
            patch.object(self.dock, "_start_translation") as start,
            patch("src.gui.google_translate_dock.QMessageBox.warning") as warning,
        ):
            self.dock._reverse_translation()

        warning.assert_called_once()
        start.assert_not_called()
        assert self.dock.combo_from_lang.currentData() == "auto"
        assert self.dock.combo_to_lang.currentData() == "pt"

    def test_reverse_translation_leaves_file_mode_before_reusing_output(self):
        self.dock.chk_file_mode.setChecked(True)
        self.dock._last_detected_lang = "en"
        self.dock.text_output.setPlainText("Olá")

        with patch.object(self.dock, "_start_translation"):
            self.dock._reverse_translation()

        assert not self.dock.chk_file_mode.isChecked()
        assert not self.dock.text_input.isReadOnly()


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
        api.translate_text_chunked.return_value = mock_result
        
        # Create worker
        worker = TranslationWorker(api, "Hello", "en", "pt")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.translation_completed = Mock()
        
        # Run worker (without actual threading for test)
        with patch('time.sleep'):  # Speed up test
            worker.run()
        
        # Verify API was called
        api.translate_text_chunked.assert_called_once_with(
            "Hello", "en", "pt", progress_callback=ANY, cancel_callback=ANY
        )
        
        # Verify signals were emitted
        worker.translation_completed.emit.assert_called_with("Olá", True, "", "en")
    
    @pytest.mark.timeout(10)
    def test_worker_failed_translation(self):
        """Test worker failed translation."""
        # Mock API with failure
        api = Mock()
        mock_result = TranslationResult(
            success=False,
            error_message="Network error"
        )
        api.translate_text_chunked.return_value = mock_result
        
        # Create worker
        worker = TranslationWorker(api, "Hello", "en", "pt")
        
        # Mock signals
        worker.progress_updated = Mock()
        worker.translation_completed = Mock()
        
        # Run worker
        with patch('time.sleep'):  # Speed up test
            worker.run()
        
        # Verify failure was handled
        worker.translation_completed.emit.assert_called_with("", False, "Network error", "en")
    
    @pytest.mark.timeout(10)
    def test_worker_delegates_large_text_chunking(self):
        """Test worker delegates large text to the chunked API."""
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
        api.translate_text_chunked.return_value = mock_result
        
        # Create worker
        worker = TranslationWorker(api, large_text, "en", "pt")
        worker.progress_updated = Mock()
        worker.translation_completed = Mock()
        
        # Run worker
        with patch('time.sleep'):  # Speed up test
            worker.run()
        
        api.translate_text_chunked.assert_called_once_with(
            large_text, "en", "pt", progress_callback=ANY, cancel_callback=ANY
        )
        
        # Verify final result combines chunks
        final_result = worker.translation_completed.emit.call_args[0][0]
        assert len(final_result) > 0


class TestNotebookTranslationWorker:
    """Test notebook-specific worker behavior without starting a thread."""

    def test_worker_translates_only_markdown_cells(self):
        notebook = {
            "cells": [
                {"cell_type": "markdown", "metadata": {}, "source": "Hello"},
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": "print('Hello')",
                    "outputs": [{"output_type": "stream", "text": "Hello"}],
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        api = Mock()
        api.translate_text_chunked.return_value = TranslationResult(
            success=True,
            translated_text="Olá",
            source_language="en",
            target_language="pt",
        )
        worker = NotebookTranslationWorker(api, notebook, "auto", "pt")
        worker.progress_updated = Mock()
        worker.chunk_progress = Mock()
        worker.translation_completed = Mock()

        worker.run()

        api.translate_text_chunked.assert_called_once_with(
            "Hello", "auto", "pt", progress_callback=ANY, cancel_callback=ANY
        )
        emitted_notebook, preview, success, error, detected = (
            worker.translation_completed.emit.call_args.args
        )
        assert success is True
        assert error == ""
        assert detected == "en"
        assert preview == "Olá"
        assert emitted_notebook["cells"][0]["source"] == "Olá"
        assert emitted_notebook["cells"][1]["source"] == "print('Hello')"
        assert emitted_notebook["cells"][1]["outputs"][0]["text"] == "Hello"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
