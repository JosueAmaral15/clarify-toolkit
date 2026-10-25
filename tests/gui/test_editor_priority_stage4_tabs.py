"""Focused regressions for Editor tab context, splits and Explorer sync."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial

from PySide6 import QtCore
from PySide6.QtWidgets import QMessageBox

from src.gui import editor_dock as module


def make_dock(qtbot, tmp_path, monkeypatch, settings=None):
    settings = settings or QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    return dock, settings


def open_files(dock, tmp_path, names):
    tabs = []
    for name in names:
        path = tmp_path / name
        path.write_text(name, encoding="utf-8")
        assert dock.open_file_path(str(path))
        tabs.append(dock.tab_widget.currentWidget())
    return tabs


def test_tab_context_menu_has_complete_bounded_actions(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    open_files(dock, tmp_path, ["a.txt", "b.txt", "c.txt"])

    menu = dock._build_tab_context_menu(1)
    ids = [action.data() for action in menu.actions() if not action.isSeparator()]

    assert ids == [
        "close",
        "close_others",
        "close_all",
        "close_left",
        "close_right",
        "copy_absolute",
        "copy_relative",
        "split_down",
        "split_right",
        "toggle_edit_only",
    ]
    assert all(action.text() for action in menu.actions() if not action.isSeparator())


def test_bulk_close_stops_on_cancel_without_losing_buffer(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    tabs = open_files(dock, tmp_path, ["a.txt", "b.txt"])
    tabs[0].editor.insertPlainText(" changed")
    assert tabs[0].is_modified
    monkeypatch.setattr(
        module.QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.Cancel,
    )

    assert dock._close_tab_objects(tabs) is False
    assert dock.tab_widget.count() == 2
    assert "changed" in tabs[0].editor.toPlainText()


def test_close_left_and_right_use_tab_identity(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    tabs = open_files(dock, tmp_path, ["a.txt", "b.txt", "c.txt", "d.txt"])

    assert dock._close_tab_objects(tabs[:2]) is True
    assert [dock.tab_widget.widget(i) for i in range(dock.tab_widget.count())] == tabs[2:]
    assert dock._close_tab_objects([tabs[3]]) is True
    assert dock.tab_widget.count() == 1
    assert dock.tab_widget.widget(0) is tabs[2]


def test_split_view_shares_document_without_duplicate_tab_or_watcher(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    tab = open_files(dock, tmp_path, ["a.txt"])[0]
    watched_before = set(dock._watched_file_paths)

    assert dock._show_split_view(tab, QtCore.Qt.Horizontal)
    assert dock.split_panel.isHidden() is False
    assert dock.editor_workspace_splitter.orientation() == QtCore.Qt.Horizontal
    assert dock.split_editor.document() is tab.editor.document()
    assert dock.tab_widget.count() == 1
    assert dock._watched_file_paths == watched_before

    dock.split_editor.moveCursor(module.QTextCursor.End)
    dock.split_editor.insertPlainText(" shared")
    assert tab.editor.toPlainText().endswith(" shared")

    assert dock._show_split_view(tab, QtCore.Qt.Vertical)
    assert dock.editor_workspace_splitter.orientation() == QtCore.Qt.Vertical
    dock._close_split_view()
    assert dock.split_panel.isHidden()
    assert dock._split_source_tab is None


def test_split_selected_tab_uses_visible_spaces_preference(qtbot, tmp_path, monkeypatch):
    """Selected-line Tab in a split must use the same visible Spaces setting."""
    settings = QtCore.QSettings(str(tmp_path / "split-indent.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("indent_width", 3)
    dock, settings = make_dock(qtbot, tmp_path, monkeypatch, settings=settings)
    if dock.action_indent_use_tabs.isChecked():
        dock.action_indent_use_tabs.trigger()

    tab = open_files(dock, tmp_path, ["split.txt"])[0]
    tab.editor.setPlainText("one\ntwo")
    assert dock._show_split_view(tab, QtCore.Qt.Horizontal)
    dock.split_editor.selectAll()

    qtbot.keyClick(dock.split_editor, QtCore.Qt.Key_Tab)

    assert tab.editor.toPlainText() == "   one\n   two"
    dock.split_editor.undo()
    assert tab.editor.toPlainText() == "one\ntwo"

    dock.split_editor.selectAll()
    dock.action_indent.trigger()
    assert tab.editor.toPlainText() == "   one\n   two"
    dock.split_editor.selectAll()
    qtbot.keyClick(dock.split_editor, QtCore.Qt.Key_Backtab)
    assert tab.editor.toPlainText() == "one\ntwo"


def test_closing_split_source_detaches_secondary_document(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    tab = open_files(dock, tmp_path, ["a.txt"])[0]
    dock._show_split_view(tab, QtCore.Qt.Horizontal)

    assert dock._close_tab_object(tab)

    assert dock.tab_widget.count() == 0
    assert dock.split_panel.isHidden()
    assert dock._split_source_tab is None


def test_tab_drag_order_persists_and_restores_by_path(qtbot, tmp_path, monkeypatch):
    dock, settings = make_dock(qtbot, tmp_path, monkeypatch)
    open_files(dock, tmp_path, ["a.txt", "b.txt", "c.txt"])
    dock.tab_widget.tabBar().moveTab(2, 0)
    expected = [str(tmp_path / name) for name in ("c.txt", "a.txt", "b.txt")]
    assert dock._persisted_tab_order == expected

    restored, _settings = make_dock(qtbot, tmp_path, monkeypatch, settings)
    open_files(restored, tmp_path, ["a.txt", "b.txt", "c.txt"])
    actual = [restored.tab_widget.widget(index).file_path for index in range(restored.tab_widget.count())]
    assert actual == expected


def test_active_file_is_selected_only_inside_explorer_root(qtbot, tmp_path, monkeypatch):
    dock, _settings = make_dock(qtbot, tmp_path, monkeypatch)
    inside = tmp_path / "inside.txt"
    inside.write_text("inside", encoding="utf-8")
    outside = tmp_path.parent / "outside-clarify-editor-test.txt"
    outside.write_text("outside", encoding="utf-8")
    try:
        dock.explorer_model.setRootPath(str(tmp_path))
        qtbot.waitUntil(lambda: dock.explorer_model.index(str(inside)).isValid())
        assert dock.open_file_path(str(inside))
        assert dock._select_explorer_path(str(inside))
        assert dock.explorer_model.filePath(dock.explorer_tree.currentIndex()) == str(inside)

        assert dock.open_file_path(str(outside))
        assert dock._select_explorer_path(str(outside)) is False
        assert not dock.explorer_tree.currentIndex().isValid()
    finally:
        outside.unlink(missing_ok=True)
