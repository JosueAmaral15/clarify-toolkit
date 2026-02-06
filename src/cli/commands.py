"""
CLI Commands
Command handlers for search, replace, insert, translate, and dedupe operations.

Refactored from src/app.py (Phase 3.1 - v2.9.114)
Original lines: 901-1115 (215 lines)
"""

from __future__ import annotations
import argparse
import json
import sys
from typing import Optional

from ..core import (
    SearchOptions, replace_in_text, insert_at_line,
    filter_files_by_conditions
)
from ..utils import walk_files, read_text, write_text
from ..rewriter import (
    parse_json_preserving_duplicates_text, find_object_block, ts_block_to_json_text,
    dedupe, join_keys, eliminate_duplicates, normalize_escaping, array_to_object_conversion,
    dump_ts_node, collapse_blank_lines, Obj, JSONNode
)

from .utils import split_globs, parse_conditions


def cli_search(args: argparse.Namespace) -> int:
    """Search command: Find matches in files."""
    patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    conds = parse_conditions(args.cond)
    files = filter_files_by_conditions(files, conds)
    total = 0
    for file_path in files:
        try:
            text = read_text(file_path)
            for m in patt.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                col = m.start() - (text.rfind("\n", 0, m.start()) + 1)
                print(f"{file_path}:{line}:{col}")
                total += 1
        except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
            print(f"[WARN] {file_path}: {e}", file=sys.stderr)
    print(f"\n{total} matches.")
    return 0


