"""Tests for deterministic, confirmation-oriented voice command parsing."""

import pytest

from src.voice_programming import normalize_programming_dictation, parse_voice_command, speech_backend_status


def test_programming_punctuation_is_normalized_in_two_languages():
    assert normalize_programming_dictation("print abre parenteses 'ok' fecha parenteses") == "print('ok')"
    assert normalize_programming_dictation("items open bracket 0 close bracket") == "items[0]"


def test_commands_are_preview_data_and_always_require_confirmation():
    assert parse_voice_command("go to line 42") == {
        "action": "go_to_line", "line": 42, "requires_confirmation": True
    }
    assert parse_voice_command("save file") == {"action": "save", "requires_confirmation": True}
    inserted = parse_voice_command("write value colon space 1")
    assert inserted == {"action": "insert_text", "text": "value: 1", "requires_confirmation": True}


def test_transcript_limit_and_backend_status_are_explicit():
    with pytest.raises(ValueError, match="exceeds"):
        parse_voice_command("x" * 20_001)
    status = speech_backend_status()
    assert set(status["backends"]) == {
        "whisper_executable", "speech_recognition_python", "vosk_python"
    }
    assert "No audio" in status["notice"]
