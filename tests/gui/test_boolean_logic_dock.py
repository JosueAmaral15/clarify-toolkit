"""GUI smoke tests for Boolean Logic."""

import json

from src.gui.boolean_logic_dock import BooleanLogicDock


def test_expression_mode_renders_bounded_json(qapp):
    dock = BooleanLogicDock()
    try:
        dock.variables_input.setText("A, B")
        dock.input_edit.setPlainText("A | B")
        dock.run()

        result = json.loads(dock.output_edit.toPlainText())
        assert result["minterms"] == [1, 2, 3]
        assert dock.output_edit.isReadOnly()
    finally:
        dock.close()
        dock.deleteLater()
