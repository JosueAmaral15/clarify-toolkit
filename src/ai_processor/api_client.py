"""
AI API Client Module

Provides unified interface for OpenAI and Google Gemini APIs.
"""
# pylint: disable=broad-exception-caught  # API robustness

from typing import Optional, Tuple
import base64
import json
import socket
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

try:
    from google import genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

try:
    import anthropic
    _CLAUDE_AVAILABLE = True
except ImportError:
    _CLAUDE_AVAILABLE = False


# Available models
AVAILABLE_MODELS = {
    'openai': [
        {'name': 'gpt-4o-mini', 'label': 'GPT-4o Mini (Recommended)'},
        {'name': 'gpt-4o', 'label': 'GPT-4o'},
    ],
    'gemini': [
        {'name': 'gemini-2.5-flash', 'label': 'Gemini 2.5 Flash (Recommended)'},
        {'name': 'gemini-2.5-pro', 'label': 'Gemini 2.5 Pro'},
    ],
    'claude': [
        {'name': 'claude-sonnet-4-20250514', 'label': 'Claude Sonnet 4 (Recommended)'},
        {'name': 'claude-3-5-sonnet-20241022', 'label': 'Claude 3.5 Sonnet'},
        {'name': 'claude-3-5-haiku-20241022', 'label': 'Claude 3.5 Haiku'},
    ],
    'perplexity': [
        {'name': 'llama-3.1-sonar-small-128k-online', 'label': 'Sonar Small (Online)'},
        {'name': 'llama-3.1-sonar-large-128k-online', 'label': 'Sonar Large (Online)'},
        {'name': 'llama-3.1-sonar-huge-128k-online', 'label': 'Sonar Huge (Online)'},
    ],
    'ollama': [
        {'name': 'llava:latest', 'label': 'LLaVA (install with: ollama pull llava)'},
    ],
}


OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
OLLAMA_MAX_IMAGE_BYTES = 10 * 1024 * 1024


def _read_bounded_json(response, limit=OLLAMA_MAX_RESPONSE_BYTES):
    payload = response.read(limit + 1)
    if len(payload) > limit:
        raise ValueError("Ollama response exceeded the 8 MiB safety limit")
    return json.loads(payload.decode("utf-8"))


def list_ollama_models(base_url: str = OLLAMA_BASE_URL) -> list:
    """List locally installed Ollama models without internet access."""
    try:
        with urlopen(f"{base_url}/api/tags", timeout=5) as response:
            data = _read_bounded_json(response)
        return [
            {"name": item["name"], "label": item["name"]}
            for item in data.get("models", [])
            if isinstance(item, dict) and item.get("name")
        ]
    except (OSError, URLError, ValueError, json.JSONDecodeError):
        return []


def has_internet() -> bool:
    """Check if internet connection is available."""
    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=3):
            pass
        return True
    except OSError:
        return False


def is_openai_available() -> bool:
    """Check if OpenAI SDK is installed."""
    return _OPENAI_AVAILABLE


def is_gemini_available() -> bool:
    """Check if Gemini SDK is installed."""
    return _GEMINI_AVAILABLE


def is_claude_available() -> bool:
    """Check if Claude SDK is installed."""
    return _CLAUDE_AVAILABLE


def list_openai_models(api_key: str) -> list:
    """List available OpenAI models."""
    if not _OPENAI_AVAILABLE or not api_key:
        return []

    try:
        client = OpenAI(api_key=api_key)
        models = client.models.list()

        # Filter for chat models only (gpt-*)
        chat_models = []
        for model in models.data:
            model_id = model.id
            if model_id.startswith('gpt-'):
                chat_models.append({
                    'name': model_id,
                    'label': model_id.upper()
                })

        return sorted(chat_models, key=lambda x: x['name'])
    except Exception:
        return []


