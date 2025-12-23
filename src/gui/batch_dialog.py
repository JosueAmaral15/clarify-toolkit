"""
Batch Dialog for Set Operations
GUI for creating, managing and executing batch jobs.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.102
"""

from typing import Optional
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QGroupBox, QLineEdit, QComboBox, QCheckBox,
                                QFileDialog, QMessageBox, QHeaderView, QTextEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from ..batch_manager import BatchJob, BatchStep, BatchExecutor, BatchHistory
import os


class BatchStepEditorDialog(QDialog):
    """Dialog for adding/editing a batch step."""
    
    def __init__(self, step: Optional[BatchStep] = None, is_first_step: bool = True, parent=None):
        """
        Initialize BatchStepEditorDialog.
        
        Args:
            step: Existing step to edit (None for new step)
            is_first_step: Whether this is the first step in batch (affects file_a_source options)
            parent: Parent widget
        """
        super().__init__(parent)
        self.step = step
        self.is_first_step = is_first_step
        self.edited_step = None
        
        self.setWindowTitle("Add Batch Step" if step is None else "Edit Batch Step")
        self.resize(600, 400)
        
        self._init_ui()
        
        # Populate if editing
        if self.step:
            self._populate_from_step()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.ed_description = QLineEdit()
        self.ed_description.setPlaceholderText("Optional step description")
        desc_layout.addWidget(self.ed_description)
        layout.addLayout(desc_layout)
        
        # File A source
        file_a_group = QGroupBox("File A Source")
        file_a_layout = QVBoxLayout()
        
        self.radio_file_a_file = QCheckBox("From File Path")
        self.radio_file_a_previous = QCheckBox("From Previous Result")
        
        if self.is_first_step:
            self.radio_file_a_file.setChecked(True)
            self.radio_file_a_previous.setEnabled(False)
            self.radio_file_a_previous.setToolTip("Not available for first step")
        else:
            self.radio_file_a_previous.setChecked(True)
        
        file_a_layout.addWidget(self.radio_file_a_file)
        file_a_layout.addWidget(self.radio_file_a_previous)
        
        # File A path (if from file)
        path_a_layout = QHBoxLayout()
        self.ed_file_a = QLineEdit()
        self.ed_file_a.setPlaceholderText("Path to File A (if from file)")
        self.ed_file_a.setEnabled(self.radio_file_a_file.isChecked())
        self.btn_browse_a = QPushButton("Browse...")
        self.btn_browse_a.clicked.connect(lambda: self._browse_file('a'))
        self.btn_browse_a.setEnabled(self.radio_file_a_file.isChecked())
        path_a_layout.addWidget(self.ed_file_a)
        path_a_layout.addWidget(self.btn_browse_a)
        file_a_layout.addLayout(path_a_layout)
        
        file_a_group.setLayout(file_a_layout)
        layout.addWidget(file_a_group)
        
        # Connect radio buttons
        self.radio_file_a_file.stateChanged.connect(self._on_file_a_source_changed)
        self.radio_file_a_previous.stateChanged.connect(self._on_file_a_source_changed)
        
        # Operation
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel("Operation:"))
        self.combo_operation = QComboBox()
        self.combo_operation.addItems(['Intersection (∩)', 'Union (∪)', 'Difference (−)', 'Symmetric Difference (⊕)'])
        op_layout.addWidget(self.combo_operation)
        layout.addLayout(op_layout)
        
        # File B
        file_b_layout = QHBoxLayout()
        file_b_layout.addWidget(QLabel("File B:"))
        self.ed_file_b = QLineEdit()
        self.ed_file_b.setPlaceholderText("Path to File B")
        self.btn_browse_b = QPushButton("Browse...")
        self.btn_browse_b.clicked.connect(lambda: self._browse_file('b'))
        file_b_layout.addWidget(self.ed_file_b)
        file_b_layout.addWidget(self.btn_browse_b)
        layout.addLayout(file_b_layout)
        
        # Comparison mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Comparison Mode:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(['Key + Value', 'Full Path + Value', 'Key Only'])
        mode_layout.addWidget(self.combo_mode)
        layout.addLayout(mode_layout)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.chk_ignore_case_keys = QCheckBox("Ignore case in keys")
        self.chk_ignore_case_values = QCheckBox("Ignore case in values")
        self.chk_skip_empty = QCheckBox("Skip empty values")
        self.chk_arrays_ignore_order = QCheckBox("Arrays ignore order")
        
        options_layout.addWidget(self.chk_ignore_case_keys)
        options_layout.addWidget(self.chk_ignore_case_values)
        options_layout.addWidget(self.chk_skip_empty)
        options_layout.addWidget(self.chk_arrays_ignore_order)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self._on_ok)
        btn_layout.addWidget(self.btn_ok)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _on_file_a_source_changed(self):
        """Handle File A source change."""
        use_file = self.radio_file_a_file.isChecked()
        self.ed_file_a.setEnabled(use_file)
        self.btn_browse_a.setEnabled(use_file)
        
        # Ensure mutual exclusion
        if self.sender() == self.radio_file_a_file and use_file:
            self.radio_file_a_previous.setChecked(False)
        elif self.sender() == self.radio_file_a_previous and self.radio_file_a_previous.isChecked():
            self.radio_file_a_file.setChecked(False)
    
    def _browse_file(self, target: str):
        """Browse for JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select File {target.upper()}",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if target == 'a':
                self.ed_file_a.setText(file_path)
            else:
                self.ed_file_b.setText(file_path)
    
    def _populate_from_step(self):
        """Populate fields from existing step."""
        self.ed_description.setText(self.step.description)
        
        # File A source
        if self.step.file_a_source == 'file_path':
            self.radio_file_a_file.setChecked(True)
            self.radio_file_a_previous.setChecked(False)
            self.ed_file_a.setText(self.step.file_a_path)
        else:
            self.radio_file_a_previous.setChecked(True)
            self.radio_file_a_file.setChecked(False)
        
        # Operation
        op_map = {
            'intersection': 0,
            'union': 1,
            'difference': 2,
            'symmetric_difference': 3
        }
        self.combo_operation.setCurrentIndex(op_map.get(self.step.operation, 0))
        
        # File B
        self.ed_file_b.setText(self.step.file_b_path)
        
        # Comparison mode
        mode_map = {
            'key_value': 0,
            'full_path_value': 1,
            'key_only': 2
        }
        self.combo_mode.setCurrentIndex(mode_map.get(self.step.comparison_mode, 0))
        
        # Options
        opts = self.step.options
        self.chk_ignore_case_keys.setChecked(opts.get('ignore_case_keys', False))
        self.chk_ignore_case_values.setChecked(opts.get('ignore_case_values', False))
        self.chk_skip_empty.setChecked(opts.get('skip_empty', False))
        self.chk_arrays_ignore_order.setChecked(opts.get('arrays_ignore_order', False))
    
    def _on_ok(self):
        """Validate and create step."""
        # Validate File A
        file_a_source = 'file_path' if self.radio_file_a_file.isChecked() else 'previous_result'
        file_a_path = self.ed_file_a.text().strip()
        
        if file_a_source == 'file_path' and not file_a_path:
            QMessageBox.warning(self, "Validation Error", "Please select File A")
            return
        
        if file_a_source == 'file_path' and not os.path.exists(file_a_path):
            QMessageBox.warning(self, "Validation Error", f"File A not found: {file_a_path}")
            return
        
        # Validate File B
        file_b_path = self.ed_file_b.text().strip()
        if not file_b_path:
            QMessageBox.warning(self, "Validation Error", "Please select File B")
            return
        
        if not os.path.exists(file_b_path):
            QMessageBox.warning(self, "Validation Error", f"File B not found: {file_b_path}")
            return
        
        # Get operation
        op_map = ['intersection', 'union', 'difference', 'symmetric_difference']
        operation = op_map[self.combo_operation.currentIndex()]
        
        # Get comparison mode
        mode_map = ['key_value', 'full_path_value', 'key_only']
        comparison_mode = mode_map[self.combo_mode.currentIndex()]
        
        # Get options
        options = {
            'ignore_case_keys': self.chk_ignore_case_keys.isChecked(),
            'ignore_case_values': self.chk_ignore_case_values.isChecked(),
            'skip_empty': self.chk_skip_empty.isChecked(),
            'arrays_ignore_order': self.chk_arrays_ignore_order.isChecked()
        }
        
        # Create step
        self.edited_step = BatchStep(
            operation=operation,
            file_a_source=file_a_source,
            file_a_path=file_a_path if file_a_source == 'file_path' else "",
            file_b_path=file_b_path,
            comparison_mode=comparison_mode,
            options=options,
            description=self.ed_description.text().strip()
        )
        
        self.accept()
    
    def get_step(self) -> Optional[BatchStep]:
        """Get edited step."""
        return self.edited_step


class BatchDialog(QDialog):
    """
    Main dialog for batch operations management.
    
    Features:
    - Add/Remove/Edit steps in batch
    - Save/Load batch jobs to/from JSON
    - Execute batch with progress tracking
    - Save intermediate results (optional)
    """
    
    # Signal emitted when batch completes with final result
    batch_result_ready = Signal(object)  # Emits final result data
    
    def __init__(self, parent=None):
        """Initialize BatchDialog."""
        super().__init__(parent)
        self.batch_job = BatchJob(name="Untitled Batch")
        self.executor = None
        self.history = BatchHistory()
        
        self.setWindowTitle("Batch Set Operations")
        self.resize(900, 600)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        
        # Batch name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Batch Name:"))
        self.ed_batch_name = QLineEdit("Untitled Batch")
        name_layout.addWidget(self.ed_batch_name)
        layout.addLayout(name_layout)
        
        # Steps table
        steps_label = QLabel("<b>Batch Steps</b> (executed sequentially):")
        layout.addWidget(steps_label)
        
        self.table_steps = QTableWidget()
        self.table_steps.setColumnCount(7)
        self.table_steps.setHorizontalHeaderLabels([
            "#", "Description", "Operation", "File A", "File B", "Mode", "Status"
        ])
        self.table_steps.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_steps.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_steps.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table_steps)
        
        # Step buttons
        step_btn_layout = QHBoxLayout()
        
        self.btn_add_step = QPushButton("➕ Add Step")
        self.btn_add_step.clicked.connect(self._add_step)
        step_btn_layout.addWidget(self.btn_add_step)
        
        self.btn_edit_step = QPushButton("✏️ Edit Step")
        self.btn_edit_step.clicked.connect(self._edit_step)
        step_btn_layout.addWidget(self.btn_edit_step)
        
        self.btn_remove_step = QPushButton("🗑️ Remove Step")
        self.btn_remove_step.clicked.connect(self._remove_step)
        step_btn_layout.addWidget(self.btn_remove_step)
        
        step_btn_layout.addStretch()
        layout.addLayout(step_btn_layout)
        
        # Intermediate results option
        self.chk_save_intermediate = QCheckBox("Save intermediate results to folder")
        layout.addWidget(self.chk_save_intermediate)
        
        intermediate_layout = QHBoxLayout()
        self.ed_output_folder = QLineEdit()
        self.ed_output_folder.setPlaceholderText("Output folder (if saving intermediate)")
        self.ed_output_folder.setEnabled(False)
        self.btn_browse_output = QPushButton("Browse...")
        self.btn_browse_output.clicked.connect(self._browse_output_folder)
        self.btn_browse_output.setEnabled(False)
        intermediate_layout.addWidget(self.ed_output_folder)
        intermediate_layout.addWidget(self.btn_browse_output)
        layout.addLayout(intermediate_layout)
        
        self.chk_save_intermediate.stateChanged.connect(self._on_save_intermediate_changed)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.btn_save_batch = QPushButton("💾 Save Batch")
        self.btn_save_batch.setToolTip("Save batch definition to JSON file")
        self.btn_save_batch.clicked.connect(self._save_batch)
        action_layout.addWidget(self.btn_save_batch)
        
        self.btn_load_batch = QPushButton("📂 Load Batch")
        self.btn_load_batch.setToolTip("Load batch definition from JSON file")
        self.btn_load_batch.clicked.connect(self._load_batch)
        action_layout.addWidget(self.btn_load_batch)
        
        action_layout.addStretch()
        
        self.btn_execute = QPushButton("▶️ Execute Batch")
        self.btn_execute.setStyleSheet("background-color: #0e639c; color: white; font-weight: bold;")
        self.btn_execute.clicked.connect(self._execute_batch)
        action_layout.addWidget(self.btn_execute)
        
        self.btn_cancel_exec = QPushButton("⏹️ Cancel")
        self.btn_cancel_exec.setEnabled(False)
        self.btn_cancel_exec.clicked.connect(self._cancel_execution)
        action_layout.addWidget(self.btn_cancel_exec)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.reject)
        action_layout.addWidget(self.btn_close)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
    
    def _refresh_table(self):
        """Refresh steps table."""
        self.table_steps.setRowCount(len(self.batch_job.steps))
        
        for row, step in enumerate(self.batch_job.steps):
            # Step number
            self.table_steps.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # Description
            desc = step.description or f"Step {row + 1}"
            self.table_steps.setItem(row, 1, QTableWidgetItem(desc))
            
            # Operation
            op_symbols = {
                'intersection': '∩',
                'union': '∪',
                'difference': '−',
                'symmetric_difference': '⊕'
            }
            op_text = op_symbols.get(step.operation, step.operation)
            self.table_steps.setItem(row, 2, QTableWidgetItem(op_text))
            
            # File A
            file_a_display = "Previous Result" if step.file_a_source == 'previous_result' else os.path.basename(step.file_a_path)
            self.table_steps.setItem(row, 3, QTableWidgetItem(file_a_display))
            
            # File B
            file_b_display = os.path.basename(step.file_b_path)
            self.table_steps.setItem(row, 4, QTableWidgetItem(file_b_display))
            
            # Mode
            mode_short = {
                'key_value': 'K+V',
                'full_path_value': 'FP+V',
                'key_only': 'K'
            }
            mode_text = mode_short.get(step.comparison_mode, step.comparison_mode)
            self.table_steps.setItem(row, 5, QTableWidgetItem(mode_text))
            
            # Status
            status_icons = {
                'pending': '⏸️ Pending',
                'running': '⏳ Running',
                'completed': f'✅ Done ({step.result_count})',
                'failed': f'❌ Failed'
            }
            status_text = status_icons.get(step.status, step.status)
            status_item = QTableWidgetItem(status_text)
            self.table_steps.setItem(row, 6, status_item)
    
    def _add_step(self):
        """Add new step."""
        is_first = len(self.batch_job.steps) == 0
        dialog = BatchStepEditorDialog(is_first_step=is_first, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            step = dialog.get_step()
            if step:
                self.batch_job.add_step(step)
                self._refresh_table()
    
    def _edit_step(self):
        """Edit selected step."""
        row = self.table_steps.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a step to edit")
            return
        
        step = self.batch_job.steps[row]
        is_first = (row == 0)
        
        dialog = BatchStepEditorDialog(step=step, is_first_step=is_first, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            edited_step = dialog.get_step()
            if edited_step:
                self.batch_job.steps[row] = edited_step
                self._refresh_table()
    
    def _remove_step(self):
        """Remove selected step."""
        row = self.table_steps.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a step to remove")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove step {row + 1}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.batch_job.steps[row]
            self._refresh_table()
    
    def _on_save_intermediate_changed(self, state):
        """Handle save intermediate checkbox change."""
        enabled = (state == Qt.Checked)
        self.ed_output_folder.setEnabled(enabled)
        self.btn_browse_output.setEnabled(enabled)
    
    def _browse_output_folder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.ed_output_folder.setText(folder)
    
    def _save_batch(self):
        """Save batch to JSON file."""
        if len(self.batch_job.steps) == 0:
            QMessageBox.warning(self, "Empty Batch", "Please add at least one step before saving")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Batch Job",
            f"{self.ed_batch_name.text()}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.batch_job.name = self.ed_batch_name.text()
            self.batch_job.save_intermediate = self.chk_save_intermediate.isChecked()
            self.batch_job.output_folder = self.ed_output_folder.text()
            
            if self.batch_job.save_to_file(file_path):
                QMessageBox.information(self, "Saved", f"Batch saved to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to save batch job")
    
    def _load_batch(self):
        """Load batch from JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Batch Job",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            batch_job = BatchJob.load_from_file(file_path)
            if batch_job:
                self.batch_job = batch_job
                self.ed_batch_name.setText(batch_job.name)
                self.chk_save_intermediate.setChecked(batch_job.save_intermediate)
                self.ed_output_folder.setText(batch_job.output_folder)
                self._refresh_table()
                QMessageBox.information(self, "Loaded", f"Batch loaded: {batch_job.name}\n{len(batch_job.steps)} steps")
            else:
                QMessageBox.critical(self, "Error", "Failed to load batch job")
    
    def _execute_batch(self):
        """Execute batch job."""
        if len(self.batch_job.steps) == 0:
            QMessageBox.warning(self, "Empty Batch", "Please add at least one step before executing")
            return
        
        # Update batch job settings
        self.batch_job.name = self.ed_batch_name.text()
        self.batch_job.save_intermediate = self.chk_save_intermediate.isChecked()
        self.batch_job.output_folder = self.ed_output_folder.text()
        
        # Reset step statuses
        for step in self.batch_job.steps:
            step.status = 'pending'
            step.result = None
            step.result_count = 0
            step.error_message = ""
            step.execution_time = 0.0
        
        # Disable UI
        self._set_ui_enabled(False)
        self.btn_cancel_exec.setEnabled(True)
        
        # Create executor
        self.executor = BatchExecutor(self.batch_job)
        self.executor.step_started.connect(self._on_step_started)
        self.executor.step_completed.connect(self._on_step_completed)
        self.executor.step_failed.connect(self._on_step_failed)
        self.executor.batch_completed.connect(self._on_batch_completed)
        self.executor.batch_failed.connect(self._on_batch_failed)
        self.executor.finished.connect(self._on_executor_finished)
        
        # Start execution
        self.executor.start()
    
    def _cancel_execution(self):
        """Cancel batch execution."""
        if self.executor:
            self.executor.cancel()
            self.btn_cancel_exec.setEnabled(False)
    
    def _on_step_started(self, step_index: int, total_steps: int):
        """Handle step started."""
        self.batch_job.steps[step_index].status = 'running'
        self._refresh_table()
        self.table_steps.selectRow(step_index)
    
    def _on_step_completed(self, step_index: int, result_count: int, execution_time: float):
        """Handle step completed."""
        self.batch_job.steps[step_index].status = 'completed'
        self.batch_job.steps[step_index].result_count = result_count
        self.batch_job.steps[step_index].execution_time = execution_time
        self._refresh_table()
    
    def _on_step_failed(self, step_index: int, error_message: str):
        """Handle step failed."""
        self.batch_job.steps[step_index].status = 'failed'
        self.batch_job.steps[step_index].error_message = error_message
        self._refresh_table()
    
    def _on_batch_completed(self):
        """Handle batch completed."""
        QMessageBox.information(
            self,
            "Batch Completed",
            f"All {len(self.batch_job.steps)} steps completed successfully!\n\n"
            f"Final result: {self.batch_job.steps[-1].result_count} items"
        )
        
        # Add to history
        self.history.add_batch(self.batch_job)
        
        # Emit final result
        final_result = self.batch_job.steps[-1].result
        if final_result:
            self.batch_result_ready.emit(final_result)
    
    def _on_batch_failed(self, failed_step_index: int, error_message: str):
        """Handle batch failed."""
        QMessageBox.critical(
            self,
            "Batch Failed",
            f"Batch failed at step {failed_step_index + 1}:\n\n{error_message}\n\n"
            f"Partial results preserved for debugging."
        )
    
    def _on_executor_finished(self):
        """Handle executor thread finished."""
        self._set_ui_enabled(True)
        self.btn_cancel_exec.setEnabled(False)
        self.executor = None
    
    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI during execution."""
        self.btn_add_step.setEnabled(enabled)
        self.btn_edit_step.setEnabled(enabled)
        self.btn_remove_step.setEnabled(enabled)
        self.btn_save_batch.setEnabled(enabled)
        self.btn_load_batch.setEnabled(enabled)
        self.btn_execute.setEnabled(enabled)
        self.btn_close.setEnabled(enabled)
