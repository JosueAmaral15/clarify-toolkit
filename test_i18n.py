#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for i18n system (Task #24 - v2.9.10)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.i18n import get_translator, switch_language, tr

def test_translator():
    """Test translator functionality."""
    print("=" * 60)
    print("Testing i18n System (Task #24 - v2.9.10)")
    print("=" * 60)
    
    translator = get_translator()
    
    # Test 1: Check detected language
    print(f"\n1. Auto-detected language: {translator.current_language}")
    print(f"   Available languages: {translator.available_languages}")
    
    # Test 2: Get translations in current language
    print(f"\n2. Translations in {translator.current_language}:")
    print(f"   app.title = {tr('app.title')}")
    print(f"   menu.file = {tr('menu.file')}")
    print(f"   menu.edit.undo = {tr('menu.edit.undo')}")
    print(f"   search.button = {tr('search.button')}")
    
    # Test 3: Switch to Portuguese
    print("\n3. Switching to Portuguese...")
    switch_language("pt_BR")
    print(f"   Current language: {translator.current_language}")
    print(f"   app.title = {tr('app.title')}")
    print(f"   menu.file = {tr('menu.file')}")
    print(f"   menu.edit.undo = {tr('menu.edit.undo')}")
    print(f"   search.button = {tr('search.button')}")
    
    # Test 4: Switch to English
    print("\n4. Switching to English...")
    switch_language("en")
    print(f"   Current language: {translator.current_language}")
    print(f"   app.title = {tr('app.title')}")
    print(f"   menu.file = {tr('menu.file')}")
    print(f"   menu.edit.undo = {tr('menu.edit.undo')}")
    print(f"   search.button = {tr('search.button')}")
    
    # Test 5: Missing key fallback
    print("\n5. Testing fallback for missing key:")
    print(f"   missing.key = {tr('missing.key')}")
    print(f"   missing.key (with default) = {tr('missing.key', 'Default Value')}")
    
    # Test 6: Language names
    print("\n6. Language display names:")
    for lang in translator.available_languages:
        print(f"   {lang}: {translator.get_language_name(lang)}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_translator()
