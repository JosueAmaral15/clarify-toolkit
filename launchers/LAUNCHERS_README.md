# 🚀 Clarify - Launcher Scripts

## Quick Start

**Simple launch options for all platforms - just double-click!**

### 🪟 Windows
**Double-click:** `clarify.bat`

### 🐧 Linux
**Double-click:** `clarify.sh` (or run `./clarify.sh` in terminal)

### 🍎 macOS
**Double-click:** `clarify.command` (or run `./clarify.command` in terminal)

---

## 📋 What These Scripts Do

All launcher scripts automatically:
- ✅ Verify Python 3.10+ is installed
- ✅ Check for PySide6 (GUI framework)
- ✅ Offer to install PySide6 if missing
- ✅ Launch the Clarify GUI application
- ✅ Display helpful error messages if something fails
- ✅ Verify project directory structure

---

## 🎯 Features

### Automatic Dependency Management
- Detects missing dependencies
- Offers one-click installation
- Provides manual installation instructions

### Error Handling
- Clear error messages
- Common troubleshooting tips
- Pause before closing (Windows) to read errors

### Platform-Specific Support
- **Windows:** Uses `python` command, checks PATH
- **Linux:** Uses `python3`, supports multiple distros
- **macOS:** Detects both `python` and `python3`, Homebrew-friendly

---

## 📦 Requirements

### Python
- **Version:** Python 3.10 or higher
- **Check:** Run `python --version` or `python3 --version`
- **Install:**
  - **Windows:** [python.org/downloads](https://www.python.org/downloads/) (check "Add to PATH")
  - **Linux:** `sudo apt install python3 python3-pip` (Ubuntu/Debian)
  - **macOS:** `brew install python3` or [python.org/downloads](https://www.python.org/downloads/)

### PySide6
- **Purpose:** GUI framework (Qt for Python)
- **Auto-install:** Scripts offer to install automatically
- **Manual install:** `pip install PySide6` or `pip3 install PySide6`

---

## 🔧 Troubleshooting

### "Python not found"
**Windows:**
- Reinstall Python and check "Add Python to PATH"
- Or add manually: System Properties → Environment Variables → Path

**Linux/macOS:**
- Install via package manager (see Requirements above)
- Verify with: `which python3`

### "PySide6 not installed"
**Option 1:** Let the script install it (recommended)
- Script will prompt and install automatically

**Option 2:** Install manually
```bash
# Standard installation
pip3 install PySide6

# User installation (no admin needed)
pip3 install --user PySide6

# Linux: System package (Ubuntu/Debian)
sudo apt install python3-pyside6.qtwidgets

# macOS: Homebrew
brew install pyside6
```

### macOS: "Developer not verified" or security warning
1. Right-click `clarify.command` → **Open**
2. Click **Open** in the security dialog
3. Or: System Preferences → Security & Privacy → Click "Open Anyway"

### Linux: "Permission denied"
```bash
chmod +x clarify.sh
./clarify.sh
```

### Script runs but GUI doesn't appear
**Linux:**
- Ensure X11 or Wayland is running
- Check: `echo $DISPLAY` should show output

**All platforms:**
- Check Python version: `python3 --version` (must be 3.10+)
- Verify PySide6: `python3 -c "import PySide6; print(PySide6.__version__)"`

---

## 📂 Alternative Launch Methods

### Standard Python Module Execution (Recommended for developers)
```bash
# From project root directory
python3 -m src
```

### Using main.py (development/testing)
```bash
python3 main.py test
```

---

## 🗂️ Additional Launchers

**Location:** `launchers/` directory

These are the original launchers (kept for compatibility):
- `launchers/clarify_gui.bat` (Windows)
- `launchers/clarify_gui.sh` (Linux)
- `launchers/clarify_gui.command` (macOS)
- `launchers/clarify.py` (legacy wrapper; prefer `python -m src` from the project root)

**Note:** Root launchers (`clarify.bat`, `clarify.sh`, `clarify.command`) are recommended as they're easier to find and use.

---

## 📝 Protocol Compliance

These launchers follow **Protocolo Simplicidade 3** guidelines:

✅ **Security:** No system modifications without user consent  
✅ **Solo Developer:** Simple, self-documenting scripts  
✅ **Production Ready:** Comprehensive error handling  
✅ **User Friendly:** Clear messages and automatic dependency handling  
✅ **Cross-Platform:** Works on Windows, Linux, and macOS  
✅ **Documented:** Inline comments and this README  

---

## 🆘 Support

If you encounter issues:

1. **Check Python version:** `python3 --version` (must be 3.10+)
2. **Check PySide6:** `python3 -c "import PySide6"`
3. **Run manually:** `cd <project_root> && python3 -m src`
4. **Check logs:** Look for error messages in the console
5. **Review docs:** `docs/README.md` and `README.md`

**Common Issues:**
- Python not in PATH → Reinstall Python with PATH option
- Missing dependencies → Run `poetry install` or `python3 -m pip install -e .`
- Configuration errors → Check `config/` directory
- Display issues (Linux) → Ensure X11/Wayland is running

---

## 📌 Quick Reference

| Platform | Launcher File | Command | Executable |
|----------|--------------|---------|------------|
| Windows | `clarify.bat` | Double-click or `clarify.bat` | ✅ Ready |
| Linux | `clarify.sh` | Double-click or `./clarify.sh` | ✅ Ready |
| macOS | `clarify.command` | Double-click or `./clarify.command` | ✅ Ready |

---

## 🎨 Creating Desktop Shortcuts

### Windows
1. Right-click `clarify.bat`
2. Send to → Desktop (create shortcut)
3. Rename to "Clarify"

### Linux (GNOME/KDE)
1. Copy `clarify.sh` to Desktop
2. Right-click → Properties → Permissions → Allow executing as program
3. Or create `.desktop` file (see distribution docs)

### macOS
1. Drag `clarify.command` to Desktop
2. Or create an Alias (Cmd+Option+drag)

---

**Created:** 2026-01-07  
**Protocol:** Simplicidade 3  
**Version:** 1.0.0
