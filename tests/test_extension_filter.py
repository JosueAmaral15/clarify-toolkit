#!/usr/bin/env python3
"""
Testes para o filtro de extensões (v2.9.0)
"""
import sys
import re
from pathlib import Path


def parse_extensions_to_globs(extensions_text: str):
    """Parse extension filter text into glob patterns."""
    if not extensions_text or not extensions_text.strip():
        return []
    
    extensions = [ext.strip() for ext in re.split(r"[;,]", extensions_text) if ext.strip()]
    extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
    return [f"*{ext}" for ext in extensions]


def test_parse_extensions_basic():
    """Testa parsing básico de extensões"""
    print("🧪 Test 1: Basic parsing")
    
    result = parse_extensions_to_globs(".py,.js,.tsx")
    expected = ["*.py", "*.js", "*.tsx"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Passed")


def test_parse_extensions_without_dots():
    """Testa parsing sem pontos"""
    print("\n🧪 Test 2: Without dots")
    
    result = parse_extensions_to_globs("py,js,tsx")
    expected = ["*.py", "*.js", "*.tsx"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Passed")


def test_parse_extensions_semicolon():
    """Testa parsing com ponto e vírgula"""
    print("\n🧪 Test 3: Semicolon separator")
    
    result = parse_extensions_to_globs(".py;.js;.tsx")
    expected = ["*.py", "*.js", "*.tsx"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Passed")


def test_parse_extensions_empty():
    """Testa string vazia"""
    print("\n🧪 Test 4: Empty string")
    
    result = parse_extensions_to_globs("")
    expected = []
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Passed")


def test_parse_extensions_whitespace():
    """Testa com espaços em branco"""
    print("\n🧪 Test 5: With whitespace")
    
    result = parse_extensions_to_globs("  .py  ,  .js  ,  .tsx  ")
    expected = ["*.py", "*.js", "*.tsx"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Passed")


def test_parse_extensions_mixed():
    """Testa formato misto"""
    print("\n🧪 Test 6: Mixed format")
    
    result = parse_extensions_to_globs("py, .js, tsx")
    expected = ["*.py", "*.js", "*.tsx"]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ Passed")


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("Extension Filter Tests (v2.9.0)")
    print("=" * 60)
    
    try:
        test_parse_extensions_basic()
        test_parse_extensions_without_dots()
        test_parse_extensions_semicolon()
        test_parse_extensions_empty()
        test_parse_extensions_whitespace()
        test_parse_extensions_mixed()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM! (6/6)")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
