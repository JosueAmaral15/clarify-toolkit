import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QLabel

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.gui.panels.results_tree import (
    AI_EXPLAIN_MAX_BYTES_PER_FILE,
    AI_EXPLAIN_MAX_FILES,
    AI_EXPLAIN_MAX_PROMPT_CHARS,
    AI_EXPLAIN_MAX_SNIPPET_CHARS,
    ITEM_TYPE_ROOT,
    ITEM_TYPE_ROLE,
    RESULT_PATH_ROLE,
    RESULTS_JSON_SNIPPET_MAX_CHARS,
    ResultsTree,
)
from src.gui.ai_processor_dock import AIProcessorDock


def _qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _top_level_by_type(tree: ResultsTree, item_type: str):
    for index in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(index)
        if item.data(0, ITEM_TYPE_ROLE) == item_type:
            return item
    raise AssertionError(f"top-level item not found: {item_type}")


def _child_by_text(parent, text: str):
    for index in range(parent.childCount()):
        child = parent.child(index)
        if child.text(0) == text:
            return child
    raise AssertionError(f"child not found: {text}")


class _FakeAIProcessor:
    def __init__(self):
        self.calls = []

    def prepare_file_explorer_explanation(self, prompt, file_paths, max_bytes):
        self.calls.append((prompt, file_paths, max_bytes))
        return len(file_paths)


class _FakeMainWindow:
    def __init__(self, ai_processor):
        self.dock_ai_processor = ai_processor
        self.show_count = 0

    def _show_ai_processor(self):
        self.show_count += 1


class _FakeTextValue:
    def __init__(self):
        self.value = ""

    def setText(self, value):
        self.value = value


class _FakePlainTextValue:
    def __init__(self):
        self.value = ""

    def setPlainText(self, value):
        self.value = value


class _FakeCheckValue:
    def __init__(self):
        self.checked = None

    def setChecked(self, checked):
        self.checked = checked


class _FakeSpinValue:
    def __init__(self):
        self.value = None

    def setValue(self, value):
        self.value = value


class _FakeButtonValue:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, enabled):
        self.enabled = enabled


class _FakePathEntry:
    def __init__(self):
        self.ed_path = _FakeTextValue()
        self.chk_is_file = _FakeCheckValue()
        self.btn_remove = _FakeButtonValue()
        self.lbl_path = _FakeTextValue()
        self.path_number = None
        self.deleted = False

    def deleteLater(self):
        self.deleted = True


class _FakeAIProcessorDockForPrepare:
    def __init__(self):
        self.path_entries = []
        self.ed_prompt = _FakePlainTextValue()
        self.spin_max_bytes = _FakeSpinValue()
        self.chk_line_by_line = _FakeCheckValue()
        self.text_results = _FakePlainTextValue()

    def _add_path_entry(self):
        self.path_entries.append(_FakePathEntry())

    def clear_results(self, widget):
        widget.value = ""

    def append_result(self, widget, text):
        widget.value += text


def test_populate_builds_unicode_hierarchy_with_base_path(tmp_path):
    _qapp()
    base = tmp_path / "raiz_acao" / "raiz_ação"
    folder = base / "coração"
    folder.mkdir(parents=True)
    file_path = folder / "maçã_ção.txt"
    file_path.write_text("Olá ação", encoding="utf-8")

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, "Olá ação")]}, base_path=str(base))

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    assert root.text(0).endswith("raiz_ação")
    assert root.text(0).startswith(("Root:", "Raiz:"))
    assert root.toolTip(0) == str(base)

    folder_item = _child_by_text(root, "coração")
    file_item = _child_by_text(folder_item, "maçã_ção.txt")
    match_item = file_item.child(0)

    assert file_item.text(0) == "maçã_ção.txt"
    assert file_item.data(0, RESULT_PATH_ROLE) == str(file_path)
    assert "Olá ação" in match_item.text(0)
    assert match_item.data(0, RESULT_PATH_ROLE) == str(file_path)


