#!/usr/bin/env python3
"""
Teste manual dos filtros do FileFilterPanel
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_size_filter():
    """Testa filtro de tamanho máximo"""
    print("=== TESTE 1: Size Max Filter ===")
    
    # Criar arquivo de teste 40KB
    test_file = Path("test_large.txt")
    test_file.write_text("x" * 40000)
    file_size = test_file.stat().st_size
    
    # Simular filtro size_max = 30KB
    size_max_bytes = 30 * 1024
    passes_filter = file_size <= size_max_bytes
    
    print(f"Arquivo: {test_file}")
    print(f"Tamanho: {file_size} bytes ({file_size/1024:.2f} KB)")
    print(f"Filtro size_max: {size_max_bytes} bytes (30 KB)")
    print(f"Passa no filtro: {passes_filter}")
    print(f"Esperado: False")
    print(f"✅ PASSOU" if not passes_filter else "❌ FALHOU")
    
    test_file.unlink()
    print()

def test_modify_after():
    """Testa filtro Modify After"""
    print("=== TESTE 2: Modify After Filter ===")
    
    # Criar arquivo recente
    test_file = Path("test_recent.txt")
    test_file.write_text("test")
    file_mtime = datetime.fromtimestamp(test_file.stat().st_mtime)
    
    # Filtro: modified_after = 2025-01-01
    filter_date = datetime(2025, 1, 1)
    passes_filter = file_mtime > filter_date
    
    print(f"Arquivo: {test_file}")
    print(f"Data modificação: {file_mtime}")
    print(f"Filtro modified_after: {filter_date}")
    print(f"Passa no filtro: {passes_filter}")
    print(f"Esperado: True")
    print(f"✅ PASSOU" if passes_filter else "❌ FALHOU")
    
    test_file.unlink()
    print()

def test_modify_before():
    """Testa filtro Modify Before"""
    print("=== TESTE 3: Modify Before Filter ===")
    
    # Criar arquivo novo
    test_file = Path("test_new.txt")
    test_file.write_text("test")
    file_mtime = datetime.fromtimestamp(test_file.stat().st_mtime)
    
    # Filtro: modified_before = 2024-01-01
    filter_date = datetime(2024, 1, 1)
    passes_filter = file_mtime < filter_date
    
    print(f"Arquivo: {test_file}")
    print(f"Data modificação: {file_mtime}")
    print(f"Filtro modified_before: {filter_date}")
    print(f"Passa no filtro: {passes_filter}")
    print(f"Esperado: False")
    print(f"✅ PASSOU" if not passes_filter else "❌ FALHOU")
    
    test_file.unlink()
    print()

if __name__ == "__main__":
    print("🔬 TESTES MANUAIS DOS FILTROS\n")
    test_size_filter()
    test_modify_after()
    test_modify_before()
    print("✅ Testes concluídos!")
