#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translation module for Clarify.

Provides translation services using various providers.
"""

from .google_translate import GoogleTranslateAPI
from .notebook_translation import (
    NotebookFormatError,
    load_notebook,
    markdown_cell_count,
    notebook_markdown_text,
    save_notebook,
    translate_markdown_cells,
)
from .pdf_translation import PdfExtractionError, PdfTextExtraction, extract_pdf_text

__all__ = [
    'GoogleTranslateAPI',
    'NotebookFormatError',
    'load_notebook',
    'markdown_cell_count',
    'notebook_markdown_text',
    'save_notebook',
    'translate_markdown_cells',
    'PdfExtractionError',
    'PdfTextExtraction',
    'extract_pdf_text',
]
