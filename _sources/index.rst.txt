Clarify API Documentation
==========================

Welcome to **Clarify's** API documentation! This documentation covers the public API for developers who want to understand, extend, or integrate with Clarify programmatically.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   quickstart
   core
   rewriter
   translators
   extractors
   gui
   utils
   cli

Overview
--------

**Clarify** is an advanced text processing and JSON manipulation system with a modern GUI and powerful CLI. It provides 10+ specialized tools for file operations.

**Key Features:**

* 🔍 **Search & Replace**: Advanced pattern matching with regex support
* 📝 **JSON Rewriter**: Deduplication, formatting, normalization
* 🔤 **Case Converter**: Convert between camelCase, PascalCase, snake_case, kebab-case
* 🔎 **JSON Search**: Deep search in JSON/TypeScript files
* 🎯 **JSX Extractor**: Extract parameters from React/JSX files
* 🤖 **AI Processor**: Integration with OpenAI, Gemini, Claude, Perplexity
* 🌐 **JSON Translator**: Bidirectional translation with dictionaries
* 🔄 **Placeholder Replacer**: Batch placeholder substitution
* 🔧 **Set Operations**: Compare and merge files (∩∪−⊕)

Architecture
------------

Clarify follows a modular architecture with clear separation of concerns:

.. code-block:: text

   clarify/
   ├── src/
   │   ├── core/          # Core functionality (search, insert, filters)
   │   ├── rewriter/      # JSON rewriting operations
   │   ├── translators/   # Translation systems
   │   ├── extractors/    # Text/JSX extraction
   │   ├── gui/           # GUI components (PySide6)
   │   ├── utils/         # Utilities (file, text, TypeScript)
   │   └── cli/           # Command-line interfaces

Quick Links
-----------

* :doc:`quickstart` - Get started with Clarify API
* :doc:`core` - Core search, replace, and insert operations
* :doc:`rewriter` - JSON rewriting and manipulation
* :doc:`gui` - GUI components and docks
* `GitHub Repository <https://github.com/JosueAmaral15/clarify>`_
* `User Manual <../wiki/README.md>`_

Installation for Development
-----------------------------

.. code-block:: bash

   git clone https://github.com/JosueAmaral15/clarify.git
   cd clarify
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   pip install -r requirements-docs.txt  # For building docs

Building Documentation
----------------------

.. code-block:: bash

   cd docs/api
   make html  # Linux/macOS
   make.bat html  # Windows
   
   # Open in browser
   open _build/html/index.html  # macOS
   xdg-open _build/html/index.html  # Linux
   start _build/html/index.html  # Windows

Contributing
------------

See the `Contributing Guide <../../CONTRIBUTING.md>`_ for guidelines on:

* Code style (black, isort, pylint >9.0)
* Testing requirements (coverage >90%)
* Pull request process
* i18n contributions (7 languages)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
