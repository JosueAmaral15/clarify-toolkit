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
        group = QGroupBox("Regex Insert with Memory Register")
        group_layout = QVBoxLayout()
        
        # === STEP 1: Capture Phase ===
        capture_group = QGroupBox("Step 1: Capture Values")
        capture_layout = QGridLayout()
        
        # Source text (where to search)
        capture_layout.addWidget(QLabel("Source:"), 0, 0)
        self.combo_source = QComboBox()
        self.combo_source.addItems(["Current Editor", "Selection Only", "Custom Text"])
        self.combo_source.setToolTip("Where to search for regex matches")
        capture_layout.addWidget(self.combo_source, 0, 1, 1, 2)
        
        # Regex pattern
        capture_layout.addWidget(QLabel("Pattern:"), 1, 0)
        self.ed_pattern = QLineEdit()
        self.ed_pattern.setPlaceholderText(r'Regex pattern (e.g., "email": "(.*?)@(.*?)")')
        self.ed_pattern.setToolTip("Regex pattern with capture groups (use parentheses)")
        capture_layout.addWidget(self.ed_pattern, 1, 1, 1, 2)
        
        # Flags
        flags_layout = QHBoxLayout()
        self.chk_case_insensitive = QCheckBox("Case insensitive")
        self.chk_case_insensitive.setToolTip("Ignore case when matching")
        flags_layout.addWidget(self.chk_case_insensitive)
        
        self.chk_multiline = QCheckBox("Multiline")
        self.chk_multiline.setToolTip("^ and $ match line boundaries")
        flags_layout.addWidget(self.chk_multiline)
        flags_layout.addStretch()
        capture_layout.addLayout(flags_layout, 2, 0, 1, 3)
        
        # Capture button
        btn_capture_layout = QHBoxLayout()
        self.btn_capture = QPushButton("🎯 Capture")
        self.btn_capture.setToolTip("Execute regex capture and populate registers")
        self.btn_capture.clicked.connect(self._execute_capture)
        btn_capture_layout.addWidget(self.btn_capture)
        
        self.btn_test_pattern = QPushButton("🧪 Test")
        self.btn_test_pattern.setToolTip("Test regex pattern validity")
        self.btn_test_pattern.clicked.connect(self._test_pattern)
        btn_capture_layout.addWidget(self.btn_test_pattern)
        
        self.btn_clear_registers = QPushButton("🗑️ Clear")
        self.btn_clear_registers.setToolTip("Clear all registers")
        self.btn_clear_registers.clicked.connect(self._clear_registers)
        btn_capture_layout.addWidget(self.btn_clear_registers)
        btn_capture_layout.addStretch()
        
        capture_layout.addLayout(btn_capture_layout, 3, 0, 1, 3)
        
        capture_group.setLayout(capture_layout)
        group_layout.addWidget(capture_group)
        
        # === Registers Display ===
        registers_group = QGroupBox("Memory Registers")
        registers_layout = QVBoxLayout()
        
        self.table_registers = QTableWidget()
        self.table_registers.setColumnCount(3)
        self.table_registers.setHorizontalHeaderLabels(["Register", "Value", "Source"])
        self.table_registers.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_registers.setMaximumHeight(120)
        self.table_registers.setToolTip("Captured values ($0 = whole match, $1+ = groups)")
        registers_layout.addWidget(self.table_registers)
        
        registers_group.setLayout(registers_layout)
        group_layout.addWidget(registers_group)
        
        # === STEP 2: Insert Phase ===
        insert_group = QGroupBox("Step 2: Insert Using Registers")
        insert_layout = QGridLayout()
        
        # Target key (onde inserir)
        insert_layout.addWidget(QLabel("Target Key:"), 0, 0)
        self.ed_target_key = QLineEdit()
        self.ed_target_key.setPlaceholderText("Existing JSON key (e.g., 'user')")
        self.ed_target_key.setToolTip("JSON key where new field will be inserted")
        insert_layout.addWidget(self.ed_target_key, 0, 1, 1, 2)
        
        # Position
        insert_layout.addWidget(QLabel("Position:"), 1, 0)
        self.combo_position = QComboBox()
        self.combo_position.addItems(["Inside (as child)", "Before (sibling)", "After (sibling)"])
        self.combo_position.setToolTip("Where to insert relative to target key")
        insert_layout.addWidget(self.combo_position, 1, 1, 1, 2)
        
        # New key
        insert_layout.addWidget(QLabel("New Key:"), 2, 0)
        self.ed_new_key = QLineEdit()
        self.ed_new_key.setPlaceholderText("New key name (e.g., 'username')")
        self.ed_new_key.setToolTip("Name for the new JSON field")
        insert_layout.addWidget(self.ed_new_key, 2, 1, 1, 2)
        
        # New value (template with $N)
        insert_layout.addWidget(QLabel("New Value:"), 3, 0)
        self.ed_new_value = QLineEdit()
        self.ed_new_value.setPlaceholderText("Value template (use $0, $1, ... for registers)")
        self.ed_new_value.setToolTip("Value with $N placeholders (e.g., '$1@newdomain.com')")
        insert_layout.addWidget(self.ed_new_value, 3, 1, 1, 2)
        
        # Insert button
        btn_insert_layout = QHBoxLayout()
        self.btn_insert = QPushButton("📝 Insert")
        self.btn_insert.setToolTip("Insert new field using register values")
        self.btn_insert.clicked.connect(self._execute_insert)
        btn_insert_layout.addWidget(self.btn_insert)
        
        self.btn_preview = QPushButton("👁️ Preview")
        self.btn_preview.setToolTip("Preview resulting key/value before inserting")
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
            QMessageBox.warning(self, "Empty Pattern", "Please enter a regex pattern.")
            return
        
        # Get source text (from parent or custom)
        source_text = getattr(self, '_source_text', "")
        if not source_text:
            QMessageBox.warning(self, "No Source", "No source text available. Parent must call set_source_text().")
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
                "Capture Complete",
                f"Captured {num_registers} register(s):\n" + 
                "\n".join(f"${i} = {v[:50]}" for i, v in enumerate(values[:5]))
            )
            
            # Save settings
            self._save_settings()
            
        except Exception as e:
            QMessageBox.critical(self, "Capture Error", f"Error during capture:\n\n{str(e)}")
    
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
            QMessageBox.warning(self, "Empty Pattern", "Please enter a regex pattern.")
            return
        
        try:
            compiled = re.compile(pattern)
            groups = compiled.groups
            QMessageBox.information(
                self,
                "Pattern Valid ✓",
                f"Regex pattern is valid!\n\n"
                f"Capture groups: {groups}\n"
                f"Pattern: {compiled.pattern}"
            )
        except re.error as e:
            QMessageBox.critical(
                self,
                "Pattern Error ✗",
                f"Invalid regex pattern:\n\n{str(e)}"
            )
    
    def _clear_registers(self):
        """Clear all registers."""
        self.register.clear()
        self._update_registers_table()
        QMessageBox.information(self, "Cleared", "All registers cleared.")
    
    def _execute_insert(self):
        """Execute insert using registers."""
        target_key = self.ed_target_key.text().strip()
        new_key = self.ed_new_key.text().strip()
        new_value_template = self.ed_new_value.text().strip()
        position = self.combo_position.currentText()
        
        # Validate
        if not target_key:
            QMessageBox.warning(self, "Empty Target", "Please enter target key.")
            return
        
        if not new_key:
            QMessageBox.warning(self, "Empty Key", "Please enter new key name.")
            return
        
        if not new_value_template:
            QMessageBox.warning(self, "Empty Value", "Please enter new value template.")
            return
        
        if not self.register.has_registers():
            QMessageBox.warning(self, "No Registers", "Please capture values first (Step 1).")
            return
        
        # Replace $N in template
        try:
            new_value = self.register.replace_in_text(new_value_template)
        except Exception as e:
            QMessageBox.critical(self, "Template Error", f"Error replacing registers:\n\n{str(e)}")
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
            QMessageBox.warning(self, "Preview Not Ready", "Capture values first and enter template.")
            return
        
        # Replace $N
        try:
            new_value = self.register.replace_in_text(new_value_template)
            
            QMessageBox.information(
                self,
                "Preview",
                f"Target Key: {target_key or '(empty)'}\n"
                f"Position: {position}\n"
                f"New Key: {new_key or '(empty)'}\n"
                f"New Value: {new_value}\n\n"
                f"Template: {new_value_template}\n"
                f"Result JSON:\n"
                f'"{new_key}": "{new_value}"'
            )
        except Exception as e:
            QMessageBox.critical(self, "Preview Error", str(e))
    
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
