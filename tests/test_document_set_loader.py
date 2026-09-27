"""Tests for multi-format Set Operations representations."""

import json
from unittest.mock import patch

import docx
from odf import text
from odf.opendocument import OpenDocumentText

from src.core.set_operation_executor import SetOperationExecutor
from src.document_set_loader import load_document_set, text_to_content_set
from src.translation.pdf_translation import PdfTextExtraction


def test_text_representation_is_normalized_order_independent_and_deduplicated():
    first = text_to_content_set("  Shared   sentence  \nUnique\nShared sentence")
    second = text_to_content_set("Unique\nShared sentence")

    assert first == second
    assert set(first["content"].values()) == {"Shared sentence", "Unique"}


def test_json_keeps_native_structure(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"key": {"value": 1}}), encoding="utf-8")

    assert load_document_set(str(path)) == {"key": {"value": 1}}


def test_docx_and_odt_share_the_same_comparable_representation(tmp_path):
    docx_path = tmp_path / "first.docx"
    document = docx.Document()
    document.add_paragraph("Shared sentence")
    document.add_paragraph("Second paragraph")
    document.save(docx_path)

    odt_path = tmp_path / "second.odt"
    odt = OpenDocumentText()
    odt.text.addElement(text.P(text="Second paragraph"))
    odt.text.addElement(text.P(text="Shared sentence"))
    odt.save(str(odt_path))

    assert load_document_set(str(docx_path)) == load_document_set(str(odt_path))


def test_notebook_includes_markdown_and_code_cell_text(tmp_path):
    path = tmp_path / "sample.ipynb"
    path.write_text(
        json.dumps(
            {
                "nbformat": 4,
                "nbformat_minor": 5,
                "cells": [
                    {"cell_type": "markdown", "source": ["Heading\n"]},
                    {"cell_type": "code", "source": "print('hello')"},
                ],
            }
        ),
        encoding="utf-8",
    )

    values = set(load_document_set(str(path))["content"].values())
    assert values == {"Heading", "print('hello')"}


def test_pdf_uses_existing_bounded_extractor(tmp_path):
    path = tmp_path / "sample.pdf"
    path.write_bytes(b"%PDF-test")
    with patch(
        "src.document_set_loader.extract_pdf_text",
        return_value=PdfTextExtraction("Shared\nPDF only", 1),
    ):
        result = load_document_set(str(path))

    assert set(result["content"].values()) == {"Shared", "PDF only"}


def test_executor_intersects_different_document_formats(tmp_path):
    left = tmp_path / "left.txt"
    right = tmp_path / "right.txt"
    left.write_text("shared\nleft", encoding="utf-8")
    right.write_text("right\nshared", encoding="utf-8")

    success, documents, error = SetOperationExecutor.validate_and_load_files(
        [str(left), str(right)]
    )
    assert success, error

    result = SetOperationExecutor.execute_operations(
        documents,
        ["∩"],
        "key_value",
        {
            "ignore_case_keys": False,
            "ignore_case_values": False,
            "skip_empty": False,
            "arrays_ignore_order": False,
        },
    )

    assert result.success
    assert len(result.results["intersection"]["intersection"]) == 1
