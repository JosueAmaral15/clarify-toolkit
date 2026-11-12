"""External-file reload authorization and consistency regressions."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from unittest.mock import patch

import pytest
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMessageBox

from src.gui.editor_dock import EditorDock, _ExternalReloadError
from src.i18n import get_translator


def _dispose(dock, qapp):
    dock.close()
    dock.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    qapp.processEvents()


def test_external_change_warning_uses_runtime_translation(qapp, tmp_path):
    translator = get_translator()
    previous = translator.current_language
    translator.switch_language("pt_BR")
    path = tmp_path / "externo.txt"
    path.write_text("antes\n", encoding="utf-8")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        path.write_text("depois\n", encoding="utf-8")
        assert dock._check_tab_external_state(tab) == "modified"
        assert dock._show_external_status_for_current_tab()
        assert "alterado no disco" in dock.lbl_status.text().lower()
    finally:
        translator.switch_language(previous)
        _dispose(dock, qapp)


def test_stable_reader_returns_one_bounded_revision(qapp, tmp_path):
    dock = EditorDock()
    try:
        path = tmp_path / "stable.txt"
        path.write_text("stable\n", encoding="utf-8")
        text, signature = dock._read_stable_reload_text(str(path))
        assert text == "stable\n"
        assert signature == dock._file_disk_signature(str(path))
    finally:
        _dispose(dock, qapp)


def test_stable_reader_rejects_revision_changed_during_read(qapp, tmp_path, monkeypatch):
    path = tmp_path / "race.txt"
    path.write_text("one\n", encoding="utf-8")
    dock = EditorDock()
    try:
        actual = dock._file_disk_signature(str(path))
        changed = (actual[0] + 1, *actual[1:])
        signatures = iter((actual, changed))
        monkeypatch.setattr(dock, "_file_disk_signature", lambda _path: next(signatures))
        with pytest.raises(_ExternalReloadError) as caught:
            dock._read_stable_reload_text(str(path))
        assert caught.value.reason == "changed_again"
    finally:
        _dispose(dock, qapp)


def test_watcher_warns_but_never_reloads_without_user_action(qapp, tmp_path):
    path = tmp_path / "watched.txt"
    path.write_text("editor revision\n", encoding="utf-8")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        path.write_text("external revision\n", encoding="utf-8")

        dock._on_watched_file_changed(str(path))

        assert tab.editor.toPlainText() == "editor revision\n"
        assert getattr(tab, "_clarify_external_state") == "modified"
        assert getattr(tab, "_clarify_auto_save_paused_for_external_change") is True
        assert dock.action_reload_from_disk.isEnabled()
    finally:
        _dispose(dock, qapp)


def test_dirty_reload_refusal_preserves_editor_buffer(qapp, tmp_path):
    path = tmp_path / "dirty.txt"
    path.write_text("opened\n", encoding="utf-8")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        tab.editor.setPlainText("local unsaved\n")
        tab.is_modified = True
        path.write_text("external\n", encoding="utf-8")
        dock._check_tab_external_state(tab)

        with patch.object(QMessageBox, "question", return_value=QMessageBox.No):
            assert dock._reload_current_tab_from_disk() is False

        assert tab.editor.toPlainText() == "local unsaved\n"
        assert tab.is_modified is True
        assert getattr(tab, "_clarify_external_state") == "modified"
    finally:
        _dispose(dock, qapp)


@pytest.mark.parametrize(
    ("payload", "limit", "reason"),
    ((b"\xff\xfe", 1024, "decode"), (b"12345", 4, "too_large")),
)
def test_invalid_external_content_never_replaces_buffer(
    qapp, tmp_path, payload, limit, reason
):
    path = tmp_path / f"{reason}.txt"
    path.write_text("original\n", encoding="utf-8")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        dock.MAX_TYPED_FILE_BYTES = limit
        path.write_bytes(payload)
        dock._check_tab_external_state(tab)

        with patch.object(QMessageBox, "warning") as warning:
            assert dock._reload_current_tab_from_disk() is False

        assert tab.editor.toPlainText() == "original\n"
        assert getattr(tab, "_clarify_external_state") == "modified"
        assert warning.call_count == 1
    finally:
        _dispose(dock, qapp)


def test_revision_changed_after_read_aborts_before_buffer_application(
    qapp, tmp_path, monkeypatch
):
    path = tmp_path / "before-apply.txt"
    path.write_text("old\n", encoding="utf-8")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        path.write_text("new\n", encoding="utf-8")
        loaded_signature = dock._file_disk_signature(str(path))
        changed_signature = (loaded_signature[0] + 1, *loaded_signature[1:])
        monkeypatch.setattr(
            dock,
            "_read_stable_reload_text",
            lambda _path: ("new\n", loaded_signature),
        )
        monkeypatch.setattr(
            dock, "_file_disk_signature", lambda _path: changed_signature
        )

        with patch.object(QMessageBox, "warning"):
            assert dock._reload_current_tab_from_disk() is False

        assert tab.editor.toPlainText() == "old\n"
        assert getattr(tab, "_clarify_external_state") == "modified"
    finally:
        _dispose(dock, qapp)


def test_change_immediately_after_apply_remains_external(qapp, tmp_path, monkeypatch):
    path = tmp_path / "after-apply.txt"
    path.write_text("old\n", encoding="utf-8")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        path.write_text("loaded\n", encoding="utf-8")
        loaded_signature = dock._file_disk_signature(str(path))
        changed_signature = (loaded_signature[0] + 1, *loaded_signature[1:])
        monkeypatch.setattr(
            dock,
            "_read_stable_reload_text",
            lambda _path: ("loaded\n", loaded_signature),
        )
        signatures = iter((loaded_signature, changed_signature))
        monkeypatch.setattr(
            dock, "_file_disk_signature", lambda _path: next(signatures)
        )

        assert dock._reload_current_tab_from_disk() is True

        assert tab.editor.toPlainText() == "loaded\n"
        assert getattr(tab, "_clarify_external_state") == "modified"
        assert "external" in dock.tab_widget.tabText(
            dock.tab_widget.currentIndex()
        )
    finally:
        _dispose(dock, qapp)


def test_reload_preserves_cursor_selection_and_utf8_text_format(qapp, tmp_path):
    path = tmp_path / "formatted.txt"
    path.write_bytes(b"\xef\xbb\xbffirst\r\nsecond\r\n")
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        cursor = tab.editor.textCursor()
        cursor.setPosition(2)
        cursor.setPosition(7, QTextCursor.KeepAnchor)
        tab.editor.setTextCursor(cursor)

        path.write_bytes(b"\xef\xbb\xbfchanged\r\nsecond\r\n")
        dock._check_tab_external_state(tab)
        assert dock._reload_current_tab_from_disk() is True

        reloaded_cursor = tab.editor.textCursor()
        assert reloaded_cursor.anchor() == 2
        assert reloaded_cursor.position() == 7
        assert tab.editor.toPlainText() == "changed\nsecond\n"
        tab.editor.insertPlainText("!")
        assert tab.save_file()
        assert path.read_bytes().startswith(b"\xef\xbb\xbf")
        assert b"\r\n" in path.read_bytes()
        assert b"\n" not in path.read_bytes().replace(b"\r\n", b"")
    finally:
        _dispose(dock, qapp)


def test_json_reload_preserves_utf8_bom_and_crlf(qapp, tmp_path):
    path = tmp_path / "formatted.json"
    path.write_bytes(b'\xef\xbb\xbf{\r\n  "value": 1\r\n}\r\n')
    dock = EditorDock()
    try:
        assert dock.open_file_path(str(path))
        tab = dock.tab_widget.currentWidget()
        path.write_bytes(b'\xef\xbb\xbf{\r\n  "value": 2\r\n}\r\n')
        dock._check_tab_external_state(tab)

        assert dock._reload_current_tab_from_disk() is True
        assert '"value": 2' in tab.editor.toPlainText()
        assert tab.save_file()[0] is True
        payload = path.read_bytes()
        assert payload.startswith(b"\xef\xbb\xbf")
        assert b"\r\n" in payload
        assert b"\n" not in payload.replace(b"\r\n", b"")
    finally:
        _dispose(dock, qapp)
