"""Tests for bounded, read-only information structure analyzers."""

import sqlite3

import pytest

from src.information_structure import (
    StructureLimitError,
    document_visual_structures,
    folder_map_from_paths,
    organize_text_hierarchy,
    python_context_graph,
    scientific_reference_graph,
    sqlite_schema_graph,
)


def test_folder_map_reuses_supplied_paths_and_skips_outside_root(tmp_path):
    root = tmp_path / "project"
    paths = [root / "src" / "app.py", root / "README.md", tmp_path / "outside.txt"]

    result = folder_map_from_paths(root, paths)

    assert result["accepted_paths"] == 2
    assert result["skipped_outside_root"] == 1
    assert [child["name"] for child in result["tree"]["children"]] == ["README.md", "src"]


def test_sqlite_graph_reads_tables_columns_and_foreign_keys(tmp_path):
    database = tmp_path / "library.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE author (id INTEGER PRIMARY KEY, name TEXT)")
        connection.execute(
            "CREATE TABLE book (id INTEGER PRIMARY KEY, author_id INTEGER REFERENCES author(id), title TEXT)"
        )

    result = sqlite_schema_graph(database)

    assert {node["id"] for node in result["nodes"]} >= {"table:author", "table:book", "table:book.title"}
    assert {edge["kind"] for edge in result["edges"]} == {"contains", "foreign_key"}


def test_python_graph_distinguishes_functions_methods_imports_and_calls():
    source = """import json

def free():
    return json.dumps({})

class Service:
    def run(self):
        return free()
"""
    result = python_context_graph(source, "sample")
    kinds = {(node["label"], node["kind"]) for node in result["nodes"]}

    assert ("free", "function") in kinds
    assert ("run", "method") in kinds
    assert ("json", "import") in kinds
    assert any(edge["kind"] == "calls" and edge["target"] == "call:free" for edge in result["edges"])


def test_loose_text_is_grouped_without_changing_paragraphs():
    text = "Alpha topic first.\n\nBeta separate.\n\nAlpha topic second."
    result = organize_text_hierarchy(text)

    recovered = [paragraph["text"] for group in result["groups"] for paragraph in group["paragraphs"]]
    assert sorted(recovered) == sorted(text.split("\n\n"))
    assert result["metrics"]["paragraphs"] == 3


def test_loose_text_can_suggest_recursive_keyword_subgroups():
    text = (
        "System alpha database storage.\n\nSystem alpha database query.\n\n"
        "System beta interface button.\n\nSystem beta interface menu."
    )
    result = organize_text_hierarchy(text)
    assert any(group["subgroups"] for group in result["groups"])


def test_reference_graph_finds_common_ancestors_and_reading_order():
    result = scientific_reference_graph({
        "advanced": "Refs 10.1234/common.1 and 10.1234/extra.2",
        "intro": "Refs 10.1234/common.1",
    })

    assert result["shared_ancestors"] == ["10.1234/common.1"]
    assert result["reading_order_suggestion"] == ["intro", "advanced"]
    assert result["suggested_combinations"] == [
        {"articles": ["advanced", "intro"], "shared_ancestors": ["10.1234/common.1"]}
    ]


def test_document_visual_structures_expose_all_requested_views():
    result = document_visual_structures({"chapter": {"section": ["paragraph"]}})

    assert result["hierarchy"]["chapter"]["section"] == ["paragraph"]
    assert result["inclusion_edges"]
    assert result["bar_counts_by_level"]
    assert any(node["number"] == "1.1.1" for node in result["numbered_nodes"])


def test_source_limit_is_explicit():
    with pytest.raises(StructureLimitError):
        python_context_graph("x" * 2_000_001)
