"""
Placeholder Replacer Dock Widget

Provides UI for batch replacement of placeholders (e.g., {t.key}) with values
from mapping files (JSON or CSV).
"""

import os
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout
from .base_dock import StandardToolDock
from src.placeholder_replacer import (
    parse_mapping_file, process_file, process_directory
)
from src.i18n.translator import tr, tooltip_tr


class PlaceholderReplacerDock(StandardToolDock):
    """Dock widget for placeholder replacement tool."""

    def __init__(self, parent=None) -> None:
        super().__init__(tr("placeholder_replacer.title"), parent)
        self._mapping = {}
        self._setup_tooltips()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        grid = QGridLayout()

        # Mapping file section
        grid.addWidget(QLabel(tr("placeholder_replacer.lbl_mapping")), 0, 0)
        self.ed_mapping = QLineEdit()
        self.ed_mapping.setPlaceholderText(tr("placeholder_replacer.placeholder_mapping"))
        self.btn_browse_mapping = QPushButton(tr("placeholder_replacer.btn_browse"))
        grid.addWidget(self.ed_mapping, 0, 1, 1, 3)
        grid.addWidget(self.btn_browse_mapping, 0, 4)

        # Target section
        lbl_target, self.ed_target, self.btn_browse_target, self.chk_is_file = self.create_file_input(
            "Target path:",
            "File or directory to process"
        )
        grid.addWidget(lbl_target, 1, 0)
        grid.addWidget(self.ed_target, 1, 1, 1, 3)
        grid.addWidget(self.btn_browse_target, 1, 4)

        self.chk_backup = QCheckBox(tr("placeholder_replacer.chk_backup"))
        self.chk_backup.setChecked(True)
        grid.addWidget(self.chk_is_file, 2, 0, 1, 2)
        grid.addWidget(self.chk_backup, 2, 2, 1, 2)

        # Options section
        grid.addWidget(QLabel(tr("placeholder_replacer.lbl_root_var")), 3, 0)
        self.ed_root_var = QLineEdit()
        self.ed_root_var.setText("t")
        self.ed_root_var.setMaximumWidth(100)
        grid.addWidget(self.ed_root_var, 3, 1)

        grid.addWidget(QLabel(tr("placeholder_replacer.lbl_scope_start")), 3, 2)
        self.ed_scope_start = QLineEdit()
        self.ed_scope_start.setPlaceholderText(tr("placeholder_replacer.placeholder_scope_start"))
        grid.addWidget(self.ed_scope_start, 3, 3, 1, 2)

        grid.addWidget(QLabel(tr("placeholder_replacer.lbl_scope_end")), 4, 2)
        self.ed_scope_end = QLineEdit()
        self.ed_scope_end.setPlaceholderText(tr("placeholder_replacer.placeholder_scope_end"))
        grid.addWidget(self.ed_scope_end, 4, 3, 1, 2)

        self.layout.addLayout(grid)

        # Action buttons
        buttons = [
            (tr("placeholder_replacer.btn_preview"), self._preview),
            (tr("placeholder_replacer.btn_replace"), self._replace),
            (tr("placeholder_replacer.btn_clear"), self._clear)
        ]
        btn_layout = self.create_action_buttons(buttons)
        self.layout.addLayout(btn_layout)

        # Store button references for tooltips
        preview_text = tr("placeholder_replacer.btn_preview")
        replace_text = tr("placeholder_replacer.btn_replace")
        clear_text = tr("placeholder_replacer.btn_clear")
        self.btn_preview = [btn for btn in self.findChildren(QPushButton) if btn.text() == preview_text][0]
        self.btn_replace = [btn for btn in self.findChildren(QPushButton) if btn.text() == replace_text][0]
        self.btn_clear = [btn for btn in self.findChildren(QPushButton) if btn.text() == clear_text][0]

        # Results panel
        lbl_results, self.text_results = self.create_results_panel()
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.text_results)

        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        self.layout.addLayout(editor_btn_layout)

        # Setup tooltips AFTER all widgets are created (v2.9.65)
        self._apply_tooltips()

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
            self, tr("placeholder_replacer.browse_mapping_title"), "",
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
            self.show_error(tr("common.error"), tr("placeholder_replacer.error_load_mapping").replace("{error}", str(e)))
            self._mapping = {}

    def _process(self, dry_run: bool = False) -> None:
        """Process files with or without dry-run."""
        target = self.ed_target.text().strip()
        if not target:
            self.show_warning(tr("common.warning"), tr("placeholder_replacer.warning_no_target"))
            return

        if not self._mapping:
            if self.ed_mapping.text():
                self.show_warning(tr("common.warning"), tr("placeholder_replacer.warning_no_mapping"))
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
                self.show_info(tr("common.success"), tr("placeholder_replacer.success_replacement"))

        except Exception as e:
            self.show_error(tr("common.error"), tr("placeholder_replacer.error_processing").replace("{error}", str(e)))

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

    def _setup_tooltips(self) -> None:
        """Setup internationalized tooltips for all widgets (v2.9.65)."""
        # Note: This is called from __init__ but actual tooltip application
        # happens in _apply_tooltips() after widgets are created in _setup_ui()
        pass

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips to all widgets (v2.9.65)."""
        # Mapping file section
        self.ed_mapping.setToolTip(
            tooltip_tr("placeholder_replacer.ed_mapping")
        )
        self.btn_browse_mapping.setToolTip(
            tooltip_tr("placeholder_replacer.btn_browse_mapping")
        )

        # Target section
        self.ed_target.setToolTip(
            tooltip_tr("placeholder_replacer.ed_target")
        )
        self.btn_browse_target.setToolTip(
            tooltip_tr("placeholder_replacer.btn_browse_target")
        )
        self.chk_is_file.setToolTip(
            tooltip_tr("placeholder_replacer.chk_is_file")
        )

        # Options section
        self.chk_backup.setToolTip(
            tooltip_tr("placeholder_replacer.chk_backup")
        )
        self.ed_root_var.setToolTip(
            tooltip_tr("placeholder_replacer.ed_root_var")
        )
        self.ed_scope_start.setToolTip(
            tooltip_tr("placeholder_replacer.ed_scope_start")
        )
        self.ed_scope_end.setToolTip(
            tooltip_tr("placeholder_replacer.ed_scope_end")
        )

        # Action buttons
        self.btn_preview.setToolTip(
            tooltip_tr("placeholder_replacer.btn_preview")
        )
        self.btn_replace.setToolTip(
            tooltip_tr("placeholder_replacer.btn_replace")
        )
        self.btn_clear.setToolTip(
            tooltip_tr("placeholder_replacer.btn_clear")
        )

        # Results panel
        self.text_results.setToolTip(
            tooltip_tr("placeholder_replacer.text_results")
        )