def test_incremental_add_keeps_unicode_root_after_clear(tmp_path):
    _qapp()
    base = tmp_path / "projeto_ação"
    folder = base / "dados"
    folder.mkdir(parents=True)
    file_path = folder / "configuração.json"
    file_path.write_text("{}", encoding="utf-8")

    tree = ResultsTree()
    tree.set_base_path(str(base))
    tree.clear()
    tree.add_file_result(str(file_path), [(2, 4, '"ação": true')])

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    folder_item = _child_by_text(root, "dados")
    file_item = _child_by_text(folder_item, "configuração.json")

    assert root.text(0).endswith("projeto_ação")
    assert root.text(0).startswith(("Root:", "Raiz:"))
    assert file_item.data(0, RESULT_PATH_ROLE) == str(file_path)
    assert tree.get_matches_data()[str(file_path)] == [(2, 4, '"ação": true')]


def test_copy_selected_uses_full_unicode_path_not_visible_label(tmp_path):
    app = _qapp()
    base = tmp_path / "raiz_ação"
    folder = base / "coração"
    folder.mkdir(parents=True)
    file_path = folder / "maçã_ção.txt"
    file_path.write_text("Olá ação", encoding="utf-8")

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, "Olá ação")]}, base_path=str(base))

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    file_item = _child_by_text(_child_by_text(root, "coração"), "maçã_ção.txt")
    assert file_item.text(0) == "maçã_ção.txt"

    file_item.setSelected(True)
    tree._copy_selected()

    assert app.clipboard().text().strip() == str(file_path)

    tree.clearSelection()
    match_item = file_item.child(0)
    match_item.setSelected(True)
    tree._copy_selected()

    copied = app.clipboard().text()
    assert str(file_path) in copied
    assert "1:0  Olá ação" in copied


def test_copy_all_content_copies_textual_result_files(tmp_path):
    app = _qapp()
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("alpha", encoding="utf-8")
    second.write_text("coração", encoding="utf-8")

    tree = ResultsTree()
    tree.populate(
        {
            str(first): [(1, 0, "alpha")],
            str(second): [(1, 0, "coração")],
        },
        base_path=str(tmp_path),
    )

    tree._copy_all_content()

    copied = app.clipboard().text()
    assert f"===== {first} =====\nalpha" in copied
    assert f"===== {second} =====\ncoração" in copied


def test_copy_all_content_skips_unsafe_or_oversized_results(tmp_path):
    ok_file = tmp_path / "ok.txt"
    binary_file = tmp_path / "binary.bin"
    directory = tmp_path / "folder"
    large_file = tmp_path / "large.txt"
    total_limited_file = tmp_path / "total.txt"
    missing_file = tmp_path / "missing.txt"

    ok_file.write_text("ok", encoding="utf-8")
    binary_file.write_bytes(b"\x00abc")
    directory.mkdir()
    large_file.write_text("x" * 20, encoding="utf-8")
    total_limited_file.write_text("abcd", encoding="utf-8")

    tree = ResultsTree()
    tree.populate(
        {
            str(ok_file): [(1, 0, "ok")],
            str(binary_file): [(1, 0, "abc")],
            str(directory): [(1, 0, "folder")],
            str(missing_file): [(1, 0, "missing")],
            str(large_file): [(1, 0, "large")],
            str(total_limited_file): [(1, 0, "total")],
        },
        base_path=str(tmp_path),
    )

    text, stats = tree._build_all_content_clipboard_text(max_file_bytes=10, max_total_bytes=5)

    assert f"===== {ok_file} =====\nok" in text
    assert str(binary_file) not in text
    assert str(large_file) not in text
    assert str(total_limited_file) not in text
    assert stats["copied"] == 1
    assert stats["skipped_binary"] == 1
    assert stats["skipped_directory"] == 1
    assert stats["skipped_missing"] == 1
    assert stats["skipped_size"] == 1
    assert stats["skipped_total_limit"] == 1
    assert "skipped 5" in tree._format_copy_content_status(stats)


