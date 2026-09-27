"""
Behavioral regression tests for File Explorer v2.9.117 corrections.

Tests the File Explorer phases of the integration plan:
- Phase B.1-6: Layout refactoring and feature additions
- Phase C.1-2: Visual polish and UX improvements

Phase A window-flag behavior is covered by tests/test_window_flags_restore.py.
"""

import pytest
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QLabel, QTreeWidgetItem

from src.i18n import tr
from src.gui.file_explorer_dock import (
    FileExplorerDock,
    PROGRESS_DIALOG_LABEL_WIDTH,
    PROGRESS_DIALOG_WIDTH,
)
from src.gui.panels.results_tree import ResultsTree
from src.gui.widgets.collapsible_section import CollapsibleSection

# Tests are designed to validate code structure without full app initialization
# This avoids import errors from relative imports in the codebase


def test_progress_message_compacts_long_paths():
    """Progress text should not expose full paths that resize the modal."""
    long_name = "deeply_nested_component_" * 8 + "extremely_long_name.json"
    long_path = f"/very/long/project/path/src/features/{long_name}"

    message = FileExplorerDock._format_progress_message(long_path, current=12, total=99)
    item = message.removeprefix("Processing 12/99: ")

    assert message.startswith("Processing 12/99: ")
    assert long_path not in message
    assert "/" not in item
    assert item.endswith("name.json")
    assert "..." in item


def test_progress_dialog_has_fixed_width_configuration(qapp):
    """Progress dialog should have a fixed width instead of resizing around label text."""
    dock = FileExplorerDock()
    try:
        dock._ensure_progress_dialog()

        assert dock.progress_dialog.minimumWidth() == PROGRESS_DIALOG_WIDTH
        assert dock.progress_dialog.maximumWidth() == PROGRESS_DIALOG_WIDTH
        assert dock._progress_label in dock.progress_dialog.findChildren(QLabel)
        assert dock._progress_label.wordWrap() is True
        assert dock._progress_label.maximumWidth() == PROGRESS_DIALOG_LABEL_WIDTH
    finally:
        if dock.progress_dialog:
            dock.progress_dialog.close()
        dock.deleteLater()


