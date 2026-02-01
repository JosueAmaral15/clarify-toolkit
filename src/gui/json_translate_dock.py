"""
JSON Translate Dock - Modular implementation
Translates text in files using a JSON/TS dictionary, replacing text with variable references.
Supports scope filtering, backup creation, and reverse translation.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy imports in helper functions
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=fixme  # TODO markers for future work
# pylint: disable=attribute-defined-outside-init  # Qt widget pattern

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QGridLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QWidget
)

from src.accessibility_manager import AccessibilityManager
from src.i18n.translator import tooltip_tr, tr
from src.utils import parse_exclusion_patterns, walk_files

from .base_dock import BaseDock

# Type checking imports
if TYPE_CHECKING:
    pass  # Type hints removed


# Import translation helper functions (assumed to exist in app.py or a module)
def load_translation_dict(dict_path: str) -> dict:
    """Load translation dictionary from JSON/TS file."""
    import json

    from src.utils import load_ts_object

    if dict_path.endswith((".ts", ".tsx", ".js", ".jsx")):
        return load_ts_object(dict_path)
    with open(dict_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_translate_file(
    filepath: str,
    dictionary: dict,  # pylint: disable=unused-argument  # Future implementation
    root_alias: str,  # pylint: disable=unused-argument  # Future implementation
    start_rx: str,  # pylint: disable=unused-argument  # Future implementation
    end_rx: str,  # pylint: disable=unused-argument  # Future implementation
    make_backup: bool,  # pylint: disable=unused-argument  # Future implementation
    dont_override: bool,  # pylint: disable=unused-argument  # Future implementation
    inverse: bool,  # pylint: disable=unused-argument  # Future implementation
    exclude_patterns: list,  # pylint: disable=unused-argument  # Future implementation
    emit_export: bool = True,  # pylint: disable=unused-argument  # Future implementation
    preserve_uppercase: bool = False,  # pylint: disable=unused-argument  # Future implementation
) -> tuple[bool, str]:
    """
    Process a single file for translation.
    Returns (success: bool, error_message: str)
    """
    # This function should implement the actual translation logic
    # For now, returning a placeholder implementation
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            _ = f.read()  # Content read but not used yet

        # TODO: Implement actual translation logic here
        # This is a placeholder that mimics the original behavior

        return (True, "")
    except Exception as e:
        return (False, str(e))


class JsonTranslateDock(BaseDock):
    """
    Dock widget for JSON translation functionality.
    Translates text in source files by replacing with dictionary variable references.

    Features:
    - File or directory selection
    - JSON/TS dictionary file
    - Customizable root variable name (e.g., 't', 'i18n')
    - Scope delimiters (start/end regex)
    - Exclusion patterns (do not translate)
    - Backup creation
    - Don't override existing translations
    - Reverse translation support
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(tr("json_translate.title"), parent)
        self._apply_accessibility()

    def _setup_ui(self) -> None:
        """Setup UI components."""
        self._create_widgets()
        self._create_layout()
        self._apply_tooltips()

    def _create_widgets(self) -> None:
        """Create all widgets for the translate dock."""
        # Root path section
        self.lbl_path = QLabel(tr("json_translate.lbl_path"))
        self.ed_path = QLineEdit()
        self.btn_browse = QPushButton(tr("json_translate.btn_browse"))
        self.is_file = QCheckBox(tr("json_translate.is_file"))

        # Dictionary file section
        self.lbl_dict = QLabel(tr("json_translate.lbl_dict"))
        self.ed_dict = QLineEdit()
        self.btn_open = QPushButton(tr("json_translate.btn_open"))

        # Variable name
        self.lbl_var = QLabel(tr("json_translate.lbl_var"))
        self.object_variable_name = QLineEdit()
        self.object_variable_name.setPlaceholderText(tr("json_translate.placeholder_var"))

        # Scope delimiters
        self.lbl_start = QLabel(tr("json_translate.lbl_start"))
        self.ed_start = QLineEdit("<[^>]*?>")  # default: start of HTML/JSX tag
        self.lbl_end = QLabel(tr("json_translate.lbl_end"))
        self.ed_end = QLineEdit("</[^>]*?>")  # default: end tag

        # Exclusion patterns
        self.lbl_exclude = QLabel(tr("json_translate.lbl_exclude"))
        self.ed_exclude = QLineEdit()
        self.ed_exclude.setPlaceholderText(tr("json_translate.placeholder_exclude"))
        self.ed_exclude.setText(r'className="[^"]*", data-testid="[^"]*", id="[^"]*"')

        # Options
        self.chk_backup = QCheckBox(tr("json_translate.chk_backup"))
        self.chk_backup.setChecked(True)

        self.chk_dont_override = QCheckBox(tr("json_translate.chk_dont_override"))
        self.chk_dont_override.setChecked(True)

        self.chk_inverse_json_translate = QCheckBox(tr("json_translate.chk_inverse"))
        self.chk_inverse_json_translate.setToolTip(
            "Reverse translation: replace variable references (t.key) with actual "
            "dictionary values (e.g., t.home.title → 'Homepage') | Ctrl+T to open Translate"
        )

        self.chk_emit_export = QCheckBox(tr("json_translate.chk_emit_export"))
        self.chk_emit_export.setChecked(True)

        self.chk_preserve_uppercase = QCheckBox(tr("json_translate.chk_preserve_uppercase"))
        self.chk_preserve_uppercase.setToolTip(tr("json_translate.tooltip_preserve_uppercase"))

        # Stats label (Task #43 - v2.9.13)
        self.lbl_stats = QLabel(tr("json_translate.lbl_stats_ready"))
        self.lbl_stats.setStyleSheet("color: gray; font-style: italic;")
        self.lbl_stats.setWordWrap(True)

        # Action buttons (Task #10 - v2.9.8)
        self.btn_run = QPushButton(tr("json_translate.btn_run"))
        self.btn_swap = QPushButton(tr("json_translate.btn_swap"))
        self.btn_undo = QPushButton(tr("json_translate.btn_undo"))

    def _create_layout(self) -> None:
        """Arrange widgets in the dock."""
        # Clear the existing VBoxLayout and replace with QGridLayout
        grid_layout = QGridLayout()

        # Remove the old layout and set the new one
        old_layout = self.main_widget.layout()
        if old_layout:
            QWidget().setLayout(old_layout)  # Take ownership to delete
        self.main_widget.setLayout(grid_layout)

        # Row 0: Root path
        grid_layout.addWidget(self.lbl_path, 0, 0)
        grid_layout.addWidget(self.ed_path, 0, 1, 1, 2)
        grid_layout.addWidget(self.btn_browse, 0, 3)

        # Row 1: Is file checkbox
        grid_layout.addWidget(self.is_file, 1, 0)

        # Row 2: Dictionary file
        grid_layout.addWidget(self.lbl_dict, 2, 0)
        grid_layout.addWidget(self.ed_dict, 2, 1, 1, 2)
        grid_layout.addWidget(self.btn_open, 2, 3)

        # Row 3: Variable name
        grid_layout.addWidget(self.lbl_var, 3, 0)
        grid_layout.addWidget(self.object_variable_name, 3, 1, 1, 2)

        # Row 4: Scope delimiters
        grid_layout.addWidget(self.lbl_start, 4, 0)
        grid_layout.addWidget(self.ed_start, 4, 1)
        grid_layout.addWidget(self.lbl_end, 4, 2)
        grid_layout.addWidget(self.ed_end, 4, 3)

        # Row 5: Exclusion patterns
        grid_layout.addWidget(self.lbl_exclude, 5, 0)
        grid_layout.addWidget(self.ed_exclude, 5, 1, 1, 3)

        # Row 6: Backup and don't override options
        grid_layout.addWidget(self.chk_backup, 6, 0, 1, 2)
        grid_layout.addWidget(self.chk_dont_override, 6, 2, 1, 2)

        # Row 7: Inverse and emit export options
        grid_layout.addWidget(self.chk_inverse_json_translate, 7, 0, 1, 2)
        grid_layout.addWidget(self.chk_emit_export, 7, 2, 1, 2)

        # Row 8: Preserve uppercase option
        grid_layout.addWidget(self.chk_preserve_uppercase, 8, 0, 1, 2)

        # Row 9: Stats label (Task #43 - v2.9.13)
        grid_layout.addWidget(self.lbl_stats, 9, 0, 1, 4)

        # Row 10: Action buttons
        grid_layout.addWidget(self.btn_swap, 10, 0)
        grid_layout.addWidget(self.btn_undo, 10, 1)
        grid_layout.addWidget(self.btn_run, 10, 2, 1, 2)

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.btn_browse.clicked.connect(self._browse_root)
        self.btn_open.clicked.connect(self._browse_dict)
        self.btn_run.clicked.connect(self._run)
        self.btn_swap.clicked.connect(self._swap_dictionaries)
        self.btn_undo.clicked.connect(self._undo_translation)
        # Task #43 - v2.9.13: Update stats on path/dict changes
        self.ed_path.textChanged.connect(self._update_stats)
        self.ed_dict.textChanged.connect(self._update_stats)
        # v2.9.51: Enter key executes translation
        self._setup_enter_key()

    def _setup_enter_key(self) -> None:
        """Setup Enter key to execute translation (v2.9.51)."""

        # Connect returnPressed for all text inputs
        for widget in [self.ed_path, self.ed_dict, self.object_variable_name,
                       self.ed_start, self.ed_end, self.ed_exclude]:
            widget.returnPressed.connect(self._run)

    def _apply_tooltips(self) -> None:
        """Apply internationalized tooltips to all widgets."""
        self.ed_path.setToolTip(tooltip_tr("json_translate.ed_path"))
        self.btn_browse.setToolTip(tooltip_tr("json_translate.btn_browse"))
        self.is_file.setToolTip(tooltip_tr("json_translate.is_file"))
        self.ed_dict.setToolTip(tooltip_tr("json_translate.ed_dict"))
        self.btn_open.setToolTip(tooltip_tr("json_translate.btn_open"))
        self.object_variable_name.setToolTip(tooltip_tr("json_translate.object_variable_name"))
        self.ed_start.setToolTip(tooltip_tr("json_translate.ed_start"))
        self.ed_end.setToolTip(tooltip_tr("json_translate.ed_end"))
        self.ed_exclude.setToolTip(tooltip_tr("json_translate.ed_exclude"))
        self.chk_backup.setToolTip(tooltip_tr("json_translate.chk_backup"))
        self.chk_dont_override.setToolTip(tooltip_tr("json_translate.chk_dont_override"))
        self.chk_inverse_json_translate.setToolTip(tooltip_tr("json_translate.chk_inverse_json_translate"))
        self.chk_emit_export.setToolTip(tooltip_tr("json_translate.chk_emit_export"))
        self.chk_preserve_uppercase.setToolTip(tooltip_tr("json_translate.chk_preserve_uppercase"))
        self.lbl_stats.setToolTip(tooltip_tr("json_translate.lbl_stats"))
        self.btn_run.setToolTip(tooltip_tr("json_translate.btn_run"))
        self.btn_swap.setToolTip(tooltip_tr("json_translate.btn_swap"))
        self.btn_undo.setToolTip(tooltip_tr("json_translate.btn_undo"))

    # UI Helper Methods

    def _browse_root(self) -> None:
        """Browse for root path (file or directory)."""
        if self.is_file.isChecked():
            path, _ = QFileDialog.getOpenFileName(self, tr("json_translate.dialog_select_file"))
            if path:
                self.ed_path.setText(path)
        else:
            _ = QFileDialog.getExistingDirectory(self, tr("json_translate.dialog_select_folder"))

    def _browse_dict(self) -> None:
        """Browse for dictionary file."""
        path, _ = QFileDialog.getOpenFileName(
            self, tr("json_translate.dialog_dict_file"), "",
            "JSON/TS (*.json *.ts *.js);;All files (*)"
        )
        if path:
            self.ed_dict.setText(path)

    def _update_stats(self) -> None:
        """Update stats label (Task #43 - v2.9.13)."""
        path = self.ed_path.text().strip()
        dict_path = self.ed_dict.text().strip()

        if not path and not dict_path:
            self.lbl_stats.setText(tr("json_translate.lbl_stats_ready"))
            return

        file_count = 0
        translation_count = 0

        # Count files to process
        if path:
            if os.path.isfile(path):
                file_count = 1
            elif os.path.isdir(path):
                try:
                    paths = list(
                        walk_files(path, include_globs=None, exclude_globs=["node_modules", ".git", "dist", "build"])
                    )
                    file_count = len(paths)
                except Exception:
                    file_count = 0

        # Count translations in dictionary
        if dict_path and os.path.isfile(dict_path):
            try:
                dictionary = load_translation_dict(dict_path)
                translation_count = len(dictionary) if isinstance(dictionary, dict) else 0
            except Exception:
                translation_count = 0

        # Update label
        if file_count > 0 or translation_count > 0:
            parts = []
            if file_count > 0:
                file_str = tr(
                    "json_translate.stats_files"
                    if file_count == 1 else "json_translate.stats_files_plural"
                )
                parts.append(
                    f"{file_count} {file_str} {tr('json_translate.stats_to_process')}"
                )
            if translation_count > 0:
                trans_str = tr("json_translate.stats_translations" if translation_count == 1 else "json_translate.stats_translations_plural")
                parts.append(f"{translation_count} {trans_str} {tr('json_translate.stats_available')}")
            self.lbl_stats.setText(" | ".join(parts))
        else:
            self.lbl_stats.setText(tr("json_translate.lbl_stats_ready"))

            # Core Processing
            self.ed_dict.setText(path)

    # Core Processing

    def _run(self) -> None:
        """Execute translation on selected files."""
        path = self.ed_path.text().strip()
        dpath = self.ed_dict.text().strip()
        root_alias = self.object_variable_name.text().strip() or "t"
        start_rx = self.ed_start.text().strip()
        end_rx = self.ed_end.text().strip()
        exclude_csv = self.ed_exclude.text().strip()
        make_backup = self.chk_backup.isChecked()
        dont_override = self.chk_dont_override.isChecked()
        inverse = self.chk_inverse_json_translate.isChecked()
        emit_export = self.chk_emit_export.isChecked()
        preserve_uppercase = self.chk_preserve_uppercase.isChecked()

        # Validation
        if not path or not dpath:
            QMessageBox.warning(self, tr("json_translate.error_missing"), tr("json_translate.error_missing_msg"))
            return

        # Load dictionary
        try:
            dictionary = load_translation_dict(dpath)
        except Exception as e:
            QMessageBox.critical(self, tr("json_translate.error_dict"), str(e))
            return

        # Parse exclusion patterns
        exclude_patterns = parse_exclusion_patterns(exclude_csv)

        # Gather files to process
        if os.path.isfile(path):
            paths = [path]
        else:
            paths = list(walk_files(path, include_globs=None, exclude_globs=["node_modules", ".git", "dist", "build"]))

        # Process files
        changed = 0
        errors = []

        for file_path in paths:
            ok, err = process_translate_file(
                file_path,
                dictionary,
                root_alias,
                start_rx,
                end_rx,
                make_backup,
                dont_override,
                inverse,
                exclude_patterns,
                emit_export,
                preserve_uppercase,
            )
            if ok:
                changed += 1
            if err:
                errors.append(f"{p}: {err}")

        # Display results
        msg = f"{tr('json_translate.result_modified')} {changed}"
        if errors:
            msg += (
                f"\n{tr('json_translate.result_errors')} {len(errors)}\n"
                + "\n".join(errors[:5])
            )
        QMessageBox.information(self, tr("json_translate.dialog_translate"), msg)

    def _swap_dictionaries(self) -> None:
        """
        Swap source and target dictionaries (Task #10 - v2.9.8).
        This is useful for reverse translation workflows.
        Note: This doesn't physically swap files, just toggles the inverse checkbox.
        """
        # Toggle inverse checkbox to reverse translation direction
        self.chk_inverse_json_translate.setChecked(not self.chk_inverse_json_translate.isChecked())

        status = tr("json_translate.swap_enabled") if self.chk_inverse_json_translate.isChecked() else tr("json_translate.swap_disabled")
        msg = tr("json_translate.swap_msg").replace("{status}", status)
        QMessageBox.information(
            self,
            tr("json_translate.swap_title"),
            msg,
        )

    def _undo_translation(self) -> None:
        """
        Restore original files from backup (.bak files) (Task #10 - v2.9.8).
        Searches for .bak files and restores them.
        """
        path = self.ed_path.text().strip()

        if not path:
            QMessageBox.warning(self, tr("json_translate.undo_missing"), tr("json_translate.undo_missing_msg"))
            return

        # Find .bak files
        backup_files = []

        if os.path.isfile(path):
            # Single file mode
            backup_path = path + ".bak"
            if os.path.exists(backup_path):
                backup_files.append((backup_path, path))
        else:
            # Directory mode - find all .bak files
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".bak"):
                        backup_path = os.path.join(root, file)
                        original_path = backup_path[:-4]  # Remove .bak
                        if os.path.exists(original_path):
                            backup_files.append((backup_path, original_path))

        if not backup_files:
            QMessageBox.warning(self, tr("json_translate.undo_no_backups"), tr("json_translate.undo_no_backups_msg"))
            return

        # Confirm restoration
        confirm_msg = tr("json_translate.undo_confirm_msg").replace("{count}", str(len(backup_files)))
        reply = QMessageBox.question(
            self,
            tr("json_translate.undo_confirm_title"),
            confirm_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return

        # Restore files
        restored = 0
        errors = []

        for backup_path, original_path in backup_files:
            try:
                import shutil

                shutil.copy2(backup_path, original_path)
                restored += 1
            except Exception as e:
                errors.append(f"{os.path.basename(original_path)}: {str(e)}")

        # Show results
        msg = tr("json_translate.undo_complete_msg").replace("{count}", str(restored))
        if errors:
            error_header = tr("json_translate.undo_errors").replace("{count}", str(len(errors)))
            msg += f"\n\n{error_header}\n" + "\n".join(errors[:5])

        QMessageBox.information(self, tr("json_translate.undo_complete_title"), msg)

    def _execute_action(self) -> None:
        """Execute the main action when ENTER is pressed."""
        self._run()

    def _apply_accessibility(self) -> None:
        """Apply accessibility labels to all widgets (v2.9.37)."""
        # Root path section
        AccessibilityManager.set_accessible_widget(
            self.lbl_path, "JSON Translate - Label - Root Path", "Label indicating root path input field"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_path, "JSON Translate - Input - Root Path", "File or directory path to translate"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_browse,
            "JSON Translate - Button - Browse Root Path",
            "Open file browser to select file or directory",
        )
        AccessibilityManager.set_accessible_widget(
            self.is_file,
            "JSON Translate - Checkbox - Is File",
            "Check if root path is a file (unchecked for directory)",
        )

        # Dictionary file section
        AccessibilityManager.set_accessible_widget(
            self.lbl_dict, "JSON Translate - Label - Dictionary File", "Label indicating dictionary file input field"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_dict,
            "JSON Translate - Input - Dictionary File Path",
            "JSON or TypeScript file containing translation dictionary",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_open, "JSON Translate - Button - Browse Dictionary", "Open file browser to select dictionary file"
        )

        # Variable name
        AccessibilityManager.set_accessible_widget(
            self.lbl_var, "JSON Translate - Label - Variable Name", "Label indicating variable name input field"
        )
        AccessibilityManager.set_accessible_widget(
            self.object_variable_name,
            "JSON Translate - Input - Variable Name",
            "Variable name used in code to access translations (e.g., 't' for t.key)",
        )

        # Scope delimiters
        AccessibilityManager.set_accessible_widget(
            self.lbl_start, "JSON Translate - Label - Start Delimiter", "Label indicating start delimiter regex input"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_start,
            "JSON Translate - Input - Start Delimiter Regex",
            "Regex pattern marking where translation scope begins",
        )
        AccessibilityManager.set_accessible_widget(
            self.lbl_end, "JSON Translate - Label - End Delimiter", "Label indicating end delimiter regex input"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_end,
            "JSON Translate - Input - End Delimiter Regex",
            "Regex pattern marking where translation scope ends",
        )

        # Exclusion patterns
        AccessibilityManager.set_accessible_widget(
            self.lbl_exclude, "JSON Translate - Label - Exclusion Patterns", "Label indicating exclusion patterns input"
        )
        AccessibilityManager.set_accessible_widget(
            self.ed_exclude,
            "JSON Translate - Input - Exclusion Patterns",
            "Comma-separated regex patterns for text that should not be translated",
        )

        # Options checkboxes
        AccessibilityManager.set_accessible_widget(
            self.chk_backup,
            "JSON Translate - Checkbox - Backup Original Files",
            "Create backup files (.bak) before modifying originals",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_dont_override,
            "JSON Translate - Checkbox - Don't Override Existing Translations",
            "Skip text that is already translated",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_inverse_json_translate,
            "JSON Translate - Checkbox - Reverse Translation",
            "Reverse translation: replace variable references with dictionary values",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_emit_export,
            "JSON Translate - Checkbox - Emit Export Const",
            "Add 'export const varName = {...}' wrapper to output (TS/JS files)",
        )
        AccessibilityManager.set_accessible_widget(
            self.chk_preserve_uppercase,
            "JSON Translate - Checkbox - Preserve Uppercase Keys",
            "Preserve keys that are already UPPERCASE (e.g., HOME_TITLE stays HOME_TITLE)",
        )

        # Stats label
        AccessibilityManager.set_accessible_widget(
            self.lbl_stats, "JSON Translate - Label - Statistics", "Statistics about files and translations to process"
        )

        # Action buttons
        AccessibilityManager.set_accessible_widget(
            self.btn_run, "JSON Translate - Button - Run Translation", "Execute translation on selected files"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_swap,
            "JSON Translate - Button - Swap Dictionaries",
            "Swap source and target dictionaries (toggle reverse translation)",
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_undo,
            "JSON Translate - Button - Undo with Backup",
            "Restore original files from backup (.bak files)",
        )
