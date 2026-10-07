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
    QMenu,
)
from PySide6.QtGui import QAction, QFont

from ..gui.base_dock import BaseDock
from ..translation.google_translate import GoogleTranslateAPI, TranslationResult
from ..translation.document_parser import extract_text_from_document, DocumentParserError
from ..translation.format_mapper import FormatMapper
from ..translation.notebook_translation import (
    NotebookFormatError,
    load_notebook,
    markdown_cell_count,
    notebook_markdown_text,
    save_notebook,
    translate_markdown_cells,
)
from ..translation.pdf_translation import PdfExtractionError, extract_pdf_text
from ..translation.recent_paths import (
    TranslationRecentPaths,
    record_translation_operation,
)
from ..i18n import tr, tooltip_tr
from ..ui import FeatureType, thread_manager


class TranslationWorker(QThread):
    """Background worker for translation operations."""

    progress_updated = Signal(int, str)  # progress, status
    translation_completed = Signal(str, bool, str, str)  # result, success, error, detected_lang
    chunk_progress = Signal(int, int, int, str)  # Phase B: current_chunk, total_chunks, percentage, status_msg

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

            # Phase B: Use new chunked translation API with progress callback
            def progress_callback(current_chunk, total_chunks, percentage, status_msg):
                """Progress callback for chunked translation."""
                if self.is_cancelled:
                    return
                
                # Emit chunk progress signal (for detailed tracking)
                self.chunk_progress.emit(current_chunk, total_chunks, percentage, status_msg)
                
                # Update main progress bar (50-95% range for translation)
                # 0-30% already used for preparation, 95-100% for restoration
                translation_progress = 50 + int(percentage * 0.45)
                self.progress_updated.emit(translation_progress, status_msg)
            
            self.progress_updated.emit(50, "Starting translation...")
            
            # Use new chunked translation API (automatically chunks if > 4500 chars)
            result = self.api.translate_text_chunked(
                text_to_translate,
                self.from_lang,
                self.to_lang,
                progress_callback=progress_callback,
                cancel_callback=lambda: self.is_cancelled,
            )

            if self.is_cancelled:
                return

            if not result.success:
                self.translation_completed.emit("", False, result.error_message, self.from_lang)
                return
            
            final_result = result.translated_text
            detected_language = result.source_language or self.from_lang
            
            # Restore whitespace and format tags based on format type
            if is_html_format:
                self.progress_updated.emit(96, "Restoring whitespace...")
                from translation.html_format_mapper import restore_special_whitespace
                final_result = restore_special_whitespace(final_result)
            else:
                if self._placeholder_mapping:
                    # Old format system - restore whitespace then tags
                    from translation.format_mapper import (
                        restore_special_whitespace,
                        restore_tags_from_placeholders
                    )
                    self.progress_updated.emit(96, "Restoring whitespace...")
                    final_result = restore_special_whitespace(final_result)
                    
                    self.progress_updated.emit(98, "Restoring format tags...")
                    final_result = restore_tags_from_placeholders(final_result, self._placeholder_mapping)

            self.progress_updated.emit(100, "Translation completed!")
            self.translation_completed.emit(final_result, True, "", detected_language)

        except Exception as e:
            if not self.is_cancelled:
                self.translation_completed.emit(
                    "", False, f"Translation error: {str(e)}", self.from_lang
                )


class _NotebookTranslationCancelled(Exception):
    """Internal control flow for a cancelled notebook worker."""


class NotebookTranslationWorker(QThread):
    """Translate notebook Markdown cells without exposing code or outputs."""

    progress_updated = Signal(int, str)
    chunk_progress = Signal(int, int, int, str)
    translation_completed = Signal(object, str, bool, str, str)

    def __init__(self, api, notebook, from_lang: str, to_lang: str):
        super().__init__()
        self.api = api
        self.notebook = notebook
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.is_cancelled = False

    def cancel(self):
        """Request cancellation before the next Markdown cell."""
        self.is_cancelled = True

    def run(self):
        """Translate Markdown cells sequentially in the worker thread."""
        try:
            total_cells = markdown_cell_count(self.notebook)
            if total_cells == 0:
                self.translation_completed.emit(
                    None,
                    "",
                    False,
                    tr("google_translate.error_notebook_no_markdown"),
                    self.from_lang,
                )
                return

            completed_cells = 0
            detected_language = self.from_lang

            def translate_cell(text: str) -> str:
                nonlocal completed_cells, detected_language
                if self.is_cancelled:
                    raise _NotebookTranslationCancelled()

                cell_number = completed_cells + 1

                def report_chunk(_current, _total, percentage, status):
                    overall = int(
                        ((completed_cells + (percentage / 100)) / total_cells) * 100
                    )
                    self.chunk_progress.emit(
                        cell_number, total_cells, overall, status
                    )
                    self.progress_updated.emit(overall, status)

                result = self.api.translate_text_chunked(
                    text,
                    self.from_lang,
                    self.to_lang,
                    progress_callback=report_chunk,
                    cancel_callback=lambda: self.is_cancelled,
                )
                if self.is_cancelled:
                    raise _NotebookTranslationCancelled()
                if not result.success:
                    raise RuntimeError(result.error_message)
                if completed_cells == 0 and result.source_language:
                    detected_language = result.source_language
                completed_cells += 1
                self.progress_updated.emit(
                    int((completed_cells / total_cells) * 100),
                    tr("google_translate.status_notebook_cell").format(
                        current=completed_cells, total=total_cells
                    ),
                )
                return result.translated_text

            translate_markdown_cells(self.notebook, translate_cell)
            if self.is_cancelled:
                return
            preview = notebook_markdown_text(self.notebook)
            self.translation_completed.emit(
                self.notebook, preview, True, "", detected_language
            )
        except _NotebookTranslationCancelled:
            return
        except Exception as exc:
            self.translation_completed.emit(
                None,
                "",
                False,
                f"Notebook translation error: {exc}",
                self.from_lang,
            )