def test_export_to_json_data_includes_metadata_matches_and_missing_paths(tmp_path):
    _qapp()
    file_path = tmp_path / "result.txt"
    missing_path = tmp_path / "missing.txt"
    file_path.write_text("alpha", encoding="utf-8")

    tree = ResultsTree()
    tree.populate(
        {
            str(file_path): [(2, 3, "alpha")],
            str(missing_path): [(1, 0, "missing")],
        },
        base_path=str(tmp_path),
    )

    data = tree.export_to_json_data()
    files_by_path = {entry["path"]: entry for entry in data["files"]}

    assert data["format"] == "clarify.file_explorer.results"
    assert data["version"] == 1
    assert data["base_path"] == str(tmp_path)
    assert data["total_files"] == 2
    assert data["total_matches"] == 2

    file_entry = files_by_path[str(file_path)]
    assert file_entry["exists"] is True
    assert file_entry["type"] == "file"
    assert file_entry["size_bytes"] == len("alpha")
    assert "modified_at" in file_entry
    assert file_entry["matches"] == [
        {"line": 2, "column": 3, "snippet": "alpha", "snippet_truncated": False}
    ]

    missing_entry = files_by_path[str(missing_path)]
    assert missing_entry["exists"] is False
    assert missing_entry["type"] == "missing"
    assert missing_entry["matches_count"] == 1


def test_export_to_json_data_truncates_large_snippets(tmp_path):
    _qapp()
    file_path = tmp_path / "large-snippet.txt"
    file_path.write_text("body", encoding="utf-8")
    snippet = "x" * (RESULTS_JSON_SNIPPET_MAX_CHARS + 10)

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, snippet)]}, base_path=str(tmp_path))

    exported_snippet = tree.export_to_json_data()["files"][0]["matches"][0]

    assert len(exported_snippet["snippet"]) == RESULTS_JSON_SNIPPET_MAX_CHARS
    assert exported_snippet["snippet_truncated"] is True


def test_copy_results_as_json_sets_clipboard(tmp_path):
    app = _qapp()
    file_path = tmp_path / "result.txt"
    file_path.write_text("alpha", encoding="utf-8")

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, "alpha")]}, base_path=str(tmp_path))

    tree._copy_results_as_json()

    copied = json.loads(app.clipboard().text())
    assert copied["total_files"] == 1
    assert copied["files"][0]["path"] == str(file_path)


def test_export_results_as_json_writes_file(tmp_path, monkeypatch):
    _qapp()
    file_path = tmp_path / "result.txt"
    output_path = tmp_path / "results.json"
    file_path.write_text("alpha", encoding="utf-8")

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, "alpha")]}, base_path=str(tmp_path))

    monkeypatch.setattr(
        "src.gui.panels.results_tree.QFileDialog.getSaveFileName",
        lambda *_args, **_kwargs: (str(output_path), "JSON Files (*.json)"),
    )

    tree._export_results_as_json()

    exported = json.loads(output_path.read_text(encoding="utf-8"))
    assert exported["format"] == "clarify.file_explorer.results"
    assert exported["files"][0]["matches"][0]["snippet"] == "alpha"


def test_prepare_ai_explanation_filters_binary_and_prepares_ai_processor(tmp_path):
    _qapp()
    text_file = tmp_path / "text.txt"
    binary_file = tmp_path / "binary.bin"
    directory = tmp_path / "folder"
    missing_file = tmp_path / "missing.txt"
    text_file.write_text("alpha", encoding="utf-8")
    binary_file.write_bytes(b"\x00binary")
    directory.mkdir()

    fake_ai = _FakeAIProcessor()
    fake_main = _FakeMainWindow(fake_ai)
    tree = ResultsTree(main_window=fake_main)
    status = QLabel()
    tree.set_status_label(status)
    tree.populate(
        {
            str(text_file): [(3, 4, "alpha match")],
            str(binary_file): [(1, 0, "binary")],
            str(directory): [(1, 0, "directory")],
            str(missing_file): [(1, 0, "missing")],
        },
        base_path=str(tmp_path),
    )

    tree._prepare_ai_explanation()

    assert fake_main.show_count == 1
    assert len(fake_ai.calls) == 1
    prompt, file_paths, max_bytes = fake_ai.calls[0]
    assert file_paths == [str(text_file)]
    assert max_bytes == AI_EXPLAIN_MAX_BYTES_PER_FILE
    assert "Explain these File Explorer search results." in prompt
    assert str(text_file) in prompt
    assert "alpha match" in prompt
    assert str(binary_file) not in prompt
    assert "Prepared AI explanation for 1 file(s)" in status.text()
    assert "binary 1" in status.text()
    assert "dirs 1" in status.text()
    assert "missing 1" in status.text()


