"""Confirmation-gated programming dictation command tool."""

from __future__ import annotations

import json

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.voice_programming import parse_voice_command, speech_backend_status


class VoiceProgrammingDock(QWidget):
    """Preview transcript commands and require explicit confirmation before emitting."""

    confirmed_command = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("VoiceProgrammingDock")
        self._pending_command = None
        layout = QVBoxLayout(self)
        status = speech_backend_status()
        self.backend_status = QLabel(
            "Speech recognition backend available." if status["available"]
            else "Live speech recognition unavailable: no supported STT backend is installed."
        )
        self.backend_status.setWordWrap(True)
        layout.addWidget(self.backend_status)
        self.transcript_edit = QPlainTextEdit()
        self.transcript_edit.setPlaceholderText(
            "Paste a transcript, for example: escreva print abre parenteses 'ok' fecha parenteses"
        )
        self.transcript_edit.document().setMaximumBlockCount(1_000)
        layout.addWidget(self.transcript_edit)
        self.preview_button = QPushButton("Preview command")
        self.preview_button.clicked.connect(self.preview)
        layout.addWidget(self.preview_button)
        self.preview_edit = QPlainTextEdit()
        self.preview_edit.setReadOnly(True)
        layout.addWidget(self.preview_edit)
        self.confirm_checkbox = QCheckBox("I reviewed this exact command")
        self.confirm_checkbox.toggled.connect(self._confirmation_changed)
        layout.addWidget(self.confirm_checkbox)
        self.apply_button = QPushButton("Apply confirmed command to Clarify Editor")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_confirmed)
        layout.addWidget(self.apply_button)

    def preview(self) -> None:
        try:
            self._pending_command = parse_voice_command(self.transcript_edit.toPlainText())
            self.preview_edit.setPlainText(json.dumps(self._pending_command, ensure_ascii=False, indent=2))
            self.confirm_checkbox.setChecked(False)
        except ValueError as exc:
            self._pending_command = None
            self.apply_button.setEnabled(False)
            QMessageBox.warning(self, "Voice command unavailable", str(exc))

    def _confirmation_changed(self, checked: bool) -> None:
        self.apply_button.setEnabled(bool(checked and self._pending_command))

    def apply_confirmed(self) -> None:
        if not self.confirm_checkbox.isChecked() or not self._pending_command:
            return
        self.confirmed_command.emit(dict(self._pending_command))
        self._pending_command = None
        self.confirm_checkbox.setChecked(False)
