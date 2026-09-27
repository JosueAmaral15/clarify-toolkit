Quickstart
==========

This guide shows how to use Clarify's API programmatically in your Python scripts.

Installation
------------

.. code-block:: bash

   git clone https://github.com/JosueAmaral15/clarify.git
   cd clarify
   python3 -m venv venv
   source venv/bin/activate
   python -m pip install -e .

Basic Examples
--------------

Search Files
~~~~~~~~~~~~

Search for a pattern across multiple files:

.. code-block:: python

   from src.core import SearchOptions
   from src.utils import read_text, walk_files

   # Find all TODOs in Python files
   pattern = SearchOptions(case_sensitive=True).compile("TODO")
   files = walk_files("/path/to/project", include_globs=["*.py"])

   for file_path in files:
       text = read_text(file_path)
       for match in pattern.finditer(text):
           line = text.count("\n", 0, match.start()) + 1
           print(f"{file_path}:{line}")

Replace Text
~~~~~~~~~~~~

Replace text with preview and backup:

.. code-block:: python

   from src.core import SearchOptions, replace_in_text
   from src.utils import read_text, walk_files, write_text

   # Replace old API calls with new ones
   pattern = SearchOptions(regex=False).compile("old_function(")
   changed = 0

   for file_path in walk_files("/path/to/project", include_globs=["*.py", "*.js"]):
       old = read_text(file_path)
       new, count = replace_in_text(old, pattern, "new_function(")
       if count:
           write_text(file_path, new)
           changed += 1

   print(f"Replaced in {changed} files")

Deduplicate JSON
~~~~~~~~~~~~~~~~

Clean a JSON file by removing duplicate keys:

.. code-block:: python

   import json
   from pathlib import Path

   from src.rewriter import (
       Obj,
       dedupe,
       parse_json_preserving_duplicates_text,
   )

   def to_plain(node):
       if isinstance(node, Obj):
           return {key: to_plain(value) for key, value in node}
       if isinstance(node, list):
           return [to_plain(value) for value in node]
       return node

   raw = Path("config.json").read_text(encoding="utf-8")
   data = parse_json_preserving_duplicates_text(raw)
   clean_data = dedupe(data)
   Path("config_clean.json").write_text(
       json.dumps(to_plain(clean_data), ensure_ascii=False, indent=2) + "\n",
       encoding="utf-8",
   )

Set Operations
~~~~~~~~~~~~~~

Compare two JSON files to find differences:

.. code-block:: python

   import json
   from src.set_operations import difference

   # Load files
   with open("config_prod.json") as f:
       prod = json.load(f)

   with open("config_dev.json") as f:
       dev = json.load(f)

   # Find keys in prod but not in dev
   diff = difference([prod, dev])

   print(f"Keys in prod but not in dev: {diff}")

Case Conversion
~~~~~~~~~~~~~~~

Convert identifiers between naming conventions:

.. code-block:: python

   from src.case_converter import JSObjectCaseConverter

   # Convert to different styles
   converter = JSObjectCaseConverter()
   camel = converter.to_camel("hello_world")       # "helloWorld"
   pascal = converter.to_pascal("hello_world")     # "HelloWorld"
   snake = converter.to_snake("HelloWorld")        # "hello_world"
   kebab = converter.to_kebab("HelloWorld")        # "hello-world"

AI Processing
~~~~~~~~~~~~~

Use AI to refactor code:

.. code-block:: python

   from src.ai_processor import OpenAIClient, process_file

   # Initialize with OpenAI
   client = OpenAIClient(api_key="sk-...", model="gpt-4o-mini")
   prompt = "Convert this React class component to a functional component with hooks"
   result = process_file("MyComponent.jsx", prompt, client, max_bytes=100_000)

   print(result)

Advanced Usage
--------------

Batch Processing with Threading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Process multiple files concurrently:

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor, as_completed
   from pathlib import Path
   from src.rewriter import dedupe, dump_ts_node, parse_json_preserving_duplicates_text

   def process_file(filepath):
       data = parse_json_preserving_duplicates_text(Path(filepath).read_text(encoding="utf-8"))
       clean = dedupe(data)
       output = filepath.replace(".json", "_clean.json")
       Path(output).write_text(dump_ts_node(clean, indent=2, level=0) + "\n", encoding="utf-8")

       return filepath

   # Process 100 files in parallel
   files = [f"data/file_{i}.json" for i in range(100)]

   with ThreadPoolExecutor(max_workers=8) as executor:
       futures = {executor.submit(process_file, f): f for f in files}

       for future in as_completed(futures):
           filepath = futures[future]
           try:
               result = future.result()
               print(f"✅ {result}")
           except Exception as e:
               print(f"❌ {filepath}: {e}")

Custom Filters
~~~~~~~~~~~~~~

Apply advanced filters to search results:

.. code-block:: python

   from src.core import Condition, filter_files_by_conditions
   from src.utils import walk_files

   files = list(walk_files("/path/to/project"))
   conditions = [
       Condition("size", ">", "10240"),
       Condition("content", "contains", "deprecated", use_regex=False),
   ]
   filtered = filter_files_by_conditions(files, conditions)

JSX Text Extraction
~~~~~~~~~~~~~~~~~~~

Extract hardcoded strings from React components for i18n:

.. code-block:: python

   import json
   from src.text_extractor.extractor import extract_from_directory, extract_to_json

   # Extract from directory
   paths_and_values = extract_from_directory(
       directory="/path/to/components",
       param_name=None,
       drop_standard_tags=True,
       extensions=[".jsx", ".tsx"],
   )
   texts = extract_to_json(paths_and_values, nested=True)

   # Save as i18n JSON
   with open("i18n/en.json", "w") as f:
       json.dump(texts, f, indent=2)

Error Handling
~~~~~~~~~~~~~~

Proper error handling with logging:

.. code-block:: python

   from src.core import SearchOptions, replace_in_text
   from src.utils import read_text, write_text
   from src.utils.logger import get_logger

   logger = get_logger(__name__)

   try:
       file_path = "example.py"
       old = read_text(file_path)
       pattern = SearchOptions().compile("old_api")
       new, count = replace_in_text(old, pattern, "new_api")
       if count:
           write_text(file_path, new)
       logger.info("Replacement complete: %s replacements", count)
   except FileNotFoundError as e:
       logger.error(f"File not found: {e}")
   except PermissionError as e:
       logger.error(f"Permission denied: {e}")
   except Exception as e:
       logger.exception(f"Unexpected error: {e}")

Next Steps
----------

* :doc:`core` - Detailed core API reference
* :doc:`rewriter` - JSON manipulation API
* :doc:`gui` - Building custom GUI extensions
* :doc:`cli` - Command-line usage
