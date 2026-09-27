# Clarify - GUI Launchers

This directory contains convenient launcher scripts for starting Clarify in GUI mode.

## 🪟 Windows

**File**: `clarify.bat` (root launcher)

**Usage**:
- Double-click `clarify.bat` in Windows Explorer
- Or run from Command Prompt: `clarify.bat`

**Features**:
- ✅ Automatically checks Python installation
- ✅ Verifies PySide6 dependency
- ✅ Offers to install PySide6 if missing
- ✅ Shows error messages if something goes wrong
- ✅ Pauses on error for troubleshooting

## 🐧 Linux / 🍎 macOS

**File**: `clarify.sh` (Linux/Unix root launcher) or `clarify.command` (macOS root launcher)

**First-time setup**:
```bash
chmod +x clarify.sh clarify.command
```

**Usage**:
- Double-click `clarify.sh` or `clarify.command` in the file manager (may need to allow execution)
- Or run from terminal: `./clarify.sh` or `./clarify.command`

**Features**:
- ✅ Automatically checks Python 3 installation
- ✅ Verifies PySide6 dependency
- ✅ Offers to install PySide6 if missing
- ✅ Shows error messages if something goes wrong
- ✅ Pauses on error for troubleshooting

## 📝 What They Do

Both scripts:
1. Check if Python is installed
2. Display Python version
3. Check if PySide6 (GUI library) is installed
4. Offer to install PySide6 if missing
5. Launch `python -m src` (GUI mode)
6. Show any errors that occur

## ⚠️ Requirements

- **Python 3.12+** must be installed
- **PySide6** is required for GUI. Prefer installing the project with `poetry install` or `python -m pip install -e .`.

## 🔧 Troubleshooting

### Windows
- If double-click doesn't work, right-click → "Run as administrator"
- If Python not found, add Python to PATH during installation
- Check Python: Open CMD and type `python --version`

### Linux/macOS
- If "Permission denied", run: `chmod +x clarify.sh clarify.command`
- If Python not found, install: `sudo apt install python3` (Ubuntu/Debian)
- Check Python: `python3 --version`

### PySide6 Installation Failed
Manual installation:
```bash
# Using Poetry (recommended)
poetry install

# Without Poetry
python -m pip install -e .

# Last-resort direct GUI dependency install
python -m pip install PySide6
```

## 💡 Alternative Methods

You can also launch Clarify GUI without these scripts:

```bash
# Direct Python execution
python -m src

# As a module
python -m src

# Using Poetry
poetry run python -m src
```

## 📚 More Information

See the root [README.md](../../README.md) and [CURRENT_STATE.md](../CURRENT_STATE.md) for current operational guidance.
