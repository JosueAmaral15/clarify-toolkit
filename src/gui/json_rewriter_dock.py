#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Rewriter Dock - Modular implementation
Rewrites JSON/TS files with options to join keys, eliminate duplicates, and format output.
"""

from __future__ import annotations
import argparse
import os
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
    QSpinBox, QFileDialog, QMessageBox, QComboBox
)

from .base_dock import BaseDock

# Type checking imports
if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QWidgetType


# Import CLI dedupe function (assumed to exist in app.py)
def cli_dedupe(args: argparse.Namespace):
    """Execute the dedupe/rewrite operation based on args.
    
    Returns:
        tuple: (output_text, substitution_map) where substitution_map
               maps removed keys to their replacements (for Task #23)
    """
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
    
    # Build substitution map for eliminated keys (Task #23)
    substitution_map = {}
    if args.eliminate_duplicates:
        # Extract all keys before elimination
        old_keys = rw.extract_all_keys_from_dict(obj.data if hasattr(obj, 'data') else obj)
        obj = rw.eliminate_duplicates(obj)
        # Extract all keys after elimination
        new_keys = rw.extract_all_keys_from_dict(obj.data if hasattr(obj, 'data') else obj)
        # Build substitution map
        substitution_map = rw.build_substitution_map(old_keys, new_keys)
    
    # Exclude numeric keys if requested
    if hasattr(args, 'exclude_numeric') and args.exclude_numeric:
        obj = rw.exclude_numeric_keys(obj)
    
    # Skip empty values if requested
    if hasattr(args, 'skip_empty') and args.skip_empty:
        obj = rw.skip_empty_values(obj)
    
    # Avoid duplicate child keys if requested
    if hasattr(args, 'avoid_duplicate_child_keys') and args.avoid_duplicate_child_keys:
        obj = rw.avoid_duplicate_child_keys(obj)
    
    # Remove duplicate array values if requested (Task #8 - v2.9.8)
    if hasattr(args, 'remove_dup_consecutive') and args.remove_dup_consecutive:
        obj = rw.remove_duplicate_array_values(obj, consecutive_only=True)
    
    if hasattr(args, 'remove_dup_all') and args.remove_dup_all:
        obj = rw.remove_duplicate_array_values(obj, consecutive_only=False)
    
    # Skip keys without siblings if requested (Task #35 - v2.9.11)
    if hasattr(args, 'skip_no_siblings') and args.skip_no_siblings:
        obj = rw.skip_keys_without_siblings(obj)
    
    # Enforce consistent case if requested (Task #9 - v2.9.8)
    if hasattr(args, 'enforce_case') and args.enforce_case:
        case_style = getattr(args, 'case_style', 'camel')
        obj, warnings = rw.enforce_consistent_case(obj, target_case=case_style, warn_inconsistencies=True)
        if warnings:
            print(f"\n⚠️ Case inconsistencies detected and corrected ({len(warnings)} warnings):")
            for warning in warnings[:10]:  # Show first 10 warnings
                print(f"  - {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more warnings")
    
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
    
    return output_text, substitution_map


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
        self.chk_exclude_numeric = QCheckBox("Exclude numeric keys")
        self.chk_exclude_numeric.setToolTip("Skip keys that are purely numeric (e.g., '0', '123')")
        self.chk_skip_empty = QCheckBox("Skip empty values")
        self.chk_skip_empty.setToolTip("Skip empty strings, null, [], {}, and whitespace-only values")
        self.chk_avoid_dup_child = QCheckBox("Avoid duplicate child keys")
        self.chk_avoid_dup_child.setToolTip("Merge parent.child.child -> parent.child (e.g., t.pages.home.home -> t.pages.home)")
        self.chk_normalize_escaping = QCheckBox("Normalize escaping")
        self.chk_normalize_escaping.setToolTip("Auto-detect excessive escaping (\\\\\\' or more) and normalize to \\' (Task #22)")
        self.chk_convert_arrays = QCheckBox("Convert arrays to objects")
        self.chk_convert_arrays.setToolTip("Convert string arrays to objects with generated keys (Task #21)")
        self.chk_skip_no_siblings = QCheckBox("Skip keys without siblings")
        self.chk_skip_no_siblings.setToolTip("Remove serial hierarchies (chains) where keys don't have siblings (Task #35)")
        
        # Task #23 - Update orphaned references
        self.chk_update_refs = QCheckBox("Update references in project")
        self.chk_update_refs.setToolTip("Update orphaned translation references (t.key.path) in .tsx/.jsx files after eliminating duplicates (Task #23)")
        self.ed_project_dir = QLineEdit()
        self.ed_project_dir.setToolTip("Project directory containing .tsx/.jsx/.ts/.js files to update")
        self.btn_project_browse = QPushButton("Browse…")
        self.btn_project_browse.setToolTip("Browse for project directory")
        self.chk_ref_backup = QCheckBox("Create backups")
        self.chk_ref_backup.setToolTip("Create .bak files before modifying references")
        self.chk_ref_backup.setChecked(True)
        
        self.chk_remove_dup_consecutive = QCheckBox("Remove consecutive duplicates")
        self.chk_remove_dup_consecutive.setToolTip("Remove only consecutive duplicates in arrays: ['a','a','b'] → ['a','b']")
        self.chk_remove_dup_all = QCheckBox("Remove all duplicates")
        self.chk_remove_dup_all.setToolTip("Remove all duplicates in arrays (set behavior): ['a','b','a'] → ['a','b']")
        self.chk_enforce_case = QCheckBox("Enforce consistent case")
        self.chk_enforce_case.setToolTip("Automatically convert all keys to consistent case style (warns on inconsistencies)")
        self.chk_enforce_case.setChecked(True)  # Applied automatically
        self.combo_case_style = QComboBox()
        self.combo_case_style.addItems(["camelCase", "PascalCase", "snake_case", "kebab-case"])
        self.combo_case_style.setCurrentIndex(0)  # Default: camelCase
        self.combo_case_style.setToolTip("Target case style for key conversion")
        self.chk_validate_case = QCheckBox("Validate case before applying")
        self.chk_validate_case.setToolTip("Show preview dialog with before/after comparison before applying case conversion")
        self.chk_validate_case.setChecked(False)  # Optional validation
        self.chk_is_file = QCheckBox("Is file")
        self.chk_is_file.setToolTip("Input path is a single file (unchecked for directory)")
        self.chk_is_file.setChecked(True)
        
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
        
        # Row 2: Options checkboxes (line 1)
        g.addWidget(self.chk_from_ts, 2, 0)
        g.addWidget(self.chk_ts_out, 2, 1)
        g.addWidget(self.chk_join, 2, 2)
        g.addWidget(self.chk_elim, 2, 3)
        g.addWidget(self.chk_nlb, 2, 4)
        
        # Row 3: Options checkboxes (line 2)
        g.addWidget(self.chk_exclude_numeric, 3, 0)
        g.addWidget(self.chk_skip_empty, 3, 1)
        g.addWidget(self.chk_avoid_dup_child, 3, 2)
        g.addWidget(self.chk_normalize_escaping, 3, 3)
        g.addWidget(self.chk_is_file, 3, 4)
        
        # Row 4: Options checkboxes (line 3) - Array operations
        g.addWidget(self.chk_convert_arrays, 4, 0, 1, 2)
        g.addWidget(self.chk_remove_dup_consecutive, 4, 2, 1, 1)
        g.addWidget(self.chk_remove_dup_all, 4, 3, 1, 1)
        g.addWidget(self.chk_skip_no_siblings, 4, 4, 1, 1)
        
        # Row 5: Update references (Task #23)
        g.addWidget(self.chk_update_refs, 5, 0, 1, 1)
        g.addWidget(self.ed_project_dir, 5, 1, 1, 2)
        g.addWidget(self.btn_project_browse, 5, 3)
        g.addWidget(self.chk_ref_backup, 5, 4)
        
        # Row 6: Enforce consistent case
        g.addWidget(self.chk_enforce_case, 6, 0, 1, 2)
        g.addWidget(QLabel("Case style:"), 6, 2)
        g.addWidget(self.combo_case_style, 6, 3)
        g.addWidget(self.chk_validate_case, 6, 4)
        
        # Row 7: Indent and run button
        g.addWidget(self.lbl_indent, 7, 0)
        g.addWidget(self.spin_indent, 7, 1)
        g.addWidget(self.btn_run, 7, 4)
    
    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_in.clicked.connect(self._open_in)
        self.btn_out.clicked.connect(self._open_out)
        self.btn_project_browse.clicked.connect(self._browse_project_dir)
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
    
    def _browse_project_dir(self) -> None:
        """Browse for project directory (Task #23)."""
        d = QFileDialog.getExistingDirectory(
            self, "Select project directory",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if d:
            self.ed_project_dir.setText(d)
    
    # Core Processing
    
    def _rewrite(self) -> None:
        """Execute rewrite operation on selected file."""
        if not self.ed_in.text().strip():
            QMessageBox.warning(self, "Missing", "Choose an input file.")
            return
        
        # Case validation dialog (if enabled)
        if self.chk_enforce_case.isChecked() and self.chk_validate_case.isChecked():
            try:
                # Read and parse input file
                from .. import rewriter as rw
                with open(self.ed_in.text().strip(), 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Parse based on format
                if self.chk_from_ts.isChecked():
                    obj = rw.ts_process_full_preserving(text)
                else:
                    obj = rw.parse_json_preserving_duplicates_text(text)
                
                # Show validation dialog
                from .case_validator_dialog import show_case_validator
                accepted, obj_converted, warnings = show_case_validator(obj, self)
                
                # User cancelled
                if not accepted:
                    QMessageBox.information(self, "Cancelled", "Case conversion cancelled by user.")
                    return
                
                # User accepted - we'll use the converted object
                # But first, temporarily disable enforce_case to avoid double conversion
                # (We'll write the already-converted object)
                self.chk_enforce_case.setChecked(False)
                
                # Write the converted object to a temporary state
                # and let cli_dedupe handle the rest
                # Actually, we need to serialize it back to text first
                if self.chk_ts_out.isChecked():
                    temp_text = rw.dump_ts_node(obj_converted, indent=self.spin_indent.value())
                    if not self.chk_nlb.isChecked():
                        temp_text = rw.collapse_blank_lines(temp_text)
                else:
                    temp_text = rw.dump_ts_obj(obj_converted, indent=self.spin_indent.value())
                
                # Write to output
                out_path = self.ed_out.text().strip() or self.ed_in.text().strip()
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(temp_text)
                
                QMessageBox.information(self, "Done", f"Rewriter finished with {len(warnings)} case conversions.")
                
                # Re-enable enforce_case for next run
                self.chk_enforce_case.setChecked(True)
                return
                
            except Exception as e:
                QMessageBox.critical(self, "Validation Error", f"Failed to validate case: {e}")
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
            exclude_numeric=self.chk_exclude_numeric.isChecked(),
            skip_empty=self.chk_skip_empty.isChecked(),
            avoid_duplicate_child_keys=self.chk_avoid_dup_child.isChecked(),
            normalize_escaping=self.chk_normalize_escaping.isChecked(),
            convert_arrays_to_objects=self.chk_convert_arrays.isChecked(),
            remove_dup_consecutive=self.chk_remove_dup_consecutive.isChecked(),
            remove_dup_all=self.chk_remove_dup_all.isChecked(),
            skip_no_siblings=self.chk_skip_no_siblings.isChecked(),
            enforce_case=self.chk_enforce_case.isChecked(),
            case_style=self.combo_case_style.currentText().lower().replace('-', '').replace('case', ''),  # 'camelCase' -> 'camel'
            is_file=self.chk_is_file.isChecked(),
        )
        
        # Execute rewrite
        try:
            output_text, substitution_map = cli_dedupe(ns)
            
            # Task #23: Update orphaned references in project (if enabled)
            if self.chk_update_refs.isChecked() and substitution_map:
                project_dir = self.ed_project_dir.text().strip()
                
                if not project_dir:
                    QMessageBox.warning(self, "Missing", "Choose a project directory to update references.")
                    return
                
                if not os.path.isdir(project_dir):
                    QMessageBox.warning(self, "Invalid", f"Project directory does not exist: {project_dir}")
                    return
                
                # Show preview dialog with substitutions
                from .. import rewriter as rw
                results = rw.update_references_in_project(
                    project_dir,
                    substitution_map,
                    create_backup=self.chk_ref_backup.isChecked()
                )
                
                if results:
                    # Show summary
                    total_subs = sum(results.values())
                    file_count = len(results)
                    msg = f"Updated {total_subs} references in {file_count} files:\n\n"
                    for filepath, count in list(results.items())[:10]:
                        msg += f"  - {os.path.basename(filepath)}: {count} changes\n"
                    if file_count > 10:
                        msg += f"  ... and {file_count - 10} more files\n"
                    QMessageBox.information(self, "References Updated", msg)
                else:
                    QMessageBox.information(self, "No Changes", "No orphaned references found in project.")
            
            QMessageBox.information(self, "Done", "Rewriter finished.")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"{str(e)}\n\n{traceback.format_exc()}")
    
    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._rewrite()
