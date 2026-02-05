"""
CLI Argument Parser
ArgumentParser setup for all CLI subcommands.

Refactored from src/app.py (Phase 3.1 - v2.9.114)
Original lines: 4417-4504 (88 lines)
"""

from __future__ import annotations
import argparse

from ..core import InsertMode
from .commands import (
    cli_search, cli_replace, cli_insert,
    cli_translate, cli_gtranslate, cli_dedupe
)


def build_parser() -> argparse.ArgumentParser:
    """
    Build the complete argument parser for Clarify CLI.
    
    Returns:
        ArgumentParser with all subcommands configured.
    """
    parser = argparse.ArgumentParser(
        description="Search/Replace/Insert + JSON Translate/Dedupe — GUI or CLI"
    )
    sub = parser.add_subparsers(dest="cmd")

    # GUI
    parser.add_argument("--gui", action="store_true", help="Launch GUI (default if no cmd).")

    # search
    ps = sub.add_parser("search", help="Search in a file/folder")
    ps.add_argument("path", help="File or folder")
    ps.add_argument("query", help="Search string or regex")
    ps.add_argument("--case", action="store_true", help="Case sensitive")
    ps.add_argument("--word", action="store_true", help="Whole word")
    ps.add_argument("--regex", action="store_true", help="Interpret query as regex")
    ps.add_argument("--include", nargs="*", default=None, help="Include globs (*.ts *.tsx …)")
    ps.add_argument("--exclude", nargs="*", default=None, help="Exclude globs (node_modules …)")
    ps.add_argument(
        "--cond", nargs="*",
        help="Advanced conditions like field:op:value (field=filename|path|ext|size|mtime)"
    )
    ps.set_defaults(func=cli_search)

    # replace
    pr = sub.add_parser("replace", help="Replace text")
    pr.add_argument("path", help="File or folder")
    pr.add_argument("query", help="Search string or regex")
    pr.add_argument("replacement", help="Replacement text")
    pr.add_argument("--all", action="store_true", help="Replace all (default: first per file)")
    pr.add_argument("--preserve-case", action="store_true", help="Mimic match casing in replacement")
    pr.add_argument("--case", action="store_true")
    pr.add_argument("--word", action="store_true")
    pr.add_argument("--regex", action="store_true")
    pr.add_argument("--include", nargs="*", default=None)
    pr.add_argument("--exclude", nargs="*", default=None)
    pr.add_argument("--cond", nargs="*", help="Advanced conditions (field:op:value)")
    pr.add_argument("--dry-run", action="store_true")
    pr.set_defaults(func=cli_replace)

    # insert
    pi = sub.add_parser("insert", help="Insert text at a given line")
    pi.add_argument("path")
    pi.add_argument("line", type=int)
    pi.add_argument("text")
    pi.add_argument("--mode", choices=[InsertMode.LEFT, InsertMode.RIGHT, InsertMode.REPLACE,
                                       InsertMode.INSERT_ABOVE, InsertMode.INSERT_BELOW],
                    default=InsertMode.INSERT_BELOW)
    pi.add_argument("--include", nargs="*", default=None)
    pi.add_argument("--exclude", nargs="*", default=None)
    pi.add_argument("--cond", nargs="*", help="Advanced conditions (field:op:value)")
    pi.add_argument("--dry-run", action="store_true")
    pi.set_defaults(func=cli_insert)

    # translate
    pt = sub.add_parser("translate", help="Replace texts by keys from a JSON/TS dictionary")
    pt.add_argument("path")
    pt.add_argument("dictionary")
    pt.add_argument("--include", nargs="*", default=None)
    pt.add_argument("--exclude", nargs="*", default=None)
    pt.add_argument("--dry-run", action="store_true")
    pt.add_argument("--root", default="t", help="Root alias for placeholders (default: t)")
    pt.add_argument("--inverse", action="store_true", help="Inverse mode: {t.path} → text")
    pt.set_defaults(func=cli_translate)

    # gtranslate (Google Translate)
    pg = sub.add_parser("gtranslate", help="Translate text using Google Translate")
    group = pg.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", help="Text to translate")
    group.add_argument("-f", "--file", help="File to translate")
    pg.add_argument("-s", "--source", default="auto", help="Source language (default: auto)")
    pg.add_argument("-T", "--target", default="pt", help="Target language (default: pt)")
    pg.add_argument("-o", "--output", help="Output file (default: stdout)")
    pg.set_defaults(func=cli_gtranslate)

    # dedupe
    pd = sub.add_parser("dedupe", help="JSON/TS rewriter (dedupe/join/eliminate)")
    pd.add_argument("input")
    pd.add_argument("-o", "--output")
    pd.add_argument("-i", "--indent", type=int, default=2)
    pd.add_argument("-f", "--from-ts", action="store_true", help="TS/JS mode preserving file")
    pd.add_argument("-t", "--ts-out", action="store_true", help="Emit export default { … };")
    pd.add_argument("-j", "--join-keys", action="store_true", help="Join identical keys")
    pd.add_argument("-e", "--eliminate-duplicates", action="store_true", help="Eliminate global duplicates")
    pd.add_argument("-b", "--no-line-break", action="store_true", help="Remove blank blanklines in output")
    pd.set_defaults(func=cli_dedupe)

    return parser