def test_prepare_ai_explanation_uses_selection_scope(tmp_path):
    _qapp()
    selected_file = tmp_path / "selected.txt"
    other_file = tmp_path / "other.txt"
    selected_file.write_text("selected", encoding="utf-8")
    other_file.write_text("other", encoding="utf-8")

    fake_ai = _FakeAIProcessor()
    tree = ResultsTree(main_window=_FakeMainWindow(fake_ai))
    tree.populate(
        {
            str(selected_file): [(1, 0, "selected")],
            str(other_file): [(1, 0, "other")],
        },
        base_path=str(tmp_path),
    )

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    _child_by_text(root, "selected.txt").setSelected(True)

    tree._prepare_ai_explanation()

    prompt, file_paths, _max_bytes = fake_ai.calls[0]
    assert file_paths == [str(selected_file)]
    assert str(selected_file) in prompt
    assert str(other_file) not in prompt
    assert "selected File Explorer results" in prompt


def test_build_ai_explanation_prompt_is_bounded(tmp_path):
    _qapp()
    matches = {}
    long_snippet = "x" * (AI_EXPLAIN_MAX_SNIPPET_CHARS + 20)
    for index in range(AI_EXPLAIN_MAX_FILES + 3):
        path = tmp_path / f"file-{index}.txt"
        path.write_text("body", encoding="utf-8")
        matches[str(path)] = [
            (line, 1, long_snippet)
            for line in range(1, 25)
        ]

    tree = ResultsTree()
    tree.populate(matches, base_path=str(tmp_path))
    candidates, stats = tree._prepare_ai_explanation_candidates(list(matches.keys()))
    prompt = tree._build_ai_explanation_prompt(candidates, stats, "all")

    assert len(candidates) == AI_EXPLAIN_MAX_FILES
    assert stats["skipped_file_limit"] == 3
    assert len(prompt) <= AI_EXPLAIN_MAX_PROMPT_CHARS + len("\n\nPrompt context truncated.")
    assert "[truncated]" in prompt
    assert "additional match(es) omitted" in prompt


def test_ai_processor_prepare_file_explorer_explanation_sets_prompt_paths_and_limits():
    fake_dock = _FakeAIProcessorDockForPrepare()

    prepared = AIProcessorDock.prepare_file_explorer_explanation(
        fake_dock,
        "Explain this",
        ["/tmp/a.txt", "/tmp/b.txt"],
        12345,
    )

    assert prepared == 2
    assert fake_dock.ed_prompt.value == "Explain this"
    assert fake_dock.spin_max_bytes.value == 12345
    assert fake_dock.chk_line_by_line.checked is False
    assert len(fake_dock.path_entries) == 2
    assert fake_dock.path_entries[0].ed_path.value == "/tmp/a.txt"
    assert fake_dock.path_entries[1].ed_path.value == "/tmp/b.txt"
    assert fake_dock.path_entries[0].chk_is_file.checked is True
    assert fake_dock.path_entries[1].chk_is_file.checked is True
    assert "Prepared from File Explorer" in fake_dock.text_results.value


