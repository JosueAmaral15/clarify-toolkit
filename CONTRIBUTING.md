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
pip install pytest pytest-qt pytest-cov black isort pylint

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

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_translator.py

# Run with verbose output
pytest -v
```

### Test Coverage

- **Minimum coverage**: 90% for core modules (`src/set_operations.py`, `src/rewriter/`, `src/json_search/`)
- **Coverage report**: Generated in `htmlcov/index.html`

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
- [ ] Docstrings added/updated
- [ ] CHANGELOG.md updated
- [ ] Screenshots added (if UI change)
```

### Review Process

1. **Maintainer review**: May take 1-7 days
2. **CI checks**: GitHub Actions will run tests automatically
3. **Feedback**: Address review comments
4. **Merge**: Once approved, maintainer will merge

---

## 🙏 Thank You!

Your contributions make Clarify better for everyone. We appreciate your time and effort! 🚀

**Questions?** Open a [Discussion](https://github.com/JosueAmaral15/clarify/discussions) or reach out via [Issues](https://github.com/JosueAmaral15/clarify/issues).

---

**License**: Clarify is open-source under the [MIT License](LICENSE).
