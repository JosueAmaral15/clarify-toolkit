# Quick Start Guide

Get started with Clarify in 5 minutes! This guide walks you through a complete workflow.

## 🎯 Your First Workflow: Clean a JSON File

We'll demonstrate Clarify's power by cleaning a JSON file with duplicate keys.

### Step 1: Create a Sample File (1 min)

Create a file named `config.json` with duplicate keys:

```json
{
  "app": {
    "name": "MyApp",
    "version": "1.0.0",
    "version": "1.0.1",
    "port": 8080,
    "port": 3000,
    "debug": true
  },
  "database": {
    "host": "localhost",
    "host": "192.168.1.100",
    "port": 5432
  }
}
```

### Step 2: Open in Clarify (30 seconds)

1. **Launch Clarify**: `python main.py`
2. **Open the file**: 
   - `File → Open` or `Ctrl+O`
   - Select `config.json`
3. **File appears in Editor** dock

### Step 3: Deduplicate with JSON Rewriter (1 min)

1. **Open JSON Rewriter** dock:
   - Press `Ctrl+Shift+R`
   - Or `View → Docks → JSON Rewriter`

2. **Load the file**:
   - Click "Browse" button
   - Select `config.json`

3. **Configure operation**:
   - Operation: **Deduplicate**
   - Mode: **Keep Last** (newest value wins)
   - ✅ Check "Create Backup"

4. **Execute**:
   - Click **"Run"** or press `F5`
   - Processing takes < 1 second

### Step 4: View Results (30 seconds)

**Original** (with duplicates):
```json
{
  "app": {
    "version": "1.0.0",  ← duplicate
    "version": "1.0.1",  ← kept
    "port": 8080,        ← duplicate
    "port": 3000         ← kept
  }
}
```

**After Deduplication**:
```json
{
  "app": {
    "name": "MyApp",
    "version": "1.0.1",  ← last value kept
    "port": 3000,        ← last value kept
    "debug": true
  },
  "database": {
    "host": "192.168.1.100",  ← last value kept
    "port": 5432
  }
}
```

### Step 5: Save (30 seconds)

1. **Review in Editor**: File automatically updated
2. **Save**: `Ctrl+S` or `File → Save`
3. **Backup available**: `config.json.bak`

**✅ Congratulations!** You've completed your first workflow.

---

## 🚀 More Quick Workflows

### Workflow 2: Search and Replace Across Files (2 min)

**Goal**: Replace "localhost" with "192.168.1.100" in multiple config files.

1. **Open Search/Replace** (`Ctrl+F`)
2. **Configure**:
   - Path: `/path/to/configs/`
   - ✅ Recursive
   - Extensions: `json,yaml,ini`
   - Find: `localhost`
   - Replace: `192.168.1.100`
3. **Execute**: Click "Replace All"
4. **Review**: Results show 15 replacements in 5 files

**Time**: 2 minutes | **Files**: Multiple | **Safety**: Backup created

---

### Workflow 3: Extract Text from JSX Files (3 min)

**Goal**: Extract translatable strings from React components.

1. **Open Text Extractor** (`Ctrl+Shift+T`)
2. **Load JSX file**: `/src/App.jsx`
3. **Configure**:
   - Scope: **Tag content** (text between tags)
   - Extract: ✅ String literals, ✅ Text nodes
4. **Extract**: Click "Extract"
5. **Export**: Save as JSON for i18n

**Output**:
```json
{
  "Welcome to MyApp": "Welcome to MyApp",
  "Click here to get started": "Click here to get started",
  "© 2024 MyApp": "© 2024 MyApp"
}
```

---

### Workflow 4: Set Operations on JSON Files (3 min)

**Goal**: Find differences between two configuration files.

1. **Open Set Operations** (`Ctrl+Shift+S`)
2. **Load files**:
   - File 1: `config-prod.json`
   - File 2: `config-dev.json`
3. **Operation**: Select **Difference (A − B)**
4. **Execute**: Click "Execute"
5. **Result**: Keys present in prod but not in dev

**Use Case**: Identify missing configuration in development environment.

---

### Workflow 5: AI-Powered Refactoring (5 min)

**Goal**: Modernize legacy JavaScript code using AI.

1. **Open AI Processor** (`Ctrl+Shift+A`)
2. **Configure**:
   - Provider: OpenAI or Gemini
   - Model: GPT-4o or Gemini Flash 2.0
   - API Key: Enter your key
3. **Prompt**:
   ```
   Refactor this code to use modern ES6+ syntax:
   - Convert var to let/const
   - Use arrow functions
   - Add JSDoc comments
   ```
4. **Load file**: `legacy.js`
5. **Process**: Click "Process"
6. **Review**: AI response with refactored code

**Time**: 5 minutes | **Cost**: ~$0.01 per file | **Quality**: Professional

---

## 📚 Learn More

### Essential Features

| Feature | Use Case | Shortcut |
|---------|----------|----------|
| **JSON Rewriter** | Clean duplicates, normalize structure | `Ctrl+Shift+R` |
| **Search/Replace** | Find & replace across files | `Ctrl+F` |
| **Set Operations** | Compare files, merge configs | `Ctrl+Shift+S` |
| **AI Processor** | Refactor, translate, analyze | `Ctrl+Shift+A` |
| **Text Extractor** | Extract strings for i18n | `Ctrl+Shift+T` |

### Next Steps

1. **Explore All Features**: [Features Overview](features-overview.md)
2. **Master Shortcuts**: [Keyboard Shortcuts](keyboard-shortcuts.md)
3. **Advanced Usage**: [Performance Tips](advanced/performance.md)
4. **Get Help**: [FAQ](faq.md) | [Troubleshooting](troubleshooting.md)

### Built-in Tutorials

Clarify includes **interactive tutorials**:
- `Help → Tutorials → Quick Start`
- `Help → Tutorials → JSON Rewriter Deep Dive`
- `Help → Tutorials → Search & Replace Mastery`

---

## 💡 Tips for Beginners

1. **Start with Backups**: Always check "Create Backup" when learning
2. **Use Presets**: Try layout presets (`View → Layouts`)
3. **Keyboard Shortcuts**: Learn 5-10 shortcuts to speed up workflow
4. **Experiment Safely**: Work on copies of important files
5. **Read Tooltips**: Hover over buttons for helpful hints

## 🎓 Practice Exercises

Try these to build proficiency:

1. **Exercise 1**: Deduplicate 5 different JSON files
2. **Exercise 2**: Search & replace across a project directory
3. **Exercise 3**: Extract all strings from 10 JSX files
4. **Exercise 4**: Compare two versions of a config file
5. **Exercise 5**: Use AI to document undocumented functions

---

**Ready for more?** [Features Overview →](features-overview.md)
