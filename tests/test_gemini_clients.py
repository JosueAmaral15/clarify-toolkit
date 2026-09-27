"""Gemini requests use isolated credentials and close transports on every path."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.ai_processor import api_client
from src import tutorial_assistant


@pytest.fixture
def sdk(monkeypatch):
    factory = MagicMock()
    client = factory.return_value.__enter__.return_value
    client.models.list.return_value = [
        SimpleNamespace(name="models/gemini-2.5-flash", supported_actions=["generateContent"]),
        SimpleNamespace(name="models/embedding", supported_actions=["embedContent"]),
        SimpleNamespace(name="models/unknown", supported_actions=None),
    ]
    client.models.generate_content.return_value = SimpleNamespace(text="Answer")
    monkeypatch.setattr(api_client.genai, "Client", factory)
    monkeypatch.setattr(api_client, "has_internet", lambda: True)
    return factory, client


def test_model_listing_filters_generation_and_closes(sdk):
    factory, _ = sdk
    assert api_client.list_gemini_models("listing-key") == [
        {"name": "gemini-2.5-flash", "label": "Gemini 2.5 Flash"}
    ]
    factory.assert_called_once_with(api_key="listing-key")
    factory.return_value.__exit__.assert_called_once()


def test_clients_keep_credentials_separate_and_use_system_instruction(sdk):
    factory, client = sdk
    first = api_client.GeminiClient("first-key")
    second = api_client.GeminiClient("second-key")
    assert first.chat("Translate", "Hello") == "Answer"
    assert second.verify_key()[0]
    assert [call.kwargs["api_key"] for call in factory.call_args_list] == ["first-key", "second-key"]
    client.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash", contents="Hello", config={"system_instruction": "Translate"}
    )
    assert factory.return_value.__exit__.call_count == 2


def test_failed_generation_closes_transport(sdk):
    factory, client = sdk
    client.models.generate_content.side_effect = RuntimeError("offline")
    assert "API ERROR" in api_client.GeminiClient("key").chat("", "Hello")
    factory.return_value.__exit__.assert_called_once()


def test_missing_key_does_not_create_client(sdk):
    factory, _ = sdk
    assert api_client.list_gemini_models("") == []
    wrapper = api_client.GeminiClient(None)
    assert not wrapper.verify_key()[0]
    assert "SIMULATED" in wrapper.chat("", "Hello")
    factory.assert_not_called()


def test_tutorial_assistant_closes_request_and_records_answer(sdk, tmp_path):
    factory, client = sdk
    assistant = tutorial_assistant.TutorialAssistant("tutorial-key", tmp_path)
    assert assistant.ask("How do I open a file?") == ("Answer", True)
    assert assistant.conversation_history[-1]["content"] == "Answer"
    assert client.models.generate_content.call_args.kwargs["model"] == "gemini-2.5-flash"
    factory.return_value.__exit__.assert_called_once()


def test_tutorial_failure_does_not_append_history(sdk, tmp_path):
    factory, client = sdk
    client.models.generate_content.side_effect = RuntimeError("offline")
    assistant = tutorial_assistant.TutorialAssistant("tutorial-key", tmp_path)
    assert assistant.ask("Help")[1] is False
    assert assistant.conversation_history == []
    factory.return_value.__exit__.assert_called_once()
