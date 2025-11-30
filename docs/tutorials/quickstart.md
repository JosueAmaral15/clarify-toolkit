# Quick Start Guide

Welcome to **Clarify**! This guide will help you get started in 5 minutes.

---

## 🎯 What is Clarify?

Clarify is a professional desktop application for:
- **JSON Translation**: Extract text from code → Generate i18n JSON files
- **Search & Replace**: Batch find/replace across multiple files with regex
- **JSON Rewriting**: Transform, clean, and deduplicate JSON structures
- **Case Conversion**: Convert between camelCase, PascalCase, snake_case, kebab-case
- **AI Processing**: Process files with ChatGPT or Gemini AI

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- PySide6 (Qt for Python)

### Install
```bash
pip install -r requirements.txt
python main.py
```

---

## 📋 First Steps

### 1. Open Clarify
Launch the application:
```bash
python main.py
```

### 2. Choose a Tool
Clarify has 5 main tools accessible via **Tools** menu:

| Tool | Purpose | Best For |
|------|---------|----------|
| **JSON Translate** | Extract text → i18n JSON | React/Vue internationalization |
| **Search & Replace** | Find/replace across files | Refactoring, bulk updates |
| **JSON Rewriter** | Transform JSON structures | Cleaning data, deduplication |
| **Case Converter** | Change naming conventions | Code style consistency |
| **AI File Processor** | Process with ChatGPT/Gemini | Documentation, code analysis |

### 3. Try JSON Translate (Example)

**Goal**: Extract `"Hello World"` from code → Generate JSON

1. **Open** Tools → Open JSON Translate
2. **Input Path**: Select your `.tsx` or `.js` file
3. **Output Path**: Choose where to save JSON
4. **Root Variable**: Enter `t` (default)
5. **Click**: "Process" button
6. **Result**: JSON file with extracted translations

**Before:**
```tsx
<h1>Hello World</h1>
<p>Welcome to our app</p>
```

**After (JSON):**
```json
{
  "t": {
    "hello_world": "Hello World",
    "welcome_to_our_app": "Welcome to our app"
  }
}
```

---

## 🎓 Next Steps

### Beginner Tutorials
Start with these step-by-step guides:

1. [JSON Translate Tutorial](beginner/basic/01-json-translate.md) - 10 min
2. [Search & Replace Tutorial](beginner/basic/02-search-replace.md) - 15 min
3. [JSON Rewriter Tutorial](beginner/basic/03-json-rewriter.md) - 12 min

### Advanced Features
- **Advanced Conditions**: Filter files by size, date, regex patterns
- **Scope Filtering**: Process only text inside `<div>` tags, `{...}` blocks, etc.
- **Batch Processing**: Process entire directories recursively
- **Undo/Redo**: Command pattern with Ctrl+Z/Ctrl+Y (10 levels)

---

## 💡 Tips & Tricks

### Keyboard Shortcuts
- `Ctrl+Z` / `Ctrl+Y`: Undo / Redo
- `Ctrl+Shift+F`: Advanced File Search
- `Ctrl+S`: Save results
- `Ctrl+Q`: Quit application

### Common Workflows

**Workflow 1: Internationalize React App**
1. JSON Translate: Extract text from `.tsx` files → `en.json`
2. Translate `en.json` → `pt.json` (manually or with AI)
3. Search & Replace: Replace hardcoded strings with `{t.key.path}`

**Workflow 2: Clean Messy JSON**
1. JSON Rewriter: Load messy JSON with duplicates
2. Enable: "Eliminate Duplicates" + "Remove Empty Values"
3. Apply: "Consistent Case" (camelCase)
4. Save: Clean JSON output

**Workflow 3: Bulk Rename Variables**
1. Case Converter: Load `.ts` files
2. Select: snake_case → camelCase
3. Process: All variables renamed automatically

---

## ❓ Need Help?

### Built-in AI Assistant
- **Menu**: Help → AI Assistant
- Ask questions like:
  - "How do I use regex in Search & Replace?"
  - "What's the difference between dedupe and join_keys?"
  - "Show me an example of scope filtering"

### Tutorials
Browse all tutorials: [Tutorial Index](README.md)

### Documentation
- [Full Documentation](../TASKS.md)
- [GitHub Repository](https://github.com/JosueAmaral15/clarify)
- [Report Issues](https://github.com/JosueAmaral15/clarify/issues)

---

## 🎉 You're Ready!

You now know the basics of Clarify. Explore the tutorials to master advanced features!

**Happy processing!** 🚀

---

**Last Updated**: November 30, 2025  
**Author**: Josué Amaral
