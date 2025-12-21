# Contributing to Clarify

Thank you for your interest in contributing to Clarify! 🎉

This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Report Bugs](#how-to-report-bugs)
3. [How to Suggest Features](#how-to-suggest-features)
4. [Development Setup](#development-setup)
5. [Contributing Translations (i18n)](#contributing-translations-i18n)
6. [Code Style Guidelines](#code-style-guidelines)
7. [Testing Requirements](#testing-requirements)
8. [Pull Request Process](#pull-request-process)

---

## 🤝 Code of Conduct

Be respectful, inclusive, and constructive. We welcome contributions from everyone regardless of experience level.

---

## 🐛 How to Report Bugs

1. **Check existing issues**: Search [GitHub Issues](https://github.com/JosueAmaral15/clarify/issues) to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Include**:
   - Clarify version (`Help → About`)
   - Operating System (Windows/Linux/macOS)
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Log files from `logs/clarify.log` (if relevant)

---

## 💡 How to Suggest Features

1. **Check existing feature requests** in [GitHub Issues](https://github.com/JosueAmaral15/clarify/issues)
2. **Use the feature request template**
3. **Describe**:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions you've considered
   - Why this feature would benefit Clarify users

---

## 🛠️ Development Setup

### Prerequisites

- **Python 3.12+** (required)
- **PySide6** (Qt for Python)
- **pytest** (for testing)

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/JosueAmaral15/clarify.git
cd clarify

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-qt pytest-cov pytest-timeout black isort pylint psutil

# 5. Run Clarify
python -m src.app
```

### Project Structure

```
clarify/
├── src/                  # Source code
│   ├── gui/             # GUI components (docks, dialogs)
│   ├── i18n/            # Translations (EN, PT-BR, ES, FR, DE, ZH, JA)
│   ├── rewriter/        # JSON Rewriter operations
│   ├── json_search/     # JSON Search engine
│   ├── set_operations.py # Set operations (∩, ∪, −, ⊕)
│   └── app.py           # Main application
├── tests/               # Unit tests
├── docs/                # Documentation
│   ├── TASKS.md         # Project backlog (MoSCoW)
│   ├── tutorials/       # User tutorials
│   └── protocolos/      # Development protocols
├── CHANGELOG.md         # Release notes
└── README.md            # Project overview
```

---

## 🌍 Contributing Translations (i18n)

Clarify supports **7 languages**:
- 🇺🇸 **English (en)** - Complete
- 🇧🇷 **Português Brasil (pt_BR)** - Complete
- 🇪🇸 **Español (es)** - Needs review
- 🇫🇷 **Français (fr)** - Needs review
- 🇩🇪 **Deutsch (de)** - Needs review
- 🇨🇳 **中文 简体 (zh)** - Needs review
- 🇯🇵 **日本語 (ja)** - Needs review

### Translation Files

All translations are in **JSON format** under `src/i18n/`:

```
src/i18n/
├── en.json       # English (reference)
├── pt_BR.json    # Portuguese (Brazil)
├── es.json       # Spanish
├── fr.json       # French
├── de.json       # German
├── zh.json       # Chinese (Simplified)
└── ja.json       # Japanese
```

### How to Contribute Translations

#### Option 1: Edit Directly on GitHub (Easiest)

1. Go to `src/i18n/` folder on GitHub
2. Click on the language file you want to improve (e.g., `es.json`)
3. Click the **pencil icon** (Edit this file)
4. Make your changes
5. Submit a Pull Request with description: "Improve ES translations"

#### Option 2: Fork & Pull Request (Recommended for multiple changes)

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/clarify.git
cd clarify

# 3. Create a branch for translations
git checkout -b improve-translations-es

# 4. Edit the translation file
nano src/i18n/es.json  # or use your favorite editor

# 5. Commit changes
git add src/i18n/es.json
git commit -m "feat(i18n): improve Spanish translations for menu items"

# 6. Push to your fork
git push origin improve-translations-es

# 7. Open a Pull Request on GitHub
```

### Translation File Format

```json
{
  "_comment": "Spanish (ES) translation for Clarify",
  "_translators": [
    "Your Name <email@example.com>"
  ],
  "app.title": "Clarify - Sistema de gestión de archivos JSON",
  "menu.file": "Archivo",
  "menu.file.exit": "Salir",
  "search.path": "Ruta",
  "search.browse": "Examinar..."
}
```

**Key Naming Convention**:
- `menu.file` → Menu bar items
- `menu.tools.json_translate` → Nested menu items
- `search.path` → UI labels
- `dialog.ok` → Dialog buttons
- `shortcuts.action.save` → Keyboard shortcut descriptions

### Translation Guidelines

1. **Keep key structure**: Do NOT change keys (e.g., `"menu.file"`), only values (e.g., `"Archivo"`)
2. **Preserve formatting**: Keep `...`, placeholders like `{0}`, and special characters
3. **Context matters**: Some terms have different translations depending on context
4. **Use native terminology**: 
   - Technical terms: Keep as-is (JSON, GUI, API) or use accepted translation
   - UI conventions: Follow OS standards (File → Archivo, Edit → Editar)
5. **Test your changes**: Run Clarify and switch to your language to verify

### Adding a New Language

To add a new language (e.g., Italian - `it`):

1. **Copy `en.json`** as starting point:
   ```bash
   cp src/i18n/en.json src/i18n/it.json
   ```

2. **Translate all strings** in `it.json`

3. **Register language in `translator.py`**:
   ```python
   # Line ~50
   self._available_languages = ["en", "pt_BR", "es", "fr", "de", "zh", "ja", "it"]
   
   # Line ~150
   def get_language_name(self, lang: str) -> str:
       names = {
           "en": "English",
           "pt_BR": "Português (Brasil)",
           "es": "Español",
           "fr": "Français",
           "de": "Deutsch",
           "zh": "中文 (简体)",
           "ja": "日本語",
           "it": "Italiano"  # Add this
       }
   ```

4. **Add menu item in `app.py`** (search for "Language submenu"):
   ```python
   self.act_lang_it = QAction("Italiano", self, checkable=True)
   m_language.addAction(self.act_lang_it)
   self.act_lang_it.triggered.connect(lambda: self._switch_language("it"))
   ```

5. **Test**: Run Clarify, go to `Settings → Language → Italiano`

6. **Submit PR** with title: `feat(i18n): add Italian (it) translations`

---

## 📐 Development Protocols

**Clarify uses structured development protocols** to ensure code quality and prevent common errors.

### Available Protocols

1. **Simplicidade 1** (`docs/protocolos/PROTOCOLO_SIMPLICIDADE_1.md`) - v2.0
   - **For**: Solo developers, prototyping, internal non-critical projects
   - **Features**: Fast iteration, minimal overhead
   - **Steps**: 9 mandatory steps (requirements → testing → rollback)

2. **Simplicidade 2** (`docs/protocolos/PROTOCOLO_SIMPLICIDADE_2.md`) - v2.2
   - **For**: Teams (3+ developers), production systems requiring compliance
   - **Features**: Code review, retrospectives, ADR, accessibility, API docs
   - **Steps**: 16 mandatory + 3 optional steps
   - **Overhead**: 4-6h per task (justified by quality gains)

3. **Simplicidade 3** (`docs/protocolos/PROTOCOLO_SIMPLICIDADE_3.md`) - v3.1 ⭐
   - **For**: Solo developer in production (most Clarify contributions)
   - **Features**: Hybrid approach, AI suggestions, security without bureaucracy
   - **Steps**: 16 mandatory + 3 optional steps
   - **AI Integration**: Optional AI suggestions in Step 3 (questions to developer)

### When to Use Each Protocol

| Protocol | Best For | Example Scenarios |
|----------|----------|------------------|
| **Simplicidade 1** | Solo dev, non-critical | Personal scripts, POC, learning |
| **Simplicidade 2** | Teams, compliance | Enterprise, regulated industries, large codebases |
| **Simplicidade 3** | Solo dev, production | Open-source projects like Clarify ✅ |

### Critical Protocol Rules (Simplicidade 3 - Step 9.1)

**MANDATORY for GUI tests** (prevents infinite loops):

1. ✅ `@pytest.mark.timeout(5)` on EVERY test function
2. ✅ `QT_QPA_PLATFORM=offscreen` environment variable
3. ✅ Dry-run first: `pytest --collect-only`
4. ✅ Shell timeout: `timeout 30s pytest ...`
5. ✅ NO complex workflows (only instantiation)
6. ✅ NO I/O operations in tests
7. ✅ NO signal triggering

**Why**: These rules prevented a **critical infinite loop error** in v2.9.53 that wasted hours of development time.

---

## 🎨 Code Style Guidelines

### Python Style

We follow **PEP 8** with some adjustments:

- **Formatter**: Use `black` (line length: 100)
- **Import sorting**: Use `isort`
- **Linter**: Maintain **Pylint score > 9.0/10**

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
pylint src/ --rcfile=.pylintrc
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `JsonRewriterDock`, `Translator`)
- **Functions/Methods**: `snake_case` (e.g., `get_translator()`, `_load_language()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_FILE_SIZE`, `DEFAULT_TIMEOUT`)
- **Private methods**: Prefix with `_` (e.g., `_load_language()`)

### Documentation

- **Docstrings**: Use Google style for all public methods
  ```python
  def switch_language(self, lang: str) -> None:
      """
      Switch to a different language at runtime.
      
      Args:
          lang: Language code ('en', 'pt_BR', 'es', etc.)
      
      Raises:
          ValueError: If language not supported
      """
  ```

- **Type hints**: Required for all function signatures
  ```python
  def get(self, key: str, default: Optional[str] = None) -> str:
  ```

---

## ✅ Testing Requirements

### Test Categories

Clarify has **3 types of QA tests** (as of v2.9.53):

1. **GUI Safety Tests** (`tests/test_gui_safety_basic.py`)
   - 5 tests, instantiation only
   - MUST follow Protocol Simplicidade 3 - Step 9.1 (timeout protection)
   - Example: `test_set_operations_dock_instantiation`

2. **Performance Benchmarks** (`tests/test_performance_benchmarks.py`)
   - 14 tests, baseline metrics established
   - Parsing: 75-90 MB/s (stdlib), 32-38 MB/s (rewriter)
   - Write: 11-16 MB/s (bottleneck)
   - Search: 5-6M items/s

3. **Load Tests** (`tests/test_load_testing.py`)
   - 4 tests, stress & scale validation
   - 1000+ files: 12.3k files/s
   - 1GB+ corpus: 16.26 MB/s, memory peak <500 MB
   - System validated up to 2-3 GB with 1 GB RAM

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest tests/test_gui_safety_basic.py           # GUI tests
pytest tests/test_performance_benchmarks.py     # Performance
pytest tests/test_load_testing.py               # Load tests

# Run GUI tests SAFELY (with timeout protection)
QT_QPA_PLATFORM=offscreen timeout 30s pytest tests/test_gui_safety_basic.py -v

# Run with verbose output
pytest -v
```

### Test Coverage

- **Minimum coverage**: 90% for core modules (`src/set_operations.py`, `src/rewriter/`, `src/json_search/`)
- **Coverage report**: Generated in `htmlcov/index.html`
- **Current status**: 23 QA tests, 100% passing (v2.9.53)

### Writing Tests

- **Location**: `tests/test_{module_name}.py`
- **Framework**: `pytest` + `pytest-qt` (for GUI)
- **Style**: Use descriptive test names

```python
def test_translator_switch_language_updates_current():
    """Test that switch_language() updates current_language property."""
    translator = Translator()
    translator.switch_language("es")
    assert translator.current_language == "es"
```

**For GUI tests**, ALWAYS follow Protocol Simplicidade 3 - Step 9.1:

```python
import pytest

@pytest.mark.timeout(5)  # CRITICAL: Individual timeout
def test_my_dock_instantiation(qtbot):
    """Test safe instantiation of MyDock."""
    from src.gui.my_dock import MyDock
    
    dock = MyDock()
    qtbot.addWidget(dock)  # Ensures cleanup
    
    # NO heavy operations - just basic assertions
    assert dock.windowTitle() == "My Dock"
    assert dock.isVisible() is False
```

### Performance Requirements

When modifying core operations, ensure performance doesn't degrade:

| Operation | Baseline (v2.9.53) | Acceptable Range |
|-----------|-------------------|------------------|
| **JSON Parsing (stdlib)** | 75-90 MB/s | >70 MB/s |
| **Rewriter Parsing** | 32-38 MB/s | >30 MB/s |
| **JSON Search** | 5-6M items/s | >4M items/s |
| **JSON Write** | 11-16 MB/s | >10 MB/s |
| **Memory Peak (1GB corpus)** | <500 MB | <600 MB |

**Run benchmarks before submitting PR**:
```bash
pytest tests/test_performance_benchmarks.py -v
```

If throughput drops >10%, explain why in PR description.

---

## 🔄 Pull Request Process

### Before Submitting

1. **Create a branch**: `git checkout -b feature/my-awesome-feature`
2. **Follow code style**: Run `black`, `isort`, `pylint`
3. **Write tests**: Add tests for new functionality
4. **Run tests**: Ensure all tests pass (`pytest`)
5. **Update docs**: Modify `CHANGELOG.md` (Unreleased section) and `TASKS.md` if applicable
6. **Commit messages**: Use [Conventional Commits](https://www.conventionalcommits.org/)
   - `feat(i18n): add Spanish translations`
   - `fix(rewriter): prevent data loss on empty values`
   - `docs(readme): update installation instructions`
   - `test(search): add unit tests for regex queries`

### PR Template

When opening a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Translation improvement
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added (if applicable)
- [ ] Manually tested on [OS]

## Checklist
- [ ] Code follows style guidelines (black, pylint >9.0)
- [ ] Followed appropriate protocol (Simplicidade 1/2/3)
- [ ] Docstrings added/updated
- [ ] Tests added/updated (if applicable)
- [ ] Performance benchmarks run (if core changes)
- [ ] GUI tests follow Protocol 9.1 (timeout protection)
- [ ] CHANGELOG.md updated
- [ ] Screenshots added (if UI change)
```

### Review Process

1. **Maintainer review**: May take 1-7 days
2. **CI checks**: GitHub Actions will run tests automatically
3. **Feedback**: Address review comments
4. **Merge**: Once approved, maintainer will merge

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code restructuring without behavior change
- `test`: Adding/updating tests
- `chore`: Maintenance tasks (dependencies, build config)

**Examples:**
```
feat(ai-processor): add Gemini Flash 2.0 model support

Integrates Google's new Gemini Flash 2.0 model with improved
context window (1M tokens) and faster response times.

Closes #234
```

```
fix(rewriter): prevent data loss with nested objects

Fixed critical bug where nested objects were incorrectly
flattened during deduplication process.

Fixes #189
```

---

## 📝 Changelog Automation

Clarify uses **automated changelog generation** from git commits following Conventional Commits format.

### Using the Changelog Script

**Generate changelog for unreleased commits:**
```bash
# Automatic mode (since last CHANGELOG.md update)
python scripts/generate_changelog.py --auto-since

# Manual mode (last 20 commits)
python scripts/generate_changelog.py

# Since specific commit/tag
python scripts/generate_changelog.py --since="c3f5782"

# For new version release
python scripts/generate_changelog.py --auto-since --version="2.9.86"
```

**Script Features:**
- ✅ Parses Conventional Commits (feat, fix, docs, refactor, test, chore, perf, style)
- ✅ Groups by commit type with emojis (✨ Features, 🐛 Bug Fixes, etc.)
- ✅ Includes commit hash, scope, and body
- ✅ Auto-inserts at top of CHANGELOG.md
- ✅ Supports custom version and output file

**Best Practices:**
1. Write clear, descriptive commit messages following Conventional Commits
2. Use `--auto-since` for releases to include all commits since last changelog update
3. Review generated output before committing
4. Include breaking changes in commit footer: `BREAKING CHANGE: ...`

**Example Workflow:**
```bash
# 1. Make changes and commit with conventional format
git add .
git commit -m "feat(layout): add custom layout presets"

# 2. Generate changelog before release
python scripts/generate_changelog.py --auto-since --version="2.9.86"

# 3. Review CHANGELOG.md
git diff CHANGELOG.md

# 4. Commit changelog
git add CHANGELOG.md
git commit -m "docs(changelog): add v2.9.86 release notes"
```

**Alternative: git-cliff**

For advanced users, `cliff.toml` configuration is provided for [git-cliff](https://git-cliff.org/):

```bash
# Install git-cliff (optional)
cargo install git-cliff

# Generate changelog
git-cliff --output CHANGELOG.md

# For specific range
git-cliff --tag 2.9.86 v2.9.85..HEAD
```

---

## 🙏 Thank You!

Your contributions make Clarify better for everyone. We appreciate your time and effort! 🚀

**Questions?** Open a [Discussion](https://github.com/JosueAmaral15/clarify/discussions) or reach out via [Issues](https://github.com/JosueAmaral15/clarify/issues).

---

**License**: Clarify is open-source under the [MIT License](LICENSE).
