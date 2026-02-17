# 📁 Clarify - Project Root Organization

## 📂 Root Structure

```
clarify/
├── 📄 Core Files
│   ├── README.md                  # Project introduction
│   ├── CHANGELOG.md               # Version history
│   ├── CONTRIBUTING.md            # Contribution guide
│   ├── PROJECT_STRUCTURE.md       # Architecture overview
│   ├── SECURITY.md                # Security policy
│   ├── pyproject.toml             # Project configuration
│   ├── poetry.lock                # Dependency lock
│   └── requirements-docs.txt      # Docs dependencies
│
├── 🔧 Configuration
│   ├── .gitignore                 # Git ignore rules
│   ├── .pylintrc                  # Pylint config
│   ├── .coveragerc                # Coverage config
│   ├── .pre-commit-config.yaml    # Pre-commit hooks
│   ├── cliff.toml                 # Changelog generator
│   └── config/                    # Runtime configs
│       └── examples/              # Config examples
│
├── 🚀 Launchers
│   ├── main.py                    # Main entry point
│   ├── launchers/                 # Platform-specific launchers
│   │   ├── clarify.py            # CLI launcher
│   │   ├── clarify_gui.sh        # Linux GUI launcher
│   │   └── clarify_gui.bat       # Windows GUI launcher
│
├── 📦 Source Code
│   └── src/                       # Application source code
│       ├── core/                  # Business logic
│       ├── gui/                   # PySide6 GUI
│       ├── cli/                   # Command-line interface
│       ├── plugins/               # Plugin system
│       ├── converters/            # Format converters
│       ├── translators/           # Translation engines
│       ├── extractors/            # Text/JSX extractors
│       ├── i18n/                  # Internationalization
│       └── utils/                 # Utilities
│
├── 🧪 Testing
│   └── tests/                     # Test suite (94 test files)
│
├── 📚 Documentation
│   └── docs/                      # Comprehensive docs
│       ├── INDEX.md              # Documentation index
│       ├── guides/               # User guides
│       ├── architecture/         # Architecture docs
│       ├── specifications/       # Feature specs
│       ├── releases/             # Release notes
│       ├── processes/            # Dev processes
│       └── tutorials/            # Step-by-step tutorials
│
├── 🔌 Plugins
│   └── plugins/                   # External plugins
│       ├── export_to_postgresql/
│       └── slack_notifications/
│
├── 🛠️ Scripts
│   └── scripts/                   # Automation scripts
│       ├── generate_changelog.py
│       └── automation/           # CI/CD scripts
│
├── 🎨 Assets
│   ├── assets/                    # Images, icons
│   ├── beeps/                     # Sound effects
│   └── benchmarks/                # Performance benchmarks
│
├── 🧪 Testing & Quality
│   ├── load_tests/                # Load testing
│   └── .github/                   # GitHub Actions
│       ├── workflows/
│       └── ISSUE_TEMPLATE/
│
└── 🗄️ Archive
    └── .archive/                  # Deprecated/old files
        ├── REVIEW.md
        ├── old_archive/
        └── protocolos_simplicidade.zip
```

---

## 🎯 Quick Navigation

### 👨‍💻 For Developers
- **Start here**: [README.md](README.md)
- **Project structure**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentation**: [docs/INDEX.md](docs/INDEX.md)
- **Architecture**: [docs/architecture/](docs/architecture/)

