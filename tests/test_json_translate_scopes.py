"""Behavioral regressions for JSON Translate scope processing."""

import json
from unittest.mock import patch

from src.gui.json_translate_dock import JsonTranslateDock
from src.translators.json_translate_helpers import (
    apply_scoped_translation,
    apply_scoped_translations,
    process_translate_file,
)


def test_custom_scope_transforms_each_inner_region_once():
    content = "before [[hello]] middle [[world]] after"

    result = apply_scoped_translation(
        content,
        start_rx=r"\[\[",
        end_rx=r"\]\]",
        fn_transform=str.upper,
    )

    assert result == "before [[HELLO]] middle [[WORLD]] after"


def test_multiple_scope_pairs_transform_their_union():
    content = "outside [[first]] middle {{second}} outside"

    result = apply_scoped_translations(
        content,
        [(r"\[\[", r"\]\]"), (r"\{\{", r"\}\}")],
        str.upper,
    )

    assert result == "outside [[FIRST]] middle {{SECOND}} outside"


def test_overlapping_scope_pairs_transform_source_text_once():
    calls = []

    def record_transform(text):
        calls.append(text)
        return text.upper()

    result = apply_scoped_translations(
        "A first B second C",
        [("A", "C"), ("B", "C")],
        record_transform,
    )

    assert result == "A FIRST B SECOND C"
    assert calls == [" first B second "]


def test_multiple_literal_tag_scopes_do_not_touch_other_tags():
    content = "<div>first</div><script>second</script><p>outside</p>"

    result = apply_scoped_translations(
        content,
        [(r"<div>", r"</div>"), (r"<script>", r"</script>")],
        str.upper,
    )

    assert result == "<div>FIRST</div><script>SECOND</script><p>outside</p>"


def test_process_translate_file_accepts_parsed_exclusion_list(tmp_path):
    source = tmp_path / "source.ts"
    source.write_text(
        'const keep = "Hello";\nconst translate = "World";\n',
        encoding="utf-8",
    )
    dictionary = {"home": {"hello": "Hello", "world": "World"}}

    changed, error = process_translate_file(
        str(source),
        dictionary,
        root_alias="t",
        start_rx="",
        end_rx="",
        make_backup=False,
        dont_override=False,
        inverse=False,
        exclude_patterns=[r'const keep = "Hello";'],
    )

    translated = source.read_text(encoding="utf-8")
    assert changed is True
    assert error is None
    assert 'const keep = "Hello";' in translated
    assert 'const translate = "{t.home.world}";' in translated


def test_process_translate_file_keeps_json_source_valid(tmp_path):
    source = tmp_path / "source.json"
    source.write_text(
        json.dumps({"title": "Hello", "nested": {"label": "World"}}),
        encoding="utf-8",
    )
    dictionary = {"home": {"hello": "Hello", "world": "World"}}

    changed, error = process_translate_file(
        str(source),
        dictionary,
        root_alias="t",
        start_rx="",
        end_rx="",
        make_backup=False,
        dont_override=False,
        inverse=False,
        exclude_patterns=[],
    )

    translated = json.loads(source.read_text(encoding="utf-8"))
    assert changed is True
    assert error is None
    assert translated == {
        "title": "{t.home.hello}",
        "nested": {"label": "{t.home.world}"},
    }


def test_process_translate_file_supports_multiple_scope_pairs(tmp_path):
    source = tmp_path / "source.ts"
    source.write_text(
        'outside "Hello"; [["Hello"]] middle {{"World"}}',
        encoding="utf-8",
    )
    dictionary = {"home": {"hello": "Hello", "world": "World"}}

    changed, error = process_translate_file(
        str(source),
        dictionary,
        root_alias="t",
        start_rx="unused",
        end_rx="unused",
        make_backup=False,
        dont_override=False,
        inverse=False,
        exclude_patterns=[],
        scope_pairs=[(r"\[\[", r"\]\]"), (r"\{\{", r"\}\}")],
    )

    translated = source.read_text(encoding="utf-8")
    assert changed is True
    assert error is None
    assert 'outside "Hello";' in translated
    assert '[["{t.home.hello}"]]' in translated
    assert '{{"{t.home.world}"}}' in translated


