"""File discovery and I/O utilities."""

import os
import shutil
import fnmatch
from typing import Iterator, Optional, Sequence


def walk_files(root: str,
               include_globs: Sequence[str] | None = None,
               exclude_globs: Sequence[str] | None = None) -> Iterator[str]:
    """
    Recursively yield files under 'root' (file or directory). Uses fnmatch-style glob filters.
    - include_globs: if provided, file path must match at least one of them (relative or absolute).
    - exclude_globs: if provided, file path must NOT match any of them.
    """
    include_globs = [g.strip() for g in (include_globs or []) if g.strip()]
    exclude_globs = [g.strip() for g in (exclude_globs or []) if g.strip()]

    def _match_any(path: str, patterns: Sequence[str]) -> bool:
        if not patterns:
            return True
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
                return True
        return False

    def _match_none(path: str, patterns: Sequence[str]) -> bool:
        for pat in patterns:
            if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
                return False
        return True

    if os.path.isfile(root):
        if _match_any(root, include_globs) and _match_none(root, exclude_globs):
            yield root
        return

    for dirpath, _dirnames, filenames in os.walk(root):
        for f in filenames:
            path = os.path.join(dirpath, f)
            if _match_any(path, include_globs) and _match_none(path, exclude_globs):
                yield path


def read_text(path: str, max_bytes: Optional[int] = None) -> str:
    """Read text file with UTF-8 fallback to latin-1."""
    with open(path, "rb") as fh:
        data = fh.read() if max_bytes is None else fh.read(max_bytes)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="replace")


def write_text(path: str, content: str) -> None:
    """Write text to file, creating parent directories if needed."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def safe_backup_file(path: str) -> None:
    """Create path.bak once. If already exists, do not overwrite."""
    bak = path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
