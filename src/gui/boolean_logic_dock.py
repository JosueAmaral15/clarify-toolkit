"""Truth-table generation and bounded Boolean minimization UI."""

from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.boolean_logic import expression_truth_table, minimize_truth_table


class BooleanLogicDock(QWidget):
    """Convert expressions to tables or tables to minimized forms."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BooleanLogicDock")
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Expression to truth table", "expression")
        self.mode_combo.addItem("Truth table JSON to minimized expression", "table")
        self.mode_combo.currentIndexChanged.connect(self._mode_changed)
        self.variables_input = QLineEdit("A, B")
        self.variables_input.setPlaceholderText("Variables: A, B, C")
        controls.addWidget(self.mode_combo)
        controls.addWidget(QLabel("Variables:"))
        controls.addWidget(self.variables_input, 1)
        layout.addLayout(controls)
        self.input_edit = QPlainTextEdit("A & ~B")
        layout.addWidget(self.input_edit, 2)
        self.run_button = QPushButton("Generate")
        self.run_button.clicked.connect(self.run)
        layout.addWidget(self.run_button)
        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.document().setMaximumBlockCount(5_000)
        layout.addWidget(self.output_edit, 3)
        self._mode_changed()

    def _mode_changed(self) -> None:
        if self.mode_combo.currentData() == "expression":
            self.input_edit.setPlaceholderText("Boolean expression using ~, &, |, ^ and parentheses")
            self.run_button.setText("Generate truth table")
        else:
            self.input_edit.setPlaceholderText('[{"A": 0, "B": 0, "output": 0}, ...]')
            self.run_button.setText("Minimize truth table")

    def run(self) -> None:
        try:
            if self.mode_combo.currentData() == "expression":
                result = expression_truth_table(self.variables_input.text(), self.input_edit.toPlainText().strip())
            else:
                rows = json.loads(self.input_edit.toPlainText())
                if not isinstance(rows, list):
                    raise ValueError("Truth table JSON must be a list of rows")
                result = minimize_truth_table(self.variables_input.text(), rows)
            self.output_edit.setPlainText(json.dumps(result, ensure_ascii=False, indent=2))
        except (SyntaxError, ValueError, json.JSONDecodeError) as exc:
            QMessageBox.warning(self, "Boolean logic error", str(exc))
