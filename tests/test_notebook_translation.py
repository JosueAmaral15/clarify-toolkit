"""Tests for structure-preserving Jupyter notebook translation."""

from __future__ import annotations

import json

import pytest

from src.translation.notebook_translation import (
    NotebookFormatError,
    load_notebook,
    markdown_cell_count,
    notebook_markdown_text,
    save_notebook,
    translate_markdown_cells,
)


def _notebook() -> dict:
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "id": "intro",
                "metadata": {"tags": ["keep"]},
                "attachments": {"image.png": {"image/png": "AA=="}},
                "source": ["Hello\n", "World"],
            },
            {
                "cell_type": "code",
                "id": "code",
                "metadata": {"trusted": True},
                "execution_count": 7,
                "source": ["print('Hello')\n"],
                "outputs": [{"output_type": "stream", "text": ["Hello\n"]}],
            },
            {
                "cell_type": "raw",
                "metadata": {},
                "source": "Hello raw",
            },
        ],
        "metadata": {"kernelspec": {"name": "python3"}},
        "nbformat": 4,
        "nbformat_minor": 5,
        "custom": {"preserve": True},
    }


def test_translate_markdown_cells_preserves_notebook_structure():
    notebook = _notebook()
    code_cell_before = json.loads(json.dumps(notebook["cells"][1]))
    raw_cell_before = json.loads(json.dumps(notebook["cells"][2]))
    metadata_before = json.loads(json.dumps(notebook["metadata"]))

    count = translate_markdown_cells(notebook, lambda text: text.replace("Hello", "Olá"))

    assert count == 1
    assert notebook["cells"][0]["source"] == ["Olá\n", "World"]
    assert notebook["cells"][0]["id"] == "intro"
    assert notebook["cells"][0]["attachments"] == {"image.png": {"image/png": "AA=="}}
    assert notebook["cells"][1] == code_cell_before
    assert notebook["cells"][2] == raw_cell_before
    assert notebook["metadata"] == metadata_before
    assert notebook["custom"] == {"preserve": True}


def test_translate_markdown_string_and_skip_blank_cell():
    notebook = {
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": "Hello"},
            {"cell_type": "markdown", "metadata": {}, "source": ["  ", "\n"]},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    calls = []

    count = translate_markdown_cells(notebook, lambda text: calls.append(text) or "Olá")

    assert count == 1
    assert calls == ["Hello"]
    assert notebook["cells"][0]["source"] == "Olá"
    assert notebook["cells"][1]["source"] == ["  ", "\n"]


def test_markdown_preview_and_count_ignore_code_outputs():
    notebook = _notebook()

    assert markdown_cell_count(notebook) == 1
    assert notebook_markdown_text(notebook) == "Hello\nWorld"
    assert "print" not in notebook_markdown_text(notebook)


def test_load_and_atomic_save_notebook_round_trip(tmp_path):
    source = tmp_path / "source.ipynb"
    output = tmp_path / "translated.ipynb"
    source.write_text(json.dumps(_notebook()), encoding="utf-8")

    notebook = load_notebook(source)
    translate_markdown_cells(notebook, lambda text: text.upper())
    save_notebook(notebook, output)

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["cells"][0]["source"] == ["HELLO\n", "WORLD"]
    assert saved["cells"][1]["outputs"][0]["text"] == ["Hello\n"]
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize(
    "payload",
    [[], {}, {"cells": [], "nbformat": "4"}],
)
def test_load_notebook_rejects_invalid_structure(tmp_path, payload):
    source = tmp_path / "invalid.ipynb"
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(NotebookFormatError):
        load_notebook(source)


def test_load_notebook_checks_size_before_parsing(tmp_path):
    source = tmp_path / "large.ipynb"
    source.write_text(json.dumps(_notebook()), encoding="utf-8")

    with pytest.raises(NotebookFormatError, match="too large"):
        load_notebook(source, max_bytes=10)


def test_translate_rejects_invalid_markdown_source():
    notebook = {
        "cells": [{"cell_type": "markdown", "source": ["valid", 3]}],
        "nbformat": 4,
    }

    with pytest.raises(NotebookFormatError):
        translate_markdown_cells(notebook, str.upper)
