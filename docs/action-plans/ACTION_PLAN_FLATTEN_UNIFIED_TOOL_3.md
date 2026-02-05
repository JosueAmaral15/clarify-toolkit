# Action Plan: Flatten Unified Tool UI

**Programmer:** #3  
**Date:** 2026-01-30  
**Status:** In Progress

---

## Objective

Refactor UnifiedTextToJsonDock from composition pattern to flattened UI:
- Remove embedded widgets (TextToJsonDock, AdvancedExtractorDock)
- Copy all widget creation code directly into UnifiedTextToJsonDock
- Copy all methods (conversion logic, templates, history, signals)
- Create two separate flat layouts (Format Conversion + JSX Extraction)
- Switch between layouts on mode change
- ONE main scrollbar only (no internal scrolls)

---

## User Requirements

1. ✅ Extract all controls to main body (no embedded containers)
2. ✅ Flatten Format Conversion mode (Format, Type Inference, Input, Output, buttons)
3. ✅ Flatten JSX Extraction mode (Path, Mode, checkboxes, output tabs)
4. ✅ Two separate flat layouts, switch between them (hide/show)
5. ✅ Copy ALL code (widgets + business logic)
6. ✅ All features must work (10 converters, templates, history, validation, etc.)

---

## Implementation Steps

### Phase 1: Read Source Files (30 min)
- [ ] Read 100% of TextToJsonDock (584 lines)
- [ ] Read 100% of AdvancedExtractorDock (645 lines)
- [ ] List all widgets to copy
- [ ] List all methods to copy
- [ ] List all signals/slots to copy

### Phase 2: Create Format Conversion Layout (2 hours)
- [ ] Copy widget creation from TextToJsonDock
  - [ ] Format selector (ComboBox)
  - [ ] Type Inference group (RadioButtons)
  - [ ] CSV Options group (CheckBoxes, ComboBox)
  - [ ] Input text area (QPlainTextEdit, 200px min)
  - [ ] Output text area (QPlainTextEdit, 200px min)
  - [ ] All buttons (Convert, Templates, Clear, Validate, Copy, Open, History, Swap)
  - [ ] Status label
- [ ] Copy all conversion methods
  - [ ] _do_conversion()
  - [ ] _on_convert_clicked()
  - [ ] _on_input_changed()
  - [ ] _update_preview()
  - [ ] _validate_json()
  - [ ] _swap_io()
- [ ] Copy templates system
  - [ ] TemplatesDialog class
  - [ ] _show_templates()
- [ ] Copy history system
  - [ ] HistoryDialog class
  - [ ] _show_history()
  - [ ] _add_to_history()
- [ ] Copy all signal connections
- [ ] Test all features work

### Phase 3: Create JSX Extraction Layout (2 hours)
- [ ] Copy widget creation from AdvancedExtractorDock
  - [ ] Path input field + Browse button
  - [ ] Mode selector (JSX, Tags, Generic, Paths)
  - [ ] Parameter field
  - [ ] All 26 checkboxes (Include key, Drop standard, TypeScript, etc.)
  - [ ] Output tabs (Paths | JSON)
  - [ ] Extract button, Clear button, Copy buttons
- [ ] Copy all extraction methods
  - [ ] _extract()
  - [ ] _on_extract_clicked()
  - [ ] _clear_output()
  - [ ] _copy_paths()
  - [ ] _copy_json()
- [ ] Copy mode toggle logic
  - [ ] _toggle_generic_fields()
  - [ ] _update_avoid_mode()
- [ ] Copy all signal connections
- [ ] Test all features work

### Phase 4: Mode Switching Logic (30 min)
- [ ] Create two container widgets (format_conversion_container, jsx_extraction_container)
- [ ] Add both to scroll area with stacked layout
- [ ] Implement _switch_mode() to show/hide containers
- [ ] Test mode switching

### Phase 5: Testing (1 hour)
- [ ] Programmatic tests
  - [ ] Test Format Conversion mode widget creation
  - [ ] Test all 10 format converters
  - [ ] Test templates dialog
  - [ ] Test history dialog
  - [ ] Test JSX Extraction mode widget creation
  - [ ] Test extraction with sample file
  - [ ] Test mode switching
- [ ] Create test report
- [ ] Report to user for manual testing

---

## Files to Modify

- `src/gui/unified_text_to_json_dock.py` (150 lines → ~1,200 lines)

## Files to Read

- `src/gui/text_to_json_dock.py` (584 lines) - source for Format Conversion
- `src/gui/advanced_extractor_dock.py` (645 lines) - source for JSX Extraction
- `src/text_to_json.py` (624 lines) - backend for conversion
- `src/extractors/advanced_extractor.py` (708 lines) - backend for extraction

---

## Estimated Time

- Phase 1: 30 min ✅
- Phase 2: 2 hours ⏳
- Phase 3: 2 hours ⏳
- Phase 4: 30 min ⏳
- Phase 5: 1 hour ⏳
- **Total:** 6 hours

---

## Current Status

**Phase 1: In Progress** - Reading source files
