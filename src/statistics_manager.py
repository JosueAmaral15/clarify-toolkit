"""
Statistics Manager
Calcula estatísticas comparativas para operações de conjuntos JSON.
"""
from typing import Dict, Any, List
import json


class StatisticsManager:
    """Gerenciador de estatísticas para operações de conjunto."""
    
    @staticmethod
    def calculate_statistics(data: Any) -> Dict[str, Any]:
        """
        Calcula estatísticas para dados JSON.
        
        Args:
            data: Dados JSON (dict, list, ou primitivo)
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "total_keys": 0,
            "unique_keys": set(),
            "max_depth": 0,
            "size_bytes": 0,
            "value_types": {
                "string": 0,
                "number": 0,
                "boolean": 0,
                "null": 0,
                "array": 0,
                "object": 0
            },
            "duplicate_keys": 0
        }
        
        # Calcula tamanho em bytes
        try:
            stats["size_bytes"] = len(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except Exception:
            stats["size_bytes"] = 0
        
        # Analisa estrutura recursivamente
        StatisticsManager._analyze_recursive(data, stats, depth=1)
        
        # Converte set para count
        unique_count = len(stats["unique_keys"])
        stats["duplicate_keys"] = stats["total_keys"] - unique_count
        stats["unique_keys"] = unique_count
        
        return stats
    
    @staticmethod
    def _analyze_recursive(data: Any, stats: Dict[str, Any], depth: int, seen_keys: set = None):
        """
        Analisa dados recursivamente.
        
        Args:
            data: Dados a analisar
            stats: Dicionário de estatísticas (modificado in-place)
            depth: Profundidade atual
            seen_keys: Set de chaves já vistas (para duplicates)
        """
        if seen_keys is None:
            seen_keys = set()
        
        # Atualiza profundidade máxima
        if depth > stats["max_depth"]:
            stats["max_depth"] = depth
        
        if isinstance(data, dict):
            stats["value_types"]["object"] += 1
            
            for key, value in data.items():
                stats["total_keys"] += 1
                stats["unique_keys"].add(key)
                
                # Analisa valor recursivamente
                StatisticsManager._analyze_recursive(value, stats, depth + 1, seen_keys)
        
        elif isinstance(data, list):
            stats["value_types"]["array"] += 1
            
            for item in data:
                StatisticsManager._analyze_recursive(item, stats, depth + 1, seen_keys)
        
        elif isinstance(data, str):
            stats["value_types"]["string"] += 1
        
        elif isinstance(data, bool):
            stats["value_types"]["boolean"] += 1
        
        elif isinstance(data, (int, float)):
            stats["value_types"]["number"] += 1
        
        elif data is None:
            stats["value_types"]["null"] += 1
    
    @staticmethod
    def calculate_overlap_percentage(file1_stats: Dict[str, Any], file2_stats: Dict[str, Any], result_count: int) -> float:
        """
        Calcula percentual de overlap entre dois arquivos.
        
        Args:
            file1_stats: Estatísticas do arquivo 1
            file2_stats: Estatísticas do arquivo 2
            result_count: Número de elementos no resultado da operação
        
        Returns:
            Percentual de overlap (0-100)
        """
        total_keys = file1_stats["total_keys"] + file2_stats["total_keys"]
        
        if total_keys == 0:
            return 0.0
        
        # Overlap é baseado no resultado da interseção
        overlap = (result_count / total_keys) * 100
        
        return min(100.0, max(0.0, overlap))
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Formata tamanho em bytes para string legível.
        
        Args:
            size_bytes: Tamanho em bytes
        
        Returns:
            String formatada (ex: "1.5 KB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    @staticmethod
    def format_statistics_text(stats: Dict[str, Any], label: str = "Statistics") -> str:
        """
        Formata estatísticas para exibição em texto.
        
        Args:
            stats: Dicionário de estatísticas
            label: Label descritivo
        
        Returns:
            String formatada multi-linha
        """
        size_str = StatisticsManager.format_size(stats["size_bytes"])
        
        text = f"""=== {label} ===
Total Keys: {stats['total_keys']}
Unique Keys: {stats['unique_keys']}
Duplicate Keys: {stats['duplicate_keys']}
Max Depth: {stats['max_depth']}
Size: {size_str}

Value Types:
  • Strings: {stats['value_types']['string']}
  • Numbers: {stats['value_types']['number']}
  • Booleans: {stats['value_types']['boolean']}
  • Nulls: {stats['value_types']['null']}
  • Arrays: {stats['value_types']['array']}
  • Objects: {stats['value_types']['object']}"""
        
        return text
    
    @staticmethod
    def format_comparative_statistics(
        file1_stats: Dict[str, Any],
        file2_stats: Dict[str, Any],
        result_stats: Dict[str, Any],
        overlap_pct: float
    ) -> str:
        """
        Formata estatísticas comparativas para 3 datasets.
        
        Args:
            file1_stats: Stats do arquivo 1
            file2_stats: Stats do arquivo 2
            result_stats: Stats do resultado
            overlap_pct: Percentual de overlap
        
        Returns:
            String formatada com comparação lado-a-lado
        """
        text = f"""📊 COMPARATIVE STATISTICS

Overlap: {overlap_pct:.1f}%

                    File A      File B      Result
─────────────────────────────────────────────────────
Total Keys:         {file1_stats['total_keys']:<11} {file2_stats['total_keys']:<11} {result_stats['total_keys']}
Unique Keys:        {file1_stats['unique_keys']:<11} {file2_stats['unique_keys']:<11} {result_stats['unique_keys']}
Duplicate Keys:     {file1_stats['duplicate_keys']:<11} {file2_stats['duplicate_keys']:<11} {result_stats['duplicate_keys']}
Max Depth:          {file1_stats['max_depth']:<11} {file2_stats['max_depth']:<11} {result_stats['max_depth']}
Size:               {StatisticsManager.format_size(file1_stats['size_bytes']):<11} {StatisticsManager.format_size(file2_stats['size_bytes']):<11} {StatisticsManager.format_size(result_stats['size_bytes'])}

Value Types Distribution:
  Strings:          {file1_stats['value_types']['string']:<11} {file2_stats['value_types']['string']:<11} {result_stats['value_types']['string']}
  Numbers:          {file1_stats['value_types']['number']:<11} {file2_stats['value_types']['number']:<11} {result_stats['value_types']['number']}
  Booleans:         {file1_stats['value_types']['boolean']:<11} {file2_stats['value_types']['boolean']:<11} {result_stats['value_types']['boolean']}
  Nulls:            {file1_stats['value_types']['null']:<11} {file2_stats['value_types']['null']:<11} {result_stats['value_types']['null']}
  Arrays:           {file1_stats['value_types']['array']:<11} {file2_stats['value_types']['array']:<11} {result_stats['value_types']['array']}
  Objects:          {file1_stats['value_types']['object']:<11} {file2_stats['value_types']['object']:<11} {result_stats['value_types']['object']}"""
        
        return text
