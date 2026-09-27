#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for accessibility labels (v2.9.37)
Tests that all widgets in MVP docks have proper accessible names and descriptions.
"""

import sys

import pytest
from PySide6.QtWidgets import QApplication


# Ensure QApplication exists for widget tests
@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestJsonTranslateDockAccessibility:
    """Test accessibility labels for JSON Translate Dock (22 widgets)."""

    def test_all_widgets_have_accessible_names(self, qapp):
        """Verify all widgets have accessible names set."""
        from src.gui.json_translate_dock import JsonTranslateDock

        dock = JsonTranslateDock()

        # Test input widgets
        assert dock.ed_path.accessibleName() == "JSON Translate - Input - Root Path"
        assert dock.ed_dict.accessibleName() == "JSON Translate - Input - Dictionary File Path"
        assert dock.object_variable_name.accessibleName() == "JSON Translate - Input - Variable Name"
        assert dock.ed_start.accessibleName() == "JSON Translate - Input - Start Delimiter Regex"
        assert dock.ed_end.accessibleName() == "JSON Translate - Input - End Delimiter Regex"
        assert dock.ed_exclude.accessibleName() == "JSON Translate - Input - Exclusion Patterns"

        # Test buttons
        assert dock.btn_browse.accessibleName() == "JSON Translate - Button - Browse Root Path"
        assert dock.btn_open.accessibleName() == "JSON Translate - Button - Browse Dictionary"
        assert dock.btn_add_scope.accessibleName() == "JSON Translate - Button - Add Scope"
        assert dock.btn_run.accessibleName() == "JSON Translate - Button - Run Translation"
        assert dock.btn_swap.accessibleName() == "JSON Translate - Button - Swap Dictionaries"
        assert dock.btn_undo.accessibleName() == "JSON Translate - Button - Undo with Backup"

        # Test checkboxes
        assert dock.is_file.accessibleName() == "JSON Translate - Checkbox - Is File"
        assert dock.chk_backup.accessibleName() == "JSON Translate - Checkbox - Backup Original Files"
        assert (
            dock.chk_dont_override.accessibleName()
            == "JSON Translate - Checkbox - Don't Override Existing Translations"
        )
        assert dock.chk_inverse_json_translate.accessibleName() == "JSON Translate - Checkbox - Reverse Translation"
        assert dock.chk_emit_export.accessibleName() == "JSON Translate - Checkbox - Emit Export Const"
        assert dock.chk_preserve_uppercase.accessibleName() == "JSON Translate - Checkbox - Preserve Uppercase Keys"

        # Test labels
        assert dock.lbl_path.accessibleName() == "JSON Translate - Label - Root Path"
        assert dock.lbl_dict.accessibleName() == "JSON Translate - Label - Dictionary File"
        assert dock.lbl_var.accessibleName() == "JSON Translate - Label - Variable Name"
        assert dock.lbl_start.accessibleName() == "JSON Translate - Label - Start Delimiter"
        assert dock.lbl_end.accessibleName() == "JSON Translate - Label - End Delimiter"
        assert dock.lbl_exclude.accessibleName() == "JSON Translate - Label - Exclusion Patterns"
        assert dock.lbl_stats.accessibleName() == "JSON Translate - Label - Statistics"

    def test_all_widgets_have_descriptions(self, qapp):
        """Verify all critical widgets have accessible descriptions."""
        from src.gui.json_translate_dock import JsonTranslateDock

        dock = JsonTranslateDock()

        # Critical inputs must have descriptions
        assert len(dock.ed_path.accessibleDescription()) > 0
        assert len(dock.ed_dict.accessibleDescription()) > 0
        assert len(dock.btn_run.accessibleDescription()) > 0

        # Descriptions should be meaningful
        assert "file or directory" in dock.ed_path.accessibleDescription().lower()
        assert "dictionary" in dock.ed_dict.accessibleDescription().lower()
        assert (
            "execute" in dock.btn_run.accessibleDescription().lower()
            or "translation" in dock.btn_run.accessibleDescription().lower()
        )

    def test_accessible_names_not_empty(self, qapp):
        """Ensure no widgets have empty accessible names."""
        from src.gui.json_translate_dock import JsonTranslateDock

        dock = JsonTranslateDock()

        widgets = [
            dock.ed_path,
            dock.ed_dict,
            dock.object_variable_name,
            dock.ed_start,
            dock.ed_end,
            dock.ed_exclude,
            dock.btn_browse,
            dock.btn_open,
            dock.btn_add_scope,
            dock.btn_run,
            dock.btn_swap,
            dock.btn_undo,
            dock.is_file,
            dock.chk_backup,
            dock.chk_dont_override,
            dock.chk_inverse_json_translate,
            dock.chk_emit_export,
            dock.chk_preserve_uppercase,
            dock.lbl_path,
            dock.lbl_dict,
            dock.lbl_var,
            dock.lbl_start,
            dock.lbl_end,
            dock.lbl_exclude,
            dock.lbl_stats,
        ]

        for widget in widgets:
            assert widget.accessibleName() != "", f"Widget {widget.__class__.__name__} has empty accessible name"
            assert (
                len(widget.accessibleName()) > 5
            ), f"Widget {widget.__class__.__name__} has too short accessible name: {widget.accessibleName()}"


class TestJsonRewriterDockAccessibility:
    """Test accessibility labels for JSON Rewriter Dock (42 widgets)."""

    def test_all_widgets_have_accessible_names(self, qapp):
        """Verify all widgets have accessible names set."""
        from src.gui.json_rewriter_dock import JsonRewriterDock

        dock = JsonRewriterDock()

        # Test input/output widgets
        assert dock.ed_in.accessibleName() == "JSON Rewriter - Input - Input File Path"
        assert dock.ed_out.accessibleName() == "JSON Rewriter - Input - Output File Path"
        assert dock.btn_in.accessibleName() == "JSON Rewriter - Button - Browse Input File"
        assert dock.btn_out.accessibleName() == "JSON Rewriter - Button - Browse Output File"

        # Test core checkboxes
        assert dock.chk_from_ts.accessibleName() == "JSON Rewriter - Checkbox - From TypeScript/JavaScript"
        assert dock.chk_ts_out.accessibleName() == "JSON Rewriter - Checkbox - Emit Export Default"
        assert dock.chk_join.accessibleName() == "JSON Rewriter - Checkbox - Join Keys"
        assert dock.chk_elim.accessibleName() == "JSON Rewriter - Checkbox - Eliminate Duplicates"
        assert dock.chk_nlb.accessibleName() == "JSON Rewriter - Checkbox - No Blank Lines"

        # Test advanced checkboxes
        assert dock.chk_exclude_numeric.accessibleName() == "JSON Rewriter - Checkbox - Exclude Numeric Keys"
        assert dock.chk_skip_empty.accessibleName() == "JSON Rewriter - Checkbox - Skip Empty Values"
        assert dock.chk_avoid_dup_child.accessibleName() == "JSON Rewriter - Checkbox - Avoid Duplicate Child Keys"
        assert dock.chk_normalize_escaping.accessibleName() == "JSON Rewriter - Checkbox - Normalize Escaping"
        assert dock.chk_convert_arrays.accessibleName() == "JSON Rewriter - Checkbox - Convert Arrays to Objects"
        assert dock.chk_skip_no_siblings.accessibleName() == "JSON Rewriter - Checkbox - Skip Keys Without Siblings"

        # Test duplicate objects section
        assert dock.chk_remove_dup_objects.accessibleName() == "JSON Rewriter - Checkbox - Remove Duplicate Objects"
        assert (
            dock.chk_include_dup_arrays.accessibleName()
            == "JSON Rewriter - Checkbox - Include Arrays in Duplicate Detection"
        )
        assert dock.spin_dup_threshold.accessibleName() == "JSON Rewriter - SpinBox - Similarity Threshold Percentage"
        assert dock.combo_dup_mode.accessibleName() == "JSON Rewriter - ComboBox - Duplicate Detection Mode"

        # Test reference update section
        assert dock.chk_update_refs.accessibleName() == "JSON Rewriter - Checkbox - Update References in Project"
        assert dock.ed_project_dir.accessibleName() == "JSON Rewriter - Input - Project Directory"
        assert dock.btn_project_browse.accessibleName() == "JSON Rewriter - Button - Browse Project Directory"
        assert dock.chk_ref_backup.accessibleName() == "JSON Rewriter - Checkbox - Create Backups"

        # Test array duplicates
        assert (
            dock.chk_remove_dup_consecutive.accessibleName()
            == "JSON Rewriter - Checkbox - Remove Consecutive Array Duplicates"
        )
        assert dock.chk_remove_dup_all.accessibleName() == "JSON Rewriter - Checkbox - Remove All Array Duplicates"

        # Test case enforcement
        assert dock.chk_enforce_case.accessibleName() == "JSON Rewriter - Checkbox - Enforce Consistent Case"
        assert dock.combo_case_style.accessibleName() == "JSON Rewriter - ComboBox - Case Style"
        assert dock.chk_validate_case.accessibleName() == "JSON Rewriter - Checkbox - Validate Case Before Applying"

        # Test action buttons
        assert dock.btn_run.accessibleName() == "JSON Rewriter - Button - Run Rewrite"

    def test_spinbox_and_combobox_names(self, qapp):
        """Verify SpinBox and ComboBox widgets have proper names."""
        from src.gui.json_rewriter_dock import JsonRewriterDock

        dock = JsonRewriterDock()

        # SpinBoxes
        assert "SpinBox" in dock.spin_dup_threshold.accessibleName()
        assert "SpinBox" in dock.spin_indent.accessibleName()

        # ComboBoxes
        assert "ComboBox" in dock.combo_dup_mode.accessibleName()
        assert "ComboBox" in dock.combo_case_style.accessibleName()

    def test_radio_buttons_accessible(self, qapp):
        """Verify radio buttons have proper accessible names."""
        from src.gui.json_rewriter_dock import JsonRewriterDock

        dock = JsonRewriterDock()

        assert "RadioButton" in dock.radio_delete_dups.accessibleName()
        assert "RadioButton" in dock.radio_use_refs.accessibleName()
        assert "Delete Duplicates" in dock.radio_delete_dups.accessibleName()
        assert "Use References" in dock.radio_use_refs.accessibleName()

    def test_accessible_names_descriptive(self, qapp):
        """Ensure accessible names are descriptive, not generic."""
        from src.gui.json_rewriter_dock import JsonRewriterDock

        dock = JsonRewriterDock()

        widgets = [
            dock.ed_in,
            dock.ed_out,
            dock.btn_in,
            dock.btn_out,
            dock.chk_join,
            dock.chk_elim,
            dock.chk_nlb,
            dock.spin_dup_threshold,
            dock.combo_dup_mode,
        ]

        for widget in widgets:
            name = widget.accessibleName()
            # Should not be generic like "Button 1", "Input 2"
            assert not any(
                generic in name for generic in ["Button 1", "Input 1", "Checkbox 1", "Widget"]
            ), f"Widget has generic name: {name}"
            # Should contain dock name
            assert "JSON Rewriter" in name, f"Widget name missing dock prefix: {name}"


class TestJsonSearchDockAccessibility:
    """Test accessibility labels for JSON Search Dock (16 widgets)."""

    def test_all_widgets_have_accessible_names(self, qapp):
        """Verify all widgets have accessible names set."""
        from src.gui.json_search_dock import JsonSearchDock

        dock = JsonSearchDock()

        # Test search inputs
        assert dock.ed_search_key.accessibleName() == "JSON Search - Input - Search Key"
        assert dock.ed_search_value.accessibleName() == "JSON Search - Input - Search Value"
        assert dock.ed_filename.accessibleName() == "JSON Search - Input - Filename Filter"

        # Test combo and path
        assert dock.combo_mode.accessibleName() == "JSON Search - ComboBox - Search Mode"
        assert dock.ed_path.accessibleName() == "JSON Search - Input - Search Path"
        assert dock.btn_browse.accessibleName() == "JSON Search - Button - Browse Path"

        # Test options
        assert dock.chk_is_file.accessibleName() == "JSON Search - Checkbox - Is File"
        assert dock.chk_case.accessibleName() == "JSON Search - Checkbox - Case Sensitive"
        assert dock.chk_regex.accessibleName() == "JSON Search - Checkbox - Use Regex"

        # Test spinbox
        assert dock.spin_max.accessibleName() == "JSON Search - SpinBox - Maximum Results"

    def test_action_buttons_accessible(self, qapp):
        """Verify action buttons created by base class have labels."""
        from src.gui.json_search_dock import JsonSearchDock

        dock = JsonSearchDock()

        # These buttons are created by StandardToolDock.create_action_buttons()
        if hasattr(dock, "btn_search"):
            assert "JSON Search" in dock.btn_search.accessibleName()
            assert "Run Search" in dock.btn_search.accessibleName() or "Search" in dock.btn_search.accessibleName()

        if hasattr(dock, "btn_interrupt"):
            assert "JSON Search" in dock.btn_interrupt.accessibleName()

        if hasattr(dock, "btn_save_results"):
            assert "JSON Search" in dock.btn_save_results.accessibleName()

        if hasattr(dock, "btn_clear"):
            assert "JSON Search" in dock.btn_clear.accessibleName()

    def test_results_text_area_accessible(self, qapp):
        """Verify results text area has accessible name."""
        from src.gui.json_search_dock import JsonSearchDock

        dock = JsonSearchDock()

        if hasattr(dock, "text_results"):
            assert dock.text_results.accessibleName() == "JSON Search - TextArea - Search Results"
            assert len(dock.text_results.accessibleDescription()) > 0
            assert "results" in dock.text_results.accessibleDescription().lower()


class TestAccessibilityConsistency:
    """Test consistency across all docks."""

    def test_naming_convention_consistency(self, qapp):
        """Verify all docks use consistent naming convention."""
        from src.gui.json_rewriter_dock import JsonRewriterDock
        from src.gui.json_search_dock import JsonSearchDock
        from src.gui.json_translate_dock import JsonTranslateDock

        translate_dock = JsonTranslateDock()
        rewriter_dock = JsonRewriterDock()
        search_dock = JsonSearchDock()

        # All names should follow pattern: "Dock Name - Widget Type - Purpose"
        all_widgets = [
            translate_dock.ed_path,
            translate_dock.btn_browse,
            rewriter_dock.ed_in,
            rewriter_dock.btn_run,
            search_dock.ed_search_key,
            search_dock.combo_mode,
        ]

        for widget in all_widgets:
            name = widget.accessibleName()
            # Should have exactly 2 hyphens (3 parts)
            assert name.count(" - ") == 2, f"Name doesn't follow convention: {name}"

            # First part should be dock name
            dock_name = name.split(" - ")[0]
            assert dock_name in ["JSON Translate", "JSON Rewriter", "JSON Search"], f"Invalid dock name: {dock_name}"

            # Second part should be widget type
            widget_type = name.split(" - ")[1]
            assert widget_type in [
                "Button",
                "Input",
                "Checkbox",
                "ComboBox",
                "SpinBox",
                "Label",
                "RadioButton",
                "TextArea",
            ], f"Invalid widget type: {widget_type}"

    def test_no_duplicate_names(self, qapp):
        """Ensure no two widgets have the same accessible name."""
        from PySide6.QtWidgets import QWidget

        from src.gui.json_rewriter_dock import JsonRewriterDock
        from src.gui.json_search_dock import JsonSearchDock
        from src.gui.json_translate_dock import JsonTranslateDock

        translate_dock = JsonTranslateDock()
        rewriter_dock = JsonRewriterDock()
        search_dock = JsonSearchDock()

        all_names = []

        # Collect all names from translate dock
        for attr in dir(translate_dock):
            try:
                obj = getattr(translate_dock, attr)
                if isinstance(obj, QWidget) and callable(getattr(obj, "accessibleName", None)):
                    name = obj.accessibleName()
                    if name:
                        all_names.append(name)
            except (TypeError, AttributeError):
                continue

        # Collect all names from rewriter dock
        for attr in dir(rewriter_dock):
            try:
                obj = getattr(rewriter_dock, attr)
                if isinstance(obj, QWidget) and callable(getattr(obj, "accessibleName", None)):
                    name = obj.accessibleName()
                    if name:
                        all_names.append(name)
            except (TypeError, AttributeError):
                continue

        # Collect all names from search dock
        for attr in dir(search_dock):
            try:
                obj = getattr(search_dock, attr)
                if isinstance(obj, QWidget) and callable(getattr(obj, "accessibleName", None)):
                    name = obj.accessibleName()
                    if name:
                        all_names.append(name)
            except (TypeError, AttributeError):
                continue

        # Check for duplicates (names should be unique across all docks)
        assert len(all_names) == len(
            set(all_names)
        ), f"Found duplicate accessible names! Duplicates: {[name for name in all_names if all_names.count(name) > 1]}"

    def test_total_widget_count(self, qapp):
        """Verify total number of accessible widgets matches expectation."""
        from PySide6.QtWidgets import QWidget

        from src.gui.json_rewriter_dock import JsonRewriterDock
        from src.gui.json_search_dock import JsonSearchDock
        from src.gui.json_translate_dock import JsonTranslateDock

        translate_dock = JsonTranslateDock()
        rewriter_dock = JsonRewriterDock()
        search_dock = JsonSearchDock()

        # Count widgets with accessible names in each dock
        translate_count = 0
        for attr in dir(translate_dock):
            try:
                obj = getattr(translate_dock, attr)
                if isinstance(obj, QWidget) and callable(getattr(obj, "accessibleName", None)):
                    if obj.accessibleName():
                        translate_count += 1
            except (TypeError, AttributeError):
                continue

        rewriter_count = 0
        for attr in dir(rewriter_dock):
            try:
                obj = getattr(rewriter_dock, attr)
                if isinstance(obj, QWidget) and callable(getattr(obj, "accessibleName", None)):
                    if obj.accessibleName():
                        rewriter_count += 1
            except (TypeError, AttributeError):
                continue

        search_count = 0
        for attr in dir(search_dock):
            try:
                obj = getattr(search_dock, attr)
                if isinstance(obj, QWidget) and callable(getattr(obj, "accessibleName", None)):
                    if obj.accessibleName():
                        search_count += 1
            except (TypeError, AttributeError):
                continue

        # Expected counts (minimum thresholds)
        assert translate_count >= 22, f"JSON Translate has only {translate_count} accessible widgets (expected >= 22)"
        assert rewriter_count >= 42, f"JSON Rewriter has only {rewriter_count} accessible widgets (expected >= 42)"
        assert search_count >= 10, f"JSON Search has only {search_count} accessible widgets (expected >= 10)"

        total = translate_count + rewriter_count + search_count
        assert total >= 74, f"Total accessible widgets is {total} (expected >= 74 from MVP scope)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
