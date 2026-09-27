"""Bounded, read-only information structure analyzers."""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
import re
import sqlite3
from pathlib import Path
from typing import Any, Iterable


MAX_ITEMS = 50_000
MAX_SOURCE_CHARS = 2_000_000
MAX_DATABASE_BYTES = 100 * 1024 * 1024
_WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ][\wÀ-ÖØ-öø-ÿ'-]{2,}", re.UNICODE)
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
_STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "entre", "esse", "esta", "este", "foi", "mais", "na", "nas",
    "no", "nos", "o", "os", "ou", "para", "por", "que", "se", "sem", "sua",
    "um", "uma", "the", "and", "for", "from", "into", "that", "this", "with",
}


class StructureLimitError(ValueError):
    """Raised when an input exceeds a documented safety boundary."""


def _bounded_text(text: str) -> str:
    if len(text) > MAX_SOURCE_CHARS:
        raise StructureLimitError(f"Input exceeds {MAX_SOURCE_CHARS:,} characters")
    return text


def folder_map_from_paths(root: str | Path, paths: Iterable[str | Path]) -> dict[str, Any]:
    """Build a folder tree from previously collected paths without scanning disk."""
    root_path = Path(root).expanduser().resolve(strict=False)
    tree: dict[str, Any] = {"name": root_path.name or str(root_path), "kind": "directory", "children": {}}
    accepted = 0
    skipped = 0
    for index, raw_path in enumerate(paths):
        if index >= MAX_ITEMS:
            raise StructureLimitError(f"Path list exceeds {MAX_ITEMS:,} items")
        candidate = Path(raw_path).expanduser().resolve(strict=False)
        try:
            parts = candidate.relative_to(root_path).parts
        except ValueError:
            skipped += 1
            continue
        if not parts:
            continue
        current = tree
        for position, part in enumerate(parts):
            children = current["children"]
            kind = "file" if position == len(parts) - 1 else "directory"
            current = children.setdefault(part, {"name": part, "kind": kind, "children": {}})
        accepted += 1

    def normalize(node: dict[str, Any]) -> dict[str, Any]:
        children = node.pop("children")
        if children:
            node["children"] = [normalize(children[name]) for name in sorted(children, key=str.casefold)]
        return node

    return {
        "type": "folder_map",
        "source": "existing_file_explorer_results",
        "root": str(root_path),
        "accepted_paths": accepted,
        "skipped_outside_root": skipped,
        "tree": normalize(tree),
    }


def sqlite_schema_graph(database_path: str | Path) -> dict[str, Any]:
    """Read a SQLite schema using a read-only connection and return nodes and edges."""
    path = Path(database_path).expanduser().resolve(strict=True)
    if path.suffix.lower() not in {".db", ".sqlite", ".sqlite3"}:
        raise ValueError("Expected a .db, .sqlite, or .sqlite3 file")
    if path.stat().st_size > MAX_DATABASE_BYTES:
        raise StructureLimitError(f"Database exceeds {MAX_DATABASE_BYTES // (1024 * 1024)} MiB")

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
        table_rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        if len(table_rows) > 1_000:
            raise StructureLimitError("Database contains more than 1,000 tables")
        for (table_name,) in table_rows:
            table_id = f"table:{table_name}"
            nodes.append({"id": table_id, "kind": "table", "label": table_name})
            quoted = table_name.replace('"', '""')
            for column in connection.execute(f'PRAGMA table_info("{quoted}")'):
                column_id = f"{table_id}.{column[1]}"
                nodes.append({
                    "id": column_id,
                    "kind": "column",
                    "label": column[1],
                    "data_type": column[2] or None,
                    "primary_key": bool(column[5]),
                })
                edges.append({"source": table_id, "target": column_id, "kind": "contains"})
            for foreign_key in connection.execute(f'PRAGMA foreign_key_list("{quoted}")'):
                edges.append({
                    "source": f"{table_id}.{foreign_key[3]}",
                    "target": f"table:{foreign_key[2]}.{foreign_key[4]}",
                    "kind": "foreign_key",
                })
    return {"type": "sqlite_schema_graph", "database": str(path), "nodes": nodes, "edges": edges}


