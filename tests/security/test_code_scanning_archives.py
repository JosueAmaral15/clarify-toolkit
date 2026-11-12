"""Regressions for compressed ODT and DOCX resource-amplification findings."""

import zipfile
from unittest.mock import patch

import pytest
from docx import Document
from odf.opendocument import OpenDocumentText
from odf.text import P

from src.translation.archive_security import (
    DOCUMENT_ARCHIVE_LIMITS,
    ZipArchiveLimits,
    validate_zip_archive,
)
from src.translation.docx_html_mapper import DocxHtmlMapper
from src.translation.html_format_mapper import HTMLFormatMapper


def _write_zip(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries:
            archive.writestr(name, content)


def test_shared_archive_validation_accepts_bounded_document_parts(tmp_path):
    source = tmp_path / "valid-package.zip"
    _write_zip(
        source,
        [("content.xml", b"<document/>"), ("Pictures/image.png", b"image")],
    )

    with zipfile.ZipFile(source) as archive:
        members = validate_zip_archive(archive, label="test")

    assert [member.filename for member in members] == [
        "content.xml",
        "Pictures/image.png",
    ]


def test_shared_archive_validation_bounds_entry_and_byte_totals(tmp_path):
    source = tmp_path / "bounded-package.zip"
    _write_zip(source, [("one", b"1234"), ("two", b"5678")])
    limits = ZipArchiveLimits(
        max_entries=2,
        max_member_bytes=4,
        max_total_expanded_bytes=7,
        max_total_compressed_bytes=1024,
        max_compression_ratio=200,
    )

    with zipfile.ZipFile(source) as archive, pytest.raises(
        ValueError, match="expanded size"
    ):
        validate_zip_archive(archive, label="test", limits=limits)


def test_shared_archive_validation_bounds_entry_count(tmp_path):
    source = tmp_path / "too-many-entries.zip"
    _write_zip(source, [("one", b"1"), ("two", b"2")])
    limits = ZipArchiveLimits(
        max_entries=1,
        max_member_bytes=1024,
        max_total_expanded_bytes=1024,
        max_total_compressed_bytes=1024,
        max_compression_ratio=200,
    )

    with zipfile.ZipFile(source) as archive, pytest.raises(
        ValueError, match="too many entries"
    ):
        validate_zip_archive(archive, label="test", limits=limits)


def test_shared_archive_validation_bounds_member_size(tmp_path):
    source = tmp_path / "oversized-member.zip"
    _write_zip(source, [("large", b"1234")])
    limits = ZipArchiveLimits(
        max_entries=1,
        max_member_bytes=3,
        max_total_expanded_bytes=1024,
        max_total_compressed_bytes=1024,
        max_compression_ratio=200,
    )

    with zipfile.ZipFile(source) as archive, pytest.raises(
        ValueError, match="member is too large"
    ):
        validate_zip_archive(archive, label="test", limits=limits)


def test_shared_archive_validation_bounds_compressed_bytes(tmp_path):
    source = tmp_path / "compressed-package.zip"
    _write_zip(source, [("one", b"not-compressible-enough")])
    limits = ZipArchiveLimits(
        max_entries=1,
        max_member_bytes=1024,
        max_total_expanded_bytes=1024,
        max_total_compressed_bytes=1,
        max_compression_ratio=200,
    )

    with zipfile.ZipFile(source) as archive, pytest.raises(
        ValueError, match="compressed size"
    ):
        validate_zip_archive(archive, label="test", limits=limits)


def test_odt_rejects_compression_bomb_before_parser_load(tmp_path):
    source = tmp_path / "bomb.odt"
    _write_zip(source, [("Pictures/bomb.png", b"0" * (1024 * 1024))])

    with (
        patch("src.translation.html_format_mapper.opendocument.load") as load,
        pytest.raises(ValueError, match="compression ratio"),
    ):
        HTMLFormatMapper.extract_html_from_odt(str(source))

    load.assert_not_called()


def test_docx_rejects_compression_bomb_before_parser_load(tmp_path):
    source = tmp_path / "bomb.docx"
    _write_zip(source, [("word/document.xml", b"0" * (1024 * 1024))])

    with (
        patch("src.translation.docx_html_mapper.Document") as load,
        pytest.raises(ValueError, match="compression ratio"),
    ):
        DocxHtmlMapper(str(source))

    load.assert_not_called()


def test_valid_odt_uses_the_validated_stream_for_translation(tmp_path):
    source = tmp_path / "valid.odt"
    document = OpenDocumentText()
    document.text.addElement(P(text="bounded ODT"))
    document.save(str(source))

    html, _css, _images, _tables = HTMLFormatMapper.extract_html_from_odt(
        str(source)
    )

    assert "bounded ODT" in html


def test_valid_docx_uses_the_validated_stream_for_translation(tmp_path):
    source = tmp_path / "valid.docx"
    document = Document()
    document.add_paragraph("bounded DOCX")
    document.save(source)

    mapper = DocxHtmlMapper(str(source))
    html = mapper.extract_html_from_docx()

    assert "bounded DOCX" in html


def test_default_limits_match_existing_odt_extraction_contract():
    assert DOCUMENT_ARCHIVE_LIMITS.max_entries == 4096
    assert DOCUMENT_ARCHIVE_LIMITS.max_member_bytes == 64 * 1024 * 1024
    assert DOCUMENT_ARCHIVE_LIMITS.max_total_expanded_bytes == 512 * 1024 * 1024
    assert DOCUMENT_ARCHIVE_LIMITS.max_total_compressed_bytes == 512 * 1024 * 1024
    assert DOCUMENT_ARCHIVE_LIMITS.max_compression_ratio == 200
