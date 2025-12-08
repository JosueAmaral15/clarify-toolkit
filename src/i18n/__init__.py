"""
Internationalization system for Clarify.

Provides runtime language switching without restart.
Supports lazy loading and on-demand translation.

Usage:
    from src.i18n import get_translator, switch_language, tr
    
    translator = get_translator()
    print(translator.get("menu.file"))
    
    # Or use shorthand
    print(tr("menu.file"))
    
    switch_language("pt_BR")  # Runtime switch
"""

from .translator import Translator, get_translator, switch_language, tr, tooltip_tr

__all__ = ['Translator', 'get_translator', 'switch_language', 'tr', 'tooltip_tr']
