#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for Format Converter output handoff to Clarify Editor."""

from src.gui.unified_text_to_json_dock import UnifiedTextToJsonDock


def test_open_in_editor_and_switch_emits_paths_output_when_paths_tab_is_active(qapp):
    """The active Paths tab should be used as the editor handoff source."""
    dock = UnifiedTextToJsonDock()
    emitted = []
    dock.open_in_editor_and_switch_requested.connect(
        lambda content, output_kind: emitted.append((content, output_kind))
    )

    try:
        dock.jsx_paths_output.setPlainText("Component.title")
        dock.jsx_json_output.setPlainText('{"title": "Hello"}')
        dock.jsx_output_tabs.setCurrentIndex(0)

        dock._jsx_open_in_editor_and_switch()

        assert emitted == [("Component.title", "paths")]
    finally:
        dock.deleteLater()


def test_open_in_editor_and_switch_emits_json_output_when_json_tab_is_active(qapp):
    """The active JSON tab should be used as the editor handoff source."""
    dock = UnifiedTextToJsonDock()
    emitted = []
    dock.open_in_editor_and_switch_requested.connect(
        lambda content, output_kind: emitted.append((content, output_kind))
    )

    try:
        dock.jsx_paths_output.setPlainText("Component.title")
        dock.jsx_json_output.setPlainText('{"title": "Hello"}')
        dock.jsx_output_tabs.setCurrentIndex(1)

        dock._jsx_open_in_editor_and_switch()

        assert emitted == [('{"title": "Hello"}', "json")]
    finally:
        dock.deleteLater()
