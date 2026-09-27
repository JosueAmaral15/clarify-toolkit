"""Tests for bounded Poppler-based PDF text extraction."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.translation.pdf_translation import PdfExtractionError, extract_pdf_text


def test_extract_pdf_text_uses_argument_lists_and_returns_metadata(tmp_path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"%PDF-test")
    commands = []

    def run(command, **_kwargs):
        commands.append(command)
        if command[0] == "pdfinfo":
            return subprocess.CompletedProcess(command, 0, "Pages:          2\n", "")
        Path(command[-1]).write_text("First page\fSecond page\n", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    with (
        patch("src.translation.pdf_translation._find_working_tool", side_effect=lambda name: name),
        patch("src.translation.pdf_translation.subprocess.run", side_effect=run),
    ):
        result = extract_pdf_text(source)

    assert result.text == "First page\fSecond page\n"
    assert result.page_count == 2
    assert result.backend == "poppler"
    assert commands[0] == ["pdfinfo", str(source)]
    assert commands[1][:4] == ["pdftotext", "-enc", "UTF-8", str(source)]


def test_extract_pdf_text_rejects_size_before_running_tools(tmp_path):
    source = tmp_path / "large.pdf"
    source.write_bytes(b"%PDF-too-large")

    with patch("src.translation.pdf_translation.subprocess.run") as run:
        with pytest.raises(PdfExtractionError, match="too large"):
            extract_pdf_text(source, max_bytes=4)
    run.assert_not_called()


def test_extract_pdf_text_rejects_page_limit_before_conversion(tmp_path):
    source = tmp_path / "many-pages.pdf"
    source.write_bytes(b"%PDF-test")

    with (
        patch("src.translation.pdf_translation._find_working_tool", side_effect=lambda name: name),
        patch(
            "src.translation.pdf_translation.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, "Pages: 501\n", ""),
        ) as run,
    ):
        with pytest.raises(PdfExtractionError, match="501 pages"):
            extract_pdf_text(source, max_pages=500)
    assert run.call_count == 1


def test_extract_pdf_text_rejects_scanned_pdf_without_text(tmp_path):
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-test")

    def run(command, **_kwargs):
        if command[0] == "pdfinfo":
            return subprocess.CompletedProcess(command, 0, "Pages: 1\n", "")
        Path(command[-1]).write_text("", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")

    with (
        patch("src.translation.pdf_translation._find_working_tool", side_effect=lambda name: name),
        patch("src.translation.pdf_translation.subprocess.run", side_effect=run),
    ):
        with pytest.raises(PdfExtractionError, match="require OCR"):
            extract_pdf_text(source)


def test_find_tool_failure_is_actionable(tmp_path):
    source = tmp_path / "source.pdf"
    source.write_bytes(b"%PDF-test")

    with patch(
        "src.translation.pdf_translation._find_working_tool",
        side_effect=PdfExtractionError("Install poppler-utils"),
    ):
        with pytest.raises(PdfExtractionError, match="poppler-utils"):
            extract_pdf_text(source)
