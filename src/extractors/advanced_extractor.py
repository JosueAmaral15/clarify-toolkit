#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Advanced Extractor - Core Business Logic for Parameter Extraction.
# pylint: disable=consider-using-in  # Explicit comparisons for clarity

Extracted from add/main.py (Sprint 2, Task 1.1)
Handles advanced extraction features:
- Hierarchical path building with normalization
- Nested JSON generation with deep merge
- Numeric hierarchy removal algorithm
- String literal validation (only_strings mode)
- Advanced filtering with avoid_keys
- Attribute vs Tag-content modes

Author: Extracted by GitHub Copilot
Date: 2025-12-25
Version: 2.9.115
"""

from __future__ import annotations

import os
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Union

# Type aliases
JSONLike = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

# Standard HTML tags (imported from utils)
STANDARD_HTML_TAGS = {
    'html','head','title','base','link','meta','style','script','noscript',
    'body','section','nav','article','aside','h1','h2','h3','h4','h5','h6','header',
    'footer','address','main','p','hr','pre','blockquote','ol','ul','li','dl','dt','dd',
    'figure','figcaption','div','a','em','strong','small','s','cite','q','dfn','abbr','ruby',
    'rb','rt','rtc','rp','data','time','code','var','samp','kbd','sub','sup','i','b','u',
    'mark','bdi','bdo','span','br','wbr','ins','del','picture','source','img','iframe',
    'embed','object','param','video','audio','track','map','area','table','caption',
    'colgroup','col','tbody','thead','tfoot','tr','td','th','form','label','input',
    'button','select','datalist','optgroup','option','textarea','output','progress',
    'meter','fieldset','legend','details','summary','dialog','slot','template','canvas'
}


def is_standard_tag(name: str) -> bool:
    """Check if tag name is a standard HTML tag."""
    return name.lower() in STANDARD_HTML_TAGS


def kept_prefix(file_root: str, stack: list[str], drop_standard: bool) -> list[str]:
    """
    Return [file_root] plus the stack up to the deepest NON-standard tag
    (when drop_standard=True). If none exists, just [file_root].
    If drop_standard=False, return [file_root] + full stack.
    """
    if not drop_standard:
        return [file_root] + stack

    # find deepest custom tag from right to left
    for i in range(len(stack) - 1, -1, -1):
        if not is_standard_tag(stack[i]):
            return [file_root] + stack[:i + 1]
    return [file_root]


def smart_truncate(text: str, limit: Optional[str], avoid_cut: bool, avoid_cut_direction: str = "before") -> str:
    """
    Truncate text by char limit. If limit is 'all' or None -> return original.
    If avoid_cut=True, cut at whitespace boundary:
      - 'before': cut at last whitespace <= limit (existing behavior)
      - 'after': cut at next whitespace >= limit (new behavior)
    """
    # pylint: disable=too-many-return-statements  # Multiple early exit conditions
    if not text or limit in (None, 'all', 'ALL', 'All'):
        return text
    try:
        n = int(limit)
    except Exception:  # pylint: disable=broad-exception-caught  # Parse robustness
        return text

    if n <= 0 or len(text) <= n:
        return text

    sub = text[:n]

    if not avoid_cut:
        return sub

    # Direction-aware cutting
    if avoid_cut_direction == "after":
        # Search AFTER limit for next whitespace
        for i in range(n, len(text)):
            if text[i].isspace():
                return text[:i].rstrip()
        # No whitespace found after limit, return full text
        return text
    else:
        # Original "before" behavior: cut at last whitespace before limit
        # If we ended already on whitespace, just strip trailing whitespace.
        if sub[-1].isspace():
            return sub.rstrip()

        # Find the last whitespace run before the cut and cut right before it.
        m = re.search(r'\s+\S*$', sub, flags=re.UNICODE)
        if m:
            cut = m.start()
            if cut > 0:
                return sub[:cut].rstrip()

        # Fallback: no whitespace found in the window (a very long first word).
        return sub


def normalize_token(s: str, case_style: str, to_upper: bool) -> str:
    """
    Normalize a string to snake/camel/pascal/kebab/preserve; drop non-alnum (after spaces);
    optionally uppercase whole token.
    Splits camelCase/PascalCase into words before applying conversion.
    """
    s = s.strip()
    
    # Special handling for 'preserve' mode - keep original case
    if case_style == "preserve" or case_style == "none":
        # Only remove non-alphanumeric characters, keep original case
        cleaned = re.sub(r"[^0-9A-Za-z]+", "_", s)
        # Remove leading/trailing underscores
        token = cleaned.strip("_")
        if to_upper:
            token = token.upper()
        return token
    
    # Step 1: Split camelCase/PascalCase into separate words
    # Insert space before uppercase letters that follow lowercase or are followed by lowercase
    with_spaces = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)  # lowerUpper → lower Upper
    with_spaces = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', with_spaces)  # XMLParser → XML Parser
    
    # Step 2: Convert any remaining non-alphanumeric into space
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", with_spaces)
    
    # Step 3: Split into words
    words = [w for w in cleaned.strip().split() if w]
    
    if not words:
        token = ""
    else:
        if case_style == "snake":
            token = "_".join(w.lower() for w in words)
        elif case_style == "kebab":
            token = "-".join(w.lower() for w in words)
        elif case_style == "camel":
            head = words[0].lower()
            tail = [w[:1].upper() + w[1:].lower() for w in words[1:]]
            token = head + "".join(tail)
        elif case_style == "pascal":
            token = "".join(w[:1].upper() + w[1:].lower() for w in words)
        else:
            # default snake
            token = "_".join(w.lower() for w in words)
    if to_upper:
        token = token.upper()
    return token


def path_join(parts: List[str]) -> str:
    """Join path parts with dots."""
    return ".".join([p for p in parts if p])


def read_text(path: str) -> str:
    """Read text file with UTF-8 encoding."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def list_files(root: str, patterns: Optional[List[str]] = None) -> List[str]:
    """List files in directory matching patterns."""
    files = []
    if os.path.isfile(root):
        files.append(root)
    else:
        for r, _, filenames in os.walk(root):
            for fn in filenames:
                if not patterns:
                    files.append(os.path.join(r, fn))
                else:
                    if any(fn.endswith(pat) for pat in patterns):
                        files.append(os.path.join(r, fn))
    return files


