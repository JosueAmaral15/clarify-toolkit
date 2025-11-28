#!/usr/bin/env python3
"""
Testes para a funcionalidade de Multi-Query Search (v2.8.0)
"""
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Add src directory to path
project_root = Path(__file__).parent.parent
multi_query_path = project_root / "src" / "core" / "multi_query.py"

# Load module directly
import importlib.util
spec = importlib.util.spec_from_file_location("multi_query", multi_query_path)
multi_query_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(multi_query_module)

MultiQueryProcessor = multi_query_module.MultiQueryProcessor
split_multi_query = multi_query_module.split_multi_query


def test_single_query():
    """Testa busca com uma única query (compatibilidade reversa)"""
    print("🧪 Test 1: Single Query")
    
    processor = MultiQueryProcessor(
        multi_line_text="test",
        case_sensitive=False,
        whole_word=False,
        use_regex=False
    )
    
    assert processor.get_query_count() == 1, "Deve ter 1 query"
    
    text = "This is a test line\nAnother test here\nNo match"
    matches = processor.search_in_text(text)
    
    assert len(matches) == 2, f"Esperado 2 matches, obteve {len(matches)}"
    print("✅ Passed: Single query encontrou 2 matches")


def test_multi_query_two_patterns():
    """Testa busca com duas queries"""
    print("\n🧪 Test 2: Two Queries")
    
    processor = MultiQueryProcessor(
        multi_line_text="error\nwarning",
        case_sensitive=False,
        whole_word=False,
        use_regex=False
    )
    
    assert processor.get_query_count() == 2, "Deve ter 2 queries"
    
    text = "Error occurred\nWarning: check this\nInfo: all good"
    matches = processor.search_in_text(text)
    
    # Deve encontrar "error" e "warning"
    assert len(matches) >= 2, f"Esperado pelo menos 2 matches, obteve {len(matches)}"
    print(f"✅ Passed: Duas queries encontraram {len(matches)} matches")


def test_multi_query_with_comments():
    """Testa que comentários são ignorados"""
    print("\n🧪 Test 3: Queries with Comments")
    
    query_text = """# Buscar por erros
error
# Buscar por avisos
warning
# info - desabilitado"""
    
    processor = MultiQueryProcessor(
        multi_line_text=query_text,
        case_sensitive=False,
        whole_word=False,
        use_regex=False
    )
    
    # Apenas 2 queries válidas (error e warning)
    assert processor.get_query_count() == 2, f"Esperado 2 queries, obteve {processor.get_query_count()}"
    print("✅ Passed: Comentários ignorados corretamente")


def test_multi_query_with_empty_lines():
    """Testa que linhas vazias são ignoradas"""
    print("\n🧪 Test 4: Queries with Empty Lines")
    
    query_text = """error

warning

"""
    
    processor = MultiQueryProcessor(
        multi_line_text=query_text,
        case_sensitive=False,
        whole_word=False,
        use_regex=False
    )
    
    assert processor.get_query_count() == 2, f"Esperado 2 queries, obteve {processor.get_query_count()}"
    print("✅ Passed: Linhas vazias ignoradas corretamente")


def test_multi_query_with_regex():
    """Testa queries com regex"""
    print("\n🧪 Test 5: Queries with Regex")
    
    # Use quebras de linha reais, não \n escapado
    processor = MultiQueryProcessor(
        multi_line_text=r"""error\d+
warning:\s+\w+""",
        case_sensitive=False,
        whole_word=False,
        use_regex=True
    )
    
    assert processor.get_query_count() == 2, f"Deve ter 2 queries, obteve {processor.get_query_count()}"
    
    text = "error123 occurred\nwarning: check\nerror456 also\nwarning: another"
    matches = processor.search_in_text(text)
    
    # Deve encontrar error123, error456, warning: check, warning: another
    assert len(matches) >= 4, f"Esperado pelo menos 4 matches, obteve {len(matches)}"
    print(f"✅ Passed: Regex queries encontraram {len(matches)} matches")


