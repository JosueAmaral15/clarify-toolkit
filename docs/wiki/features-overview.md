# Features Overview

Clarify provides 10+ specialized tools (docks) for text processing and JSON manipulation. This page gives you a complete overview of all features.

## 🔧 Core Features

### 1. Editor Dock (`Ctrl+E`)

**Purpose**: Edit text and JSON files with syntax highlighting.

**Key Features**:
- Syntax highlighting for JSON, JavaScript, TypeScript, HTML, XML
- Line numbers and code folding
- Find & replace within file
- Auto-save with configurable interval
- Multiple tabs for concurrent editing

**Use Cases**:
- Quick edits to configuration files
- Manual JSON structure modifications
- Review AI-generated content before saving

**Pro Tip**: Use `Ctrl+F` for in-file search, `Ctrl+H` for find & replace.

---

### 2. Search & Replace (`Ctrl+F`)

**Purpose**: Find and replace text across single or multiple files.

**Key Features**:
- ✅ **Search Modes**: Case-sensitive, whole-word, regex
- ✅ **Filters**: File extension, size, date modified, content patterns
- ✅ **Bulk Operations**: Replace in 100+ files simultaneously
- ✅ **Advanced Conditions**: AND/OR logic, field operators (>, <, contains)
- ✅ **Preview**: See all matches before replacing
- ✅ **Undo**: Restore original files from backup

**Use Cases**:
- Update API endpoints across codebase
- Rename variables in legacy code
- Fix typos in documentation
- Standardize configuration values

**Example**:
```
Find:    http://localhost:3000
Replace: https://api.production.com
Files:   *.json, *.yaml, *.env
Result:  42 replacements in 12 files
```

**Advanced**: Use regex for pattern matching:
```
Find:    version:\s*"(\d+\.\d+)\.\d+"
Replace: version: "$1.0"
Result:  Normalizes all patch versions to .0
```

[→ Detailed Guide](features/search-replace.md)

---

### 3. Insert Panel

**Purpose**: Insert text at specific positions (line numbers, before/after patterns).

**Key Features**:
- **5 Insert Modes**: Left, Right, Replace, Above, Below
- **Conditional Insertion**: Only if condition met
- **Batch Processing**: Insert in multiple files
- **Pattern Matching**: Insert relative to regex patterns

**Use Cases**:
- Add headers/footers to files
- Insert imports at top of files
- Add logging statements
- Inject configuration sections

**Example**:
```
Mode:     Above
Pattern:  export default
Text:     // Auto-generated file - do not edit manually
Result:   Comment added above all export statements
```

---

### 4. JSON Rewriter (`Ctrl+Shift+R`)

**Purpose**: Clean, deduplicate, and normalize JSON files.

**Key Features**:
- ✅ **Deduplicate**: Remove duplicate key-value pairs
- ✅ **Join Duplicates**: Merge duplicate keys into arrays
- ✅ **Global Cleanup**: Remove all duplicates across entire file
- ✅ **Format**: Pretty-print with configurable indentation
- ✅ **Validate**: Check JSON syntax before processing
- ✅ **TypeScript Support**: Works with TS object literals

**Use Cases**:
- Clean messy configuration files
- Merge conflicting JSON from git
- Normalize i18n translation files
- Prepare JSON for database import

**Example**:
```json
// Before (duplicates)
{"key": "value1", "key": "value2", "other": "data"}

// After (deduplicated - keep last)
{"key": "value2", "other": "data"}

// After (joined)
{"key": ["value1", "value2"], "other": "data"}
```

**Performance**: Processes 10 MB files in <2 seconds.

[→ Detailed Guide](features/json-rewriter.md)

---

### 5. Set Operations (`Ctrl+Shift+S`)

**Purpose**: Perform logical set operations (∩, ∪, −, ⊕) on JSON files.

**Key Features**:
- **4 Operations**:
  - **Intersection (∩)**: Keys present in both files
  - **Union (∪)**: All keys from both files
  - **Difference (−)**: Keys in A but not in B
  - **Symmetric Difference (⊕)**: Keys in A or B but not both
