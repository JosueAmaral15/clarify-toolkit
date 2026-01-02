#!/usr/bin/env python3
"""
Teste manual dos filtros Modify After/Before do Advanced Filters
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Test directory
test_dir = Path("/home/josue/Documents/Informática/Programação/programming workspace/archived/PTEasy/PTEasy-frontend-v2")

print("=== TESTE MANUAL: Modify After/Before ===\n")
print(f"Diretório de teste: {test_dir}\n")

# Get all files with their modification times
files = []
for root, dirs, filenames in os.walk(test_dir):
    for filename in filenames:
        filepath = Path(root) / filename
        try:
            mtime = filepath.stat().st_mtime
            mtime_dt = datetime.fromtimestamp(mtime)
            files.append((filepath, mtime_dt))
        except:
            pass

files.sort(key=lambda x: x[1])

print(f"Total de arquivos encontrados: {len(files)}\n")
print("Primeiros 10 arquivos (mais antigos):")
for f, dt in files[:10]:
    print(f"  {dt.strftime('%Y-%m-%d %H:%M:%S')} - {f.name}")

print("\nÚltimos 10 arquivos (mais recentes):")
for f, dt in files[-10:]:
    print(f"  {dt.strftime('%Y-%m-%d %H:%M:%S')} - {f.name}")

# Test filter
print("\n=== TESTE: Filtrar arquivos modificados após 2024-01-01 ===")
target_date = datetime(2024, 1, 1)
filtered = [f for f, dt in files if dt >= target_date]
print(f"Arquivos modificados após 2024-01-01: {len(filtered)}")

print("\n=== TESTE: Filtrar arquivos modificados antes de 2024-01-01 ===")
filtered_before = [f for f, dt in files if dt < target_date]
print(f"Arquivos modificados antes de 2024-01-01: {len(filtered_before)}")

print("\n✅ Teste manual concluído. Use estes valores para comparar com o File Explorer.")
