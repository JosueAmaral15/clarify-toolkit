"""Regressions for confirmed high-severity code-scanning findings."""

import importlib.util
import stat
import zipfile
from pathlib import Path

import pytest

from src.translation import html_format_mapper


def _load_postgresql_plugin_module():
    path = Path(__file__).parents[2] / "plugins" / "export_to_postgresql" / "main.py"
    spec = importlib.util.spec_from_file_location("export_to_postgresql_security", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _FakeSQL:
    def __init__(self, text):
        self.text = text

    def format(self, **values):
        rendered = self.text
        for key, value in values.items():
            rendered = rendered.replace("{" + key + "}", value.text)
        return _FakeSQL(rendered)


class _FakeSQLModule:
    @staticmethod
    def SQL(text):
        return _FakeSQL(text)

    @staticmethod
    def Identifier(value):
        return _FakeSQL('"' + value.replace('"', '""') + '"')


def test_postgresql_table_name_is_composed_as_quoted_identifier():
    plugin = _load_postgresql_plugin_module()
    malicious = 'records; DROP TABLE users; --'

    create, insert = plugin._postgresql_statements(_FakeSQLModule, malicious)

    quoted = '"records; DROP TABLE users; --"'
    assert quoted in create.text
    assert quoted in insert.text
    assert "VALUES (%s)" in insert.text


@pytest.mark.parametrize("name", ["", "bad\x00name", "x" * 64])
def test_postgresql_table_name_rejects_invalid_identifiers(name):
    plugin = _load_postgresql_plugin_module()

    with pytest.raises(ValueError):
        plugin._postgresql_statements(_FakeSQLModule, name)


def _write_zip(path, entries):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in entries:
            archive.writestr(name, content)


def test_odt_extraction_keeps_regular_members_inside_root(tmp_path):
    source = tmp_path / "safe.odt"
    destination = tmp_path / "output"
    destination.mkdir()
    _write_zip(
        source,
        [("content.xml", b"<document/>"), ("META-INF/manifest.xml", b"ok")],
    )

    with zipfile.ZipFile(source) as archive:
        html_format_mapper._extract_odt_archive_safely(archive, str(destination))

    assert (destination / "content.xml").read_bytes() == b"<document/>"
    assert (destination / "META-INF" / "manifest.xml").read_bytes() == b"ok"


@pytest.mark.parametrize(
    "name", ["../escaped", "/tmp/escaped", "C:/escaped", "dir\\escaped"]
)
def test_odt_extraction_rejects_traversal_and_absolute_paths(tmp_path, name):
    source = tmp_path / "unsafe.odt"
    destination = tmp_path / "output"
    destination.mkdir()
    _write_zip(source, [(name, b"unsafe")])

    with zipfile.ZipFile(source) as archive, pytest.raises(ValueError):
        html_format_mapper._extract_odt_archive_safely(archive, str(destination))


def test_odt_extraction_rejects_symbolic_links(tmp_path):
    source = tmp_path / "link.odt"
    destination = tmp_path / "output"
    destination.mkdir()
    link = zipfile.ZipInfo("linked")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr(link, "target")

    with zipfile.ZipFile(source) as archive, pytest.raises(ValueError):
        html_format_mapper._extract_odt_archive_safely(archive, str(destination))


def test_odt_extraction_rejects_excessive_compression_ratio(tmp_path):
    source = tmp_path / "bomb.odt"
    destination = tmp_path / "output"
    destination.mkdir()
    _write_zip(source, [("content.xml", b"0" * (1024 * 1024))])

    with zipfile.ZipFile(source) as archive, pytest.raises(
        ValueError, match="compression ratio"
    ):
        html_format_mapper._extract_odt_archive_safely(archive, str(destination))