- **Comparison Modes**: Keys only, values only, both
- **Nested Support**: Deep object comparison
- **Multiple Files**: Operate on 2-10 files

**Use Cases**:
- Compare config files (prod vs dev)
- Merge translation files
- Find missing keys in i18n
- Identify configuration drift

**Example**:
```
File A (prod): {"db": "prod", "api": "v2", "cache": true}
File B (dev):  {"db": "dev", "api": "v2", "debug": true}

Difference (A−B): {"cache": true}  ← in prod but not dev
Intersection (A∩B): {"api": "v2"}  ← in both
```

[→ Detailed Guide](features/set-operations.md)

---

### 6. AI Processor (`Ctrl+Shift+A`)

**Purpose**: Process files with AI (OpenAI GPT, Google Gemini, Claude, Perplexity).

**Key Features**:
- ✅ **4 Providers**: OpenAI, Gemini, Claude, Perplexity
- ✅ **10+ Models**: GPT-4o, Gemini Flash 2.0, Claude Sonnet 4, etc.
- ✅ **Batch Processing**: Process 100+ files in one run
- ✅ **Advanced Filters**: Filename, size, date, content patterns
- ✅ **Token Tracking**: Session + lifetime statistics
- ✅ **Cost Estimation**: Real-time cost calculation
- ✅ **Interrupt**: Stop long-running operations

**Use Cases**:
- Refactor legacy code to modern syntax
- Generate JSDoc/type annotations
- Translate code comments
- Analyze security vulnerabilities
- Generate unit tests

**Example**:
```
Prompt:   "Refactor to TypeScript with strict types"
Files:    src/**/*.js (50 files)
Model:    GPT-4o
Cost:     $2.15
Time:     3.5 minutes
Result:   50 TypeScript files with full type safety
```

**Supported Models**:
- OpenAI: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
- Gemini: Flash 2.0, Pro 2.0, Flash 1.5
- Claude: Opus 4, Sonnet 4, Haiku 4
- Perplexity: Llama 3.1 (70B), Mixtral (8x22B)

[→ Detailed Guide](features/ai-processor.md)

---

### 7. JSON Translator (`Ctrl+Shift+J`)

**Purpose**: Translate text using JSON/TypeScript dictionary files.

**Key Features**:
- **Bidirectional**: Text → Object or Object → Text
- **Scope Support**: JSX, string literals, custom delimiters
- **Exclusion Patterns**: Skip className, data-*, etc.
- **Backup**: Automatic .bak files for safety
- **Undo**: Restore previous state

**Use Cases**:
- Internationalize React/Vue applications
- Translate hardcoded strings to i18n keys
- Reverse translation for debugging
- Update translation files

**Example**:
```jsx
// Before
<h1>Welcome to MyApp</h1>

// Dictionary (en.json)
{"welcome": "Welcome to MyApp"}

// After (inverse translation)
<h1>{t.welcome}</h1>
```

[→ Detailed Guide](features/json-translator.md)

---

### 8. Text Extractor (`Ctrl+Shift+T`)

**Purpose**: Extract text from JSX, HTML, or code files.

**Key Features**:
- **Smart Extraction**: Tag content, attributes, comments
- **Scope Filtering**: Specific tags, classes, custom patterns
- **Export Formats**: JSON, CSV, plain text
- **Deduplication**: Remove duplicate strings
- **Statistics**: Show extraction summary

**Use Cases**:
- Extract translatable strings for i18n
- Generate translation templates
- Audit UI text for consistency
- Create glossaries

**Example**:
```jsx
// Input (App.jsx)
<div>
  <h1>Dashboard</h1>
  <p>Welcome back, {user.name}</p>
  <button>Click here</button>
</div>

// Extracted (output.json)
{
  "Dashboard": "Dashboard",
  "Welcome back, ": "Welcome back, ",
  "Click here": "Click here"
}
```

