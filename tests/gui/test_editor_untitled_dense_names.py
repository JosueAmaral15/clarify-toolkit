"""Regressions for dense visible Untitled names and stable buffer identity."""

# pylint: disable=no-name-in-module  # PySide modules are generated dynamically.

from functools import partial

from PySide6 import QtCore

from src.gui import editor_dock as module


def make_dock(qtbot, tmp_path, monkeypatch):
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.IniFormat)
    settings.setValue("explorer_root_path", str(tmp_path))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(module.UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    monkeypatch.setattr(
        module,
        "TemporaryNoteStore",
        partial(module.TemporaryNoteStore, root=tmp_path / "notes"),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    return dock


def tab_titles(dock):
    return [dock.tab_widget.widget(index).get_tab_title() for index in range(dock.tab_widget.count())]


def visible_titles(dock):
    return [dock.tab_widget.tabText(index) for index in range(dock.tab_widget.count())]


def test_close_and_reorder_keep_dense_names_and_stable_identities(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    for _unused in range(3):
        dock._new_file()
    tabs = [dock.tab_widget.widget(index) for index in range(3)]
    find_identities = [dock._find_buffer_identity(tab) for tab in tabs]

    assert tab_titles(dock) == ["Untitled", "Untitled-2", "Untitled-3"]
    assert dock._close_tab(1)
    assert tab_titles(dock) == ["Untitled", "Untitled-2"]

    identities = [tab._clarify_buffer_identity for tab in tabs]
    assert len(set(identities)) == 3

    active = dock.tab_widget.currentWidget()
    dock.tab_widget.tabBar().moveTab(1, 0)
    assert tab_titles(dock) == ["Untitled", "Untitled-2"]
    assert dock.tab_widget.currentWidget() is active
    assert [dock._find_buffer_identity(dock.tab_widget.widget(index)) for index in range(2)] == [
        find_identities[2],
        find_identities[0],
    ]
    assert [dock.tab_widget.widget(index)._clarify_buffer_identity for index in range(2)] == [
        identities[2],
        identities[0],
    ]


def test_new_tab_reuses_current_dense_count_after_close(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    for _unused in range(3):
        dock._new_file()
    assert dock._close_tab(2)
    assert dock._close_tab(1)

    dock._new_file()

    assert tab_titles(dock) == ["Untitled", "Untitled-2"]


def test_dirty_markers_follow_buffers_while_visible_names_change(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    dock._new_file()
    first = dock.tab_widget.currentWidget()
    first.editor.insertPlainText("first")
    dock._new_file()
    second = dock.tab_widget.currentWidget()
    second.editor.insertPlainText("second")

    assert visible_titles(dock) == ["Untitled *", "Untitled-2 *"]
    dock.tab_widget.tabBar().moveTab(1, 0)
    assert visible_titles(dock) == ["Untitled *", "Untitled-2 *"]
    assert dock.tab_widget.widget(0) is second
    assert dock.tab_widget.widget(1) is first


def test_save_as_removes_only_saved_buffer_from_dense_names(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    for _unused in range(3):
        dock._new_file()
    tabs = [dock.tab_widget.widget(index) for index in range(3)]
    saved_identity = tabs[1]._clarify_buffer_identity
    destination = tmp_path / "saved.txt"
    dock.tab_widget.setCurrentWidget(tabs[1])
    monkeypatch.setattr(
        module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(destination), ""),
    )

    assert dock._save_file_as()

    assert tab_titles(dock) == ["Untitled", "saved.txt", "Untitled-2"]
    assert tabs[1]._clarify_buffer_identity == saved_identity
    assert destination.read_text(encoding="utf-8") == ""


def test_temporary_note_title_replaces_untitled_and_renumbers_remaining(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    dock._new_file()
    note_tab = dock.tab_widget.currentWidget()
    note_tab.editor.insertPlainText("remember")
    dock._new_file()
    other_tab = dock.tab_widget.currentWidget()
    note_identity = note_tab._clarify_buffer_identity
    dock.tab_widget.setCurrentWidget(note_tab)

    assert dock._save_current_as_temp_note("Scratch")

    assert tab_titles(dock) == ["Scratch", "Untitled"]
    assert note_tab._clarify_buffer_identity == note_identity
    assert other_tab.get_tab_title() == "Untitled"
    assert dock.temp_note_store.get(note_tab._clarify_temp_note_id).title == "Scratch"


def test_sparse_legacy_recovery_titles_restore_as_dense_untitled_buffers(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    dock.recovery_store.save("old-17", title="Untitled-17", content="seventeen", extension=".txt")
    dock.recovery_store.save("old-22", title="Untitled-22", content="twenty-two", extension=".txt")
    snapshots = {item.snapshot_id: item for item in dock.recovery_store.list()}

    first = dock._restore_recovery_snapshot(snapshots["old-17"])
    second = dock._restore_recovery_snapshot(snapshots["old-22"])

    assert tab_titles(dock) == ["Untitled", "Untitled-2"]
    assert first._clarify_recovery_id == "old-17"
    assert second._clarify_recovery_id == "old-22"
    assert first._clarify_buffer_identity != second._clarify_buffer_identity
    assert first.editor.toPlainText() == "seventeen"
    assert second.editor.toPlainText() == "twenty-two"


def test_reorder_updates_split_title_without_changing_shared_document(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    dock._new_file()
    dock._new_file()
    split_tab = dock.tab_widget.currentWidget()
    document = split_tab.editor.document()
    assert dock._show_split_view(split_tab, QtCore.Qt.Horizontal)
    assert dock.split_title.text() == "Untitled-2"

    dock.tab_widget.tabBar().moveTab(1, 0)

    assert dock.split_title.text() == "Untitled"
    assert dock.split_editor.document() is document
    assert dock._split_source_tab is split_tab


def test_explicit_generated_names_json_and_folder_identity_are_not_rewritten(qtbot, tmp_path, monkeypatch):
    dock = make_dock(qtbot, tmp_path, monkeypatch)
    dock._new_file(edit_only=True)
    untitled = dock.tab_widget.currentWidget()
    generated = dock.load_generated_content("{}", "report.json", extension=".json")

    assert untitled.get_tab_title() == "Untitled"
    assert generated.get_tab_title() == "report.json"
    assert "report.json" in dock.tab_widget.tabText(dock.tab_widget.indexOf(generated))
    assert dock._tab_folder_identity(untitled) == ""
    assert dock._tab_folder_root(untitled) == ""
