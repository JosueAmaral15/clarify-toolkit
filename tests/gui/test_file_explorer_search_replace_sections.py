"""Focused GUI contracts for separate File Explorer Search and Replace sections."""

# pylint: disable=no-name-in-module,import-error
# PySide modules are generated dynamically; pytest adds tests/ for shared fixtures.

import pytest
from PySide6.QtWidgets import QMessageBox

from src.i18n.translator import get_translator, tr
from test_file_explorer_lifecycle import docks
from test_file_explorer_replace import populate_dock
from test_file_explorer_target_scope import select_paths, set_scope


def test_search_and_replace_use_distinct_sections(docks):
    dock = docks()

    assert dock.section_search.title() == tr("file_list.section_search")
    assert dock.section_replace.title() == tr("file_list.section_replace")
    assert dock.section_search.isAncestorOf(dock.content_panel)
    assert not dock.section_search.isAncestorOf(dock.replace_panel)
    assert dock.section_replace.isAncestorOf(dock.replace_panel)
    assert dock.section_replace.isCollapsed()
    assert not dock.section_search.isCollapsed()


def test_replace_starts_disabled_without_query_or_result_universe(docks):
    dock = docks()

    assert not dock.replace_panel.btn_replace_first.isEnabled()
    assert not dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr("file_explorer.replace_no_query")
    assert dock.replace_status.accessibleName() == dock.replace_status.text()

    dock.content_panel.set_query("needle")
    assert not dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr("file_explorer.replace_no_targets")


@pytest.mark.parametrize("view", [0, 1])
def test_selected_search_results_enable_replace_with_bounded_counts(
    view, docks, tmp_path,
):
    targets = [tmp_path / "one.txt", tmp_path / "two.txt"]
    for target in targets:
        target.write_text("needle needle", encoding="utf-8")
    dock = docks()
    populate_dock(dock, targets)
    dock.last_was_search = True
    dock.last_search_results = {
        str(targets[0]): [(1, 0, "needle"), (1, 7, "needle")],
        str(targets[1]): [(1, 0, "needle")],
    }
    set_scope(dock, "selected")
    select_paths(dock, view, [targets[0]])
    dock.content_panel.set_query("needle")

    assert dock.replace_panel.btn_replace_first.isEnabled()
    assert dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr(
        "file_explorer.replace_ready_known"
    ).format(files=1, matches=2)

    dock.results_tree.clearSelection()
    dock.table_manager.table.clearSelection()
    assert not dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr("file_explorer.replace_no_targets")


def test_explicit_file_is_a_valid_bounded_universe_without_sibling_discovery(
    docks, tmp_path,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    sibling = tmp_path / "sibling.txt"
    sibling.write_text("needle", encoding="utf-8")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")

    assert dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr(
        "file_explorer.replace_ready_unknown"
    ).format(files=1)
    assert str(sibling) not in dock.replace_status.toolTip()


def test_replace_availability_tracks_operation_gate_and_workspace_modes(
    docks, tmp_path,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")

    for mode in ("compact", "advanced"):
        dock.set_workspace_mode(mode)
        assert dock.section_replace.isVisible()
        assert dock.replace_panel.btn_replace_all.isEnabled()

    dock._active_operation = True
    dock._update_replace_availability()
    assert not dock.replace_panel.btn_replace_all.isEnabled()
    assert dock.replace_status.text() == tr("file_explorer.replace_busy")
    dock._active_operation = False
    dock._update_replace_availability()
    assert dock.replace_panel.btn_replace_all.isEnabled()


def test_runtime_translation_preserves_replace_state(docks, tmp_path):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")
    dock.section_replace.setCollapsed(False)
    translator = get_translator()
    original_language = translator.current_language

    try:
        target_language = "pt_BR" if original_language != "pt_BR" else "en"
        translator.switch_language(target_language)
        assert dock.section_search.title() == translator.get("file_list.section_search")
        assert dock.section_replace.title() == translator.get("file_list.section_replace")
        assert dock.replace_status.text() == translator.get(
            "file_explorer.replace_ready_unknown"
        ).format(files=1)
        assert not dock.section_replace.isCollapsed()
        assert dock.content_panel.get_query() == "needle"
    finally:
        translator.switch_language(original_language)


def test_confirmation_contains_bounded_universe_summary_before_launch(
    docks, tmp_path, monkeypatch,
):
    target = tmp_path / "target.txt"
    target.write_text("needle", encoding="utf-8")
    dock = docks()
    set_scope(dock, "file")
    dock.ed_directory.setText(str(target))
    dock.content_panel.set_query("needle")
    dock.replace_panel.set_replacement("changed")
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

    dock._start_replace(True)

    assert questions and dock.replace_status.text() in questions[0]
    assert str(target) in questions[0]
    assert launches and launches[0][0] == "replace"
