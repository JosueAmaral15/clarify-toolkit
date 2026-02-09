#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Translate Dock - Translation Interface

Provides GUI for text and file translation using Google Translate.
Supports the 7 languages from Clarify's i18n system.

Features:
- Text and file translation
- 7 languages (EN, PT-BR, ES, FR, DE, ZH, JA)
- Auto-detect source language
- Caching and retry mechanism
- Progress tracking for large files
- Copy results to clipboard

Author: Josué Amaral
Date: December 21, 2025
Version: 2.9.78
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QComboBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QCheckBox,
    QMessageBox,
    QFileDialog,
    QSplitter,
    QFrame,
    QApplication,
)
from PySide6.QtGui import QFont

from ..gui.base_dock import BaseDock
from ..translation.google_translate import GoogleTranslateAPI, TranslationResult
from ..translation.document_parser import extract_text_from_document, DocumentParserError
from ..translation.format_mapper import FormatMapper
from ..i18n import tr, tooltip_tr


class TranslationWorker(QThread):
    """Background worker for translation operations."""

    progress_updated = Signal(int, str)  # progress, status
    translation_completed = Signal(str, bool, str, str)  # result, success, error, detected_lang

    def __init__(self, api: GoogleTranslateAPI, text: str, from_lang: str, to_lang: str):
        super().__init__()
        self.api = api
        self.text = text
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.is_cancelled = False
        self._placeholder_mapping = None  # For old format system backward compatibility

    def cancel(self):
        """Cancel translation operation."""
        self.is_cancelled = True

    def run(self):
        """Run translation in background."""
        try:
            if self.is_cancelled:
                return

            self.progress_updated.emit(25, "Preparing translation...")
            time.sleep(0.1)  # Allow UI update

            if self.is_cancelled:
                return

            # Session 77: NEW HTML-based approach for format preservation
            # Check if text is HTML (from ODT/DOCX extraction)
            is_html_format = '<!DOCTYPE html>' in self.text or '<html>' in self.text
            
            if is_html_format:
                # HTML format - just protect whitespace and send to Google
                # Google already knows how to preserve HTML structure
                self.progress_updated.emit(30, "Protecting whitespace...")
                from translation.html_format_mapper import protect_special_whitespace
                text_to_translate = protect_special_whitespace(self.text)
            else:
                # Plain text - check if it has old format tags (backward compatibility)
                has_format_tags = '<' in self.text and '>' in self.text and '|' in self.text
                
                if has_format_tags:
                    # Old format - use placeholder protection (Session 75)
                    from translation.format_mapper import (
                        replace_tags_with_placeholders, 
                        protect_special_whitespace
                    )
                    self.progress_updated.emit(30, "Protecting format tags...")
                    text_to_translate, self._placeholder_mapping = replace_tags_with_placeholders(self.text)
                    
                    self.progress_updated.emit(32, "Protecting whitespace...")
                    text_to_translate = protect_special_whitespace(text_to_translate)
                else:
                    # Pure plain text - no special handling
                    text_to_translate = self.text
                    self._placeholder_mapping = None

            # For large texts, split into chunks
            max_chunk_size = 5000  # Google Translate limit
            text_chunks = []

            if len(text_to_translate) > max_chunk_size:
                # Split by paragraphs/double newlines to maintain context
                if is_html_format:
                    # For HTML, split on </p> or <br><br>
                    paragraphs = text_to_translate.split("</p>")
                else:
                    # For plain text, split on double newlines
                    separator = "【BR】【BR】" if self._placeholder_mapping else "\n\n"
                    paragraphs = text_to_translate.split(separator)
                
                current_chunk = ""

                for paragraph in paragraphs:
                    if len(current_chunk + paragraph) > max_chunk_size:
                        if current_chunk:
                            text_chunks.append(current_chunk.strip())
                        current_chunk = paragraph
                    else:
                        separator_str = "</p>" if is_html_format else "\n\n"
                        current_chunk += separator_str + paragraph if current_chunk else paragraph

                if current_chunk:
                    text_chunks.append(current_chunk.strip())
            else:
                text_chunks = [text_to_translate]

            self.progress_updated.emit(50, f"Translating {len(text_chunks)} chunk(s)...")

            translated_chunks = []
            detected_language = self.from_lang  # Default to input language
            total_chunks = len(text_chunks)

            for i, chunk in enumerate(text_chunks):
                if self.is_cancelled:
                    return

                progress = 50 + int((i / total_chunks) * 35)
                self.progress_updated.emit(progress, f"Translating chunk {i+1}/{total_chunks}...")

                result = self.api.translate_text(chunk, self.from_lang, self.to_lang)

                if not result.success:
                    self.translation_completed.emit("", False, result.error_message, self.from_lang)
                    return

                translated_chunks.append(result.translated_text)
                
                # Capture detected language from first chunk
                if i == 0 and result.source_language:
                    detected_language = result.source_language

            # Combine translated chunks
            if is_html_format:
                final_result = "</p>".join(translated_chunks)
            else:
                separator = "【BR】【BR】" if self._placeholder_mapping else "\n\n"
                final_result = separator.join(translated_chunks)
            
            # Restore whitespace and format tags based on format type
            if is_html_format:
                self.progress_updated.emit(93, "Restoring whitespace...")
                from translation.html_format_mapper import restore_special_whitespace
                final_result = restore_special_whitespace(final_result)
            else:
                if self._placeholder_mapping:
                    # Old format system - restore whitespace then tags
                    from translation.format_mapper import (
                        restore_special_whitespace,
                        restore_tags_from_placeholders
                    )
                    self.progress_updated.emit(93, "Restoring whitespace...")
                    final_result = restore_special_whitespace(final_result)
                    
                    self.progress_updated.emit(96, "Restoring format tags...")
                    final_result = restore_tags_from_placeholders(final_result, self._placeholder_mapping)

            self.progress_updated.emit(100, "Translation completed!")
            self.translation_completed.emit(final_result, True, "", detected_language)

        except Exception as e:
            self.translation_completed.emit("", False, f"Translation error: {str(e)}", self.from_lang)