def test_delete_result_files_deletes_only_selected_file(tmp_path, monkeypatch):
    _qapp()
    selected_file = tmp_path / "delete-me.txt"
    kept_file = tmp_path / "keep-me.txt"
    selected_file.write_text("remove", encoding="utf-8")
    kept_file.write_text("keep", encoding="utf-8")

    tree = ResultsTree()
    tree.populate(
        {
            str(selected_file): [(1, 0, "remove")],
            str(kept_file): [(1, 0, "keep")],
        },
        base_path=str(tmp_path),
    )

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    selected_item = _child_by_text(root, "delete-me.txt")
    selected_item.setSelected(True)

    def fake_trash(path):
        Path(path).unlink()
        return True

    monkeypatch.setattr(tree, "_confirm_delete_result_files", lambda _paths, _stats, _scope: True)
    monkeypatch.setattr(tree, "_move_result_file_to_trash", fake_trash)

    tree._delete_result_files()

    assert not selected_file.exists()
    assert kept_file.exists()
    assert str(selected_file) not in tree.get_matches_data()
    assert str(kept_file) in tree.get_matches_data()


def test_delete_result_files_cancel_keeps_files(tmp_path, monkeypatch):
    _qapp()
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first", encoding="utf-8")
    second.write_text("second", encoding="utf-8")

    tree = ResultsTree()
    tree.populate(
        {
            str(first): [(1, 0, "first")],
            str(second): [(1, 0, "second")],
        },
        base_path=str(tmp_path),
    )

    trash_calls = []
    monkeypatch.setattr(tree, "_confirm_delete_result_files", lambda _paths, _stats, _scope: False)
    monkeypatch.setattr(tree, "_move_result_file_to_trash", lambda path: trash_calls.append(path) or True)

    tree._delete_result_files()

    assert first.exists()
    assert second.exists()
    assert trash_calls == []
    assert str(first) in tree.get_matches_data()
    assert str(second) in tree.get_matches_data()


def test_delete_result_files_reports_permission_failure(tmp_path, monkeypatch):
    _qapp()
    blocked_file = tmp_path / "blocked.txt"
    blocked_file.write_text("blocked", encoding="utf-8")

    tree = ResultsTree()
    status = QLabel()
    tree.set_status_label(status)
    tree.populate({str(blocked_file): [(1, 0, "blocked")]}, base_path=str(tmp_path))

    monkeypatch.setattr(tree, "_confirm_delete_result_files", lambda _paths, _stats, _scope: True)
    monkeypatch.setattr(tree, "_confirm_permanent_delete_result_files", lambda _paths: False)

    def fail_with_permission(_path):
        raise PermissionError("blocked")

    monkeypatch.setattr(tree, "_move_result_file_to_trash", fail_with_permission)

    tree._delete_result_files()

    assert blocked_file.exists()
    assert str(blocked_file) in tree.get_matches_data()
    assert "failed 1" in status.text()


def test_delete_result_files_uses_permanent_fallback_after_confirmation(tmp_path, monkeypatch):
    _qapp()
    file_path = tmp_path / "fallback.txt"
    file_path.write_text("fallback", encoding="utf-8")

    tree = ResultsTree()
    status = QLabel()
    tree.set_status_label(status)
    tree.populate({str(file_path): [(1, 0, "fallback")]}, base_path=str(tmp_path))

    monkeypatch.setattr(tree, "_confirm_delete_result_files", lambda _paths, _stats, _scope: True)
    monkeypatch.setattr(tree, "_confirm_permanent_delete_result_files", lambda _paths: True)
    monkeypatch.setattr(tree, "_move_result_file_to_trash", lambda _path: False)

    def fake_permanent_delete(path):
        Path(path).unlink()
        return True

    monkeypatch.setattr(tree, "_delete_result_file_permanently", fake_permanent_delete)

    tree._delete_result_files()

    assert not file_path.exists()
    assert str(file_path) not in tree.get_matches_data()
    assert "permanent 1" in status.text()
    assert "failed" not in status.text()


