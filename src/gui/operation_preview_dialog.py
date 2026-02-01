"""
Operation Preview Dialog for Calculator Memory
Shows preview of operation result before storing in slot.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.101
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules

import json

from typing import Any, Dict

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox, QDialog, QGroupBox, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout
)

from src.i18n.translator import tr, tooltip_tr


class OperationPreviewDialog(QDialog):
    """
    Dialog for previewing operation result before storing.

    Shows:
    - Operation description (A ∩ B)
    - Result statistics
    - Result JSON preview
    - Slot selector for storage

    Returns:
        Tuple (store: bool, target_slot: Optional[str])
    """

    def __init__(
        self,
        operation_desc: str,
        result_data: Dict[str, Any],
        result_stats: Dict[str, Any],
        message: str,
        available_slots: list,
        parent=None,
    ):
        """
        Initialize OperationPreviewDialog.

        Args:
            operation_desc: Operation description (e.g., "Intersection: Slot A ∩ Slot B")
            result_data: Result JSON data
            result_stats: Result statistics
            message: Operation result message
            available_slots: List of available slot names for storage
            parent: Parent widget
        """
        super().__init__(parent)
        self.operation_desc = operation_desc
        self.result_data = result_data
        self.result_stats = result_stats
        self.message = message
        self.available_slots = available_slots

        self.store_result = False
        self.target_slot = None

        self.setWindowTitle(tr("operation_preview.title"))
        self.resize(700, 550)

        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Header with operation description
        header_label = QLabel(f"<b>{self.operation_desc}</b>")
        header_label.setStyleSheet("font-size: 14pt; color: #4EC9B0;")
        layout.addWidget(header_label)

        # Result message
        message_label = QLabel(self.message)
        message_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(message_label)

        # Statistics summary
        stats_group = QGroupBox(tr("operation_preview.group_stats"))
        stats_layout = QVBoxLayout()

        stats_text = self._format_stats_summary()
        stats_label = QLabel(stats_text)
        stats_label.setFont(QFont("Courier New", 9))
        stats_layout.addWidget(stats_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Result preview
        preview_label = QLabel(tr("operation_preview.lbl_preview"))
        layout.addWidget(preview_label)

        self.data_preview = QTextEdit()
        self.data_preview.setReadOnly(True)
        self.data_preview.setFont(QFont("Courier New", 10))

        # Format JSON with color highlighting for empty results
        if not self.result_data or (isinstance(self.result_data, dict) and not self.result_data):
            self.data_preview.setPlainText("{}\n\n(Empty result - no matching keys)")
            self.data_preview.setStyleSheet("background-color: #3a3a3a; color: #CE9178;")
        else:
            self.data_preview.setPlainText(json.dumps(self.result_data, indent=2))

        layout.addWidget(self.data_preview)

        # Storage options
        storage_group = QGroupBox(tr("operation_preview.group_storage"))
        storage_layout = QHBoxLayout()

        storage_label = QLabel(tr("operation_preview.lbl_store_slot"))
        storage_layout.addWidget(storage_label)

        self.slot_combo = QComboBox()
        if self.available_slots:
            self.slot_combo.addItems(self.available_slots)
        else:
            self.slot_combo.addItem(tr("operation_preview.no_slots"))
            self.slot_combo.setEnabled(False)
        self.slot_combo.setToolTip(tooltip_tr("operation_preview.tooltip_slot"))
        storage_layout.addWidget(self.slot_combo)

        storage_layout.addStretch()

        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # Store button
        self.btn_store = QPushButton(tr("operation_preview.btn_store"))
        self.btn_store.setStyleSheet("background-color: #0e639c; color: white;")
        self.btn_store.setToolTip(tooltip_tr("operation_preview.tooltip_store"))
        self.btn_store.clicked.connect(self._store_result)
        self.btn_store.setEnabled(bool(self.available_slots))
        btn_layout.addWidget(self.btn_store)

        # Discard button
        self.btn_discard = QPushButton(tr("operation_preview.btn_discard"))
        self.btn_discard.setToolTip(tooltip_tr("operation_preview.tooltip_discard"))
        self.btn_discard.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_discard)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _format_stats_summary(self) -> str:
        """
        Format statistics summary for display.

        Returns:
            Formatted statistics string
        """
        stats = self.result_stats

        lines = []
        lines.append(f"Keys Count: {stats.get('total_keys', 0)}")
        lines.append(f"Size: {stats.get('size_bytes', 0)} bytes")
        lines.append(f"Max Depth: {stats.get('max_depth', 0)}")
        lines.append(f"Unique Keys: {stats.get('unique_keys', 0)}")
        lines.append(f"Duplicate Keys: {stats.get('duplicate_keys', 0)}")

        # Value types
        value_types = stats.get("value_types", {})
        types_str = ", ".join([f"{k}: {v}" for k, v in value_types.items() if v > 0])
        lines.append(f"Value Types: {types_str}")

        return "\n".join(lines)

    def _store_result(self):
        """Store result in selected slot."""
        if not self.available_slots:
            QMessageBox.warning(
                self,
                "No Slots Available",
                "All memory slots are occupied.\n\n" "Please clear a slot before storing new results.",
            )
            return

        # Get selected slot
        self.target_slot = self.slot_combo.currentText()

        # Confirm if result is empty
        if not self.result_data or (isinstance(self.result_data, dict) and not self.result_data):
            reply = QMessageBox.question(
                self,
                "Empty Result",
                f"The result is empty (no matching keys).\n\n"
                f"Store empty result in Slot {self.target_slot}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

        self.store_result = True
        self.accept()

    def get_storage_info(self) -> tuple:
        """
        Get storage information.

        Returns:
            Tuple (store: bool, target_slot: Optional[str])
        """
        return self.store_result, self.target_slot
