Overview
========

What is Clarify?
----------------

**Clarify** is a comprehensive text processing and JSON manipulation system designed for developers, data engineers, and power users who work with large volumes of text and JSON files.

Key Capabilities
----------------

Core Operations
~~~~~~~~~~~~~~~

* **Search & Replace**: Advanced pattern matching with case-sensitive, whole-word, and regex support
* **Batch Processing**: Process thousands of files with filtering by extension, size, date, and content
* **JSON Manipulation**: Deduplicate, format, normalize, and validate JSON files
* **TypeScript Support**: Parse and process TypeScript/JavaScript object literals

Advanced Features
~~~~~~~~~~~~~~~~~

* **Set Operations**: Compare multiple files with intersection (∩), union (∪), difference (−), and symmetric difference (⊕)
* **AI Integration**: Process files with OpenAI GPT-4o, Google Gemini, Anthropic Claude, and Perplexity
* **i18n Support**: Built-in translation system with 7 languages (English, Portuguese, Spanish, French, German, Chinese, Japanese)
* **JSX Extraction**: Intelligently extract text from React/JSX components for i18n workflows

Architecture Principles
-----------------------

Modularity
~~~~~~~~~~

Clarify follows a modular architecture where each feature is independent:

* **Base Classes**: Reusable ``BaseProcessor`` and ``BaseDock`` reduce code duplication by 40-60%
* **Plugin-Ready**: Architecture supports future plugin system
* **Separation of Concerns**: GUI, CLI, and core logic are decoupled

Performance
~~~~~~~~~~~

* **Threading**: Background processing with configurable thread pools
* **Chunked Processing**: Handle files >100 MB by processing in chunks
* **Caching**: Intelligent caching for repeated operations
* **Memory Efficient**: Stream-based processing for large datasets

Benchmarks (i5-8250U, 16GB RAM, SSD):

+-------------------+-------------+
| Operation         | Speed       |
+===================+=============+
| JSON Parsing      | 80 MB/s     |
+-------------------+-------------+
| Search            | 5.2M items/s|
+-------------------+-------------+
| Replace           | 2.8M items/s|
+-------------------+-------------+
| Dedupe (10K keys) | 450ms       |
+-------------------+-------------+

Use Cases
---------

Development Workflows
~~~~~~~~~~~~~~~~~~~~~

1. **Refactoring**: Bulk rename variables across hundreds of files with regex
2. **i18n Migration**: Extract hardcoded strings from JSX, generate translation files, replace with ``{t.key}``
3. **Config Management**: Merge, compare, and sync configuration files across environments
4. **Code Generation**: Use AI to transform boilerplate code (e.g., class → functional component)

Data Engineering
~~~~~~~~~~~~~~~~

1. **JSON Cleaning**: Deduplicate keys, remove nulls, standardize format
2. **Data Validation**: Search for patterns, validate against schemas
3. **ETL Pipelines**: Transform JSON between different structures
4. **Log Analysis**: Extract patterns from log files with regex

API Design Philosophy
---------------------

Public vs Private
~~~~~~~~~~~~~~~~~

* **Public API**: Functions/classes without leading underscore, documented with docstrings
* **Private API**: Internal implementation details (``_function``), subject to change
* **Stable Interfaces**: Core modules (``core/``, ``rewriter/``, ``utils/``) have stable APIs

Example:

.. code-block:: python

   from src.core.search_replace import search_files  # Public API
   from src.rewriter.rewriter import JSONRewriter     # Public API
   
   # Search for pattern in directory
   results = search_files(
       directory="/path/to/files",
       pattern="TODO",
       regex=False,
       case_sensitive=True,
       extensions=[".py", ".js"]
   )
   
   # Deduplicate JSON
   rewriter = JSONRewriter()
   clean_data = rewriter.deduplicate(json_data)

Type Hints
~~~~~~~~~~

Clarify uses Python 3.12+ type hints extensively:

.. code-block:: python

   def search_files(
       directory: str,
       pattern: str,
       *,
       regex: bool = False,
       case_sensitive: bool = True,
       extensions: list[str] | None = None
   ) -> list[dict[str, Any]]:
       """Search for pattern in files.
       
       Args:
           directory: Root directory to search
           pattern: Search pattern (literal or regex)
           regex: Whether pattern is regex
           case_sensitive: Whether search is case-sensitive
           extensions: File extensions to include (e.g., [".py", ".js"])
           
       Returns:
           List of dicts with keys: file, line_number, line_content, match
       """
       ...

Error Handling
~~~~~~~~~~~~~~

* **Exceptions**: Raise descriptive exceptions for error conditions
* **Logging**: Comprehensive logging at DEBUG, INFO, WARNING, ERROR levels
* **User Feedback**: GUI provides clear error messages with actionable suggestions

Next Steps
----------

* :doc:`quickstart` - Build your first Clarify script
* :doc:`core` - Core search and replace operations
* :doc:`rewriter` - JSON manipulation
* :doc:`gui` - Build custom GUI extensions
