"""Bounded editorial diagnostics that never modify source documents."""

from __future__ import annotations

from collections import Counter
import re
import shutil
import subprocess
from typing import Any

from src.information_structure import MAX_SOURCE_CHARS, StructureLimitError, text_complexity_metrics


_LANGUAGE_MARKERS = {
    "pt_BR": {"de", "que", "não", "para", "uma", "com", "por", "como", "mais"},
    "en_US": {"the", "and", "that", "for", "with", "this", "from", "not", "are"},
    "es": {"de", "que", "el", "la", "para", "con", "una", "por", "los"},
}
_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][\wÀ-ÖØ-öø-ÿ'-]*", re.UNICODE)


def detect_language(text: str) -> dict[str, Any]:
    """Return a transparent marker-based language estimate, not a certainty."""
    words = Counter(word.lower() for word in _WORD_RE.findall(text))
    scores = {language: sum(words[marker] for marker in markers) for language, markers in _LANGUAGE_MARKERS.items()}
    language, score = max(scores.items(), key=lambda item: item[1])
    return {"language": language if score else "unknown", "confidence": "heuristic", "scores": scores}


def available_aspell_dictionaries(executable: str | None = None) -> list[str]:
    executable = executable or shutil.which("aspell")
    if not executable:
        return []
    try:
        result = subprocess.run(
            [executable, "dump", "dicts"], capture_output=True, text=True, timeout=5, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def aspell_diagnostics(text: str, language: str, executable: str | None = None) -> dict[str, Any]:
    """List possible misspellings through a bounded external Aspell process."""
    if len(text) > MAX_SOURCE_CHARS:
        raise StructureLimitError(f"Input exceeds {MAX_SOURCE_CHARS:,} characters")
    executable = executable or shutil.which("aspell")
    if not executable:
        raise RuntimeError("Aspell is not installed")
    dictionaries = available_aspell_dictionaries(executable)
    requested = language
    if requested not in dictionaries:
        variants = [item for item in dictionaries if item == requested.split("_")[0] or item.startswith(f"{requested.split('_')[0]}_")]
        if not variants:
            raise RuntimeError(f"No Aspell dictionary is installed for {language}")
        requested = variants[0]
    try:
        result = subprocess.run(
            [executable, "--encoding=utf-8", f"--lang={requested}", "list"],
            input=text,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Aspell exceeded the 10 second limit") from exc
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Aspell failed")
    misspellings = Counter(word.strip() for word in result.stdout.splitlines() if word.strip())
    return {
        "type": "spelling_diagnostics",
        "backend": "aspell",
        "language": requested,
        "possible_misspellings": [
            {"word": word, "occurrences": count} for word, count in sorted(misspellings.items())
        ],
        "notice": "Candidates require human review; no text was changed.",
    }


def diagnose_textual_defects(text: str) -> dict[str, Any]:
    """Find review candidates in separate, non-authoritative defect categories."""
    if len(text) > MAX_SOURCE_CHARS:
        raise StructureLimitError(f"Input exceeds {MAX_SOURCE_CHARS:,} characters")
    lines = text.splitlines()
    findings: dict[str, list[dict[str, Any]]] = {
        "omission": [],
        "strange_information": [],
        "inconsistency": [],
        "ambiguity": [],
        "possibly_incorrect_fact": [],
    }
    vague = re.compile(r"\b(isso|isto|aquilo|coisa|algo|they|it|this thing|something)\b", re.IGNORECASE)
    number_statements: dict[str, set[str]] = {}
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if re.search(r"\b(TODO|TBD|FIXME|XXX)\b|\?{2,}|\[\s*\]", line, re.IGNORECASE):
            findings["omission"].append({"line": line_number, "excerpt": stripped[:240]})
        if "\ufffd" in line or any(ord(char) < 32 and char not in "\t" for char in line):
            findings["strange_information"].append({"line": line_number, "excerpt": repr(line[:240])})
        if vague.search(line):
            findings["ambiguity"].append({"line": line_number, "excerpt": stripped[:240]})
        match = re.search(r"\b([A-Za-zÀ-ÖØ-öø-ÿ][\w -]{2,30})\s+(?:is|é|equals?|corresponde a)\s+(\d+(?:[.,]\d+)?)", line, re.IGNORECASE)
        if match:
            subject = match.group(1).strip().lower()
            number_statements.setdefault(subject, set()).add(match.group(2))
    for subject, values in sorted(number_statements.items()):
        if len(values) > 1:
            findings["inconsistency"].append({"subject": subject, "values": sorted(values)})
    if re.search(r"\b(according to|segundo|conforme|data|estudo|pesquisa)\b", text, re.IGNORECASE):
        findings["possibly_incorrect_fact"].append({
            "notice": "Claims that depend on external facts require source verification; no automatic truth claim was made."
        })
    return {
        "type": "textual_defect_diagnostics",
        "language_estimate": detect_language(text),
        "metrics": text_complexity_metrics(text),
        "findings": findings,
        "notice": "These are review candidates, not automatic corrections.",
    }


def abnt_structure_diagnostics(text: str) -> dict[str, Any]:
    """Check a Markdown-like book hierarchy and table of contents consistency."""
    if len(text) > MAX_SOURCE_CHARS:
        raise StructureLimitError(f"Input exceeds {MAX_SOURCE_CHARS:,} characters")
    headings = []
    issues = []
    previous_level = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        if previous_level and level > previous_level + 1:
            issues.append({"line": line_number, "kind": "heading_level_jump", "from": previous_level, "to": level})
        headings.append({"line": line_number, "level": level, "title": title})
        previous_level = level
    normalized = {item["title"].casefold() for item in headings}
    expected = {
        "summary_or_toc": {"sumário", "sumario", "contents", "table of contents"},
        "references": {"referências", "referencias", "references", "bibliography"},
    }
    for kind, alternatives in expected.items():
        if not normalized.intersection(alternatives):
            issues.append({"kind": "missing_expected_section", "section": kind})
    generated_toc = [f"{'  ' * (item['level'] - 1)}- {item['title']}" for item in headings]
    return {
        "type": "abnt_structure_diagnostics",
        "scope": "structural preflight only; pagination, typography, citations, and current standards need specialist validation",
        "headings": headings,
        "issues": issues,
        "generated_toc_preview": generated_toc,
        "source_changed": False,
    }


def editorial_ai_prompt(review_type: str, language: str, bridge_translation: bool = False) -> str:
    """Create a constrained prompt for the existing AI Processor."""
    bridge = (
        "You may use a bridge language to reason, but return all suggestions in the original language and flag translation losses."
        if bridge_translation else "Work directly in the document's original language."
    )
    return (
        f"Perform a {review_type} review. Estimated language: {language}. {bridge}\n"
        "Keep spelling correction, grammar correction, and publication rewrite as separate sections. "
        "Classify omissions, strange information, inconsistencies, ambiguities, and claims needing fact verification separately. "
        "Quote only short excerpts with locations, explain every suggestion, and never claim to have modified the source file. "
        "For ABNT concerns, distinguish structural preflight from requirements that need current standards or specialist review."
    )
