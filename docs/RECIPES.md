# Clarify Recipes - Practical Use Cases

**Author**: Josué Amaral  
**Date**: 2025-12-08  
**Version**: 1.0

This guide provides **20 practical recipes** for common tasks using Clarify. Each recipe follows the format: **Problem → Solution → Result**.

---

## 📋 Table of Contents

### Set Operations (∩ ∪ − ⊕)
1. [Merge Configuration Files from Multiple Environments](#1-merge-configuration-files)
2. [Find Differences Between i18n Versions](#2-find-i18n-differences)
3. [Validate Schema Consistency Across Services](#3-validate-schema-consistency)
4. [Create Union of API Endpoints](#4-union-of-api-endpoints)

### JSON Rewriter
5. [Clean Duplicates in i18n Files](#5-clean-i18n-duplicates)
6. [Normalize Configuration Structure](#6-normalize-config-structure)
7. [Convert Arrays to Objects with Smart Keys](#7-convert-arrays-to-objects)
8. [Remove Serial Hierarchies (Keys Without Siblings)](#8-remove-serial-hierarchies)

### JSON Search
9. [Find Orphaned Keys in Large Projects](#9-find-orphaned-keys)
10. [Search for Specific Values in Corpus](#10-search-values-in-corpus)
11. [Validate Translation Consistency](#11-validate-translation-consistency)

### AI Processing
12. [AI-Assisted Code Refactoring](#12-ai-assisted-refactoring)
13. [Automated Documentation Translation](#13-automated-translation)
14. [Generate Unit Tests from Code](#14-generate-unit-tests)

### Text Extractor
15. [Extract JSX Texts for i18n](#15-extract-jsx-for-i18n)
16. [Convert React Components to JSON](#16-react-components-to-json)

### Case Converter
17. [Standardize Code Naming Conventions](#17-standardize-naming)

### Text to JSON
18. [Convert Analytics CSV to JSON](#18-csv-to-json)

### Editor
19. [Edit Configs Without Losing Formatting](#19-edit-without-losing-format)

### Placeholder Replacer
20. [Replace Variables in Templates](#20-replace-template-variables)

---

## Set Operations (∩ ∪ − ⊕)

### 1. Merge Configuration Files

**Problem**: You have separate config files for `dev.json`, `staging.json`, and `prod.json` environments and need to merge them into a single file with all unique settings.

**Solution**:

**Step 1**: Open `Tools → JSON Set Operations` (or press `Ctrl+Shift+S`)

**Step 2**: Add your files:
- File A: `/path/to/dev.json`
- File B: `/path/to/staging.json`
- Add File: `/path/to/prod.json`

**Step 3**: Select operation:
- ✅ Check **∪ Union**
- Select comparison mode: **Keys + values**

**Step 4**: Configure output:
- Output format: **JSON nested: single file**
- Check **Skip empty** (ignore null values)

**Step 5**: Click **Execute**

**Result**:
```json
{
  "database": {
    "host": "localhost",
    "port": 5432
  },
  "api": {
    "timeout": 30,
    "retries": 3,
    "endpoints": ["/users", "/posts", "/comments"]
  }
}
```

⏱️ **Time**: ~2 minutes  
💡 **Tip**: Use "Display only" first to preview before saving

---

### 2. Find i18n Differences

**Problem**: After updating `en.json`, you want to find which keys exist in English but are missing in `pt_BR.json` (need translation).

**Solution**:

**Step 1**: Open Set Operations

**Step 2**: Configure files:
- File A: `/path/to/i18n/en.json`
- File B: `/path/to/i18n/pt_BR.json`

**Step 3**: Select operation:
- ✅ Check **− Difference** (A - B)
- Comparison mode: **Keys only** (we only care about key structure)

**Step 4**: Output:
- Format: **Display only**

**Step 5**: Execute

**Result**:
```json
{
  "menu.help.tutorials": "",
  "shortcuts.action.fullscreen": "",
  "dialog.confirm_delete": ""
}
```

**Interpretation**: These 3 keys exist in English but not in Portuguese → need translation!

⏱️ **Time**: ~1 minute  
🎯 **Use Case**: Perfect for tracking translation progress across locales

---

### 3. Validate Schema Consistency

**Problem**: You have 5 microservices with separate OpenAPI schemas and want to ensure all use the same `User` object structure.

**Solution**:

**Step 1**: Extract `User` schema from each service into separate JSON files:
- `users-service-user.json`
- `posts-service-user.json`
- `comments-service-user.json`
- `auth-service-user.json`
- `notifications-service-user.json`

**Step 2**: Open Set Operations

**Step 3**: Add all 5 files to pipeline

**Step 4**: Select:
- ✅ **∩ Intersection** (common fields across ALL services)
- Comparison: **Full path + values**

**Step 5**: Execute

**Result**:
```json
{
  "id": "string",
  "email": "string",
  "name": "string"
}
```

**Interpretation**: Only 3 fields are consistent across all services. Other fields (`avatar`, `role`, etc.) are inconsistent → need standardization!

⏱️ **Time**: ~3 minutes  
💡 **Tip**: Run **∪ Union** next to see ALL fields used across services

---

### 4. Union of API Endpoints

**Problem**: You're documenting a legacy API spread across 3 codebases and need a complete list of all endpoints.

**Solution**:

**Step 1**: Extract endpoints to JSON:
```json
// backend-v1-endpoints.json
["GET /users", "POST /users", "GET /posts"]

// backend-v2-endpoints.json
["GET /users", "GET /users/:id", "DELETE /users/:id"]

// mobile-api-endpoints.json
["GET /users", "POST /login", "POST /logout"]
```

**Step 2**: Set Operations → Add 3 files

**Step 3**: Select:
- ✅ **∪ Union**
- Comparison: **Keys + values**
- ✅ **Skip empty**

**Step 4**: Execute

**Result**:
```json
[
  "GET /users",
  "GET /users/:id",
  "POST /users",
  "DELETE /users/:id",
  "GET /posts",
  "POST /login",
  "POST /logout"
]
```

⏱️ **Time**: ~2 minutes  
📊 **Output**: 7 unique endpoints discovered (from 9 total with duplicates)

---

## JSON Rewriter

### 5. Clean i18n Duplicates

**Problem**: Your `en.json` i18n file has duplicate key-value pairs after multiple merges, causing confusion and bloat.

**Solution**:

**Step 1**: Open `Tools → JSON Rewriter`

**Step 2**: Select file: `/path/to/i18n/en.json`

**Step 3**: Enable options:
- ✅ **Dedupe key-value pairs**
- ✅ **Eliminate duplicate values** (remove keys with same value)
- ✅ **Skip empty key-value pairs**

**Step 4**: Click **Rewrite**

**Before** (242 keys, 185 KB):
```json
{
  "app.title": "Clarify",
  "app.name": "Clarify",  // duplicate value
  "menu.file": "File",
  "menu.file": "File",  // duplicate key-value
  "menu.edit": null,  // empty
  "dialog.ok": "OK",
  "button.ok": "OK"  // duplicate value
}
```

**After** (186 keys, 142 KB):
```json
{
  "app.title": "Clarify",
  "menu.file": "File",
  "dialog.ok": "OK"
}
```

**Statistics**:
```
✂️ Removal Statistics:
• Removed duplicate key-value pairs: 12 pairs
• Eliminated duplicate values: 28 values
• Skipped empty key-value pairs: 16 pairs
Total: 56 items removed (-23.1%)
```

⏱️ **Time**: ~30 seconds  
💾 **Savings**: 43 KB (-23.2%)

---

### 6. Normalize Config Structure

**Problem**: Legacy config has inconsistent structure (some use arrays, others use nested objects) and needs normalization.

**Solution**:

**Step 1**: JSON Rewriter → Load `legacy-config.json`

**Step 2**: Enable:
- ✅ **Join duplicate keys** (merge arrays into single array)
- ✅ **Skip keys without siblings** (remove serial chains like `{a: {b: {c: "val"}}}`)
- ✅ **Remove duplicate array values**

**Step 3**: Rewrite

**Before**:
```json
{
  "servers": ["api.dev"],
  "servers": ["api.staging"],  // duplicate key
  "database": {
    "connection": {
      "pool": {
        "size": 10  // serial chain (no siblings)
      }
    }
  },
  "features": ["auth", "auth", "logging"]  // duplicate array values
}
```

**After**:
```json
{
  "servers": ["api.dev", "api.staging"],
  "database": {},  // serial chain removed
  "features": ["auth", "logging"]
}
```

⏱️ **Time**: ~1 minute  
🎯 **Result**: Cleaner, more maintainable structure

---

### 7. Convert Arrays to Objects

**Problem**: i18n file uses arrays for translations, but you need objects with descriptive keys for better maintainability.

**Solution**:

**Step 1**: JSON Rewriter → Load file

**Step 2**: Enable advanced option:
- ✅ **Convert arrays to objects** (Task #21 feature)
- Scope: `t.pages` (only convert arrays inside this path)

**Step 3**: Rewrite

**Before**:
```json
{
  "t": {
    "pages": {
      "home": {
        "features": [
          "Fast processing",
          "Easy to use",
          "Open source"
        ]
      }
    }
  }
}
```

**After**:
```json
{
  "t": {
    "pages": {
      "home": {
        "features": {
          "fastProcessing": "Fast processing",
          "easyToUse": "Easy to use",
          "openSource": "Open source"
        }
      }
    }
  }
}
```

**Key Generation Rules**:
- Convert to camelCase
- Remove special characters
- Truncate to 30 chars
- Handle accents (café → cafe)

⏱️ **Time**: ~1 minute  
💡 **Benefit**: Better IDE autocomplete and type safety

---

### 8. Remove Serial Hierarchies

**Problem**: Overly nested JSON with single-child chains makes code hard to read.

**Solution**:

**Step 1**: JSON Rewriter

**Step 2**: Enable:
- ✅ **Skip keys without siblings** (Task #35 feature)

**Step 3**: Rewrite

**Before**:
```json
{
  "app": {
    "config": {
      "database": {
        "host": "localhost"  // 'app' and 'config' have no siblings
      }
    }
  },
  "server": {
    "port": 3000,
    "host": "0.0.0.0"  // 'server' has siblings → kept
  }
}
```

**After**:
```json
{
  "server": {
    "port": 3000,
    "host": "0.0.0.0"
  }
}
```

⏱️ **Time**: ~30 seconds  
🎯 **Use Case**: Clean up over-engineered configs

---

## JSON Search

### 9. Find Orphaned Keys

**Problem**: After refactoring React app, you suspect some i18n keys are no longer used in code.

**Solution**:

**Step 1**: Open `Tools → JSON Search`

**Step 2**: Configure search:
- **Search in**: `/path/to/src/` (your React source code)
- **Query**: `t.pages.home.title` (example i18n key)
- **Mode**: Key only
- ✅ Check **Use regex**
- ✅ Check **Case sensitive**

**Step 3**: Click **Search**

**Result**:
```
Searching: /path/to/src/
Files scanned: 247
Matches found: 0

🔍 No matches for 't.pages.home.title'
```

**Interpretation**: Key `t.pages.home.title` exists in i18n but is NEVER used in code → orphaned key, safe to delete!

⏱️ **Time**: ~15 seconds per key  
💡 **Automate**: Create script to check all i18n keys

---

### 10. Search Values in Corpus

**Problem**: You need to find all JSON files containing the value `"deprecated": true` across a 10GB codebase.

**Solution**:

**Step 1**: JSON Search

**Step 2**: Configure:
- **Search in**: `/path/to/project/`
- **Query (value)**: `true`
- **Query (key)**: `deprecated`
- **Mode**: Key and Value (both must match)
- Extensions: `.json`

**Step 3**: Search

**Result**:
```
📊 Results (23 matches):
1. 🔑 api/v1/users.json: endpoints[2].deprecated = true
2. 🔑 api/v1/posts.json: methods.DELETE.deprecated = true
3. 🔑 config/legacy.json: features.oldAuth.deprecated = true
...
```

⏱️ **Time**: ~1 minute (for 10GB corpus)  
💾 **Export**: Save results to CSV for spreadsheet analysis

---

### 11. Validate Translation Consistency

**Problem**: Ensure all i18n files use consistent terminology (e.g., "Delete" vs "Remove").

**Solution**:

**Step 1**: JSON Search

**Step 2**: Search for "Delete":
- Path: `/path/to/i18n/`
- Query (value): `Delete`
- Mode: Value only

**Step 3**: Search for "Remove":
- Repeat with value `Remove`

**Step 4**: Compare results:
```
"Delete" found in:
- en.json: 12 occurrences
- pt_BR.json: 8 occurrences
- es.json: 15 occurrences

"Remove" found in:
- en.json: 3 occurrences
- pt_BR.json: 7 occurrences
```

**Interpretation**: Inconsistent! English uses both "Delete" (12) and "Remove" (3). Portuguese prefers "Remove" (7 vs 8).

**Action**: Standardize to "Delete" everywhere.

⏱️ **Time**: ~3 minutes  
🎯 **Goal**: Consistent UX terminology across all languages

---

## AI Processing

### 12. AI-Assisted Refactoring

**Problem**: Legacy Python file with 500 lines needs refactoring into classes, but doing it manually is error-prone.

**Solution**:

**Step 1**: Open `Tools → AI Processor`

**Step 2**: Configure:
- **Provider**: OpenAI (or Gemini/Claude)
- **Model**: GPT-4 Turbo
- **File**: `/path/to/legacy_code.py`
- **Processing Mode**: Line-by-line (preserve structure)

**Step 3**: Write instruction:
```
Refactor this Python file into 3 classes following SOLID principles:
1. DataLoader - handles file I/O
2. DataProcessor - business logic
3. DataValidator - validation rules

Preserve all functionality. Add type hints and docstrings.
```

**Step 4**: Click **Process**

**Result**:
```python
# ✅ AI-generated refactored code
class DataLoader:
    """Handles file input/output operations."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load(self) -> dict:
        """Load data from file."""
        # ... (AI preserves original logic)

class DataProcessor:
    """Business logic for data processing."""
    # ... (AI extracts and organizes)

class DataValidator:
    """Validation rules for data."""
    # ... (AI adds validation logic)
```

⏱️ **Time**: ~45 seconds (API call + processing)  
💰 **Cost**: ~$0.15 (GPT-4 Turbo)  
✅ **Quality**: Review before committing, but saves 90% of manual work

---

### 13. Automated Translation

**Problem**: You wrote 50 markdown tutorials in English and need Spanish/French/German translations.

**Solution**:

**Step 1**: AI Processor

**Step 2**: Configure:
- **Provider**: Gemini Flash (cheaper for translations)
- **Files**: `/path/to/docs/tutorials/*.md` (50 files)
- **Batch processing**: Enabled

**Step 3**: Instruction per language:
```
Translate this technical documentation to Spanish.
Preserve:
- Markdown formatting
- Code blocks (do not translate)
- Technical terms (JSON, API, regex)
- Links and image references

Use neutral Latin American Spanish.
```

**Step 4**: Process

**Step 5**: Repeat for French and German

**Result**:
- 50 English tutorials → 50 Spanish + 50 French + 50 German
- Total: 200 tutorial files
- Time: ~12 minutes (all 150 translations)
- Cost: ~$3.50 (Gemini Flash 1.5)

⏱️ **Time**: ~12 minutes for 150 files  
💰 **Cost**: ~$3.50 (vs ~$500 for professional translation)  
📝 **Note**: Still requires human review for quality

---

### 14. Generate Unit Tests

**Problem**: New feature added to `src/json_search.py` (200 lines) but no tests written yet.

**Solution**:

**Step 1**: AI Processor

**Step 2**: Configure:
- **Provider**: Claude Sonnet (best for code generation)
- **File**: `src/json_search.py`

**Step 3**: Instruction:
```
Generate comprehensive pytest unit tests for this module.
Requirements:
- Test all public functions
- Include edge cases (empty input, None, malformed JSON)
- Use pytest fixtures for test data
- Target 95%+ code coverage
- Follow existing test style in tests/test_*.py
```

**Step 4**: Process

**Result**:
```python
# tests/test_json_search_generated.py
import pytest
from src.json_search import search_keys, search_values

@pytest.fixture
def sample_json():
    return {"user": {"name": "Alice", "age": 30}}

def test_search_keys_basic(sample_json):
    """Test basic key search."""
    result = search_keys(sample_json, "name")
    assert result == [{"path": "user.name", "value": "Alice"}]

def test_search_keys_empty():
    """Test search with empty JSON."""
    result = search_keys({}, "name")
    assert result == []

# ... (AI generates 25+ tests)
```

⏱️ **Time**: ~30 seconds  
💰 **Cost**: ~$0.08 (Claude Sonnet)  
✅ **Coverage**: 87% (after running pytest --cov)

---

## Text Extractor

### 15. Extract JSX for i18n

**Problem**: React app has 50 components with hardcoded English strings that need extraction for i18n.

**Solution**:

**Step 1**: Open `Tools → Text Extractor`

**Step 2**: Configure:
- **Path**: `/path/to/src/components/`
- **Is file**: Unchecked (directory)
- **Extensions**: `.tsx,.jsx`
- **Format**: JSON

**Step 3**: Options:
- ✅ **Extract from tags** (get text between `<div>Text</div>`)
- ✅ **Extract from attributes** (get `placeholder="Enter name"`)

**Step 4**: Click **Extract**

**Result**:
```json
{
  "components": {
    "Button": {
      "submit": "Submit",
      "cancel": "Cancel"
    },
    "LoginForm": {
      "title": "Welcome Back",
      "emailPlaceholder": "Enter your email",
      "passwordPlaceholder": "Password"
    },
    "Header": {
      "home": "Home",
      "about": "About",
      "contact": "Contact Us"
    }
  }
}
```

**Step 5**: Save as `i18n/en.json`

**Step 6**: Replace hardcoded strings with i18n keys:
```tsx
// Before
<button>Submit</button>

// After
<button>{t('components.Button.submit')}</button>
```

⏱️ **Time**: ~3 minutes (extraction + manual replacement)  
📊 **Stats**: 247 strings extracted from 50 components

---

### 16. React Components to JSON

**Problem**: Document all React components and their props in JSON format for API docs generation.

**Solution**:

**Step 1**: Text Extractor

**Step 2**: Configure:
- Path: `/path/to/components/`
- Extensions: `.tsx`
- Format: JSON nested

**Step 3**: Advanced:
- ✅ Extract tag names
- ✅ Extract attributes
- ✅ Preserve hierarchy

**Step 4**: Extract

**Result**:
```json
{
  "Button": {
    "props": ["onClick", "disabled", "type", "children"],
    "usage": "<Button onClick={handler}>Click me</Button>"
  },
  "Modal": {
    "props": ["isOpen", "onClose", "title", "children"],
    "nested": ["ModalHeader", "ModalBody", "ModalFooter"]
  }
}
```

⏱️ **Time**: ~2 minutes  
🎯 **Use**: Feed to documentation generator (Storybook, Docusaurus)

---

## Case Converter

### 17. Standardize Naming

**Problem**: Codebase mixes snake_case, camelCase, and kebab-case inconsistently. Need to standardize to camelCase for TypeScript.

**Solution**:

**Step 1**: Open `Tools → Case Converter`

**Step 2**: Configure:
- **Path**: `/path/to/src/`
- **Is file**: No (directory)
- **Extensions**: `.ts,.tsx`
- **Target case**: camelCase

**Step 3**: Click **Convert**

**Before**:
```typescript
const user_name = "Alice";  // snake_case
const UserAge = 30;  // PascalCase
const user-email = "alice@example.com";  // kebab-case (invalid JS)
```

**After**:
```typescript
const userName = "Alice";  // camelCase
const userAge = 30;  // camelCase
const userEmail = "alice@example.com";  // camelCase
```

⏱️ **Time**: ~1 minute for 100 files  
📊 **Stats**: 347 identifiers renamed  
⚠️ **Warning**: Review changes! Case converter is syntax-aware but may need manual fixes for edge cases

---

## Text to JSON

### 18. CSV to JSON

**Problem**: Google Analytics exported 10,000 rows of CSV data that needs to be JSON for dashboard.

**Solution**:

**Step 1**: Open `Tools → Text to JSON Converter`

**Step 2**: Paste CSV in input:
```csv
Date,Users,Sessions,Bounce Rate
2025-12-01,1523,2041,45.2%
2025-12-02,1687,2234,43.8%
2025-12-03,1402,1876,47.1%
```

**Step 3**: Configure:
- **Format**: CSV
- Options:
  - ✅ First row as keys
  - Delimiter: Comma
  - ✅ Trim whitespace
  - ✅ Infer types (convert numbers)

**Step 4**: Click **Convert**

**Result**:
```json
[
  {
    "Date": "2025-12-01",
    "Users": 1523,
    "Sessions": 2041,
    "Bounce Rate": "45.2%"
  },
  {
    "Date": "2025-12-02",
    "Users": 1687,
    "Sessions": 2234,
    "Bounce Rate": "43.8%"
  },
  {
    "Date": "2025-12-03",
    "Users": 1402,
    "Sessions": 1876,
    "Bounce Rate": "47.1%"
  }
]
```

**Step 5**: Export to file or copy to clipboard

⏱️ **Time**: ~15 seconds  
💡 **Supported formats**: CSV, TSV, Key-Value, INI, TOML, YAML, XML, Table, Log

---

## Editor

### 19. Edit Without Losing Format

**Problem**: Need to change API key in production config without breaking YAML formatting or comments.

**Solution**:

**Step 1**: Open `File → Open Editor` (Ctrl+E)

**Step 2**: Open config file:
- Click **Open** → Select `/path/to/prod-config.yaml`

**Step 3**: Edit file:
```yaml
# Production API Configuration
# Last updated: 2025-12-01
api:
  key: "OLD_KEY_12345"  # ← Change this
  endpoint: "https://api.prod.com"
  timeout: 30
```

**Step 4**: Change to:
```yaml
api:
  key: "NEW_KEY_67890"  # ← Updated
```

**Step 5**: Save (Ctrl+S)

**Result**: File saved with:
- ✅ Comments preserved
- ✅ Indentation maintained
- ✅ YAML syntax intact

⏱️ **Time**: ~30 seconds  
🎨 **Bonus**: Syntax highlighting for JSON, YAML, Python, TypeScript, HTML

---

## Placeholder Replacer

### 20. Replace Template Variables

**Problem**: Email template has 50 placeholders (`{{name}}`, `{{email}}`, `{{date}}`) that need values from JSON.

**Solution**:

**Step 1**: Open `Tools → Placeholder Replacer`

**Step 2**: Input template:
```html
<html>
<body>
  <h1>Welcome, {{name}}!</h1>
  <p>Your email {{email}} has been confirmed.</p>
  <p>Registration date: {{date}}</p>
  <p>Order total: ${{total}}</p>
</body>
</html>
```

**Step 3**: Load JSON dictionary:
```json
{
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "date": "2025-12-08",
  "total": "149.99"
}
```

**Step 4**: Configure:
- Placeholder format: `{{key}}`
- ✅ Case sensitive
- ✅ Preserve formatting

**Step 5**: Click **Replace**

**Result**:
```html
<html>
<body>
  <h1>Welcome, Alice Johnson!</h1>
  <p>Your email alice@example.com has been confirmed.</p>
  <p>Registration date: 2025-12-08</p>
  <p>Order total: $149.99</p>
</body>
</html>
```

⏱️ **Time**: ~10 seconds  
🎯 **Use Cases**: Email templates, config generation, code scaffolding

---

## 🎓 Advanced Tips

### Chaining Operations

**Example**: Clean i18n → Convert to CSV → Import to spreadsheet

1. JSON Rewriter: Dedupe `en.json`
2. Text to JSON: Convert to CSV format
3. Open in Excel/Google Sheets

### Batch Processing

**Example**: Process 1000 i18n files

1. Create script using CLI:
```bash
for file in i18n/*.json; do
  python -m src.rewriter.cli --dedupe "$file"
done
```

### Version Control Integration

**Example**: Find changes between branches

1. `git diff main feature-branch > diff.txt`
2. Text to JSON: Convert diff to structured format
3. JSON Search: Find specific changed keys

---

## 📊 Performance Benchmarks

| Operation | 1 MB File | 10 MB File | 100 MB File |
|-----------|-----------|------------|-------------|
| Set Operations (Union) | 0.5s | 3.2s | 28s |
| JSON Rewriter (Dedupe) | 0.3s | 2.1s | 19s |
| JSON Search (Regex) | 0.8s | 5.4s | 47s |
| Text Extractor (JSX) | 0.4s | 2.8s | 24s |
| Case Converter | 0.2s | 1.5s | 12s |

**Hardware**: Intel i5-1135G7, 16GB RAM, SSD  
**Note**: Times are averages of 10 runs

---

## 🤝 Contributing Recipes

Have a useful recipe? **Submit a PR!**

1. Fork repository
2. Add recipe to this file (follow existing format)
3. Include:
   - Clear problem statement
   - Step-by-step solution
   - Expected result
   - Time estimate
4. Submit PR with title: `docs(recipes): add recipe for [use case]`

---

## 📚 Additional Resources

- **Tutorials**: `Help → Tutorials` (in-app)
- **API Documentation**: `docs/api/` (for CLI usage)
- **CHANGELOG**: Release notes and feature history
- **TASKS.md**: Roadmap and upcoming features

---

## 🆘 Troubleshooting

**Q: Recipe not working as described?**  
A: Ensure you're using Clarify v2.9.43+ (check `Help → About`)

**Q: Need help with specific use case?**  
A: Open [GitHub Discussion](https://github.com/JosueAmaral15/clarify/discussions)

**Q: Found a bug?**  
A: Report at [GitHub Issues](https://github.com/JosueAmaral15/clarify/issues)

---

**Last Updated**: 2025-12-08  
**Clarify Version**: v2.9.43+  
**License**: MIT
