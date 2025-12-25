#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Merge Preview Dialog - Preview merge operation before applying

Shows original, result, and merged data side-by-side with diff highlighting
to help user understand changes before applying merge.

v2.9.100 - Merge Results to File
Author: Josué Amaral
Date: 2025-12-23
"""

import json
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QTextEdit, QPushButton, QLabel, QMessageBox,
    QSplitter, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from src.i18n.translator import tr


class DiffHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for diff-style coloring in JSON preview."""
    
    def __init__(self, parent, diff_lines: Dict[int, str]):
        """
        Initialize DiffHighlighter.
        
        Args:
            parent: Parent QTextDocument
            diff_lines: Dict mapping line number to diff type ('added', 'removed', 'modified', 'unchanged')
        """
        super().__init__(parent)
        self.diff_lines = diff_lines
        
        # Define formats for different diff types
        self.format_added = QTextCharFormat()
        self.format_added.setBackground(QColor("#c8f7c5"))  # Light green
        
        self.format_removed = QTextCharFormat()
        self.format_removed.setBackground(QColor("#ffcccb"))  # Light red
        
        self.format_modified = QTextCharFormat()
        self.format_modified.setBackground(QColor("#ffffcc"))  # Light yellow
        
        self.format_unchanged = QTextCharFormat()
        # No background color for unchanged lines
    
    def highlightBlock(self, text: str):
        """Apply highlighting to a block of text."""
        # Get current block line number (0-indexed)
        block_num = self.currentBlock().blockNumber()
        
        # Get diff type for this line
        diff_type = self.diff_lines.get(block_num, 'unchanged')
        
        # Apply format based on diff type
        if diff_type == 'added':
            self.setFormat(0, len(text), self.format_added)
        elif diff_type == 'removed':
            self.setFormat(0, len(text), self.format_removed)
        elif diff_type == 'modified':
            self.setFormat(0, len(text), self.format_modified)