def list_gemini_models(api_key: str) -> list:
    """List available Gemini models."""
    if not _GEMINI_AVAILABLE or not api_key:
        return []

    try:
        gen_models = []
        with genai.Client(api_key=api_key) as client:
            for model in client.models.list():
                if model.name and 'generateContent' in (model.supported_actions or []):
                    name = model.name.split('/')[-1]
                    gen_models.append({
                        'name': name,
                        'label': name.replace('-', ' ').title()
                    })

        return sorted(gen_models, key=lambda x: x['name'])
    except Exception:
        return []


def list_claude_models(api_key: str) -> list:
    """List available Claude models (static list as API doesn't provide model listing)."""
    if not _CLAUDE_AVAILABLE or not api_key:
        return []

    # Claude API doesn't have a models list endpoint, return static list
    return AVAILABLE_MODELS['claude']


def list_perplexity_models(api_key: str) -> list:
    """List available Perplexity models (static list)."""
    if not _OPENAI_AVAILABLE or not api_key:
        return []

    # Perplexity doesn't expose model listing, return static list
    return AVAILABLE_MODELS['perplexity']


class OpenAIClient:
    """OpenAI API client wrapper."""

    def __init__(self, api_key: Optional[str], model: str = 'gpt-4o-mini'):
        self.api_key = api_key
        self.model = model
        self.available = bool(api_key) and _OPENAI_AVAILABLE
        self.client = OpenAI(api_key=api_key) if self.available else None

    def verify_key(self) -> Tuple[bool, str]:
        """Verify API key is valid."""
        if not _OPENAI_AVAILABLE:
            return False, "OpenAI SDK not installed (pip install openai)"
        if not self.api_key:
            return False, "No API key provided"
        if not has_internet():
            return False, "No internet connection"

        try:
            models = self.client.models.list()
            if not models or not getattr(models, "data", None):
                return False, "Could not list models"
            return True, "✅ Valid key, internet OK, OpenAI access confirmed"
        except Exception as e:
            return False, f"❌ Key validation error: {str(e)}"

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send chat request to OpenAI."""
        if not self.available:
            return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"<<API ERROR: {str(e)}>>"


class GeminiClient:
    """Google Gemini API client wrapper."""

    def __init__(self, api_key: Optional[str], model: str = 'gemini-2.5-flash'):
        self.api_key = api_key
        self.model = model
        self.available = bool(api_key) and _GEMINI_AVAILABLE

    def verify_key(self) -> Tuple[bool, str]:
        """Verify API key is valid."""
        if not _GEMINI_AVAILABLE:
            return False, "Gemini SDK not installed (pip install google-genai)"
        if not self.api_key:
            return False, "No API key provided"
        if not has_internet():
            return False, "No internet connection"

        try:
            with genai.Client(api_key=self.api_key) as client:
                ok = any(
                    "generateContent" in (model.supported_actions or [])
                    for model in client.models.list()
                )
            if ok:
                return True, "✅ Valid key, internet OK, Gemini access confirmed"
            return False, "Could not list/verify Gemini models"
        except Exception as e:
            return False, f"❌ Key validation error: {str(e)}"

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send chat request to Gemini."""
        if not self.available:
            return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"

        try:
            with genai.Client(api_key=self.api_key) as client:
                response = client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config={"system_instruction": system_prompt},
                )
            return getattr(response, "text", "") or ""
        except Exception as e:
            return f"<<API ERROR: {str(e)}>>"


