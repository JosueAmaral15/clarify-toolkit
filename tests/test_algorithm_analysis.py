"""Tests for local algorithm review preflight and prompts."""

import pytest

from src.algorithm_analysis import algorithm_review_preflight, algorithm_review_prompt


def test_python_preflight_reuses_ast_context_graph(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("def run(value):\n    return print(value)\n", encoding="utf-8")

    result = algorithm_review_preflight(str(source))
    prompt = algorithm_review_prompt(result)

    assert result["source_kind"] == "python"
    assert any(node["kind"] == "function" for node in result["context_graph"]["nodes"])
    assert "Local Python AST preflight" in prompt
    assert "Do not modify files" in prompt


def test_flowchart_and_project_preflights_state_provider_limits(tmp_path):
    image = tmp_path / "flow.png"
    image.write_bytes(b"not-decoded-during-preflight")

    image_result = algorithm_review_preflight(str(image))
    project_result = algorithm_review_preflight(str(tmp_path))

    assert image_result["source_kind"] == "flowchart_image"
    assert "multimodal provider" in image_result["notice"]
    assert project_result["source_kind"] == "project_directory"
    assert "not a whole-project proof" in project_result["notice"]


def test_preflight_rejects_oversized_files(tmp_path):
    source = tmp_path / "large.py"
    source.write_bytes(b"x" * 2_000_001)
    with pytest.raises(ValueError, match="exceeds"):
        algorithm_review_preflight(str(source))
