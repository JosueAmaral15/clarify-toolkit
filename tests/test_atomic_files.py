"""Tests for shared conflict-aware atomic text writes."""

import os
import stat

import pytest

from src.utils.atomic_files import write_text_atomically


def test_atomic_text_write_creates_and_replaces_regular_file(tmp_path):
    target = tmp_path / "notes.txt"

    write_text_atomically(target, "first")
    target.chmod(0o640)
    write_text_atomically(target, "second")

    assert target.read_text(encoding="utf-8") == "second"
    assert stat.S_IMODE(target.stat().st_mode) == 0o640
    assert list(tmp_path.glob(".clarify-save-*.tmp")) == []


def test_atomic_text_write_rejects_symlink_without_changing_origin(tmp_path):
    origin = tmp_path / "origin.txt"
    origin.write_text("original", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(origin)

    with pytest.raises(ValueError, match="without links"):
        write_text_atomically(link, "replacement")

    assert origin.read_text(encoding="utf-8") == "original"
    assert link.is_symlink()


def test_atomic_text_write_rejects_missing_parent(tmp_path):
    target = tmp_path / "missing" / "notes.txt"

    with pytest.raises(FileNotFoundError, match="Parent directory"):
        write_text_atomically(target, "content")

    assert not os.path.lexists(target)
