# Getting Started with Clarify

Welcome to Clarify! This guide will help you install and configure Clarify for first use.

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.12 or higher
- **RAM**: 4 GB minimum (8 GB recommended for large files)
- **Disk Space**: 500 MB for application + space for your files

### Dependencies
- **PySide6** 6.9.3+ (Qt for Python)
- **pytest** (for testing)
- Standard library only (no external dependencies for core features)

## 🔧 Installation

### Option 1: From Source (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/JosueAmaral15/clarify.git
cd clarify

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run Clarify
python main.py
```

### Option 2: Using pip (Future)

```bash
# Coming soon!
pip install clarify-app
clarify
```

## 🚀 First Run

When you launch Clarify for the first time:

1. **Main Window Opens**: You'll see the main window with multiple docks
2. **Default Layout**: The application starts in "Standard" layout
3. **Language Selection**: Default is system language (or English)

### Initial Configuration

1. **Set Your Preferred Language**:
   - Go to `Settings → Language`
   - Choose from 7 available languages
   - Interface updates immediately

2. **Choose a Layout**:
   - Go to `View → Layouts`
   - Options: Compact, Standard, Advanced
   - Or create your own custom layout

3. **Configure Keyboard Shortcuts** (Optional):
   - Go to `Settings → Keyboard Shortcuts`
   - Customize 45+ shortcuts
   - Reset to defaults anytime

## 🎯 Understanding the Interface

### Main Components

```
┌─────────────────────────────────────────────┐
│  Menu Bar (File, Edit, View, Tools, Help)  │
├─────────────────────────────────────────────┤
│  ┌────────────┐  ┌──────────────────────┐  │
│  │  Search    │  │                      │  │
│  │  Replace   │  │   Editor (Center)    │  │
│  │  Insert    │  │                      │  │
│  │  Set Ops   │  │                      │  │
│  │ (Left)     │  └──────────────────────┘  │
│  └────────────┘                             │
│  ┌────────────┐  ┌──────────────────────┐  │
│  │ Rewriter   │  │   JSON Search        │  │
│  │ Translate  │  │   (Right)            │  │
│  │ AI Proc    │  │                      │  │
│  │ (Bottom)   │  └──────────────────────┘  │
│  └────────────┘                             │
└─────────────────────────────────────────────┘
```

### Dock Panels

Clarify uses **dockable panels** that can be:
- **Moved**: Drag by title bar to reposition
- **Resized**: Drag edges to resize
- **Hidden/Shown**: `View → Docks` menu or keyboard shortcuts
- **Floated**: Drag outside main window to float

### Key Docks

1. **Editor** (`Ctrl+E`) - Edit JSON/text files with syntax highlighting
2. **Search/Replace** (`Ctrl+F`) - Find and replace text across files
3. **JSON Rewriter** (`Ctrl+Shift+R`) - Clean and deduplicate JSON
4. **Set Operations** (`Ctrl+Shift+S`) - Perform set logic on files
5. **AI Processor** (`Ctrl+Shift+A`) - Process files with AI (OpenAI/Gemini)

## 📁 File Management

### Opening Files

**Method 1: File Menu**
- `File → Open` or `Ctrl+O`
- Select single or multiple files

**Method 2: Drag & Drop**
- Drag files from file manager
- Drop onto Editor or any dock that accepts files

**Method 3: Recent Files**
- `File → Recent Files`
- Quick access to last 10 files

### Supported File Types

- **Text Files**: `.txt`, `.md`, `.log`, `.csv`
- **JSON Files**: `.json`, `.jsonc` (with comments)
- **JavaScript/TypeScript**: `.js`, `.jsx`, `.ts`, `.tsx`
- **Web Files**: `.html`, `.xml`, `.svg`
- **Configuration**: `.yaml`, `.yml`, `.ini`, `.conf`

## ⚙️ Basic Configuration

### Settings Location

Settings are stored in:
- **Linux**: `~/.config/Clarify/`
- **macOS**: `~/Library/Preferences/com.clarify/`
- **Windows**: `%APPDATA%\Clarify\`

### Essential Settings

Access via `Settings` menu:

1. **General**:
   - Theme: Light, Dark, System
   - Font size: 8-24pt (Ctrl+Scroll to adjust)
   - Auto-save interval

2. **Performance**:
   - Max file size (default: 100 MB)
   - Thread pool size (default: CPU count)
   - Cache duration

3. **Accessibility**:
   - Screen reader support
   - High contrast mode
   - Keyboard navigation

## 🎓 Next Steps

Now that Clarify is installed:

1. **Try the Quick Start**: [Quick Start Guide](quick-start-guide.md)
2. **Explore Features**: [Features Overview](features-overview.md)
3. **Learn Shortcuts**: [Keyboard Shortcuts](keyboard-shortcuts.md)
4. **Watch Tutorials**: Built-in tutorial system (`Help → Tutorials`)

## 🆘 Need Help?

- **FAQ**: [Frequently Asked Questions](faq.md)
- **Troubleshooting**: [Common Problems](troubleshooting.md)
- **Community**: [GitHub Discussions](https://github.com/JosueAmaral15/clarify/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/JosueAmaral15/clarify/issues)

---

**Next**: [Quick Start Guide →](quick-start-guide.md)
