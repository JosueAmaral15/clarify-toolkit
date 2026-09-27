"""Tests for non-destructive editorial diagnostics."""

from subprocess import CompletedProcess

import pytest

from src.editorial_analysis import (
    abnt_structure_diagnostics,
    aspell_diagnostics,
    detect_language,
    diagnose_textual_defects,
    editorial_ai_prompt,
)


def test_language_detection_is_transparent_and_heuristic():
    result = detect_language("Este é um texto para uma revisão com mais contexto que o exemplo.")
    assert result["language"] == "pt_BR"
    assert result["confidence"] == "heuristic"
    assert set(result["scores"]) == {"pt_BR", "en_US", "es"}


def test_aspell_returns_candidates_without_rewriting(monkeypatch):
    calls = []

    def fake_run(arguments, **kwargs):
        calls.append((arguments, kwargs))
        if arguments[-2:] == ["dump", "dicts"]:
            return CompletedProcess(arguments, 0, stdout="en_US\n", stderr="")
        return CompletedProcess(arguments, 0, stdout="mispelled\nmispelled\n", stderr="")

    monkeypatch.setattr("src.editorial_analysis.subprocess.run", fake_run)
    result = aspell_diagnostics("A mispelled word", "en_US", executable="aspell")

    assert result["possible_misspellings"] == [{"word": "mispelled", "occurrences": 2}]
    assert calls[-1][1]["input"] == "A mispelled word"


def test_aspell_missing_dictionary_is_explicit(monkeypatch):
    monkeypatch.setattr(
        "src.editorial_analysis.available_aspell_dictionaries", lambda _executable: ["en_US"]
    )
    with pytest.raises(RuntimeError, match="No Aspell dictionary"):
        aspell_diagnostics("texto", "pt_BR", executable="aspell")


def test_defect_categories_remain_separate_and_reviewable():
    result = diagnose_textual_defects("TODO: completar isso.\nPopulation is 10.\nPopulation is 20.\nSegundo o estudo, algo ocorreu.")

    assert result["findings"]["omission"]
    assert result["findings"]["ambiguity"]
    assert result["findings"]["inconsistency"]
    assert result["findings"]["possibly_incorrect_fact"]
    assert "review candidates" in result["notice"]


def test_abnt_preflight_detects_heading_jump_and_generates_toc_without_changes():
    result = abnt_structure_diagnostics("# Book\n\n### Section\n\nText")

    assert any(issue["kind"] == "heading_level_jump" for issue in result["issues"])
    assert any(issue["section"] == "references" for issue in result["issues"] if "section" in issue)
    assert result["generated_toc_preview"] == ["- Book", "    - Section"]
    assert result["source_changed"] is False


def test_ai_prompt_separates_review_types_and_source_safety():
    prompt = editorial_ai_prompt("publication", "pt_BR", bridge_translation=True)
    assert "spelling correction, grammar correction, and publication rewrite as separate" in prompt
    assert "never claim to have modified" in prompt
    assert "bridge language" in prompt