class _PythonGraphVisitor(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.nodes: list[dict[str, Any]] = [
            {"id": module_name, "kind": "module", "label": module_name, "line": 1}
        ]
        self.edges: list[dict[str, str]] = []
        self.scope = [module_name]
        self.class_depth = 0
        self.complexity: Counter[str] = Counter()

    @property
    def current(self) -> str:
        return self.scope[-1]

    def _visit_definition(self, node: ast.AST, name: str, kind: str) -> None:
        identifier = f"{self.current}.{name}"
        self.nodes.append({"id": identifier, "kind": kind, "label": name, "line": node.lineno})
        self.edges.append({"source": self.current, "target": identifier, "kind": "contains"})
        self.scope.append(identifier)
        self.generic_visit(node)
        self.scope.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_depth += 1
        self._visit_definition(node, node.name, "class")
        self.class_depth -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_definition(node, node.name, "method" if self.class_depth else "function")

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            target = f"import:{alias.name}"
            self.nodes.append({"id": target, "kind": "import", "label": alias.name, "line": node.lineno})
            self.edges.append({"source": self.current, "target": target, "kind": "imports"})

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            name = f"{module}.{alias.name}".strip(".")
            target = f"import:{name}"
            self.nodes.append({"id": target, "kind": "import", "label": name, "line": node.lineno})
            self.edges.append({"source": self.current, "target": target, "kind": "imports"})

    def visit_Call(self, node: ast.Call) -> None:
        try:
            called = ast.unparse(node.func)
        except Exception:  # pragma: no cover - defensive for unusual ASTs
            called = "<unknown>"
        self.edges.append({"source": self.current, "target": f"call:{called}", "kind": "calls"})
        self.complexity[self.current] += 1
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.BoolOp)):
            self.complexity[self.current] += 1
        super().generic_visit(node)


def python_context_graph(source: str, module_name: str = "module") -> dict[str, Any]:
    """Parse Python with its grammar and map containment, imports, calls, and complexity."""
    source = _bounded_text(source)
    visitor = _PythonGraphVisitor(module_name.strip() or "module")
    visitor.visit(ast.parse(source))
    deduplicated_nodes = {node["id"]: node for node in visitor.nodes}
    for edge in visitor.edges:
        if edge["target"].startswith("call:"):
            name = edge["target"].removeprefix("call:")
            deduplicated_nodes.setdefault(
                edge["target"], {"id": edge["target"], "kind": "call_target", "label": name}
            )
    return {
        "type": "python_context_graph",
        "module": visitor.module_name,
        "nodes": list(deduplicated_nodes.values()),
        "edges": visitor.edges,
        "function_metrics": [
            {"id": identifier, "decision_and_call_count": count}
            for identifier, count in sorted(visitor.complexity.items())
        ],
    }


def text_complexity_metrics(text: str) -> dict[str, Any]:
    text = _bounded_text(text)
    words = _WORD_RE.findall(text.lower())
    sentences = [item for item in re.split(r"[.!?]+", text) if item.strip()]
    paragraphs = [item for item in re.split(r"\n\s*\n", text) if item.strip()]
    return {
        "words": len(words),
        "unique_words": len(set(words)),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "average_sentence_words": round(len(words) / max(1, len(sentences)), 2),
        "lexical_diversity": round(len(set(words)) / max(1, len(words)), 4),
    }


