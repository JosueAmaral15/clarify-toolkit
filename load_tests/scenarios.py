"""
Scenarios - Cenários de teste de carga para Clarify

Define cenários realistas de uso intensivo:
1. Batch Processing: Processar 1000+ arquivos simultaneamente
2. Set Operations: Union/Intersection com 100+ arquivos grandes

Author: Josué Amaral
Date: 21/12/2024
"""

import json
import random
import time
from pathlib import Path
from typing import List, Tuple, Callable
import tempfile
import shutil

# Imports do Clarify
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import set_operations


class Scenarios:
    """
    Cenários de teste de carga para Clarify.
    
    Cada cenário simula um caso de uso real com alta demanda.
    """
    
    @staticmethod
    def generate_test_corpus(
        size_mb: float,
        num_files: int,
        output_dir: Path
    ) -> List[Path]:
        """
        Gera corpus de teste com distribuição realística de tamanhos.
        
        Distribuição:
        - 70% arquivos pequenos (10-100KB)
        - 20% arquivos médios (1-5MB)
        - 10% arquivos grandes (10-50MB)
        
        Args:
            size_mb: Tamanho total alvo em MB (aproximado)
            num_files: Número de arquivos a gerar
            output_dir: Diretório de saída
            
        Returns:
            Lista de Paths dos arquivos gerados
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        random.seed(42)  # Reproducibilidade
        
        files = []
        target_size_bytes = size_mb * 1024 * 1024
        current_size = 0
        
        for i in range(num_files):
            # Determina tamanho do arquivo baseado na distribuição
            rand = random.random()
            
            if rand < 0.7:  # 70% pequenos
                file_size_kb = random.randint(10, 100)
            elif rand < 0.9:  # 20% médios
                file_size_kb = random.randint(1000, 5000)
            else:  # 10% grandes
                file_size_kb = random.randint(10000, 50000)
            
            # Ajusta se exceder target total
            remaining_kb = (target_size_bytes - current_size) / 1024
            if remaining_kb < file_size_kb:
                file_size_kb = max(10, int(remaining_kb))
            
            # Gera conteúdo JSON
            data = Scenarios._generate_json_content(file_size_kb)
            
            # Salva arquivo
            file_path = output_dir / f"test_file_{i:04d}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            
            files.append(file_path)
            current_size += file_path.stat().st_size
            
            # Para se atingir target
            if current_size >= target_size_bytes:
                break
        
        return files
    
    @staticmethod
    def _generate_json_content(target_size_kb: int) -> dict:
        """
        Gera conteúdo JSON com tamanho aproximado.
        
        Args:
            target_size_kb: Tamanho alvo em KB
            
        Returns:
            Dicionário Python (será serializado para JSON)
        """
        # Estima número de items necessários (~100 bytes por item)
        num_items = (target_size_kb * 1024) // 100
        
        items = []
        for i in range(num_items):
            item = {
                "id": i,
                "name": f"Item_{i:06d}",
                "value": random.uniform(0, 1000),
                "category": random.choice(["A", "B", "C", "D", "E"]),
                "tags": [f"tag_{j}" for j in range(random.randint(1, 5))],
                "metadata": {
                    "created_at": "2024-12-21T00:00:00Z",
                    "updated_at": "2024-12-21T00:00:00Z",
                    "version": 1
                }
            }
            items.append(item)
        
        return {
            "version": "1.0",
            "generated_at": "2024-12-21T00:00:00Z",
            "items": items,
            "count": len(items)
        }
    
    @staticmethod
    def batch_file_processing(
        num_files: int = 100,
        operation_func: Callable[[Path], Tuple[bool, float]] = None
    ) -> List[Tuple[bool, float, float]]:
        """
        Cenário 1: Processar múltiplos arquivos em batch.
        
        Simula processamento massivo de arquivos JSON (ex: conversão de formato,
        validação, transformação).
        
        Args:
            num_files: Número de arquivos a processar
            operation_func: Função customizada de processamento.
                           Se None, usa operação dummy (apenas leitura).
                           Deve retornar (success: bool, duration: float)
            
        Returns:
            Lista de (success, duration_seconds, size_mb) para cada arquivo
        """
        # Cria diretório temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="clarify_load_"))
        
        try:
            # Gera corpus de teste (total ~50MB)
            files = Scenarios.generate_test_corpus(
                size_mb=50.0,
                num_files=num_files,
                output_dir=temp_dir
            )
            
            # Operação default: ler e parsear JSON
            if operation_func is None:
                def default_operation(file_path: Path) -> Tuple[bool, float]:
                    start = time.time()
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Simula processamento (valida estrutura)
                        assert "items" in data
                        assert "count" in data
                        
                        duration = time.time() - start
                        return (True, duration)
                    except Exception as e:
                        duration = time.time() - start
                        return (False, duration)
                
                operation_func = default_operation
            
            # Processa arquivos
            results = []
            for file_path in files:
                success, duration = operation_func(file_path)
                size_mb = file_path.stat().st_size / (1024 * 1024)
                results.append((success, duration, size_mb))
            
            return results
        
        finally:
            # Limpa diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    def set_operations_stress(
        num_files: int = 10,
        operation: str = "union"
    ) -> List[Tuple[bool, float, float]]:
        """
        Cenário 2: Set Operations (union/intersection) com múltiplos arquivos grandes.
        
        Simula operações de conjunto em arquivos JSON grandes, testando
        uso de memória e performance de algoritmos.
        
        Args:
            num_files: Número de arquivos para operação (default: 10)
            operation: Tipo de operação ("union" ou "intersection")
            
        Returns:
            Lista de (success, duration_seconds, size_mb) para cada operação
        """
        # Cria diretório temporário
        temp_dir = Path(tempfile.mkdtemp(prefix="clarify_load_"))
        
        try:
            # Gera arquivos grandes (5MB cada)
            files = Scenarios.generate_test_corpus(
                size_mb=5.0 * num_files,
                num_files=num_files,
                output_dir=temp_dir
            )
            
            # Converte Paths para strings (SetOperations espera strings)
            file_paths = [str(f) for f in files]
            
            results = []
            
            # Executa operação de conjunto
            start = time.time()
            try:
                # Carrega JSONs
                file_dicts = []
                for file_path in file_paths:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_dicts.append(json.load(f))
                
                if operation == "union":
                    result_data = set_operations.union(file_dicts)
                elif operation == "intersection":
                    result_data = set_operations.intersection(file_dicts)
                else:
                    raise ValueError(f"Operação desconhecida: {operation}")
                
                duration = time.time() - start
                
                # Calcula tamanho total processado
                total_size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
                
                results.append((True, duration, total_size_mb))
            
            except Exception as e:
                duration = time.time() - start
                total_size_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
                results.append((False, duration, total_size_mb))
            
            return results
        
        finally:
            # Limpa diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    def mixed_operations(
        num_iterations: int = 50
    ) -> List[Tuple[str, bool, float, float]]:
        """
        Cenário 3: Operações mistas (batch + set operations).
        
        Simula carga mista de diferentes tipos de operações, mais realístico
        para uso em produção.
        
        Args:
            num_iterations: Número de iterações (cada iteração = batch + set op)
            
        Returns:
            Lista de (operation_type, success, duration_seconds, size_mb)
        """
        results = []
        
        for i in range(num_iterations):
            # Alterna entre batch processing e set operations
            if i % 2 == 0:
                # Batch processing (10 files)
                batch_results = Scenarios.batch_file_processing(num_files=10)
                for success, duration, size_mb in batch_results:
                    results.append(("batch_process", success, duration, size_mb))
            else:
                # Set operation (5 files, union)
                set_results = Scenarios.set_operations_stress(num_files=5, operation="union")
                for success, duration, size_mb in set_results:
                    results.append(("set_union", success, duration, size_mb))
        
        return results
