# Frequently Asked Questions (FAQ)

Common questions and answers about using Clarify.

## 🚀 Getting Started

### Q: What is Clarify?
**A**: Clarify is an advanced text processing and JSON manipulation system with a modern GUI. It provides 10+ specialized tools for file operations, including search/replace, JSON cleaning, set operations, AI processing, and more.

### Q: Is Clarify free?
**A**: Yes! Clarify is open-source under the MIT License. You can use it freely for personal or commercial projects.

### Q: What platforms does Clarify support?
**A**: Clarify runs on **Windows 10+**, **macOS 10.15+**, and **Linux** (Ubuntu 20.04+, or any distro with Python 3.12+).

### Q: Do I need programming knowledge to use Clarify?
**A**: No. While Clarify is developer-friendly, the GUI is designed for anyone who works with text/JSON files. No coding required for basic operations.

---

## 📦 Installation & Setup

### Q: What are the system requirements?
**A**:
- **Python**: 3.12 or higher
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk**: 500 MB + space for your files
- **Display**: 1280x720 or higher

### Q: How do I install Clarify?
**A**: See the [Getting Started](getting-started.md) guide. Quick version:
```bash
git clone https://github.com/JosueAmaral15/clarify.git
cd clarify
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Q: Can I use pip to install Clarify?
**A**: Not yet, but it's planned! For now, install from source (see above).

### Q: Why does Clarify require Python 3.12+?
**A**: Clarify uses modern Python features like `match` statements, type hints with `|` syntax, and performance improvements from 3.12. These significantly improve code quality and speed.

---

## 🔧 Features & Usage

### Q: What's the difference between JSON Rewriter and Set Operations?
**A**:
- **JSON Rewriter**: Cleans **single files** (deduplicate, format, normalize)
- **Set Operations**: Compares **multiple files** (find differences, intersections, unions)

Use Rewriter for cleaning, Set Operations for comparing.

### Q: Can I process multiple files at once?
**A**: Yes! Most docks support batch processing:
- **Search/Replace**: Recursive directory search
- **JSON Rewriter**: Process entire folder
- **AI Processor**: Batch process 100+ files
- **Set Operations**: Compare 2-10 files

### Q: Does Clarify create backups?
**A**: Yes, when enabled:
- Check **"Create Backup"** option in each dock
- Backup files: `filename.ext.bak`
- Undo function available in some docks

**Tip**: Always enable backups when learning!

### Q: What file types does Clarify support?
**A**:
- **Text**: `.txt`, `.md`, `.log`, `.csv`
- **JSON**: `.json`, `.jsonc` (with comments)
- **Code**: `.js`, `.jsx`, `.ts`, `.tsx`, `.py`, `.java`
- **Web**: `.html`, `.xml`, `.svg`
- **Config**: `.yaml`, `.yml`, `.ini`, `.conf`

Essentially, any text-based file format.

---

## 🤖 AI Features

### Q: Which AI providers are supported?
**A**: Clarify supports 4 providers:
1. **OpenAI** (GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo)
2. **Google Gemini** (Flash 2.0, Pro 2.0, Flash 1.5)
3. **Anthropic Claude** (Opus 4, Sonnet 4, Haiku 4)
4. **Perplexity** (Llama 3.1 70B, Mixtral 8x22B)

### Q: Do I need an API key?
**A**: Yes, for AI features. Get keys from:
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://aistudio.google.com/apikey
- Claude: https://console.anthropic.com/
- Perplexity: https://www.perplexity.ai/settings/api

### Q: How much does AI processing cost?
**A**: Costs vary by provider and model:
- **GPT-4o**: ~$0.01-0.03 per file (depending on size)
- **Gemini Flash 2.0**: ~$0.001-0.005 per file (much cheaper!)
- **Claude Sonnet 4**: ~$0.015-0.05 per file

Clarify shows real-time cost estimates before processing.

### Q: Can I process files without internet?
**A**: AI features require internet (API calls), but all other features work offline:
- ✅ Search/Replace
- ✅ JSON Rewriter
- ✅ Set Operations
- ✅ Text Extractor
- ❌ AI Processor (requires API)

---

## ⚙️ Configuration

### Q: How do I change the theme?
**A**: `Settings → Themes → Light/Dark/System`

### Q: How do I customize keyboard shortcuts?
**A**: `Settings → Keyboard Shortcuts`
- 45+ shortcuts available
- Full customization
- Conflict detection
- Reset to defaults anytime

### Q: Where are my settings stored?
**A**:
- **Linux**: `~/.config/Clarify/`
- **macOS**: `~/Library/Preferences/com.clarify/`
- **Windows**: `%APPDATA%\Clarify\`

### Q: Can I export/import settings?
**A**: Not yet, but planned for v3.0. For now, copy the settings folder.

---

## 🌍 Internationalization

### Q: What languages are supported?
**A**: 7 languages:
- 🇺🇸 English
- 🇧🇷 Português (Brasil)
- 🇪🇸 Español
- 🇫🇷 Français
- 🇩🇪 Deutsch
- 🇨🇳 中文 (简体)
- 🇯🇵 日本語

### Q: How do I change the language?
**A**: `Settings → Language → Choose your language`

Interface updates immediately—no restart needed!

### Q: Can I contribute translations?
**A**: Yes! See [Contributing Guide](../CONTRIBUTING.md#contributing-translations-i18n).

Translation files are simple JSON: `src/i18n/{lang}.json`

---

## 🐛 Troubleshooting

### Q: Clarify won't start. What should I do?
**A**:
1. **Check Python version**: `python --version` (must be 3.12+)
2. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
3. **Check logs**: `logs/clarify.log` for error messages
4. **Run tests**: `pytest tests/ -v` to diagnose issues

### Q: I get "Module not found" errors
**A**: Install missing dependencies:
```bash
pip install PySide6 pytest pytest-qt
```

### Q: Performance is slow with large files
**A**: Tips for better performance:
- Close unnecessary docks
- Disable real-time syntax highlighting for >50 MB files
- Increase thread pool size: `Settings → Performance`
- Use SSD instead of HDD

See [Performance Tips](advanced/performance.md) for details.

### Q: Can Clarify handle files larger than 100 MB?
**A**: Yes, but with limitations:
- **Editor**: Up to 100 MB (syntax highlighting disabled >50 MB)
- **Search/Replace**: Unlimited (processes in chunks)
- **JSON Rewriter**: Up to 50 MB recommended
- **Set Operations**: 10 MB per file recommended

For very large files (>500 MB), consider using CLI tools instead.

---

## 🔐 Security & Privacy

### Q: Does Clarify collect data?
**A**: **No.** Clarify does not collect, store, or transmit any user data, except:
- AI features send files to AI provider APIs (OpenAI, Gemini, etc.)
- You control what is sent (prompt + files)

### Q: Is my API key stored securely?
**A**: API keys are stored in QSettings (OS-encrypted on Windows/macOS). On Linux, consider using a secrets manager.

**Best Practice**: Use environment variables for keys in production.

### Q: Can I use Clarify on confidential files?
**A**: Yes, but:
- **DO**: Use non-AI features (all local processing)
- **DO**: Use self-hosted AI models (future feature)
- **DON'T**: Send confidential data to public AI APIs without permission

---

## 📚 Learning & Support

### Q: Where can I find tutorials?
**A**:
- **Built-in**: `Help → Tutorials` (interactive lessons)
- **Wiki**: [Quick Start Guide](quick-start-guide.md)
- **Docs**: [RECIPES.md](../RECIPES.md) (practical examples)

### Q: How do I report bugs?
**A**: [GitHub Issues](https://github.com/JosueAmaral15/clarify/issues/new?template=bug_report.md)

Please include:
- Clarify version
- OS and Python version
- Steps to reproduce
- Error logs (`logs/clarify.log`)

### Q: Can I request features?
**A**: Yes! [Feature Request Template](https://github.com/JosueAmaral15/clarify/issues/new?template=feature_request.md)

### Q: How can I contribute?
**A**: See [Contributing Guide](../CONTRIBUTING.md). Options:
- **Code**: Fix bugs, add features
- **Translations**: Improve i18n
- **Documentation**: Write guides, fix typos
- **Testing**: Report bugs, test new features

---

## 🚀 Advanced Topics

### Q: Can I automate Clarify with scripts?
**A**: Yes! Clarify has a CLI for most operations:
```bash
# Example: JSON Rewriter
python -m src.rewriter.cli deduplicate input.json --output output.json

# Example: Search/Replace
python -m src.cli.search --path /data --find "old" --replace "new"
```

See CLI help: `python -m src.cli --help`

### Q: Can I create custom docks/plugins?
**A**: Plugin system is planned for v3.0. For now, you can:
- Fork the repo
- Add custom docks in `src/gui/`
- Integrate with `src/app.py`

See [Plugin Development](advanced/plugins.md) (draft).

### Q: Is there a REST API?
**A**: Experimental REST API exists (`src/rest_api.py`) but is disabled by default. Enable in `Settings → Advanced → REST API`.

**Warning**: API is unstable and may change significantly.

---

## 📖 More Resources

- [Wiki Home](README.md)
- [Getting Started](getting-started.md)
- [Quick Start Guide](quick-start-guide.md)
- [Features Overview](features-overview.md)
- [Troubleshooting](troubleshooting.md)
- [Keyboard Shortcuts](keyboard-shortcuts.md)

---

**Can't find your question?** Ask in [GitHub Discussions](https://github.com/JosueAmaral15/clarify/discussions)!
