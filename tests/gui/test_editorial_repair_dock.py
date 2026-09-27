"""GUI tests for editorial review sessions."""

import json

from src.gui.editorial_repair_dock import EditorialRepairDock


def test_new_tab_creates_independent_editorial_session(qapp):
    dock = EditorialRepairDock()
    try:
        first = dock.tabs.widget(0)
        first.source_edit.setPlainText("First session")
        second = dock.add_session()
        second.source_edit.setPlainText("Second session")

        assert dock.tabs.count() == 2
        assert first.source_edit.toPlainText() == "First session"
        assert second.source_edit.toPlainText() == "Second session"
        assert dock.new_tab_button.text() == "New Tab"
    finally:
        dock.close()
        dock.deleteLater()


def test_local_defect_diagnostics_render_read_only_json(qapp):
    dock = EditorialRepairDock()
    try:
        session = dock.tabs.widget(0)
        session.mode_combo.setCurrentIndex(session.mode_combo.findData("defects"))
        session.source_edit.setPlainText("TODO: explain this thing.")
        session.analyze()

        result = json.loads(session.output_edit.toPlainText())
        assert result["type"] == "textual_defect_diagnostics"
        assert session.output_edit.isReadOnly()
    finally:
        dock.close()
        dock.deleteLater()
