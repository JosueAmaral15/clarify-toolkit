"""Dialog for previewing case conversion changes before applying them."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt
from typing import List, Tuple
from src.rewriter.types import JSONNode
from src.rewriter.operations import enforce_consistent_case
import json


class CaseValidatorDialog(QDialog):
    """
    Dialog that shows before/after preview of case conversion.
    User can review changes and choose to continue or cancel.
    """
    
    def __init__(self, node: JSONNode, parent=None):
        """Initialize Case Validator Dialog.
        
        Args:
            node: JSONNode object to validate and convert
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.setWindowTitle("Case Conversion Validator")
        self.resize(900, 600)
        
        self.original_node = node
        self.converted_node = None
        self.warnings = []
        
        self._build_ui()
        
    def _build_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Review Case Conversion Changes")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Case style selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Target Case Style:"))
        
        self.combo_case = QComboBox()
        self.combo_case.addItems(["camelCase", "PascalCase", "snake_case", "kebab-case"])
        self.combo_case.currentTextChanged.connect(self._update_preview)
        selector_layout.addWidget(self.combo_case)
        selector_layout.addStretch()
        
        layout.addLayout(selector_layout)
        
        # Before/After comparison
        comparison_layout = QHBoxLayout()
        
        # Before panel
        before_layout = QVBoxLayout()
        before_label = QLabel("Before (Original):")
        before_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        before_layout.addWidget(before_label)
        
        self.text_before = QTextEdit()
        self.text_before.setReadOnly(True)
        self.text_before.setStyleSheet("font-family: monospace; background-color: #2c3e50; color: #ecf0f1;")
        before_layout.addWidget(self.text_before)
        
        comparison_layout.addLayout(before_layout)
        
        # After panel
        after_layout = QVBoxLayout()
        after_label = QLabel("After (Converted):")
        after_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        after_layout.addWidget(after_label)
        
        self.text_after = QTextEdit()
        self.text_after.setReadOnly(True)
        self.text_after.setStyleSheet("font-family: monospace; background-color: #2c3e50; color: #ecf0f1;")
        after_layout.addWidget(self.text_after)
        
        comparison_layout.addLayout(after_layout)
        
        layout.addLayout(comparison_layout)
        
        # Warnings panel
        warnings_label = QLabel("Detected Changes:")
        warnings_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(warnings_label)
        
        self.text_warnings = QTextEdit()
        self.text_warnings.setReadOnly(True)
        self.text_warnings.setMaximumHeight(150)
        self.text_warnings.setStyleSheet("font-family: monospace; background-color: #34495e; color: #f39c12;")
        layout.addWidget(self.text_warnings)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        self.btn_apply = QPushButton("Apply Changes")
        self.btn_apply.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 16px;")
        self.btn_apply.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_apply)
        
        layout.addLayout(btn_layout)
        
        # Initial preview
        self._update_preview()
        
    def _update_preview(self):
        """Update the preview based on selected case style.
        
        Applies case conversion to original node and displays:
        - Converted JSON preview
        - Warnings list (if any)
        - Statistics (keys changed, warnings count)
        """
        case_map = {
            "camelCase": "camel",
            "PascalCase": "pascal",
            "snake_case": "snake",
            "kebab-case": "kebab"
        }
        
        selected = self.combo_case.currentText()
        target_case = case_map.get(selected, "camel")
        
        # Convert and collect warnings
        self.converted_node, self.warnings = enforce_consistent_case(
            self.original_node, 
            target_case=target_case,
            warn_inconsistencies=True
        )
        
        # Display before
        try:
            before_json = json.dumps(self.original_node, indent=2, ensure_ascii=False)
            self.text_before.setPlainText(before_json)
        except Exception as e:
            self.text_before.setPlainText(f"Error displaying original: {e}")
        
        # Display after
        try:
            after_json = json.dumps(self.converted_node, indent=2, ensure_ascii=False)
            self.text_after.setPlainText(after_json)
        except Exception as e:
            self.text_after.setPlainText(f"Error displaying converted: {e}")
        
        # Display warnings
        if self.warnings:
            warnings_text = f"Total changes: {len(self.warnings)}\n\n"
            warnings_text += "\n".join(f"• {w}" for w in self.warnings[:50])  # Limit to 50 for performance
            if len(self.warnings) > 50:
                warnings_text += f"\n\n... and {len(self.warnings) - 50} more changes"
            self.text_warnings.setPlainText(warnings_text)
        else:
            self.text_warnings.setPlainText("No changes detected. Keys are already in the target case style.")
            self.btn_apply.setEnabled(False)
        
    def get_result(self) -> Tuple[bool, JSONNode, List[str]]:
        """
        Get the dialog result.
        
        Returns:
            Tuple of (accepted, converted_node, warnings)
            - accepted: True if user clicked Apply, False if Cancel
            - converted_node: The converted JSON node (or original if cancelled)
            - warnings: List of warning messages
        """
        accepted = self.exec() == QDialog.DialogCode.Accepted
        if accepted:
            return (True, self.converted_node, self.warnings)
        else:
            return (False, self.original_node, [])


def show_case_validator(node: JSONNode, parent=None) -> Tuple[bool, JSONNode, List[str]]:
    """
    Show the case validator dialog.
    
    Args:
        node: The JSON node to validate/convert
        parent: Parent widget
        
    Returns:
        Tuple of (accepted, converted_node, warnings)
    """
    dialog = CaseValidatorDialog(node, parent)
    return dialog.get_result()
