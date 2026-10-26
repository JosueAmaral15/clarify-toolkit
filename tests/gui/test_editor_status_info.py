"""Regressions for persistent Clarify Editor document status indicators."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QFileDialog

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def dock(qapp, qtbot, monkeypatch, tmp_path):
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    widget = module.EditorDock()
    qtbot.addWidget(widget)
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def test_editor_exposes_stable_accessible_document_indicators(dock):
    dock._new_file()

    indicators = (
        dock.status_indent_label,
        dock.status_cursor_label,
        dock.status_language_label,
    )
    assert [label.objectName() for label in indicators] == [
        "editor_status_indent",
        "editor_status_cursor",
        "editor_status_language",
    ]
    assert all(label.accessibleName() for label in indicators)
    assert all(label.toolTip() for label in indicators)
    assert all(label.minimumWidth() == label.maximumWidth() for label in indicators)


def test_indentation_and_cursor_status_follow_active_editor(dock, qtbot):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    dock._set_indent_use_tabs(False)
    assert dock._set_indent_width(3)
    tab.editor.setPlainText("first\nsecond")
    cursor = tab.editor.textCursor()
    cursor.setPosition(len("first\nse"))
    tab.editor.setTextCursor(cursor)
    qtbot.waitUntil(
        lambda: dock.status_cursor_label.toolTip()
        == module.tr("editor.status_cursor_position").format(line=2, column=3)
    )

    assert dock.status_indent_label.toolTip() == module.tr("editor.status_indent_spaces").format(width=3)

    dock._set_indent_use_tabs(True)
    assert dock.status_indent_label.toolTip() == module.tr("editor.status_indent_tabs").format(width=3)


def test_language_uses_extension_metadata_and_plain_text_fallback(dock):
    python_tab = dock.load_generated_content("print('ok')", "demo.py", extension=".py")
    assert dock.status_language_label.toolTip() == module.tr("editor.status_language").format(language="Python")

    unknown_tab = dock.load_generated_content("opaque", "demo.unknown", extension=".unknown")
    assert dock.status_language_label.toolTip() == module.tr("editor.status_language").format(
        language=module.tr("editor.status_language_plain_text")
    )

    json_tab = dock.load_generated_content('{"ok": true}', "demo.json", extension=".json")
    assert dock.status_language_label.toolTip() == module.tr("editor.status_language").format(language="JSON")

    dock.tab_widget.setCurrentWidget(python_tab)
    assert dock.status_language_label.toolTip().endswith("Python")
    dock.tab_widget.setCurrentWidget(unknown_tab)
    assert module.tr("editor.status_language_plain_text") in dock.status_language_label.toolTip()
    dock.tab_widget.setCurrentWidget(json_tab)
    assert dock.status_language_label.toolTip().endswith("JSON")


def test_extensionless_shebang_detection_is_bounded_and_reactive(dock, monkeypatch):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    original_to_plain_text = tab.editor.toPlainText
    monkeypatch.setattr(
        tab.editor,
        "toPlainText",
        lambda: pytest.fail("status detection must not extract the whole document"),
    )

    tab.editor.setPlainText("#!/usr/bin/env python3\nprint('ok')")
    assert dock.status_language_label.toolTip().endswith("Python")

    tab.editor.setPlainText("ordinary text")
    assert module.tr("editor.status_language_plain_text") in dock.status_language_label.toolTip()
    monkeypatch.setattr(tab.editor, "toPlainText", original_to_plain_text)


def test_split_cursor_is_active_then_main_cursor_returns_on_close(dock, qtbot):
    dock._new_file()
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("one\ntwo\nthree")
    main_cursor = tab.editor.textCursor()
    main_cursor.setPosition(1)
    tab.editor.setTextCursor(main_cursor)

    assert dock._show_split_view(tab, Qt.Orientation.Horizontal)
    split_cursor = dock.split_editor.textCursor()
    split_cursor.setPosition(len("one\ntw"))
    dock.split_editor.setTextCursor(split_cursor)
    qtbot.waitUntil(
        lambda: dock.status_cursor_label.toolTip()
        == module.tr("editor.status_cursor_position").format(line=2, column=3)
    )

    dock._close_split_view()
    assert dock.status_cursor_label.toolTip() == module.tr("editor.status_cursor_position").format(line=1, column=2)


def test_first_save_as_refreshes_language_from_new_path(dock, monkeypatch, tmp_path):
    target = tmp_path / "saved.ts"
    dock._new_file()
    dock.tab_widget.currentWidget().editor.setPlainText("const value = 1")
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(target), "All Files (*)"),
    )

    assert dock._save_file_as()
    assert dock.status_language_label.toolTip().endswith("TypeScript")


def test_explorer_rename_refreshes_open_tab_language(dock, monkeypatch, tmp_path):
    source = tmp_path / "module.py"
    source.write_text("print('ok')", encoding="utf-8")
    dock.explorer_root_path = str(tmp_path)
    assert dock.open_file_path(str(source))
    monkeypatch.setattr(
        dock,
        "_handle_reference_updates_after_rename",
        lambda *_args, **_kwargs: None,
    )

    assert dock._rename_explorer_path(str(source), "module.md")
    assert dock.status_language_label.toolTip().endswith("Markdown")


def test_status_templates_retranslate_without_changing_document(dock, monkeypatch):
    dock._new_file()
    dock._set_indent_use_tabs(False)
    tab = dock.tab_widget.currentWidget()
    tab.editor.setPlainText("unchanged")
    before = tab.editor.toPlainText()
    translations = {
        "editor.status_indent_spaces": "Indent {width}",
        "editor.status_indent_tabs": "Tabs {width}",
        "editor.status_cursor_position": "Cursor {line}:{column}",
        "editor.status_cursor_unavailable": "Cursor -:-",
        "editor.status_language": "Lang {language}",
        "editor.status_language_plain_text": "Text",
    }
    monkeypatch.setattr(module, "tr", lambda key, default=None: translations.get(key, key))

    dock._retranslate_status_info("test")

    assert dock.status_indent_label.accessibleName().startswith("Indent ")
    assert dock.status_cursor_label.accessibleName().startswith("Cursor ")
    assert dock.status_language_label.accessibleName() == "Lang Text"
    assert tab.editor.toPlainText() == before


def test_empty_editor_reports_no_cursor_and_plain_text(dock):
    assert dock.tab_widget.count() == 0
    dock._update_editor_status_indicators()

    assert dock.status_cursor_label.toolTip() == module.tr("editor.status_cursor_unavailable")
    assert module.tr("editor.status_language_plain_text") in dock.status_language_label.toolTip()
