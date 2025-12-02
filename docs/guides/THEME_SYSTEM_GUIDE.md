# Theme System Guide - Clarify

**Version**: 2.9.4  
**Date**: November 28, 2025  
**Author**: Josué Amaral

## Overview

Clarify now features a comprehensive theme system with three distinct visual modes:
- ☀️ **Light Theme**: Clean, professional design with bright colors
- 🌙 **Dark Theme**: Modern dark design for reduced eye strain
- 🖥️ **System Theme**: Automatically matches your operating system settings

---

## How to Change Themes

### Via Menu Bar

1. Open Clarify
2. Click on **Themes** in the menu bar
3. Select your preferred theme:
   - 🖥️ **System** - Uses OS settings (default)
   - ☀️ **Light** - Bright, professional theme
   - 🌙 **Dark** - Eye-friendly dark theme

Your selection is automatically saved and will persist across application restarts.

---

## Theme Features

### Light Theme (☀️)

**Best for**: Bright environments, daytime use, printed documentation

**Color Palette**:
- Background: Clean white (#FAFAFA)
- Text: Dark gray (#1E1E1E)
- Accents: Microsoft Blue (#0078D7)
- Buttons: Light gray (#F0F0F0)

**Styled Components**:
- ✅ Input fields with focus indicators
- ✅ Buttons with hover/pressed states
- ✅ Rounded corners and smooth borders
- ✅ Clean scrollbars
- ✅ Professional GroupBox styling
- ✅ Subtle shadows and depth

### Dark Theme (🌙)

**Best for**: Low-light environments, extended use, reduced eye strain

**Color Palette**:
- Background: Charcoal (#2D2D30)
- Text: Light gray (#F0F0F0)
- Accents: Azure Blue (#007ACC)
- Buttons: Dark gray (#3C3C3C)

**Styled Components**:
- ✅ High contrast text for readability
- ✅ Reduced brightness for comfort
- ✅ Consistent dark UI elements
- ✅ Modern IDE-like appearance
- ✅ Optimized for long coding sessions
- ✅ Blue accents for visual hierarchy

### System Theme (🖥️)

**Best for**: Users who prefer OS consistency

**Features**:
- Automatically matches your operating system theme
- Uses Qt Fusion style with system palette
- Respects OS accessibility settings
- Changes automatically when OS theme changes (on supported systems)

---

## Component Styling

All themes include comprehensive styling for:

### Input Components
- `QLineEdit` - Text input fields
- `QPlainTextEdit` - Multi-line text editors
- `QTextEdit` - Rich text editors
- `QSpinBox` - Numeric inputs

### Buttons and Controls
- `QPushButton` - Action buttons
- `QCheckBox` - Checkboxes
- `QRadioButton` - Radio buttons
- `QComboBox` - Dropdown menus

### Containers
- `QGroupBox` - Grouped controls
- `QTabWidget` - Tabbed panels
- `QDockWidget` - Dockable panels

### Lists and Trees
- `QTreeView` - Results tree
- `QListView` - List displays

### Navigation
- `QMenuBar` - Application menu
- `QMenu` - Dropdown menus
- `QScrollBar` - Scrollbars (vertical and horizontal)
- `QStatusBar` - Bottom status information

---

## Technical Details

### Theme Manager Architecture

Themes are managed by the dedicated `ThemeManager` class:

```python
from src.theme_manager import ThemeManager

# Apply a theme
ThemeManager.apply_theme(app, "dark")  # "light", "dark", or "system"
```

### Persistence

Theme preferences are stored in:
```
~/.config/clarify.conf
```

Format:
```ini
[THEME]
mode = dark
```

### Custom Stylesheets

Each theme includes comprehensive QSS (Qt Style Sheets) for:
- Colors and backgrounds
- Borders and corners
- Hover and focus states
- Disabled states
- Selection colors
- Padding and margins

---

## Tips and Best Practices

### For Light Theme Users
- Best used in well-lit environments
- Reduces glare on glossy screens
- Professional appearance for presentations
- High contrast for accessibility

### For Dark Theme Users
- Ideal for late-night coding
- Reduces eye strain during extended use
- Better for OLED screens (reduces burn-in)
- Lower power consumption on some displays

### For System Theme Users
- Ensures consistency across all applications
- Automatically adapts to time of day (if OS supports)
- Respects accessibility preferences
- No manual switching needed

---

## Keyboard Shortcuts

Currently, theme switching is available only through the menu bar. Future versions may include:
- `Ctrl+Shift+T` - Toggle themes
- `Ctrl+Shift+L` - Light theme
- `Ctrl+Shift+D` - Dark theme

---

## Troubleshooting

### Theme doesn't change
1. Ensure you clicked on the theme option in the menu
2. Check that the checkmark appears next to your selection
3. Restart the application if needed

### Theme looks inconsistent
1. Make sure you're running the latest version (v2.9.4+)
2. Some custom Qt styles may override theme settings
3. Check for any custom stylesheet files in your config

### System theme not working
1. Verify your OS theme settings are properly configured
2. Some Linux environments may need additional Qt platform themes
3. Try selecting Light or Dark explicitly if System doesn't work

---

## Future Enhancements

Planned improvements for the theme system:

- [ ] Custom theme editor
- [ ] Additional theme presets (Solarized, Monokai, etc.)
- [ ] Per-panel theme overrides
- [ ] High contrast mode for accessibility
- [ ] Theme import/export functionality
- [ ] Animated theme transitions

---

## Version History

### v2.9.4 (2025-11-28)
- Initial release of theme system
- Three themes: Light, Dark, System
- Comprehensive component styling
- Theme persistence
- Menu bar integration

---

## Support

For issues or suggestions regarding themes:
- Open an issue on GitHub: [github.com/JosueAmaral15/clarify](https://github.com/JosueAmaral15/clarify)
- Include screenshots showing the theme issue
- Mention your OS and Qt version

---

**Enjoy your new themed experience in Clarify!** ✨
