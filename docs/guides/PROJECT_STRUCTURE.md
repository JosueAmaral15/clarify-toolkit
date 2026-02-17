# Clarify - Project Structure

## 📁 Directory Organization

```
clarify/
├── src/                          # Main source code
│   ├── gui/                      # Modular GUI components (NEW ARCHITECTURE)
│   │   ├── __init__.py          # Exports all docks
│   │   ├── base_dock.py         # Base classes & mixins (295 lines)
│   │   ├── dock_factory.py      # Factory for creating docks
│   │   ├── menu_builder.py      # Menu construction logic
│   │   ├── advanced_extractor_dock.py   # Advanced parameter extraction (v2.9.115 - 700 lines)
│   │   ├── ai_processor_dock.py         # AI processing with OpenAI/Gemini (456 lines)
│   │   ├── case_converter_dock.py       # Case style conversion (223 lines)
│   │   ├── file_explorer_dock.py        # File exploration & search (v2.9.115)
│   │   ├── json_rewriter_dock.py        # JSON deduplication & formatting (188 lines)
│   │   ├── json_search_dock.py          # JSON/TS key/value search (250 lines)
│   │   ├── json_translate_dock.py       # Text translation with dict (267 lines)
│   │   ├── placeholder_replacer_dock.py # Batch placeholder replacement (209 lines)
│   │   └── text_extractor_dock.py       # JSX/HTML text extraction (480 lines)
│   │
│   ├── extractors/               # Extraction engines (NEW - v2.9.115)
│   │   └── advanced_extractor.py # Advanced parameter extraction core (708 lines)
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
│   │   ├── file_walker.py
│   │   └── file_list_executor.py # File listing logic
│   │
│   ├── cli/                      # CLI commands
│   │   └── commands.py
│   │
│   ├── utils/                    # Utility functions
│   │   └── error_reporter.py    # Error reporting system
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
│   ├── test_advanced_extractor.py    # Advanced Extractor tests (v2.9.115 - 24 tests)
│   ├── test_docks_factory_pytest.py  # Factory tests (v2.9.115 - pytest)
│   ├── test_load_tests.py            # Load testing system tests
│   ├── test_*.py                # Individual test files
│   ├── test_*.json              # Test data
│   ├── test_component.tsx       # JSX test component
│   └── test_jsx_extractor.py    # JSX extractor tests
│
├── benchmarks/                   # Performance benchmarking (v2.9.115)
│   ├── __init__.py
│   ├── __main__.py              # Module entry point
│   ├── README.md                # Comprehensive docs (600 lines)
│   ├── run.py                   # CLI runner with scenarios
│   ├── generators.py            # Test data generators
│   ├── metrics_collector.py     # Metrics collection
│   ├── benchmark_runner.py      # Execution engine
│   └── results.json             # Latest results
│
├── load_tests/                   # Load testing system (v2.9.82)
│   ├── __init__.py
│   ├── __main__.py              # Module entry point
│   ├── run.py                   # CLI runner
│   ├── scenarios.py             # Load test scenarios
│   ├── metrics_collector.py     # Metrics collection
│   ├── report_generator.py      # Report generation
│   └── load_runner.py           # Execution engine
│
├── docs/                         # Documentation
│   ├── INTEGRATION_SUMMARY.md   # Orphaned code integration summary (v2.9.115)
│   ├── ADVANCED_EXTRACTOR_INTEGRATION.md  # Sprint 2 analysis (v2.9.115)
│   ├── ORPHANED_CODE_INTEGRATION_PLAN.md  # Integration plan
│   ├── TASKS.md                 # Programming tasks
│   ├── specifications/          # Version specifications
│   │   ├── v2.9.36-SPECIFICATION.md
│   │   ├── v2.9.82-SPECIFICATION.md  # Load testing
│   │   └── v2.9.115-SPECIFICATION.md # Advanced Extractor
│   ├── plans/                   # Project planning
│   │   └── SPRINTS_REQUISITE_TO_CHATGPT.md
│   └── architecture/            # Architecture docs
│
├── .github/                      # GitHub configuration
│   └── workflows/
│       └── benchmarks.yml       # CI/CD for benchmarks (v2.9.115)
│
├── scripts/                      # Utility scripts
│   ├── generate_changelog.py    # Changelog automation
│   └── ci_quality_check.sh      # CI quality checks
│
├── config/                       # Configuration files
│   └── config.yaml.example      # Example configuration
│
├── launchers/                    # Application launchers
│   ├── clarify_gui.sh           # Launch script (Linux/Mac)
│   └── clarify_gui.bat          # Launch script (Windows)
│
├── archive/                      # Archived code (DEPRECATED)
│   ├── add/                     # Orphaned code (INTEGRATED v2.9.115)
│   │   ├── main.py              # → Advanced Extractor (Sprint 2)
│   │   └── README.md            # Integration summary
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
└── clarify.py                   # Entry point (main)
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
./launchers/clarify_gui.sh  # Linux/Mac
launchers/clarify_gui.bat   # Windows
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