def organize_text_hierarchy(text: str, max_groups: int = 12) -> dict[str, Any]:
    """Group loose paragraphs by repeated keywords while preserving original text."""
    text = _bounded_text(text)
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    if len(paragraphs) > 10_000:
        raise StructureLimitError("Input contains more than 10,000 paragraphs")
    tokens = [
        [word.lower() for word in _WORD_RE.findall(paragraph) if word.lower() not in _STOPWORDS]
        for paragraph in paragraphs
    ]
    document_frequency = Counter(word for words in tokens for word in set(words))
    keywords = [word for word, frequency in document_frequency.most_common(max_groups) if frequency > 1]
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, (paragraph, words) in enumerate(zip(paragraphs, tokens), start=1):
        word_counts = Counter(words)
        keyword = max(keywords, key=lambda item: (word_counts[item], document_frequency[item]), default="ungrouped")
        if not word_counts[keyword]:
            keyword = "ungrouped"
        groups[keyword].append({"original_position": index, "text": paragraph})
    def subgroups(items: list[dict[str, Any]], excluded: set[str], depth: int) -> list[dict[str, Any]]:
        if depth >= 3 or len(items) < 3:
            return []
        item_tokens = [
            [word.lower() for word in _WORD_RE.findall(item["text"]) if word.lower() not in _STOPWORDS]
            for item in items
        ]
        frequencies = Counter(word for words in item_tokens for word in set(words) if word not in excluded)
        candidates = [word for word, count in frequencies.most_common(max_groups) if count > 1]
        if not candidates:
            return []
        nested: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for item, words in zip(items, item_tokens):
            counts = Counter(words)
            keyword = max(candidates, key=lambda word: (counts[word], frequencies[word]), default="other")
            nested[keyword if counts[keyword] else "other"].append(item)
        if len(nested) == 1:
            return []
        return [
            {
                "title_suggestion": name.title(),
                "paragraphs": nested[name],
                "subgroups": subgroups(nested[name], excluded | {name}, depth + 1),
            }
            for name in sorted(nested)
        ]

    structured_groups = []
    for name in sorted(groups):
        structured_groups.append({
            "title_suggestion": name.title(),
            "paragraphs": groups[name],
            "subgroups": subgroups(groups[name], {name}, 1),
        })
    return {
        "type": "text_hierarchy_suggestion",
        "method": "repeated_keyword_document_frequency",
        "metrics": text_complexity_metrics(text),
        "groups": structured_groups,
    }


def scientific_reference_graph(articles: dict[str, str]) -> dict[str, Any]:
    """Link articles to DOI references so shared ancestors are directly visible."""
    if len(articles) > 1_000:
        raise StructureLimitError("Input contains more than 1,000 articles")
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []
    doi_usage: Counter[str] = Counter()
    for article_name, text in articles.items():
        _bounded_text(text)
        article_id = f"article:{article_name}"
        nodes[article_id] = {"id": article_id, "kind": "article", "label": article_name}
        for doi in sorted({match.rstrip(".,;)").lower() for match in _DOI_RE.findall(text)}):
            doi_id = f"doi:{doi}"
            nodes[doi_id] = {"id": doi_id, "kind": "reference", "label": doi}
            edges.append({"source": article_id, "target": doi_id, "kind": "references"})
            doi_usage[doi] += 1
    article_dois = {
        name: {match.rstrip(".,;)").lower() for match in _DOI_RE.findall(text)}
        for name, text in articles.items()
    }
    combinations = []
    article_names = sorted(articles)
    for index, first in enumerate(article_names):
        for second in article_names[index + 1:]:
            shared = sorted(article_dois[first] & article_dois[second])
            if shared:
                combinations.append({"articles": [first, second], "shared_ancestors": shared})
    return {
        "type": "scientific_reference_graph",
        "nodes": list(nodes.values()),
        "edges": edges,
        "shared_ancestors": [doi for doi, count in doi_usage.items() if count > 1],
        "reading_order_suggestion": sorted(articles, key=lambda name: (len(set(_DOI_RE.findall(articles[name]))), name)),
        "suggested_combinations": combinations,
    }


def document_visual_structures(data: Any) -> dict[str, Any]:
    """Represent nested data as paths, inclusion edges, level counts, and numbering."""
    paths: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    levels: Counter[int] = Counter()

    def walk(value: Any, path: tuple[str, ...], number: tuple[int, ...]) -> None:
        if len(paths) >= MAX_ITEMS:
            raise StructureLimitError(f"Document exceeds {MAX_ITEMS:,} nodes")
        node_id = "/".join(path) or "$"
        paths.append({"id": node_id, "path": list(path), "number": ".".join(map(str, number)) or "0", "level": len(path)})
        levels[len(path)] += 1
        if isinstance(value, dict):
            children = list(value.items())
        elif isinstance(value, list):
            children = [(str(index), item) for index, item in enumerate(value)]
        else:
            paths[-1]["value"] = value
            return
        for index, (name, child) in enumerate(children, start=1):
            child_path = (*path, str(name))
            child_id = "/".join(child_path)
            edges.append({"source": node_id, "target": child_id, "kind": "includes"})
            walk(child, child_path, (*number, index))

    walk(data, (), ())
    return {
        "type": "document_visual_structures",
        "hierarchy": data,
        "numbered_nodes": paths,
        "inclusion_edges": edges,
        "bar_counts_by_level": [{"level": level, "nodes": count} for level, count in sorted(levels.items())],
    }
