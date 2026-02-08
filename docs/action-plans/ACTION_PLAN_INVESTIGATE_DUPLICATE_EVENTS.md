# Action Plan: Investigate Duplicate Qt Event Bug

**Programmer**: COM8  
**Date**: 2026-01-26  
**Protocol**: SIMPLICITY_PROTOCOL_3 v4.5  
**Issue**: All button clicks trigger events TWICE (Translate, Reverse, Save As)

## Problem Statement

Every QPushButton.clicked signal in GoogleTranslateDock fires TWICE from single click:
- `_start_translation()` called 2x → worker crash (fixed with guard)
- `_reverse_translation()` called 2x → swap then swap back (fixed with guard)  
- `_save_as()` called 2x → dialog appears twice (fixed with guard)

**Pattern**: ALL buttons affected, not just one. This suggests:
- Problem in signal connection logic
- Problem in parent class (BaseDock)
- Problem in Qt event propagation

## Investigation Plan - Following Protocol

### Phase 1: Examine Signal Connections (THIS SESSION)

**Goal**: Find if signals are connected multiple times

**Steps**:
1. Check `_connect_signals()` - is it called multiple times?
2. Check if BaseDock also connects signals
3. Add debug prints to count how many times signals connect
4. Search for duplicate `.connect()` calls in code

**Files to investigate**:
- `src/gui/google_translate_dock.py` (lines 299-310: _connect_signals)
- `src/gui/base_dock.py` (parent class - might have duplicate connection)

### Phase 2: Examine BaseDock Inheritance

**Goal**: Check if parent class interferes with signals

**Steps**:
1. Read BaseDock.__init__() to see what it does
2. Check if BaseDock connects widget signals
3. Check if _setup_ui() is called multiple times

### Phase 3: Search Online for Qt Duplicate Event Issues

**Goal**: Find if this is known Qt/PySide6 bug

**Steps**:
1. Search: "PySide6 clicked signal fires twice"
2. Search: "Qt button clicked duplicate event"
3. Check Qt documentation for signal connection best practices

### Phase 4: Check Application-Level Event Handling

**Goal**: See if app.py or tab_manager.py causes duplication

**Steps**:
1. Check how GoogleTranslateDock is instantiated
2. Check if dock is created multiple times
3. Check event filters or global event handlers

## Current Workarounds in Place

✅ `_start_translation()` - guard flag `self.translation_worker.isRunning()`
✅ `_reverse_translation()` - guard flag `self._reversing` + 300ms debounce
✅ `_save_as()` - guard flag `self._saving` + 300ms debounce

**These are BAND-AIDS, not root cause fix!**

## Success Criteria

- Understand WHY events fire twice
- Fix root cause (remove all guard flags if possible)
- Document findings for future reference
- Test that fix doesn't break other docks

## Next Steps

Starting Phase 1 investigation now...


## Phase 1 Results: ROOT CAUSE FOUND! ✅

**File**: `src/gui/base_dock.py` (line 55-56)  
**File**: `src/gui/google_translate_dock.py` (line 162)

### The Bug Flow

```
GoogleTranslateDock.__init__() [line 156]
  ↓
super().__init__()
  ↓
BaseDock.__init__() [line 50]
  ↓
self._setup_ui() [line 55] ← Calls GoogleTranslateDock._setup_ui (polymorphism)
  ↓
GoogleTranslateDock._setup_ui() [line 158]
  ↓
self._connect_signals() [line 162] ← ⚠️ FIRST CONNECTION
  ↓
(returns to BaseDock.__init__)
  ↓
self._connect_signals() [line 56] ← ⚠️ SECOND CONNECTION (DUPLICATE!)
```

### The Problem

BaseDock pattern EXPECTS child classes to NOT call `_connect_signals()` in `_setup_ui()`, because BaseDock will call it after _setup_ui() completes.

GoogleTranslateDock VIOLATES this pattern by calling `_connect_signals()` inside `_setup_ui()`.

### The Fix

**Remove line 162** from GoogleTranslateDock._setup_ui():

```python
# BEFORE (WRONG):
def _setup_ui(self):
    self._create_widgets()
    self._create_layout()
    self._connect_signals()  # ← DELETE THIS LINE
    self._apply_tooltips()
    self._load_preferences()

# AFTER (CORRECT):
def _setup_ui(self):
    self._create_widgets()
    self._create_layout()
    # BaseDock calls _connect_signals() automatically
    self._apply_tooltips()
    self._load_preferences()
```

### Expected Impact

✅ All button clicks fire only ONCE  
✅ Can REMOVE all guard flags (_reversing, _saving, translation_worker check)  
✅ Code becomes cleaner and more maintainable  
✅ Follows BaseDock design pattern correctly  

### Verification Needed

After fix, test ALL buttons:
- Translate button
- Copy Result button
- Save As button
- Reverse button
- Clear button
- Cancel button
- Browse button

