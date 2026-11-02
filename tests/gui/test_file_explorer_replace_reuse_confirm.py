"""Replacement preflight, explicit cache reuse and stale-preview contracts."""

# pylint: disable=no-name-in-module,import-error

from PySide6.QtWidgets import QMessageBox

import src.core.file_explorer_executor as explorer_core
from src.core.file_explorer_executor import SearchMatch, SearchResult
from src.core.file_list_executor import FileListExecutor
from src.i18n.translator import tr
from test_file_explorer_lifecycle import docks
from test_file_explorer_target_scope import set_scope


def _result(path):
    return SearchResult(
        FileListExecutor._get_file_info(str(path)),
        [SearchMatch(1, 0, "needle")],
        1,
    )


def _prepare_file_scope(dock, path):
    set_scope(dock, "file")
    dock.ed_directory.setText(str(path))
    dock.content_panel.set_query("needle")
    dock.replace_panel.set_replacement("changed")


def _pending_plan(dock):
    return {
        "query": "needle",
        "replacement": "changed",
        "options": dict(dock.search_options_panel.get_options()),
        "preserve_case": dock.replace_panel.get_preserve_case(),
        "replace_all": True,
        "target_signature": dock._snapshot_target()[-1],
        "scope": "file",
        "directory": dock._snapshot_target()[2],
        "reuse_previous": False,
    }


def test_folder_scope_enables_read_only_preflight_without_selected_results(docks, tmp_path):
    dock = docks()
    set_scope(dock, "folder")
    dock.ed_directory.setText(str(tmp_path))
    dock.content_panel.set_query("needle")

    assert dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr("file_explorer.replace_ready_scope")


def test_initial_confirmation_never_launches_write_before_preflight(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    _prepare_file_scope(dock, target)
    searches = []
    writes = []
    monkeypatch.setattr(
        dock,
        "_confirm_replace_preflight",
        lambda **_kwargs: (True, False),
    )
    monkeypatch.setattr(dock, "_list_files", lambda: searches.append(True))
    monkeypatch.setattr(dock, "_launch_operation", lambda *args: writes.append(args))

    dock._start_replace(True)

    assert searches == [True]
    assert writes == []
    assert target.read_text(encoding="utf-8") == "needle"


def test_compatible_reuse_is_applied_only_after_explicit_dialog_choice(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    _prepare_file_scope(dock, target)
    signature = dock._snapshot_target()[-1]
    dock._last_content_search_universe = {
        "directory": str(tmp_path),
        "content_query": "needle",
        "paths": [str(target)],
        "target_signature": signature,
    }
    observed = {}

    def confirm(**kwargs):
        observed.update(kwargs)
        return True, True

    monkeypatch.setattr(dock, "_confirm_replace_preflight", confirm)
    monkeypatch.setattr(dock, "_list_files", lambda: None)

    dock._start_replace(True)

    assert observed["compatible_paths"] == [str(target)]
    assert dock.chk_reuse_previous.isChecked()


def test_complete_preflight_requires_separate_final_confirmation(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    _prepare_file_scope(dock, target)
    dock._pending_replace_preflight = _pending_plan(dock)
    questions = []
    launches = []
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda _parent, _title, message, *_args: questions.append(message)
        or QMessageBox.Yes,
    )
    monkeypatch.setattr(
        dock,
        "_launch_operation",
        lambda kind, request: launches.append((kind, request)) or True,
    )

    dock._complete_replace_preflight({
        "files": [_result(target)],
        "stats": {"cancelled": False, "errors": [], "partial": False},
    })

    assert len(questions) == 1
    assert "1" in questions[0]
    assert launches and launches[0][0] == "replace"
    assert launches[0][1]["files"][0].file_info.path == str(target)


def test_partial_error_cancelled_or_empty_preflight_never_writes(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    _prepare_file_scope(dock, target)
    launches = []
    questions = []
    monkeypatch.setattr(dock, "_launch_operation", lambda *args: launches.append(args))
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: questions.append(args) or QMessageBox.Yes,
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "information", lambda *_args: QMessageBox.Ok)

    for files, stats in (
        ([_result(target)], {"cancelled": True, "errors": []}),
        ([_result(target)], {"cancelled": False, "errors": ["read failed"]}),
        ([_result(target)], {"cancelled": False, "errors": [], "partial": True}),
        ([], {"cancelled": False, "errors": []}),
    ):
        dock._pending_replace_preflight = _pending_plan(dock)
        dock._complete_replace_preflight({"files": files, "stats": stats})

    assert questions == []
    assert launches == []
    assert target.read_text(encoding="utf-8") == "needle"


def test_file_changed_during_final_confirmation_blocks_write(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    _prepare_file_scope(dock, target)
    dock._pending_replace_preflight = _pending_plan(dock)
    launches = []
    warnings = []

    def mutate_then_accept(*_args):
        target.write_text("changed offline", encoding="utf-8")
        return QMessageBox.Yes

    monkeypatch.setattr(QMessageBox, "question", mutate_then_accept)
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda _parent, _title, message, *_args: warnings.append(message)
        or QMessageBox.Ok,
    )
    monkeypatch.setattr(dock, "_launch_operation", lambda *args: launches.append(args))

    dock._complete_replace_preflight({
        "files": [_result(target)],
        "stats": {"cancelled": False, "errors": [], "partial": False},
    })

    assert launches == []
    assert warnings == [tr("file_explorer.replace_preflight_stale")]
    assert target.read_text(encoding="utf-8") == "changed offline"


def test_preflight_over_file_budget_is_blocked_before_final_confirmation(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    _prepare_file_scope(dock, target)
    dock._pending_replace_preflight = _pending_plan(dock)
    questions = []
    launches = []
    monkeypatch.setattr(explorer_core, "MAX_REPLACE_FILES", 0)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args: questions.append(args) or QMessageBox.Yes,
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: QMessageBox.Ok)
    monkeypatch.setattr(dock, "_launch_operation", lambda *args: launches.append(args))

    dock._complete_replace_preflight({
        "files": [_result(target)],
        "stats": {"cancelled": False, "errors": [], "partial": False},
    })

    assert questions == []
    assert launches == []
    assert target.read_text(encoding="utf-8") == "needle"
