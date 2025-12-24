#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Statistics Formatter - Format removal statistics for display

Extracted from json_rewriter_dock.py (v2.9.114 - Phase 2.2.1)
Provides formatting utilities for displaying operation statistics.
"""

from __future__ import annotations


def format_removal_statistics(stats: dict) -> str:
    """
    Format removal statistics for display.

    Args:
        stats: Dictionary with removal counters

    Returns:
        Formatted string or empty string if nothing was removed
    """
    lines = []
    total = 0

    # Map operation keys to display labels (Q4: specific terms)
    labels = {
        "dedupe": ("Removed duplicate key-value pairs", "key-value pairs"),
        "eliminate": ("Eliminated duplicate values", "values"),
        "numeric_keys": ("Excluded numeric keys", "keys"),
        "empty_values": ("Skipped empty key-value pairs", "key-value pairs"),
        "duplicate_child": ("Avoided duplicate child hierarchies", "object hierarchies"),
        "array_duplicates_consecutive": ("Removed consecutive duplicate array elements", "array elements"),
        "array_duplicates_all": ("Removed all duplicate array elements", "array elements"),
        "no_siblings": ("Skipped orphan object chains", "object chains"),
        "duplicate_objects": ("Removed duplicate objects", "objects"),
        "advanced_filters_filtered": ("🔍 Filtered by Advanced Conditions", "files"),
    }

    # Omit operations with 0 count (Q5-B)
    for key, (label, unit) in labels.items():
        count = stats.get(key, 0)
        if count > 0:
            lines.append(f"• {label}: {count} {unit}")
            total += count

    # If nothing was removed, return empty (Q5-C handled in caller)
    if total == 0:
        return ""

    # Format final message
    result = "✂️ Removal Statistics:\n"
    result += "\n".join(lines)
    result += f"\n\nTotal: {total} items removed"

    return result


__all__ = ['format_removal_statistics']