def test_replace_content_with_file_replaces_only_selected_text_file(tmp_path, monkeypatch):
    _qapp()
    source = tmp_path / "template.txt"
    selected_file = tmp_path / "selected.txt"
    kept_file = tmp_path / "kept.txt"
    source.write_text("new template\nconteudo", encoding="utf-8")
    selected_file.write_text("old selected", encoding="utf-8")
    kept_file.write_text("old kept", encoding="utf-8")

    tree = ResultsTree()
    status = QLabel()
    tree.set_status_label(status)
    tree.populate(
        {
            str(selected_file): [(1, 0, "old selected")],
            str(kept_file): [(1, 0, "old kept")],
        },
        base_path=str(tmp_path),
    )

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    selected_item = _child_by_text(root, "selected.txt")
    selected_item.setSelected(True)

    monkeypatch.setattr(tree, "_choose_replacement_template_path", lambda: str(source))
    monkeypatch.setattr(
        tree,
        "_confirm_replace_content_with_file",
        lambda _paths, _stats, _source_path, _replacement_content, _scope: True,
    )

    tree._replace_content_with_file()

    assert selected_file.read_text(encoding="utf-8") == "new template\nconteudo"
    assert kept_file.read_text(encoding="utf-8") == "old kept"
    assert str(selected_file) not in tree.get_matches_data()
    assert str(kept_file) in tree.get_matches_data()
    assert "Replaced 1 file(s)" in status.text()


def test_replace_content_with_file_cancel_keeps_targets(tmp_path, monkeypatch):
    _qapp()
    source = tmp_path / "template.txt"
    target = tmp_path / "target.txt"
    source.write_text("new", encoding="utf-8")
    target.write_text("old", encoding="utf-8")

    tree = ResultsTree()
    status = QLabel()
    tree.set_status_label(status)
    tree.populate({str(target): [(1, 0, "old")]}, base_path=str(tmp_path))

    monkeypatch.setattr(tree, "_choose_replacement_template_path", lambda: str(source))
    monkeypatch.setattr(
        tree,
        "_confirm_replace_content_with_file",
        lambda _paths, _stats, _source_path, _replacement_content, _scope: False,
    )

    tree._replace_content_with_file()

    assert target.read_text(encoding="utf-8") == "old"
    assert str(target) in tree.get_matches_data()
    assert "canceled" in status.text()


def test_replace_content_with_file_blocks_binary_source(tmp_path, monkeypatch):
    _qapp()
    source = tmp_path / "template.bin"
    target = tmp_path / "target.txt"
    source.write_bytes(b"\x00binary")
    target.write_text("old", encoding="utf-8")

    tree = ResultsTree()
    status = QLabel()
    tree.set_status_label(status)
    tree.populate({str(target): [(1, 0, "old")]}, base_path=str(tmp_path))

    warning_messages = []
    monkeypatch.setattr(tree, "_choose_replacement_template_path", lambda: str(source))
    monkeypatch.setattr(
        "src.gui.panels.results_tree.QMessageBox.warning",
        lambda _parent, _title, message, *args: warning_messages.append(message),
    )

    tree._replace_content_with_file()

    assert target.read_text(encoding="utf-8") == "old"
    assert str(target) in tree.get_matches_data()
    assert "Binary template files are not supported" in status.text()
    assert warning_messages == ["Binary template files are not supported for this operation."]


def test_replace_content_with_file_skips_binary_targets(tmp_path, monkeypatch):
    _qapp()
    source = tmp_path / "template.txt"
    text_target = tmp_path / "target.txt"
    binary_target = tmp_path / "target.bin"
    source.write_text("new", encoding="utf-8")
    text_target.write_text("old", encoding="utf-8")
    binary_target.write_bytes(b"\x00old")

    tree = ResultsTree()
    status = QLabel()
    tree.set_status_label(status)
    tree.populate(
        {
            str(text_target): [(1, 0, "old")],
            str(binary_target): [(1, 0, "old")],
        },
        base_path=str(tmp_path),
    )

    monkeypatch.setattr(tree, "_choose_replacement_template_path", lambda: str(source))
    monkeypatch.setattr(
        tree,
        "_confirm_replace_content_with_file",
        lambda _paths, _stats, _source_path, _replacement_content, _scope: True,
    )

    tree._replace_content_with_file()

    assert text_target.read_text(encoding="utf-8") == "new"
    assert binary_target.read_bytes() == b"\x00old"
    assert str(text_target) not in tree.get_matches_data()
    assert str(binary_target) in tree.get_matches_data()
    assert "Replaced 1 file(s)" in status.text()
    assert "binary 1" in status.text()
