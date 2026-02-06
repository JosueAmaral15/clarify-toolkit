"""
AI Token Counter Module

Provides token counting functionality for OpenAI (GPT) and Google Gemini models.
"""
# pylint: disable=broad-exception-caught  # Counting robustness


try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False


def count_tokens(text: str, model: str = 'gpt-4o') -> int:
    """
    Count tokens in text for a specific model.

    Args:
        text: Input text to count tokens
        model: Model name (default: 'gpt-4o')

    Returns:
        Number of tokens (approximate if tiktoken not available)
    """
    if not text:
        return 0

    if not _TIKTOKEN_AVAILABLE:
        # Fallback: rough estimate (1 token ≈ 4 chars)
        return len(text) // 4

    try:
        # Map model names to tiktoken encodings
        if "gpt-4" in model.lower() or "gpt-5" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-4")
        elif "gpt-3.5" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            # Default to cl100k_base (GPT-4, GPT-3.5-turbo, text-embedding-ada-002)
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))
    except Exception:
        # Fallback if encoding fails
        return len(text) // 4


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Estimate cost in USD based on token counts and model.

    Pricing (as of 2025):
    - gpt-4o-mini: $0.15/$0.60 per 1M tokens (in/out)
    - gpt-4o: $5.00/$15.00 per 1M tokens
    - gemini-2.5-flash: $0.10/$0.40 per 1M tokens (estimated)
    - gemini-2.5-pro: $0.50/$1.50 per 1M tokens (estimated)

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name

    Returns:
        Estimated cost in USD
    """
    model_lower = model.lower()

    # GPT pricing
    if "gpt-4o-mini" in model_lower:
        return (input_tokens * 0.00015 + output_tokens * 0.00060) / 1000.0
    elif "gpt-4o" in model_lower:
        return (input_tokens * 0.00500 + output_tokens * 0.01500) / 1000.0
    elif "gpt-5" in model_lower:
        # GPT-5 estimated pricing
        return (input_tokens * 0.01500 + output_tokens * 0.12000) / 1000.0

    # Gemini pricing (estimated)
    elif "gemini-2.5-flash" in model_lower or "gemini-flash" in model_lower:
        return (input_tokens * 0.00010 + output_tokens * 0.00040) / 1000.0
    elif "gemini-2.5-pro" in model_lower or "gemini-pro" in model_lower:
        return (input_tokens * 0.00050 + output_tokens * 0.00150) / 1000.0

    # Default fallback
    return (input_tokens * 0.00050 + output_tokens * 0.00150) / 1000.0


def is_tiktoken_available() -> bool:
    """Check if tiktoken is installed."""
    return _TIKTOKEN_AVAILABLE
