"""
Case Converter Dock Widget

Provides UI for converting text case styles between camelCase, PascalCase,
snake_case, and kebab-case.
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy Qt imports
# pylint: disable=broad-exception-caught  # GUI robustness

import os

from PySide6.QtWidgets import QGridLayout, QLabel, QComboBox, QLineEdit, QHBoxLayout

from src.case_converter import convert_file
from src.i18n.translator import tr, tooltip_tr

from .base_dock import StandardToolDock, ProcessorWorkerBase


class CaseConverterWorker(ProcessorWorkerBase):
    """Background worker for case conversion."""

    def __init__(self, files, target_style, source_style=None):
        super().__init__()
        self.files = files
        self.target_style = target_style
        self.source_style = source_style

    def run(self):
        """Execute case conversion on all files."""
        try:
            total = len(self.files)
            results = {}

            for i, file_path in enumerate(self.files):
                if self.check_interrupt():
                    self.emit_progress("⚠️ Processing interrupted")
                    break

                self.emit_progress(f"[{i+1}/{total}] Processing {os.path.basename(file_path)}...")

                try:
                    # Use convert_file to convert in-place
                    convert_file(file_path, file_path, self.target_style, output_format='js')

                    # Read to count conversions (simple heuristic)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Estimate number of keys converted (count of colons in objects)
                    count = content.count(':')

                    results[file_path] = count
                    self.emit_progress(f"✓ Converted {os.path.basename(file_path)}")

                except Exception as e:
                    self.emit_progress(f"✗ Error in {os.path.basename(file_path)}: {str(e)}")

            self.emit_success(results)

        except Exception as e:
            self.emit_error(str(e))


class CaseConverterDock(StandardToolDock):
    """Dock widget for case conversion tool."""

    def __init__(self, parent=None):
        super().__init__(tr("case_converter.title"), parent)
        self.worker = None

    def _setup_ui(self):
        """Setup UI components."""
        grid = QGridLayout()

        # Source case style
        grid.addWidget(QLabel(tr("case_converter.lbl_source")), 0, 0)
        self.combo_source = QComboBox()
        self.combo_source.addItems([
            tr("case_converter.option_auto"),
            tr("case_converter.option_camel"),
            tr("case_converter.option_pascal"),
            tr("case_converter.option_snake"),
            tr("case_converter.option_kebab")
        ])
        self.combo_source.setToolTip(tooltip_tr("case.combo_source"))
        grid.addWidget(self.combo_source, 0, 1, 1, 3)

        # Target case style
        grid.addWidget(QLabel(tr("case_converter.lbl_target")), 1, 0)
        self.combo_target = QComboBox()
        self.combo_target.addItems([
            tr("case_converter.option_camel"),
            tr("case_converter.option_pascal"),
            tr("case_converter.option_snake"),
            tr("case_converter.option_kebab")
        ])
        self.combo_target.setToolTip(tooltip_tr("case.combo_target"))
        grid.addWidget(self.combo_target, 1, 1, 1, 3)

        # File/directory input
        lbl, self.ed_path, self.btn_browse, self.chk_is_file = self.create_file_input(
            "Input path:",
            "File or directory to process"
        )
        self.ed_path.setToolTip(tooltip_tr("case.ed_path"))
        grid.addWidget(lbl, 2, 0)
        grid.addWidget(self.ed_path, 2, 1, 1, 2)
        self.btn_browse.setToolTip(tooltip_tr("case.btn_browse"))
        grid.addWidget(self.btn_browse, 2, 3)
        self.chk_is_file.setToolTip(tooltip_tr("case.chk_is_file"))
        grid.addWidget(self.chk_is_file, 3, 0, 1, 2)

        # Extensions filter
        grid.addWidget(QLabel(tr("case_converter.lbl_extensions")), 3, 2)
        self.ed_extensions = QLineEdit()
        self.ed_extensions.setText(tr("case_converter.default_extensions"))
        self.ed_extensions.setPlaceholderText(tr("case_converter.placeholder_extensions"))
        self.ed_extensions.setToolTip(tooltip_tr("case.ed_extensions"))
        grid.addWidget(self.ed_extensions, 3, 3)

        self.layout.addLayout(grid)

        # Action buttons
        buttons = [
            ("Convert", self._convert),
            ("Interrupt", self._interrupt),
            ("Clear", self._clear)
        ]
        btn_layout = self.create_action_buttons(buttons)
        self.btn_convert.setToolTip(tr("case_converter.tooltip_convert"))
        self.btn_interrupt.setToolTip(tr("case_converter.tooltip_interrupt"))
        self.btn_clear.setToolTip(tr("case_converter.tooltip_clear"))
        self.btn_interrupt.setEnabled(False)
        self.layout.addLayout(btn_layout)

        # Results panel
        lbl_results, self.text_results = self.create_results_panel()
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.text_results)

        # Open in Editor button (Task #6 - v2.9.19)
        editor_btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(self.text_results, editor_btn_layout)
        self.layout.addLayout(editor_btn_layout)

    def _connect_signals(self):
        """Connect signals."""
        self.btn_browse.clicked.connect(self._browse)
        self._setup_enter_key_execution(self.ed_path, self.ed_extensions)
        self._setup_escape_key_interrupt()

    def _setup_escape_key_interrupt(self):
        """Setup Esc key to interrupt case conversion (v2.9.50.1)."""
        # pylint: disable=reimported,redefined-outer-name  # Lazy import for Qt
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QShortcut, QKeySequence

        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        shortcut.activated.connect(self._interrupt)

    def _browse(self):
        """Browse for file or directory."""
        self.browse_file_or_directory(
            self.ed_path,
            self.chk_is_file.isChecked(),
            tr("case_converter.browse_filter")
        )

    def _get_files(self):
        """Get list of files to process."""
        path = self.ed_path.text().strip()
        valid, error = self.validate_file_path(path)
        if not valid:
            raise ValueError(error)

        if self.chk_is_file.isChecked():
            if not os.path.isfile(path):
                raise ValueError(f"Not a file: {path}")
            return [path]
        else:
            if not os.path.isdir(path):
                raise ValueError(f"Not a directory: {path}")

            # Get extensions
            ext_text = self.ed_extensions.text().strip()
            extensions = [e.strip() for e in ext_text.split(',') if e.strip()] if ext_text else []

            # List files recursively
            files = []
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    if not extensions or any(filename.endswith(ext) for ext in extensions):
                        files.append(os.path.join(root, filename))

            if not files:
                raise ValueError(f"No matching files found in {path}")
            return files

    def _convert(self):
        """Start conversion process."""
        try:
            # Validate inputs
            files = self._get_files()

            # Get styles (use string-based style names)
            source_text = self.combo_source.currentText()
            target_text = self.combo_target.currentText()

            # Map UI text to case_converter style strings
            style_map = {
                "camelCase": "camel",
                "PascalCase": "pascal",
                "snake_case": "snake",
                "kebab-case": "kebab"
            }

            source_style = None if source_text == "Auto-detect" else style_map.get(source_text, "snake")
            target_style = style_map.get(target_text, "snake")

            # Start worker
            self.worker = CaseConverterWorker(files, target_style, source_style)
            self.worker.progress.connect(lambda msg: self.append_result(self.text_results, msg))
            self.worker.finished_ok.connect(self._on_finished)
            self.worker.failed.connect(self._on_failed)

            self.btn_convert.setEnabled(False)
            self.btn_interrupt.setEnabled(True)
            self.clear_results(self.text_results)
            self.append_result(self.text_results, f"Processing {len(files)} file(s)...\n")

            self.worker.start()

        except Exception as e:
            self.show_error(tr("case_converter.error_title"), str(e))

    def _interrupt(self):
        """Interrupt processing."""
        if self.worker and self.worker.isRunning():
            self.worker.request_interrupt()
            self.append_result(self.text_results, "\n⚠️ Interrupt requested...")

    def _on_finished(self, results):
        """Handle successful completion."""
        total_converted = sum(results.values())
        self.append_result(
            self.text_results,
            f"\n✅ Conversion complete! {total_converted} words converted in {len(results)} file(s)."
        )
        self.btn_convert.setEnabled(True)
        self.btn_interrupt.setEnabled(False)
        self.notify_processing_completed()

    def _on_failed(self, error):
        """Handle processing failure."""
        self.append_result(self.text_results, f"\n❌ Error: {error}")
        self.btn_convert.setEnabled(True)
        self.btn_interrupt.setEnabled(False)

    def _clear(self):
        """Clear results."""
        self.clear_results(self.text_results)

    def _execute_action(self):
        """Execute the main action when ENTER is pressed."""
        self._convert()
