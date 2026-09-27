"""Local preflight and constrained prompts for AI-assisted algorithm review."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.information_structure import python_context_graph


MAX_CODE_BYTES = 2_000_000
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def algorithm_review_preflight(path_text: str) -> dict[str, Any]:
    path = Path(path_text).expanduser().resolve(strict=True)
    if path.is_dir():
        return {
            "source_kind": "project_directory",
            "path": str(path),
            "notice": "The existing AI Processor applies the prompt per bounded file; it is not a whole-project proof.",
        }
    if path.stat().st_size > MAX_CODE_BYTES:
        raise ValueError(f"Source exceeds {MAX_CODE_BYTES:,} bytes")
    if path.suffix.lower() in IMAGE_EXTENSIONS:
        return {
            "source_kind": "flowchart_image",
            "path": str(path),
            "notice": "Requires a configured multimodal provider such as an installed Ollama LLaVA model.",
        }
    if path.suffix.lower() == ".py":
        source = path.read_text(encoding="utf-8")
        graph = python_context_graph(source, path.stem)
        return {
            "source_kind": "python",
            "path": str(path),
            "context_graph": graph,
        }
    return {
        "source_kind": "code_or_text",
        "path": str(path),
        "notice": "No language-specific parser is active; AI review must identify the syntax first.",
    }


def algorithm_review_prompt(preflight: dict[str, Any]) -> str:
    kind = preflight["source_kind"]
    context = ""
    if kind == "python":
        graph = preflight["context_graph"]
        compact = {
            "nodes": graph["nodes"][:300],
            "edges": graph["edges"][:500],
            "function_metrics": graph["function_metrics"][:300],
        }
        context = f"\nLocal Python AST preflight (bounded):\n{json.dumps(compact, ensure_ascii=False)}"
    elif kind == "flowchart_image":
        context = "\nTreat the attached image as a flowchart. Transcribe nodes and directed edges before reviewing logic."
    elif kind == "project_directory":
        context = "\nReview each supplied project file in context, but state when cross-file evidence is missing."
    return (
        "Review this algorithm or software artifact for programming errors, logic errors, unreachable paths, "
        "incorrect state transitions, boundary cases, resource leaks, excessive complexity, and unsafe assumptions. "
        "Separate confirmed defects from hypotheses and style suggestions. Cite file locations or flowchart nodes. "
        "Do not modify files, do not claim execution, and propose focused tests for every material finding. "
        "Treat generated output as advisory until tests reproduce each issue."
        f"{context}"
    )
