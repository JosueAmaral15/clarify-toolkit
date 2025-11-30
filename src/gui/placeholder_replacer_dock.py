"""
Placeholder Replacer Dock Widget

Provides UI for batch replacement of placeholders (e.g., {t.key}) with values
from mapping files (JSON or CSV).
"""

import os
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout
from ..gui.base_dock import StandardToolDock
from ..placeholder_replacer import (
    parse_mapping_file, process_file, process_directory
)


class PlaceholderReplacerDock(StandardToolDock):
    """Dock widget for placeholder replacement tool."""
    
    def __init__(self, parent=None) -> None:
        super().__init__("Placeholder Replacer", parent)
        self._mapping = {}
    
    def _setup_ui(self) -> None:
        """Setup UI components."""
        grid = QGridLayout()
        
        # Mapping file section
        grid.addWidget(QLabel("Mapping file:"), 0, 0)
        self.ed_mapping = QLineEdit()
        self.ed_mapping.setPlaceholderText("JSON or CSV file with translations")
        self.ed_mapping.setToolTip("Select a JSON or CSV file containing key-value mappings for placeholder replacement")
        self.btn_browse_mapping = QPushButton("Browse...")
        self.btn_browse_mapping.setToolTip("Browse for a mapping file")
        grid.addWidget(self.ed_mapping, 0, 1, 1, 3)
        grid.addWidget(self.btn_browse_mapping, 0, 4)
        
        # Target section
        lbl_target, self.ed_target, self.btn_browse_target, self.chk_is_file = self.create_file_input(
            "Target path:",
            "File or directory to process"
        )
        self.ed_target.setToolTip("Select the file or directory containing placeholders to replace")
        self.btn_browse_target.setToolTip("Browse for target file or directory")
        self.chk_is_file.setToolTip("Check if target is a file (unchecked for directory)")
        grid.addWidget(lbl_target, 1, 0)
        grid.addWidget(self.ed_target, 1, 1, 1, 3)
        grid.addWidget(self.btn_browse_target, 1, 4)
        
        self.chk_backup = QCheckBox("Create backups (.bak)")
        self.chk_backup.setChecked(True)
        self.chk_backup.setToolTip("Create .bak backup files before modifying originals")
        grid.addWidget(self.chk_is_file, 2, 0, 1, 2)
        grid.addWidget(self.chk_backup, 2, 2, 1, 2)
        
        # Options section
        grid.addWidget(QLabel("Root variable:"), 3, 0)
        self.ed_root_var = QLineEdit()
        self.ed_root_var.setText("t")
        self.ed_root_var.setMaximumWidth(100)
        self.ed_root_var.setToolTip("The root variable name for placeholders (e.g., 't' for {t.key})")
        grid.addWidget(self.ed_root_var, 3, 1)
        
        grid.addWidget(QLabel("Scope start (regex):"), 3, 2)
        self.ed_scope_start = QLineEdit()
        self.ed_scope_start.setPlaceholderText("Optional, e.g. <script>")
        self.ed_scope_start.setToolTip("Optional regex pattern to mark where replacement scope starts")
        grid.addWidget(self.ed_scope_start, 3, 3, 1, 2)
        
        grid.addWidget(QLabel("Scope end (regex):"), 4, 2)
        self.ed_scope_end = QLineEdit()
        self.ed_scope_end.setPlaceholderText("Optional, e.g. </script>")
        self.ed_scope_end.setToolTip("Optional regex pattern to mark where replacement scope ends")
        grid.addWidget(self.ed_scope_end, 4, 3, 1, 2)
        
        self.layout.addLayout(grid)
        
        # Action buttons
        buttons = [
            ("Preview", self._preview),
            ("Replace", self._replace),
            ("Clear", self._clear)
        ]
        btn_layout = self.create_action_buttons(buttons)
        self.layout.addLayout(btn_layout)
        
        # Results panel
        lbl_results, self.text_results = self.create_results_panel()
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.text_results)
        
        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        self.layout.addLayout(editor_btn_layout)
    
    def _connect_signals(self) -> None:
        """Connect signals."""
        self.btn_browse_mapping.clicked.connect(self._browse_mapping)
        self.btn_browse_target.clicked.connect(self._browse_target)
        self._setup_enter_key_execution(
            self.ed_mapping, self.ed_target, self.ed_root_var,
            self.ed_scope_start, self.ed_scope_end
        )
    
    def _browse_mapping(self) -> None:
        """Browse for mapping file."""
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Select mapping file", "",
            "Mapping files (*.json *.csv);;All (*)"
        )
        if path:
            self.ed_mapping.setText(path)
            self._load_mapping()
    
    def _browse_target(self) -> None:
        """Browse for target file or directory."""
        self.browse_file_or_directory(
            self.ed_target,
            self.chk_is_file.isChecked(),
            "Source files (*.js *.jsx *.ts *.tsx *.html);;All (*)"
        )
    
    def _load_mapping(self) -> None:
        """Load mapping file."""
        mapping_file = self.ed_mapping.text().strip()
        if not mapping_file:
            return
        
        try:
            self._mapping = parse_mapping_file(mapping_file)
            self.append_result(
                self.text_results,
                f"✓ Loaded {len(self._mapping)} mappings from {os.path.basename(mapping_file)}\n"
            )
        except Exception as e:
            self.show_error("Error", f"Failed to load mapping file:\n{str(e)}")
            self._mapping = {}
    
    def _process(self, dry_run: bool = False) -> None:
        """Process files with or without dry-run."""
        target = self.ed_target.text().strip()
        if not target:
            self.show_warning("No Target", "Please select a file or directory.")
            return
        
        if not self._mapping:
            if not self.ed_mapping.text().strip():
                self.show_warning("No Mapping", "Please select a mapping file.")
                return
            self._load_mapping()
            if not self._mapping:
                return
        
        root_var = self.ed_root_var.text().strip() or "t"
        scope_start = self.ed_scope_start.text().strip() or None
        scope_end = self.ed_scope_end.text().strip() or None
        create_backup = self.chk_backup.isChecked() and not dry_run
        
        try:
            self.clear_results(self.text_results)
            
            if self.chk_is_file.isChecked():
                # Single file
                count, modified = process_file(
                    target,
                    self._mapping,
                    root_var,
                    scope_start,
                    scope_end,
                    create_backup,
                    dry_run
                )
                
                if dry_run:
                    self.append_result(self.text_results, f"=== Preview: {os.path.basename(target)} ===\n")
                    self.append_result(self.text_results, f"Would replace {count} placeholders\n")
                    if count > 0:
                        self.append_result(self.text_results, "\nModified content preview:\n")
                        self.append_result(self.text_results, modified[:2000])
                        if len(modified) > 2000:
                            self.append_result(self.text_results, "\n\n... (truncated)")
                else:
                    self.append_result(self.text_results, f"✓ Replaced {count} placeholders in {os.path.basename(target)}")
                    if create_backup:
                        self.append_result(self.text_results, f"  Backup: {target}.bak")
                
            else:
                # Directory
                results = process_directory(
                    target,
                    self._mapping,
                    root_var,
                    scope_start,
                    scope_end,
                    create_backup
                )
                
                total_count = sum(results.values())
                self.append_result(self.text_results, f"✓ Processed {len(results)} files\n")
                self.append_result(self.text_results, f"✓ Replaced {total_count} placeholders total\n\n")
                
                if results:
                    self.append_result(self.text_results, "Files modified:")
                    for file_path, count in results.items():
                        rel_path = os.path.relpath(file_path, target)
                        self.append_result(self.text_results, f"  {rel_path}: {count} replacements")
            
            if not dry_run:
                self.show_info("Success", "Replacement completed!")
            
        except Exception as e:
            self.show_error("Error", f"Processing failed:\n{str(e)}")
    
    def _preview(self) -> None:
        """Preview replacements without making changes."""
        self._process(dry_run=True)
    
    def _replace(self) -> None:
        """Execute replacements."""
        self._process(dry_run=False)
    
    def _clear(self) -> None:
        """Clear results and reset mapping."""
        self.clear_results(self.text_results)
        self._mapping = {}
    
    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._replace()