class ClaudeClient:
    """Anthropic Claude API client wrapper."""

    def __init__(self, api_key: Optional[str], model: str = 'claude-sonnet-4-20250514'):
        self.api_key = api_key
        self.model = model
        self.available = bool(api_key) and _CLAUDE_AVAILABLE
        self.client = anthropic.Anthropic(api_key=api_key) if self.available else None

    def verify_key(self) -> Tuple[bool, str]:
        """Verify API key is valid."""
        if not _CLAUDE_AVAILABLE:
            return False, "Claude SDK not installed (pip install anthropic)"
        if not self.api_key:
            return False, "No API key provided"
        if not has_internet():
            return False, "No internet connection"

        try:
            # Test with minimal request
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            if response and hasattr(response, 'content'):
                return True, "✅ Valid key, internet OK, Claude access confirmed"
            return False, "Could not verify Claude API"
        except Exception as e:
            return False, f"❌ Key validation error: {str(e)}"

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send chat request to Claude."""
        if not self.available:
            return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text if response.content else ""
        except Exception as e:
            return f"<<API ERROR: {str(e)}>>"


class PerplexityClient:
    """Perplexity API client wrapper (OpenAI-compatible)."""

    def __init__(self, api_key: Optional[str], model: str = 'llama-3.1-sonar-small-128k-online'):
        self.api_key = api_key
        self.model = model
        self.available = bool(api_key) and _OPENAI_AVAILABLE
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        ) if self.available else None

    def verify_key(self) -> Tuple[bool, str]:
        """Verify API key is valid."""
        if not _OPENAI_AVAILABLE:
            return False, "OpenAI SDK not installed (pip install openai) - required for Perplexity"
        if not self.api_key:
            return False, "No API key provided"
        if not has_internet():
            return False, "No internet connection"

        try:
            # Test with minimal request
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            if response and response.choices:
                return True, "✅ Valid key, internet OK, Perplexity access confirmed"
            return False, "Could not verify Perplexity API"
        except Exception as e:
            return False, f"❌ Key validation error: {str(e)}"

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send chat request to Perplexity."""
        if not self.available:
            return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"<<API ERROR: {str(e)}>>"


class OllamaClient:
    """Bounded client for a local Ollama service, including image-capable models."""

    def __init__(self, _api_key=None, model: str = "llava:latest", base_url=OLLAMA_BASE_URL):
        self.model = model or "llava:latest"
        self.base_url = base_url.rstrip("/")
        self.available = True

    def _request(self, path, payload=None, timeout=120):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(f"{self.base_url}{path}", data=data, headers=headers)
        with urlopen(request, timeout=timeout) as response:
            return _read_bounded_json(response)

    def verify_key(self) -> Tuple[bool, str]:
        """Verify the local service and selected model; no key is required."""
        models = list_ollama_models(self.base_url)
        names = {model["name"] for model in models}
        if not models:
            return False, "Ollama is unavailable or has no installed models"
        if self.model not in names:
            return False, f"Ollama is running, but model '{self.model}' is not installed"
        return True, f"Ollama is running and model '{self.model}' is available"

    def _chat_payload(self, system_prompt, user_prompt, images=None):
        user_message = {"role": "user", "content": user_prompt}
        if images:
            user_message["images"] = images
        return {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                user_message,
            ],
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096,
                "num_predict": 1024,
            },
        }

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a bounded text request to local Ollama."""
        try:
            response = self._request(
                "/api/chat", self._chat_payload(system_prompt, user_prompt)
            )
            return str(response.get("message", {}).get("content", ""))
        except Exception as exc:
            return f"<<OLLAMA ERROR: {exc}>>"

    def chat_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str,
        max_bytes: Optional[int] = None,
    ) -> str:
        """Send one bounded image to a locally installed multimodal model."""
        limit = min(max_bytes or OLLAMA_MAX_IMAGE_BYTES, OLLAMA_MAX_IMAGE_BYTES)
        path = Path(image_path)
        with path.open("rb") as stream:
            image = stream.read(limit + 1)
        if len(image) > limit:
            raise ValueError(f"Image exceeds the {limit}-byte safety limit")

        encoded = base64.b64encode(image).decode("ascii")
        try:
            response = self._request(
                "/api/chat",
                self._chat_payload(system_prompt, user_prompt, images=[encoded]),
            )
            return str(response.get("message", {}).get("content", ""))
        except Exception as exc:
            return f"<<OLLAMA ERROR: {exc}>>"
