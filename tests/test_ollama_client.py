"""Tests for bounded local Ollama integration."""

import io
import json

import pytest

from src.ai_processor.api_client import OllamaClient, list_ollama_models
from src.ai_processor.processor import process_file


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_list_ollama_models_uses_local_tags_endpoint(monkeypatch):
    payload = json.dumps({"models": [{"name": "llava:latest"}]}).encode()
    seen = []
    monkeypatch.setattr(
        "src.ai_processor.api_client.urlopen",
        lambda request, timeout: seen.append((request, timeout)) or _Response(payload),
    )

    assert list_ollama_models() == [{"name": "llava:latest", "label": "llava:latest"}]
    assert seen[0][1] == 5


def test_ollama_chat_has_finite_context_and_output_limits(monkeypatch):
    client = OllamaClient(model="tinyllama:latest")
    captured = {}

    def fake_request(path, payload=None, timeout=120):
        captured.update(path=path, payload=payload, timeout=timeout)
        return {"message": {"content": "local response"}}

    monkeypatch.setattr(client, "_request", fake_request)

    assert client.chat("system", "user") == "local response"
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["options"]["num_ctx"] == 4096
    assert captured["payload"]["options"]["num_predict"] == 1024


def test_ollama_image_payload_is_bounded(tmp_path):
    image = tmp_path / "large.png"
    image.write_bytes(b"x" * 11)
    client = OllamaClient(model="llava:latest")

    with pytest.raises(ValueError, match="safety limit"):
        client.chat_with_image("system", "user", str(image), max_bytes=10)


def test_process_file_routes_images_without_decoding_them(tmp_path):
    image = tmp_path / "sample.png"
    image.write_bytes(b"not-real-image")

    class Client:
        def chat_with_image(self, system, prompt, image_path, max_bytes=None):
            return (system, prompt, image_path, max_bytes)

    result = process_file(str(image), "describe", Client(), max_bytes=1024)

    assert result[2] == str(image)
    assert result[3] == 1024
