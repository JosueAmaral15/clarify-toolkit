"""
GUI Panels - Reusable UI Components

Modular panels that can be integrated into multiple docks/editors.

Pattern: Composite (GoF)
- Reusable components
- Common interface
- Signal-based communication
"""

from .search_replace_panel import SearchReplacePanel
from .insert_panel import InsertPanel
from .regex_insert_panel import RegexInsertPanel

__all__ = ['SearchReplacePanel', 'InsertPanel', 'RegexInsertPanel']