def test_json_translate_dock_runs_real_translation_helper(qapp, tmp_path):
    source = tmp_path / "source.ts"
    source.write_text('const title = "Hello";\n', encoding="utf-8")
    dictionary_path = tmp_path / "translations.json"
    dictionary_path.write_text(
        json.dumps({"home": {"title": "Hello"}}),
        encoding="utf-8",
    )

    dock = JsonTranslateDock()
    try:
        dock.ed_path.setText(str(source))
        dock.ed_dict.setText(str(dictionary_path))
        dock.object_variable_name.setText("t")
        dock.ed_start.clear()
        dock.ed_end.clear()
        dock.ed_exclude.clear()
        dock.chk_backup.setChecked(False)
        dock.chk_dont_override.setChecked(False)

        with (
            patch("src.gui.json_translate_dock.QMessageBox.information") as information,
            patch("src.gui.json_translate_dock.record_translation_operation"),
        ):
            dock._run()

        assert source.read_text(encoding="utf-8") == 'const title = "{t.home.title}";\n'
        information.assert_called_once()
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_json_translate_dock_adds_and_removes_scope_rows(qapp):
    dock = JsonTranslateDock()
    try:
        dock.btn_add_scope.click()
        qapp.processEvents()
        second_row = dock.scope_rows[1]
        second_row["start"].setText(r"\[\[")
        second_row["end"].setText(r"\]\]")

        assert len(dock.scope_rows) == 2
        assert dock._get_scope_pairs() == [
            ("<[^>]*?>", "</[^>]*?>"),
            (r"\[\[", r"\]\]"),
        ]
        assert second_row["remove"].toolTip()
        assert second_row["start"].accessibleName()

        second_row["remove"].click()
        qapp.processEvents()
        assert len(dock.scope_rows) == 1
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_json_translate_dock_rejects_incomplete_scope(qapp):
    dock = JsonTranslateDock()
    try:
        dock.ed_path.setText("source.ts")
        dock.ed_dict.setText("translations.json")
        dock.btn_add_scope.click()
        dock.scope_rows[1]["start"].setText(r"\[\[")

        with (
            patch("src.gui.json_translate_dock.QMessageBox.warning") as warning,
            patch("src.gui.json_translate_dock.process_translate_file") as process,
        ):
            dock._run()

        warning.assert_called_once()
        process.assert_not_called()
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_json_translate_dock_runs_with_two_configured_scopes(qapp, tmp_path):
    source = tmp_path / "multi-scope.ts"
    source.write_text(
        'outside "Hello"; [["Hello"]] middle {{"World"}}',
        encoding="utf-8",
    )
    dictionary_path = tmp_path / "translations.json"
    dictionary_path.write_text(
        json.dumps({"home": {"hello": "Hello", "world": "World"}}),
        encoding="utf-8",
    )

    dock = JsonTranslateDock()
    try:
        dock.ed_path.setText(str(source))
        dock.ed_dict.setText(str(dictionary_path))
        dock.ed_start.setText(r"\[\[")
        dock.ed_end.setText(r"\]\]")
        dock.btn_add_scope.click()
        dock.scope_rows[1]["start"].setText(r"\{\{")
        dock.scope_rows[1]["end"].setText(r"\}\}")
        dock.ed_exclude.clear()
        dock.chk_backup.setChecked(False)
        dock.chk_dont_override.setChecked(False)

        with (
            patch("src.gui.json_translate_dock.QMessageBox.information"),
            patch("src.gui.json_translate_dock.record_translation_operation"),
        ):
            dock._run()

        translated = source.read_text(encoding="utf-8")
        assert 'outside "Hello";' in translated
        assert '[["{t.home.hello}"]]' in translated
        assert '{{"{t.home.world}"}}' in translated
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()
