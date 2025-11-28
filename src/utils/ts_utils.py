"""TypeScript/JavaScript object loading and serialization utilities."""

import re
import json


_TS_EXPORT_RE = re.compile(r'^\s*export\s+default\s*', re.IGNORECASE)


def strip_export_default(src: str) -> str:
    """Remove a leading `export default` (if present)."""
    return _TS_EXPORT_RE.sub("", src, count=1).strip()


def to_json_ish(src: str) -> str:
    """
    Convert a TS object literal into valid JSON:
      - Ensure keys are quoted
      - Convert single-quoted strings → double-quoted
      - Remove trailing commas
      - Remove optional semicolon at end
    This is not a full JS parser, but works for object/array/string/number/bool/null.
    """
    s = strip_export_default(src)
    s = re.sub(r';\s*$', '', s)
    s = re.sub(r'(?m)(^|[{,\s])([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', s)
    
    def _s2d(m):
        inner = m.group(1).replace(r'\"', '"')
        inner = inner.replace(r"\\'", r"\u0027")
        inner = inner.replace("'", r"\u0027")
        return '"' + inner + '"'
    
    s = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", _s2d, s, flags=re.DOTALL)
    s = re.sub(r',(\s*[}\]])', r'\1', s)
    return s


def load_ts_object(text: str) -> dict:
    """Parse a TS/JS object (`export default { ... }` or `{ ... }`) to dict safely."""
    js = to_json_ish(text)
    return json.loads(js)


def _esc_ts(s: str) -> str:
    """Only escape backslash and single quote; leave double quotes alone."""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def dump_ts_object(obj: dict, emit_export_default: bool = True, indent: int = 2) -> str:
    """Deterministic pretty TS object: single-quoted strings, sorted keys, optional export default."""
    def _dump(v, lvl=0):
        sp = ' ' * (indent * lvl)
        if v is None:
            return 'null'
        if isinstance(v, bool):
            return 'true' if v else 'false'
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str):
            return "'" + _esc_ts(v) + "'"
        if isinstance(v, list):
            inner = ',\n'.join(sp + ' ' * indent + _dump(x, lvl + 1) for x in v)
            return '[\n' + inner + '\n' + sp + ']'
        if isinstance(v, dict):
            items = []
            for k in sorted(v.keys()):
                kk = k if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', k) else "'" + _esc_ts(k) + "'"
                items.append(sp + ' ' * indent + f"{kk}: " + _dump(v[k], lvl + 1))
            return '{\n' + ',\n'.join(items) + '\n' + sp + '}'
        return "'" + _esc_ts(str(v)) + "'"

    body = _dump(obj, 0)
    return (f"export default {body}\n" if emit_export_default else body + "\n")
