"""
Formula Builder Dock Widget
Visual interface for building complex set operation formulas.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.108
"""
# pylint: disable=no-name-in-module  # Qt dynamic modules
# pylint: disable=attribute-defined-outside-init  # Qt dialog pattern

import json

from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QMessageBox,
    QInputDialog,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QSplitter,
    QGroupBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal

from src.formula_manager import Formula, FormulaStep, FormulaManager, FormulaExecutor
from src.i18n.translator import get_translator

tr = get_translator().get


class AddStepDialog(QWidget):
    """Dialog for adding/editing a formula step."""

    def __init__(self, parent=None, step: FormulaStep = None):
        """
        Initialize AddStepDialog.

        Args:
            parent: Parent widget
            step: FormulaStep to edit (None for new step)
        """
        super().__init__(parent)
        self.step = step
        self.setWindowTitle(tr("formula.dialog_add_title") if not step else tr("formula.dialog_edit_title"))
        self.setMinimumWidth(500)
        self._init_ui()

        if step:
            self._load_step(step)

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Operation selection
        op_layout = QHBoxLayout()
        op_layout.addWidget(QLabel(tr("formula.lbl_operation")))
        self.combo_operation = QComboBox()
        self.combo_operation.addItems(["∩ Intersection", "∪ Union", "− Difference", "⊕ Symmetric"])
        op_layout.addWidget(self.combo_operation)
        layout.addLayout(op_layout)

        # Input A
        layout.addWidget(QLabel(tr("formula.lbl_input_a")))
        input_a_layout = QHBoxLayout()
        self.combo_input_a = QComboBox()
        self.combo_input_a.addItems(["file_path", "previous", "slot_a", "slot_b", "r1", "r2", "r3"])
        input_a_layout.addWidget(self.combo_input_a)
        self.ed_file_a = QLineEdit()
        self.ed_file_a.setPlaceholderText(tr("formula.placeholder_file_a"))
        input_a_layout.addWidget(self.ed_file_a)
        self.btn_browse_a = QPushButton(tr("formula.btn_browse"))
        self.btn_browse_a.clicked.connect(self._browse_file_a)
        input_a_layout.addWidget(self.btn_browse_a)
        layout.addLayout(input_a_layout)

        # Input B
        layout.addWidget(QLabel(tr("formula.lbl_input_b")))
        input_b_layout = QHBoxLayout()
        self.combo_input_b = QComboBox()
        self.combo_input_b.addItems(["file_path", "previous", "slot_a", "slot_b", "r1", "r2", "r3"])
        input_b_layout.addWidget(self.combo_input_b)
        self.ed_file_b = QLineEdit()
        self.ed_file_b.setPlaceholderText(tr("formula.placeholder_file_b"))
        input_b_layout.addWidget(self.ed_file_b)
        self.btn_browse_b = QPushButton(tr("formula.btn_browse"))
        self.btn_browse_b.clicked.connect(self._browse_file_b)
        input_b_layout.addWidget(self.btn_browse_b)
        layout.addLayout(input_b_layout)

        # Output variable
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel(tr("formula.lbl_output_var")))
        self.ed_output = QLineEdit()
        self.ed_output.setPlaceholderText(tr("formula.placeholder_output"))
        output_layout.addWidget(self.ed_output)
        layout.addLayout(output_layout)

        # Comparison mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel(tr("formula.lbl_comparison_mode")))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["key_value", "full_path_value", "key_only"])
        mode_layout.addWidget(self.combo_mode)
        layout.addLayout(mode_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton(tr("formula.btn_ok"))
        self.btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_ok)
        self.btn_cancel = QPushButton(tr("formula.btn_cancel"))
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _browse_file_a(self):
        """Browse for File A."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File A", "", "JSON Files (*.json)")
        if file_path:
            self.ed_file_a.setText(file_path)

    def _browse_file_b(self):
        """Browse for File B."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File B", "", "JSON Files (*.json)")
        if file_path:
            self.ed_file_b.setText(file_path)

    def _load_step(self, step: FormulaStep):
        """Load step data into UI."""
        # Operation
        op_map = {"∩": 0, "∪": 1, "−": 2, "⊕": 3}
        self.combo_operation.setCurrentIndex(op_map.get(step.operation, 0))

        # Inputs
        self.combo_input_a.setCurrentText(step.input_a)
        self.combo_input_b.setCurrentText(step.input_b)
        self.ed_file_a.setText(step.file_a_path)
        self.ed_file_b.setText(step.file_b_path)

        # Output
        self.ed_output.setText(step.output_variable)

        # Mode
        self.combo_mode.setCurrentText(step.comparison_mode)

    def accept(self):
        """Accept dialog and create/update step."""
        # Get operation symbol
        op_text = self.combo_operation.currentText()
        operation = op_text[0]  # First char is symbol

        # Validation
        output_var = self.ed_output.text().strip()
        if not output_var:
            QMessageBox.warning(self, tr("formula.msg_validation_error_title"), tr("formula.msg_output_required"))
            return

        # Create step
        self.result_step = FormulaStep(
            operation=operation,
            input_a=self.combo_input_a.currentText(),
            input_b=self.combo_input_b.currentText(),
            file_a_path=self.ed_file_a.text().strip(),
            file_b_path=self.ed_file_b.text().strip(),
            output_variable=output_var,
            comparison_mode=self.combo_mode.currentText(),
        )

        self.close()

    def get_step(self) -> FormulaStep:
        """Get created/edited step."""
        return getattr(self, "result_step", None)


