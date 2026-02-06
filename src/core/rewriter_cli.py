#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rewriter CLI - Command-line interface for JSON/TS rewriting

Extracted from json_rewriter_dock.py (v2.9.114 - Phase 2.2.2)
Provides CLI execution logic for dedupe/rewrite operations.
"""

from __future__ import annotations

import argparse
from typing import Optional

from src.core.filters import Condition
from src.utils.advanced_conditions import apply_conditions_to_files


def cli_dedupe(
    args: argparse.Namespace, advanced_conditions: Optional[list[Condition]] = None, apply_all_types: bool = False
):
    """Execute the dedupe/rewrite operation based on args.

    Args:
        args: Command-line arguments (or GUI-generated args)
        advanced_conditions: Optional list of Condition objects for filtering files (Sprint B Feature #1)
        apply_all_types: If True, apply filters to all files; if False, auto-detect .json (Sprint B Feature #1)

    Returns:
        tuple: (output_text, substitution_map, removal_stats, detailed_stats) where:
            - output_text: processed file content
            - substitution_map: maps removed keys to replacements (Task #23)
            - removal_stats: dict with removal counters (Task v2.9.22)
            - detailed_stats: list of DetailedStatEntry objects (Sprint B Feature #3 v2.9.31)
    """
    # pylint: disable=import-outside-toplevel  # Lazy import for CLI function
    from src import rewriter as rw
    from src.rewriter.detailed_stats import get_global_collector

    # Enable detailed stats collection (Sprint B Feature #3)
    collector = get_global_collector()
    collector.clear()
    collector.enable()

    # Initialize removal statistics counter
    stats = {
        "dedupe": 0,
        "eliminate": 0,
        "numeric_keys": 0,
        "empty_values": 0,
        "duplicate_child": 0,
        "array_duplicates_consecutive": 0,
        "array_duplicates_all": 0,
        "no_siblings": 0,
        "advanced_filters_filtered": 0,  # Sprint B Feature #1
    }

    # Apply advanced filters BEFORE processing (Sprint B Feature #1)
    if advanced_conditions:
        # Auto-detect JSON files unless apply_all_types is True
        input_file = args.input
        should_filter = apply_all_types or input_file.endswith((".json", ".JSON"))

        if should_filter:
            # Apply filters
            filtered_files, filtered_out = apply_conditions_to_files(
                [input_file], advanced_conditions, logic_op="AND", enabled=True
            )

            stats["advanced_filters_filtered"] = filtered_out

            # If file was filtered out, skip processing (Q6: process all if zero files pass)
            # But since we're only checking single file here, if it's filtered out, we skip it
            if not filtered_files:
                # Return empty result (file was filtered out)
                collector.disable()
                return "", {}, stats, []

    # Read input
    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse based on format
    if args.from_ts:
        # TypeScript/JavaScript object literal - parse only, transformations applied later
        # pylint: disable=no-value-for-parameter  # Passing minimal args for parsing only
        obj = rw.ts_process_full_preserving(text, None, False, False)
    else:
        # Pure JSON
        obj = rw.parse_json_preserving_duplicates_text(text)

    # Sprint A v2.9.29: Resolve existing references FIRST (if enabled)
    if hasattr(args, "resolve_references") and args.resolve_references:
        obj, ref_stats = rw.resolve_references(obj)
        stats["references_resolved"] = ref_stats.get("resolved", 0)
        stats["references_invalid"] = ref_stats.get("invalid", 0)

    # Apply transformations with counting
    obj, stats["dedupe"] = rw.dedupe(obj)

    if args.join_keys:
        obj, _ = rw.join_keys(obj)  # join_keys doesn't remove items

    # Build substitution map for eliminated keys (Task #23 - v2.9.14 COMPLETO)
    substitution_map = {}
    if args.eliminate_duplicates:
        # Extract all keys AND values before elimination
        old_keys_values = rw.extract_all_keys_from_obj(obj.data if hasattr(obj, "data") else obj, prefix="t")
        obj, stats["eliminate"] = rw.eliminate_duplicates(obj)
        # Extract all keys AND values after elimination
        new_keys_values = rw.extract_all_keys_from_obj(obj.data if hasattr(obj, "data") else obj, prefix="t")
        # Build substitution map based on VALUE EQUALITY (not string similarity)
        substitution_map = rw.build_substitution_map_by_value(old_keys_values, new_keys_values)

    # Exclude numeric keys if requested
    if hasattr(args, "exclude_numeric") and args.exclude_numeric:
        obj, stats["numeric_keys"] = rw.exclude_numeric_keys(obj)

    # Skip empty values if requested
    if hasattr(args, "skip_empty") and args.skip_empty:
        obj, stats["empty_values"] = rw.skip_empty_values(obj)

    # Avoid duplicate child keys if requested
    if hasattr(args, "avoid_duplicate_child_keys") and args.avoid_duplicate_child_keys:
        obj, stats["duplicate_child"] = rw.avoid_duplicate_child_keys(obj)

    # Remove duplicate array values if requested (Task #8 - v2.9.8)
    if hasattr(args, "remove_dup_consecutive") and args.remove_dup_consecutive:
        obj, stats["array_duplicates_consecutive"] = rw.remove_duplicate_array_values(obj, consecutive_only=True)

    if hasattr(args, "remove_dup_all") and args.remove_dup_all:
        obj, stats["array_duplicates_all"] = rw.remove_duplicate_array_values(obj, consecutive_only=False)

    # Skip keys without siblings if requested (Task #35 - v2.9.11)
    if hasattr(args, "skip_no_siblings") and args.skip_no_siblings:
        obj, stats["no_siblings"] = rw.skip_keys_without_siblings(obj)

    # Remove duplicate objects if requested (Task #52 - v2.9.27 + Sprint A v2.9.29 + Sprint B Feature #4 v2.9.30)
    if hasattr(args, "remove_duplicate_objects") and args.remove_duplicate_objects:
        # Sprint A v2.9.29: Use create_references() if use_references mode enabled
        if hasattr(args, "use_references") and args.use_references:
            # Use new reference resolver (Sprint A + Sprint B Feature #4)
            format_type = getattr(args, "reference_format", "$ref")
            include_line_numbers = getattr(args, "include_line_numbers_ref", True)
            use_relative_paths = getattr(args, "use_relative_paths", False)

            obj, ref_stats = rw.create_references(
                obj,
                mode="references",
                include_line_numbers=include_line_numbers,
                format_type=format_type,
                use_relative_path=use_relative_paths,
            )
            stats["references_created"] = ref_stats.get("created", 0)
            stats["duplicate_objects"] = ref_stats.get("created", 0)  # For backward compatibility
        else:
            # Use legacy remove_duplicate_objects (delete mode)
            threshold = getattr(args, "duplicate_threshold", 100) / 100.0  # Convert percentage to 0.0-1.0
            include_arrays = getattr(args, "include_duplicate_arrays", False)
            mode = getattr(args, "duplicate_mode", "remove")
            obj, stats["duplicate_objects"], _dup_stats = rw.remove_duplicate_objects(
                obj, threshold=threshold, include_arrays=include_arrays, mode=mode
            )

    # Enforce consistent case if requested (Task #9 - v2.9.8)
    if hasattr(args, "enforce_case") and args.enforce_case:
        case_style = getattr(args, "case_style", "camel")
        obj, warnings = rw.enforce_consistent_case(obj, target_case=case_style, warn_inconsistencies=True)
        if warnings:
            print(f"\n⚠️ Case inconsistencies detected and corrected ({len(warnings)} warnings):")
            for warning in warnings[:10]:  # Show first 10 warnings
                print(f"  - {warning}")
            if len(warnings) > 10:
                print(f"  ... and {len(warnings) - 10} more warnings")

    # Serialize output
    if args.ts_out:
        output_text = rw.dump_ts_node(obj, indent=args.indent, level=0)
        if not args.no_line_break:
            output_text = rw.collapse_blank_lines(output_text)
    else:
        output_text = rw.dump_ts_obj(obj, indent=args.indent, level=0)

    # Write output
    out_path = args.output or args.input
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    # Collect detailed stats and disable collector (Sprint B Feature #3)
    detailed_stats = [entry.to_dict() for entry in collector.get_entries()]
    collector.disable()

    return output_text, substitution_map, stats, detailed_stats


__all__ = ['cli_dedupe']
