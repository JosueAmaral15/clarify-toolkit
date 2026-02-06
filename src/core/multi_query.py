#!/usr/bin/env python3
"""
multi_query.py

Suporte para buscas com múltiplas queries (uma por linha).
Cada linha representa uma query independente que pode usar regex.
"""
import re
from typing import List, Tuple, Pattern
from dataclasses import dataclass


@dataclass
class QueryLine:
    """Representa uma linha de query"""
    raw_text: str
    pattern: Pattern
    line_number: int  # Original line number (1-based)


class MultiQueryProcessor:
    """
    Processa múltiplas queries separadas por linha.

    Cada linha não-vazia é tratada como uma query independente.
    Lines starting with # are ignored (comments).
    """

    def __init__(self,
                 multi_line_text: str,
                 case_sensitive: bool = False,
                 whole_word: bool = False,
                 use_regex: bool = True):
        """
        Args:
            multi_line_text: Texto com múltiplas queries (uma por linha)
            case_sensitive: Se deve ser case-sensitive
            whole_word: Se deve fazer match de palavra inteira
            use_regex: Se queries devem ser tratadas como regex
        """
        self.multi_line_text = multi_line_text
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        self.use_regex = use_regex
        self.queries: List[QueryLine] = []

        self._parse_queries()

    def _parse_queries(self):
        """Parse o texto multi-linha em queries individuais"""
        lines = self.multi_line_text.split('\n')

        for i, line in enumerate(lines, start=1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            try:
                pattern = self._compile_pattern(line)
                self.queries.append(QueryLine(
                    raw_text=line,
                    pattern=pattern,
                    line_number=i
                ))
            except re.error:  # Regex error - treat as literal text
                # If regex compilation fails, treat as literal text
                escaped = re.escape(line)
                pattern = self._compile_pattern(escaped)
                self.queries.append(QueryLine(
                    raw_text=line,
                    pattern=pattern,
                    line_number=i
                ))

    def _compile_pattern(self, text: str) -> Pattern:
        """Compila uma query em pattern regex"""
        if not self.use_regex:
            # Escape special chars if not using regex
            text = re.escape(text)

        if self.whole_word:
            # Add word boundaries
            text = rf'\b{text}\b'

        flags = 0 if self.case_sensitive else re.IGNORECASE

        return re.compile(text, flags)

    def search_in_text(self, content: str) -> List[Tuple[int, int, str, int]]:
        """
        Busca todas as queries no conteúdo.

        Args:
            content: Texto onde buscar

        Returns:
            Lista de tuplas (line, col, snippet, query_line_number)
            onde query_line_number indica qual query fez o match
        """
        matches = []

        for query in self.queries:
            for match in query.pattern.finditer(content):
                line = content.count("\n", 0, match.start()) + 1
                col = match.start() - (content.rfind("\n", 0, match.start()) + 1)

                # Get snippet (linha inteira do match)
                lines = content.splitlines()
                snippet = lines[line - 1] if line - 1 < len(lines) else ""

                matches.append((line, col, snippet, query.line_number))

        return matches

    def get_query_count(self) -> int:
        """Retorna número de queries válidas"""
        return len(self.queries)

    def get_query_summary(self) -> str:
        """Retorna resumo das queries para display"""
        if not self.queries:
            return "No queries"

        if len(self.queries) == 1:
            return f"1 query: {self.queries[0].raw_text[:50]}"

        return f"{len(self.queries)} queries"

    def validate(self) -> Tuple[bool, str]:
        """
        Valida as queries.

        Returns:
            (is_valid, error_message)
        """
        if not self.queries:
            return False, "No valid queries found"

        # Check for very complex patterns that might be slow
        for query in self.queries:
            if len(query.raw_text) > 500:
                return False, f"Query on line {query.line_number} is too long (>500 chars)"

        return True, ""


def split_multi_query(text: str) -> List[str]:
    """
    Utilitário para dividir texto multi-linha em queries individuais.
    Remove linhas vazias e comentários.
    """
    lines = text.split('\n')
    queries = []

    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            queries.append(line)

    return queries


def combine_query_results(results_by_query: List[List[Tuple]]) -> List[Tuple]:
    """
    Combina resultados de múltiplas queries, removendo duplicatas.

    Args:
        results_by_query: Lista de listas de resultados (cada inner list é de uma query)

    Returns:
        Lista combinada sem duplicatas, ordenada por (line, col)
    """
    all_matches = []
    seen = set()

    for results in results_by_query:
        for match in results:
            # Use (line, col) as unique key
            key = (match[0], match[1])
            if key not in seen:
                seen.add(key)
                all_matches.append(match)

    # Sort by line, then column
    all_matches.sort(key=lambda x: (x[0], x[1]))

    return all_matches
