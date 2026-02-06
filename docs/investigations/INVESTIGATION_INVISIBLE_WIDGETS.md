# Investigation: Search/Replace Widgets Invisible - CRITICAL Indentation Bug

**Date**: 2026-01-27 12:52 UTC  
**Investigator**: Programmer #3  
**Severity**: CRITICAL (Feature completely broken)  
**Status**: ROOT CAUSE FOUND ✅

---

## 🔴 USER REPORT

**Symptoms**:
- Search/Replace **tab** appears in tab bar ✅
- But **widgets inside are invisible** ❌
  - No search input fields
  - No replace input fields  
  - No buttons (Search, Replace, Replace All)
  - No checkboxes (Match case, Whole word, Regex)
  - Empty/blank content area

**Insert tab**: Works correctly (all widgets visible) ✅

---

## 🔍 ROOT CAUSE ANALYSIS

### Critical Bug: Indentation Error

**File**: `src/gui/panels/search_replace_panel.py`  
**Lines**: 82-324

**The Problem**:
```python
class SearchReplacePanel(QWidget):
    def __init__(self, parent=None, progress_manager=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        self.processing_search = False
        self.progress_manager = progress_manager
        self._current_task_id = None
        self._processing_modal = None
        # ❌ __init__ ENDS HERE (only 7 lines!)
        # NO WIDGETS CREATED!

    def set_editor_fonts(self, font):  # ⬅️ WRONG! Should be inside __init__
        """Set monospaced font..."""
        self.ed_repl.setFont(font)
        self.ed_query.setFont(font)

        # ❌ ALL 235 LINES OF UI CODE ARE HERE!
        column = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("search_replace.lbl_root_path")))
        self.ed_path = QLineEdit()
        self.btn_browse = QPushButton(tr("search_replace.btn_browse"))
        # ... 230+ more lines creating ALL widgets ...
        self.btn_search.clicked.connect(self._start_search_threaded)
        # ❌ Ends at line 324!
```

**What Should Happen**:
```python
def __init__(self, parent=None, progress_manager=None):
    super().__init__(parent)
    root = QVBoxLayout(self)
    self.processing_search = False
    # ...
    
    # ✅ Create ALL widgets HERE in __init__
    column = QVBoxLayout()
    row = QHBoxLayout()
    self.ed_path = QLineEdit()
    # ... all widget creation ...
    
    # ✅ Connect signals
    self.btn_search.clicked.connect(self._start_search_threaded)

def set_editor_fonts(self, font):
    """✅ ONLY set fonts, don't create widgets"""
    self.ed_repl.setFont(font)
    self.ed_query.setFont(font)
```

---

## 🎯 Why Widgets Are Invisible

**Execution Flow**:

1. **UIBuilder.build_panels()** creates SearchReplacePanel:
   ```python
   main_window.tab_search = SearchReplacePanel(parent=main_window, progress_manager=...)
   ```
   - ❌ `__init__()` runs → creates empty layout, NO widgets

2. **MainWindow.__init__()** tries to set fonts (line 436):
   ```python
   try:
       f = QFontDatabase.systemFont(QFontDatabase.FixedFont)
       self.tab_search.set_editor_fonts(f)  # ⬅️ This should create widgets
   except Exception:
       pass  # ❌ Silently catches errors!
   ```

3. **If `set_editor_fonts()` is never called** → widgets never created → invisible!

4. **Even worse**: `set_editor_fonts()` tries to set fonts on widgets that don't exist yet:
   ```python
   def set_editor_fonts(self, font):
       self.ed_repl.setFont(font)  # ❌ self.ed_repl doesn't exist yet!
       self.ed_query.setFont(font)  # ❌ self.ed_query doesn't exist yet!
       
       # Then creates them...
       self.ed_repl = QPlainTextEdit()  # ⬅️ Created AFTER trying to use it!
   ```

---

## 🐛 How This Bug Happened

**Likely Scenario**:

1. Developer wrote `__init__()` with all UI code (correct)
2. Later added `set_editor_fonts()` method  
3. **Copy/paste error**: Accidentally moved ALL UI code from `__init__()` into `set_editor_fonts()`
4. Forgot to properly re-indent / only left setup code in `__init__()`
5. Bug only noticed now because:
   - Insert tab doesn't have this problem
   - SearchReplacePanel rarely tested in isolation
   - Silent exception catching in app.py hides the error

---

## ✅ THE FIX

**Strategy**: Move ALL UI creation code back into `__init__()`

**Steps**:
1. Keep lines 82-89 in `__init__()` (initialization)
2. Move lines 95-324 (UI creation) into `__init__()` with proper indentation
3. Make `set_editor_fonts()` ONLY set fonts (2 lines):
   ```python
   def set_editor_fonts(self, font):
       """Set monospaced font for query and replacement editors."""
       self.ed_repl.setFont(font)
       self.ed_query.setFont(font)
   ```

**Lines to Fix**: 242 lines need re-indentation  
**Risk**: LOW (pure indentation fix, no logic change)

---

## 📊 IMPACT ASSESSMENT

**Before Fix**:
- ❌ Search/Replace feature completely broken
- ❌ Users cannot search files
- ❌ Users cannot replace text
- ❌ Major feature unusable
- ❌ Silent failure (no error messages)

**After Fix**:
- ✅ All widgets visible and functional
- ✅ Search works
- ✅ Replace works
- ✅ Feature restored

---

## 🎓 LESSONS LEARNED

1. **Indentation Errors**: Python indentation bugs can hide entire features
2. **Silent Exceptions**: `try/except: pass` hides critical initialization failures
3. **Testing**: Need UI tests to catch invisible widget bugs
4. **Code Review**: Copy/paste errors need careful review
5. **Debug Prints**: Protocol debug prints would have revealed this immediately:
   ```python
   def __init__(self, parent=None, progress_manager=None):
       print(f"DEBUG 82 __init__() | ENTER")
       super().__init__(parent)
       root = QVBoxLayout(self)
       print(f"DEBUG 85 __init__() | Creating widgets...")
       # ... widget creation ...
       print(f"DEBUG 324 __init__() | EXIT | widgets_created: True")
   ```

---

## 🔧 FIX IMPLEMENTATION

**Next**: Apply indentation fix to move UI code into `__init__()`

**Status**: READY TO FIX  
**Confidence**: 100% ✅  
**Priority**: CRITICAL 🔴

---

**Investigator**: Programmer #3  
**Investigation Time**: 10 minutes  
**Root Cause**: Indentation error (UI code in wrong method)  
**Fix Complexity**: MEDIUM (242 lines to re-indent)
