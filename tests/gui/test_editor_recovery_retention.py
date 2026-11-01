"""Regressions for recovery retention defaults and empty-state reporting."""

# pylint: disable=no-name-in-module  # PySide6 exposes Qt classes dynamically.

from functools import partial
import json
from datetime import datetime, timedelta, timezone

from PySide6 import QtCore

from src.editor_recovery import UnsavedRecoveryStore
from src.gui import editor_dock as module


def _create_dock(qtbot, tmp_path, monkeypatch, *, retention=None):
    settings = QtCore.QSettings(
        str(tmp_path / "editor.ini"), QtCore.QSettings.Format.IniFormat
    )
    settings.setValue("explorer_root_path", str(tmp_path))
    if retention is not None:
        settings.setValue("recovery_retention_hours", retention)
    monkeypatch.setattr(QtCore, "QSettings", lambda *args: settings)
    monkeypatch.setattr(
        module,
        "UnsavedRecoveryStore",
        partial(UnsavedRecoveryStore, root=tmp_path / "recovery"),
    )
    dock = module.EditorDock()
    qtbot.addWidget(dock)
    return dock


def test_new_profile_defaults_to_thirty_days(qtbot, tmp_path, monkeypatch):
    dock = _create_dock(qtbot, tmp_path, monkeypatch)

    assert dock.recovery_retention_hours == 30 * 24
    assert dock.recovery_store.retention_hours == 30 * 24


def test_existing_retention_preference_is_preserved(qtbot, tmp_path, monkeypatch):
    dock = _create_dock(qtbot, tmp_path, monkeypatch, retention=24)

    assert dock.recovery_retention_hours == 24
    assert dock.recovery_store.retention_hours == 24


def test_pending_inventory_counts_snapshots_already_open(qtbot, tmp_path, monkeypatch):
    dock = _create_dock(qtbot, tmp_path, monkeypatch)
    dock.recovery_store.save("open", title="Draft", content="private")
    tab = dock.load_generated_content("private", "Recovered Draft")
    setattr(tab, "_clarify_recovery_id", "open")

    assert dock._pending_recovery_snapshots() == []
    assert dock._recovery_already_open_count == 1


def test_pending_inventory_reports_expiration_and_corruption(
    qtbot, tmp_path, monkeypatch
):
    dock = _create_dock(qtbot, tmp_path, monkeypatch)
    dock.recovery_store.save("old", title="Old", content="private")
    path = tmp_path / "recovery" / "old.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["updated_at"] = (
        datetime.now(timezone.utc) - timedelta(days=31)
    ).isoformat()
    path.write_text(json.dumps(data), encoding="utf-8")
    (tmp_path / "recovery" / "corrupt.json").write_text(
        "not json", encoding="utf-8"
    )

    assert dock._pending_recovery_snapshots() == []
    assert dock._last_recovery_prune_report.expired == 1
    assert dock._last_recovery_prune_report.invalid == 1

    # A later explicit inventory must retain the reasons pruned at startup.
    assert dock._pending_recovery_snapshots() == []
    message = dock._recovery_empty_message()
    assert module.tr("editor.recovery_reason_expired").format(count=1) in message
    assert module.tr("editor.recovery_reason_invalid").format(count=1) in message


def test_explicit_recovery_reports_inventory_io_failure(
    qtbot, tmp_path, monkeypatch
):
    dock = _create_dock(qtbot, tmp_path, monkeypatch)

    def fail_inventory():
        raise OSError("synthetic inventory failure")

    monkeypatch.setattr(dock.recovery_store, "list_with_report", fail_inventory)
    monkeypatch.setattr(
        module.QMessageBox,
        "warning",
        lambda *_args: (_ for _ in ()).throw(AssertionError("unexpected modal")),
    )

    dock._show_recovery_dialog()

    assert dock.lbl_status.text() == module.tr("editor.recovery_store_unavailable")
