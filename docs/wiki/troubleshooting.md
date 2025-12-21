# Troubleshooting Guide

Common problems and their solutions. If you encounter an issue not listed here, please [report it](https://github.com/JosueAmaral15/clarify/issues/new?template=bug_report.md).

## 🚨 Installation Issues

### Problem: "python: command not found"
**Symptoms**: Can't run `python main.py`

**Solution**:
1. **Check Python installation**:
   ```bash
   python3 --version  # On Linux/macOS
   python --version   # On Windows
   ```
2. **Install Python 3.12+**: https://www.python.org/downloads/
3. **Add to PATH**: Ensure Python is in system PATH

---

### Problem: "No module named 'PySide6'"
**Symptoms**: ImportError when starting Clarify

**Solution**:
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# If still failing, install directly
pip install PySide6==6.9.3
```

---

### Problem: "ModuleNotFoundError: No module named 'src'"
**Symptoms**: Error when running `python main.py`

**Solution**:
```bash
# Run from project root directory
cd /path/to/clarify

# Ensure you're in correct directory
pwd  # Should show .../clarify

# Run with Python module syntax
python -m src.app

# Or use main.py
python main.py
```

---

## 🖥️ Application Crashes

### Problem: Clarify crashes on startup
**Symptoms**: Window doesn't appear, Python errors in terminal

**Diagnosis**:
1. **Check logs**:
   ```bash
   cat logs/clarify.log  # Linux/macOS
   type logs\clarify.log # Windows
   ```
2. **Look for errors**: Search for "ERROR" or "CRITICAL"

**Common Causes**:
- **Corrupted settings**: Delete `~/.config/Clarify/` and restart
- **Missing dependencies**: Reinstall requirements
- **Python version**: Verify Python 3.12+

**Solution**:
```bash
# 1. Clean settings
rm -rf ~/.config/Clarify/  # Linux/macOS
del %APPDATA%\Clarify      # Windows

# 2. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 3. Run with verbose logging
python main.py --debug
```

---

### Problem: "Segmentation fault" or "Access violation"
**Symptoms**: Immediate crash, no error message

**Solution**:
1. **Update PySide6**:
   ```bash
   pip install --upgrade PySide6
   ```
2. **Check Qt plugins**:
   ```bash
   export QT_DEBUG_PLUGINS=1  # Linux/macOS
   set QT_DEBUG_PLUGINS=1     # Windows
   python main.py
   ```
3. **Use offscreen platform** (headless testing):
   ```bash
   QT_QPA_PLATFORM=offscreen python main.py
   ```

---

## 🐌 Performance Issues

### Problem: Clarify is slow with large files
**Symptoms**: UI freezes, operations take minutes

**Solution**:
1. **Increase thread pool**:
   - `Settings → Performance → Thread Pool Size`
   - Set to CPU count (e.g., 8 for 8-core CPU)

2. **Disable syntax highlighting** for files >50 MB:
   - `Settings → Editor → Syntax Highlighting Threshold`
   - Set to 50 MB

3. **Close unnecessary docks**:
   - `View → Docks` → Uncheck unused docks

4. **Process in batches**:
   - Instead of 1000 files at once, do 100 at a time

**Expected Performance** (i5-8250U, 16GB RAM, SSD):
| File Size | JSON Parsing | Search | Replace |
|-----------|-------------|--------|---------|
| 1 MB | 13 ms | 50 ms | 200 ms |
| 10 MB | 130 ms | 500 ms | 2 s |
| 50 MB | 650 ms | 2.5 s | 10 s |

---

### Problem: High memory usage
**Symptoms**: RAM usage >4 GB, system slow

**Solution**:
1. **Check file sizes**: `Settings → Performance → Max File Size`
   - Default: 100 MB
   - Reduce to 50 MB if memory limited

2. **Enable garbage collection**:
   - `Settings → Performance → Aggressive GC`
   - May slow down but reduces memory

3. **Use CLI for very large operations**:
   ```bash
   python -m src.cli.search --path /huge/dir --find "pattern"
   ```

---

## 🔍 Search & Replace Issues

### Problem: Regex doesn't work
**Symptoms**: Pattern not matching expected files

**Solution**:
1. **Enable regex mode**: Check "Regex" checkbox
2. **Escape special characters**:
   ```
   Wrong: . means any character
   Right: \. means literal dot
   ```
3. **Test regex**: Use https://regex101.com/
4. **Common patterns**:
   ```regex
   \d+          # digits
   [a-z]+       # lowercase letters
   \w+          # word characters
   .*           # anything (greedy)
   .*?          # anything (non-greedy)
   ```

---

### Problem: Replace all replaces too much
**Symptoms**: Unintended replacements

**Solution**:
1. **Use "Preview" first**: See all matches before replacing
2. **Be more specific**:
   ```
   Bad:  Find: "test"
   Good: Find: "test_" (trailing underscore)
   ```
3. **Use whole-word match**: Check "Whole Word" checkbox
4. **Undo if needed**: `Ctrl+Z` or restore from `.bak` file

---

## 📄 JSON Rewriter Problems

### Problem: "Invalid JSON" error
**Symptoms**: Rewriter refuses to process file

**Solution**:
1. **Validate JSON**: Use https://jsonlint.com/
2. **Common issues**:
   - **Trailing commas**: `{"a": 1,}` ← invalid
   - **Unquoted keys**: `{key: "value"}` ← use `{"key": "value"}`
   - **Single quotes**: `{'a': 1}` ← use `{"a": 1}`
3. **Enable "Strict Mode"**: `Settings → JSON → Strict Parsing`
   - If disabled, Clarify attempts to fix minor issues

---

### Problem: Deduplication removes wrong values
**Symptoms**: Wrong duplicate kept

**Solution**:
- **Check mode**:
  - "Keep First": Keeps oldest occurrence
  - "Keep Last": Keeps newest occurrence (default)
- **Example**:
  ```json
  {"key": "old", "key": "new"}
  
  Keep First → {"key": "old"}
  Keep Last  → {"key": "new"}
  ```

---

## 🤖 AI Processor Issues

### Problem: "API key invalid"
**Symptoms**: AI operations fail with authentication error

**Solution**:
1. **Verify key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Gemini: https://aistudio.google.com/apikey
2. **Check key format**:
   - OpenAI: `sk-...` (51 chars)
   - Gemini: `AIza...` (39 chars)
3. **Test key**: Use "Verify Key" button in AI Processor

---

### Problem: "Rate limit exceeded"
**Symptoms**: AI requests fail after several files

**Solution**:
1. **Slow down**: Add delay between files
   - `Settings → AI → Request Delay` (default: 1s)
2. **Upgrade plan**: Check provider's rate limits
3. **Switch model**: Use different model tier

---

### Problem: AI responses are cut off
**Symptoms**: Output incomplete, ends mid-sentence

**Solution**:
- **Increase max tokens**:
  - `AI Processor → Max Output Tokens`
  - GPT-4o: up to 16,384
  - Gemini Flash 2.0: up to 8,192

---

## 🖼️ UI Issues

### Problem: Docks are missing/invisible
**Symptoms**: Can't find a specific dock

**Solution**:
1. **Show dock**: `View → Docks → [Dock Name]`
2. **Reset layout**: `View → Layouts → Standard`
3. **Reset all settings**:
   ```bash
   rm -rf ~/.config/Clarify/  # Deletes all settings
   ```

---

### Problem: Font too small/large
**Symptoms**: Text hard to read

**Solution**:
- **Quick zoom**: `Ctrl+Scroll` (mouse wheel)
- **Settings**: `Settings → Appearance → Font Size`
- **Accessibility**: `Settings → Accessibility → Font Scaling`

---

### Problem: Theme doesn't change
**Symptoms**: Still light/dark after switching

**Solution**:
1. **Restart Clarify**: Some theme changes require restart
2. **Check system theme**: If "System" selected, matches OS
3. **Clear cache**: Delete `~/.cache/clarify/`

---

## 🌐 Network Issues

### Problem: "No internet connection"
**Symptoms**: AI features fail, update checker fails

**Solution**:
1. **Check connection**: `ping google.com`
2. **Check firewall**: Allow Python/Clarify through firewall
3. **Proxy settings**: If behind proxy, configure:
   ```bash
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
   ```

---

## 📊 Testing & Debugging

### Problem: Tests fail
**Symptoms**: `pytest` shows errors

**Solution**:
```bash
# Run with verbose output
pytest tests/ -v

# Run specific test
pytest tests/test_rewriter.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Check test_gui (requires display)
QT_QPA_PLATFORM=offscreen pytest tests/gui/ -v
```

---

### Problem: Need detailed logs
**Symptoms**: Hard to diagnose issue

**Solution**:
```bash
# Enable debug logging
python main.py --debug

# Check log file
tail -f logs/clarify.log  # Live view

# Filter errors only
grep ERROR logs/clarify.log
```

---

## 🔄 Update Problems

### Problem: "Git pull" fails
**Symptoms**: Can't update to latest version

**Solution**:
```bash
# Stash local changes
git stash

# Pull latest
git pull origin main

# Reapply local changes
git stash pop

# If conflicts, reset (WARNING: loses local changes)
git reset --hard origin/main
```

---

## 🆘 Still Need Help?

If your issue isn't listed:

1. **Search Issues**: [GitHub Issues](https://github.com/JosueAmaral15/clarify/issues)
2. **Ask Community**: [GitHub Discussions](https://github.com/JosueAmaral15/clarify/discussions)
3. **Report Bug**: [New Issue](https://github.com/JosueAmaral15/clarify/issues/new?template=bug_report.md)

**When reporting, include**:
- Clarify version: `Help → About`
- OS and Python version
- Steps to reproduce
- Error logs: `logs/clarify.log`
- Screenshots (if UI issue)

---

**Related Guides**:
- [FAQ](faq.md) - Frequently Asked Questions
- [Getting Started](getting-started.md) - Installation guide
- [Features Overview](features-overview.md) - Feature documentation

---

**Last Updated**: December 21, 2024
