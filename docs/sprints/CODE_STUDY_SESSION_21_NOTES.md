# Code Study Session 21 - Root-Level Managers & Converters
**Date**: 2026-01-23
**Programmer**: #7
**Branch**: COM7-read-docs
**Protocol**: Simplicity Protocol 3 v4.5 - Step 1.2 (Deep Comprehension)

---

## 📋 Session Overview

**Session Focus**: Root-level managers, converters, and extractors (high-value business logic)

### Files Selected for Session 21 (12 files)

**Root-Level Managers**:
1. `src/batch_manager.py` - Batch operation management
2. `src/diff_analyzer.py` - Diff analysis utilities
3. `src/export_manager.py` - Multi-format export manager
4. `src/merge_manager.py` - JSON merge logic
5. `src/history_manager.py` - Operation history tracking
6. `src/statistics_manager.py` - Statistics calculation

**Converters Module**:
7. `src/converters/format_converter.py` - Format conversion logic
8. `src/converters/factory.py` - Converter factory
9. `src/converters/strategies.py` - Conversion strategies
10. `src/converters/bson.py` - BSON format support
11. `src/converters/toon.py` - TOML/JSON conversion
12. `src/case_converter.py` - Case conversion utilities

---

## 🔍 Detailed File Analysis


### 1. batch_manager.py (316 lines)

**Purpose**: Batch execution manager for Set Operations pipelines (v2.9.102)

**Key Classes**:
1. **BatchStep**: Single operation in pipeline (operation, file_a_source, file_b_path, comparison_mode, options)
2. **BatchJob**: Named pipeline with multiple steps (save_intermediate, output_folder)
3. **BatchExecutor**: QThread-based executor with progress signals
4. **BatchHistory**: QSettings storage for last 10 jobs

**Key Features**:
- **Pipeline Execution**: Chain multiple set operations (A ∩ B → result ∩ C...)
- **Previous Result Chaining**: file_a_source='previous_result' uses output from prior step
- **Auto Backups**: 5 backup rotation per file
- **Stop Immediately**: Batch aborts on first error (no partial execution)
- **Intermediate Saves**: Optional save after each step to output folder
- **History**: Last 10 batches persisted in QSettings

**Design Patterns**:
1. **Template Method** - Batch execution workflow
2. **Observer** - Progress signals (step_started, step_completed, step_failed, batch_completed, batch_failed)
3. **Strategy** - Different operations (intersection, union, difference, symmetric)
4. **Memento** - Batch history persistence

**Critical Code**:
- **Lines 198-203**: Previous result handling (first step must use file_path)
- **Lines 246-258**: Error handling with batch abortion (Stop Immediately)
- **Lines 294-303**: History rotation (MAX_HISTORY=10)

---

### 2. diff_analyzer.py (242 lines)

**Purpose**: Diff analysis for JSON datasets with visualization (v2.9.99)

**Key Features**:
- **4 Categories**: only_in_a, only_in_b, common, modified
- **Flattening**: Dot-notation for nested structures (a.b.c)
- **Comparison Modes**: key_only, key_value, full_path_value
- **HTML Export**: Side-by-side diff with color highlighting

**Design Patterns**:
1. **Strategy** - Comparison modes
2. **Visitor** - Recursive flattening
3. **Template Method** - HTML export workflow

**HTML Colors** (Lines 173-177):
```python
.only-a: #c8f7c5 (light green)
.only-b: #ffcccb (light red)
.common: #ffffcc (yellow)
.modified: #ffd9b3 (orange)
```

**Flattening Logic** (Lines 74-106):
- Dicts: {"a": {"b": 1}} → {"a.b": 1}
- Lists: [1, 2] → {"[0]": 1, "[1]": 2}
- Mixed: {"items": [{"id": 1}]} → {"items[0].id": 1}

---

### 3. export_manager.py (383 lines)

**Purpose**: Multi-format export manager (v2.9.93)

