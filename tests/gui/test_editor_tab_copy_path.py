"""Focused regressions for safe path copying from Clarify Editor file tabs."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

import threading
from functools import partial

from PySide6 import QtCore

from src.gui import editor_dock as module


def make_dock(qtbot, tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(root))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    return dock, root


def actions_by_id(menu):
    return {action.data(): action for action in menu.actions() if not action.isSeparator()}


def copy_actions(dock, tab):
    menu = dock._build_tab_context_menu(dock.tab_widget.indexOf(tab))
    actions = actions_by_id(menu)
    return menu, actions["copy_absolute"], actions["copy_relative"]


def test_tab_menu_copies_clicked_file_absolute_and_canonical_relative_path(qtbot, tmp_path, monkeypatch):
    dock, root = make_dock(qtbot, tmp_path, monkeypatch)
    folder = root / "folder"
    folder.mkdir()
    first = folder / "first.txt"
    second = root / "second.txt"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")
    assert dock.open_file_path(str(first))
    first_tab = dock.tab_widget.currentWidget()
    assert dock.open_file_path(str(second))

    menu, absolute, relative = copy_actions(dock, first_tab)
    assert menu.toolTipsVisible()
    assert absolute.isEnabled()
    assert relative.isEnabled()
    absolute.trigger()
    assert module.QApplication.clipboard().text() == str(first)
    relative.trigger()
    assert module.QApplication.clipboard().text() == "folder/first.txt"


def test_tab_menu_disables_untitled_and_temporary_notes_with_specific_reasons(qtbot, tmp_path, monkeypatch):
    dock, root = make_dock(qtbot, tmp_path, monkeypatch)
    untitled = dock.load_generated_content("draft", "Untitled.txt")
    menu, absolute, relative = copy_actions(dock, untitled)
    assert menu.toolTipsVisible()
    assert not absolute.isEnabled()
    assert not relative.isEnabled()
    assert absolute.toolTip() == module.tr("editor.path_copy_unavailable_untitled")
    assert relative.statusTip() == absolute.toolTip()

    assert dock._save_current_as_temp_note("Reminder")
    menu, absolute, relative = copy_actions(dock, untitled)
    assert not absolute.isEnabled()
    assert not relative.isEnabled()
    assert absolute.toolTip() == module.tr("editor.path_copy_unavailable_temp_note")
    assert relative.statusTip() == absolute.toolTip()

    file_path = root / "saved.txt"
    file_path.write_text("saved", encoding="utf-8")
    assert dock.open_file_path(str(file_path))
    saved_tab = dock.tab_widget.currentWidget()
    assert dock._save_current_as_temp_note("Saved reminder")
    _menu, absolute, relative = copy_actions(dock, saved_tab)
    assert not absolute.isEnabled() and not relative.isEnabled()
    assert absolute.toolTip() == module.tr("editor.path_copy_unavailable_temp_note")


def test_tab_menu_disables_missing_external_and_symlink_escape_paths(qtbot, tmp_path, monkeypatch):
    dock, root = make_dock(qtbot, tmp_path, monkeypatch)
    missing = root / "missing.txt"
    missing.write_text("missing", encoding="utf-8")
    assert dock.open_file_path(str(missing))
    missing_tab = dock.tab_widget.currentWidget()
    missing.unlink()
    menu, absolute, relative = copy_actions(dock, missing_tab)
    assert menu.toolTipsVisible()
    assert not absolute.isEnabled() and not relative.isEnabled()
    assert absolute.toolTip() == module.tr("editor.path_copy_unavailable_missing")

    external = tmp_path / "external.txt"
    external.write_text("external", encoding="utf-8")
    assert dock.open_file_path(str(external))
    external_tab = dock.tab_widget.currentWidget()
    _menu, absolute, relative = copy_actions(dock, external_tab)
    assert not absolute.isEnabled() and not relative.isEnabled()
    assert absolute.toolTip() == module.tr("editor.path_copy_unavailable_external")

    target = tmp_path / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = root / "escape.txt"
    link.symlink_to(target)
    assert dock.open_file_path(str(link))
    link_tab = dock.tab_widget.currentWidget()
    _menu, absolute, relative = copy_actions(dock, link_tab)
    assert not absolute.isEnabled() and not relative.isEnabled()
    assert absolute.toolTip() == module.tr("editor.path_copy_unavailable_symlink")


def test_copy_path_rejects_non_gui_thread_without_touching_clipboard(qtbot, tmp_path, monkeypatch):
    dock, root = make_dock(qtbot, tmp_path, monkeypatch)
    module.QApplication.clipboard().setText("preserve")
    results = []
    worker = threading.Thread(target=lambda: results.append(dock._copy_path(str(root / "file.txt"))))
    worker.start()
    worker.join(timeout=2)

    assert not worker.is_alive()
    assert results == [False]
    assert module.QApplication.clipboard().text() == "preserve"


def test_tab_path_is_revalidated_when_the_action_is_triggered(qtbot, tmp_path, monkeypatch):
    dock, root = make_dock(qtbot, tmp_path, monkeypatch)
    source = root / "vanishing.txt"
    source.write_text("content", encoding="utf-8")
    assert dock.open_file_path(str(source))
    tab = dock.tab_widget.currentWidget()
    _menu, absolute, relative = copy_actions(dock, tab)
    assert absolute.isEnabled() and relative.isEnabled()
    module.QApplication.clipboard().setText("preserve")
    source.unlink()

    absolute.trigger()

    assert module.QApplication.clipboard().text() == "preserve"
    assert dock.lbl_status.text() == module.tr("editor.path_copy_unavailable_missing")
