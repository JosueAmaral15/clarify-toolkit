#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Automated Tooltip Presence Tests - v2.9.47

Verifies all interactive widgets have non-empty tooltips.
Uses pytest-qt for GUI testing.

Strategy: Check toolTip() != "" for all widgets in docks
"""

import pytest
from PySide6.QtWidgets import QWidget, QPushButton, QCheckBox, QComboBox, QLineEdit, QSpinBox, QRadioButton
from src.gui.set_operations_dock import SetOperationsDock
from src.gui.case_converter_dock import CaseConverterDock
from src.gui.json_rewriter_dock import JsonRewriterDock
from src.gui.ai_processor_dock import AIProcessorDock
from src.gui.json_editor_tab import JsonEditorTab
from src.gui.editor_dock import EditorDock


def get_interactive_widgets(widget: QWidget) -> list[QWidget]:
    """
    Recursively find all interactive widgets that should have tooltips.
    
    Args:
        widget: Parent widget to search
        
    Returns:
        List of interactive widgets (buttons, checkboxes, inputs, etc.)
    """
    interactive_types = (QPushButton, QCheckBox, QComboBox, QLineEdit, QSpinBox, QRadioButton)
    widgets = []
    
    for child in widget.findChildren(QWidget):
        if isinstance(child, interactive_types):
            widgets.append(child)
    
    return widgets


def test_set_operations_dock_tooltips(qtbot):
    """Verify Set Operations Dock has tooltips on all interactive widgets."""
    dock = SetOperationsDock()
    qtbot.addWidget(dock)
    
    # Specific widgets to check (known from implementation)
    critical_widgets = [
        (dock.ed_file_a, "ed_file_a"),
        (dock.btn_browse_a, "btn_browse_a"),
        (dock.ed_file_b, "ed_file_b"),
        (dock.btn_browse_b, "btn_browse_b"),
        (dock.chk_multiple, "chk_multiple"),
        (dock.btn_add_file, "btn_add_file"),
        (dock.btn_remove_file, "btn_remove_file"),
        (dock.btn_clear_files, "btn_clear_files"),
        (dock.chk_intersection, "chk_intersection"),
        (dock.chk_union, "chk_union"),
        (dock.chk_difference, "chk_difference"),
        (dock.chk_symmetric, "chk_symmetric"),
        (dock.radio_key_value, "radio_key_value"),
        (dock.radio_full_path, "radio_full_path"),
        (dock.radio_key_only, "radio_key_only"),
        (dock.chk_ignore_case_keys, "chk_ignore_case_keys"),
        (dock.chk_ignore_case_values, "chk_ignore_case_values"),
        (dock.chk_skip_empty, "chk_skip_empty"),
        (dock.chk_arrays_ignore_order, "chk_arrays_ignore_order"),
        (dock.combo_output, "combo_output"),
        (dock.btn_execute, "btn_execute"),
    ]
    
    for widget, name in critical_widgets:
        tooltip = widget.toolTip()
        assert tooltip != "", f"Set Operations - {name} missing tooltip"
        assert len(tooltip) >= 10, f"Set Operations - {name} tooltip too short: '{tooltip}'"
        print(f"✓ {name}: {tooltip[:50]}...")


def test_case_converter_dock_tooltips(qtbot):
    """Verify Case Converter Dock has tooltips on all interactive widgets."""
    dock = CaseConverterDock()
    qtbot.addWidget(dock)
    
    # Critical widgets
    critical_widgets = [
        (dock.combo_source, "combo_source"),
        (dock.combo_target, "combo_target"),
        (dock.ed_path, "ed_path"),
        (dock.btn_browse, "btn_browse"),
        (dock.chk_is_file, "chk_is_file"),
        (dock.ed_extensions, "ed_extensions"),
    ]
    
    for widget, name in critical_widgets:
        tooltip = widget.toolTip()
        assert tooltip != "", f"Case Converter - {name} missing tooltip"
        assert len(tooltip) >= 10, f"Case Converter - {name} tooltip too short: '{tooltip}'"
        print(f"✓ {name}: {tooltip[:50]}...")


def test_json_rewriter_dock_tooltips(qtbot):
    """Verify JSON Rewriter Dock has tooltips on all interactive widgets."""
    dock = JsonRewriterDock()
    qtbot.addWidget(dock)
    
    # Critical widgets (sample - Rewriter has 30+ widgets)
    critical_widgets = [
        (dock.ed_in, "ed_in"),
        (dock.btn_in, "btn_in"),
        (dock.ed_out, "ed_out"),
        (dock.btn_out, "btn_out"),
        (dock.chk_from_ts, "chk_from_ts"),
        (dock.chk_ts_out, "chk_ts_out"),
        (dock.chk_join, "chk_join"),
        (dock.chk_elim, "chk_elim"),
        (dock.chk_nlb, "chk_nlb"),
        (dock.chk_exclude_numeric, "chk_exclude_numeric"),
        (dock.chk_skip_empty, "chk_skip_empty"),
        (dock.chk_avoid_dup_child, "chk_avoid_dup_child"),
        (dock.chk_normalize_escaping, "chk_normalize_escaping"),
        (dock.chk_convert_arrays, "chk_convert_arrays"),
        (dock.chk_skip_no_siblings, "chk_skip_no_siblings"),
        (dock.chk_remove_dup_objects, "chk_remove_dup_objects"),
        (dock.chk_include_dup_arrays, "chk_include_dup_arrays"),
        (dock.spin_dup_threshold, "spin_dup_threshold"),
        (dock.combo_dup_mode, "combo_dup_mode"),
        (dock.chk_update_refs, "chk_update_refs"),
        (dock.ed_project_dir, "ed_project_dir"),
        (dock.btn_project_browse, "btn_project_browse"),
        (dock.chk_ref_backup, "chk_ref_backup"),
        (dock.chk_remove_dup_consecutive, "chk_remove_dup_consecutive"),
        (dock.chk_remove_dup_all, "chk_remove_dup_all"),
        (dock.chk_enforce_case, "chk_enforce_case"),
        (dock.combo_case_style, "combo_case_style"),
        (dock.chk_validate_case, "chk_validate_case"),
        (dock.chk_is_file, "chk_is_file"),
        (dock.btn_advanced_filters, "btn_advanced_filters"),
        (dock.chk_apply_all_types, "chk_apply_all_types"),
        (dock.radio_delete_dups, "radio_delete_dups"),
        (dock.radio_use_refs, "radio_use_refs"),
        (dock.chk_resolve_refs, "chk_resolve_refs"),
        (dock.btn_configure_format, "btn_configure_format"),
        (dock.spin_indent, "spin_indent"),
        (dock.btn_run, "btn_run"),
    ]
    
    for widget, name in critical_widgets:
        tooltip = widget.toolTip()
        assert tooltip != "", f"JSON Rewriter - {name} missing tooltip"
        assert len(tooltip) >= 10, f"JSON Rewriter - {name} tooltip too short: '{tooltip}'"
        print(f"✓ {name}: {tooltip[:50]}...")


def test_ai_processor_dock_tooltips(qtbot):
    """Verify AI Processor Dock has tooltips on all interactive widgets (v2.9.48)."""
    dock = AIProcessorDock()
    qtbot.addWidget(dock)
    
    # Critical widgets (38 total: 23 existing + 15 new in v2.9.48)
    critical_widgets = [
        # Provider & Model (3)
        (dock.combo_provider, "combo_provider"),
        (dock.combo_model, "combo_model"),
        (dock.btn_refresh_models, "btn_refresh_models"),
        # API Key (2)
        (dock.ed_api_key, "ed_api_key"),
        (dock.btn_verify, "btn_verify"),
        # Prompt (1)
        (dock.ed_prompt, "ed_prompt"),
        # Options (3)
        (dock.chk_line_by_line, "chk_line_by_line"),
        (dock.spin_max_bytes, "spin_max_bytes"),
        (dock.ed_extensions, "ed_extensions"),
        # Scope Filter (7)
        (dock.chk_scope_enable, "chk_scope_enable"),
        (dock.ed_scope_start, "ed_scope_start"),
        (dock.chk_start_regex, "chk_start_regex"),
        (dock.chk_start_case, "chk_start_case"),
        (dock.ed_scope_end, "ed_scope_end"),
        (dock.chk_end_regex, "chk_end_regex"),
        (dock.chk_end_case, "chk_end_case"),
        # Advanced Conditions (9 - 1st row as sample)
        (dock.combo_cond_logic, "combo_cond_logic"),
        (dock.cond_rows[0][0], "cond_field_1"),  # combo_field
        (dock.cond_rows[0][1], "cond_op_1"),     # combo_op
        (dock.cond_rows[0][2], "cond_value_1"),  # ed_value
        (dock.cond_rows[0][3], "cond_scope_1"),  # combo_scope
        (dock.cond_rows[0][4], "cond_case_1"),   # chk_case
        (dock.cond_rows[0][5], "cond_regex_1"),  # chk_regex
        # Action Buttons (4)
        (dock.btn_process, "btn_process"),
        (dock.btn_interrupt, "btn_interrupt"),
        (dock.btn_save_results, "btn_save_results"),
        (dock.btn_clear, "btn_clear"),
        # Statistics (3)
        (dock.lbl_session_stats, "lbl_session_stats"),
        (dock.lbl_lifetime_stats, "lbl_lifetime_stats"),
        (dock.chk_remove_fences, "chk_remove_fences"),
        # PathEntry widgets (3 from first path)
        (dock.path_entries[0].ed_path, "path_1_ed_path"),
        (dock.path_entries[0].btn_browse, "path_1_btn_browse"),
        (dock.path_entries[0].chk_is_file, "path_1_chk_is_file"),
    ]
    
    for widget, name in critical_widgets:
        tooltip = widget.toolTip()
        assert tooltip != "", f"AI Processor - {name} missing tooltip"
        assert len(tooltip) >= 10, f"AI Processor - {name} tooltip too short: '{tooltip}'"
        print(f"✓ {name}: {tooltip[:60]}...")


def test_json_editor_tab_tooltips(qtbot):
    """Verify JSON Editor Tab has tooltips on all interactive widgets (v2.9.49)."""
    tab = JsonEditorTab()
    qtbot.addWidget(tab)
    
    # Critical widgets (8 total: 4 existing updated + 4 new)
    critical_widgets = [
        # Toolbar buttons (6)
        (tab.btn_format, "btn_format"),
        (tab.combo_indent, "combo_indent"),
        (tab.btn_validate, "btn_validate"),
        (tab.btn_search, "btn_search"),
        (tab.btn_collapse, "btn_collapse"),
        (tab.btn_expand, "btn_expand"),
        # Editor & Tree (2)
        (tab.editor, "editor"),
        (tab.tree, "tree"),
        # Validation label (1) - NEW in v2.9.49
        (tab.lbl_validation, "lbl_validation"),
    ]
    
    for widget, name in critical_widgets:
        tooltip = widget.toolTip()
        assert tooltip != "", f"JSON Editor Tab - {name} missing tooltip"
        assert len(tooltip) >= 10, f"JSON Editor Tab - {name} tooltip too short: '{tooltip}'"
        print(f"✓ {name}: {tooltip[:60]}...")


def test_editor_dock_tooltips(qtbot):
    """Verify Editor Dock has tooltips on all interactive widgets (v2.9.49)."""
    dock = EditorDock()
    qtbot.addWidget(dock)
    
    # Critical widgets (8 total: 6 existing updated + 2 new)
    critical_widgets = [
        # Toolbar buttons (6)
        (dock.btn_new, "btn_new"),
        (dock.btn_open, "btn_open"),
        (dock.btn_save, "btn_save"),
        (dock.btn_save_as, "btn_save_as"),
        (dock.btn_close_tab, "btn_close_tab"),
        (dock.chk_auto_save, "chk_auto_save"),
        # Tab widget & Status (2) - NEW in v2.9.49
        (dock.tab_widget, "tab_widget"),
        (dock.lbl_status, "lbl_status"),
    ]
    
    for widget, name in critical_widgets:
        tooltip = widget.toolTip()
        assert tooltip != "", f"Editor Dock - {name} missing tooltip"
        assert len(tooltip) >= 10, f"Editor Dock - {name} tooltip too short: '{tooltip}'"
        print(f"✓ {name}: {tooltip[:60]}...")


def test_tooltip_format_standards(qtbot):
    """Verify tooltips follow format standards from TOOLTIP_GUIDELINES.md."""
    dock = SetOperationsDock()
    qtbot.addWidget(dock)
    
    # Check tooltips with keyboard shortcuts follow "Description | Shortcut" format
    widgets_with_shortcuts = [
        (dock.btn_browse_a, "Ctrl+O"),
        (dock.btn_execute, "F5"),
    ]
    
    for widget, expected_shortcut in widgets_with_shortcuts:
        tooltip = widget.toolTip()
        if expected_shortcut in tooltip:
            # Should have " | " separator
            assert " | " in tooltip, f"Tooltip '{tooltip}' missing ' | ' separator before shortcut"
            print(f"✓ Shortcut format valid: {tooltip}")


def test_tooltip_length_limits(qtbot):
    """Verify English tooltips respect 150 character limit."""
    docks = [
        SetOperationsDock(),
        CaseConverterDock(),
        JsonRewriterDock(),
        AIProcessorDock(),
        EditorDock(),
    ]
    
    # Also test JsonEditorTab (not a dock)
    tab = JsonEditorTab()
    qtbot.addWidget(tab)
    widgets_tab = get_interactive_widgets(tab)
    for widget in widgets_tab:
        tooltip = widget.toolTip()
        if tooltip:
            desc = tooltip.split(" | ")[0] if " | " in tooltip else tooltip
            assert len(desc) <= 150, f"{widget.objectName()} tooltip too long ({len(desc)} chars): '{desc}'"
    
    for dock in docks:
        qtbot.addWidget(dock)
        widgets = get_interactive_widgets(dock)
        
        for widget in widgets:
            tooltip = widget.toolTip()
            if tooltip:  # Skip empty tooltips (some widgets intentionally have none)
                # Remove keyboard shortcuts from length check
                desc = tooltip.split(" | ")[0] if " | " in tooltip else tooltip
                assert len(desc) <= 150, f"{widget.objectName()} tooltip too long ({len(desc)} chars): '{desc}'"


def test_tooltip_no_html(qtbot):
    """Verify tooltips use plain text (no HTML tags) for accessibility."""
    dock = SetOperationsDock()
    qtbot.addWidget(dock)
    
    widgets = get_interactive_widgets(dock)
    
    for widget in widgets:
        tooltip = widget.toolTip()
        if tooltip:
            # Check for common HTML tags
            assert "<" not in tooltip or tooltip.count("<") == tooltip.count("&lt;"), \
                f"{widget.objectName()} tooltip contains HTML: '{tooltip}'"
            assert ">" not in tooltip or tooltip.count(">") == tooltip.count("&gt;"), \
                f"{widget.objectName()} tooltip contains HTML: '{tooltip}'"


@pytest.mark.skip(reason="Focus handling may fail in headless environments")
def test_tooltip_keyboard_accessibility(qtbot):
    """Verify tooltips appear on keyboard focus (not just hover)."""
    dock = SetOperationsDock()
    qtbot.addWidget(dock)
    
    # Test a few focusable widgets
    focusable_widgets = [
        dock.ed_file_a,
        dock.btn_browse_a,
        dock.chk_intersection,
    ]
    
    for widget in focusable_widgets:
        # Set focus
        widget.setFocus()
        qtbot.waitUntil(lambda: widget.hasFocus(), timeout=1000)
        
        # Tooltip should be accessible (Qt handles display on focus automatically)
        tooltip = widget.toolTip()
        assert tooltip != "", f"{widget.objectName()} should have tooltip for keyboard users"
        print(f"✓ Keyboard accessible: {widget.objectName()}")


# Summary test
def test_tooltip_coverage_summary(qtbot):
    """Summary: Count total tooltips and coverage percentage."""
    docks = [
        ("Set Operations", SetOperationsDock()),
        ("Case Converter", CaseConverterDock()),
        ("JSON Rewriter", JsonRewriterDock()),
        ("AI Processor", AIProcessorDock()),
        ("Editor Dock", EditorDock()),
    ]
    
    # Add JsonEditorTab separately (not a dock)
    json_editor_tab = JsonEditorTab()
    qtbot.addWidget(json_editor_tab)
    tab_widgets = get_interactive_widgets(json_editor_tab)
    tab_with_tooltips = sum(1 for w in tab_widgets if w.toolTip() != "")
    print(f"\nJSON Editor Tab:")
    print(f"  Total widgets: {len(tab_widgets)}")
    print(f"  With tooltips: {tab_with_tooltips}")
    print(f"  Coverage: {(tab_with_tooltips / len(tab_widgets) * 100) if tab_widgets else 0:.1f}%")
    
    total_widgets = 0
    widgets_with_tooltips = 0
    
    for dock_name, dock in docks:
        qtbot.addWidget(dock)
        widgets = get_interactive_widgets(dock)
        total_widgets += len(widgets)
        
        with_tooltips = sum(1 for w in widgets if w.toolTip() != "")
        widgets_with_tooltips += with_tooltips
        
        coverage = (with_tooltips / len(widgets) * 100) if widgets else 0
        print(f"\n{dock_name} Dock:")
        print(f"  Total widgets: {len(widgets)}")
        print(f"  With tooltips: {with_tooltips}")
        print(f"  Coverage: {coverage:.1f}%")
    
    overall_coverage = (widgets_with_tooltips / total_widgets * 100) if total_widgets else 0
    print(f"\n{'='*50}")
    print(f"OVERALL TOOLTIP COVERAGE: {overall_coverage:.1f}%")
    print(f"Total widgets: {total_widgets}")
    print(f"With tooltips: {widgets_with_tooltips}")
    print(f"{'='*50}\n")
    
    # Assert minimum 90% coverage
    assert overall_coverage >= 90.0, f"Tooltip coverage too low: {overall_coverage:.1f}% (target: ≥90%)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