class GoogleTranslateDock(BaseDock):
    """
    Google Translate Dock for text and file translation.

    Provides free translation using Google Translate web interface
    with caching, retry mechanism, and support for 7 languages.
    """

    open_in_editor_requested = Signal(str, str)

    def __init__(self, parent=None):
        self._main_window_ref = parent
        self.api = GoogleTranslateAPI()
        self.recent_paths = TranslationRecentPaths()
        self.translation_worker = None
        self._close_action = None
        self._cancel_requested = False
        self._thread_id = f"google_translate:{id(self)}"
        self._last_detected_lang = None  # Store detected language from last translation
        self._pending_history_details = None
        
        # Store formatting data (backend only - never shown to user)
        self._source_segments = []  # Original document formatting (TextSegment list) - OLD SYSTEM
        self._translated_segments = []  # Translated document formatting (TextSegment list) - OLD SYSTEM
        
        # Session 77: NEW HTML format system
        self._css_manager = None  # CSS class manager for HTML-based translation
        self._source_file_path = None  # Source file path for format reference
        self._translated_html = None  # Translated HTML content
        self._translated_notebook = None
        
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
        
        # Language swap button
        self.btn_swap_languages = QPushButton("⇄")  # Unicode swap arrows
        self.btn_swap_languages.setMaximumWidth(40)
        self.btn_swap_languages.setToolTip(tr("google_translate.tooltip_swap_languages") if "tooltip_swap_languages" in dir(tr) else "Swap source and target languages")
        self.btn_swap_languages.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Input type selection
        self.chk_file_mode = QCheckBox(tr("google_translate.chk_file_mode"))

        # File input (hidden by default)
        self.lbl_file = QLabel(tr("google_translate.lbl_file"))
        self.ed_file_path = QComboBox()
        self.ed_file_path.setEditable(True)
        self.btn_recent_file = QPushButton(tr("translation_recent.btn_recent"))
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

        self.btn_open_in_editor = QPushButton(
            tr("google_translate.btn_open_in_editor")
        )
        self.btn_open_in_editor.setEnabled(False)

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
        # Language selection with swap button
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(self.lbl_from_lang)
        lang_layout.addWidget(self.combo_from_lang, 1)
        lang_layout.addSpacing(10)
        lang_layout.addWidget(self.btn_swap_languages)  # Swap button between languages
        lang_layout.addSpacing(10)
        lang_layout.addWidget(self.lbl_to_lang)
        lang_layout.addWidget(self.combo_to_lang, 1)

        # File input layout (initially hidden)
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.lbl_file)
        file_layout.addWidget(self.ed_file_path, 1)
        file_layout.addWidget(self.btn_recent_file)
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
        btn_layout.addWidget(self.btn_open_in_editor)
        btn_layout.addWidget(self.btn_reverse)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        # Main layout
        self.layout.addLayout(lang_layout)
        self.layout.addLayout(options_layout)

        # File input widgets (initially hidden)
        self.file_widgets = [
            self.lbl_file,
            self.ed_file_path,
            self.btn_recent_file,
            self.btn_browse_file,
        ]
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
        self.btn_open_in_editor.clicked.connect(self._open_result_in_editor)
        self.btn_reverse.clicked.connect(self._reverse_translation)
        self.btn_clear.clicked.connect(self._clear)
        self.btn_cancel.clicked.connect(self._cancel_translation)
        self.btn_browse_file.clicked.connect(self._browse_file)
        self.btn_recent_file.clicked.connect(self._show_recent_files)
        self.btn_swap_languages.clicked.connect(self._swap_languages)  # New swap button

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
        self.btn_recent_file.setToolTip(tooltip_tr("translation_recent.source"))
        self.btn_recent_file.setAccessibleName("Google Translate - Button - Recent Files")
        self.btn_recent_file.setAccessibleDescription(
            "Select or clear recently used translation source files"
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
        self.btn_open_in_editor.setToolTip(
            tooltip_tr(
                "google_translate.open_in_editor",
                "Open the translated text in Clarify Editor for review and editing.",
            )
        )
        self.btn_clear.setToolTip(
            tooltip_tr("google_translate.clear_btn", "Clear input and output text areas | Ctrl+L")
        )

    def _load_preferences(self):
        """Load saved preferences."""
        self._refresh_recent_files()
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

    def _refresh_recent_files(self) -> None:
        """Populate the editable file combo without replacing typed text."""
        current_path = self.ed_file_path.currentText()
        self.ed_file_path.blockSignals(True)
        self.ed_file_path.clear()
        self.ed_file_path.addItems(
            path for path in self.recent_paths.get("source") if os.path.isfile(path)
        )
        self.ed_file_path.setCurrentIndex(-1)
        self.ed_file_path.setEditText(current_path)
        self.ed_file_path.blockSignals(False)

    def _show_recent_files(self) -> None:
        """Show recently used translation source files."""
        recent = [
            path for path in self.recent_paths.get("source") if os.path.isfile(path)
        ]
        if not recent:
            QMessageBox.information(
                self,
                tr("translation_recent.empty_title"),
                tr("translation_recent.empty_message"),
            )
            return

        menu = QMenu(self)
        for path in recent:
            action = QAction(path, menu)
            action.triggered.connect(
                lambda _checked=False, selected=path: self._select_recent_file(selected)
            )
            menu.addAction(action)
        menu.addSeparator()
        clear_action = QAction(tr("translation_recent.clear"), menu)
        clear_action.triggered.connect(self._clear_recent_files)
        menu.addAction(clear_action)
        menu.exec(self.btn_recent_file.mapToGlobal(self.btn_recent_file.rect().bottomLeft()))

    def _select_recent_file(self, path: str) -> None:
        """Select a recent file without starting a network operation."""
        self.ed_file_path.setCurrentText(path)

    def _clear_recent_files(self) -> None:
        """Clear translation source history and refresh the combo."""
        self.recent_paths.clear("source")
        self._refresh_recent_files()

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
        """Browse for a supported file to translate."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Translate",
            "",
            "Text Files (*.txt);;Jupyter Notebooks (*.ipynb);;PDF Documents (*.pdf);;Word Documents (*.docx);;OpenDocument (*.odt);;All Files (*)"
        )

        if file_path:
            # Phase A: Clear previous translation state on new file load
            self._translated_html = None
            self._translated_notebook = None
            self._translated_segments = []
            self._css_manager = None
            self._image_manager = None
            self._table_manager = None
            self.text_output.clear()
            
            try:
                # Use format mapper for DOCX/ODT files to extract formatting
                if file_path.lower().endswith('.ipynb'):
                    notebook = load_notebook(file_path)
                    plain_text = notebook_markdown_text(notebook)
                    cell_count = markdown_cell_count(notebook)
                    self._source_file_path = file_path
                    self._source_segments = []
                    self.lbl_status.setText(
                        tr("google_translate.status_notebook_loaded").format(
                            count=cell_count
                        )
                    )
                elif file_path.lower().endswith('.pdf'):
                    extraction = extract_pdf_text(file_path)
                    plain_text = extraction.text
                    self._source_file_path = file_path
                    self._source_segments = []
                    self.lbl_status.setText(
                        tr("google_translate.status_pdf_loaded").format(
                            pages=extraction.page_count
                        )
                    )
                elif file_path.lower().endswith('.docx'):
                    # Session COM8: NEW HTML-based format system for DOCX (with image and table support)
                    from translation.docx_html_mapper import extract_html_from_docx
                    
                    # Extract as HTML (with CSS formatting, images, and tables)
                    html_content, css_manager, image_manager, table_manager = extract_html_from_docx(file_path)
                    
                    # Store managers for later DOCX creation
                    self._css_manager = css_manager
                    self._image_manager = image_manager
                    self._table_manager = table_manager
                    self._source_file_path = file_path
                    
                    # Parse HTML to extract plain text for UI preview (with tabs, line-breaks, and tables)
                    from html.parser import HTMLParser
                    import html as html_module
                    
                    class TextExtractor(HTMLParser):
                        def __init__(self):
                            super().__init__()
                            self.text_parts = []
                            self.in_head = False
                            self.in_table = False
                            self.table_row_cells = []
                        
                        def handle_starttag(self, tag, attrs):
                            if tag in ('head', 'style', 'meta'):
                                self.in_head = True
                            elif tag == 'br':
                                attr_dict = dict(attrs)
                                classes = attr_dict.get('class', '').split()
                                # Both brk1 (paragraph) and brk2 (line-break) show as newline in preview
                                self.text_parts.append('\n')
                            elif tag == 'span':
                                # Check for tab marker
                                attr_dict = dict(attrs)
                                if 'data-tab' in attr_dict:
                                    self.text_parts.append('\t')  # Add tab character
                                # Check for image marker (show placeholder in preview)
                                elif 'data-image' in attr_dict:
                                    image_id = attr_dict['data-image']
                                    self.text_parts.append(f'[{image_id}]')  # Show [IMG001] in preview
                            elif tag == 'table':
                                # Show table marker in preview
                                attr_dict = dict(attrs)
                                table_id = attr_dict.get('data-table', 'TABLE')
                                self.text_parts.append(f'\n[{table_id}]\n')
                                self.in_table = True
                            elif tag == 'tr' and self.in_table:
                                self.table_row_cells = []
                            elif tag == 'td' and self.in_table:
                                pass  # Cell content will be added via handle_data
                        
                        def handle_endtag(self, tag):
                            if tag in ('head', 'style'):
                                self.in_head = False
                            elif tag == 'td' and self.in_table:
                                pass  # Cell ended
                            elif tag == 'tr' and self.in_table:
                                # Row ended - add separator
                                pass
                            elif tag == 'table':
                                self.in_table = False
                                self.text_parts.append('\n')
                        
                        def handle_data(self, data):
                            if not self.in_head and data.strip():
                                self.text_parts.append(html_module.unescape(data))
                        
                        def get_text(self):
                            return ''.join(self.text_parts)
                    
                    extractor = TextExtractor()
                    extractor.feed(html_content)
                    plain_text = extractor.get_text()
                    
                    # Display preview in UI (with tabs visible)
                    self.text_input.setPlainText(plain_text)
                    self.lbl_status.setText(f"DOCX loaded with formatting. {len(plain_text)} characters.")
                elif file_path.lower().endswith('.odt'):
                    # Session 77: NEW HTML-based format system
                    from translation.html_format_mapper import HTMLFormatMapper
                    
                    # Extract as HTML (with CSS formatting, images, and tables) - Phase 2 COM8
                    html_content, css_manager_or_path, image_manager, table_manager = HTMLFormatMapper.extract_html_from_odt(file_path)
                    
                    # Store managers for later ODT creation
                    self._css_manager = css_manager_or_path
                    self._image_manager = image_manager  # Phase 1: Store image manager
                    self._table_manager = table_manager  # Phase 2: Store table manager
                    self._source_file_path = file_path
                    
                    # Parse HTML to extract plain text for UI preview
                    from html.parser import HTMLParser
                    import html as html_module
                    
                    class TextExtractor(HTMLParser):
                        def __init__(self):
                            super().__init__()
                            self.text_parts = []
                            self.current_tag = None
                            self.current_class = None
                            self.prev_class = None
                            # Header classes (bold/large text that should have newlines around them)
                            self.header_classes = ['fmt1', 'fmt3', 'fmt4', 'fmt5', 'fmt7']
                        
                        def handle_starttag(self, tag, attrs):
                            if tag == 'br':
                                # Line break
                                self.text_parts.append('\n')
                                self.current_tag = tag
                                return
                            
                            if tag == 'span':
                                new_class = None
                                for attr, value in attrs:
                                    if attr == 'class':
                                        new_class = value
                                        break
                                
                                # Add newline on format class transition (header ↔ body)
                                if self.prev_class and new_class and self.prev_class != new_class:
                                    prev_is_header = self.prev_class in self.header_classes
                                    new_is_header = new_class in self.header_classes
                                    
                                    # Newline if entering or leaving header format
                                    if prev_is_header != new_is_header:
                                        self.text_parts.append('\n')
                                
                                self.current_class = new_class
                            
                            self.current_tag = tag
                        
                        def handle_endtag(self, tag):
                            if tag == 'span' and self.current_class:
                                self.prev_class = self.current_class
                            if tag == self.current_tag:
                                self.current_tag = None
                        
                        def handle_data(self, data):
                            # Skip data inside style/script/head tags
                            if self.current_tag in ['style', 'script', 'head', 'title']:
                                return
                            
                            # Inside content tags - decode entities and keep ALL content (including whitespace)
                            # Outside content tags - only keep if has non-whitespace (ignore HTML formatting)
                            if self.current_tag in ['span', 'p', 'div']:
                                decoded = html_module.unescape(data)
                                self.text_parts.append(decoded)
                            elif data.strip():
                                decoded = html_module.unescape(data)
                                self.text_parts.append(decoded)
                        
                        def get_text(self):
                            return ''.join(self.text_parts)
                    
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
                self.recent_paths.add("source", file_path)
                self._refresh_recent_files()
                self.ed_file_path.setCurrentText(file_path)
                self.text_input.setPlainText(plain_text[:5000])  # Show preview (plain text only)

                if len(plain_text) > 5000:
                    current_status = self.lbl_status.text()
                    self.lbl_status.setText(f"{current_status} Showing first 5000 chars.")

            except (DocumentParserError, NotebookFormatError, PdfExtractionError) as e:
                QMessageBox.warning(
                    self, tr("google_translate.msg_file_error_title"), f"Could not parse file:\n{str(e)}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, tr("google_translate.msg_file_error_title"), tr("google_translate.msg_file_error_read").format(str(e))
                )

    def _translate(self):
        """Start translation process."""
        # Phase A: Clear previous translation state before starting new translation
        self._translated_html = None
        self._translated_notebook = None
        self._translated_segments = []
        self.text_output.clear()
        
        # Get text to translate
        text_to_translate = ""
        notebook_to_translate = None

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
                if file_path.lower().endswith('.ipynb'):
                    notebook_to_translate = load_notebook(file_path)
                    text_to_translate = notebook_markdown_text(notebook_to_translate)
                    self._source_file_path = file_path
                    self._source_segments = []
                elif file_path.lower().endswith('.pdf'):
                    extraction = extract_pdf_text(file_path)
                    text_to_translate = extraction.text
                    self._source_file_path = file_path
                    self._source_segments = []
                elif file_path.lower().endswith('.docx'):
                    # Session COM8: NEW HTML-based format system for DOCX (with image and table support)
                    from translation.docx_html_mapper import extract_html_from_docx
                    
                    # Extract as HTML (with CSS formatting, images, and tables)
                    html_content, css_manager, image_manager, table_manager = extract_html_from_docx(file_path)
                    
                    # Store managers for later DOCX creation
                    self._css_manager = css_manager
                    self._image_manager = image_manager
                    self._table_manager = table_manager
                    self._source_file_path = file_path
                    
                    # Send HTML to translation (Google preserves HTML structure, image markers, and tables)
                    text_to_translate = html_content
                elif file_path.lower().endswith('.odt'):
                    # Session 77: NEW HTML-based format system
                    from translation.html_format_mapper import HTMLFormatMapper
                    
                    # Extract as HTML (with CSS formatting, images, and tables) - Phase 2 COM8
                    html_content, css_manager_or_path, image_manager, table_manager = HTMLFormatMapper.extract_html_from_odt(file_path)
                    
                    # Store managers for later ODT creation
                    self._css_manager = css_manager_or_path
                    self._image_manager = image_manager  # Phase 1: Store image manager
                    self._table_manager = table_manager  # Phase 2: Store table manager
                    self._source_file_path = file_path
                    
                    # Store empty segments (HTML system doesn't use segments)
                    self._source_segments = []
                    
                    # Keep HTML for translation (Google Translate will preserve HTML structure)
                    text_to_translate = html_content
                else:
                    # Use plain text parser for other file types
                    text_to_translate = extract_text_from_document(file_path)
                    self._source_segments = []  # No formatting for plain text files
            except (DocumentParserError, NotebookFormatError, PdfExtractionError) as e:
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
        if self.chk_file_mode.isChecked():
            self.recent_paths.add("source", self.ed_file_path.currentText().strip())
            self._refresh_recent_files()
            self.ed_file_path.setCurrentText(file_path)
        if notebook_to_translate is not None:
            self._start_notebook_translation(
                notebook_to_translate, from_lang, to_lang
            )
        else:
            self._start_translation(text_to_translate, from_lang, to_lang)

    def _start_translation(self, text: str, from_lang: str, to_lang: str):
        """Start background translation."""
        self._translated_notebook = None
        # Prevent starting new worker while one is running (fixes crash on duplicate calls)
        if self.translation_worker is not None:
            return

        self._cancel_requested = False
        
        # Update UI for translation in progress
        self.btn_translate.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(tr("google_translate.status_starting"))
        self.text_output.clear()

        source_path = self.ed_file_path.currentText().strip() if self.chk_file_mode.isChecked() else ""
        self._pending_history_details = {
            "mode": "file" if source_path else "text",
            "source_path": source_path,
            "source_language": from_lang,
            "target_language": to_lang,
            "files_processed": 1 if source_path else 0,
        }

        # Create and start worker
        self.translation_worker = TranslationWorker(self.api, text, from_lang, to_lang)
        
        # Connect signals BEFORE starting thread
        self.translation_worker.progress_updated.connect(self._on_progress_updated)
        self.translation_worker.translation_completed.connect(self._on_translation_completed)
        self.translation_worker.chunk_progress.connect(self._on_chunk_progress)  # Phase B: Chunking progress
        
        # Store finished workers to prevent premature deletion
        # For QThread subclass, do NOT use finished->deleteLater pattern
        worker = self.translation_worker
        worker.finished.connect(lambda finished_worker=worker: self._on_worker_finished(finished_worker))

        if not thread_manager.start_thread(
            self._thread_id,
            worker,
            worker,
            FeatureType.GOOGLE_TRANSLATE,
            worker.cancel,
            exclusive=False,
        ):
            self.translation_worker = None
            self._set_worker_controls_idle()
            self.lbl_status.setText(tr("google_translate.status_failed"))
            return

        worker.start()

    def _start_notebook_translation(self, notebook, from_lang: str, to_lang: str):
        """Start structure-preserving notebook translation."""
        if self.translation_worker is not None:
            return

        self._cancel_requested = False

        self.btn_translate.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(tr("google_translate.status_starting"))
        self.text_output.clear()

        source_path = self.ed_file_path.currentText().strip()
        self._pending_history_details = {
            "mode": "notebook",
            "source_path": source_path,
            "source_language": from_lang,
            "target_language": to_lang,
            "files_processed": 1,
        }

        worker = NotebookTranslationWorker(
            self.api, notebook, from_lang, to_lang
        )
        self.translation_worker = worker
        worker.progress_updated.connect(self._on_progress_updated)
        worker.chunk_progress.connect(self._on_chunk_progress)
        worker.translation_completed.connect(
            self._on_notebook_translation_completed
        )
        worker.finished.connect(
            lambda finished_worker=worker: self._on_worker_finished(finished_worker)
        )
        if not thread_manager.start_thread(
            self._thread_id,
            worker,
            worker,
            FeatureType.GOOGLE_TRANSLATE,
            worker.cancel,
            exclusive=False,
        ):
            self.translation_worker = None
            self._set_worker_controls_idle()
            self.lbl_status.setText(tr("google_translate.status_failed"))
            return
        worker.start()

    def _on_notebook_translation_completed(
        self, notebook, preview: str, success: bool, error: str, detected_lang: str
    ):
        """Store the translated notebook and reuse common completion UI."""
        self._translated_notebook = notebook if success else None
        self._on_translation_completed(
            preview, success, error, detected_lang
        )

    def _on_progress_updated(self, progress: int, status: str):
        """Handle progress updates."""
        self.progress_bar.setValue(progress)
        self.lbl_status.setText(status)
    
    def _on_chunk_progress(self, current_chunk: int, total_chunks: int, percentage: int, status_msg: str):
        """
        Handle chunk-level progress updates (Phase B).
        
        Displays detailed progress for large document translations.
        Example: "Chunk 5/10 (50%): Translating... (2341 chars)"
        """
        # Update progress bar with chunk percentage
        # Note: translate_text_chunked already maps to 50-95% range in worker
        
        # Enhanced status message with chunk info
        if total_chunks > 1:
            # Multi-chunk translation: show detailed status
            enhanced_status = f"{status_msg} [Chunk {current_chunk}/{total_chunks}]"
            self.lbl_status.setText(enhanced_status)
        else:
            # Single chunk: use simple status
            self.lbl_status.setText(status_msg)

    def _on_translation_completed(
        self,
        result: str,
        success: bool,
        error: str,
        detected_lang: str = "",
    ):
        """Handle translation completion."""
        if not success:
            # Phase A: Clear state on translation failure
            self._translated_html = None
            self._translated_segments = []
            self.text_output.clear()
        
        if success:
            # Session 77: Check if result is HTML (from new format system)
            is_html_format = '<!DOCTYPE html>' in result or '<html>' in result
            
            if is_html_format:
                # HTML format - extract plain text for UI display
                from html.parser import HTMLParser
                import html as html_module
                
                class TextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.text_parts = []
                        self.current_tag = None
                        self.current_class = None
                        self.prev_class = None
                        self.in_head = False
                        # Header classes (bold/large text that should have newlines around them)
                        self.header_classes = ['fmt1', 'fmt3', 'fmt4', 'fmt5', 'fmt7']
                    
                    def handle_starttag(self, tag, attrs):
                        if tag in ('head', 'style', 'meta', 'script', 'title'):
                            self.in_head = True
                            return
                        
                        if tag == 'br':
                            # Line break
                            self.text_parts.append('\n')
                            self.current_tag = tag
                            return
                        
                        if tag == 'span':
                            # Check for tab marker first
                            attr_dict = dict(attrs)
                            if 'data-tab' in attr_dict:
                                self.text_parts.append('\t')  # Add tab character
                                return
                            
                            # Regular span with format class
                            new_class = attr_dict.get('class')
                            
                            # Add newline on format class transition (header ↔ body)
                            if self.prev_class and new_class and self.prev_class != new_class:
                                prev_is_header = self.prev_class in self.header_classes
                                new_is_header = new_class in self.header_classes
                                
                                # Newline if entering or leaving header format
                                if prev_is_header != new_is_header:
                                    self.text_parts.append('\n')
                            
                            self.current_class = new_class
                        
                        self.current_tag = tag
                    
                    def handle_endtag(self, tag):
                        if tag in ('head', 'style', 'script'):
                            self.in_head = False
                        if tag == 'span' and self.current_class:
                            self.prev_class = self.current_class
                        if tag == self.current_tag:
                            self.current_tag = None
                    
                    def handle_data(self, data):
                        # Skip data inside style/script/head tags
                        if self.in_head:
                            return
                        
                        # Inside content tags - decode entities and keep ALL content (including whitespace)
                        # Outside content tags - only keep if has non-whitespace (ignore HTML formatting)
                        if self.current_tag in ['span', 'p', 'div']:
                            decoded = html_module.unescape(data)
                            self.text_parts.append(decoded)
                        elif data.strip():
                            decoded = html_module.unescape(data)
                            self.text_parts.append(decoded)
                    
                    def get_text(self):
                        return ''.join(self.text_parts)
                
                extractor = TextExtractor()
                extractor.feed(result)
                plain_text = extractor.get_text()
                
                # Store translated HTML for ODT/DOCX creation
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
            self.btn_open_in_editor.setEnabled(True)
            self.btn_reverse.setEnabled(True)
            self._last_detected_lang = detected_lang  # Store detected language
            self.lbl_status.setText(tr("google_translate.status_completed"))
            self.lbl_status.setStyleSheet("color: #22C55E; font-weight: bold;")
            if self._pending_history_details is not None:
                details = dict(self._pending_history_details)
                details["detected_language"] = detected_lang
                record_translation_operation(
                    self,
                    "google_translate",
                    "Google Translate",
                    details,
                )
            self.notify_processing_completed()
        else:
            self.text_output.setPlainText(f"Translation failed: {error}")
            self.btn_copy_result.setEnabled(False)
            self.btn_save_as.setEnabled(False)
            self.btn_open_in_editor.setEnabled(False)
            self.lbl_status.setText(tr("google_translate.status_failed"))
            self.lbl_status.setStyleSheet("color: #EF4444; font-weight: bold;")

        # Update cache info
        self._update_cache_info()

        # Reset status color after delay
        QTimer.singleShot(5000, lambda: self.lbl_status.setStyleSheet("color: #666; font-style: italic;"))

    def _on_worker_finished(self, worker):
        """Settle the operation only after the native thread has stopped."""
        if worker is not self.translation_worker:
            return
        self.translation_worker = None
        self._set_worker_controls_idle()
        if self._cancel_requested:
            self.lbl_status.setText(tr("google_translate.text_cancelled"))
        self._pending_history_details = None
        self._cancel_requested = False

        action = self._close_action
        self._close_action = None
        if action:
            name, target = action
            if name == "tab" and target is not None:
                index = target.tabs.indexOf(self)
                if index >= 0:
                    target._close_tab(index)
            else:
                (target or self).close()

    def _set_worker_controls_idle(self):
        """Restore controls after a worker has fully settled."""
        self.btn_translate.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_bar.setVisible(False)

    def _cancel_translation(self):
        """Cancel ongoing translation."""
        if self.translation_worker and self.translation_worker.isRunning():
            self._cancel_requested = True
            self.translation_worker.cancel()
            self.btn_cancel.setEnabled(False)
            self.lbl_status.setText(tr("google_translate.text_cancelled"))
            self._pending_history_details = None

    def _clear(self):
        """Clear all input and output fields."""
        self.text_input.clear()
        self.text_output.clear()
        self.ed_file_path.clearEditText()
        self._translated_notebook = None
        self.btn_copy_result.setEnabled(False)
        self.btn_save_as.setEnabled(False)
        self.btn_open_in_editor.setEnabled(False)
        self.btn_reverse.setEnabled(False)
        self.lbl_status.setText(tr("google_translate.status_ready"))
        self.lbl_status.setStyleSheet("color: #666; font-style: italic;")

    def _reverse_translation(self):
        """Reverse source and target languages, swap input/output text, and auto-translate."""
        # Check if translation is currently running - if so, ignore the click
        if self.translation_worker is not None:
            return
        
        # Get current language codes (not display text)
        from_code = self.combo_from_lang.currentData()
        to_code = self.combo_to_lang.currentData()
        
        # Store the output text before swapping (this will become the new input)
        output_text = self.text_output.toPlainText()
        if not output_text.strip():
            return
        
        # Also store translated segments with formatting for document mode
        has_formatting = bool(self._translated_segments)
        
        # Swap languages
        if from_code == "auto":
            detected_index = self.combo_to_lang.findData(self._last_detected_lang)
            if detected_index < 0 or self._last_detected_lang == to_code:
                QMessageBox.warning(
                    self,
                    tr("google_translate.reverse_unavailable_title"),
                    tr("google_translate.reverse_unavailable_message"),
                )
                return

            from_index = self.combo_from_lang.findData(to_code)
            self.combo_from_lang.setCurrentIndex(from_index)
            self.combo_to_lang.setCurrentIndex(detected_index)
        else:
            # Normal swap when From is not auto-detect
            from_index = self.combo_from_lang.findData(to_code)
            to_index = self.combo_to_lang.findData(from_code)
            
            if from_index >= 0:
                self.combo_from_lang.setCurrentIndex(from_index)
            if to_index >= 0:
                self.combo_to_lang.setCurrentIndex(to_index)
        
        # The translated output is now a text input, not the original file.
        if self.chk_file_mode.isChecked():
            self.chk_file_mode.setChecked(False)
        self.text_input.setPlainText(output_text)
        self.text_output.clear()  # Clear output before auto-translation
        
        # Swap formatting segments if we have them (for document mode)
        if has_formatting:
            # Swap source and translated segments
            self._source_segments, self._translated_segments = self._translated_segments, self._source_segments
        
        # Auto-trigger translation with the swapped text
        new_from_lang = self.combo_from_lang.currentData()
        new_to_lang = self.combo_to_lang.currentData()

        if has_formatting and self._source_segments:
            text_to_translate = "".join(
                segment.to_tagged_text() for segment in self._source_segments
            )
        else:
            text_to_translate = output_text

        self._start_translation(text_to_translate, new_from_lang, new_to_lang)

    def _swap_languages(self):
        """Swap source and target language selections only (doesn't swap content)."""
        # Get current language codes
        from_code = self.combo_from_lang.currentData()
        to_code = self.combo_to_lang.currentData()
        
        # Handle auto-detect case
        if from_code == "auto":
            # If From is "auto", use detected language if available
            if self._last_detected_lang:
                # Swap: From becomes To language, To becomes detected language
                from_index = self.combo_from_lang.findData(to_code)
                to_index = self.combo_to_lang.findData(self._last_detected_lang)
                
                if from_index >= 0:
                    self.combo_from_lang.setCurrentIndex(from_index)
                if to_index >= 0:
                    self.combo_to_lang.setCurrentIndex(to_index)
            else:
                # No detected language yet, just swap To to From (From stays auto)
                from_index = self.combo_from_lang.findData(to_code)
                if from_index >= 0:
                    self.combo_from_lang.setCurrentIndex(from_index)
        else:
            # Normal swap: exchange From and To languages
            from_index = self.combo_from_lang.findData(to_code)
            to_index = self.combo_to_lang.findData(from_code)
            
            if from_index >= 0:
                self.combo_from_lang.setCurrentIndex(from_index)
            if to_index >= 0:
                self.combo_to_lang.setCurrentIndex(to_index)
        
        # Update status to indicate languages were swapped
        self.lbl_status.setText("Languages swapped")
        self.lbl_status.setStyleSheet("color: #3B82F6; font-style: italic;")
        QTimer.singleShot(2000, lambda: self.lbl_status.setStyleSheet("color: #666; font-style: italic;"))


    def _copy_result(self):
        """Copy translation result to clipboard."""
        result = self.text_output.toPlainText()
        if result:
            clipboard = QApplication.clipboard()
            clipboard.setText(result)

            # Visual feedback
            self.btn_copy_result.setText(tr("google_translate.btn_copied"))
            QTimer.singleShot(2000, lambda: self.btn_copy_result.setText(tr("google_translate.btn_copy_result")))

    def _open_result_in_editor(self):
        """Send the reviewable plain-text result to Clarify Editor."""
        result = self.text_output.toPlainText()
        if not result:
            return

        source_path = self._source_file_path or ""
        source_stem = Path(source_path).stem if source_path else "translation"
        self.open_in_editor_requested.emit(
            result,
            f"{source_stem}_translated.txt",
        )

    def _save_as(self):
        """Save translation result to file (TXT, DOCX, or ODT based on dropdown selection)."""
        result = self.text_output.toPlainText()
        if not result:
            return
        
        # Determine default format based on whether we have stored formatting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"translation_{timestamp}"  # NO extension - dropdown determines it
        
        if self._translated_notebook is not None:
            file_filter = "Jupyter Notebooks (*.ipynb);;Text Files (*.txt)"
        elif self._translated_segments:
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
                if 'ipynb' in selected_filter.lower() or 'jupyter' in selected_filter.lower():
                    if not file_path.lower().endswith('.ipynb'):
                        file_path += '.ipynb'
                    save_notebook(self._translated_notebook, file_path)
                elif 'docx' in selected_filter.lower() or 'word' in selected_filter.lower():
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
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(result)
                    except (IOError, OSError, PermissionError) as e:
                        QMessageBox.critical(
                            self,
                            tr("google_translate.error_title", "Error"),
                            f"Failed to save file: {e}"
                        )
                        return
                 
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
        Save translation as DOCX with formatting restored.
        
        Session COM8: Uses NEW HTML-based format system with image support.
        Falls back to old segment system for backward compatibility.
        
        Args:
            output_path: Path to save DOCX file
        """
        if self._translated_html and self._css_manager:
            # NEW HTML system - use HTML to DOCX conversion with images and tables
            from translation.docx_html_mapper import create_docx_from_html
            
            # Check if we have image_manager and table_manager (new system)
            image_manager = getattr(self, '_image_manager', None)
            table_manager = getattr(self, '_table_manager', None)
            
            if image_manager or table_manager:
                # New system with images and/or tables
                from translation.docx_html_mapper import ImageManager, TableManager
                
                # Use existing managers or create empty ones
                img_mgr = image_manager if image_manager else ImageManager()
                tbl_mgr = table_manager if table_manager else TableManager()
                
                create_docx_from_html(
                    self._translated_html,
                    output_path,
                    self._css_manager,
                    img_mgr,
                    tbl_mgr
                )
            else:
                # Old DOCX files without images/tables - create empty managers
                from translation.docx_html_mapper import ImageManager, TableManager
                empty_image_manager = ImageManager()
                empty_table_manager = TableManager()
                create_docx_from_html(
                    self._translated_html,
                    output_path,
                    self._css_manager,
                    empty_image_manager,
                    empty_table_manager
                )
            
        elif self._translated_segments:
            # OLD system - use segment-based approach (backward compatibility)
            FormatMapper.create_docx_from_segments(self._translated_segments, output_path)
            
        else:
            # Fallback: no formatting, create plain text segment
            plain_text = self.text_output.toPlainText()
            
            # CRITICAL: Remove any system tags that might have leaked into UI
            # Only remove numeric tags (Clarify system), preserve user tags like <div>
            plain_text = FormatMapper.remove_tags(plain_text)
            
            from ..translation.format_mapper import TextSegment
            self._translated_segments = [TextSegment(text=plain_text)]
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
        # DEBUG: Log what we have
        print(f"\n[DEBUG] _save_as_odt called:")
        print(f"  _translated_html: {self._translated_html is not None} (length: {len(self._translated_html) if self._translated_html else 0})")
        print(f"  _css_manager: {self._css_manager is not None} (type: {type(self._css_manager).__name__ if self._css_manager else 'None'})")
        print(f"  _translated_segments: {len(self._translated_segments)} segments")
        
        if self._translated_html and self._css_manager:
            # Session 77: NEW HTML system - use HTML to ODT conversion (Phase 1: with images)
            # COM8 2026-02-20: PROPER ODT fix (Option B) - preserve original structure
            print(f"  → Using HTML system (Option B: preserve structure)")
            
            # Check if we have original file path (needed for Option B)
            original_odt = getattr(self, '_source_file_path', None)
            
            if original_odt and os.path.exists(original_odt) and original_odt.endswith('.odt'):
                # Option B: Preserve original ODT structure (PROPER fix)
                from translation.html_format_mapper import create_odt_from_original
                image_mgr = getattr(self, '_image_manager', None)
                table_mgr = getattr(self, '_table_manager', None)
                create_odt_from_original(original_odt, self._translated_html, self._css_manager, 
                                        output_path, image_mgr, table_mgr)
                print(f"  → ODT created with preserved structure (Option B)")
            else:
                # Fallback: Use old method if no original file (shouldn't happen for ODT workflow)
                print(f"  → WARNING: No original ODT path, using fallback method")
                from translation.html_format_mapper import create_odt_from_html
                image_mgr = getattr(self, '_image_manager', None)
                table_mgr = getattr(self, '_table_manager', None)
                create_odt_from_html(self._translated_html, self._css_manager, output_path, image_mgr, table_mgr)
            
            print(f"  → ODT created successfully")
            
        elif self._translated_segments:
            # OLD system - use segment-based approach (backward compatibility)
            print(f"  → Using OLD segment system")
            FormatMapper.create_odt_from_segments(self._translated_segments, output_path)
            
        else:
            # Fallback: no formatting, create plain text segment
            print(f"  → Using FALLBACK plain text")
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

    def request_tab_close(self):
        """Defer tab removal until its worker has stopped."""
        if self.translation_worker is None:
            return True
        action = "tab" if self._main_window_ref is not None else "close"
        self._close_action = (action, self._main_window_ref or self)
        self._cancel_translation()
        return False

    def closeEvent(self, event):
        """Defer dock closure until cooperative cancellation settles."""
        if self.translation_worker is not None:
            self._close_action = ("close", self)
            self._cancel_translation()
            event.ignore()
            return
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
