"""Bounded, read-only PDF text extraction for translation workflows."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_MAX_PDF_BYTES = 50 * 1024 * 1024
DEFAULT_MAX_PDF_PAGES = 500
DEFAULT_MAX_TEXT_BYTES = 100 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 60


class PdfExtractionError(ValueError):
    """Raised when a PDF cannot be safely converted to reviewable text."""


@dataclass(frozen=True)
class PdfTextExtraction:
    """Text extraction result with audit metadata."""

    text: str
    page_count: int
    backend: str = "poppler"


def _find_working_tool(name: str) -> str:
    """Find a runnable Poppler binary, bypassing broken PATH overrides."""
    candidates = [shutil.which(name), f"/usr/bin/{name}", f"/usr/local/bin/{name}"]
    checked = set()
    for candidate in candidates:
        if not candidate or candidate in checked or not os.path.isfile(candidate):
            continue
        checked.add(candidate)
        try:
            probe = subprocess.run(
                [candidate, "-v"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=3,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            return candidate
    raise PdfExtractionError(
        f"Required Poppler tool is unavailable: {name}. Install poppler-utils."
    )


def extract_pdf_text(
    file_path: str | os.PathLike[str],
    *,
    max_bytes: int = DEFAULT_MAX_PDF_BYTES,
    max_pages: int = DEFAULT_MAX_PDF_PAGES,
    max_text_bytes: int = DEFAULT_MAX_TEXT_BYTES,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> PdfTextExtraction:
    """Extract text from a PDF without modifying it or loading output unboundedly."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise PdfExtractionError("Input file must use the .pdf extension")

    size = path.stat().st_size
    if size > max_bytes:
        raise PdfExtractionError(
            f"PDF is too large ({size} bytes); limit is {max_bytes} bytes"
        )

    pdfinfo = _find_working_tool("pdfinfo")
    pdftotext = _find_working_tool("pdftotext")
    try:
        info = subprocess.run(
            [pdfinfo, str(path)],
            capture_output=True,
            text=True,
            check=False,
            timeout=min(timeout_seconds, 15),
        )
    except subprocess.TimeoutExpired as exc:
        raise PdfExtractionError("Timed out while inspecting PDF metadata") from exc
    if info.returncode != 0:
        detail = (info.stderr or "invalid or encrypted PDF").strip()
        raise PdfExtractionError(f"Could not inspect PDF: {detail}")

    pages_match = re.search(r"^Pages:\s+(\d+)\s*$", info.stdout, re.MULTILINE)
    if not pages_match:
        raise PdfExtractionError("Could not determine PDF page count")
    page_count = int(pages_match.group(1))
    if page_count > max_pages:
        raise PdfExtractionError(
            f"PDF has {page_count} pages; limit is {max_pages} pages"
        )

    fd, output_name = tempfile.mkstemp(prefix="clarify-pdf-", suffix=".txt")
    os.close(fd)
    try:
        try:
            conversion = subprocess.run(
                [pdftotext, "-enc", "UTF-8", str(path), output_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise PdfExtractionError("Timed out while extracting PDF text") from exc
        if conversion.returncode != 0:
            detail = (conversion.stderr or "unknown Poppler error").strip()
            raise PdfExtractionError(f"Could not extract PDF text: {detail}")

        output_path = Path(output_name)
        output_size = output_path.stat().st_size
        if output_size > max_text_bytes:
            raise PdfExtractionError(
                f"Extracted text is too large ({output_size} bytes); "
                f"limit is {max_text_bytes} bytes"
            )
        text = output_path.read_text(encoding="utf-8")
        if not text.strip():
            raise PdfExtractionError(
                "PDF contains no extractable text; scanned PDFs require OCR"
            )
        return PdfTextExtraction(text=text, page_count=page_count)
    finally:
        try:
            os.unlink(output_name)
        except FileNotFoundError:
            pass
