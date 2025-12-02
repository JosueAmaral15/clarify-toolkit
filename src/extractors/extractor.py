#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor.py

Orchestrator class for JSX/Generic parameter extraction.
Processes files/directories, parses with JSXParser or GenericScopeParser,
builds hierarchical JSON structures, and applies normalization options.
"""

import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..utils.normalization import (
    STANDARD_HTML_TAGS,
    is_standard_tag,
    kept_prefix,
    normalize_token,
    path_join,
    smart_truncate,
)
from .generic_parser import GenericScopeParser
from .jsx_parser import JSXParser


def read_text(path: str) -> str:
    """Read file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def list_files(root: str, patterns: Optional[List[str]] = None) -> Iterable[str]:
    """
    List files recursively from root.
    If root is a file, yield it directly.
    If root is a directory, walk recursively and yield files matching patterns.
    """
    if os.path.isfile(root):
        yield root
    else:
        for r, _, files in os.walk(root):
            for fn in files:
                if not patterns:
                    yield os.path.join(r, fn)
                else:
                    if any(fn.endswith(pat) for pat in patterns):
                        yield os.path.join(r, fn)


class Extractor:
    """
    Orchestrator for extracting parameters from JSX/TSX files or generic scope-based files.

    Processes files with JSXParser or GenericScopeParser, builds hierarchical paths,
    applies normalization (case styles, truncation), and generates nested JSON output.
    """

    CONTAINS = "contains"
    EQUALS = "equals"

    def __init__(
        self,
        param: str,
        mode: str,
        avoid_keys: str,
        avoid_keys_parameter: str,
        include_key: bool,
        include_value: bool,
        no_standard: bool,
        convert_to_json: bool,
        with_quotation_marks: bool,
        indentation: int,
        case_style: str,
        limit: Optional[str],
        avoid_cut: bool,
        to_upper: bool,
        only_strings: bool = False,
        is_attribute_mode: bool = False,
        start_regex: Optional[str] = None,
        end_regex: Optional[str] = None,
        root_alias: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
    ):
        self.param = param
        self.match_all = (param is None) or (param.strip() == "") or (param.strip() == "*")
        self.mode = mode
        self.avoid_keys = avoid_keys
        self.avoid_keys_parameter = avoid_keys_parameter
        self.include_key = include_key
        self.include_value = include_value
        self.no_standard = no_standard
        self.convert_to_json = convert_to_json
        self.with_quotation_marks = with_quotation_marks
        self.indentation = indentation
        self.case_style = case_style
        self.limit = limit
        self.avoid_cut = avoid_cut
        self.to_upper = to_upper
        self.only_strings = only_strings
        self.is_attribute_mode = is_attribute_mode
        self.start_regex = start_regex
        self.end_regex = end_regex
        self.root_alias = root_alias
        self.file_extensions = file_extensions or []

    def _record_text_kv(self, path_tokens: List[str], raw_value: str) -> Dict[str, Any]:
        """
        Build a tree from path_tokens + normalized key from raw_value.
        E.g., path_tokens = ['DashboardPage', 'Button'] + key from raw_value "Click Me" => click_me
        Returns nested dict structure.
        """
        # Normalize raw_value into a token that becomes the final key
        truncated = smart_truncate(raw_value, self.limit, self.avoid_cut)
        key = normalize_token(truncated, self.case_style, self.to_upper)

        # If include_value=True, set value to raw_value, else set to empty dict
        if self.include_value:
            leaf = raw_value
        else:
            leaf = {}

        # Build nested dict from path_tokens + [key]
        full_path = path_tokens + [key]
        return self.build_tree_from_path(full_path, leaf)

    def find_paths_to_key(self, structure: Dict[str, Any], word_key: str) -> List[List[str]]:
        """
        Find all paths (as list of keys) leading to a specific key in nested dict.
        Returns list of paths, e.g., [['DashboardPage', 'Button', 'label'], ...]
        """
        paths = []

        def recurse(node, current_path):
            if not isinstance(node, dict):
                return
            for k, v in node.items():
                if k == word_key:
                    paths.append(current_path + [k])
                if isinstance(v, dict):
                    recurse(v, current_path + [k])

        recurse(structure, [])
        return paths

    def get_subtree_at_path(self, structure: Dict[str, Any], path: List[str]) -> Any:
        """
        Navigate nested dict by path list.
        Returns value at path, or None if path doesn't exist.
        """
        node = structure
        for key in path:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return None
        return node

    def build_tree_from_path(self, path: List[str], leaf_value: Any) -> Dict[str, Any]:
        """
        Build nested dict from path list with leaf_value at the end.
        E.g., ['a', 'b', 'c'], "value" => {'a': {'b': {'c': "value"}}}
        """
        if not path:
            return {}
        result = current = {}
        for key in path[:-1]:
            current[key] = {}
            current = current[key]
        current[path[-1]] = leaf_value
        return result

    def merge_dicts(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge dict b into dict a.
        For conflicting keys, b's value wins if both are not dicts.
        """
        result = dict(a)
        for k, v in b.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self.merge_dicts(result[k], v)
            else:
                result[k] = v
        return result

    def prune_to_key(self, structure: Dict[str, Any], word_key: str, depth_offset: int) -> Dict[str, Any]:
        """
        Preserve only branches leading to word_key, with depth offset:
        - depth_offset = -1: keep up to (and including) word_key
        - depth_offset = -2: keep up to parent of word_key
        Returns pruned dict structure.
        """
        paths = self.find_paths_to_key(structure, word_key)
        if not paths:
            return structure

        result = {}
        for path in paths:
            # Apply depth offset
            if depth_offset == -1:
                effective_path = path
            elif depth_offset == -2:
                effective_path = path[:-1] if len(path) > 1 else path
            else:
                effective_path = path

            # Get subtree at path and merge into result
            subtree = self.get_subtree_at_path(structure, effective_path)
            tree_to_merge = self.build_tree_from_path(effective_path, subtree if subtree is not None else {})
            result = self.merge_dicts(result, tree_to_merge)

        return result

    def remove_key(self, structure: Dict[str, Any], key_to_remove: str) -> Dict[str, Any]:
        """
        Recursively remove all occurrences of key_to_remove from nested dict.
        Returns cleaned dict.
        """
        if not isinstance(structure, dict):
            return structure

        result = {}
        for k, v in structure.items():
            if k == key_to_remove:
                continue
            if isinstance(v, dict):
                result[k] = self.remove_key(v, key_to_remove)
            else:
                result[k] = v
        return result

    def remove_key_with_collapse(self, structure: Dict[str, Any], key_to_remove: str) -> Dict[str, Any]:
        """
        Remove key_to_remove and collapse empty dicts.
        If a dict becomes empty after removal, replace it with the key name as string.
        """
        if not isinstance(structure, dict):
            return structure

        result = {}
        for k, v in structure.items():
            if k == key_to_remove:
                continue
            if isinstance(v, dict):
                cleaned = self.remove_key_with_collapse(v, key_to_remove)
                # Collapse empty dict to key name
                if not cleaned:
                    result[k] = k
                else:
                    result[k] = cleaned
            else:
                result[k] = v
        return result

    def _build_path_tokens_with_key(self, file_root: str, stack: List[str], effective_key: str) -> List[str]:
        """
        Build path tokens with key inclusion logic.
        Returns [file_root] + filtered stack + [effective_key] (if include_key=True).
        """
        # Get base path from file_root and stack
        base_tokens = kept_prefix(file_root, stack, drop_standard=self.no_standard)

        # Add effective_key if include_key=True
        if self.include_key:
            return base_tokens + [effective_key]
        else:
            return base_tokens

    def deep_merge(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        For conflicting keys, recursively merge if both are dicts, else b wins.
        """
        result = dict(a)
        for k, v in b.items():
            if k in result:
                if isinstance(result[k], dict) and isinstance(v, dict):
                    result[k] = self.deep_merge(result[k], v)
                else:
                    result[k] = v
            else:
                result[k] = v
        return result

    def check_value_if_it_is_just_string(self, value: str) -> bool:
        """
        Returns True if value represents a literal string (pure text in quotes),
        False if it contains expressions, variables, operations, objects, arrays, etc.

        Valid examples: "Hello world", 'Hi there', "Today's Practice"
        Invalid examples: {dynamicGreeting}, user.name, count + 1, {"Expr " + name}
        """
        if value is None:
            return False

        s = value.strip()

        # If wrapped in braces, likely an expression
        if s.startswith("{") and s.endswith("}"):
            return False

        # Check for operators and special chars that indicate expressions
        if re.search(r"[+*/\{\}|\&\[\]=]", s):
            return False

        # Check for property access or function calls
        if re.search(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*|\s*\()", s):
            return False

        # Check for conditionals
        if re.search(r"\?\s{0,3}\(", s):
            return False

        return True

    def process_text(self, file_alias: str, text: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Process text with parser (JSXParser or GenericScopeParser).
        Returns (list_of_path_strings, merged_json_dict).
        """
        # Initialize parser
        if self.mode == "jsx":
            parser = JSXParser(
                self.param,
                match_all=self.match_all,
                is_attribute_mode=self.is_attribute_mode,
                no_standard=self.no_standard,
            )
        else:
            if not (self.start_regex and self.end_regex):
                raise ValueError("Generic mode requires start_regex and end_regex.")
            parser = GenericScopeParser(self.param, self.start_regex, self.end_regex, match_all=self.match_all)

        out_lines, merged_json = [], {}

        for stack, tag, key_matched, value in parser.parse(text, []):
            # Filter by only_strings option
            if self.only_strings:
                is_only_strings = self.check_value_if_it_is_just_string(value)
                if not is_only_strings:
                    continue

            # Filter by avoid_keys
            keys_to_avoid = None
            if self.avoid_keys:
                keys_to_avoid = [i.strip() for i in self.avoid_keys.split(",")]
                if self.avoid_keys_parameter == self.CONTAINS:
                    if any(x in (key_matched or "") or x in tag or x in (value or "") for x in keys_to_avoid):
                        continue
                elif self.avoid_keys_parameter == self.EQUALS:
                    if any(x == (key_matched or "") or x == tag or x == (value or "") for x in keys_to_avoid):
                        continue

            # Build path tokens based on mode
            if self.is_attribute_mode:
                # Attribute mode: extract key="value"
                if value is None:
                    continue

                effective_key = key_matched if (self.match_all and key_matched) else self.param
                tokens = self._build_path_tokens_with_key(file_alias, stack, effective_key)

                # Additional avoid_keys filtering on tokens
                if self.avoid_keys and keys_to_avoid:
                    if self.avoid_keys_parameter == self.CONTAINS:
                        if any(x in token for token in tokens for x in keys_to_avoid):
                            continue
                    elif self.avoid_keys_parameter == self.EQUALS:
                        if any(x == token for token in tokens for x in keys_to_avoid):
                            continue

                if tokens:
                    out_lines.append(path_join(tokens))
                    if self.convert_to_json:
                        j = self._record_text_kv(tokens, value)
                        merged_json = self.deep_merge(merged_json, j)
            else:
                # Tag-content mode: extract inner text
                tag_name = tag

                # Keep the tag name as a key in the hierarchy
                if self.no_standard and (tag_name.lower() in STANDARD_HTML_TAGS):
                    tokens = self._nearest_kept_ancestor_tokens(file_alias, stack)
                else:
                    effective_key = tag_name
                    tokens = self._build_path_tokens_with_key(file_alias, stack, effective_key)

                # Additional avoid_keys filtering on tokens
                if self.avoid_keys and keys_to_avoid:
                    if self.avoid_keys_parameter == self.CONTAINS:
                        if any(x in token for token in tokens for x in keys_to_avoid):
                            continue
                    elif self.avoid_keys_parameter == self.EQUALS:
                        if any(token == x for token in tokens for x in keys_to_avoid):
                            continue

                if tokens and value:
                    if self.convert_to_json:
                        j = self._record_text_kv(tokens, value)
                        merged_json = self.deep_merge(merged_json, j)
                    out_lines.append(path_join(tokens))

        # Apply pruning for attribute mode
        if self.is_attribute_mode:
            if not self.include_value:
                if self.include_key:
                    merged_json = self.prune_to_key(merged_json, self.param, -1)
                else:
                    merged_json = self.prune_to_key(merged_json, self.param, -2)

        return out_lines, merged_json

    def json_to_js_literal(self, data: Dict[str, Any], indent: int = 2) -> str:
        """
        Convert JSON dict to JS literal (unquoted keys).
        E.g., {"key": "value"} => {key: "value"}
        """
        text = json.dumps(data, ensure_ascii=False, indent=indent)
        # Remove quotes from simple keys
        text = re.sub(r'"([A-Za-z_][A-Za-z0-9_]*)":', r"\1:", text)
        return text

    def _nearest_kept_ancestor_tokens(self, file_root_token: str, stack: List[str]) -> List[str]:
        """
        Anchor for flattened text:
        - If dropping standard tags, anchor at the deepest NON-standard
            ancestor present in stack. If none exists, anchor at root.
        - If not dropping, keep the entire stack.
        """
        return kept_prefix(file_root_token, stack, drop_standard=self.no_standard)

    def run(self, path: str) -> Tuple[str, Optional[str]]:
        """
        Main orchestrator: process file or directory.
        Returns (text_result, json_result_or_None).

        Scans files matching file_extensions, processes each with parser,
        merges JSON results, and returns formatted output.
        """
        all_lines: List[str] = []
        merged_json: Dict[str, Any] = {}

        file_patterns = self.file_extensions
        for fp in list_files(path, file_patterns):
            try:
                text = read_text(fp)
            except Exception as e:
                all_lines.append(f"<<ERROR reading {fp}: {e}>>")
                continue

            # Derive file-root token from filename (prefer exported name, fallback to filename)
            base = os.path.splitext(os.path.basename(fp))[0]
            export_m = re.search(r"\bexport\s+default\s+function\s+([A-Za-z_]\w*)", text)
            if not export_m:
                # covers: "export default DashboardPage" (identifier)
                export_m = re.search(r"\bexport\s+default\s+([A-Za-z_]\w*)\b", text)

            if export_m:
                file_root = export_m.group(1)  # keep EXACT identifier: "DashboardPage"
            else:
                # fallback: PascalCase filename
                file_root = base[0:1].upper() + base[1:]

            lines, j = self.process_text(file_root, text)

            if lines:
                all_lines.append(f"# File: {fp}")
                all_lines.extend(lines)
            if self.convert_to_json and j:
                merged_json = self.deep_merge(merged_json, j)

        result_text = "\n".join(all_lines) if all_lines else "(no matches)"
        json_text = None

        if self.convert_to_json:
            if self.with_quotation_marks:
                json_text = json.dumps(merged_json, ensure_ascii=False, indent=self.indentation)
            else:
                json_text = self.json_to_js_literal(merged_json, indent=self.indentation)

        return result_text, json_text
