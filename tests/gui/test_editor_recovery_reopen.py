"""Regressions for explicit recovery on a new Clarify Editor instance."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial

import pytest
from PySide6 import QtCore

from src.editor_recovery import RecoverySnapshotError, UnsavedRecoveryStore
from src.gui import editor_dock as module


@pytest.fixture
def recovery_context(qtbot, tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    root.mkdir()
    recovery_root = tmp_path / "recovery"
    settings = QtCore.QSettings(str(tmp_path / "editor.ini"), QtCore.QSettings.Format.IniFormat)
    settings.setValue("explorer_root_path", str(root))
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=recovery_root),
    )

    widgets = []

    def create():
        dock = module.EditorDock()
        qtbot.addWidget(dock)
        widgets.append(dock)
        return dock

    yield create, root, recovery_root
    for widget in widgets:
        widget.close()
        widget.deleteLater()


def test_new_instance_offers_untitled_and_deduplicates_folder_recovery(recovery_context, qtbot):
    create, root, _recovery_root = recovery_context
    source = root / "saved.txt"
    source.write_text("original", encoding="utf-8")
    first = create()
    assert first.open_file_path(str(source))
    first.tab_widget.currentWidget().editor.setPlainText("dirty saved buffer")
    first._new_file()
    first.tab_widget.currentWidget().editor.setPlainText("untitled buffer")
    assert first.request_tab_close()

    reopened = create()

    assert reopened.tab_widget.count() == 1
    assert reopened.tab_widget.currentWidget().editor.toPlainText() == "dirty saved buffer"
    assert source.read_text(encoding="utf-8") == "original"
    assert not reopened.recovery_offer.isHidden()
    assert reopened.recovery_offer.property("pending_count") == 1

    qtbot.mouseClick(reopened.btn_recovery_offer_recover, QtCore.Qt.LeftButton)

    assert reopened.tab_widget.count() == 2
    assert {reopened.tab_widget.widget(index).editor.toPlainText() for index in range(reopened.tab_widget.count())} == {
        "dirty saved buffer",
        "untitled buffer",
    }
    assert reopened.recovery_offer.isHidden()
    assert source.read_text(encoding="utf-8") == "original"


def test_new_instance_can_explicitly_discard_without_opening_content(recovery_context, qtbot):
    create, _root, recovery_root = recovery_context
    first = create()
    first._new_file()
    first.tab_widget.currentWidget().editor.setPlainText("private draft")
    assert first.request_tab_close()

    reopened = create()
    assert not reopened.recovery_offer.isHidden()
    assert reopened.tab_widget.count() == 0
    qtbot.mouseClick(reopened.btn_recovery_offer_discard, QtCore.Qt.LeftButton)

    assert reopened.recovery_offer.isHidden()
    assert reopened.tab_widget.count() == 0
    assert UnsavedRecoveryStore(recovery_root).list() == []


def test_cancel_keeps_snapshots_and_next_instance_offers_again(recovery_context, qtbot):
    create, _root, recovery_root = recovery_context
    first = create()
    first._new_file()
    first.tab_widget.currentWidget().editor.setPlainText("keep for later")
    assert first.request_tab_close()

    reopened = create()
    qtbot.mouseClick(reopened.btn_recovery_offer_cancel, QtCore.Qt.LeftButton)
    assert reopened.recovery_offer.isHidden()
    assert [item.content for item in UnsavedRecoveryStore(recovery_root).list()] == ["keep for later"]

    later = create()
    assert not later.recovery_offer.isHidden()
    assert later.recovery_offer.property("pending_count") == 1


def test_changed_reference_stays_available_after_failed_inline_recovery(recovery_context, qtbot):
    create, root, recovery_root = recovery_context
    source = root / "saved.txt"
    source.write_text("original", encoding="utf-8")
    store = UnsavedRecoveryStore(recovery_root)
    store.save_reference(
        "saved-reference",
        title=source.name,
        file_path=str(source),
        source_signature=store.source_signature(str(source)),
    )
    source.write_text("changed outside Clarify", encoding="utf-8")

    reopened = create()
    qtbot.mouseClick(reopened.btn_recovery_offer_recover, QtCore.Qt.LeftButton)

    assert reopened.tab_widget.count() == 0
    assert not reopened.recovery_offer.isHidden()
    assert reopened.recovery_offer.property("pending_count") == 1
    assert "1" in reopened.lbl_status.text()
    assert [item.snapshot_id for item in store.list()] == ["saved-reference"]
    assert source.read_text(encoding="utf-8") == "changed outside Clarify"


def test_failed_inline_discard_keeps_offer_and_reports_failure(recovery_context, qtbot, monkeypatch):
    create, _root, recovery_root = recovery_context
    store = UnsavedRecoveryStore(recovery_root)
    store.save("keep", title="draft", content="private draft")
    reopened = create()

    def fail_discard(_snapshot_id):
        raise RecoverySnapshotError("synthetic discard failure")

    monkeypatch.setattr(reopened.recovery_store, "discard", fail_discard)
    qtbot.mouseClick(reopened.btn_recovery_offer_discard, QtCore.Qt.LeftButton)

    assert not reopened.recovery_offer.isHidden()
    assert reopened.recovery_offer.property("pending_count") == 1
    assert "1" in reopened.lbl_status.text()
    assert [item.snapshot_id for item in store.list()] == ["keep"]
