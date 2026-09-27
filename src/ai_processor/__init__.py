"""
AI Processor Package

Provides AI-powered file processing with OpenAI and Google Gemini APIs.
"""

from .token_counter import count_tokens, estimate_cost, is_tiktoken_available
from .api_client import (
    OpenAIClient, GeminiClient, ClaudeClient, PerplexityClient, OllamaClient, AVAILABLE_MODELS,
    has_internet, is_openai_available, is_gemini_available, is_claude_available,
    list_openai_models, list_gemini_models, list_claude_models, list_perplexity_models,
    list_ollama_models
)
from .processor import (
    read_file_safe, list_files_recursive, strip_code_fences,
    process_file, process_multiple_files, save_results,
    extract_between_markers
)
from .template_engine import (
    TemplateEngine, render_prompt, create_context, has_templates, preview_template
)

__all__ = [
    'count_tokens', 'estimate_cost', 'is_tiktoken_available',
    'OpenAIClient', 'GeminiClient', 'ClaudeClient', 'PerplexityClient', 'OllamaClient', 'AVAILABLE_MODELS',
    'has_internet', 'is_openai_available', 'is_gemini_available', 'is_claude_available',
    'list_openai_models', 'list_gemini_models', 'list_claude_models', 'list_perplexity_models',
    'list_ollama_models',
    'read_file_safe', 'list_files_recursive', 'strip_code_fences',
    'process_file', 'process_multiple_files', 'save_results',
    'extract_between_markers',
    'TemplateEngine', 'render_prompt', 'create_context', 'has_templates', 'preview_template'
]
