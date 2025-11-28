"""
AI API Client Module

Provides unified interface for OpenAI and Google Gemini APIs.
"""

from typing import Optional, Tuple
import socket

try:
    from openai import OpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
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
    ]
}


def has_internet() -> bool:
    """Check if internet connection is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
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
        genai.configure(api_key=api_key)
        models = genai.list_models()
        
        # Filter for generative models
        gen_models = []
        for model in models:
            if hasattr(model, 'name') and hasattr(model, 'supported_generation_methods'):
                if 'generateContent' in model.supported_generation_methods:
                    # Extract model name (e.g., "models/gemini-2.5-flash" -> "gemini-2.5-flash")
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
        
        if self.available:
            try:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(self.model)
            except Exception:
                self.available = False
                self._model = None
        else:
            self._model = None
    
    def verify_key(self) -> Tuple[bool, str]:
        """Verify API key is valid."""
        if not _GEMINI_AVAILABLE:
            return False, "Gemini SDK not installed (pip install google-generativeai)"
        if not self.api_key:
            return False, "No API key provided"
        if not has_internet():
            return False, "No internet connection"
        
        try:
            models = list(genai.list_models())
            ok = any(
                hasattr(m, "supported_generation_methods")
                and "generateContent" in m.supported_generation_methods
                for m in models
            )
            if ok:
                return True, "✅ Valid key, internet OK, Gemini access confirmed"
            return False, "Could not list/verify Gemini models"
        except Exception as e:
            return False, f"❌ Key validation error: {str(e)}"
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send chat request to Gemini."""
        if not self.available or not self._model:
            return ">> SIMULATED RESPONSE << (no valid API key or SDK missing)"
        
        try:
            # Gemini doesn't have roles the same way; fold system+user into single prompt
            prompt = f"[SYSTEM]\n{system_prompt}\n\n[USER]\n{user_prompt}"
            response = self._model.generate_content(prompt)
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