[→ Detailed Guide](features/text-extractor.md)

---

### 9. Case Converter

**Purpose**: Convert naming conventions (camelCase, snake_case, etc.).

**Key Features**:
- **4 Styles**: camelCase, PascalCase, snake_case, kebab-case
- **Batch Conversion**: Process entire directories
- **Extension Filter**: Only specific file types
- **Preserve Structure**: Maintains file organization

**Use Cases**:
- Standardize variable naming
- Convert API responses to code conventions
- Migrate between coding styles
- Normalize database columns

**Example**:
```python
# Before (mixed styles)
user_name = "John"
UserAge = 30
first-name = "Jane"

# After (camelCase)
userName = "John"
userAge = 30
firstName = "Jane"
```

[→ Detailed Guide](features/case-converter.md)

---

### 10. JSON Search (`Ctrl+Shift+F`)

**Purpose**: Search for keys/values in JSON files with advanced filtering.

**Key Features**:
- **3 Search Modes**: Key only, value only, both
- **Regex Support**: Pattern matching
- **Case Sensitivity**: Toggle on/off
- **Result Limit**: Configurable (default: 1000)
- **Export**: Save results as JSON

**Use Cases**:
- Find all keys containing "email"
- Locate specific configuration values
- Audit JSON structures
- Debug nested data

**Example**:
```
Search: "port" (key mode)
Files: config/*.json

Results:
- config/app.json: "port": 3000
- config/db.json: "port": 5432
- config/redis.json: "port": 6379
Total: 3 matches in 3 files
```

---

### 11. Placeholder Replacer

**Purpose**: Replace placeholders in files with actual values.

**Key Features**:
- **Pattern Support**: {{variable}}, ${variable}, %variable%
- **Dictionary**: Load replacements from JSON
- **Conditional**: Replace only if conditions met
- **Nested**: Support nested placeholders

**Use Cases**:
- Generate files from templates
- Deploy configuration files
- Create documentation from schemas
- Personalize emails/messages

**Example**:
```
Template:
Hello {{name}}, your order #{{order_id}} is {{status}}.

Dictionary:
{"name": "Alice", "order_id": "12345", "status": "shipped"}

Result:
Hello Alice, your order #12345 is shipped.
```

---

## 🎨 UI Features

### Themes
- **Light**: High contrast for daytime use
- **Dark**: Comfortable for extended sessions
- **System**: Automatically match OS theme

### Layouts
- **Compact**: Minimal (Editor only)
- **Standard**: Balanced (Editor + 4 main tools)
- **Advanced**: All docks visible
- **Custom**: Save your own layouts

### Accessibility
- **Screen Reader**: Full NVDA/JAWS support
- **Keyboard Navigation**: Tab order, focus indicators
- **Font Scaling**: Ctrl+Scroll to zoom (8-24pt)
- **High Contrast**: WCAG AAA compliant

### Internationalization (i18n)
- 7 languages: EN, PT-BR, ES, FR, DE, ZH, JA
- Switch anytime: `Settings → Language`
- Community translations welcome!

---

## 📊 Performance

| Operation | Speed | Max File Size |
|-----------|-------|---------------|
| JSON Parsing | 80 MB/s | 100 MB |
| Search | 5.2M items/s | Unlimited |
| Replace | 15 MB/s | 100 MB |
| Rewriter | 35 MB/s | 50 MB |
| Set Operations | 3M items/s | 10 MB each |

**Benchmarks run on**: i5-8250U, 16GB RAM, SSD

---

## 🚀 Getting Started

1. **New to Clarify?** → [Getting Started](getting-started.md)
2. **Quick overview?** → [Quick Start Guide](quick-start-guide.md)
3. **Detailed feature docs?** → Links above ([→ Detailed Guide])
4. **Need help?** → [FAQ](faq.md) | [Troubleshooting](troubleshooting.md)

---

**Next**: Explore individual features or return to [Wiki Home](README.md)