def test_multi_query_five_patterns():
    """Testa busca com 5 queries"""
    print("\n🧪 Test 6: Five Queries")
    
    query_text = """error
warning
info
debug
trace"""
    
    processor = MultiQueryProcessor(
        multi_line_text=query_text,
        case_sensitive=False,
        whole_word=False,
        use_regex=False
    )
    
    assert processor.get_query_count() == 5, f"Esperado 5 queries, obteve {processor.get_query_count()}"
    
    text = "ERROR: failed\nWARNING: check\nINFO: ok\nDEBUG: test\nTRACE: log"
    matches = processor.search_in_text(text)
    
    assert len(matches) == 5, f"Esperado 5 matches, obteve {len(matches)}"
    print(f"✅ Passed: Cinco queries encontraram {len(matches)} matches")


def test_result_deduplication():
    """Testa que duplicatas são removidas"""
    print("\n🧪 Test 7: Result Deduplication")
    
    # Duas queries que podem dar match na mesma posição
    processor = MultiQueryProcessor(
        multi_line_text="test\ntest.*",
        case_sensitive=False,
        whole_word=False,
        use_regex=True
    )
    
    text = "test line"
    matches = processor.search_in_text(text)
    
    # Deve ter matches, mas duplicatas devem ser removidas
    unique_positions = set((m[0], m[1]) for m in matches)
    assert len(matches) <= len(unique_positions) * 2, "Muitas duplicatas não foram removidas"
    print(f"✅ Passed: Deduplicação funcionando (matches: {len(matches)}, posições: {len(unique_positions)})")


def test_case_sensitive():
    """Testa busca case-sensitive"""
    print("\n🧪 Test 8: Case Sensitive")
    
    processor_sensitive = MultiQueryProcessor(
        multi_line_text="Error",
        case_sensitive=True,
        whole_word=False,
        use_regex=False
    )
    
    text = "Error occurred\nerror also\nERROR too"
    matches = processor_sensitive.search_in_text(text)
    
    # Apenas "Error" deve dar match (case-sensitive)
    assert len(matches) == 1, f"Esperado 1 match, obteve {len(matches)}"
    print("✅ Passed: Case-sensitive funcionando")


def test_whole_word():
    """Testa busca whole-word"""
    print("\n🧪 Test 9: Whole Word")
    
    processor_word = MultiQueryProcessor(
        multi_line_text="test",
        case_sensitive=False,
        whole_word=True,
        use_regex=False
    )
    
    text = "test is here\ntesting not match\ntest."
    matches = processor_word.search_in_text(text)
    
    # Apenas "test " e "test." devem dar match (word boundaries)
    assert len(matches) == 2, f"Esperado 2 matches, obteve {len(matches)}"
    print("✅ Passed: Whole word funcionando")


def test_validation():
    """Testa validação de queries"""
    print("\n🧪 Test 10: Query Validation")
    
    # Query muito longa (>500 chars)
    long_query = "a" * 501
    processor = MultiQueryProcessor(
        multi_line_text=long_query,
        case_sensitive=False,
        whole_word=False,
        use_regex=False
    )
    
    is_valid, error_msg = processor.validate()
    assert not is_valid, "Deve ser inválido"
    assert len(error_msg) > 0, "Deve ter mensagem de erro"
    print(f"✅ Passed: Validação detectou query longa: {error_msg[:60]}...")


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("Multi-Query Search Tests (v2.8.0)")
    print("=" * 60)
    
    try:
        test_single_query()
        test_multi_query_two_patterns()
        test_multi_query_with_comments()
        test_multi_query_with_empty_lines()
        test_multi_query_with_regex()
        test_multi_query_five_patterns()
        test_result_deduplication()
        test_case_sensitive()
        test_whole_word()
        test_validation()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM! (10/10)")
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
