"""Review-first editorial diagnostics with independent internal sessions."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

from PySide6.QtCore import QProcess, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.editorial_analysis import (
    abnt_structure_diagnostics,
    aspell_diagnostics,
    detect_language,
    diagnose_textual_defects,
    editorial_ai_prompt,
)


class EditorialSession(QWidget):
    """One isolated review session; source content is never written."""

    prepare_ai_requested = Signal(str, list, int)
    google_translate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Source file:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Optional UTF-8 text or Markdown file")
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse)
        source_row.addWidget(self.path_input, 1)
        source_row.addWidget(self.browse_button)
        layout.addLayout(source_row)

        controls = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Spelling candidates (Aspell)", "spelling")
        self.mode_combo.addItem("Textual defect diagnostics", "defects")
        self.mode_combo.addItem("ABNT structure preflight", "abnt")
        self.language_combo = QComboBox()
        for label, code in (("Auto detect", "auto"), ("Portuguese", "pt_BR"), ("English", "en_US"), ("Spanish", "es")):
            self.language_combo.addItem(label, code)
        self.bridge_checkbox = QCheckBox("Allow bridge-language reasoning")
        controls.addWidget(self.mode_combo, 1)
        controls.addWidget(self.language_combo)
        controls.addWidget(self.bridge_checkbox)
        layout.addLayout(controls)

        self.source_edit = QPlainTextEdit()
        self.source_edit.setPlaceholderText("Paste book or document text here")
        self.source_edit.document().setMaximumBlockCount(50_000)
        layout.addWidget(self.source_edit, 2)

        actions = QHBoxLayout()
        self.analyze_button = QPushButton("Run local diagnostics")
        self.analyze_button.clicked.connect(self.analyze)
        self.ai_button = QPushButton("Prepare in AI Processor")
        self.ai_button.clicked.connect(self._prepare_ai)
        self.translate_button = QPushButton("Open in Google Translate")
        self.translate_button.clicked.connect(self._open_translate)
        self.libreoffice_button = QPushButton("Open source in LibreOffice")
        self.libreoffice_button.clicked.connect(self._open_libreoffice)
        self.libreoffice_button.setEnabled(bool(shutil.which("libreoffice")))
        actions.addWidget(self.analyze_button)
        actions.addWidget(self.ai_button)
        actions.addWidget(self.translate_button)
        actions.addWidget(self.libreoffice_button)
        layout.addLayout(actions)

        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.document().setMaximumBlockCount(50_000)
        layout.addWidget(self.output_edit, 2)

    def _browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open editorial source", "", "Text (*.txt *.md);;All files (*)")
        if path:
            self.path_input.setText(path)
            self.source_edit.setPlainText(self._read_source(path))

    @staticmethod
    def _read_source(path: str) -> str:
        source = Path(path).expanduser()
        if source.stat().st_size > 2_000_000:
            raise ValueError("Source exceeds 2,000,000 bytes")
        return source.read_text(encoding="utf-8")

    def _text(self) -> str:
        text = self.source_edit.toPlainText()
        if not text and self.path_input.text().strip():
            text = self._read_source(self.path_input.text().strip())
        if not text.strip():
            raise ValueError("Provide source text first")
        return text

    def _language(self, text: str) -> str:
        selected = self.language_combo.currentData()
        return detect_language(text)["language"] if selected == "auto" else selected

    def analyze(self) -> None:
        try:
            text = self._text()
            mode = self.mode_combo.currentData()
            if mode == "spelling":
                result = aspell_diagnostics(text, self._language(text))
            elif mode == "defects":
                result = diagnose_textual_defects(text)
            else:
                result = abnt_structure_diagnostics(text)
            self.output_edit.setPlainText(json.dumps(result, ensure_ascii=False, indent=2))
        except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, "Editorial diagnostics unavailable", str(exc))

    def _prepare_ai(self) -> None:
        try:
            text = self._text()
            path = self.path_input.text().strip()
            if not path:
                raise ValueError("Save or select a source file before preparing the file-oriented AI Processor")
            prompt = editorial_ai_prompt(
                self.mode_combo.currentText(), self._language(text), self.bridge_checkbox.isChecked()
            )
            self.prepare_ai_requested.emit(prompt, [path], 2_000_000)
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self, "AI review unavailable", str(exc))

    def _open_translate(self) -> None:
        try:
            self.google_translate_requested.emit(self._text())
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self, "Translation unavailable", str(exc))

    def _open_libreoffice(self) -> None:
        path = self.path_input.text().strip()
        if not path or not Path(path).is_file():
            QMessageBox.warning(self, "LibreOffice unavailable", "Select an existing source file first")
            return
        QProcess.startDetached(shutil.which("libreoffice") or "libreoffice", [path])


class EditorialRepairDock(QWidget):
    """Container supporting multiple independent editorial review tabs."""

    prepare_ai_requested = Signal(str, list, int)
    google_translate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorialRepairDock")
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        self.new_tab_button = QPushButton("New Tab")
        self.new_tab_button.clicked.connect(self.add_session)
        toolbar.addWidget(self.new_tab_button)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_session)
        layout.addWidget(self.tabs)
        self.add_session()

    def add_session(self) -> EditorialSession:
        session = EditorialSession(self)
        session.prepare_ai_requested.connect(self.prepare_ai_requested)
        session.google_translate_requested.connect(self.google_translate_requested)
        index = self.tabs.addTab(session, f"Review {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(index)
        return session

    def close_session(self, index: int) -> None:
        if self.tabs.count() == 1:
            session = self.tabs.widget(0)
            session.path_input.clear()
            session.source_edit.clear()
            session.output_edit.clear()
            return
        session = self.tabs.widget(index)
        self.tabs.removeTab(index)
        session.deleteLater()
