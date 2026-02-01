#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Syntax Highlighter Widget - Multi-language syntax highlighting

Extracted from editor_dock.py (v2.9.114 - Phase 2.5.1)
Provides syntax highlighting for multiple file types.

Supported Languages:
- HTML/JSX/TSX: tags, attributes, strings, comments
- JSON: keys, values, numbers, brackets, booleans
- Python: keywords, strings, comments, numbers
- JavaScript/TypeScript: keywords, strings, comments, numbers

Pattern: Strategy (GoF) - Different highlighting strategies per file type
"""

from __future__ import annotations

from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class SyntaxHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for different file types.

    Supports:
    - HTML/JSX/TSX: tags, attributes, strings
    - JSON: keys, values, brackets
    - Python: keywords, strings, comments
    - JavaScript/TypeScript: keywords, strings, comments
    """

    def __init__(self, document, file_type: str = "txt"):
        """
        Initialize syntax highlighter.

        Args:
            document: QTextDocument to highlight
            file_type: File extension (html, json, py, js, ts, tsx, jsx, etc.)
        """
        super().__init__(document)
        self.file_type = file_type.lower()
        self._setup_formats()
        self._setup_rules()

    def _setup_formats(self):
        """Setup text formats for different syntax elements."""
        # HTML/JSX/TSX tags
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(QColor("#569CD6"))  # Blue
        self.tag_format.setFontWeight(QFont.Bold)

        # HTML attributes
        self.attr_format = QTextCharFormat()
        self.attr_format.setForeground(QColor("#9CDCFE"))  # Light blue

        # Strings
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#CE9178"))  # Orange

        # Keywords (Python, JS, TS)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#C586C0"))  # Purple
        self.keyword_format.setFontWeight(QFont.Bold)

        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6A9955"))  # Green
        self.comment_format.setFontItalic(True)

        # JSON keys
        self.json_key_format = QTextCharFormat()
        self.json_key_format.setForeground(QColor("#9CDCFE"))  # Light blue

        # Numbers
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#B5CEA8"))  # Light green

        # Brackets/Braces
        self.bracket_format = QTextCharFormat()
        self.bracket_format.setForeground(QColor("#FFD700"))  # Gold
        self.bracket_format.setFontWeight(QFont.Bold)

    def _setup_rules(self):
        """Setup highlighting rules based on file type."""
        self.rules = []

        if self.file_type in ["html", "htm", "jsx", "tsx"]:
            # HTML/JSX tags: <tagname> </tagname>
            self.rules.append((QRegularExpression(r"</?[\w-]+"), self.tag_format))
            self.rules.append((QRegularExpression(r"/?>"), self.tag_format))

            # Attributes: attribute="value"
            self.rules.append((QRegularExpression(r"\b[\w-]+(?==)"), self.attr_format))

            # Strings: "..." or '...'
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))

            # Comments: <!-- ... -->
            self.rules.append((QRegularExpression(r"<!--.*?-->"), self.comment_format))

        elif self.file_type == "json":
            # JSON keys: "key":
            self.rules.append((QRegularExpression(r'"[\w\s.-]+"(?=\s*:)'), self.json_key_format))

            # Strings: "value"
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))

            # Numbers
            self.rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), self.number_format))

            # Brackets/Braces: {}, []
            self.rules.append((QRegularExpression(r'[{}\[\]]'), self.bracket_format))

            # Booleans and null
            self.rules.append((QRegularExpression(r'\b(true|false|null)\b'), self.keyword_format))

        elif self.file_type in ["py", "python"]:
            # Python keywords
            keywords = [
                "def", "class", "if", "elif", "else", "for", "while", "try", "except",
                "finally", "with", "as", "import", "from", "return", "yield", "lambda",
                "pass", "break", "continue", "raise", "assert", "del", "global", "nonlocal",
                "True", "False", "None", "and", "or", "not", "in", "is"
            ]
            for keyword in keywords:
                pattern = QRegularExpression(rf'\b{keyword}\b')
                self.rules.append((pattern, self.keyword_format))

            # Strings: "...", '...', """...""", '''...'''
            self.rules.append((QRegularExpression(r'""".*?"""'), self.string_format))
            self.rules.append((QRegularExpression(r"'''.*?'''"), self.string_format))
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))

            # Comments: # ...
            self.rules.append((QRegularExpression(r'#[^\n]*'), self.comment_format))

            # Numbers
            self.rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), self.number_format))

        elif self.file_type in ["js", "ts", "javascript", "typescript"]:
            # JavaScript/TypeScript keywords
            keywords = [
                "const", "let", "var", "function", "if", "else", "for", "while", "do",
                "switch", "case", "break", "continue", "return", "try", "catch", "finally",
                "throw", "new", "this", "class", "extends", "import", "export", "from",
                "default", "async", "await", "yield", "typeof", "instanceof", "void",
                "true", "false", "null", "undefined"
            ]
            for keyword in keywords:
                pattern = QRegularExpression(rf'\b{keyword}\b')
                self.rules.append((pattern, self.keyword_format))

            # Strings: "...", '...', `...`
            self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format))
            self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.string_format))
            self.rules.append((QRegularExpression(r'`[^`]*`'), self.string_format))

            # Comments: // ... or /* ... */
            self.rules.append((QRegularExpression(r'//[^\n]*'), self.comment_format))
            self.rules.append((QRegularExpression(r'/\*.*?\*/'), self.comment_format))

            # Numbers
            self.rules.append((QRegularExpression(r'\b\d+\.?\d*\b'), self.number_format))

    def highlightBlock(self, text: str):
        """
        Apply syntax highlighting to a block of text.

        Args:
            text: Text block to highlight
        """
        for pattern, format in self.rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


__all__ = ['SyntaxHighlighter']
