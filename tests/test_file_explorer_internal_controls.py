"""Regression tests for File Explorer internal control polish."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QPushButton

from src.gui.file_explorer_dock import FileExplorerDock


def _button_texts(widget):
    return {button.text().replace("&", "") for button in widget.findChildren(QPushButton)}


def test_file_explorer_dock_mode_has_no_internal_close_or_dialog_buttons(qapp):
    """Dock mode should not expose internal Close/OK/Cancel dialog controls."""
    dock = FileExplorerDock(dialog_mode=False)
    try:
        assert not hasattr(dock, "button_box")
        assert dock.findChildren(QDialogButtonBox) == []
        assert "Close" not in _button_texts(dock)
        assert "Fechar" not in _button_texts(dock)
    finally:
        dock.deleteLater()


def test_file_explorer_dialog_mode_keeps_ok_cancel_buttons(qapp):
    """Dialog mode legitimately uses OK/Cancel controls for file selection."""
    dialog = QDialog()
    dock = FileExplorerDock(dialog, dialog_mode=True)
    try:
        assert hasattr(dock, "button_box")
        assert dock.button_box in dock.findChildren(QDialogButtonBox)
        assert dock.button_box.standardButtons() & QDialogButtonBox.Ok
        assert dock.button_box.standardButtons() & QDialogButtonBox.Cancel
    finally:
        dock.deleteLater()
        dialog.deleteLater()


def test_file_explorer_dialog_mode_accept_reject_target_parent_dialog(qapp):
    """Dialog-mode accept/reject should operate on the embedding QDialog."""
    dialog = QDialog()
    dock = FileExplorerDock(dialog, dialog_mode=True)
    try:
        dock.accept()
        assert dock._dialog_result == QDialog.Accepted
        assert dialog.result() == QDialog.Accepted

        dock.reject()
        assert dock._dialog_result == QDialog.Rejected
        assert dialog.result() == QDialog.Rejected
    finally:
        dock.deleteLater()
        dialog.deleteLater()
