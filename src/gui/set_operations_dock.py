"""
Set Operations Dock - GUI Interface (v2.9.32)

Provides GUI for JSON set operations with pipeline processing.

Design Patterns:
    - Controller (GRASP): Coordinates UI workflow
    - Observer (GoF): Qt signals for communication
    - Low Coupling (GRASP): Depends only on set_operations core logic

Author: Josué Amaral
Date: December 2, 2025
Version: 2.9.32
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=import-outside-toplevel  # Lazy imports for dialogs
# pylint: disable=broad-exception-caught  # GUI robustness
# pylint: disable=attribute-defined-outside-init  # Qt data pattern
# pylint: disable=line-too-long  # Long QFileDialog lines
# pylint: disable=unexpected-keyword-arg  # BatchDialog signature varies

import json
import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QFileDialog, QFrame, QHBoxLayout,
    QLabel, QPushButton, QScrollArea,
    QTextEdit, QVBoxLayout, QWidget
)

from src.accessibility_manager import AccessibilityManager
from src.core.result_exporter import ResultExporter
from src.core.set_operation_executor import SetOperationExecutor
from src.i18n.translator import tr, tooltip_tr
from src.utils.logger import get_logger

from ..history_manager import HistoryManager
from .base_dock import BaseDock
from .widgets import FileSelectionWidget, OperationOptionsWidget
from .history_dialog import HistoryDialog
from ..presets_manager import PresetsManager
from .presets_dialog import PresetsDialog

logger = get_logger(__name__)


class SetOperationsDock(BaseDock):
    """Dock widget for JSON set operations."""

    # Signal emitted when user wants to store result in Calculator (v2.9.98)
    store_in_calculator_requested = Signal(object, str)  # (data, source)

    def __init__(self, parent=None):
        """Initialize Set Operations dock.

        Args:
            parent: Parent widget (optional)
        """
        self.history_manager = HistoryManager()
        self.presets_manager = PresetsManager()
        super().__init__(tr("set_operations.title"), parent)

    def _setup_ui(self):
        """Setup user interface components."""
        # Create scroll area for all controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)  # No frame

        scroll_widget = QWidget()
        main_layout = QVBoxLayout(scroll_widget)

        # === File Selection Section ===
        self.file_selector = FileSelectionWidget(
            title="File Selection",
            file_filter=(
                "Supported Documents (*.json *.txt *.docx *.odt *.ipynb *.pdf);;"
                "JSON Files (*.json);;Text Documents (*.txt *.docx *.odt);;"
                "Notebooks (*.ipynb);;PDF Documents (*.pdf)"
            )
        )
        main_layout.addWidget(self.file_selector)

        # === Operation Options Section ===
        self.operation_options = OperationOptionsWidget()
        main_layout.addWidget(self.operation_options)

        # === Action Buttons ===
        btn_layout = QHBoxLayout()
        self.btn_execute = QPushButton(tr("set_operations.btn_execute"))
        self.btn_execute.setMinimumHeight(35)
        self.btn_execute.setToolTip(tooltip_tr("set_ops.btn_execute"))

        self.btn_save_preset = QPushButton(tr("set_operations.btn_save_preset"))
        self.btn_save_preset.setToolTip(tooltip_tr("set_operations.tooltip_save_preset"))

        self.btn_clear = QPushButton(tr("set_operations.btn_clear"))
        self.btn_clear.setToolTip(tooltip_tr("set_operations.tooltip_clear"))
        self.btn_save = QPushButton(tr("set_operations.btn_save"))
        self.btn_save.setToolTip(tooltip_tr("set_operations.tooltip_save_results"))
        self.btn_save.setEnabled(False)
        self.btn_export = QPushButton(tr("set_operations.btn_export"))
        self.btn_export.setToolTip(tooltip_tr("set_operations.tooltip_export"))
        self.btn_export.setEnabled(False)

        self.btn_view_diff = QPushButton(tr("set_operations.btn_view_diff"))
        self.btn_view_diff.setToolTip(tooltip_tr("set_operations.tooltip_view_diff"))
        self.btn_view_diff.setEnabled(False)

        self.btn_view_venn = QPushButton(tr("set_operations.btn_view_venn"))
        self.btn_view_venn.setToolTip(tooltip_tr("set_operations.tooltip_view_venn"))
        self.btn_view_venn.setEnabled(False)

        self.btn_merge = QPushButton(tr("set_operations.btn_merge"))
        self.btn_merge.setToolTip(tooltip_tr("set_operations.tooltip_merge"))
        self.btn_merge.setEnabled(False)

        self.btn_store_calc = QPushButton(tr("set_operations.btn_store_calc"))
        self.btn_store_calc.setToolTip(tooltip_tr("set_operations.tooltip_store_calc"))
        self.btn_store_calc.setEnabled(False)

        self.btn_batch = QPushButton(tr("set_operations.btn_batch"))
        self.btn_batch.setToolTip(tooltip_tr("set_operations.tooltip_batch"))

        self.btn_history = QPushButton(tr("set_operations.btn_history"))
        self.btn_history.setToolTip(tooltip_tr("set_operations.tooltip_history"))

        self.btn_presets = QPushButton(tr("set_operations.btn_presets"))
        self.btn_presets.setToolTip(tooltip_tr("set_operations.tooltip_presets"))

        btn_layout.addWidget(self.btn_execute)
        btn_layout.addWidget(self.btn_save_preset)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_view_diff)
        btn_layout.addWidget(self.btn_view_venn)
        btn_layout.addWidget(self.btn_merge)
        btn_layout.addWidget(self.btn_store_calc)
        btn_layout.addWidget(self.btn_batch)
        btn_layout.addWidget(self.btn_history)
        btn_layout.addWidget(self.btn_presets)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        # === Results Section ===
        main_layout.addWidget(QLabel(tr("set_operations.lbl_results")))
        self.txt_result = QTextEdit()
        self.txt_result.setReadOnly(True)
        self.txt_result.setMinimumHeight(200)
        main_layout.addWidget(self.txt_result)

        # === Statistics Section ===
        self.lbl_stats = QLabel("")
        self.lbl_stats.setWordWrap(True)
        self.lbl_stats.setStyleSheet("color: #6A9955; font-weight: bold;")
        main_layout.addWidget(self.lbl_stats)

        # === Comparative Statistics Dashboard (v2.9.96) ===
        self.txt_statistics = QTextEdit()
        self.txt_statistics.setReadOnly(True)
        self.txt_statistics.setMaximumHeight(300)
        self.txt_statistics.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10pt;")
        self.txt_statistics.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.txt_statistics)

        main_layout.addStretch()

        # Set scroll widget and add to main layout
        scroll.setWidget(scroll_widget)
        self.layout.addWidget(scroll)

    def _connect_signals(self):
        """Connect UI signals to slots."""
        # File selection widget signals (handled internally)
        # No need to connect file selection signals manually

        self.btn_execute.clicked.connect(self._execute)
        self.btn_save_preset.clicked.connect(self._save_current_as_preset)
        self.btn_clear.clicked.connect(self._clear_all)
        self.btn_save.clicked.connect(self._save_result)
        self.btn_export.clicked.connect(self._export_result)
        self.btn_view_diff.clicked.connect(self._view_diff)
        self.btn_view_venn.clicked.connect(self._view_venn)
        self.btn_merge.clicked.connect(self._merge_to_file)
        self.btn_store_calc.clicked.connect(self._store_in_calculator)
        self.btn_batch.clicked.connect(self._show_batch_dialog)
        self.btn_history.clicked.connect(self._show_history)
        self.btn_presets.clicked.connect(self._show_presets)

        # Apply accessibility labels (v2.9.104)
        self._apply_accessibility()

    def _apply_accessibility(self):
        """Apply accessibility labels to widgets (v2.9.104)."""
        # File selection and operation options accessibility are handled by their widgets

        # Action buttons
        AccessibilityManager.set_accessible_widget(
            self.btn_execute, "Set Operations - Button - Execute",
            "Execute selected operations on files (Ctrl+Enter)"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_save, "Set Operations - Button - Save Result",
            "Save result to JSON file"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_store_calc, "Set Operations - Button - Store in Calculator",
            "Store result in Calculator memory slot"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_batch, "Set Operations - Button - Batch Operations",
            "Open Batch Operations dialog for pipeline workflows (v2.9.102)"
        )
        AccessibilityManager.set_accessible_widget(
            self.btn_history, "Set Operations - Button - History",
            "View execution history with re-run capability"
        )

    def _execute(self):
        """Execute set operations."""
        files = self.file_selector.get_files()
        operations = self.operation_options.get_selected_operations()

        # Validate and load files
        success, file_dicts, error = SetOperationExecutor.validate_and_load_files(files)
        if not success:
            self.show_error(tr("set_operations.error_title"), error)
            return

        # Execute operations
        comparison_mode = self.operation_options.get_comparison_mode()
        options = self.operation_options.get_options()

        exec_result = SetOperationExecutor.execute_operations(
            file_dicts, operations, comparison_mode, options
        )

        if not exec_result.success:
            self.show_error(tr("set_operations.error_title"), exec_result.error)
            return

        # Store data for diff viewer and other features
        self.file_a_data = exec_result.file_a_data
        self.file_b_data = exec_result.file_b_data
        self.result_data = exec_result.results

        # Display results
        output_text = SetOperationExecutor.format_results_json(exec_result.results)
        self.txt_result.setText(output_text)

        # Display statistics
        self.lbl_stats.setText("\n".join(exec_result.stats_lines))

        # Save to history (v2.9.94)
        try:
            operation_type = operations[0] if operations else "∩"
            result_count = SetOperationExecutor.calculate_result_count(exec_result.results)

            # Convert comparison mode for history storage
            history_comparison_mode = comparison_mode
            if comparison_mode == "full_path":
                history_comparison_mode = "full_path_value"

            if files and len(files) > 0:
                self.history_manager.add_operation(
                    operation_type=operation_type,
                    file1=files[0],
                    file2=files[1] if len(files) > 1 else files[0],
                    comparison_mode=history_comparison_mode,
                    result_count=result_count,
                    result_data=exec_result.results
                )
        except Exception as e:
            logger.warning(f"Failed to save operation to history: {e}")

        # Calculate comparative statistics (v2.9.96)
        try:
            from ..statistics_manager import StatisticsManager

            # Calculate stats for each file
            if file_dicts and len(file_dicts) > 0:
                file1_stats = StatisticsManager.calculate_statistics(file_dicts[0])
                file2_stats = StatisticsManager.calculate_statistics(file_dicts[1] if len(file_dicts) > 1 else file_dicts[0])

            # Calculate stats for result
            result_count = SetOperationExecutor.calculate_result_count(exec_result.results)
            result_stats = StatisticsManager.calculate_statistics(exec_result.results)

            # Calculate overlap percentage
            overlap_pct = StatisticsManager.calculate_overlap_percentage(file1_stats, file2_stats, result_count)

            # Format comparative statistics
            stats_text = StatisticsManager.format_comparative_statistics(
                file1_stats, file2_stats, result_stats, overlap_pct
            )

            # Display in statistics area
            self.txt_statistics.setText(stats_text)
            self.txt_statistics.setVisible(True)

        except Exception as e:
            logger.warning(f"Failed to calculate statistics: {e}")
            self.txt_statistics.setVisible(False)

        # Enable save, export, diff viewer, venn diagram, merge, and calculator buttons
        self.btn_save.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.btn_view_diff.setEnabled(True)
        self.btn_view_venn.setEnabled(True)
        self.btn_merge.setEnabled(True)
        self.btn_store_calc.setEnabled(True)

        self.show_info(tr("set_operations.success_title"), tr("set_operations.success_message").replace("{stats}", stats_text if 'stats_text' in locals() else 'Statistics calculated successfully.'))

    def _save_result(self):
        """Save operation results to JSON file."""
        data = self.txt_result.toPlainText()
        if not data:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "JSON Files (*.json)"
        )

        if file_path:
            success, message = ResultExporter.save_json(data, file_path)
            if success:
                self.show_info(tr("set_operations.success_title"), message)
            else:
                self.show_error(tr("set_operations.error_saving_title"), message)

    def _export_result(self):
        """Export results to multiple formats (v2.9.93)."""
        # Validate data
        is_valid, error = ResultExporter.validate_export_data(
            self.result_data if hasattr(self, 'result_data') else None
        )
        if not is_valid:
            self.show_warning(tr("set_operations.warning_no_data_title"), error)
            return

        # Open save dialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "",
            ResultExporter.FORMAT_FILTER
        )

        if not file_path:
            return  # User cancelled

        # Export
        success, message = ResultExporter.export_multi_format(
            self.result_data, file_path, selected_filter, parent_widget=self
        )

        if success:
            self.show_info("Export Successful", message)
        else:
            self.show_error("Export Failed", message)

    def _store_in_calculator(self):
        """Store result in Calculator memory slot (v2.9.98)."""
        if not hasattr(self, 'result_data') or not self.result_data:
            self.show_warning("No Data", "No results to store. Please execute an operation first.")
            return

        # Determine operation source description
        operations = self.operation_options.get_selected_operations()
        operation_names = {
            '∩': 'Intersection (∩)',
            '∪': 'Union (∪)',
            '−': 'Difference (−)',
            '⊕': 'Symmetric Difference (⊕)'
        }
        operation = operation_names.get(operations[0], "Unknown") if operations else "Unknown"

        # Get file names for source description
        files = self.file_selector.get_files()
        file_a = os.path.basename(files[0]) if files and len(files) > 0 else "File A"
        file_b = os.path.basename(files[1]) if files and len(files) > 1 else "File B"

        source = f"Set Operations: {operation} ({file_a}, {file_b})"

        # Emit signal for Calculator to handle
        self.store_in_calculator_requested.emit(self.result_data, source)

        self.show_info("Stored", f"Result sent to Calculator\nSource: {source}")

    def _view_diff(self):
        """Open diff viewer dialog for side-by-side comparison (v2.9.99)."""
        if not hasattr(self, 'file_a_data') or not hasattr(self, 'file_b_data'):
            self.show_warning("No Data", "No input files to compare. Execute operation first.")
            return

        from .diff_viewer_dialog import DiffViewerDialog

        # Get file names
        files = self.file_selector.get_files()
        file_a_name = os.path.basename(files[0]) if files else "File A"
        file_b_name = os.path.basename(files[1]) if len(files) > 1 else "File B"

        # Get current comparison mode
        comparison_mode = self.operation_options.get_comparison_mode()
        if comparison_mode == "full_path":
            comparison_mode = "full_path_value"  # Adapt for dialog

        dialog = DiffViewerDialog(
            self.file_a_data,
            self.file_b_data,
            file_a_name,
            file_b_name,
            comparison_mode,
            self
        )
        dialog.exec()

    def _view_venn(self):
        """Open Venn diagram viewer for interactive visualization (v2.9.107)."""
        if not hasattr(self, 'file_a_data') or not hasattr(self, 'file_b_data'):
            self.show_warning("No Data", "No input files to compare. Execute operation first.")
            return

        from .venn_diagram_dialog import VennDiagramDialog

        # Get file names
        files = self.file_selector.get_files()
        file_a_name = os.path.basename(files[0]) if files and len(files) > 0 else "File A"
        file_b_name = os.path.basename(files[1]) if files and len(files) > 1 else "File B"

        # Get current comparison mode
        comparison_mode = self.operation_options.get_comparison_mode()
        if comparison_mode == "full_path":
            comparison_mode = "full_path_value"  # Adapt for dialog

        dialog = VennDiagramDialog(
            self.file_a_data,
            self.file_b_data,
            file_a_name,
            file_b_name,
            comparison_mode,
            self
        )
        dialog.exec()

    def _merge_to_file(self):
        """Merge results back to original file (v2.9.100)."""
        if not hasattr(self, 'result_data') or not self.result_data:
            self.show_warning("No Data", "No results to merge. Execute operation first.")
            return

        # Get file A path (default merge target)
        files = self.file_selector.get_files()
        file_a_path = files[0] if files else ""
        if not file_a_path or not os.path.exists(file_a_path):
            self.show_warning("No File", "No valid file selected to merge into.")
            return

        from .merge_config_dialog import MergeConfigDialog
        from .merge_preview_dialog import MergePreviewDialog
        from ..merge_manager import MergeManager

        # Step 1: Configure merge
        config_dialog = MergeConfigDialog(file_a_path, self)
        if config_dialog.exec() != QDialog.Accepted:
            return

        mode, file_path, auto_backup, max_backups = config_dialog.get_config()

        # Step 2: Simulate merge and show preview
        merge_manager = MergeManager(max_backups=max_backups, auto_backup=auto_backup)

        success, merged_data, message = merge_manager.simulate_merge(
            file_path, self.result_data, mode
        )

        if not success:
            self.show_error("Simulation Error", message)
            return

        # Load original data for preview
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
        except Exception as e:
            self.show_error("Load Error", f"Failed to load original file:\n{e}")
            return

        # Show preview dialog
        preview_dialog = MergePreviewDialog(
            original_data,
            self.result_data,
            merged_data,
            mode,
            file_path,
            self
        )

        if preview_dialog.exec() != QDialog.Accepted or not preview_dialog.is_approved():
            return

        # Step 3: Apply merge
        success, message, _ = merge_manager.merge_to_file(
            file_path, self.result_data, mode, backup=auto_backup
        )

        if success:
            self.show_info("Merge Complete", message)
        else:
            self.show_error("Merge Error", message)


    def _clear_all(self):
        """Clear all inputs and results."""
        self.file_selector.clear()
        self.operation_options.clear()
        self.txt_result.clear()
        self.lbl_stats.clear()
        self.txt_statistics.clear()
        self.txt_statistics.setVisible(False)
        self.btn_save.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.btn_view_diff.setEnabled(False)
        self.btn_view_venn.setEnabled(False)
        self.btn_merge.setEnabled(False)
        self.btn_store_calc.setEnabled(False)

    def _show_history(self):
        """Show operation history dialog (v2.9.94)."""
        dialog = HistoryDialog(self.history_manager, self)

        # Connect re-execute signal
        dialog.re_execute_requested.connect(self._re_execute_from_history)

        dialog.exec()

    def _re_execute_from_history(self, entry: dict):
        """
        Re-execute operation from history.

        Args:
            entry: History entry with operation data
        """
        try:
            # Set files
            files = [entry["file1"], entry["file2"]]
            self.file_selector.set_files(files)

            # Set configuration using operation_options widget
            config = {
                'operations': [entry["operation_type"]],
                'comparison_mode': entry["comparison_mode"].replace('_value', ''),  # Convert full_path_value -> full_path
                'options': {},
                'output_format': 'nested'
            }
            self.operation_options.set_configuration(config)

            # Execute
            self._execute()

        except Exception as e:
            self.show_error(
                "Re-execute Error",
                f"Failed to re-execute operation:\n{e}"
            )

    def _show_presets(self):
        """Show operation presets dialog (v2.9.95)."""
        dialog = PresetsDialog(self.presets_manager, self)

        # Connect preset load signal
        dialog.preset_load_requested.connect(self._load_preset)

        dialog.exec()

    def _load_preset(self, preset: dict):
        """
        Load preset into current configuration.

        Args:
            preset: Preset data dictionary
        """
        try:
            # Create configuration dictionary for operation_options
            config = {
                'operations': [preset.get('operation_type', '∩')],
                'comparison_mode': preset.get('comparison_mode', 'key_value').replace('_value', ''),
                'options': {
                    'ignore_case_keys': preset.get('ignore_case_keys', False),
                    'ignore_case_values': preset.get('ignore_case_values', False),
                    'skip_empty': preset.get('skip_empty', True),
                    'arrays_ignore_order': preset.get('arrays_ignore_order', False)
                },
                'output_format': 'nested'
            }

            # Load configuration into widget
            self.operation_options.set_configuration(config)

            # Load favorite files if any
            favorite_files = preset.get("favorite_files", [])
            if favorite_files:
                self.file_selector.set_files(favorite_files)

            self.show_info("Preset Loaded", f"Loaded preset: {preset.get('name', 'Unnamed')}")

        except Exception as e:
            self.show_error("Load Preset Error", f"Failed to load preset:\n{e}")

    def _save_current_as_preset(self):
        """Save current configuration as a new preset."""
        from PySide6.QtWidgets import QInputDialog

        # Solicita nome do preset
        name, ok = QInputDialog.getText(
            self,
            "Save Preset",
            "Enter preset name:"
        )

        if not ok or not name.strip():
            return

        name = name.strip()

        # Verifica se nome já existe
        if self.presets_manager.get_preset(name):
            from PySide6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Preset Exists",
                f"A preset named '{name}' already exists.\nOverwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        try:
            # Get configuration from widgets
            operations = self.operation_options.get_selected_operations()
            operation_type = operations[0] if operations else "∩"

            comparison_mode = self.operation_options.get_comparison_mode()
            if comparison_mode == "full_path":
                comparison_mode = "full_path_value"  # Convert for storage

            options = self.operation_options.get_options()

            # Coleta arquivos atuais (favorite files)
            favorite_files = self.file_selector.get_files()

            # Cria preset
            preset = self.presets_manager.create_preset_from_current(
                name=name,
                operation_type=operation_type,
                comparison_mode=comparison_mode,
                ignore_case_keys=options['ignore_case_keys'],
                ignore_case_values=options['ignore_case_values'],
                skip_empty=options['skip_empty'],
                arrays_ignore_order=options['arrays_ignore_order'],
                favorite_files=favorite_files
            )

            # Salva
            success = self.presets_manager.save_preset(preset)

            if success:
                self.show_info("Preset Saved", f"Preset '{name}' saved successfully!")
            else:
                self.show_error("Save Error", "Failed to save preset.")

        except Exception as e:
            self.show_error("Save Preset Error", f"Failed to save preset:\n{e}")

    def receive_calculator_data(self, data: dict, source_description: str):
        """
        Receive data from Calculator Memory and populate File A.

        Integration method for v2.9.101 Calculator + Set Operations.

        Args:
            data: JSON data from Calculator Memory slot
            source_description: Source description (e.g., "Calculator Memory Slot A")
        """
        try:
            # Save data to temporary file
            import tempfile

            # Create temp file with descriptive name
            temp_dir = tempfile.gettempdir()
            temp_filename = f"calculator_slot_data_{source_description.split()[-1]}.json"
            temp_path = os.path.join(temp_dir, temp_filename)

            # Write data to temp file
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Populate File A with temp file path
            self.ed_file_a.setText(temp_path)
            self.file_a_path = temp_path

            # Show success message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                tr("set_operations.msg_data_received_title"),
                tr("set_operations.msg_data_received").format(
                    source=source_description,
                    path=temp_path
                )
            )

        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                tr("set_operations.msg_integration_error_title"),
                tr("set_operations.msg_integration_error").format(error=str(e))
            )

    def _show_batch_dialog(self):
        """Show batch operations dialog (v2.9.102)."""
        from .batch_dialog import BatchDialog

        # Get default files if set
        default_files = {}
        if self.ed_file_a.text():
            default_files['a'] = self.ed_file_a.text()
        if self.ed_file_b.text():
            default_files['b'] = self.ed_file_b.text()

        dialog = BatchDialog(self, default_files=default_files if default_files else None)
        dialog.exec()