class MergePreviewDialog(QDialog):
    """Dialog for previewing merge operation before applying."""
    
    def __init__(
        self,
        original_data: Dict[str, Any],
        result_data: Dict[str, Any],
        merged_data: Dict[str, Any],
        mode: str,
        file_path: str,
        parent=None
    ):
        """
        Initialize MergePreviewDialog.
        
        Args:
            original_data: Original file content
            result_data: Set Operations result
            merged_data: Simulated merge result
            mode: Merge mode (replace/merge/new_file)
            file_path: Target file path
            parent: Parent widget
        """
        super().__init__(parent)
        self.original_data = original_data
        self.result_data = result_data
        self.merged_data = merged_data
        self.mode = mode
        self.file_path = file_path
        self.user_approved = False
        
        self.setWindowTitle(tr("merge_preview.title"))
        self.setMinimumSize(1000, 700)
        self.setModal(True)
        
        self._init_ui()
        self._populate_previews()
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # === Info Header ===
        info_layout = QHBoxLayout()
        
        mode_label = QLabel(f"<b>Mode:</b> {self.mode.replace('_', ' ').title()}")
        mode_label.setStyleSheet("font-size: 11pt;")
        
        file_label = QLabel(f"<b>Target:</b> {self.file_path}")
        file_label.setWordWrap(True)
        file_label.setStyleSheet("font-size: 10pt; color: #6A9955;")
        
        info_layout.addWidget(mode_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        layout.addWidget(file_label)
        
        # === Color Legend ===
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel(tr("merge_preview.lbl_legend")))
        
        legend_added = QLabel(tr("merge_preview.lbl_added"))
        legend_added.setStyleSheet("background-color: #c8f7c5; padding: 2px 8px; border: 1px solid #4CAF50;")
        
        legend_removed = QLabel(tr("merge_preview.lbl_removed"))
        legend_removed.setStyleSheet("background-color: #ffcccb; padding: 2px 8px; border: 1px solid #F44336;")
        
        legend_modified = QLabel(tr("merge_preview.lbl_modified"))
        legend_modified.setStyleSheet("background-color: #ffffcc; padding: 2px 8px; border: 1px solid #FFC107;")
        
        legend_layout.addWidget(legend_added)
        legend_layout.addWidget(legend_removed)
        legend_layout.addWidget(legend_modified)
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # === Preview Panels (3-way split) ===
        splitter = QSplitter(Qt.Horizontal)
        
        # Original panel
        original_group = QGroupBox(tr("merge_preview.group_original"))
        original_layout = QVBoxLayout()
        self.text_original = QTextEdit()
        self.text_original.setReadOnly(True)
        self.text_original.setFont(QFont("Courier", 10))
        original_layout.addWidget(self.text_original)
        original_group.setLayout(original_layout)
        splitter.addWidget(original_group)
        
        # Result panel
        result_group = QGroupBox(tr("merge_preview.group_result"))
        result_layout = QVBoxLayout()
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setFont(QFont("Courier", 10))
        result_layout.addWidget(self.text_result)
        result_group.setLayout(result_layout)
        splitter.addWidget(result_group)
        
        # Merged panel
        merged_group = QGroupBox(tr("merge_preview.group_merged"))
        merged_layout = QVBoxLayout()
        self.text_merged = QTextEdit()
        self.text_merged.setReadOnly(True)
        self.text_merged.setFont(QFont("Courier", 10))
        merged_layout.addWidget(self.text_merged)
        merged_group.setLayout(merged_layout)
        splitter.addWidget(merged_group)
        
        layout.addWidget(splitter)
        
        # === Summary Statistics ===
        self.lbl_summary = QLabel()
        self.lbl_summary.setWordWrap(True)
        self.lbl_summary.setStyleSheet("color: #6A9955; font-weight: bold;")
        layout.addWidget(self.lbl_summary)
        
        # === Action Buttons ===
        button_layout = QHBoxLayout()
        
        btn_export = QPushButton(tr("merge_preview.btn_save"))
        btn_export.setToolTip("Save preview to HTML file")
        btn_export.clicked.connect(self._export_preview)
        
        button_layout.addWidget(btn_export)
        button_layout.addStretch()
        
        self.btn_apply = QPushButton(tr("merge_preview.btn_apply"))
        self.btn_apply.setToolTip("Apply merge operation to file")
        self.btn_apply.clicked.connect(self._apply_merge)
        self.btn_apply.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        
        btn_cancel = QPushButton(tr("merge_preview.btn_cancel"))
        btn_cancel.setToolTip("Cancel merge operation")
        btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
    
    def _populate_previews(self):
        """Populate preview panels with formatted JSON."""
        # Format JSON with indentation
        original_json = json.dumps(self.original_data, indent=2, ensure_ascii=False)
        result_json = json.dumps(self.result_data, indent=2, ensure_ascii=False)
        merged_json = json.dumps(self.merged_data, indent=2, ensure_ascii=False)
        
        # Set text in panels
        self.text_original.setPlainText(original_json)
        self.text_result.setPlainText(result_json)
        self.text_merged.setPlainText(merged_json)
        
        # Calculate diff for highlighting
        diff_lines = self._calculate_diff(original_json, merged_json)
        
        # Apply diff highlighting to merged panel
        highlighter = DiffHighlighter(self.text_merged.document(), diff_lines)
        
        # Calculate summary statistics
        self._update_summary(original_json, merged_json)
    
    def _calculate_diff(self, original: str, merged: str) -> Dict[int, str]:
        """
        Calculate line-by-line diff between original and merged.
        
        Args:
            original: Original JSON text
            merged: Merged JSON text
        
        Returns:
            Dict mapping line number to diff type
        """
        original_lines = original.split('\n')
        merged_lines = merged.split('\n')
        
        diff_lines = {}
        
        # Simple line-by-line comparison
        max_len = max(len(original_lines), len(merged_lines))
        
        for i in range(len(merged_lines)):
            if i < len(original_lines):
                if merged_lines[i] == original_lines[i]:
                    diff_lines[i] = 'unchanged'
                else:
                    diff_lines[i] = 'modified'
            else:
                # Line exists in merged but not in original
                diff_lines[i] = 'added'
        
        return diff_lines
    
    def _update_summary(self, original: str, merged: str):
        """Update summary statistics label."""
        original_lines = len(original.split('\n'))
        merged_lines = len(merged.split('\n'))
        
        original_keys = self._count_keys(self.original_data)
        merged_keys = self._count_keys(self.merged_data)
        
        added_keys = merged_keys - original_keys
        
        summary = (
            f"📊 Summary: "
            f"{original_keys} keys (original) → {merged_keys} keys (merged) "
            f"| {added_keys:+d} keys change "
            f"| {original_lines} lines (original) → {merged_lines} lines (merged)"
        )
        
        self.lbl_summary.setText(summary)
    
    def _count_keys(self, data: Any, count: int = 0) -> int:
        """Recursively count keys in nested dict/list."""
        if isinstance(data, dict):
            count += len(data)
            for value in data.values():
                count = self._count_keys(value, count)
        elif isinstance(data, list):
            for item in data:
                count = self._count_keys(item, count)
        return count
    
    def _export_preview(self):
        """Export preview to HTML file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Preview",
            "merge_preview.html",
            "HTML Files (*.html)"
        )
        
        if not file_path:
            return
        
        try:
            html_content = self._generate_html()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            QMessageBox.information(
                self,
                "Preview Saved",
                f"Preview exported to:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export preview:\n{e}"
            )
    
    def _generate_html(self) -> str:
        """Generate HTML representation of preview."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Merge Preview - {self.file_path}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .info {{ background: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        .container {{ display: flex; gap: 20px; }}
        .panel {{ flex: 1; }}
        .panel h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: Courier, monospace; font-size: 12px; }}
        .added {{ background-color: #c8f7c5; }}
        .removed {{ background-color: #ffcccb; }}
        .modified {{ background-color: #ffffcc; }}
    </style>
</head>
<body>
    <h1>🔀 Merge Preview</h1>
    <div class="info">
        <p><strong>Mode:</strong> {self.mode.replace('_', ' ').title()}</p>
        <p><strong>Target File:</strong> {self.file_path}</p>
        <p>{self.lbl_summary.text()}</p>
    </div>
    
    <div class="container">
        <div class="panel">
            <h2>Original File</h2>
            <pre>{json.dumps(self.original_data, indent=2, ensure_ascii=False)}</pre>
        </div>
        <div class="panel">
            <h2>Set Operations Result</h2>
            <pre>{json.dumps(self.result_data, indent=2, ensure_ascii=False)}</pre>
        </div>
        <div class="panel">
            <h2>After Merge (Preview)</h2>
            <pre>{json.dumps(self.merged_data, indent=2, ensure_ascii=False)}</pre>
        </div>
    </div>
</body>
</html>"""
        return html
    
    def _apply_merge(self):
        """Confirm and apply merge operation."""
        reply = QMessageBox.question(
            self,
            "Apply Merge",
            f"Apply merge to file?\n\n{self.file_path}\n\n"
            f"Mode: {self.mode.replace('_', ' ').title()}\n"
            f"This action cannot be undone (except via backup if enabled).",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.user_approved = True
            self.accept()
    
    def is_approved(self) -> bool:
        """Check if user approved the merge."""
        return self.user_approved
