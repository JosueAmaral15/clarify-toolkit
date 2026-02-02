#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Regex Insert Panel - Memory Register Integration

Panel GUI para capturar valores via regex e inserir chaves/valores
usando os valores capturados (memory registers).

Pattern: Composite (GoF) + Observer (GoF) + Memento (GoF)
- Reusable component
- Signal-based communication
- Memory register integration

Use Case:
1. User tem JSON: {"name": "John Doe", "email": "john@example.com"}
2. User captura via regex: r'"email": "(.*?)@(.*?)"'
   - $0 = "john@example.com"
   - $1 = "john"
   - $2 = "example.com"
3. User insere novo campo usando registers:
   - Key: "username"
   - Value: "$1"
   - Result: "username": "john"

Features:
- Regex capture com preview
- Memory register display
- Template insertion com $N placeholders
- Target key selection (onde inserir)
- QSettings persistence
"""

# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=line-too-long  # Qt string literals & descriptions
# pylint: disable=import-outside-toplevel  # Conditional imports
# pylint: disable=too-many-instance-attributes  # Complex UI panel
# pylint: disable=attribute-defined-outside-init  # Qt widget pattern
# pylint: disable=broad-exception-caught  # UI error handling robustness
from __future__ import annotations
from typing import Optional

from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QCheckBox
)

from src.core.memory_register import MemoryRegister
from src.i18n.translator import tr, tooltip_tr


class RegexInsertPanel(QWidget):
    """
    Regex Insert Panel with Memory Register.

    Signals:
        insert_requested(target_key, new_key, new_value, position)

    Features:
    - Regex pattern input
    - Capture button (populates registers)
    - Register table display ($0, $1, ... values)
    - Template input (supports $N placeholders)
    - Target key selection
    - Position (before/after/inside target key)
    - Preview button

    Usage:
        panel = RegexInsertPanel()
        panel.insert_requested.connect(self._handle_regex_insert)
        layout.addWidget(panel)
    """

    # Signal: (target_key, new_key, new_value, position)
    insert_requested = Signal(str, str, str, str)

    def __init__(self, parent=None, settings_prefix: str = "regex_insert"):
        """
        Initialize regex insert panel.

        Args:
            parent: Parent widget
            settings_prefix: QSettings key prefix
        """
        super().__init__(parent)
        self.settings_prefix = settings_prefix
        self.settings = QSettings("Clarify", "Clarify")
        self.register = MemoryRegister()

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main group
        group = QGroupBox(tr("regex_insert.group_main"))
        group_layout = QVBoxLayout()

        # === STEP 1: Capture Phase ===
        capture_group = QGroupBox(tr("regex_insert.group_capture"))
        capture_layout = QGridLayout()

        # Source text (where to search)
        capture_layout.addWidget(QLabel(tr("regex_insert.lbl_source")), 0, 0)
        self.combo_source = QComboBox()
        self.combo_source.addItems([tr("regex_insert.combo_current_editor"), tr("regex_insert.combo_selection"), tr("regex_insert.combo_custom")])
        self.combo_source.setToolTip(tooltip_tr("regex_insert.tooltip_source"))
        capture_layout.addWidget(self.combo_source, 0, 1, 1, 2)

        # Regex pattern
        capture_layout.addWidget(QLabel(tr("regex_insert.lbl_pattern")), 1, 0)
        self.ed_pattern = QLineEdit()
        self.ed_pattern.setPlaceholderText(tr("regex_insert.placeholder_pattern"))
        self.ed_pattern.setToolTip(tooltip_tr("regex_insert.tooltip_pattern"))
        capture_layout.addWidget(self.ed_pattern, 1, 1, 1, 2)

        # Flags
        flags_layout = QHBoxLayout()
        self.chk_case_insensitive = QCheckBox(tr("regex_insert.chk_case_insensitive"))
        self.chk_case_insensitive.setToolTip(tooltip_tr("regex_insert.tooltip_case_insensitive"))
        flags_layout.addWidget(self.chk_case_insensitive)

        self.chk_multiline = QCheckBox(tr("regex_insert.chk_multiline"))
        self.chk_multiline.setToolTip(tooltip_tr("regex_insert.tooltip_multiline"))
        flags_layout.addWidget(self.chk_multiline)
        flags_layout.addStretch()
        capture_layout.addLayout(flags_layout, 2, 0, 1, 3)

        # Capture button
        btn_capture_layout = QHBoxLayout()
        self.btn_capture = QPushButton(tr("regex_insert.btn_capture"))
        self.btn_capture.setToolTip(tooltip_tr("regex_insert.tooltip_capture"))
        self.btn_capture.clicked.connect(self._execute_capture)
        btn_capture_layout.addWidget(self.btn_capture)

        self.btn_test_pattern = QPushButton(tr("regex_insert.btn_test"))
        self.btn_test_pattern.setToolTip(tooltip_tr("regex_insert.tooltip_test_pattern"))
        self.btn_test_pattern.clicked.connect(self._test_pattern)
        btn_capture_layout.addWidget(self.btn_test_pattern)

        self.btn_clear_registers = QPushButton(tr("regex_insert.btn_clear"))
        self.btn_clear_registers.setToolTip(tooltip_tr("regex_insert.tooltip_clear_registers"))
        self.btn_clear_registers.clicked.connect(self._clear_registers)
        btn_capture_layout.addWidget(self.btn_clear_registers)
        btn_capture_layout.addStretch()

        capture_layout.addLayout(btn_capture_layout, 3, 0, 1, 3)

        capture_group.setLayout(capture_layout)
        group_layout.addWidget(capture_group)

        # === Registers Display ===
        registers_group = QGroupBox(tr("regex_insert.group_registers"))
        registers_layout = QVBoxLayout()

        self.table_registers = QTableWidget()
        self.table_registers.setColumnCount(3)
        self.table_registers.setHorizontalHeaderLabels([tr("regex_insert.table_register"), tr("regex_insert.table_value"), tr("regex_insert.table_source")])
        self.table_registers.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_registers.setMaximumHeight(120)
        self.table_registers.setToolTip(tooltip_tr("regex_insert.tooltip_registers_table"))
        registers_layout.addWidget(self.table_registers)

        registers_group.setLayout(registers_layout)
        group_layout.addWidget(registers_group)

        # === STEP 2: Insert Phase ===
        insert_group = QGroupBox(tr("regex_insert.group_insert"))
        insert_layout = QGridLayout()

        # Target key (onde inserir)
        insert_layout.addWidget(QLabel(tr("regex_insert.lbl_target_key")), 0, 0)
        self.ed_target_key = QLineEdit()
        self.ed_target_key.setPlaceholderText(tr("regex_insert.placeholder_target"))
        self.ed_target_key.setToolTip(tooltip_tr("regex_insert.tooltip_target_key"))
        insert_layout.addWidget(self.ed_target_key, 0, 1, 1, 2)

        # Position
        insert_layout.addWidget(QLabel(tr("regex_insert.lbl_position")), 1, 0)
        self.combo_position = QComboBox()
        self.combo_position.addItems([tr("regex_insert.combo_inside"), tr("regex_insert.combo_before"), tr("regex_insert.combo_after")])
        self.combo_position.setToolTip(tooltip_tr("regex_insert.tooltip_position"))
        insert_layout.addWidget(self.combo_position, 1, 1, 1, 2)

        # New key
        insert_layout.addWidget(QLabel(tr("regex_insert.lbl_new_key")), 2, 0)
        self.ed_new_key = QLineEdit()
        self.ed_new_key.setPlaceholderText(tr("regex_insert.placeholder_new_key"))
        self.ed_new_key.setToolTip(tooltip_tr("regex_insert.tooltip_new_key"))
        insert_layout.addWidget(self.ed_new_key, 2, 1, 1, 2)

        # New value (template with $N)
        insert_layout.addWidget(QLabel(tr("regex_insert.lbl_new_value")), 3, 0)
        self.ed_new_value = QLineEdit()
        self.ed_new_value.setPlaceholderText(tr("regex_insert.placeholder_new_value"))
        self.ed_new_value.setToolTip(tooltip_tr("regex_insert.tooltip_new_value"))
        insert_layout.addWidget(self.ed_new_value, 3, 1, 1, 2)

        # Insert button
        btn_insert_layout = QHBoxLayout()
        self.btn_insert = QPushButton(tr("regex_insert.btn_insert"))
        self.btn_insert.setToolTip(tooltip_tr("regex_insert.tooltip_insert"))
        self.btn_insert.clicked.connect(self._execute_insert)
        btn_insert_layout.addWidget(self.btn_insert)

        self.btn_preview = QPushButton(tr("regex_insert.btn_preview"))
        self.btn_preview.setToolTip(tooltip_tr("regex_insert.tooltip_preview"))
        self.btn_preview.clicked.connect(self._preview_insert)
        btn_insert_layout.addWidget(self.btn_preview)
        btn_insert_layout.addStretch()

        insert_layout.addLayout(btn_insert_layout, 4, 0, 1, 3)

        insert_group.setLayout(insert_layout)
        group_layout.addWidget(insert_group)

        group.setLayout(group_layout)
        layout.addWidget(group)

    def set_source_text(self, text: str):
        """Set source text for regex capture (used by parent)."""
        self._source_text = text

    def _execute_capture(self):
        """Execute regex capture."""
        pattern = self.ed_pattern.text().strip()
        if not pattern:
            QMessageBox.warning(self, tr("regex_insert.msg_empty_pattern2_title"), tr("regex_insert.msg_empty_pattern2_msg"))
            return

        # Get source text (from parent or custom)
        source_text = getattr(self, '_source_text', "")
        if not source_text:
            QMessageBox.warning(self, tr("regex_insert.msg_no_source_title"), tr("regex_insert.msg_no_source_msg"))
            return

        # Build flags
        import re
        flags = 0
        if self.chk_case_insensitive.isChecked():
            flags |= re.IGNORECASE
        if self.chk_multiline.isChecked():
            flags |= re.MULTILINE

        # Capture
        try:
            num_registers, values = self.register.capture(source_text, pattern, flags)

            # Update table
            self._update_registers_table()

            # Show feedback
            QMessageBox.information(
                self,
                tr("regex_insert.msg_capture_complete_title"),
                tr("regex_insert.msg_capture_complete_msg").format(num_registers) + "\n" +
                "\n".join(f"${i} = {v[:50]}" for i, v in enumerate(values[:5]))
            )

            # Save settings
            self._save_settings()

        except Exception as e:
            QMessageBox.critical(self, tr("regex_insert.msg_capture_error_title"), tr("regex_insert.msg_capture_error_msg").format(str(e)))

    def _update_registers_table(self):
        """Update registers table display."""
        self.table_registers.setRowCount(0)

        registers = self.register.get_all()
        for idx in sorted(registers.keys()):
            value = registers[idx]
            row = self.table_registers.rowCount()
            self.table_registers.insertRow(row)

            # Register column
            self.table_registers.setItem(row, 0, QTableWidgetItem(f"${idx}"))

            # Value column (truncate if long)
            display_value = value if len(value) <= 50 else value[:47] + "..."
            self.table_registers.setItem(row, 1, QTableWidgetItem(display_value))

            # Source column
            entry = self.register.registers.get(idx)
            source_hint = entry.source_text[:30] + "..." if entry else ""
            self.table_registers.setItem(row, 2, QTableWidgetItem(source_hint))

    def _test_pattern(self):
        """Test regex pattern validity."""
        import re
        pattern = self.ed_pattern.text().strip()
        if not pattern:
            QMessageBox.warning(self, tr("regex_insert.msg_empty_pattern_title"), tr("regex_insert.msg_empty_pattern_msg"))
            return

        try:
            compiled = re.compile(pattern)
            groups = compiled.groups
            QMessageBox.information(
                self,
                tr("regex_insert.msg_pattern_valid_title"),
                tr("regex_insert.msg_pattern_valid_msg").format(groups, compiled.pattern)
            )
        except re.error as e:
            QMessageBox.critical(
                self,
                tr("regex_insert.msg_pattern_error_title"),
                tr("regex_insert.msg_pattern_error_msg").format(str(e))
            )

    def _clear_registers(self):
        """Clear all registers."""
        self.register.clear()
        self._update_registers_table()
        QMessageBox.information(self, tr("regex_insert.msg_cleared_title"), tr("regex_insert.msg_cleared_msg"))

    def _execute_insert(self):
        """Execute insert using registers."""
        target_key = self.ed_target_key.text().strip()
        new_key = self.ed_new_key.text().strip()
        new_value_template = self.ed_new_value.text().strip()
        position = self.combo_position.currentText()

        # Validate
        if not target_key:
            QMessageBox.warning(self, tr("regex_insert.msg_empty_target_title"), tr("regex_insert.msg_empty_target_msg"))
            return

        if not new_key:
            QMessageBox.warning(self, tr("regex_insert.msg_empty_key_title"), tr("regex_insert.msg_empty_key_msg"))
            return

        if not new_value_template:
            QMessageBox.warning(self, tr("regex_insert.msg_empty_value_title"), tr("regex_insert.msg_empty_value_msg"))
            return

        if not self.register.has_registers():
            QMessageBox.warning(self, tr("regex_insert.msg_no_registers_title"), tr("regex_insert.msg_no_registers_msg"))
            return

        # Replace $N in template
        try:
            new_value = self.register.replace_in_text(new_value_template)
        except Exception as e:
            QMessageBox.critical(self, tr("regex_insert.msg_template_error_title"), tr("regex_insert.msg_template_error_msg").format(str(e)))
            return

        # Save settings
        self._save_settings()

        # Emit signal
        self.insert_requested.emit(target_key, new_key, new_value, position)

    def _preview_insert(self):
        """Preview insert result."""
        target_key = self.ed_target_key.text().strip()
        new_key = self.ed_new_key.text().strip()
        new_value_template = self.ed_new_value.text().strip()
        position = self.combo_position.currentText()

        if not new_value_template or not self.register.has_registers():
            QMessageBox.warning(self, tr("regex_insert.msg_preview_not_ready_title"), tr("regex_insert.msg_preview_not_ready_msg"))
            return

        # Replace $N
        try:
            new_value = self.register.replace_in_text(new_value_template)

            QMessageBox.information(
                self,
                tr("regex_insert.msg_preview_title"),
                f"Target Key: {target_key or '(empty)'}\n"
                f"Position: {position}\n"
                f"New Key: {new_key or '(empty)'}\n"
                f"New Value: {new_value}\n\n"
                f"Template: {new_value_template}\n"
                f"Result JSON:\n"
                f'"{new_key}": "{new_value}"'
            )
        except Exception as e:
            QMessageBox.critical(self, tr("regex_insert.msg_preview_error_title"), str(e))

    def _save_settings(self):
        """Save settings to QSettings."""
        self.settings.setValue(f"{self.settings_prefix}/pattern", self.ed_pattern.text())
        self.settings.setValue(f"{self.settings_prefix}/target_key", self.ed_target_key.text())
        self.settings.setValue(f"{self.settings_prefix}/new_key", self.ed_new_key.text())
        self.settings.setValue(f"{self.settings_prefix}/new_value", self.ed_new_value.text())
        self.settings.setValue(f"{self.settings_prefix}/case_insensitive",
                              self.chk_case_insensitive.isChecked())
        self.settings.setValue(f"{self.settings_prefix}/multiline",
                              self.chk_multiline.isChecked())
        self.settings.setValue(f"{self.settings_prefix}/position",
                              self.combo_position.currentIndex())

    def _load_settings(self):
        """Load settings from QSettings."""
        self.ed_pattern.setText(
            self.settings.value(f"{self.settings_prefix}/pattern", "", str)
        )
        self.ed_target_key.setText(
            self.settings.value(f"{self.settings_prefix}/target_key", "", str)
        )
        self.ed_new_key.setText(
            self.settings.value(f"{self.settings_prefix}/new_key", "", str)
        )
        self.ed_new_value.setText(
            self.settings.value(f"{self.settings_prefix}/new_value", "", str)
        )
        self.chk_case_insensitive.setChecked(
            self.settings.value(f"{self.settings_prefix}/case_insensitive", False, bool)
        )
        self.chk_multiline.setChecked(
            self.settings.value(f"{self.settings_prefix}/multiline", False, bool)
        )
        self.combo_position.setCurrentIndex(
            self.settings.value(f"{self.settings_prefix}/position", 0, int)
        )
