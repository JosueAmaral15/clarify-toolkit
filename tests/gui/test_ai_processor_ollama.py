"""GUI contract tests for the local Ollama provider."""

from src.ai_processor import OllamaClient
from src.gui.ai_processor_dock import AIProcessorDock


def test_ollama_provider_needs_no_api_key(qapp, mock_message_box):
    dock = AIProcessorDock()
    try:
        dock.combo_provider.setCurrentText("Ollama (Local)")

        assert not dock.ed_api_key.isEnabled()
        assert dock.btn_verify.text() == "Verify Service"
        assert isinstance(dock._get_client(), OllamaClient)
    finally:
        dock.deleteLater()
