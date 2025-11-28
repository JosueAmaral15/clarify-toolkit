#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Rewriter Dock - Modular implementation
Rewrites JSON/TS files with options to join keys, eliminate duplicates, and format output.
"""

from __future__ import annotations
import argparse
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QFileDialog, QMessageBox
)

from .base_dock import BaseDock

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


# Import CLI dedupe function (assumed to exist in app.py)
def cli_dedupe(args: argparse.Namespace):
    """Execute the dedupe/rewrite operation based on args."""
    from .. import rewriter as rw
    
    # Read input
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Parse based on format
    if args.from_ts:
        # TypeScript/JavaScript object literal
        obj = rw.ts_process_full_preserving(text)
    else:
        # Pure JSON
        obj = rw.parse_json_preserving_duplicates_text(text)
    
    # Apply transformations
    if args.join_keys:
        obj = rw.join_keys(obj)
    
    if args.eliminate_duplicates:
        obj = rw.eliminate_duplicates(obj)
    
    # Serialize output
    if args.ts_out:
        output_text = rw.dump_ts_node(obj, indent=args.indent)
        if not args.no_line_break:
            output_text = rw.collapse_blank_lines(output_text)
    else:
        output_text = rw.dump_ts_obj(obj, indent=args.indent)
    
    # Write output
    out_path = args.output or args.input
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output_text)


class JsonRewriterDock(BaseDock):
    """
    Dock widget for JSON rewriter functionality.
    Rewrites JSON/TS files with deduplication and formatting options.
    
    Features:
    - Input/output file selection
    - From TS/JS option (preserve TypeScript format)
    - Emit export default option
    - Join keys option
    - Eliminate duplicates option
    - No blank lines option
    - Configurable indentation
    """
    
    def __init__(self, parent: QWidgetType | None = None):
        super().__init__("JSON Rewriter", parent)
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
    
    def _create_widgets(self) -> None:
        """Create all widgets for the rewriter dock."""
        # Input file section
        self.lbl_in = QLabel("Input file:")
        self.ed_in = QLineEdit()
        self.ed_in.setToolTip("JSON, TypeScript, or JavaScript file to rewrite")
        self.btn_in = QPushButton("Open…")
        self.btn_in.setToolTip("Browse for input file")
        
        # Output file section
        self.lbl_out = QLabel("Output file (optional):")
        self.ed_out = QLineEdit()
        self.ed_out.setToolTip("Optional output file path (defaults to input file if empty)")
        self.btn_out = QPushButton("Save as…")
        self.btn_out.setToolTip("Browse for output file")
        
        # Options checkboxes
        self.chk_from_ts = QCheckBox("From TS/JS (preserve file)")
        self.chk_from_ts.setToolTip("Parse as TypeScript/JavaScript and preserve format")
        self.chk_ts_out = QCheckBox("Emit export default …;")
        self.chk_ts_out.setToolTip("Add 'export default' statement to output")
        self.chk_join = QCheckBox("Join keys")
        self.chk_join.setToolTip("Join nested keys into single level (e.g., a.b.c)")
        self.chk_elim = QCheckBox("Eliminate duplicates")
        self.chk_elim.setToolTip("Remove duplicate keys, keeping the last occurrence")
        self.chk_nlb = QCheckBox("No blank lines")
        self.chk_nlb.setToolTip("Remove blank lines from output")
        
        # Indent spinner
        self.lbl_indent = QLabel("Indent (<=0 compact):")
        self.spin_indent = QSpinBox()
        self.spin_indent.setRange(-1, 16)
        self.spin_indent.setValue(2)
        self.spin_indent.setToolTip("Number of spaces for indentation (0 or negative for compact output)")
        
        # Action button
        self.btn_run = QPushButton("Rewrite")
    
    def _create_layout(self) -> None:
        """Arrange widgets in the dock."""
        g = QGridLayout()
        self.main_widget.setLayout(g)
        
        # Row 0: Input file
        g.addWidget(self.lbl_in, 0, 0)
        g.addWidget(self.ed_in, 0, 1, 1, 3)
        g.addWidget(self.btn_in, 0, 4)
        
        # Row 1: Output file
        g.addWidget(self.lbl_out, 1, 0)
        g.addWidget(self.ed_out, 1, 1, 1, 3)
        g.addWidget(self.btn_out, 1, 4)
        
        # Row 2: Options checkboxes
        g.addWidget(self.chk_from_ts, 2, 0)
        g.addWidget(self.chk_ts_out, 2, 1)
        g.addWidget(self.chk_join, 2, 2)
        g.addWidget(self.chk_elim, 2, 3)
        g.addWidget(self.chk_nlb, 2, 4)
        
        # Row 3: Indent and run button
        g.addWidget(self.lbl_indent, 3, 0)
        g.addWidget(self.spin_indent, 3, 1)
        g.addWidget(self.btn_run, 3, 4)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_in.clicked.connect(self._open_in)
        self.btn_out.clicked.connect(self._open_out)
        self.btn_run.clicked.connect(self._rewrite)
        self._setup_enter_key_execution(self.ed_in, self.ed_out)
    
    # UI Helper Methods
    
    def _open_in(self) -> None:
        """Browse for input file."""
        f, _ = QFileDialog.getOpenFileName(
            self, "Select input", "",
            "JSON/TS/JS (*.json *.ts *.tsx *.js *.jsx);;All (*)"
        )
        if f:
            self.ed_in.setText(f)
    
    def _open_out(self) -> None:
        """Browse for output file."""
        f, _ = QFileDialog.getSaveFileName(self, "Save output", "", "All (*)")
        if f:
            self.ed_out.setText(f)
    
    # Core Processing
    
    def _rewrite(self) -> None:
        """Execute rewrite operation on selected file."""
        if not self.ed_in.text().strip():
            QMessageBox.warning(self, "Missing", "Choose an input file.")
            return
        
        # Build argparse namespace with all options
        ns = argparse.Namespace(
            input=self.ed_in.text().strip(),
            output=self.ed_out.text().strip() or None,
            indent=self.spin_indent.value(),
            from_ts=self.chk_from_ts.isChecked(),
            ts_out=self.chk_ts_out.isChecked(),
            join_keys=self.chk_join.isChecked(),
            eliminate_duplicates=self.chk_elim.isChecked(),
            no_line_break=self.chk_nlb.isChecked(),
        )
        
        # Execute rewrite
        try:
            cli_dedupe(ns)
            QMessageBox.information(self, "Done", "Rewriter finished.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._rewrite()