class GoogleTranslateDock(BaseDock):
    """
    Google Translate Dock for text and file translation.

    Provides free translation using Google Translate web interface
    with caching, retry mechanism, and support for 7 languages.
    """

    def __init__(self, parent=None):
        self.api = GoogleTranslateAPI()
        self.translation_worker = None
        self._finished_workers = []  # Keep references to finished workers
        self._last_detected_lang = None  # Store detected language from last translation
        
        # Store formatting data (backend only - never shown to user)
        self._source_segments = []  # Original document formatting (TextSegment list) - OLD SYSTEM
        self._translated_segments = []  # Translated document formatting (TextSegment list) - OLD SYSTEM
        
        # Session 77: NEW HTML format system
        self._css_manager = None  # CSS class manager for HTML-based translation
        self._source_file_path = None  # Source file path for format reference
        self._translated_html = None  # Translated HTML content
        
        super().__init__(tr("menu.tools.google_translate"), parent)

    def _setup_ui(self):
        """Setup the user interface."""
        self._create_widgets()
        self._create_layout()
        # Note: BaseDock.__init__ calls _connect_signals() automatically (line 56)
        # Do NOT call it here or signals will be connected twice!
        self._apply_tooltips()
        self._load_preferences()

    def _create_widgets(self):
        """Create UI widgets."""
        # Language selection
        self.lbl_from_lang = QLabel(tr("google_translate.lbl_from_lang"))
        self.combo_from_lang = QComboBox()
        self.combo_from_lang.addItem(tr("google_translate.auto_detect"), "auto")
        for code, name in GoogleTranslateAPI.LANGUAGES.items():
            self.combo_from_lang.addItem(f"{name} ({code.upper()})", code)

        self.lbl_to_lang = QLabel(tr("google_translate.lbl_to_lang"))
        self.combo_to_lang = QComboBox()
        for code, name in GoogleTranslateAPI.LANGUAGES.items():
            self.combo_to_lang.addItem(f"{name} ({code.upper()})", code)

        # Input type selection
        self.chk_file_mode = QCheckBox(tr("google_translate.chk_file_mode"))

        # File input (hidden by default)
        self.lbl_file = QLabel(tr("google_translate.lbl_file"))
        self.ed_file_path = QComboBox()
        self.ed_file_path.setEditable(True)
        self.btn_browse_file = QPushButton(tr("google_translate.btn_browse"))
        self.btn_browse_file.setMaximumWidth(100)

        # Text input/output widgets
        # Input panel
        self.lbl_input = QLabel(tr("google_translate.lbl_input"))
        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText(tr("google_translate.placeholder_input"))
        self.text_input.setMinimumHeight(150)

        # Set monospace font for better text editing
        font = QFont("Courier New", 10)
        self.text_input.setFont(font)

        # Output panel
        self.lbl_output = QLabel(tr("google_translate.lbl_output"))
        self.text_output = QPlainTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setMinimumHeight(150)
        self.text_output.setFont(font)

        # Action buttons
        self.btn_translate = QPushButton(tr("google_translate.btn_translate"))
        self.btn_translate.setMinimumHeight(35)

        self.btn_copy_result = QPushButton(tr("google_translate.btn_copy_result"))
        self.btn_copy_result.setEnabled(False)

        self.btn_save_as = QPushButton(tr("google_translate.btn_save_as"))
        self.btn_save_as.setEnabled(False)

        self.btn_reverse = QPushButton(tr("google_translate.btn_reverse"))
        self.btn_reverse.setEnabled(False)

        self.btn_clear = QPushButton(tr("google_translate.btn_clear"))
        self.btn_cancel = QPushButton(tr("google_translate.btn_cancel"))
        self.btn_cancel.setEnabled(False)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        self.lbl_status = QLabel(tr("google_translate.status_ready"))
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")

        # Cache info
        self.lbl_cache_info = QLabel("")
        self._update_cache_info()

    def _create_layout(self):
        """Arrange widgets in layout."""
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(self.lbl_from_lang)
        lang_layout.addWidget(self.combo_from_lang, 1)
        lang_layout.addSpacing(10)
        lang_layout.addWidget(self.lbl_to_lang)
        lang_layout.addWidget(self.combo_to_lang, 1)

        # File input layout (initially hidden)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.lbl_file)
        file_layout.addWidget(self.ed_file_path, 1)
        file_layout.addWidget(self.btn_browse_file)

        # Create splitter for input/output text areas
        splitter = QSplitter(Qt.Vertical)

        # Input panel
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.addWidget(self.lbl_input)
        input_layout.addWidget(self.text_input)

        # Output panel
        output_frame = QFrame()
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(5, 5, 5, 5)
        output_layout.addWidget(self.lbl_output)
        output_layout.addWidget(self.text_output)

        splitter.addWidget(input_frame)
        splitter.addWidget(output_frame)
        splitter.setSizes([1, 1])  # Equal sizes

        # Options layout
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.chk_file_mode)
        options_layout.addStretch()
        
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_translate)
        btn_layout.addWidget(self.btn_copy_result)
        btn_layout.addWidget(self.btn_save_as)
        btn_layout.addWidget(self.btn_reverse)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        # Main layout
        self.layout.addLayout(lang_layout)
        self.layout.addLayout(options_layout)

        # File input widgets (initially hidden)
        self.file_widgets = [self.lbl_file, self.ed_file_path, self.btn_browse_file]
        file_group = QGroupBox(tr("google_translate.group_file_selection"))
        file_group.setLayout(file_layout)
        self.layout.addWidget(file_group)
        file_group.setVisible(False)
        self.file_group = file_group

        self.layout.addWidget(splitter, 1)  # Take most space
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.lbl_status)
        self.layout.addWidget(self.lbl_cache_info)

    def _connect_signals(self):
        """Connect widget signals."""
        self.btn_translate.clicked.connect(self._translate)
        self.btn_copy_result.clicked.connect(self._copy_result)
        self.btn_save_as.clicked.connect(self._save_as)
        self.btn_reverse.clicked.connect(self._reverse_translation)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_cancel.clicked.connect(self._cancel_translation)
        self.btn_browse_file.clicked.connect(self._browse_file)

        self.chk_file_mode.toggled.connect(self._toggle_file_mode)
        self.combo_from_lang.currentTextChanged.connect(self._save_preferences)
        self.combo_to_lang.currentTextChanged.connect(self._save_preferences)

    def _apply_tooltips(self):
        """Apply tooltips to widgets."""
        self.combo_from_lang.setToolTip(
            tooltip_tr(
                "google_translate.from_lang",
                "Source language for translation. 'Auto-detect' will identify the language automatically.",
            )
        )
        self.combo_to_lang.setToolTip(
            tooltip_tr("google_translate.to_lang", "Target language for translation. Default is Portuguese (PT).")
        )
        self.chk_file_mode.setToolTip(
            tooltip_tr(
                "google_translate.file_mode", "Enable to translate entire text files instead of manual text input."
            )
        )
        self.text_input.setToolTip(
            tooltip_tr(
                "google_translate.input_text",
                "Enter or paste text to translate. Supports up to 5000 characters per chunk.",
            )
        )
        self.btn_translate.setToolTip(
            tooltip_tr(
                "google_translate.translate_btn", "Start translation using Google Translate (free web service) | Enter"
            )
        )
        self.btn_copy_result.setToolTip(
            tooltip_tr("google_translate.copy_result", "Copy translation result to clipboard | Ctrl+C")
        )
        self.btn_clear.setToolTip(
            tooltip_tr("google_translate.clear_btn", "Clear input and output text areas | Ctrl+L")
        )

    def _load_preferences(self):
        """Load saved preferences."""
        # Set default language combo selections
        # From: Auto-detect (index 0)
        self.combo_from_lang.setCurrentIndex(0)

        # To: Portuguese (find 'pt' in combo data)
        for i in range(self.combo_to_lang.count()):
            if self.combo_to_lang.itemData(i) == "pt":
                self.combo_to_lang.setCurrentIndex(i)
                break

    def _save_preferences(self):
        """Save user preferences (placeholder for QSettings)."""
        pass  # Could implement QSettings here

    def _toggle_file_mode(self, enabled: bool):
        """Toggle between text and file input modes."""
        self.file_group.setVisible(enabled)

        if enabled:
            self.text_input.setPlaceholderText(tr("google_translate.placeholder_file_content"))
            self.text_input.setReadOnly(True)
            self.lbl_input.setText(tr("google_translate.lbl_file_content"))
        else:
            self.text_input.setPlaceholderText(tr("google_translate.placeholder_text"))
            self.text_input.setReadOnly(False)
            self.lbl_input.setText(tr("google_translate.lbl_input"))

    def _browse_file(self):
        """Browse for file to translate (supports .txt, .docx, .odt)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Translate",
            "",
            "Text Files (*.txt);;Word Documents (*.docx);;OpenDocument (*.odt);;All Files (*)"
        )

        if file_path:
            try:
                # Use format mapper for DOCX/ODT files to extract formatting
                if file_path.lower().endswith('.docx'):
                    # Extract formatted text with tags (backend only)
                    formatted_text_with_tags = FormatMapper.extract_formatted_text_from_docx(file_path)
                    
                    # Parse tags to get segments (store formatting)
                    self._source_segments = FormatMapper.parse_tagged_text(formatted_text_with_tags)
                    
                    # Extract ONLY plain text for UI display (no tags visible to user)
                    plain_text = FormatMapper.extract_plain_text_from_segments(self._source_segments)
                    
                    self.lbl_status.setText(f"DOCX loaded with formatting. {len(plain_text)} characters.")
                elif file_path.lower().endswith('.odt'):
                    # Session 77: NEW HTML-based format system
                    from translation.html_format_mapper import HTMLFormatMapper
                    
                    # Extract as HTML (with CSS formatting)
                    html_content, css_manager_or_path = HTMLFormatMapper.extract_html_from_odt(file_path)
                    
                    # Store CSS manager for later ODT creation
                    self._css_manager = css_manager_or_path
                    self._source_file_path = file_path
                    
                    # Parse HTML to extract plain text for UI preview
                    from html.parser import HTMLParser
                    
                    class TextExtractor(HTMLParser):
                        def __init__(self):
                            super().__init__()
                            self.text_parts = []
                        
                        def handle_data(self, data):
                            if data.strip():
                                self.text_parts.append(data.strip())
                        
                        def get_text(self):
                            return ' '.join(self.text_parts)
                    
                    extractor = TextExtractor()
                    extractor.feed(html_content)
                    plain_text = extractor.get_text()
                    
                    self.lbl_status.setText(f"ODT loaded with HTML formatting. {len(plain_text)} characters.")
                    
                    # Store empty segments (HTML system doesn't use segments)
                    self._source_segments = []
                else:
                    # Use plain text parser for other file types
                    plain_text = extract_text_from_document(file_path)
                    self._source_segments = []  # No formatting for plain text files
                    self.lbl_status.setText(f"File loaded successfully. {len(plain_text)} characters.")

                self.ed_file_path.setCurrentText(file_path)
                self.text_input.setPlainText(plain_text[:5000])  # Show preview (plain text only)

                if len(plain_text) > 5000:
                    current_status = self.lbl_status.text()
                    self.lbl_status.setText(f"{current_status} Showing first 5000 chars.")

            except DocumentParserError as e:
                QMessageBox.warning(
                    self, tr("google_translate.msg_file_error_title"), f"Could not parse file:\n{str(e)}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, tr("google_translate.msg_file_error_title"), tr("google_translate.msg_file_error_read").format(str(e))
                )

    def _translate(self):
        """Start translation process."""
        # Get text to translate
        text_to_translate = ""

        if self.chk_file_mode.isChecked():
            # File mode - read full file using document parser
            file_path = self.ed_file_path.currentText().strip()
            if not file_path:
                QMessageBox.warning(
                    self, tr("google_translate.msg_no_file_title"), tr("google_translate.msg_no_file_msg")
                )
                return

            try:
                # Use format mapper for DOCX/ODT files to extract formatting
                if file_path.lower().endswith('.docx'):
                    # Extract formatted text with tags (backend only)
                    formatted_text_with_tags = FormatMapper.extract_formatted_text_from_docx(file_path)
                    
                    # Parse tags to get segments (store formatting)
                    self._source_segments = FormatMapper.parse_tagged_text(formatted_text_with_tags)
                    
                    # Keep tagged text for translation (tags go to Google Translate)
                    text_to_translate = formatted_text_with_tags
                elif file_path.lower().endswith('.odt'):
                    # Session 77: NEW HTML-based format system
                    from translation.html_format_mapper import HTMLFormatMapper
                    
                    # Extract as HTML (with CSS formatting)
                    html_content, css_manager_or_path = HTMLFormatMapper.extract_html_from_odt(file_path)
                    
                    # Store CSS manager for later ODT creation
                    self._css_manager = css_manager_or_path
                    self._source_file_path = file_path
                    
                    # Store empty segments (HTML system doesn't use segments)
                    self._source_segments = []
                    
                    # Keep HTML for translation (Google Translate will preserve HTML structure)
                    text_to_translate = html_content
                else:
                    # Use plain text parser for other file types
                    text_to_translate = extract_text_from_document(file_path)
                    self._source_segments = []  # No formatting for plain text files
            except DocumentParserError as e:
                QMessageBox.warning(
                    self,
                    tr("google_translate.msg_file_error_title"),
                    f"Could not parse file:\n{str(e)}"
                )
                return
            except Exception as e:
                QMessageBox.warning(
                    self,
                    tr("google_translate.msg_file_error_title"),
                    tr("google_translate.msg_file_error_read").format(str(e)),
                )
                return
        else:
            # Text mode - get plain text from UI
            text_to_translate = self.text_input.toPlainText().strip()
            if not text_to_translate:
                QMessageBox.warning(
                    self, tr("google_translate.msg_no_text_title"), tr("google_translate.msg_no_text_msg")
                )
                return

        # Get language selections
        from_lang = self.combo_from_lang.currentData()
        to_lang = self.combo_to_lang.currentData()

        if from_lang == to_lang and from_lang != "auto":
            QMessageBox.warning(
                self, tr("google_translate.msg_same_language_title"), tr("google_translate.msg_same_language_msg")
            )
            return

        # Start translation in background
        self._start_translation(text_to_translate, from_lang, to_lang)

    def _start_translation(self, text: str, from_lang: str, to_lang: str):
        """Start background translation."""
        # Prevent starting new worker while one is running (fixes crash on duplicate calls)
        if self.translation_worker and self.translation_worker.isRunning():
            return
        
        # Disconnect signals from previous worker if it exists
        if self.translation_worker:
            try:
                self.translation_worker.progress_updated.disconnect()
                self.translation_worker.translation_completed.disconnect()
                self.translation_worker.finished.disconnect()
            except (TypeError, RuntimeError):
                # Signals already disconnected or worker deleted
                pass
        
        # Update UI for translation in progress
        self.btn_translate.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(tr("google_translate.status_starting"))
        self.text_output.clear()

        # Create and start worker
        self.translation_worker = TranslationWorker(self.api, text, from_lang, to_lang)
        
        # Connect signals BEFORE starting thread
        self.translation_worker.progress_updated.connect(self._on_progress_updated)
        self.translation_worker.translation_completed.connect(self._on_translation_completed)
        
        # Store finished workers to prevent premature deletion
        # For QThread subclass, do NOT use finished->deleteLater pattern
        self.translation_worker.finished.connect(lambda: self._on_worker_finished(self.translation_worker))
        
        self.translation_worker.start()

    def _on_progress_updated(self, progress: int, status: str):
        """Handle progress updates."""
        self.progress_bar.setValue(progress)
        self.lbl_status.setText(status)

    def _on_translation_completed(self, result: str, success: bool, error: str, detected_lang: str):
        """Handle translation completion."""
        # Reset UI
        self.btn_translate.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)

        if success:
            # Session 77: Check if result is HTML (from new format system)
            is_html_format = '<!DOCTYPE html>' in result or '<html>' in result
            
            if is_html_format:
                # HTML format - extract plain text for UI display
                from html.parser import HTMLParser
                
                class TextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.text_parts = []
                    
                    def handle_data(self, data):
                        if self.get_starttag_text() and 'style' not in self.get_starttag_text():
                            if data.strip():
                                self.text_parts.append(data.strip())
                    
                    def get_text(self):
                        return '\n'.join(self.text_parts)
                
                extractor = TextExtractor()
                extractor.feed(result)
                plain_text = extractor.get_text()
                
                # Store translated HTML for ODT creation
                self._translated_html = result
                self._translated_segments = []  # Not used in HTML system
            else:
                # Old format system or plain text
                # Parse tags from translation result (backend only)
                self._translated_segments = FormatMapper.parse_tagged_text(result)
                
                # Extract ONLY plain text for UI display (hide tags from user)
                plain_text = FormatMapper.extract_plain_text_from_segments(self._translated_segments)
                
                self._translated_html = None
            
            # Display plain text in output box (NO TAGS VISIBLE)
            self.text_output.setPlainText(plain_text)
            self.btn_copy_result.setEnabled(True)
            self.btn_save_as.setEnabled(True)
            self.btn_reverse.setEnabled(True)
            self._last_detected_lang = detected_lang  # Store detected language
            self.lbl_status.setText(tr("google_translate.status_completed"))
            self.lbl_status.setStyleSheet("color: #22C55E; font-weight: bold;")
        else:
            self.text_output.setPlainText(f"Translation failed: {error}")
            self.btn_copy_result.setEnabled(False)
            self.btn_save_as.setEnabled(False)
            self.lbl_status.setText(tr("google_translate.status_failed"))
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: bold;")

        # Update cache info
        self._update_cache_info()

        # Reset status color after delay
        QTimer.singleShot(5000, lambda: self.lbl_status.setStyleSheet("color: #666; font-style: italic;"))

        # Worker cleanup handled by _on_worker_finished
        self.translation_worker = None

    def _on_worker_finished(self, worker):
        """Handle worker thread finishing - keep reference alive."""
        self._finished_workers.append(worker)
        # Clean up old finished workers after delay to allow proper Qt cleanup
        QTimer.singleShot(1000, self._cleanup_old_workers)

    def _cleanup_old_workers(self):
        """Clean up finished worker references."""
        self._finished_workers = [w for w in self._finished_workers if w.isRunning()]

    def _cancel_translation(self):
        """Cancel ongoing translation."""
        if self.translation_worker and self.translation_worker.isRunning():
            self.translation_worker.cancel()
            self.translation_worker.terminate()

            self.btn_translate.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.lbl_status.setText(tr("google_translate.text_cancelled"))

    def _clear(self):
        """Clear all input and output fields."""
        self.text_input.clear()
        self.text_output.clear()
        self.ed_file_path.clearEditText()
        self.btn_copy_result.setEnabled(False)
        self.btn_save_as.setEnabled(False)
        self.btn_reverse.setEnabled(False)
        self.lbl_status.setText(tr("google_translate.status_ready"))
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")

    def _reverse_translation(self):
        """Reverse source and target languages, swap input/output text, and auto-translate."""
        # Check if translation is currently running - if so, ignore the click
        if self.translation_worker and self.translation_worker.isRunning():
            return
        
        # Get current language codes (not display text)
        from_code = self.combo_from_lang.currentData()
        to_code = self.combo_to_lang.currentData()
        
        # Store the output text before swapping (this will become the new input)
        output_text = self.text_output.toPlainText()
        
        # Also store translated segments with formatting for document mode
        has_formatting = bool(self._translated_segments)
        
        # Swap languages
        if from_code == "auto":
            # Use detected language if available, otherwise keep auto-detect
            if self._last_detected_lang:
                # Set From to target language, To to detected language
                from_index = self.combo_from_lang.findData(to_code)
                to_index = self.combo_to_lang.findData(self._last_detected_lang)
                
                if from_index >= 0:
                    self.combo_from_lang.setCurrentIndex(from_index)
                if to_index >= 0:
                    self.combo_to_lang.setCurrentIndex(to_index)
        else:
            # Normal swap when From is not auto-detect
            from_index = self.combo_from_lang.findData(to_code)
            to_index = self.combo_to_lang.findData(from_code)
            
            if from_index >= 0:
                self.combo_from_lang.setCurrentIndex(from_index)
            if to_index >= 0:
                self.combo_to_lang.setCurrentIndex(to_index)
        
        # Swap input/output text
        input_text = self.text_input.toPlainText()
        
        self.text_input.setPlainText(output_text)
        self.text_output.clear()  # Clear output before auto-translation
        
        # Swap formatting segments if we have them (for document mode)
        if has_formatting:
            # Swap source and translated segments
            self._source_segments, self._translated_segments = self._translated_segments, self._source_segments
        
        # Auto-trigger translation with the swapped text
        if output_text.strip():
            # Get new language selections after swap
            new_from_lang = self.combo_from_lang.currentData()
            new_to_lang = self.combo_to_lang.currentData()
            
            # Prepare text for translation (with formatting tags if available)
            if has_formatting and self._source_segments:
                # Use tagged text for translation to preserve formatting
                text_to_translate = "".join(seg.to_tagged_text() for seg in self._source_segments)
            else:
                # Plain text mode
                text_to_translate = output_text
            
            # Start automatic translation
            self._start_translation(text_to_translate, new_from_lang, new_to_lang)

    def _copy_result(self):
        """Copy translation result to clipboard."""
        result = self.text_output.toPlainText()
        if result:
            clipboard = QApplication.clipboard()
            clipboard.setText(result)

            # Visual feedback
            self.btn_copy_result.setText(tr("google_translate.btn_copied"))
            QTimer.singleShot(2000, lambda: self.btn_copy_result.setText(tr("google_translate.btn_copy_result")))

    def _save_as(self):
        """Save translation result to file (TXT, DOCX, or ODT based on dropdown selection)."""
        result = self.text_output.toPlainText()
        if not result:
            return
        
        # Determine default format based on whether we have stored formatting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"translation_{timestamp}"  # NO extension - dropdown determines it
        
        if self._translated_segments:
            # Has formatting data - suggest DOCX first
            file_filter = "Word Documents (*.docx);;OpenDocument (*.odt);;Text Files (*.txt)"
        else:
            # Plain text - suggest TXT first
            file_filter = "Text Files (*.txt);;Word Documents (*.docx);;OpenDocument (*.odt)"
        
        # Open save file dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            tr("google_translate.save_dialog_title"),
            default_filename,
            file_filter
        )
        
        if file_path:
            try:
                # Determine extension from selected filter (dropdown)
                if 'docx' in selected_filter.lower() or 'word' in selected_filter.lower():
                    # User selected Word Documents
                    if not file_path.lower().endswith('.docx'):
                        file_path += '.docx'
                    self._save_as_docx(file_path)
                    
                elif 'odt' in selected_filter.lower() or 'opendocument' in selected_filter.lower():
                    # User selected OpenDocument
                    if not file_path.lower().endswith('.odt'):
                        file_path += '.odt'
                    self._save_as_odt(file_path)
                    
                else:
                    # User selected Text Files (or unknown - default to TXT)
                    if not file_path.lower().endswith('.txt'):
                        file_path += '.txt'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result)
                 
                # Visual feedback
                original_text = self.btn_save_as.text()
                self.btn_save_as.setText(tr("google_translate.btn_saved"))
                QTimer.singleShot(2000, lambda: self.btn_save_as.setText(original_text))
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    tr("google_translate.save_error_title"),
                    tr("google_translate.save_error_msg").format(str(e))
                )
    
    def _save_as_docx(self, output_path: str):
        """
        Save translation as DOCX with formatting restored from stored segments.
        
        Args:
            output_path: Path to save DOCX file
        """
        if not self._translated_segments:
            # Fallback: no formatting, create plain text segment
            plain_text = self.text_output.toPlainText()
            
            # CRITICAL: Remove any system tags that might have leaked into UI
            # Only remove numeric tags (Clarify system), preserve user tags like <div>
            plain_text = FormatMapper.remove_tags(plain_text)
            
            from ..translation.format_mapper import TextSegment
            self._translated_segments = [TextSegment(text=plain_text)]
        
        # Generate DOCX with formatting using stored segments
        FormatMapper.create_docx_from_segments(self._translated_segments, output_path)
        
        # Update status
        self.lbl_status.setText(tr("google_translate.status_docx_saved"))
        self.lbl_status.setStyleSheet("color: #22C55E; font-weight: bold;")
        QTimer.singleShot(3000, lambda: self.lbl_status.setStyleSheet("color: #666; font-style: italic;"))

    def _save_as_odt(self, output_path: str):
        """
        Save translation as ODT with formatting restored.
        
        Session 77: Uses NEW HTML-based format system if available.
        Falls back to old segment system for backward compatibility.
        
        Args:
            output_path: Path to save ODT file
        """
        if self._translated_html and self._css_manager:
            # Session 77: NEW HTML system - use HTML to ODT conversion
            from translation.html_format_mapper import create_odt_from_html
            create_odt_from_html(self._translated_html, self._css_manager, output_path)
            
        elif self._translated_segments:
            # OLD system - use segment-based approach (backward compatibility)
            FormatMapper.create_odt_from_segments(self._translated_segments, output_path)
            
        else:
            # Fallback: no formatting, create plain text segment
            plain_text = self.text_output.toPlainText()
            
            # CRITICAL: Remove any system tags that might have leaked into UI
            plain_text = FormatMapper.remove_tags(plain_text)
            
            from ..translation.format_mapper import TextSegment
            self._translated_segments = [TextSegment(text=plain_text)]
            FormatMapper.create_odt_from_segments(self._translated_segments, output_path)
        
        # Update status
        self.lbl_status.setText(tr("google_translate.status_odt_saved"))
        self.lbl_status.setStyleSheet("color: #22C55E; font-weight: bold;")
        QTimer.singleShot(3000, lambda: self.lbl_status.setStyleSheet("color: #666; font-style: italic;"))

    def closeEvent(self, event):
        """Handle dock close event - wait for running threads."""
        if self.translation_worker and self.translation_worker.isRunning():
            # Cancel and wait for thread to finish
            self.translation_worker.cancel()
            if not self.translation_worker.wait(3000):  # Wait up to 3 seconds
                self.translation_worker.terminate()
                self.translation_worker.wait()
        
        # Wait for any finished workers
        for worker in self._finished_workers:
            if worker.isRunning():
                worker.wait(1000)
        
        super().closeEvent(event)

    def _update_cache_info(self):
        """Update cache information display."""
        try:
            cache_info = self.api.get_cache_info()
            entries = cache_info["entries"]
            size_kb = cache_info["file_size_bytes"] / 1024

            self.lbl_cache_info.setText(f"Cache: {entries} translations, {size_kb:.1f} KB")
            self.lbl_cache_info.setStyleSheet("color: #888; font-size: 10px;")
        except Exception:
            self.lbl_cache_info.setText(tr("google_translate.cache_na"))
