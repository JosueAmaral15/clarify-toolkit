# Clarify - GUI Launchers

This directory contains convenient launcher scripts for starting Clarify in GUI mode.

## 🪟 Windows

**File**: `clarify_gui.bat`

**Usage**:
- Double-click `clarify_gui.bat` in Windows Explorer
- Or run from Command Prompt: `clarify_gui.bat`

**Features**:
- ✅ Automatically checks Python installation
- ✅ Verifies PySide6 dependency
- ✅ Offers to install PySide6 if missing
- ✅ Shows error messages if something goes wrong
- ✅ Pauses on error for troubleshooting

## 🐧 Linux / 🍎 macOS

**File**: `clarify_gui.sh`

**First-time setup**:
```bash
chmod +x clarify_gui.sh
```

**Usage**:
- Double-click `clarify_gui.sh` in file manager (may need to allow execution)
- Or run from terminal: `./clarify_gui.sh`

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
5. Launch `python clarify.py` (GUI mode)
6. Show any errors that occur

## ⚠️ Requirements

- **Python 3.10+** must be installed
- **PySide6** required for GUI (scripts can install it)

## 🔧 Troubleshooting

### Windows
- If double-click doesn't work, right-click → "Run as administrator"
- If Python not found, add Python to PATH during installation
- Check Python: Open CMD and type `python --version`

### Linux/macOS
- If "Permission denied", run: `chmod +x clarify_gui.sh`
- If Python not found, install: `sudo apt install python3` (Ubuntu/Debian)
- Check Python: `python3 --version`

### PySide6 Installation Failed
Manual installation:
```bash
# Using pip
pip install PySide6

# Using Poetry (recommended)
poetry install
```

## 💡 Alternative Methods

You can also launch Clarify GUI without these scripts:

```bash
# Direct Python execution
python clarify.py

# As a module
python -m src

# Using Poetry
poetry run python clarify.py
```

## 📚 More Information

See main [README.md](README.md) for complete documentation.
