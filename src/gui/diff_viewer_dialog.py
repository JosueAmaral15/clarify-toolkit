"""
Diff Viewer Dialog for Clarify
Side-by-side visualization of JSON differences.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.99
"""

import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QPushButton, QSplitter, QGroupBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextCursor
from ..diff_analyzer import DiffAnalyzer


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Simple JSON syntax highlighter with diff coloring."""
    
    def __init__(self, parent, diff_keys: dict):
        """
        Initialize highlighter.
        
        Args:
            parent: Parent QTextDocument
            diff_keys: Dict mapping keys to categories (only_a, only_b, common, modified)
        """
        super().__init__(parent)
        self.diff_keys = diff_keys
        
        # Define formats for each category
        self.formats = {
            "only_a": self._create_format(QColor(200, 247, 197)),  # Light green
            "only_b": self._create_format(QColor(255, 204, 203)),  # Light red
            "common": self._create_format(QColor(255, 255, 204)),  # Light yellow
            "modified": self._create_format(QColor(255, 217, 179))  # Light orange
        }
    
    def _create_format(self, bg_color: QColor) -> QTextCharFormat:
        """Create text format with background color."""
        fmt = QTextCharFormat()
        fmt.setBackground(bg_color)
        return fmt
    
    def highlightBlock(self, text: str):
        """Highlight block of text based on diff categories."""
        # Extract key from line (format: "key": value)
        if '"' in text and ':' in text:
            # Find key name between quotes
            start = text.find('"')
            if start != -1:
                end = text.find('"', start + 1)
                if end != -1:
                    key = text[start + 1:end]
                    
                    # Check if key is in any diff category
                    for category, keys in self.diff_keys.items():
                        if key in keys:
                            # Highlight entire line
                            self.setFormat(0, len(text), self.formats[category])
                            break


class DiffViewerDialog(QDialog):
    """
    Dialog for side-by-side JSON diff visualization.
    
    Features:
    - Split view with synchronized scrolling
    - Color highlighting (green/red/yellow/orange)
    - Summary statistics
    - Export to HTML
    """
    
    def __init__(self, data_a: any, data_b: any, file_a_name: str, file_b_name: str, 
                 comparison_mode: str = "key_value", parent=None):
        """
        Initialize diff viewer dialog.
        
        Args:
            data_a: First dataset
            data_b: Second dataset
            file_a_name: Name of first file
            file_b_name: Name of second file
            comparison_mode: Comparison mode
            parent: Parent widget
        """
        super().__init__(parent)
        self.data_a = data_a
        self.data_b = data_b
        self.file_a_name = file_a_name
        self.file_b_name = file_b_name
        self.comparison_mode = comparison_mode
        
        # Analyze differences
        self.diff_result = DiffAnalyzer.analyze(data_a, data_b, comparison_mode)
        
        self.setWindowTitle(f"Diff Viewer: {file_a_name} vs {file_b_name}")
        self.setModal(False)
        self.resize(1200, 700)
        self._init_ui()
        self._populate_views()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"<h2>Diff Viewer: {self.file_a_name} vs {self.file_b_name}</h2>")
        layout.addWidget(title)
        
        # Summary
        summary_group = QGroupBox(tr("diff_viewer.group_summary"))
        summary_layout = QHBoxLayout(summary_group)
        
        summary_text = DiffAnalyzer.format_diff_summary(self.diff_result)
        summary_label = QLabel(summary_text)
        summary_label.setFont(QFont("Courier", 9))
        summary_layout.addWidget(summary_label)
        
        layout.addWidget(summary_group)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel(tr("diff_viewer.lbl_legend")))
        
        legend_only_a = QLabel(" Only in A ")
        legend_only_a.setStyleSheet("background-color: #c8f7c5; padding: 3px; border: 1px solid #aaa;")
        legend_layout.addWidget(legend_only_a)
        
        legend_only_b = QLabel(" Only in B ")
        legend_only_b.setStyleSheet("background-color: #ffcccb; padding: 3px; border: 1px solid #aaa;")
        legend_layout.addWidget(legend_only_b)
        
        legend_common = QLabel(" Common ")
        legend_common.setStyleSheet("background-color: #ffffcc; padding: 3px; border: 1px solid #aaa;")
        legend_layout.addWidget(legend_common)
        
        legend_modified = QLabel(" Modified ")
        legend_modified.setStyleSheet("background-color: #ffd9b3; padding: 3px; border: 1px solid #aaa;")
        legend_layout.addWidget(legend_modified)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (File A)
        left_panel = QGroupBox(f"File A: {self.file_a_name}")
        left_layout = QVBoxLayout(left_panel)
        
        self.text_a = QTextEdit()
        self.text_a.setReadOnly(True)
        self.text_a.setFont(QFont("Courier", 10))
        left_layout.addWidget(self.text_a)
        
        splitter.addWidget(left_panel)
        
        # Right panel (File B)
        right_panel = QGroupBox(f"File B: {self.file_b_name}")
        right_layout = QVBoxLayout(right_panel)
        
        self.text_b = QTextEdit()
        self.text_b.setReadOnly(True)
        self.text_b.setFont(QFont("Courier", 10))
        right_layout.addWidget(self.text_b)
        
        splitter.addWidget(right_panel)
        
        layout.addWidget(splitter)
        
        # Synchronized scrolling
        self.text_a.verticalScrollBar().valueChanged.connect(
            lambda val: self.text_b.verticalScrollBar().setValue(val)
        )
        self.text_b.verticalScrollBar().valueChanged.connect(
            lambda val: self.text_a.verticalScrollBar().setValue(val)
        )
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("📤 Export HTML")
        self.btn_export.setToolTip("Export diff as HTML file with color highlighting")
        self.btn_export.clicked.connect(self._export_html)
        btn_layout.addWidget(self.btn_export)
        
        btn_layout.addStretch()
        
        btn_close = QPushButton(tr("diff_viewer.btn_close"))
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def _populate_views(self):
        """Populate text views with formatted JSON and apply highlighting."""
        # Prepare formatted JSON for both sides
        json_a_lines = []
        json_b_lines = []
        
        # Build key categorization for highlighter
        diff_keys_a = {
            "only_a": set(self.diff_result["only_in_a"].keys()),
            "common": set(self.diff_result["common"].keys()),
            "modified": set(self.diff_result["modified"].keys())
        }
        
        diff_keys_b = {
            "only_b": set(self.diff_result["only_in_b"].keys()),
            "common": set(self.diff_result["common"].keys()),
            "modified": set(self.diff_result["modified"].keys())
        }
        
        # Format data A
        # Only in A (green)
        for key in sorted(self.diff_result["only_in_a"].keys()):
            value = self.diff_result["only_in_a"][key]
            json_a_lines.append(f'"{key}": {json.dumps(value)}')
        
        # Common (yellow)
        for key in sorted(self.diff_result["common"].keys()):
            value = self.diff_result["common"][key]["a"]
            json_a_lines.append(f'"{key}": {json.dumps(value)}')
        
        # Modified (orange)
        for key in sorted(self.diff_result["modified"].keys()):
            value = self.diff_result["modified"][key]["a"]
            json_a_lines.append(f'"{key}": {json.dumps(value)}')
        
        # Format data B
        # Only in B (red)
        for key in sorted(self.diff_result["only_in_b"].keys()):
            value = self.diff_result["only_in_b"][key]
            json_b_lines.append(f'"{key}": {json.dumps(value)}')
        
        # Common (yellow)
        for key in sorted(self.diff_result["common"].keys()):
            value = self.diff_result["common"][key]["b"]
            json_b_lines.append(f'"{key}": {json.dumps(value)}')
        
        # Modified (orange)
        for key in sorted(self.diff_result["modified"].keys()):
            value = self.diff_result["modified"][key]["b"]
            json_b_lines.append(f'"{key}": {json.dumps(value)}')
        
        # Set text
        self.text_a.setText("{\n  " + ",\n  ".join(json_a_lines) + "\n}")
        self.text_b.setText("{\n  " + ",\n  ".join(json_b_lines) + "\n}")
        
        # Apply syntax highlighting
        JsonSyntaxHighlighter(self.text_a.document(), diff_keys_a)
        JsonSyntaxHighlighter(self.text_b.document(), diff_keys_b)
    
    def _export_html(self):
        """Export diff as HTML file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Diff as HTML",
            f"diff_{self.file_a_name}_vs_{self.file_b_name}.html",
            "HTML Files (*.html)"
        )
        
        if not file_path:
            return
        
        try:
            DiffAnalyzer.export_diff_html(
                self.diff_result,
                self.file_a_name,
                self.file_b_name,
                file_path
            )
            
            QMessageBox.information(
                self,
                "Export Successful",
                f"Diff exported to:\n{file_path}\n\nOpen in browser to view with colors preserved."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export diff:\n{str(e)}"
            )