**Supported Formats** (5):
1. **JSON**: Pretty-printed with indent
2. **CSV**: Flattened key-value pairs
3. **Excel** (XLSX): With header formatting (openpyxl)
4. **YAML**: Nested structure preserved (pyyaml)
5. **TOML**: Flattened (tomli-w)

**Key Features**:
- **Flattening**: Dot-notation for CSV/Excel/TOML
- **Metadata**: _metadata field with timestamp, operation, tool version
- **Header Formatting** (Excel): Bold, blue background (#4472C4)
- **Progress Modals**: MinimalProcessingModal for long operations
- **Auto Dependencies**: Detects missing packages (ImportError with install instructions)

**Design Patterns**:
1. **Facade** - Simplifies format-specific exporters
2. **Strategy** - Format-specific export strategies
3. **Template Method** - export() delegates to format-specific methods
4. **Factory** - Format string → exporter method mapping

**Flattening Example** (Lines 49-77):
```python
{"a": {"b": {"c": 1}}} → {"a.b.c": 1}
{"arr": [1, 2]} → {"arr": "[1, 2]"}  # Lists as JSON strings
```

**Critical Code**:
- **Lines 169-171**: openpyxl availability check
- **Lines 189-220**: Excel header formatting (bold + blue fill)
- **Lines 360-382**: Format delegation logic

---

### 4. merge_manager.py (371 lines)

**Purpose**: Merge Set Operations results back to files (v2.9.100)

**Merge Modes** (3):
1. **MODE_REPLACE**: Overwrite entire file (with backup)
2. **MODE_MERGE**: Deep recursive merge (result overwrites conflicts)
3. **MODE_NEW_FILE**: Create new file with _merged suffix

**Key Features**:
- **Auto Backups**: Max 5 backups with timestamp rotation
- **Permission Validation**: Write access checks before operation
- **Recursive Merge**: Nested dict merging with result priority
- **Simulate Mode**: Preview merge without writing (for UI preview)
- **Backup Rotation**: Keep only max_backups, delete oldest

**Design Patterns**:
1. **Strategy** - 3 merge strategies
2. **Template Method** - merge_to_file workflow
3. **Factory** - Mode selection

**Recursive Merge Strategy** (Lines 170-212):
```python
# Priority rules:
- Key only in result → add
- Key only in original → keep
- Key in both + different value → result overwrites
- Arrays: replace entirely (no element-wise merge)
- Nested dicts: merge recursively
```

**Backup Naming** (Lines 225-230):
```
data.json → data.json.bak.2025-12-23_143052
           → data.json.bak.2025-12-23_143153
           (max 5, oldest deleted)
```

**Critical Code**:
- **Lines 198-211**: Recursive merge logic (result priority)
- **Lines 241-269**: Backup rotation (sort by mtime, delete oldest)
- **Lines 314-340**: New file path generation (_merged, _merged_1, etc.)

---

### 5. history_manager.py (175 lines)

**Purpose**: Operation history tracking for Set Operations

**Key Features**:
- **Storage**: QSettings ("Clarify", "Clarify")
- **Capacity**: Last 50 operations (MAX_ENTRIES=50)
- **Persistence**: Automatic via QSettings
- **Export**: JSON export with metadata
- **Display Format**: "[2024-12-22 14:30] A ∩ B (by_key) → 42 results"

**Stored Fields**:
- timestamp (ISO format)
- operation_type (∩, ∪, −, ⊕)
- file1, file2 (full paths)
- comparison_mode
- result_count
- result_data (optional, for re-execute)

**Design Patterns**:
1. **Memento** - History entry storage
2. **Singleton** - QSettings instance

---

### 6. statistics_manager.py (215 lines)

**Purpose**: JSON statistics calculation for Set Operations

**Calculated Statistics**:
- **Keys**: total_keys, unique_keys, duplicate_keys
- **Structure**: max_depth, size_bytes
- **Value Types**: string, number, boolean, null, array, object counts

**Key Features**:
- **Recursive Analysis**: Traverses entire structure
- **Overlap Percentage**: (result_count / total_keys) * 100
- **Size Formatting**: B, KB, MB, GB
- **Comparative Display**: 3-column table (File A, File B, Result)

**Design Patterns**:
1. **Visitor** - Recursive analysis
2. **Strategy** - Different formatting strategies

**Overlap Calculation** (Lines 102-122):
```python
total = file1_keys + file2_keys
overlap = (intersection_count / total) * 100
```

---

### 7. format_converter.py (327 lines)

**Purpose**: Main facade for format conversions (v2.9.80)

**Conversion Graph**:
```
JSON ←→ TOON
 ↓  ×    ↓
BSON ←→ (via JSON)
```

**Key Features**:
- **Single File**: convert_file() with auto-detect
- **Batch Directory**: batch_convert() with recursive option
- **Auto Detection**: detect_format() from content
- **Roundtrip Validation**: validate_roundtrip() tests lossless conversion
- **Format Detection**: JSON starts with `{` or `[`, BSON is binary, TOON validated

**Design Patterns**:
1. **Facade** - Simplifies converter access
2. **Factory** - Delegates to ConverterFactory
3. **Strategy** - Format-specific adapters

**Auto-Detection Logic** (Lines 213-269):
1. bytes → BSON validation
2. String starting with `{` or `[` → Try JSON decode
3. ToonAdapter.validate() → TOON
4. Last attempt: Try JSON (minified/whitespace)

**Critical Code**:
- **Lines 110-112**: Auto format detection from file extensions
- **Lines 272-324**: Roundtrip validation (convert A→B→A, compare)

---

### 8. factory.py (129 lines)

**Purpose**: Converter factory with full conversion graph (v2.9.80)

**Supported Conversions** (6 bidirectional):
```python
(Format.JSON, Format.TOON): JsonToToonConverter
(Format.TOON, Format.JSON): ToonToJsonConverter
(Format.JSON, Format.BSON): JsonToBsonConverter
(Format.BSON, Format.JSON): BsonToJsonConverter
(Format.TOON, Format.BSON): ToonToBsonConverter  # via JSON
(Format.BSON, Format.TOON): BsonToToonConverter  # via JSON
```

**Design Patterns**:
1. **Factory Method** - create() returns converter instance
2. **Strategy** - Converter strategies for each conversion
3. **Registry** - _CONVERTERS dict maps (source, target) → class

**Error Handling**:
- Same format: ConversionError ("no conversion needed")
- Unsupported: ConversionError with list of supported conversions

---

### 9. strategies.py (235 lines)

**Purpose**: 6 converter strategy implementations (v2.9.80)

**Converter Classes**:
1. **JsonToToonConverter**: JSON → TOON
2. **ToonToJsonConverter**: TOON → JSON (with indent=2)
3. **JsonToBsonConverter**: JSON → BSON (binary)
4. **BsonToJsonConverter**: BSON → JSON (with default=str for special types)
5. **ToonToBsonConverter**: TOON → JSON → BSON (indirect)
6. **BsonToToonConverter**: BSON → JSON → TOON (indirect)

**Design Patterns**:
1. **Strategy** - Each converter is a strategy
2. **Template Method** - Abstract base class defines interface
3. **Adapter** - Wraps ToonAdapter and BsonAdapter

**Indirect Conversions** (Lines 164-220):
- TOON→BSON: ToonAdapter.decode() → BsonAdapter.encode()
- BSON→TOON: BsonAdapter.decode() → ToonAdapter.encode()
- Uses JSON (Python dict) as intermediate format

---

### 10. case_converter.py (338 lines)

**Purpose**: JSON/TS/JS case conversion (Nov 24, 2025)

**Supported Case Styles** (4):
1. **camelCase**: firstSecond
2. **PascalCase**: FirstSecond
3. **snake_case**: first_second
4. **kebab-case**: first-second

**Key Features**:
- **Tolerant Parsing**: Handles comments, unquoted keys, trailing commas
- **TS Support**: Removes `as const`, `satisfies Type` annotations
- **Template Literals**: Converts `\`text\`` → "text"
- **Export Formats**: `export default {...}`, `module.exports = {...}`
- **Recursive**: Converts keys at all nesting levels
- **Output Formats**: JSON (quoted) or JS (unquoted)

**Design Patterns**:
1. **Strategy** - 4 case conversion strategies
2. **Visitor** - Recursive key conversion
3. **Adapter** - JS/TS → JSON normalization

**Token Splitting Logic** (Lines 44-55):
```python
# Split "myVariableName" into ["my", "Variable", "Name"]
1. Replace '-' and '_' with spaces
2. Insert spaces before capitals: myVariable → my Variable
3. Handle acronyms: HTTPSConnection → HTTPS Connection
4. Split and filter empty strings
```

**Normalization Steps** (Lines 156-189):
```python
1. Remove TS type annotations: 'as const', 'satisfies Type'
2. Convert template literals: `text` → "text"
3. Convert single quotes: 'text' → "text"
4. Quote unquoted keys: { key: → { "key":
5. Remove trailing commas: {...,} → {...}
```

**Critical Code**:
- **Lines 126-154**: Balanced brace extraction (handles nested objects, strings)
- **Lines 156-189**: JS→JSON normalization (handles TS syntax)
- **Lines 206-226**: Recursive key conversion (preserves structure)

---

### 11. bson.py & toon.py (Skipped - imported modules)

These are adapters for BSON and TOON formats, used by converters but not studied in detail this session.

---

## 📊 Session Summary

### Files Studied: 10 Manager & Converter Files

| File | Lines | Category | Patterns | Key Features |
|------|-------|----------|----------|--------------|
| batch_manager.py | 316 | Manager | Template, Observer, Strategy, Memento | Pipeline chaining, history |
| diff_analyzer.py | 242 | Analyzer | Strategy, Visitor, Template | 4-category diff, HTML export |
| export_manager.py | 383 | Manager | Facade, Strategy, Template, Factory | 5 formats, metadata |
| merge_manager.py | 371 | Manager | Strategy, Template, Factory | 3 modes, backup rotation |
| history_manager.py | 175 | Manager | Memento, Singleton | 50 operations, QSettings |
| statistics_manager.py | 215 | Manager | Visitor, Strategy | 7 statistics, overlap % |
| format_converter.py | 327 | Facade | Facade, Factory, Strategy | Auto-detect, roundtrip |
| factory.py | 129 | Factory | Factory, Strategy, Registry | 6 conversions |
| strategies.py | 235 | Strategy | Strategy, Template, Adapter | 6 converters |
| case_converter.py | 338 | Converter | Strategy, Visitor, Adapter | 4 cases, TS/JS tolerant |

**Total Lines**: 2,731 lines studied

### Key Discoveries

1. **Batch Pipeline Architecture** (batch_manager.py):
   - Chain operations: (A ∩ B) → result ∩ C → result ∪ D...
   - Previous result chaining with file_a_source='previous_result'
   - Stop Immediately on error (no partial execution)
   - History persistence with 10-job capacity

2. **Diff Analysis with HTML Export** (diff_analyzer.py):
   - Flattening: {"a": {"b": 1}} → {"a.b": 1}
   - 4 categories: only_in_a, only_in_b, common, modified
   - Side-by-side HTML with color highlighting
   - Colors: green (only_a), red (only_b), yellow (common), orange (modified)

3. **Multi-Format Export** (export_manager.py):
   - 5 formats: JSON, CSV, Excel, YAML, TOML
   - Automatic flattening for CSV/Excel/TOML
   - Excel header formatting (bold, blue #4472C4)
   - Metadata injection (_metadata field)
   - Missing dependency detection with install instructions

4. **Merge Strategies** (merge_manager.py):
   - 3 modes: REPLACE, MERGE, NEW_FILE
   - Recursive merge with result priority
   - Arrays replaced entirely (no element-wise merge)
   - Backup rotation (max 5, timestamp naming)
   - Simulate mode for preview without writing

5. **Format Conversion Graph** (converters):
   - JSON ↔ TOON (direct)
   - JSON ↔ BSON (direct)
   - TOON ↔ BSON (via JSON intermediate)
   - Auto format detection from content
   - Roundtrip validation for lossless conversion

6. **Case Conversion** (case_converter.py):
   - 4 styles: camelCase, PascalCase, snake_case, kebab-case
   - Tolerant TS/JS parsing (comments, unquoted keys, template literals)
   - TS annotation removal (as const, satisfies Type)
   - Output as JSON (quoted) or JS (unquoted)

### Design Patterns Identified (16 total)

1. **Template Method** - Batch execution, export workflow, merge workflow
2. **Observer** - Batch progress signals
3. **Strategy** - Operations, comparison modes, merge modes, case conversions, format converters
4. **Memento** - Batch history, operation history
5. **Facade** - FormatConverter, ExportManager
6. **Factory** - ConverterFactory, format delegation
7. **Visitor** - Recursive flattening, statistics analysis, key conversion
8. **Registry** - Converter mapping, format mapping
9. **Adapter** - ToonAdapter, BsonAdapter, JS→JSON normalization
10. **Singleton** - QSettings (history storage)

### Critical Code Sections (13 identified)

1. **Previous result handling** (batch_manager.py, 198-203) - First step validation
2. **Batch abortion** (batch_manager.py, 246-258) - Stop Immediately strategy
3. **History rotation** (batch_manager.py, 294-303) - MAX_HISTORY=10
4. **HTML color scheme** (diff_analyzer.py, 173-177) - 4-category colors
5. **Flattening logic** (diff_analyzer.py, 74-106; export_manager.py, 49-77) - Dot notation
6. **Excel header formatting** (export_manager.py, 189-220) - Bold + blue fill
7. **Format delegation** (export_manager.py, 360-382) - Format → exporter mapping
8. **Recursive merge** (merge_manager.py, 170-212) - Result priority, array replacement
9. **Backup rotation** (merge_manager.py, 241-269) - mtime sorting, delete oldest
10. **Roundtrip validation** (format_converter.py, 272-324) - Lossless test
11. **Balanced brace extraction** (case_converter.py, 126-154) - Nested object parsing
12. **JS→JSON normalization** (case_converter.py, 156-189) - TS syntax removal
13. **Recursive key conversion** (case_converter.py, 206-226) - Structure preservation

### Performance Considerations

1. **Batch Execution**: Sequential (not parallel) to preserve order and previous result chaining
2. **Flattening**: O(N) where N = total nodes in nested structure
3. **HTML Export**: In-memory string building (consider streaming for large diffs)
4. **Backup Rotation**: Linear scan of directory (acceptable for small MAX_BACKUPS)
5. **Format Detection**: Try-parse approach (JSON first, then TOON, finally validation)

### Security Measures

1. **Permission Validation** (merge_manager.py): Check write access before merge
2. **Path Traversal Prevention**: File existence checks
3. **Backup Before Merge**: Automatic backups before REPLACE/MERGE modes

---

## 🎯 Progress Update

**Session 21 Complete**: 10 Manager & Converter files studied (2,731 lines)

**Updated Statistics**:
- **Previous**: 39/196 files (19.9%)
- **Current**: 49/196 files (25.0%) - **Quarter milestone!** 🎉
- **Progress**: +10 files (+5.1%)

**Remaining**: 147 files (75.0%)

---

## 📝 Next Session Targets

**Priority**: GUI Docks (highest complexity, user-facing)

**Candidates for Session 22** (~8-10 files, high-value GUI components):
1. GUI docks: file_explorer_dock, file_list_dock, set_operations_dock, etc.
2. GUI workers: ai_processor_worker, etc.
3. More root-level managers if time permits

**Estimated Lines**: ~2,500-3,000 lines

---

**Session 21 End**: 2026-01-23
**Files Studied**: 10 files, 2,731 lines
**Patterns Identified**: 16 design patterns
**Critical Sections**: 13 "don't touch" zones
**Milestone**: 25.0% complete (quarter milestone!) 🎉
