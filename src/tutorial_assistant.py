"""
Tutorial Assistant Module

AI-powered chatbot to help users with Clarify tutorials.
Uses Gemini Flash for natural language understanding.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple


from .utils.logger import get_logger

logger = get_logger(__name__)

try:
    from google import genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False


class TutorialAssistant:
    """
    AI assistant for helping users with Clarify tutorials.

    Features:
    - Knowledge base from docs/tutorials/
    - Session-based conversation history
    - Natural language understanding via Gemini Flash
    - Context-aware responses
    """

    def __init__(self, api_key: Optional[str] = None, base_path: Optional[Path] = None):
        """
        Initialize tutorial assistant.

        Args:
            api_key: Google Gemini API key (optional, uses env var if not provided)
            base_path: Base path to tutorials directory (defaults to docs/tutorials/)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.base_path = base_path or Path(__file__).parent.parent / 'docs' / 'tutorials'
        self.available = bool(self.api_key) and _GEMINI_AVAILABLE

        # Session state
        self.conversation_history: List[Dict[str, str]] = []
        self.knowledge_base: Dict = {}
        self.tutorials_content: Dict[str, str] = {}

        self.model = 'gemini-2.5-flash'

        # Load knowledge base
        self._load_knowledge_base()

    def _load_knowledge_base(self) -> None:
        """Load tutorials index and content into memory."""
        index_file = self.base_path / 'index.json'

        if not index_file.exists():
            return

        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)

            # Load tutorial markdown files
            tutorials = self.knowledge_base.get('tutorials', [])
            for tutorial in tutorials:
                file_path = self.base_path / tutorial['file']
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.tutorials_content[tutorial['id']] = f.read()

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Warning: Could not load tutorial knowledge base: {e}")

    def _build_context(self, user_query: str) -> str:
        """
        Build context for AI from knowledge base.

        Args:
            user_query: User's question

        Returns:
            Formatted context string
        """
        context_parts = []

        # Add general info
        context_parts.append("You are a helpful assistant for Clarify, a JSON management tool.")
        context_parts.append("\nAvailable tutorials:")

        # Add tutorial summaries
        tutorials = self.knowledge_base.get('tutorials', [])
        for tutorial in tutorials:
            title = tutorial.get('title', 'Unknown')
            desc = tutorial.get('description', '')
            keywords = ', '.join(tutorial.get('keywords', []))
            time = tutorial.get('estimated_time', 'Unknown')

            context_parts.append(f"\n- {title}: {desc}")
            context_parts.append(f"  Keywords: {keywords} | Time: {time}")

        # Add FAQ
        faqs = self.knowledge_base.get('faq', [])
        if faqs:
            context_parts.append("\n\nFrequently Asked Questions:")
            for faq in faqs[:5]:  # Limit to top 5 FAQs
                question = faq.get('question', '')
                answer = faq.get('answer', '')
                context_parts.append(f"\nQ: {question}")
                context_parts.append(f"A: {answer}")

        # Search for relevant tutorial content based on keywords
        query_lower = user_query.lower()
        matched_tutorials = []

        for tutorial in tutorials:
            keywords = tutorial.get('keywords', [])
            if any(kw in query_lower for kw in keywords):
                matched_tutorials.append(tutorial['id'])

        # Add matched tutorial content (max 2 to avoid context overflow)
        if matched_tutorials:
            context_parts.append("\n\nRelevant tutorial content:")
            for tutorial_id in matched_tutorials[:2]:
                if tutorial_id in self.tutorials_content:
                    content = self.tutorials_content[tutorial_id]
                    # Limit content to first 500 chars
                    truncated = content[:500] + "..." if len(content) > 500 else content
                    context_parts.append(f"\n{truncated}")

        return '\n'.join(context_parts)

    def ask(self, user_query: str) -> Tuple[str, bool]:
        """
        Ask a question to the tutorial assistant.

        Args:
            user_query: User's question

        Returns:
            Tuple of (response_text, success)
        """
        if not self.available:
            return ("Tutorial assistant is not available. Please configure a Google Gemini API key.", False)

        if not user_query.strip():
            return ("Please enter a question.", False)

        try:
            # Build context
            context = self._build_context(user_query)

            # Build conversation history for context
            history_text = ""
            if self.conversation_history:
                history_text = "\n\nPrevious conversation:"
                for msg in self.conversation_history[-3:]:  # Last 3 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    history_text += f"\n{role.upper()}: {content}"

            # Construct prompt
            prompt = f"""
{context}

{history_text}

USER: {user_query}

ASSISTANT: Please provide a helpful, concise answer (max 300 words).
If suggesting a tutorial, mention its title and estimated time.
If the question is unclear, ask for clarification.
"""

            # Call Gemini API
            with genai.Client(api_key=self.api_key) as client:
                response = client.models.generate_content(model=self.model, contents=prompt)
            response_text = response.text.strip()

            # Update conversation history
            self.conversation_history.append({'role': 'user', 'content': user_query})
            self.conversation_history.append({'role': 'assistant', 'content': response_text})

            # Limit history to last 10 messages (5 exchanges)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return (response_text, True)

        except Exception as e:  # pylint: disable=broad-exception-caught
            error_msg = f"Error communicating with AI: {str(e)}"
            return (error_msg, False)

    def reset_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get current conversation history."""
        return self.conversation_history.copy()

    def is_available(self) -> bool:
        """Check if assistant is available."""
        return self.available

    def get_tutorial_list(self) -> List[Dict]:
        """Get list of available tutorials."""
        return self.knowledge_base.get('tutorials', [])

    def get_faq_list(self) -> List[Dict]:
        """Get list of FAQs."""
        return self.knowledge_base.get('faq', [])


# Singleton instance (private, use get_assistant())
_assistant_instance: Optional[TutorialAssistant] = None  # pylint: disable=invalid-name


def get_assistant(api_key: Optional[str] = None) -> TutorialAssistant:
    """
    Get singleton tutorial assistant instance.

    Args:
        api_key: Google Gemini API key (only used on first call)

    Returns:
        TutorialAssistant instance
    """
    global _assistant_instance  # pylint: disable=global-statement

    if _assistant_instance is None:
        _assistant_instance = TutorialAssistant(api_key=api_key)

    return _assistant_instance
