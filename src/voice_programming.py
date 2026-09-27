"""Deterministic transcript-to-editor command parsing."""

from __future__ import annotations

import importlib.util
import re
import shutil
from typing import Any


MAX_TRANSCRIPT_CHARS = 20_000
_TOKENS = {
    " nova linha ": "\n",
    " new line ": "\n",
    " tabulação ": "\t",
    " tabulacao ": "\t",
    " tab key ": "\t",
    " espaço ": " ",
    " space ": " ",
    " abre parênteses ": "(",
    " abre parenteses ": "(",
    " open parenthesis ": "(",
    " fecha parênteses ": ")",
    " fecha parenteses ": ")",
    " close parenthesis ": ")",
    " abre colchetes ": "[",
    " open bracket ": "[",
    " fecha colchetes ": "]",
    " close bracket ": "]",
    " abre chaves ": "{",
    " open brace ": "{",
    " fecha chaves ": "}",
    " close brace ": "}",
    " dois pontos ": ":",
    " colon ": ":",
    " ponto e vírgula ": ";",
    " ponto e virgula ": ";",
    " semicolon ": ";",
    " vírgula ": ",",
    " virgula ": ",",
    " comma ": ",",
}


def speech_backend_status() -> dict[str, Any]:
    """Report optional recognition backends without loading models or devices."""
    backends = {
        "whisper_executable": bool(shutil.which("whisper") or shutil.which("whisper-cli")),
        "speech_recognition_python": importlib.util.find_spec("speech_recognition") is not None,
        "vosk_python": importlib.util.find_spec("vosk") is not None,
    }
    return {
        "available": any(backends.values()),
        "backends": backends,
        "notice": "No audio is recorded or transmitted until a recognition backend is explicitly configured.",
    }


def normalize_programming_dictation(transcript: str) -> str:
    """Convert spoken punctuation tokens while preserving arbitrary code text."""
    if len(transcript) > MAX_TRANSCRIPT_CHARS:
        raise ValueError(f"Transcript exceeds {MAX_TRANSCRIPT_CHARS:,} characters")
    result = transcript.strip()
    sentinels = {" ": "\x00SPACE\x00", "\n": "\x00NEWLINE\x00", "\t": "\x00TAB\x00"}
    for symbol in (" ", "\n", "\t"):
        for spoken, replacement in _TOKENS.items():
            if replacement == symbol:
                phrase = spoken.strip()
                result = re.sub(
                    rf"\s*(?<!\w){re.escape(phrase)}(?!\w)\s*",
                    sentinels[symbol],
                    result,
                    flags=re.IGNORECASE,
                )
    for spoken, symbol in _TOKENS.items():
        if symbol in sentinels:
            continue
        phrase = spoken.strip()
        result = re.sub(
            rf"\s*(?<!\w){re.escape(phrase)}(?!\w)\s*",
            symbol,
            result,
            flags=re.IGNORECASE,
        )
    return (
        result.replace(sentinels[" "], " ")
        .replace(sentinels["\n"], "\n")
        .replace(sentinels["\t"], "\t")
        .strip(" ")
    )


def parse_voice_command(transcript: str) -> dict[str, Any]:
    """Parse one transcript into a previewable command; never execute it."""
    stripped = transcript.strip()
    if not stripped:
        raise ValueError("Provide a transcript")
    goto = re.fullmatch(r"(?:ir para (?:a )?linha|go to line)\s+(\d+)", stripped, re.IGNORECASE)
    if goto:
        return {"action": "go_to_line", "line": int(goto.group(1)), "requires_confirmation": True}
    if re.fullmatch(r"(?:salvar(?: arquivo)?|save(?: file)?)", stripped, re.IGNORECASE):
        return {"action": "save", "requires_confirmation": True}
    write = re.match(r"^(?:escreva|write|digite|type)\s+(.+)$", stripped, re.IGNORECASE | re.DOTALL)
    content = normalize_programming_dictation(write.group(1) if write else stripped)
    return {"action": "insert_text", "text": content, "requires_confirmation": True}