### 📖 For Users
- **Installation**: [README.md#installation](README.md)
- **User guides**: [docs/guides/](docs/guides/)
- **Tutorials**: [docs/tutorials/](docs/tutorials/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

### 🔧 For Contributors
- **Setup**: [CONTRIBUTING.md#setup](CONTRIBUTING.md)
- **Testing**: [tests/](tests/)
- **CI/CD**: [.github/workflows/](.github/workflows/)
- **Code style**: [.pylintrc](.pylintrc), [.pre-commit-config.yaml](.pre-commit-config.yaml)

---

## 📋 File Locations Reference

### Configuration Files
| File | Location | Purpose |
|------|----------|---------|
| `pyproject.toml` | Root | Project metadata, dependencies |
| `poetry.lock` | Root | Locked dependencies |
| `cliff.toml` | Root | Changelog generation |
| `.pylintrc` | Root | Linting rules |
| `.coveragerc` | Root | Test coverage config |
| `config/` | Root | Runtime configurations |

### Entry Points
| File | Location | Purpose |
|------|----------|---------|
| `main.py` | Root | Main entry point |
| `clarify.py` | `launchers/` | CLI launcher |
| `clarify_gui.sh` | `launchers/` | Linux GUI |
| `clarify_gui.bat` | `launchers/` | Windows GUI |

### Documentation
| Document | Location | Purpose |
|----------|----------|---------|
| `INDEX.md` | `docs/` | Documentation index |
| `PROJECT_SUMMARY.md` | `docs/` | Executive summary |
| Feature specs | `docs/specifications/` | Feature documentation |
| Guides | `docs/guides/` | User guides |
| Release notes | `docs/releases/` | Version releases |

---

## 🗂️ Organization Principles

### Root Directory
**Keep Clean**: Only essential configuration files and entry points

✅ **Allowed**:
- Project metadata (pyproject.toml, README.md)
- Entry points (main.py)
- CI/CD configs (.github/, .pylintrc)
- Essential configs (.gitignore, .pre-commit-config.yaml)

❌ **Not Allowed**:
- Temporary files (moved to .archive/)
- Obsolete documentation (moved to .archive/)
- Data files (should be in data/ or tests/)

### Documentation (docs/)
**Organized by Type**:
- `guides/` - How-to guides
- `specifications/` - Feature specs (organized by version)
- `releases/` - Release notes and reports
- `processes/` - Development processes
- `tutorials/` - Step-by-step tutorials

### Source Code (src/)
**Modular Structure**:
- Each module has clear responsibility
- Plugin system for extensibility
- Converters follow Strategy pattern
- GUI components are reusable

### Tests (tests/)
**Comprehensive Coverage**:
- Unit tests for core logic
- Integration tests for workflows
- Performance tests in load_tests/
- 97% code coverage

---

## 🔍 Finding Files

### By Category
```bash
# Documentation
ls docs/INDEX.md                    # Start here
ls docs/guides/                     # User guides
ls docs/specifications/v2.9/        # v2.9 specs

# Configuration
ls *.toml *.yaml *.rc               # Config files
ls config/examples/                 # Config examples

# Source code
ls src/*/                           # All modules
ls src/gui/panels/                  # GUI panels

# Tests
ls tests/test_*.py                  # All tests
ls tests/test_regex_insert.py      # Specific test
```

### By Version
```bash
# v2.9 specs
ls docs/specifications/v2.9/

# v2.10 planning
ls docs/specifications/v2.10/

# Release notes
ls docs/releases/
```

---

## 🧹 Maintenance

### Archive Policy
Files moved to `.archive/` when:
- No longer needed (obsolete)
- Superseded by newer version
- Historical reference only

### Cleanup Commands
```bash
# Remove temporary files
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete
find . -name ".pytest_cache" -type d -delete

# Remove coverage artifacts
rm -rf htmlcov/ .coverage

# Clean build artifacts
rm -rf dist/ build/ *.egg-info/
```

---

## 📝 Notes

### Recent Changes (2025-12-23)
- ✅ Removed temporary file `=3.1.0` (pip install artifact)
- ✅ Organized `docs/` into categorical folders
- ✅ Moved obsolete files to `.archive/`
- ✅ Created documentation index
- ✅ Structured specifications by version

### Directory Standards
- Use `kebab-case` for folders and files
- Markdown files: `.md` extension
- Python modules: `snake_case`
- Classes: `PascalCase`

---

**Version**: 2.9.111  
**Last Updated**: 2025-12-23  
**Maintained by**: Josue Amaral
