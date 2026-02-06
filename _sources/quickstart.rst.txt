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
   pip install -r requirements.txt

Basic Examples
--------------

Search Files
~~~~~~~~~~~~

Search for a pattern across multiple files:

.. code-block:: python

   from src.core.search_replace import search_files
   
   # Find all TODOs in Python files
   results = search_files(
       directory="/path/to/project",
       pattern="TODO",
       regex=False,
       case_sensitive=True,
       extensions=[".py"]
   )
   
   for result in results:
       print(f"{result['file']}:{result['line_number']} - {result['line_content']}")

Replace Text
~~~~~~~~~~~~

Replace text with preview and backup:

.. code-block:: python

   from src.core.search_replace import replace_in_files
   
   # Replace old API calls with new ones
   results = replace_in_files(
       directory="/path/to/project",
       search_pattern="old_function(",
       replace_pattern="new_function(",
       regex=False,
       create_backup=True,
       extensions=[".py", ".js"]
   )
   
   print(f"Replaced in {len(results)} files")

Deduplicate JSON
~~~~~~~~~~~~~~~~

Clean a JSON file by removing duplicate keys:

.. code-block:: python

   import json
   from src.rewriter.rewriter import JSONRewriter
   
   # Load JSON
   with open("config.json") as f:
       data = json.load(f)
   
   # Deduplicate (keep last occurrence)
   rewriter = JSONRewriter()
   clean_data = rewriter.deduplicate(data, keep="last")
   
   # Save
   with open("config_clean.json", "w") as f:
       json.dump(clean_data, f, indent=2)

Set Operations
~~~~~~~~~~~~~~

Compare two JSON files to find differences:

.. code-block:: python

   import json
   from src.core.set_operations import difference
   
   # Load files
   with open("config_prod.json") as f:
       prod = json.load(f)
   
   with open("config_dev.json") as f:
       dev = json.load(f)
   
   # Find keys in prod but not in dev
   diff = difference(prod, dev)
   
   print(f"Keys in prod but not in dev: {diff}")

Case Conversion
~~~~~~~~~~~~~~~

Convert identifiers between naming conventions:

.. code-block:: python

   from src.case_converter import convert_case
   
   # Convert to different styles
   camel = convert_case("hello_world", "camelCase")       # "helloWorld"
   pascal = convert_case("hello_world", "PascalCase")     # "HelloWorld"
   snake = convert_case("HelloWorld", "snake_case")       # "hello_world"
   kebab = convert_case("HelloWorld", "kebab-case")       # "hello-world"

AI Processing
~~~~~~~~~~~~~

Use AI to refactor code:

.. code-block:: python

   from src.ai_processor import AIProcessor
   
   # Initialize with OpenAI
   processor = AIProcessor(
       provider="openai",
       api_key="sk-...",
       model="gpt-4o"
   )
   
   # Refactor code
   code = """
   class MyComponent extends React.Component {
       render() {
           return <div>Hello</div>;
       }
   }
   """
   
   prompt = "Convert this React class component to a functional component with hooks"
   result = processor.process(prompt, code)
   
   print(result)

Advanced Usage
--------------

Batch Processing with Threading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Process multiple files concurrently:

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor, as_completed
   from src.rewriter.rewriter import JSONRewriter
   import json
   
   def process_file(filepath):
       with open(filepath) as f:
           data = json.load(f)
       
       rewriter = JSONRewriter()
       clean = rewriter.deduplicate(data)
       
       output = filepath.replace(".json", "_clean.json")
       with open(output, "w") as f:
           json.dump(clean, f, indent=2)
       
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

   from src.core.filters import AdvancedFilter
   from src.core.search_replace import search_files
   
   # Create filter: files > 10KB, modified in last 7 days
   filter = AdvancedFilter(
       min_size=10 * 1024,  # 10 KB
       max_age_days=7,
       content_pattern="deprecated",
       content_regex=True
   )
   
   # Search with filter
   results = search_files(
       directory="/path/to/project",
       pattern="api",
       filter=filter
   )

JSX Text Extraction
~~~~~~~~~~~~~~~~~~~

Extract hardcoded strings from React components for i18n:

.. code-block:: python

   from src.extractors.jsx_extractor import JSXExtractor
   
   # Extract from directory
   extractor = JSXExtractor()
   texts = extractor.extract_from_directory(
       path="/path/to/components",
       mode="tag-content",  # Extract inner text
       only_strings=True,   # Skip {variables}
       avoid_keys=["className", "data-testid"],
       no_standard=True,    # Skip <div>, <span>, etc.
       normalize="snake_case",
       limit=40,
       avoid_cut=True       # Don't cut words
   )
   
   # Save as i18n JSON
   import json
   with open("i18n/en.json", "w") as f:
       json.dump(texts, f, indent=2)

Error Handling
~~~~~~~~~~~~~~

Proper error handling with logging:

.. code-block:: python

   import logging
   from src.core.search_replace import replace_in_files
   
   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)
   
   try:
       results = replace_in_files(
           directory="/path/to/project",
           search_pattern="old_api",
           replace_pattern="new_api",
           create_backup=True
       )
       logger.info(f"Successfully replaced in {len(results)} files")
   except FileNotFoundError as e:
       logger.error(f"Directory not found: {e}")
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
