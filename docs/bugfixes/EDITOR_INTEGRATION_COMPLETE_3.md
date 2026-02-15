# Editor Integration Complete - Programmer #3

## Issue
Text to JSON Converter's "Open in Editor" buttons were crashing with:
```
AttributeError: 'NoneType' object has no attribute 'load_json_string'
AttributeError: 'MainWindow' object has no attribute 'tab_widget'
```

## Root Causes Found

### 1. Signal Connections Missing
- Lines 641-642 in app.py: signals were commented out
- Fixed: Connected both signals properly

### 2. EditorDock Lazy Creation Issue  
- `create_dock_lazy()` used `hasattr()` check
- Problem: Attributes initialized to `None`, so `hasattr()` returned `True` but value was `None`
- Fixed: Check actual `None` value, not just attribute existence

### 3. Missing Method
- EditorDock didn't have `load_json_string()` method
- Fixed: Added method that creates new "Untitled.txt" tab with content

### 4. Wrong Tab Widget Name
- Code used `self.tab_widget` but correct name is `self.tabs`
- Fixed: Use `self.tabs` (the main QTabWidget)

### 5. Wrong Unpacking
- `tool_tabs` dict stores `(widget, index)` tuples
- Code tried to use as single value
- Fixed: Unpack properly with `_widget, editor_tab_index = self.tool_tabs["editor"]`

## Architecture Discovery

**QDockWidget CAN be added to QTabWidget!**

Initial investigation showed `addTab()` returning -1 with EditorDock, suggesting failure.
BUT: Other docks (FileExplorer, GoogleTranslate, TextToJSON) are also QDockWidgets and work fine!

Testing confirmed: `window.tabs.addTab(EditorDock(window), "Editor")` returns valid index.

The application architecture:
- MainWindow has `self.tabs` (QTabWidget) 
- Each tool added as separate tab via `_add_tool_tab()`
- All tools inherit from BaseDock(QDockWidget)
- QTabWidget accepts QDockWidget as tab content
- Each tool is a dedicated full tab in main tab bar

## Implementation

### Handler Methods (app.py lines 507-530)

```python
def _load_json_from_converter(self, json_str: str):
    """Open in Editor (stay in Text to JSON)."""
    if not hasattr(self, 'dock_editor') or self.dock_editor is None:
        from .gui import EditorDock
        self.dock_editor = EditorDock(self)
        self._add_tool_tab(self.dock_editor, "Editor", "editor")
    self.dock_editor.load_json_string(json_str)
    # Don't switch - stay in current tab

def _load_json_from_converter_and_switch(self, content: str, switch_to_file: bool):
    """Open in Editor AND switch to it."""
    if not hasattr(self, 'dock_editor') or self.dock_editor is None:
        from .gui import EditorDock
        self.dock_editor = EditorDock(self)
        self._add_tool_tab(self.dock_editor, "Editor", "editor")
    self.dock_editor.load_json_string(content)
    
    # SWITCH to Editor tab
    if hasattr(self, 'tool_tabs') and "editor" in self.tool_tabs:
        _widget, editor_tab_index = self.tool_tabs["editor"]
        self.tabs.setCurrentIndex(editor_tab_index)
```

### New Method in EditorDock (lines 595-622)

```python
def load_json_string(self, json_str: str) -> None:
    """Load JSON string into a new editor tab named 'Untitled.txt'."""
    # Create normal-mode tab (can be saved)
    tab = EditorTab(self, "", edit_only=False)
    tab.editor.setPlainText(json_str)
    
    # Add as "Untitled.txt" - user can save with any name
    tab_index = self.tab_widget.addTab(tab, "Untitled.txt")
    self.tab_widget.setCurrentIndex(tab_index)
    
    # Mark as modified so user knows to save
    tab.set_modified(True)
    
    # Update title to show modification
    self.tab_widget.setTabText(tab_index, "Untitled.txt *")
```

## User Requirements (Confirmed)

From conversation with user:

1. **Tab Location**: Existing Editor dock, NOT next to Text to JSON  
2. **Tab Name**: "Untitled.txt"
3. **Tab Mode**: Normal mode (can edit and save)
4. **Switch Behavior**: 
   - "Open in Editor" → Stay in Text to JSON tab
   - "Open in Editor and Switch" → Switch to Editor tab
5. **Existing Tabs**: Always add NEW tab (don't replace)

## Testing Status

✅ Architecture verified (QDockWidget works in tabs)
✅ Code structure correct (creates/reuses Editor, adds tab, loads content)
✅ Signal connections working
⏳ Real application testing needed

## Files Modified

1. `src/app.py`:
   - Lines 507-530: Handler methods fixed
   - Lines 641-642: Signal connections

2. `src/gui/editor_dock.py`:
   - Lines 595-622: New `load_json_string()` method

3. `src/gui/dock_factory.py`:
   - Lines 112-117: Fixed None checks

4. `src/gui/widgets/editor_tab.py`:
   - Line 234: Fixed white text color

## Next Steps

User should test:
1. Open Text to JSON Converter
2. Do extraction/conversion
3. Click "Open in Editor" → Editor tab should appear, stay in Text to JSON
4. Click "Open in Editor and Switch" → Should switch to Editor tab
5. Content should appear in "Untitled.txt" internal tab inside Editor
6. Text should be black (visible), background light gold

## Protocol Lessons Learned

❌ Violations committed:
- Claimed "fixed" without proper testing
- Made assumptions about architecture
- Didn't ask clarifying questions first

✅ Corrective actions:
- Asked 5 questions to clarify requirements
- Investigated architecture properly  
- Being honest about untested status
- Documenting findings clearly

**Status: Implementation complete, awaiting user testing**
