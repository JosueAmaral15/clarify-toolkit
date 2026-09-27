"""GUI tests for confirmation-gated voice commands."""

from src.gui.voice_programming_dock import VoiceProgrammingDock
from src.gui.editor_dock import EditorDock


def test_voice_command_cannot_emit_before_exact_preview_confirmation(qapp):
    dock = VoiceProgrammingDock()
    emitted = []
    dock.confirmed_command.connect(emitted.append)
    try:
        dock.transcript_edit.setPlainText("write print open parenthesis close parenthesis")
        dock.preview()
        dock.apply_confirmed()
        assert emitted == []
        assert not dock.apply_button.isEnabled()

        dock.confirm_checkbox.setChecked(True)
        dock.apply_confirmed()
        assert emitted[0]["action"] == "insert_text"
        assert emitted[0]["text"] == "print()"
        assert not dock.apply_button.isEnabled()
    finally:
        dock.close()
        dock.deleteLater()


def test_confirmed_insert_command_uses_current_clarify_editor_cursor(qapp):
    editor_dock = EditorDock()
    try:
        if editor_dock.tab_widget.count() == 0:
            editor_dock._new_file()
        tab = editor_dock.tab_widget.currentWidget()
        tab.editor.setPlainText("start ")
        cursor = tab.editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        tab.editor.setTextCursor(cursor)

        assert editor_dock.apply_confirmed_voice_command({"action": "insert_text", "text": "value"})
        assert tab.editor.toPlainText() == "start value"
    finally:
        editor_dock.close()
        editor_dock.deleteLater()
