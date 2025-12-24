"""
Operation history management.
Extracted from app.py (v2.9.114).
"""

from pathlib import Path
import json
from datetime import datetime


class OperationHistory:
    """
    Manages persistent history of operations (v2.5.0+).
    Saves to ~/.clarify_history.json
    """
    def __init__(self):
        self.history_file = Path.home() / ".clarify_history.json"
        self.history = self._load_history()
    
    def _load_history(self):
        """Load history from disk."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_history(self):
        """Save history to disk."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-1000:], f, indent=2)  # Keep last 1000
        except Exception as e:
            print(f"Failed to save history: {e}")
    
    def add_operation(self, operation_type: str, details: dict):
        """Add operation to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": operation_type,
            "details": details
        }
        self.history.append(entry)
        self._save_history()
    
    def get_recent(self, count: int = 10):
        """Get recent operations."""
        return self.history[-count:]
    
    def clear(self):
        """Clear all history."""
        self.history = []
        self._save_history()