class AdvancedExtractor:
    """
    Advanced parameter/content extractor with hierarchical JSON generation.

    Features:
    - Attribute mode vs Tag-content mode
    - Normalize tokens (snake/camel/pascal/kebab)
    - Drop standard HTML tags
    - Include key/value in path
    - Only accept literal strings (no expressions)
    - Avoid specific keys with contains/equals matching
    - Remove numeric hierarchy with collapse algorithm
    - Deep merge nested JSON structures
    """

    # Constants for avoid_keys_parameter
    CONTAINS = "contains"
    EQUALS = "equals"

    # pylint: disable=too-many-positional-arguments  # Complex extractor configuration
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
        avoid_cut_direction: str = "before",
        to_upper: bool = False,
        only_strings: bool = False,
        is_attribute_mode: bool = False,
        start_regex: Optional[str] = None,
        end_regex: Optional[str] = None,
        root_alias: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        use_class_names: bool = False,
    ):
        """
        Initialize AdvancedExtractor.

        Args:
            param: Parameter/attribute name to extract (or * for match_all)
            mode: 'jsx' or 'generic'
            avoid_keys: Comma-separated keys to avoid
            avoid_keys_parameter: 'contains' or 'equals'
            include_key: Include key in path
            include_value: Include normalized value in path
            no_standard: Drop standard HTML tags
            convert_to_json: Generate nested JSON output
            with_quotation_marks: Use JSON quotes vs JS literal
            indentation: JSON indent spaces
            case_style: 'snake'|'camel'|'pascal'|'kebab'
            limit: Character limit for normalization
            avoid_cut: Cut at word boundary
            avoid_cut_direction: Direction to search for word boundary ('before' or 'after')
            to_upper: Uppercase normalized tokens
            only_strings: Accept only literal strings (no expressions)
            is_attribute_mode: Extract attributes vs tag content
            start_regex: Start delimiter for generic mode
            end_regex: End delimiter for generic mode
            root_alias: Root key for file hierarchy
            file_extensions: File patterns to process
            use_class_names: Use class names as keys instead of HTML tags
        """
        self.param = param
        self.match_all = (param is None) or (not param.strip()) or (param.strip() == "*")
        self.mode = mode
        self.avoid_keys = avoid_keys
        self.avoid_keys_parameter = avoid_keys_parameter
        self.include_key = include_key
        self.include_value = include_value
        self.no_standard = no_standard
        self.convert_to_json = convert_to_json
        self.with_quotation_marks = with_quotation_marks
        self.only_strings = only_strings
        self.indentation = indentation
        self.case_style = case_style
        self.limit = limit
        self.avoid_cut = avoid_cut
        self.avoid_cut_direction = avoid_cut_direction
        self.to_upper = to_upper
        self.start_regex = start_regex
        self.end_regex = end_regex
        self.root_alias = root_alias or "Root"
        self.file_extensions = file_extensions
        self.is_attribute_mode = is_attribute_mode
        self.use_class_names = use_class_names

    def _apply_limit_to_key(self, key: str) -> str:
        """
        Apply character limit and avoid_cut logic to a key string.
        Used for both class names and JSON keys.
        """
        if self.limit in (None, 'all', 'ALL', 'All'):
            return key
        
        try:
            limit_num = int(self.limit)
        except ValueError:
            return key
        
        if limit_num <= 0 or len(key) <= limit_num:
            return key
        
        if self.avoid_cut:
            # Cut at word boundary (underscore or dash)
            if self.avoid_cut_direction == "after":
                # Search AFTER limit for next separator
                next_sep_pos = -1
                for i in range(limit_num, len(key)):
                    if key[i] in ('_', '-'):
                        next_sep_pos = i
                        break
                if next_sep_pos > 0:
                    return key[:next_sep_pos]
                # No separator found after, keep full key
                return key
            else:
                # Default: search BEFORE limit for last separator
                truncated = key[:limit_num]
                last_sep = max(truncated.rfind('_'), truncated.rfind('-'))
                if last_sep > 0:
                    return truncated[:last_sep]
                # No separator found, just truncate
                return truncated
        else:
            # Hard cut at limit
            return key[:limit_num]

    def _replace_stack_with_class_names(self, parser, stack: List[str]) -> List[str]:
        """
        Replace tag names in stack with class names where available.
        Used when use_class_names is enabled to convert entire path.
        """
        if not self.use_class_names or not hasattr(parser, 'class_map'):
            return stack
        
        modified_stack = []
        for i, tag in enumerate(stack):
            # Build the key for this position in the stack
            stack_up_to_here = tuple(stack[:i+1])
            stack_key = (stack_up_to_here, tag)
            
            # Look up class name for this tag at this position
            class_value = parser.class_map.get(stack_key)
            if class_value:
                # Join multiple classes with dash
                class_names = class_value.split()
                joined_class = "-".join(class_names) if class_names else tag
                # Apply limit to the class name
                limited_class = self._apply_limit_to_key(joined_class)
                modified_stack.append(limited_class)
            else:
                # No class found, use tag name
                modified_stack.append(tag)
        
        return modified_stack

    def _extract_class_name_from_parser(self, parser, stack: List[str], tag: str) -> Optional[str]:
        """
        Extract class attribute from parser's class_map.
        Returns joined class names with dash if multiple, or None if no class found.
        """
        if not self.use_class_names:
            return None
        
        # Check if parser has class_map (only JSXParser)
        if not hasattr(parser, 'class_map'):
            return None
        
        # Look up class using stack + tag as key
        stack_key = (tuple(stack), tag)
        class_value = parser.class_map.get(stack_key)
        
        if class_value:
            # Multiple classes: join with dash (e.g., "btn primary" -> "btn-primary")
            class_names = class_value.split()
            return "-".join(class_names) if class_names else None
        
        return None

    def _filter_standard(self, path: List[str]) -> List[str]:
        """Filter out standard HTML tags if no_standard=True."""
        if not self.no_standard:
            return path
        return [p for p in path if not is_standard_tag(p)]

    def _build_path_tokens(
        self, file_root_token: str, stack: List[str], tag: str, value_text: Optional[str]  # pylint: disable=unused-argument  # Signature consistency
    ) -> List[str]:
        """
        Build path tokens from file-root + stack + tag,
        optionally adding key and normalized value.
        """
        tokens: List[str] = [file_root_token] + stack
        tokens = self._filter_standard(tokens)

        if self.include_key or (not self.include_key and not self.include_value):
            tokens.append(self.param)

        if value_text is not None and self.include_value:
            trimmed = smart_truncate(value_text, self.limit, self.avoid_cut)
            norm = normalize_token(trimmed, self.case_style, self.to_upper)
            if norm:
                tokens.append(norm)

        return tokens

    def _build_path_tokens_with_key(
        self, file_root_token: str, stack: List[str],
        key_for_path: Optional[str]
    ) -> List[str]:
        """Build path tokens including the matched key (attribute mode)."""
        tokens = [file_root_token] + self._filter_standard(stack)

        # Include the key segment when requested / in match-all
        if self.include_key or self.match_all or (not self.include_key and not self.include_value):
            if key_for_path and self.is_attribute_mode:
                tokens.append(key_for_path)

        return tokens

    def _nearest_kept_ancestor_tokens(self, file_root_token: str, stack: List[str]) -> List[str]:
        """
        Anchor for flattened text:
        - If dropping standard tags, anchor at the deepest NON-standard
          ancestor present in stack. If none exists, anchor at root.
        - If not dropping, keep the entire stack.
        """
        return kept_prefix(file_root_token, stack, drop_standard=self.no_standard)

    def _record_text_kv(self, path_tokens: List[str], raw_value: str) -> Dict[str, Any]:
        """
        Build a small tree that, at path_tokens, adds a single key:value pair
        derived from raw_value. The key is normalized using current case settings;
        the value is the original raw_value.
        """
        # First normalize the entire raw value to get the key
        key = normalize_token(raw_value, self.case_style, self.to_upper) or "text"
        
        # Apply limit to the normalized key using the helper method
        key = self._apply_limit_to_key(key)

        # Build small tree: (... path_tokens ...) -> { key: raw_value }
        root: Dict[str, Any] = {}
        node = root
        for t in path_tokens:
            node = node.setdefault(t, {})
        node[key] = raw_value
        return root

    def _record_text_bucket(self, path_tokens: List[str], value: str) -> Dict[str, Any]:
        """
        Insert value into a '_text' list under the given path:
        DashboardPage: { Section: { _text: [ "line1", "line2", ... ] } }
        """
        root: Dict[str, Any] = {}
        node = root
        for t in path_tokens:
            node = node.setdefault(t, {})
        bucket = node.setdefault("_text", [])
        if isinstance(bucket, list):
            bucket.append(value)
        else:
            node["_text"] = [bucket, value]
        return root

    def deep_merge(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dict trees recursively."""
        for k, v in b.items():
            if k in a and isinstance(a[k], dict) and isinstance(v, dict):
                a[k] = self.deep_merge(a[k], v)
            else:
                a[k] = v
        return a

    def find_paths_to_key(
        self, structure: JSONLike, word_key: str,
        current_path: Optional[List[str]] = None
    ) -> List[List[str]]:
        """Return a list of key paths leading to every occurrence of word_key."""
        if current_path is None:
            current_path = []
        paths = []

        if isinstance(structure, dict):
            for k, v in structure.items():
                new_path = current_path + [k]
                if k == word_key:
                    paths.append(new_path)
                else:
                    paths.extend(self.find_paths_to_key(v, word_key, new_path))

        elif isinstance(structure, list):
            for i, item in enumerate(structure):
                new_path = current_path + [f"[{i}]"]
                paths.extend(self.find_paths_to_key(item, word_key, new_path))

        return paths

    def get_subtree_at_path(self, structure: JSONLike, path: List[str]) -> Optional[JSONLike]:
        """Navigate a path (list of keys) inside a nested dict and return subtree."""
        node = structure
        for key in path:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return None
        return node

    def build_tree_from_path(self, path: List[str], leaf_value: Any) -> Dict[str, Any]:
        """Build nested dict from path ending in leaf_value."""
        result = leaf_value
        for key in reversed(path):
            result = {key: result}
        return result

    def merge_dicts(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dict trees recursively."""
        result = dict(a)
        for k, v in b.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = self.merge_dicts(result[k], v)
            else:
                result[k] = v
        return result

    def prune_to_key(self, structure: JSONLike, word_key: str, depth_offset: int = 0) -> Optional[JSONLike]:
        """
        Returns a structure preserving only branches leading to word_key,
        adjusting cut depth by depth_offset:
        - 0: cut exactly at word_key
        - negative: move up (-1 removes one more level to the left)
        - positive: include deeper levels (+1 adds one more level to the right)
        """
        paths = self.find_paths_to_key(structure, word_key)
        if not paths:
            return None

        final_tree: Dict[str, Any] = {}

        for path in paths:
            if depth_offset < 0:
                new_path = path[:depth_offset] if abs(depth_offset) < len(path) else []
                leaf = path[depth_offset] if new_path else word_key
            elif not depth_offset:
                new_path = path
                leaf = word_key
            else:
                # positive depth: expand deeper into subtree
                subtree = self.get_subtree_at_path(structure, path)
                for _ in range(depth_offset):
                    if isinstance(subtree, dict) and subtree:
                        first_key = next(iter(subtree))
                        path.append(first_key)
                        subtree = subtree[first_key]
                    else:
                        break
                new_path = path
                leaf = subtree

            if new_path:
                branch = self.build_tree_from_path(new_path, leaf)
                final_tree = self.merge_dicts(final_tree, branch)

        return final_tree or None

    def remove_key(self, structure: JSONLike, key_to_remove: str) -> JSONLike:
        """
        Recursively remove all occurrences of key_to_remove from nested structure.

        Args:
            structure: nested structure (dict/list/scalars)
            key_to_remove: key name to delete

        Returns:
            New structure with all occurrences of the key removed.
        """
        if isinstance(structure, dict):
            new_dict = {}
            for key, value in structure.items():
                if key == key_to_remove:
                    continue
                new_dict[key] = self.remove_key(value, key_to_remove)
            return new_dict

        elif isinstance(structure, list):
            return [self.remove_key(item, key_to_remove) for item in structure]

        else:
            return structure

    def remove_key_with_collapse(self, structure: JSONLike, key_to_remove: str) -> JSONLike:
        """
        Remove key_to_remove throughout structure.
        If, after removal, a child dict becomes empty, collapse the value
        of that child to the key name itself.

        Example:
            { 'StatsCard': {} } -> { 'StatsCard': 'StatsCard' }

        This is the CRITICAL algorithm for removing numeric hierarchy.
        """
        if isinstance(structure, dict):
            new_dict: Dict[str, Any] = {}

            for k, v in structure.items():
                if k == key_to_remove:
                    # remove this key completely
                    continue

                nv = self.remove_key_with_collapse(v, key_to_remove)

                # If child result is an empty dict, collapse to key name
                if isinstance(nv, dict) and not nv:
                    new_dict[k] = k
                else:
                    new_dict[k] = nv

            return new_dict

        if isinstance(structure, list):
            new_list: List[Any] = []
            for item in structure:
                ni = self.remove_key_with_collapse(item, key_to_remove)
                new_list.append(ni)
            return new_list

        # Scalars remain unchanged
        return structure

    # pylint: disable=too-many-return-statements  # Multiple validation conditions
    def check_value_if_it_is_just_string(self, value: str) -> bool:
        """
        Returns True if value represents only a pure literal string,
        and False if it contains expressions, variables, operations, objects,
        arrays, conditionals, numbers, or anything outside quotes.

        Valid examples:
            "Hello world"
            'Hi there'
            "Today's Practice"

        Invalid examples:
            {dynamicGreeting}
            user.name
            count + 1
            {"Expr " + name}
            {'x' if cond else 'y'}
        """
        if value is None:
            return False

        s = value.strip()

        # If has external braces, it's an expression
        if s.startswith("{") and s.endswith("}"):
            return False

        # Check for operators and special chars
        if re.search(r"[+*/\{\}|\&\[\]=]", s):
            return False

        # Check for property access, variables, or functions
        if re.search(r"[A-Za-z_]\w*(\.[A-Za-z_]\w*|\s*\()", s):
            return False

        # Any braces, brackets, operators → invalid
        if re.search(r"[\{\}+*/=|\&\[\]]", s):
            return False

        # Ternary operator check
        if re.search(r"\?\s{0,3}\(", s):
            return False

        return True

    def process_text(self, file_alias: str, text: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Process text content and extract parameters/content.

        Returns:
            Tuple of (path_lines, merged_json_dict)
        """
        # Import parsers here to avoid circular dependency
        # pylint: disable=import-outside-toplevel  # Avoid circular import
        from .jsx_parser import JSXParser
        from .generic_parser import GenericScopeParser

        if self.mode == "jsx":
            parser = JSXParser(
                self.param,
                match_all=self.match_all,
                is_attribute_mode=self.is_attribute_mode,
                no_standard=self.no_standard
            )
        else:
            if not (self.start_regex and self.end_regex):
                raise ValueError("Generic mode requires start_regex and end_regex.")
            parser = GenericScopeParser(
                self.param,
                self.start_regex,
                self.end_regex,
                match_all=self.match_all
            )

        out_lines, merged_json = [], {}

        for stack, tag, key_matched, value in parser.parse(text, []):
            # Filter by only_strings if enabled
            if self.only_strings:
                if not self.check_value_if_it_is_just_string(value):
                    continue

            # Prepare avoid_keys filter
            keys_to_avoid = None
            if self.avoid_keys:
                keys_to_avoid = [i.strip() for i in self.avoid_keys.split(",")]
                # Check if should skip based on avoid_keys
                should_skip = False
                if self.avoid_keys_parameter == self.CONTAINS:
                    should_skip = any(
                        avoid_key in key_matched or avoid_key in tag or avoid_key in str(value)
                        for avoid_key in keys_to_avoid
                    )
                elif self.avoid_keys_parameter == self.EQUALS:
                    should_skip = any(x == key_matched or x == tag or x == value for x in keys_to_avoid)

                if should_skip:
                    continue

            # Process based on mode
            if self.is_attribute_mode:
                if value is None:
                    continue

                effective_key = (key_matched if (self.match_all and key_matched) else self.param)
                tokens = self._build_path_tokens_with_key(file_alias, stack, effective_key)

                # Additional token filtering
                if self.avoid_keys and keys_to_avoid:
                    should_skip_tokens = False
                    if self.avoid_keys_parameter == self.CONTAINS:
                        should_skip_tokens = any(any(x in token for token in tokens) for x in keys_to_avoid)
                    elif self.avoid_keys_parameter == self.EQUALS:
                        should_skip_tokens = any(any(x == token for token in tokens) for x in keys_to_avoid)

                    if should_skip_tokens:
                        continue

                if tokens:
                    out_lines.append(path_join(tokens))
                    if self.convert_to_json:
                        j = self._record_text_kv(tokens, value)
                        merged_json = self.deep_merge(merged_json, j)
            else:
                # TAG-CONTENT MODE
                tag_name = tag
                
                # Replace entire stack with class names if enabled
                if self.use_class_names:
                    modified_stack = self._replace_stack_with_class_names(parser, stack)
                else:
                    modified_stack = stack
                
                if self.no_standard and (tag_name.lower() in STANDARD_HTML_TAGS):
                    tokens = self._nearest_kept_ancestor_tokens(file_alias, modified_stack)
                else:
                    tokens = self._build_path_tokens_with_key(file_alias, modified_stack, None)

                # Additional token filtering
                if self.avoid_keys and keys_to_avoid:
                    should_skip_tokens = False
                    if self.avoid_keys_parameter == self.CONTAINS:
                        should_skip_tokens = any(any(x in token for token in tokens) for x in keys_to_avoid)
                    elif self.avoid_keys_parameter == self.EQUALS:
                        should_skip_tokens = any(token == x for token in tokens for x in keys_to_avoid)

                    if should_skip_tokens:
                        continue

                if tokens and value:
                    if self.convert_to_json:
                        j = self._record_text_kv(tokens, value)
                        merged_json = self.deep_merge(merged_json, j)
                    out_lines.append(path_join(tokens))

        # Post-process: prune if needed
        if self.is_attribute_mode:
            if not self.include_value:
                if self.include_key:
                    merged_json = self.prune_to_key(merged_json, self.param, -1)
                else:
                    merged_json = self.prune_to_key(merged_json, self.param, -2)

        return out_lines, merged_json

    def json_to_js_literal(self, data: Any, indent: int = 2) -> str:
        """Convert JSON to JavaScript literal (without quotes on keys)."""
        text = json.dumps(data, ensure_ascii=False, indent=indent)
        # Remove quotes from simple keys
        text = re.sub(r'\"([A-Za-z_][A-Za-z0-9_]*)\":', r'\1:', text)
        return text

    def run(self, path: str) -> Tuple[str, Optional[str]]:
        """
        Process a file or directory.

        Args:
            path: File or directory path

        Returns:
            Tuple of (text_result, json_result_or_None)
        """
        all_lines: List[str] = []
        merged_json: Dict[str, Any] = {}

        file_patterns = self.file_extensions
        for fp in list_files(path, file_patterns):
            try:
                text = read_text(fp)
            except Exception as e:  # pylint: disable=broad-exception-caught  # File read robustness
                all_lines.append(f"<<ERROR reading {fp}: {e}>>")
                continue

            # Derive file-root token from filename
            base = os.path.splitext(os.path.basename(fp))[0]

            # Try to find exported component/function name
            export_m = re.search(r'\bexport\s+default\s+function\s+([A-Za-z_]\w*)', text)
            if not export_m:
                export_m = re.search(r'\bexport\s+default\s+([A-Za-z_]\w*)\b', text)

            if export_m:
                file_root = export_m.group(1)
            else:
                # Fallback: Pascalize filename
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
