# Clarify - Project Structure

## 📁 Directory Organization

```
clarify/
├── src/                          # Main source code
│   ├── gui/                      # Modular GUI components (NEW ARCHITECTURE)
│   │   ├── __init__.py          # Exports all docks
│   │   ├── base_dock.py         # Base classes & mixins (295 lines)
│   │   ├── ai_processor_dock.py      # AI processing with OpenAI/Gemini (456 lines)
│   │   ├── case_converter_dock.py    # Case style conversion (223 lines)
│   │   ├── json_rewriter_dock.py     # JSON deduplication & formatting (188 lines)
│   │   ├── json_search_dock.py       # JSON/TS key/value search (250 lines)
│   │   ├── json_translate_dock.py    # Text translation with dict (267 lines)
│   │   ├── placeholder_replacer_dock.py  # Batch placeholder replacement (209 lines)
│   │   └── text_extractor_dock.py    # JSX/HTML text extraction (480 lines)
│   │
│   ├── ai_processor/             # AI client implementations
│   │   ├── openai_client.py
│   │   └── gemini_client.py
│   │
│   ├── json_search/              # JSON search engine
│   │   ├── flattener.py         # Flatten nested JSON
│   │   ├── indexer.py           # Build search index
│   │   ├── query_parser.py      # Parse queries
│   │   └── ts_extractor.py      # Extract TS objects
│   │
│   ├── rewriter/                 # JSON rewriter module
│   │   ├── parser.py            # Parse JSON/TS
│   │   ├── transformer.py       # Transform objects
│   │   └── formatter.py         # Format output
│   │
│   ├── translators/              # Translation modules
│   │   └── json_translator.py
│   │
│   ├── core/                     # Core utilities
│   │   └── file_walker.py
│   │
│   ├── cli/                      # CLI commands
│   │   └── commands.py
│   │
│   ├── utils/                    # Utility functions
│   │
│   ├── app.py                    # Main application (3606 lines)
│   ├── case_converter.py         # Case conversion logic
│   ├── placeholder_replacer.py   # Placeholder replacement logic
│   ├── __init__.py
│   └── __main__.py
│
├── tests/                        # All test files
│   ├── test_ai/                 # AI processor tests
│   ├── test_placeholder/        # Placeholder tests
│   ├── test_*.py                # Individual test files
│   └── test_*.json              # Test data
│
├── docs/                         # Documentation
│   ├── TASKS.md                 # Programming tasks
│   └── architecture/            # Architecture docs
│
├── add/                          # Reference implementations (INTEGRATED)
│   ├── searchJSON/              # → Integrated in JsonSearchDock
│   ├── translator_gui/          # → Integrated in JsonTranslateDock
│   ├── JSON_case_converter/     # → Integrated in CaseConverterDock
│   ├── converting text to JSON/ # → Integrated in TextExtractorDock
│   └── requisite_to_ChatGPT/    # → Integrated in AIProcessorDock
│
├── archive/                      # Old versions (DEPRECATED)
│   └── old/
│       ├── clarify.py
│       └── clarify_patched.py
│
├── pyproject.toml               # Poetry configuration
├── poetry.lock                  # Dependency lock file
├── README.md                    # Project documentation
├── CHANGELOG.md                 # Version history
├── PROJECT_STRUCTURE.md         # This file
├── main.py                      # Entry point (legacy)
├── clarify.py                   # Entry point (legacy)
├── clarify_gui.sh               # Launch script (Linux/Mac)
└── clarify_gui.bat              # Launch script (Windows)
```

## 🏗️ Architecture Overview

### Modular GUI System

**Base Architecture:**
- `BaseDock`: Abstract base class for all docks
- `StandardToolDock`: Pre-configured template with common features
- `ProcessorWorkerBase`: Threading support for long operations

**Mixins (Reusable Components):**
- `FileInputMixin`: File/directory selection
- `ResultsOutputMixin`: Results panel management
- `ActionButtonsMixin`: Standard buttons (Run, Clear, Save)
- `OptionsGroupMixin`: Options grouping
- `ValidationMixin`: Input validation

### Code Reduction

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| app.py lines | 4913 | 3606 | **-26.6%** |
| Inline docks | 7 | 0 | **-100%** |
| Modular docks | 0 | 7 | **+7** |
| Total GUI code | Mixed | 2373 lines | **Separated** |

### Integration Status

| Feature | Source | Status | Location |
|---------|--------|--------|----------|
| JSON Search | add/searchJSON | ✅ 100% | JsonSearchDock |
| Translation | add/translator_gui | ✅ 100% | JsonTranslateDock |
| Case Converter | add/JSON_case_converter | ✅ 100% | CaseConverterDock |
| Text Extraction | add/converting text to JSON | ✅ 100% | TextExtractorDock |
| AI Processing | add/requisite_to_ChatGPT | ✅ 85% | AIProcessorDock |

## 🚀 Running the Application

### GUI Mode (Default)
```bash
python -m src.app
# or
python clarify.py
# or
./clarify_gui.sh  # Linux/Mac
clarify_gui.bat   # Windows
```

### CLI Mode
```bash
# Search
python -m src.app search ./src --query "function" --include "*.py"

# Replace
python -m src.app replace ./src --query "old" --replacement "new" --all

# Insert
python -m src.app insert ./src --line 1 --text "# Header" --mode insert_above

# Translate
python -m src.app translate ./web --dictionary dict.ts

# Dedupe/Rewrite
python -m src.app dedupe en.ts --from-ts --join-keys --eliminate-duplicates
```

## 📦 Dependencies

**Core:**
- Python 3.10+
- PySide6 (GUI)

**Optional:**
- openai (OpenAI API)
- google-generativeai (Gemini API)
- tiktoken (token counting)

**Install:**
```bash
poetry install
# or
pip install -r requirements.txt
```

## 🔧 Development

### Adding a New Dock

1. Create file in `src/gui/new_dock.py`
2. Inherit from `BaseDock` or `StandardToolDock`
3. Implement `_setup_ui()` and `_connect_signals()`
4. Add to `src/gui/__init__.py` exports
5. Add `_open_new()` method in `MainWindow` (app.py)
6. Add menu action in `_build_menu()`

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_case_converter.py
```

## 📝 Notes

- All 7 docks follow the same architectural pattern
- Base classes provide 40-60% code reuse per dock
- Threading support via `ProcessorWorkerBase`
- Consistent UI/UX across all tools
- Complete separation of concerns (GUI vs Logic)

## 🗑️ Deprecated/Legacy

- `src/ui/` - Removed (obsolete, replaced by gui/)
- `archive/old/` - Old versions (reference only)
- `add/` - Reference implementations (all integrated)
- Individual test files in root - Moved to tests/

---

**Last Updated:** November 24, 2025
**Version:** 1.0.0 (Modular Architecture)