def test_phase_b1_qsplitter_horizontal(qapp):
    """The controls/results splitter should render horizontally near a 25/75 ratio."""
    dock = FileExplorerDock()
    try:
        dock.resize(1200, 800)
        dock.show()
        qapp.processEvents()

        sizes = dock.splitter.sizes()
        total_size = sum(sizes)
        assert dock.splitter.orientation() == Qt.Orientation.Horizontal
        assert dock.splitter.count() == 2
        assert total_size > 0
        assert 0.20 <= sizes[0] / total_size <= 0.30
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_b2_resultstree_integration(qapp):
    """The results stack should contain the search tree and browse table."""
    dock = FileExplorerDock()
    try:
        tree_container = dock.results_stack.widget(0)

        assert dock.results_stack.count() == 2
        assert isinstance(dock.results_tree, ResultsTree)
        assert tree_container.isAncestorOf(dock.results_tree)
        assert dock.results_stack.widget(1) is dock.table_manager
        assert dock.results_stack.currentIndex() == 1
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_b3_unified_browse_search_button(qapp):
    """The command button should dispatch browse and search inputs through one executor."""
    dock = FileExplorerDock()
    try:
        with (
            patch.object(dock.filename_panel, "get_pattern", side_effect=["", "*.py"]),
            patch.object(dock.content_panel, "get_query", side_effect=["", ""]),
            patch.object(dock, "_list_files") as list_files,
        ):
            dock.btn_list.click()
            dock.btn_list.click()

        assert dock.btn_list.isEnabled() is True
        assert dock.btn_list.objectName() == "btn_list"
        assert list_files.call_count == 2
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_b4_statistics_panel(qapp):
    """Statistics should count files/directories and format size and elapsed time."""
    dock = FileExplorerDock()
    results = [
        SimpleNamespace(file_info=SimpleNamespace(is_dir=False, size=1024)),
        SimpleNamespace(file_info=SimpleNamespace(is_dir=False, size=512)),
        SimpleNamespace(file_info=SimpleNamespace(is_dir=True, size=4096)),
    ]

    try:
        dock._update_statistics(results, elapsed_time=1.234)

        assert dock.lbl_files_count.text() == tr("file_list.stats_files").format("2")
        assert dock.lbl_dirs_count.text() == tr("file_list.stats_dirs").format("1")
        assert dock.lbl_total_size.text() == tr("file_list.stats_size").format("1.5 KB")
        assert dock.lbl_exec_time.text() == tr("file_list.stats_time").format("1.23")
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_b5_export_csv(qapp):
    """CSV export should use the table or tree exporter for the active view."""
    dock = FileExplorerDock()
    try:
        with (
            patch.object(dock.table_manager, "export_csv") as export_table,
            patch.object(dock, "_export_tree_to_csv") as export_tree,
        ):
            dock.results_stack.setCurrentIndex(1)
            dock._export_results_csv()
            export_table.assert_called_once_with()
            export_tree.assert_not_called()

            dock.results_stack.setCurrentIndex(0)
            dock._export_results_csv()
            export_tree.assert_called_once_with()

        assert dock.btn_export_csv.isEnabled() is True
        assert dock.btn_export_csv.objectName() == "btn_export"
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_b6_collapsible_sections(qapp):
    """Advanced sections should start collapsed and expand from their headers."""
    dock = FileExplorerDock()
    sections = (dock.section_filters, dock.section_conditions, dock.section_presets)

    try:
        assert all(isinstance(section, CollapsibleSection) for section in sections)
        assert all(section.isCollapsed() for section in sections)
        assert all(section.content_frame.isHidden() for section in sections)

        dock.section_filters.setAnimationDuration(0)
        for expected_collapsed in (False, True, False):
            dock.section_filters.header_button.click()
            qapp.processEvents()

            assert dock.section_filters.isCollapsed() is expected_collapsed
            assert dock.section_filters.header_button.isChecked() is not expected_collapsed
            assert dock.section_filters.content_frame.isHidden() is expected_collapsed
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_c1_hover_keeps_splitter_stable(qapp):
    """Moving across either pane should not resize the splitter automatically."""
    dock = FileExplorerDock()
    try:
        dock.resize(1200, 800)
        dock.show()
        qapp.processEvents()
        initial_sizes = dock.splitter.sizes()

        for pane_index in (0, 1, 0):
            pane = dock.splitter.widget(pane_index)
            QTest.mouseMove(pane, pane.rect().center())
            qapp.processEvents()
            assert dock.splitter.sizes() == initial_sizes
    finally:
        dock.close()
        dock.deleteLater()
        qapp.processEvents()


def test_phase_c2_context_menu(qapp):
    """Location and properties actions should follow selection and invoke handlers."""
    tree = ResultsTree()
    item = QTreeWidgetItem(["result.txt"])
    tree.addTopLevelItem(item)

    try:
        menu_without_selection = tree._build_context_menu()
        actions_without_selection = {
            action.text(): action for action in menu_without_selection.actions()
        }
        location_text = next(
            text for text in actions_without_selection if text.endswith("Open Location")
        )
        properties_text = next(
            text for text in actions_without_selection if text.endswith("Properties")
        )
        assert actions_without_selection[location_text].isEnabled() is False
        assert actions_without_selection[properties_text].isEnabled() is False

        item.setSelected(True)
        with (
            patch.object(tree, "_open_file_location") as open_location,
            patch.object(tree, "_show_file_properties") as show_properties,
        ):
            menu_with_selection = tree._build_context_menu()
            actions_with_selection = {
                action.text(): action for action in menu_with_selection.actions()
            }

            location_action = actions_with_selection[location_text]
            properties_action = actions_with_selection[properties_text]
            assert location_action.isEnabled() is True
            assert properties_action.isEnabled() is True

            location_action.trigger()
            properties_action.trigger()
            open_location.assert_called_once_with()
            show_properties.assert_called_once_with()
    finally:
        tree.deleteLater()


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (0, "0.0 B"),
        (1023, "1023.0 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1024**2, "1.0 MB"),
        (1024**3, "1.0 GB"),
        (1024**4, "1.0 TB"),
        (1024**5, "1.0 PB"),
    ],
)
def test_format_size_logic(size, expected):
    """File sizes should use binary thresholds and human-readable units."""
    assert ResultsTree._format_size(size) == expected
