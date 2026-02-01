"""
Recall Dialog for Calculator Memory
Provides Export/Copy/Send options when recalling data from memory slot.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.101
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules


from typing import Any, Dict, Optional
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QTextEdit, QPushButton, QFileDialog, QMessageBox,
                                QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from src.i18n.translator import tr, tooltip_tr
import json


class RecallDialog(QDialog):
    """
    Dialog for recalling data from Calculator Memory slot.

    Provides 3 actions:
    - Export to File: Save JSON to file
    - Copy to Clipboard: Copy formatted JSON
    - Send to Set Operations: Populate Set Operations File A/B

    Signals:
        send_to_set_operations: Emitted when user clicks Send (data, slot_name)
    """

    send_to_set_operations = Signal(dict, str)  # (data, slot_name)

    def __init__(self, slot_name: str, slot_data: Dict[str, Any],
                 slot_stats: Dict[str, Any], source: str, timestamp: str, parent=None):
        """
        Initialize RecallDialog.

        Args:
            slot_name: Slot identifier (A, B, C, D, E)
            slot_data: JSON data from slot
            slot_stats: Statistics dict
            source: Source description
            timestamp: Timestamp string
            parent: Parent widget
        """
        super().__init__(parent)
        self.slot_name = slot_name
        self.slot_data = slot_data
        self.slot_stats = slot_stats
        self.source = source
        self.timestamp = timestamp

        self.setWindowTitle(tr("recall_dialog.window_title").format(slot_name=slot_name))
        self.resize(700, 500)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Header with slot info
        header_label = QLabel(f"<b>Slot {self.slot_name}</b> - {self.source}")
        header_label.setStyleSheet("font-size: 14pt; color: #4EC9B0;")
        layout.addWidget(header_label)

        # Timestamp
        timestamp_label = QLabel(f"Stored: {self.timestamp}")
        timestamp_label.setStyleSheet("color: #888;")
        layout.addWidget(timestamp_label)

        # Statistics summary
        stats_group = QGroupBox(tr("recall_dialog.group_statistics"))
        stats_layout = QVBoxLayout()

        stats_text = self._format_stats_summary()
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("Courier New", 9))
        stats_layout.addWidget(stats_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Data preview
        preview_label = QLabel(tr("recall_dialog.lbl_preview"))
        layout.addWidget(preview_label)

        self.data_preview = QTextEdit()
        self.data_preview.setReadOnly(True)
        self.data_preview.setFont(QFont("Courier New", 10))
        self.data_preview.setPlainText(json.dumps(self.slot_data, indent=2))
        layout.addWidget(self.data_preview)

        # Action buttons
        btn_layout = QHBoxLayout()

        # Export to File button
        self.btn_export = QPushButton(f"📤 {tr('recall_dialog.btn_export')}")
        self.btn_export.setToolTip(tooltip_tr("recall.tooltip_export"))
        self.btn_export.clicked.connect(self._export_to_file)
        btn_layout.addWidget(self.btn_export)

        # Copy to Clipboard button
        self.btn_copy = QPushButton(f"📋 {tr('recall_dialog.btn_copy')}")
        self.btn_copy.setToolTip(tooltip_tr("recall.tooltip_copy"))
        self.btn_copy.clicked.connect(self._copy_to_clipboard)
        btn_layout.addWidget(self.btn_copy)

        # Send to Set Operations button
        self.btn_send = QPushButton(f"🔄 {tr('recall_dialog.btn_send')}")
        self.btn_send.setToolTip(tooltip_tr("recall.tooltip_send"))
        self.btn_send.clicked.connect(self._send_to_set_operations)
        btn_layout.addWidget(self.btn_send)

        layout.addLayout(btn_layout)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()

        self.btn_close = QPushButton(tr("recall_dialog.btn_close"))
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setDefault(True)
        close_layout.addWidget(self.btn_close)

        layout.addLayout(close_layout)

        self.setLayout(layout)

    def _format_stats_summary(self) -> str:
        """
        Format statistics summary for display.

        Returns:
            Formatted statistics string
        """
        stats = self.slot_stats

        lines = []
        lines.append(f"Keys Count: {stats.get('total_keys', 0)}")
        lines.append(f"Size: {stats.get('size_bytes', 0)} bytes")
        lines.append(f"Max Depth: {stats.get('max_depth', 0)}")
        lines.append(f"Unique Keys: {stats.get('unique_keys', 0)}")
        lines.append(f"Duplicate Keys: {stats.get('duplicate_keys', 0)}")

        # Value types
        value_types = stats.get('value_types', {})
        types_str = ', '.join([f"{k}: {v}" for k, v in value_types.items() if v > 0])
        lines.append(f"Value Types: {types_str}")

        return '\n'.join(lines)

    def _export_to_file(self):
        """Export JSON data to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Slot {self.slot_name} to File",
            f"slot_{self.slot_name.lower()}_data.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.slot_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(
                self,
                tr("recall.msg_export_success_title"),
                tr("recall.msg_export_success").format(slot=self.slot_name, path=file_path)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                tr("recall.msg_export_failed_title"),
                tr("recall.msg_export_failed").format(error=str(e))
            )

    def _copy_to_clipboard(self):
        """Copy formatted JSON to clipboard."""
        from PySide6.QtWidgets import QApplication

        json_text = json.dumps(self.slot_data, indent=2, ensure_ascii=False)

        clipboard = QApplication.clipboard()
        clipboard.setText(json_text)

        QMessageBox.information(
            self,
            tr("recall.msg_copied_title"),
            tr("recall.msg_copied").format(
                slot=self.slot_name,
                lines=len(json_text.splitlines()),
                chars=len(json_text)
            )
        )

    def _send_to_set_operations(self):
        """Send data to Set Operations (emit signal for integration)."""
        # Emit signal with data and slot name
        self.send_to_set_operations.emit(self.slot_data, self.slot_name)

        # Show confirmation and close
        QMessageBox.information(
            self,
            tr("recall.msg_sent_title"),
            tr("recall.msg_sent").format(slot=self.slot_name)
        )

        self.accept()
