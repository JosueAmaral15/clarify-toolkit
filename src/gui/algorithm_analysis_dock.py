"""Prepare code, project, or flowchart analysis in the existing AI Processor."""

from __future__ import annotations

import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.algorithm_analysis import algorithm_review_preflight, algorithm_review_prompt


class AlgorithmAnalysisDock(QWidget):
    """Perform local preflight, then prepare but never start an AI review."""

    prepare_ai_requested = Signal(str, list, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AlgorithmAnalysisDock")
        self._preflight = None
        layout = QVBoxLayout(self)
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Source:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Code file, project directory, or flowchart image")
        self.file_button = QPushButton("File...")
        self.directory_button = QPushButton("Directory...")
        self.file_button.clicked.connect(self._browse_file)
        self.directory_button.clicked.connect(self._browse_directory)
        path_row.addWidget(self.path_input, 1)
        path_row.addWidget(self.file_button)
        path_row.addWidget(self.directory_button)
        layout.addLayout(path_row)
        actions = QHBoxLayout()
        self.preflight_button = QPushButton("Run local preflight")
        self.preflight_button.clicked.connect(self.run_preflight)
        self.prepare_button = QPushButton("Prepare in AI Processor")
        self.prepare_button.setEnabled(False)
        self.prepare_button.clicked.connect(self.prepare_ai)
        actions.addWidget(self.preflight_button)
        actions.addWidget(self.prepare_button)
        actions.addStretch()
        layout.addLayout(actions)
        self.preview_edit = QPlainTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.document().setMaximumBlockCount(20_000)
        layout.addWidget(self.preview_edit)

    def _browse_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select code or flowchart", "", "Code and images (*.py *.js *.ts *.java *.c *.cpp *.png *.jpg *.jpeg *.webp);;All files (*)"
        )
        if path:
            self.path_input.setText(path)

    def _browse_directory(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select project directory")
        if path:
            self.path_input.setText(path)

    def run_preflight(self) -> None:
        try:
            self._preflight = algorithm_review_preflight(self.path_input.text().strip())
            preview = {
                "preflight": self._preflight,
                "prepared_prompt": algorithm_review_prompt(self._preflight),
                "processing_started": False,
            }
            rendered = json.dumps(preview, ensure_ascii=False, indent=2)
            if len(rendered) > 1_000_000:
                raise ValueError("Preflight preview exceeds 1,000,000 characters")
            self.preview_edit.setPlainText(rendered)
            self.prepare_button.setEnabled(True)
        except (OSError, UnicodeError, SyntaxError, ValueError) as exc:
            self._preflight = None
            self.prepare_button.setEnabled(False)
            QMessageBox.warning(self, "Algorithm preflight unavailable", str(exc))

    def prepare_ai(self) -> None:
        if not self._preflight:
            return
        prompt = algorithm_review_prompt(self._preflight)
        self.prepare_ai_requested.emit(prompt, [self._preflight["path"]], 2_000_000)
