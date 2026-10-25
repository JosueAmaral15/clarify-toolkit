"""Clarify Editor smart Home regressions for wrapped visual lines."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextOption
from PySide6.QtWidgets import QTextEdit

from src.editor_notes import TemporaryNoteStore
from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    monkeypatch.setattr(
        module,
        "TemporaryNoteStore",
        partial(TemporaryNoteStore, root=tmp_path / "notes"),
    )
    widget = module.EditorDock()
    qtbot.addWidget(widget)
    widget.show()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def _wrapped_editor(qapp, qtbot, text, *, width=150, wrap_anywhere=False):
    editor = QTextEdit()
    qtbot.addWidget(editor)
    editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
    if wrap_anywhere:
        option = editor.document().defaultTextOption()
        option.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
        editor.document().setDefaultTextOption(option)
    editor.resize(width, 180)
    editor.setPlainText(text)
    editor.show()
    qapp.processEvents()
    return editor


def _visual_ranges(editor):
    block = editor.document().firstBlock()
    layout = block.layout()
    return [
        (
            layout.lineAt(index).textStart(),
            layout.lineAt(index).textLength(),
        )
        for index in range(layout.lineCount())
    ]


def _set_position_in_block(editor, position, *, anchor=None):
    block = editor.document().firstBlock()
    cursor = editor.textCursor()
    if anchor is None:
        cursor.setPosition(block.position() + position)
    else:
        cursor.setPosition(block.position() + anchor)
        cursor.setPosition(
            block.position() + position,
            QTextCursor.MoveMode.KeepAnchor,
        )
    editor.setTextCursor(cursor)


def test_home_stays_on_the_current_wrapped_visual_line(qapp, qtbot):
    text = "    alpha beta gamma delta epsilon zeta eta theta iota kappa"
    editor = _wrapped_editor(qapp, qtbot, text)
    ranges = _visual_ranges(editor)
    assert len(ranges) >= 2
    visual_start, visual_length = ranges[1]
    _set_position_in_block(editor, visual_start + min(3, visual_length - 1))
    original_text = editor.toPlainText()
    original_revision = editor.document().revision()
    original_undo = editor.document().isUndoAvailable()

    module.EditorDock._move_to_smart_home(editor, keep_anchor=False)

    assert editor.textCursor().positionInBlock() == visual_start
    assert editor.toPlainText() == original_text
    assert editor.document().revision() == original_revision
    assert editor.document().isUndoAvailable() == original_undo


def test_shift_home_keeps_anchor_on_the_same_visual_line(qapp, qtbot):
    text = "    alpha beta gamma delta epsilon zeta eta theta iota kappa"
    editor = _wrapped_editor(qapp, qtbot, text)
    visual_start, visual_length = _visual_ranges(editor)[1]
    original_position = visual_start + min(5, visual_length - 1)
    _set_position_in_block(editor, original_position)

    module.EditorDock._move_to_smart_home(editor, keep_anchor=True)

    cursor = editor.textCursor()
    assert cursor.positionInBlock() == visual_start
    assert cursor.anchor() == editor.document().firstBlock().position() + original_position


def test_first_visual_line_preserves_space_and_tab_toggle(qapp, qtbot):
    for prefix in ("    ", "\t\t"):
        editor = _wrapped_editor(qapp, qtbot, f"{prefix}value", width=500)
        assert len(_visual_ranges(editor)) == 1
        _set_position_in_block(editor, len(prefix) + 3)

        module.EditorDock._move_to_smart_home(editor, keep_anchor=False)
        assert editor.textCursor().positionInBlock() == len(prefix)
        module.EditorDock._move_to_smart_home(editor, keep_anchor=False)
        assert editor.textCursor().positionInBlock() == 0


def test_whitespace_only_visual_segment_uses_its_own_start(qapp, qtbot):
    editor = _wrapped_editor(
        qapp,
        qtbot,
        "abcdefghij\t\tvalue tail tail",
        width=80,
        wrap_anywhere=True,
    )
    ranges = _visual_ranges(editor)
    whitespace_index = next(
        index
        for index, (start, length) in enumerate(ranges)
        if editor.toPlainText()[start : start + length].strip(" \t") == ""
    )
    visual_start, _visual_length = ranges[whitespace_index]
    _set_position_in_block(editor, visual_start)

    module.EditorDock._move_to_smart_home(editor, keep_anchor=False)

    assert editor.textCursor().positionInBlock() == visual_start


def test_empty_block_and_bidi_text_remain_bounded(qapp, qtbot):
    editor = _wrapped_editor(qapp, qtbot, "alpha\n\n    مرحبا بالعالم")
    empty_block = editor.document().findBlockByNumber(1)
    cursor = editor.textCursor()
    cursor.setPosition(empty_block.position())
    editor.setTextCursor(cursor)
    module.EditorDock._move_to_smart_home(editor, keep_anchor=False)
    assert editor.textCursor().position() == empty_block.position()

    bidi_block = editor.document().findBlockByNumber(2)
    cursor.setPosition(bidi_block.position() + len(bidi_block.text()))
    editor.setTextCursor(cursor)
    module.EditorDock._move_to_smart_home(editor, keep_anchor=False)
    assert editor.textCursor().position() == bidi_block.position() + 4
    module.EditorDock._move_to_smart_home(editor, keep_anchor=False)
    assert editor.textCursor().position() == bidi_block.position()


def test_layout_is_recalculated_after_resize_and_zoom(qapp, qtbot):
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda"
    editor = _wrapped_editor(qapp, qtbot, text, width=110)
    assert len(_visual_ranges(editor)) >= 3
    editor.resize(210, 180)
    editor.zoomIn(2)
    qapp.processEvents()
    ranges = _visual_ranges(editor)
    assert len(ranges) >= 2
    visual_start, visual_length = ranges[-1]
    _set_position_in_block(editor, visual_start + max(0, visual_length - 1))

    module.EditorDock._move_to_smart_home(editor, keep_anchor=False)

    assert editor.textCursor().positionInBlock() == visual_start


def test_read_only_split_receives_home_without_moving_primary_cursor(dock, qapp, qtbot):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    text = "    alpha beta gamma delta epsilon zeta eta theta iota kappa"
    tab.editor.setPlainText(text)
    primary_cursor = tab.editor.textCursor()
    primary_cursor.setPosition(2)
    tab.editor.setTextCursor(primary_cursor)
    assert dock._show_split_view(tab, Qt.Orientation.Horizontal)
    dock.split_editor.setReadOnly(True)
    dock.split_editor.resize(150, 180)
    qapp.processEvents()
    ranges = _visual_ranges(dock.split_editor)
    assert len(ranges) >= 2
    visual_start, visual_length = ranges[1]
    _set_position_in_block(
        dock.split_editor,
        visual_start + min(3, visual_length - 1),
    )
    before_text = tab.editor.toPlainText()

    qtbot.keyClick(dock.split_editor, Qt.Key.Key_Home)

    assert dock.split_editor.textCursor().positionInBlock() == visual_start
    assert tab.editor.textCursor().positionInBlock() == 2
    assert tab.editor.toPlainText() == before_text