class FormulaDock(QDockWidget):
    """Formula Builder dock widget."""

    formula_executed = Signal(dict)  # Signal for integration

    def __init__(self, parent=None):
        """Initialize FormulaDock."""
        super().__init__("Formula Builder", parent)

        self.formula_manager = FormulaManager()
        self.formula_executor = FormulaExecutor()
        self.current_formula = Formula("New Formula")

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize UI components."""
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Formula name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(tr("formula.lbl_formula_name")))
        self.ed_formula_name = QLineEdit()
        self.ed_formula_name.setPlaceholderText(tr("formula.placeholder_name"))
        name_layout.addWidget(self.ed_formula_name)
        layout.addLayout(name_layout)

        # Splitter: Steps tree | Formula preview
        splitter = QSplitter(Qt.Horizontal)

        # Left: Steps tree
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel(tr("formula.lbl_formula_steps")))
        self.tree_steps = QTreeWidget()
        self.tree_steps.setHeaderLabels([tr("formula_dock.header_step"), tr("formula_dock.header_expression")])
        self.tree_steps.setColumnWidth(0, 80)

        # Prevent horizontal expansion from long expressions (v2.9.117)
        self.tree_steps.setWordWrap(False)
        self.tree_steps.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.tree_steps.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        header = self.tree_steps.header()
        header.setStretchLastSection(True)

        left_layout.addWidget(self.tree_steps)

        # Step management buttons
        step_btn_layout = QHBoxLayout()
        self.btn_add_step = QPushButton(tr("formula.btn_add_step"))
        step_btn_layout.addWidget(self.btn_add_step)
        self.btn_edit_step = QPushButton(tr("formula.btn_edit"))
        step_btn_layout.addWidget(self.btn_edit_step)
        self.btn_remove_step = QPushButton(tr("formula.btn_remove"))
        step_btn_layout.addWidget(self.btn_remove_step)
        self.btn_move_up = QPushButton(tr("formula.btn_up"))
        step_btn_layout.addWidget(self.btn_move_up)
        self.btn_move_down = QPushButton(tr("formula.btn_down"))
        step_btn_layout.addWidget(self.btn_move_down)
        left_layout.addLayout(step_btn_layout)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right: Formula preview
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        right_layout.addWidget(QLabel(tr("formula.lbl_preview")))
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setMaximumHeight(150)
        right_layout.addWidget(self.text_preview)

        # Execution result
        result_group = QGroupBox(tr("formula.group_result"))
        result_layout = QVBoxLayout()
        self.lbl_result_status = QLabel(tr("formula.status_not_executed"))
        result_layout.addWidget(self.lbl_result_status)
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.text_result.setMaximumHeight(200)
        result_layout.addWidget(self.text_result)
        result_group.setLayout(result_layout)
        right_layout.addWidget(result_group)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        splitter.setSizes([300, 400])
        layout.addWidget(splitter)

        # Action buttons
        action_layout = QHBoxLayout()
        self.btn_execute = QPushButton(tr("formula.btn_execute"))
        self.btn_execute.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        action_layout.addWidget(self.btn_execute)

        self.btn_save_template = QPushButton(tr("formula.btn_save_template"))
        action_layout.addWidget(self.btn_save_template)

        self.btn_load_template = QPushButton(tr("formula.btn_load_template"))
        action_layout.addWidget(self.btn_load_template)

        self.btn_clear = QPushButton(tr("formula.btn_clear_all"))
        action_layout.addWidget(self.btn_clear)

        layout.addLayout(action_layout)

        main_widget.setLayout(layout)
        self.setWidget(main_widget)

    def _connect_signals(self):
        """Connect signals to slots."""
        self.btn_add_step.clicked.connect(self._add_step)
        self.btn_edit_step.clicked.connect(self._edit_step)
        self.btn_remove_step.clicked.connect(self._remove_step)
        self.btn_move_up.clicked.connect(self._move_step_up)
        self.btn_move_down.clicked.connect(self._move_step_down)
        self.btn_execute.clicked.connect(self._execute_formula)
        self.btn_save_template.clicked.connect(self._save_template)
        self.btn_load_template.clicked.connect(self._load_template)
        self.btn_clear.clicked.connect(self._clear_all)
        self.ed_formula_name.textChanged.connect(self._update_preview)

    def _add_step(self):
        """Add new step to formula."""
        dialog = AddStepDialog(self)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.show()
        dialog.accepted = lambda: self._on_step_added(dialog)

    def _on_step_added(self, dialog: AddStepDialog):
        """Handle step added."""
        step = dialog.get_step()
        if step:
            self.current_formula.add_step(step)
            self._refresh_tree()
            self._update_preview()

    def _edit_step(self):
        """Edit selected step."""
        current_item = self.tree_steps.currentItem()
        if not current_item:
            QMessageBox.warning(self, tr("formula.msg_no_selection_title"), tr("formula.msg_select_step_edit"))
            return

        index = self.tree_steps.indexOfTopLevelItem(current_item)
        if 0 <= index < len(self.current_formula.steps):
            step = self.current_formula.steps[index]
            dialog = AddStepDialog(self, step)
            dialog.setWindowModality(Qt.ApplicationModal)
            dialog.show()
            dialog.accepted = lambda: self._on_step_edited(dialog, index)

    def _on_step_edited(self, dialog: AddStepDialog, index: int):
        """Handle step edited."""
        step = dialog.get_step()
        if step:
            self.current_formula.steps[index] = step
            self._refresh_tree()
            self._update_preview()

    def _remove_step(self):
        """Remove selected step."""
        current_item = self.tree_steps.currentItem()
        if not current_item:
            QMessageBox.warning(self, tr("formula.msg_no_selection_title"), tr("formula.msg_select_step_remove"))
            return

        index = self.tree_steps.indexOfTopLevelItem(current_item)
        reply = QMessageBox.question(
            self,
            tr("formula.msg_confirm_remove_title"),
            tr("formula.msg_confirm_remove_msg").format(index + 1),
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.current_formula.remove_step(index)
            self._refresh_tree()
            self._update_preview()

    def _move_step_up(self):
        """Move selected step up."""
        current_item = self.tree_steps.currentItem()
        if not current_item:
            return

        index = self.tree_steps.indexOfTopLevelItem(current_item)
        if index > 0:
            steps = self.current_formula.steps
            steps[index], steps[index - 1] = steps[index - 1], steps[index]
            self._refresh_tree()
            self._update_preview()
            self.tree_steps.setCurrentItem(self.tree_steps.topLevelItem(index - 1))

    def _move_step_down(self):
        """Move selected step down."""
        current_item = self.tree_steps.currentItem()
        if not current_item:
            return

        index = self.tree_steps.indexOfTopLevelItem(current_item)
        if index < len(self.current_formula.steps) - 1:
            steps = self.current_formula.steps
            steps[index], steps[index + 1] = steps[index + 1], steps[index]
            self._refresh_tree()
            self._update_preview()
            self.tree_steps.setCurrentItem(self.tree_steps.topLevelItem(index + 1))

    def _refresh_tree(self):
        """Refresh steps tree widget."""
        self.tree_steps.clear()

        for i, step in enumerate(self.current_formula.steps, 1):
            display_text = step.get_display_text()
            # Truncate long expressions to prevent horizontal expansion (v2.9.117)
            if len(display_text) > 80:
                display_text_short = display_text[:80] + "..."
                item = QTreeWidgetItem([f"Step {i}", display_text_short])
                # Add full text as tooltip
                item.setToolTip(1, display_text)
            else:
                item = QTreeWidgetItem([f"Step {i}", display_text])
            self.tree_steps.addTopLevelItem(item)

    def _update_preview(self):
        """Update formula preview text."""
        name = self.ed_formula_name.text() or "Unnamed Formula"
        self.current_formula.name = name

        formula_text = self.current_formula.get_formula_text()
        if formula_text:
            self.text_preview.setPlainText(f"Formula: {name}\n\n{formula_text}")
        else:
            self.text_preview.setPlainText("No steps added yet. Click 'Add Step' to begin.")

    def _execute_formula(self):
        """Execute current formula."""
        if not self.current_formula.steps:
            QMessageBox.warning(self, tr("formula.msg_empty_formula_title"), tr("formula.msg_add_step_execute"))
            return

        # Get file paths from steps
        initial_files = {}
        for i, step in enumerate(self.current_formula.steps):
            if step.input_a == "file_path" and step.file_a_path:
                initial_files[f"file_a_{i}"] = step.file_a_path
            if step.input_b == "file_path" and step.file_b_path:
                initial_files[f"file_b_{i}"] = step.file_b_path

        # Execute
        self.lbl_result_status.setText(tr("formula.status_executing"))
        self.lbl_result_status.setStyleSheet("color: orange;")

        result = self.formula_executor.execute(self.current_formula, initial_files)

        if result["success"]:
            self.lbl_result_status.setText(f"✅ Success! {result.get('steps_executed', 0)} steps executed")
            self.lbl_result_status.setStyleSheet("color: green; font-weight: bold;")

            # Display result
            result_json = json.dumps(result["result"], indent=2, ensure_ascii=False)
            self.text_result.setPlainText(f"Final Result ({len(result['result'])} keys):\n\n{result_json[:2000]}")

            # Emit signal for integration
            self.formula_executed.emit(result)
        else:
            self.lbl_result_status.setText(f"❌ Error at step {result.get('step', '?')}")
            self.lbl_result_status.setStyleSheet("color: red; font-weight: bold;")
            self.text_result.setPlainText(f"Error: {result.get('error', 'Unknown error')}")

    def _save_template(self):
        """Save current formula as template."""
        if not self.current_formula.steps:
            QMessageBox.warning(self, tr("formula.msg_empty_formula_title"), tr("formula.msg_add_step_save"))
            return

        name = self.ed_formula_name.text().strip()
        if not name:
            name, ok = QInputDialog.getText(self, tr("formula.dialog_save_template"), tr("formula.dialog_enter_name"))
            if not ok or not name:
                return

        self.current_formula.name = name

        # Ask for description
        description, ok = QInputDialog.getMultiLineText(
            self,
            tr("formula.dialog_save_template"),
            tr("formula.dialog_description_optional"),
            self.current_formula.description,
        )
        if ok:
            self.current_formula.description = description

        self.formula_manager.save_formula(self.current_formula)
        QMessageBox.information(self, tr("formula.msg_success_title"), tr("formula.msg_saved_success").format(name))

    def _load_template(self):
        """Load formula template."""
        formulas = self.formula_manager.get_formulas()

        if not formulas:
            QMessageBox.information(self, tr("formula.msg_no_templates_title"), tr("formula.msg_no_templates_found"))
            return

        # Show selection dialog
        names = [f.name for f in formulas]
        name, ok = QInputDialog.getItem(
            self, tr("formula.dialog_load_template"), tr("formula.dialog_select_formula"), names, 0, False
        )

        if ok and name:
            formula = self.formula_manager.get_formula(name)
            if formula:
                self.current_formula = formula
                self.ed_formula_name.setText(formula.name)
                self._refresh_tree()
                self._update_preview()
                QMessageBox.information(
                    self, tr("formula.msg_success_title"), tr("formula.msg_loaded_success").format(name)
                )

    def _clear_all(self):
        """Clear all steps and reset formula."""
        if self.current_formula.steps:
            reply = QMessageBox.question(
                self,
                tr("formula.msg_confirm_clear_title"),
                tr("formula.msg_confirm_clear_msg"),
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self.current_formula = Formula("New Formula")
        self.ed_formula_name.clear()
        self._refresh_tree()
        self._update_preview()
        self.text_result.clear()
        self.lbl_result_status.setText(tr("formula.status_not_executed"))
        self.lbl_result_status.setStyleSheet("")
