"""
Advanced Conditions Utilities
==============================

Shared module for Advanced File Filters functionality (Task #51 + Sprint B Feature #1).
Provides reusable functions for building Condition objects from UI and applying filters.

Used by:
- src/gui/ai_processor_dock.py (AI Processor - Task #51)
- src/gui/json_rewriter_dock.py (JSON Rewriter - Sprint B Feature #1)
"""

from typing import Optional
from src.core.filters import Condition, filter_files_by_conditions


def get_conditions_from_ui(cond_rows) -> list[Condition]:
    """
    Build list of Condition objects from UI rows.
    Skips empty rows (no field selected).
    
    Args:
        cond_rows: List of tuples (combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex)
                   Each tuple contains PySide6 widgets representing one condition row.
    
    Returns:
        List of valid Condition objects (empty rows are skipped)
    
    Example:
        >>> conditions = get_conditions_from_ui(self.cond_rows)
        >>> # Returns [Condition(field='filename', operator='contains', value='test.json', ...)]
    """
    conditions = []
    
    for combo_field, combo_op, ed_value, combo_scope, chk_case, chk_regex in cond_rows:
        field = combo_field.currentText().strip()
        operator = combo_op.currentText().strip()
        value = ed_value.text().strip()
        scope_type = combo_scope.currentText().strip()
        case_sensitive = chk_case.isChecked()
        use_regex = chk_regex.isChecked()
        
        # Skip empty rows
        if not field or not operator or not value:
            continue
        
        # Create Condition object
        cond = Condition(
            field=field,
            operator=operator,
            value=value,
            scope_type=scope_type,
            scope_value="",  # Not used yet
            case_sensitive=case_sensitive,
            whole_word=False,  # Not exposed in UI yet
            use_regex=use_regex
        )
        conditions.append(cond)
    
    return conditions


def apply_conditions_to_files(
    files: list[str],
    conditions: list[Condition],
    logic_op: str = "AND",
    enabled: bool = True
) -> tuple[list[str], int]:
    """
    Apply advanced conditions to file list.
    
    Args:
        files: List of file paths to filter
        conditions: List of Condition objects to apply
        logic_op: "AND" (all must match) or "OR" (at least one must match)
        enabled: Whether filtering is enabled (if False, returns all files unchanged)
    
    Returns:
        Tuple of (filtered_files, num_filtered_out)
        - filtered_files: List of files that passed the filters
        - num_filtered_out: Number of files that were filtered out
    
    Example:
        >>> filtered, count = apply_conditions_to_files(
        ...     files=['a.json', 'b.txt'],
        ...     conditions=[Condition(field='ext', operator='equals', value='.json')],
        ...     logic_op='AND',
        ...     enabled=True
        ... )
        >>> # Returns (['a.json'], 1)
    """
    # If filtering is disabled, return all files unchanged
    if not enabled:
        return files, 0
    
    # If no valid conditions, return all files unchanged
    if not conditions:
        return files, 0
    
    # Apply filters using core module
    original_count = len(files)
    filtered_files = filter_files_by_conditions(files, conditions, logic_op)
    filtered_out = original_count - len(filtered_files)
    
    return filtered_files, filtered_out