def cli_replace(args: argparse.Namespace) -> int:
    """Replace command: Replace text in files."""
    patt = SearchOptions(args.case, args.word, args.regex).compile(args.query)
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    conds = parse_conditions(args.cond)
    files = filter_files_by_conditions(files, conds)
    changed = 0
    for file_path in files:
        try:
            text = read_text(file_path)
            new, n = replace_in_text(text, patt, args.replacement, args.preserve_case, 0 if args.all else 1)
            if n > 0:
                if args.dry_run:
                    print(f"[DRY] {file_path}: would replace {n}")
                else:
                    write_text(file_path, new)
                    changed += 1
        except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
            print(f"[WARN] {file_path}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0


def cli_insert(args: argparse.Namespace) -> int:
    """Insert command: Insert text at specific line."""
    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    conds = parse_conditions(args.cond)
    files = filter_files_by_conditions(files, conds)
    changed = 0
    for file_path in files:
        try:
            old = read_text(file_path)
            new = insert_at_line(old, args.line, args.text, args.mode)
            if new != old:
                if args.dry_run:
                    print(f"[DRY] {file_path}: would modify")
                else:
                    write_text(file_path, new)
                    changed += 1
        except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
            print(f"[WARN] {file_path}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0


def cli_translate(args: argparse.Namespace) -> int:
    """Translate command: Replace texts using JSON/TS dictionary."""
    # pylint: disable=import-outside-toplevel  # CLI lazy import
    from ..app import read_translation_dict
    from ..translators.json_translate_helpers import translate_replace_texts

    files = list(walk_files(args.path, split_globs(args.include), split_globs(args.exclude)))
    data_dict = read_translation_dict(args.dictionary)

    root_name = getattr(args, "root", "t")
    inverse = getattr(args, "inverse", False)

    changed = 0
    for file_path in files:
        try:
            old = read_text(file_path)
            new = translate_replace_texts(old, data_dict, root_name=root_name, inverse=inverse)
            if new != old:
                if args.dry_run:
                    print(f"[DRY] {file_path}: would translate")
                else:
                    write_text(file_path, new)
                    changed += 1
        except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
            print(f"[WARN] {file_path}: {e}", file=sys.stderr)
    print(f"\nChanged files: {changed}")
    return 0


def cli_gtranslate(args: argparse.Namespace) -> int:
    """Google Translate CLI command."""
    # pylint: disable=import-outside-toplevel  # CLI lazy import
    from ..translation.google_translate import GoogleTranslateAPI

    translator = GoogleTranslateAPI()

    # Handle text or file input
    if hasattr(args, 'text') and args.text:
        text = args.text
    elif hasattr(args, 'file') and args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
            print(f"[ERROR] Could not read file {args.file}: {e}", file=sys.stderr)
            return 1
    else:
        print("[ERROR] No text or file specified", file=sys.stderr)
        return 1

    # Get source and target languages
    source = getattr(args, 'source', 'auto')
    target = getattr(args, 'target', 'pt')

    try:
        result_obj = translator.translate_text(text, from_lang=source, to_lang=target)
        result = result_obj.translated_text

        # Handle output
        if hasattr(args, 'output') and args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"Translation saved to {args.output}")
            except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
                print(f"[ERROR] Could not write to {args.output}: {e}", file=sys.stderr)
                return 1
        else:
            print(result)

        return 0
    except Exception as e:  # pylint: disable=broad-exception-caught  # CLI robustness
        print(f"[ERROR] Translation failed: {e}", file=sys.stderr)
        return 1


def cli_dedupe(args: argparse.Namespace) -> int:
    """Dedupe command: JSON/TS rewriter (dedupe/join/eliminate)."""
    raw = read_text(args.input)
    indent = None if args.indent is not None and args.indent <= 0 else args.indent
    normalize_esc = getattr(args, 'normalize_escaping', False)
    convert_arrays = getattr(args, 'convert_arrays_to_objects', False)

    if args.from_ts or args.input.lower().endswith((".ts",".tsx",".js",".jsx")):
        if args.ts_out:
            _start, _end, block = find_object_block(raw)
            json_text = ts_block_to_json_text(block)
            data = parse_json_preserving_duplicates_text(json_text)
            result = join_keys(data) if args.join_keys else dedupe(data)
            if args.eliminate_duplicates:
                result = eliminate_duplicates(result)
            if normalize_esc:
                result = normalize_escaping(result)
            if convert_arrays:
                result = array_to_object_conversion(result)
            body = dump_ts_node(result, indent, 0)
            out = f"export default {body};\n"
        else:
            from ..rewriter.rewriter import ts_process_full_preserving  # pylint: disable=import-outside-toplevel  # CLI lazy import
            out = ts_process_full_preserving(
                raw, indent, args.join_keys, args.eliminate_duplicates,
                normalize_esc, convert_arrays
            )
    else:
        data = parse_json_preserving_duplicates_text(raw)
        result = join_keys(data) if args.join_keys else dedupe(data)
        if args.eliminate_duplicates:
            result = eliminate_duplicates(result)
        if normalize_esc:
            result = normalize_escaping(result)
        if convert_arrays:
            result = array_to_object_conversion(result)

        # pylint: disable=too-many-return-statements  # Complex nested JSON dumping
        def dump_json(n: JSONNode, ind: Optional[int], lvl: int) -> str:
            if isinstance(n, Obj):
                if not n:
                    return "{}"
                if ind is None or ind <= 0:
                    parts = (
                        ["{"] +
                        [("," if i else "") + json.dumps(k, ensure_ascii=False) +
                         ":" + dump_json(v, ind, lvl) for i,(k,v) in enumerate(n)] +
                        ["}"]
                    )
                    return "".join(parts)
                sp = " " * ind
                parts = ["{\n"]
                for i,(k,v) in enumerate(n):
                    if i:
                        parts.append(",\n")
                    parts.append(sp*(lvl+1) + json.dumps(k, ensure_ascii=False) + ": " + dump_json(v, ind, lvl+1))
                parts.append("\n" + sp*lvl + "}")
                return "".join(parts)
            if isinstance(n, list):
                if not n:
                    return "[]"
                if ind is None or ind <= 0:
                    parts = ["["] + [("," if i else "") + dump_json(v, ind, lvl)
                                     for i,v in enumerate(n)] + ["]"]
                    return "".join(parts)
                sp = " " * ind
                parts = ["[\n"]
                for i,v in enumerate(n):
                    if i:
                        parts.append(",\n")
                    parts.append(sp*(lvl+1) + dump_json(v, ind, lvl+1))
                parts.append("\n" + sp*lvl + "]")
                return "".join(parts)
            return json.dumps(n, ensure_ascii=False)
        out = dump_json(result, indent, 0) + "\n"

    if args.no_line_break:
        out = collapse_blank_lines(out)

    if args.output:
        write_text(args.output, out)
    else:
        sys.stdout.write(out)
    return 0
