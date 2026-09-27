CLI
===

Command-line interfaces for Clarify operations.

.. automodule:: src.cli
   :members:
   :undoc-members:
   :show-inheritance:

Main CLI
--------

.. automodule:: src.cli.parser
   :members:
   :undoc-members:
   :show-inheritance:

Command Handlers
----------------

.. automodule:: src.cli.commands
   :members:
   :undoc-members:
   :show-inheritance:

Current Commands
----------------

Run CLI commands through the package entry point:

.. code-block:: bash

   python -m src search PATH QUERY
   python -m src replace PATH QUERY REPLACEMENT --all
   python -m src insert PATH LINE TEXT --mode insert_below
   python -m src translate PATH DICTIONARY
   python -m src gtranslate --text "hello" --target pt
   python -m src dedupe INPUT.json -o OUTPUT.json
