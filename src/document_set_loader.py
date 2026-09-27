"""Load supported documents into representations consumed by Set Operations."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from src.translation.document_parser import DocumentParser
from src.translation.notebook_translation import load_notebook
from src.translation.pdf_translation import extract_pdf_text


SUPPORTED_SET_EXTENSIONS = {".json", ".txt", ".docx", ".odt", ".ipynb", ".pdf"}
MAX_DOCUMENT_BYTES = 50 * 1024 * 1024
MAX_TEXT_UNITS = 50_000
MAX_UNIT_CHARS = 4096


class DocumentSetError(ValueError):
    """Raised when a document cannot be represented safely for comparison."""


def validate_document_set_path(file_path: str) -> bool:
    path = Path(file_path).expanduser().resolve()
    try:
        return (
            path.is_file()
            and path.suffix.lower() in SUPPORTED_SET_EXTENSIONS
            and path.stat().st_size <= MAX_DOCUMENT_BYTES
        )
    except OSError:
        return False


def _normalize_unit(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def text_to_content_set(text: str) -> dict[str, dict[str, str]]:
    """Convert text lines/paragraphs into a bounded, order-independent content set."""
    content = {}
    for raw_unit in text.splitlines():
        unit = _normalize_unit(raw_unit)
        if not unit:
            continue
        if len(unit) > MAX_UNIT_CHARS:
            unit = unit[:MAX_UNIT_CHARS]
        digest = hashlib.sha256(unit.encode("utf-8")).hexdigest()
        content[digest] = unit
        if len(content) >= MAX_TEXT_UNITS:
            break
    return {"content": content}


def _notebook_text(notebook: dict[str, Any]) -> str:
    units = []
    for cell in notebook.get("cells", []):
        if not isinstance(cell, dict):
            continue
        source = cell.get("source", "")
        if isinstance(source, list) and all(isinstance(part, str) for part in source):
            source = "".join(source)
        if isinstance(source, str):
            units.append(source)
    return "\n".join(units)


def load_document_set(file_path: str) -> Any:
    """Load a supported file using native JSON or canonical document content."""
    path = Path(file_path).expanduser().resolve()
    if not validate_document_set_path(str(path)):
        raise DocumentSetError(
            "File must exist, be at most 50 MiB, and use JSON, TXT, DOCX, ODT, "
            "IPYNB, or PDF format"
        )

    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            with path.open("r", encoding="utf-8") as stream:
                return json.load(stream)
        if suffix in {".txt", ".docx", ".odt"}:
            return text_to_content_set(DocumentParser.extract_text(str(path)))
        if suffix == ".ipynb":
            return text_to_content_set(_notebook_text(load_notebook(path)))
        if suffix == ".pdf":
            return text_to_content_set(extract_pdf_text(path).text)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise DocumentSetError(f"Could not load {path.name}: {exc}") from exc

    raise DocumentSetError(f"Unsupported document format: {suffix}")
