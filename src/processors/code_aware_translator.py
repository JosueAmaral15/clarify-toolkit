#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code-Aware JSON Translator for Clarify
---------------------------------------
Translate visible text to {<root>.<path>} using a dictionary (and inverse).
Designed for JSX/React code translation while preserving code structure.

Phase 3.11 - Import Tree Analogy: FOLHA
Esta é uma FOLHA na árvore de importações:
- Não importa arquivos do projeto
- Importa apenas bibliotecas padrão (re, typing)
- Fornece funcionalidade atômica (processamento de texto)
- Totalmente reutilizável e testável

Author: Josué Amaral
Date: 2025-12-24
"""

import re
from typing import Dict, Any, List


class CodeAwareJSONTranslator:
    """
    Translate visible text to {<root>.<path>} using a dictionary (and inverse).
    
    Goals:
    • Translate only in "code scope" that makes sense:
        - JSX text nodes (between '>' and '<')
        - String literals in code
      and SKIP:
        - Anything inside {...} expressions
        - Inside JSX tags/attributes (<Tag ...>)
        - Type annotations and identifiers like React.ReactNode
    • Configurable root alias (default: 't'), e.g. {t.pages.home.title}
    • Never break existing placeholders; protect existing {root.*} blocks
    • Inverse: turn {root.*} back into original strings using the same dictionary
    """
    
    _re_jsx_tag = re.compile(r"<[^>]*>")  # a rough "inside tag" region
    _re_placeholder = re.compile(r"\{([A-Za-z_]\w*)(?:\.[A-Za-z0-9_]+)+\}")  # {t.pages.home.title}
    _re_string = re.compile(
        r"""
        (?P<q>['"])                # opening quote
        (?P<body>(?:\\.|(?!\1).)*) # body allowing escapes
        \1                         # closing quote
        """,
        re.VERBOSE | re.DOTALL,
    )
    
    _SMART_TO_STRAIGHT = str.maketrans(
        "''" + '""' + "‛‟",
        "'''" + '"""'
    )
    
    def __init__(self, dictionary: dict, root_name: str = "t"):
        self.root = root_name
        # flat: "pages.contact.hero.subtitle" -> "We\'re here ..."
        self.flat = self._flatten(dictionary)
        
        # Build variants → key map (multiple textual forms for each value)
        pairs: list[tuple[str, str]] = []
        for key, val in self.flat.items():
            if not isinstance(val, str) or not val.strip():
                continue
            for vv in self._variants_for_value(val):
                pairs.append((vv, key))
        
        # Sort by length (desc) so longer phrases win and avoid partial overlaps
        pairs.sort(key=lambda kv: len(kv[0]), reverse=True)
        
        # Keep as lists for fast iteration in the scanner
        self._variant_values = [p[0] for p in pairs]
        self._variant_keys = [p[1] for p in pairs]
    
    @staticmethod
    def _normalize_quotes(s: str) -> str:
        """Normalize curly quotes to straight, and unescape common HTML entities."""
        if not isinstance(s, str):
            return s
        s2 = s.translate(CodeAwareJSONTranslator._SMART_TO_STRAIGHT)
        # normalize common HTML entities
        s2 = s2.replace("&apos;", "'").replace("&#39;", "'") \
            .replace("&quot;", '"').replace("&#34;", '"')
        return s2
    
    @staticmethod
    def _unescape_backslashes(s: str) -> str:
        """
        Convert common backslash-escaped quotes into literal quotes, without touching other escapes.
        We handle simple forms: \' and \"
        """
        if not isinstance(s, str):
            return s
        return s.replace(r"\'", "'").replace(r"\"", '"')
    
    @staticmethod
    def _variants_for_value(v: str) -> list[str]:
        """
        Generate acceptable textual variants for a dictionary value:
        - raw v
        - normalized smart quotes → straight
        - unescaped (\' → ')
        - HTML-entity-decoded variants
        - combinations thereof
        Deduplicated, keep non-empty strings only.
        """
        if not isinstance(v, str) or not v.strip():
            return []
        
        variants = set()
        base = v
        
        # 1) raw
        variants.add(base)
        
        # 2) unescape backslash quotes
        unesc = CodeAwareJSONTranslator._unescape_backslashes(base)
        variants.add(unesc)
        
        # 3) normalize smart + html entities on both
        for s in (base, unesc):
            s2 = CodeAwareJSONTranslator._normalize_quotes(s)
            variants.add(s2)
            
            # Also try entity→char then normalize (covers cases like &apos; already in source)
            s3 = (s.replace("&apos;", "'")
                  .replace("&#39;", "'")
                  .replace("&quot;", '"')
                  .replace("&#34;", '"'))
            variants.add(CodeAwareJSONTranslator._normalize_quotes(s3))
        
        # 4) last-pass trim (no-op if not needed)
        return [x for x in variants if x]
    
    # ---------- public API ----------
    
    def translate_text_to_refs(self, content: str) -> str:
        """
        Forward: Replace visible text with {root.path}.
        Only in safe scopes (JSX text nodes and string literals), never inside {...} or tags.
        """
        if not content.strip():
            return content
        
        # 0) protect existing placeholders so we never touch inside/around them
        content, guards = self._mask_existing_placeholders(content)
        
        # 1) replace in JSX text nodes (outside tags and outside {...})
        content = self._replace_in_jsx_text_nodes(content)
        
        # 2) replace in string literals (again skipping {...})
        content = self._replace_in_string_literals(content)
        
        # 3) unmask placeholders
        content = self._unmask_placeholders(content, guards)
        
        # 4) consolidate fragmented placeholders (auto-fix)
        content = self._consolidate_fragmented_placeholders(content)
        
        return content
    
    def translate_refs_to_text(self, content: str) -> str:
        """
        Inverse: Replace {root.path.to.key} with dictionary value.
        Only if key exists; otherwise leave as-is.
        """
        def _repl(m: re.Match) -> str:
            alias = m.group(1)
            if alias != self.root:
                return m.group(0)
            keypath = m.group(0)[1:-1]  # strip {}
            val = self.flat.get(keypath[len(self.root) + 1:], None) if "." in keypath else None
            return val if isinstance(val, str) else m.group(0)
        
        return self._re_placeholder.sub(_repl, content)
    
    # ---------- core steps ----------
    
    def _replace_in_jsx_text_nodes(self, s: str) -> str:
        """
        Replace plain text BETWEEN '>' and '<', excluding braces blocks and tags.
        """
        out = []
        i = 0
        n = len(s)
        while i < n:
            gt = s.find(">", i)
            if gt == -1:
                out.append(s[i:])
                break
            out.append(s[i:gt + 1])  # include '>'
            lt = s.find("<", gt + 1)
            if lt == -1:
                # trailing text node to EOF
                segment = s[gt + 1:]
                out.append(self._replace_outside_braces(segment))
                break
            segment = s[gt + 1:lt]
            out.append(self._replace_outside_braces(segment))
            i = lt
        return "".join(out)
    
    def _replace_in_string_literals(self, s: str) -> str:
        """
        Replace only inside string literals, but not if the string looks like a type/identifier blob.
        """
        out = []
        last = 0
        for m in self._re_string.finditer(s):
            out.append(s[last:m.start()])
            q = m.group("q")
            body = m.group("body")
            new_body = self._replace_outside_braces(body, inside_string=True)
            out.append(q + new_body + q)
            last = m.end()
        out.append(s[last:])
        return "".join(out)
    
    def _replace_outside_braces(self, text: str, inside_string: bool = False) -> str:
        """
        Replace occurrences of known values with {root.key} only when NOT inside {...}.
        Heuristics:
        • Skip chunks that obviously look like identifiers/types (contain dots and no spaces)
        • Don't replace if either neighbor char is alnum or '.' (avoid breaking identifiers)
        """
        if not text.strip():
            return text
        
        # quick skip: likely code-ish (React.ReactNode etc.) with no spaces
        if not inside_string and "." in text and " " not in text.strip():
            return text
        
        out = []
        i = 0
        depth = 0
        while i < len(text):
            ch = text[i]
            if ch == "{":
                depth += 1
                out.append(ch)
                i += 1
                continue
            if ch == "}":
                depth = max(0, depth - 1)
                out.append(ch)
                i += 1
                continue
            
            if depth == 0:
                # Try to match any known variant at this position
                replaced = False
                for idx, val in enumerate(self._variant_values):
                    if not val:
                        continue
                    if text.startswith(val, i):
                        left = text[i - 1] if i > 0 else ""
                        right = text[i + len(val)] if i + len(val) < len(text) else ""
                        # neighbors: don't glue into identifiers or dotted tokens
                        if (left.isalnum() or left == ".") or (right.isalnum() or right == "."):
                            continue
                        key = self._variant_keys[idx]
                        out.append("{" + self.root + "." + key + "}")
                        i += len(val)
                        replaced = True
                        break
                if replaced:
                    continue
            
            # default
            out.append(ch)
            i += 1
        
        return "".join(out)
    
    # ---------- fragmentation consolidation ----------
    
    def _consolidate_fragmented_placeholders(self, s: str) -> str:
        """
        Auto-fix fragmented placeholders: merge adjacent placeholders into single unit.
        Example: '{t.our} {t.products}' → '{t.ourProducts}' (if values are "our" and "products")
        
        Algorithm:
        1. Find sequences of 2+ adjacent placeholders (separated only by whitespace)
        2. Retrieve original text values for each placeholder
        3. Generate consolidated key from concatenated values
        4. Replace fragment sequence with single placeholder
        """
        # Pattern: 2 or more placeholders separated by whitespace
        pattern = re.compile(
            r'(\{' + re.escape(self.root) + r'\.[A-Za-z0-9_.]+\})'  # first placeholder
            r'(\s+\{' + re.escape(self.root) + r'\.[A-Za-z0-9_.]+\})+'  # 1+ more placeholders
        )
        
        def consolidate_match(m: re.Match) -> str:
            full_match = m.group(0)
            
            # Extract all placeholder keys
            placeholder_pattern = re.compile(r'\{' + re.escape(self.root) + r'\.([A-Za-z0-9_.]+)\}')
            keys = placeholder_pattern.findall(full_match)
            
            if len(keys) < 2:
                return full_match  # Not fragmented, keep as-is
            
            # Get original text values
            values = []
            for key in keys:
                val = self.flat.get(key)
                if val and isinstance(val, str):
                    values.append(val)
                else:
                    # Can't consolidate if any key is missing/invalid
                    return full_match
            
            # Generate consolidated key from concatenated text
            # Example: ["Our", "products"] → "ourProducts" (camelCase)
            consolidated_text = ' '.join(values)
            consolidated_key = self._generate_consolidated_key(keys, consolidated_text)
            
            # Return single placeholder
            return '{' + self.root + '.' + consolidated_key + '}'
        
        return pattern.sub(consolidate_match, s)
    
    def _generate_consolidated_key(self, fragment_keys: list[str], consolidated_text: str) -> str:
        """
        Generate a consolidated key name from fragment keys and their combined text.
        
        Strategy:
        1. Use first fragment's path prefix (e.g., "pages.home" from "pages.home.title")
        2. Generate suffix from consolidated text (camelCase)
        3. If result already exists in dict, use it; otherwise create new synthetic key
        """
        # Try to extract common prefix from fragment keys
        if not fragment_keys:
            return "consolidated"
        
        # Split first key by dots to get path components
        parts = fragment_keys[0].split('.')
        
        if len(parts) > 1:
            # Use parent path: "pages.home.title" → prefix "pages.home"
            prefix = '.'.join(parts[:-1])
        else:
            # No parent, use root-level
            prefix = ""
        
        # Generate camelCase suffix from consolidated text
        # Example: "Our products is what you need" → "ourProductsIsWhatYouNeed"
        words = consolidated_text.split()
        if not words:
            suffix = "merged"
        else:
            suffix = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        
        # Build final key
        if prefix:
            candidate = f"{prefix}.{suffix}"
        else:
            candidate = suffix
        
        # Check if this key already exists in dictionary
        # If yes, use it (perfect match!); if no, use synthetic key
        if candidate in self.flat:
            return candidate
        
        # Synthetic key (mark as auto-generated)
        return f"{prefix}.autoMerged_{suffix}" if prefix else f"autoMerged_{suffix}"
    
    # ---------- masking helpers ----------
    
    def _mask_existing_placeholders(self, s: str) -> tuple[str, List[str]]:
        guards: List[str] = []
        
        def _mask(m: re.Match) -> str:
            idx = len(guards)
            guards.append(m.group(0))
            return f"@@TREF{idx}@@"
        
        return self._re_placeholder.sub(_mask, s), guards
    
    def _unmask_placeholders(self, s: str, guards: List[str]) -> str:
        for i, tok in enumerate(guards):
            s = s.replace(f"@@TREF{i}@@", tok)
        return s
    
    # ---------- dictionary flatten ----------
    
    def _flatten(self, d: dict, prefix: str = "") -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in (d or {}).items():
            kk = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.update(self._flatten(v, kk))
            else:
                out[kk] = v
        return out
