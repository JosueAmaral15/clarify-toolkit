"""Structure-preserving translation helpers for Jupyter notebooks."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable


DEFAULT_MAX_NOTEBOOK_BYTES = 50 * 1024 * 1024


class NotebookFormatError(ValueError):
    """Raised when an input file is not a supported notebook document."""


def load_notebook(
    file_path: str | os.PathLike[str],
    max_bytes: int = DEFAULT_MAX_NOTEBOOK_BYTES,
) -> dict[str, Any]:
    """Load and minimally validate a notebook under a bounded size limit."""
    path = Path(file_path)
    size = path.stat().st_size
    if size > max_bytes:
        raise NotebookFormatError(
            f"Notebook is too large ({size} bytes); limit is {max_bytes} bytes"
        )

    try:
        with path.open("r", encoding="utf-8") as handle:
            notebook = json.load(handle)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NotebookFormatError(f"Invalid notebook JSON: {exc}") from exc

    if not isinstance(notebook, dict):
        raise NotebookFormatError("Notebook root must be a JSON object")
    if not isinstance(notebook.get("cells"), list):
        raise NotebookFormatError("Notebook must contain a cells array")
    if not isinstance(notebook.get("nbformat"), int):
        raise NotebookFormatError("Notebook must contain an integer nbformat")
    return notebook


def translate_markdown_cells(
    notebook: dict[str, Any],
    translate_text: Callable[[str], str],
) -> int:
    """Translate Markdown cells in place and return the number changed.

    Code cells, raw cells, outputs, metadata, attachments, IDs, execution counts,
    and unknown notebook fields are never passed to the translation callback.
    """
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise NotebookFormatError("Notebook must contain a cells array")

    translated_cells = 0
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "markdown":
            continue

        source = cell.get("source", "")
        source_was_list = isinstance(source, list)
        if source_was_list:
            if not all(isinstance(part, str) for part in source):
                raise NotebookFormatError("Markdown cell source list must contain strings")
            source_text = "".join(source)
        elif isinstance(source, str):
            source_text = source
        else:
            raise NotebookFormatError("Markdown cell source must be a string or string list")

        if not source_text.strip():
            continue
        translated = translate_text(source_text)
        if not isinstance(translated, str):
            raise TypeError("Notebook translation callback must return text")

        cell["source"] = translated.splitlines(keepends=True) if source_was_list else translated
        translated_cells += 1

    return translated_cells


def markdown_cell_count(notebook: dict[str, Any]) -> int:
    """Count non-empty Markdown cells without copying notebook data."""
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise NotebookFormatError("Notebook must contain a cells array")
    count = 0
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", "")
        if isinstance(source, list):
            if not all(isinstance(part, str) for part in source):
                raise NotebookFormatError("Markdown cell source list must contain strings")
            source = "".join(source)
        if not isinstance(source, str):
            raise NotebookFormatError("Markdown cell source must be a string or string list")
        if source.strip():
            count += 1
    return count


def notebook_markdown_text(notebook: dict[str, Any]) -> str:
    """Build a bounded-purpose preview from Markdown cells only."""
    cells = notebook.get("cells")
    if not isinstance(cells, list):
        raise NotebookFormatError("Notebook must contain a cells array")
    sections: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict) or cell.get("cell_type") != "markdown":
            continue
        source = cell.get("source", "")
        if isinstance(source, list):
            if not all(isinstance(part, str) for part in source):
                raise NotebookFormatError("Markdown cell source list must contain strings")
            source = "".join(source)
        if not isinstance(source, str):
            raise NotebookFormatError("Markdown cell source must be a string or string list")
        if source.strip():
            sections.append(source)
    return "\n\n".join(sections)


def save_notebook(notebook: dict[str, Any], output_path: str | os.PathLike[str]) -> None:
    """Write a notebook atomically as UTF-8 JSON."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(notebook, handle, ensure_ascii=False, indent=1)
            handle.write("\n")
        os.replace(temporary_path, destination)
    except Exception:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass
        raise
