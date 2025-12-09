# Tooltip Guidelines - Clarify Project

**Version**: v2.9.47  
**Date**: December 9, 2025  
**Author**: Josué Amaral

This document establishes standards for creating, maintaining, and translating tooltips across the Clarify application.

---

## 1. Purpose & Scope

**Purpose**: Provide consistent, helpful, and accessible tooltip experiences for all users.

**Scope**: All interactive UI widgets (buttons, checkboxes, input fields, combo boxes, sliders, etc.) in Clarify's GUI docks.

---

## 2. Format Standard

### 2.1 Basic Structure

```
Description | Keyboard Shortcut (optional)
```

**Examples**:
- `"Browse for first JSON file | Ctrl+O"`
- `"Remove duplicate key-value pairs"`
- `"Execute selected set operations | F5"`

### 2.2 Components

1. **Description** (required):
   - Clear, concise explanation of widget's purpose
   - Use active voice ("Remove duplicates", not "Removes duplicates")
   - Include context when helpful (what, why, or when to use)

2. **Separator** (optional): ` | ` (space-pipe-space)

3. **Keyboard Shortcut** (optional):
   - Format: `Ctrl+X`, `F5`, `Ctrl+Shift+S`
   - Only include if action has direct keyboard mapping
   - Use OS-agnostic format (Ctrl, not Cmd)

### 2.3 Examples with Context

**Good** ✅:
```
"Compare keys + values with strict type checking (e.g., 1 ≠ '1') | F5 to execute"
"∩ Intersection: Find items present in ALL files (A ∩ B ∩ C...) | F5"
"Path to file or directory containing code to convert | Ctrl+O"
```

**Avoid** ❌:
```
"This button executes operations"  // Too vague
"Click here to browse files"  // Redundant ("click" implied)
"File A input field"  // Missing purpose/context
```

---

## 3. Length Guidelines

### 3.1 English (Base Language)

**Maximum**: 150 characters (hard limit for consistency)

**Recommended**: 80-120 characters (optimal readability)

**Strategy for long tooltips**:
- Prioritize essential information
- Use abbreviations sparingly (e.g., "config" for "configuration")
- Split complex concepts into 2 sentences max
- Use examples to clarify: `(e.g., {a: 1} → {a: 1})`

### 3.2 Translations (Non-English)

**No strict character limit** - Translation can be 10-30% longer than English

**Rationale**:
- Romance languages (PT-BR, ES, FR) tend to be 15-25% longer
- German compounds can extend length significantly
- Chinese/Japanese may be shorter but need extra clarification

**Quality over brevity** - Ensure translated tooltip conveys full meaning

---

## 4. When to Use Examples

### 4.1 Use Examples When:

✅ **Complex operations**:
```
"∩ Intersection: Find items present in ALL files (A ∩ B ∩ C...)"
```

✅ **Format transformations**:
```
"Remove consecutive duplicates: ['a','a','b'] → ['a','b']"
```

✅ **Type-specific behavior**:
```
"Compare keys + values with strict type checking (e.g., 1 ≠ '1', true ≠ 'true')"
```

✅ **Path notation**:
```
"Compare full paths using dot notation (e.g., 'user.name' vs 'name')"
```

### 4.2 Skip Examples When:

❌ **Self-explanatory actions**:
```
"Browse for file or directory"  // No example needed
```

❌ **Simple toggles**:
```
"Check if path is a file (unchecked for directory)"  // Clear without example
```

❌ **Already described adequately**:
```
"Create .bak files before modifying references"  // .bak is the example
```

---

## 5. Accessibility (WCAG Compliance)

### 5.1 Screen Reader Compatibility

**Do**:
- ✅ Use plain text (no HTML tags)
- ✅ Spell out abbreviations on first use: "JSON (JavaScript Object Notation)"
- ✅ Provide context: "First JSON file" not just "File A"

**Don't**:
- ❌ Rely solely on visual cues: "Click the blue button" → "Click Browse button"
- ❌ Use special characters without explanation: "∩" → "∩ Intersection:"

### 5.2 Keyboard Navigation

- All widgets with tooltips should be keyboard-accessible
- Include relevant keyboard shortcuts in tooltip when available
- Test tooltips appear on focus (not just hover)

### 5.3 Color & Contrast

- Tooltips use system theme (automatic dark/light mode)
- Contrast ratio ≥ 4.5:1 (WCAG AA standard)
- ThemeManager handles contrast automatically

---

## 6. Translation Workflow

### 6.1 Process

1. **English First**: Create all tooltips in `src/i18n/en.json` under `"tooltip.*"` namespace
2. **Review**: Ensure 150 char limit, clarity, consistency
3. **Translate**: Add to other language files (pt_BR, es, fr, de, zh, ja)
4. **Validate**: Test in-app with language switching

### 6.2 Namespace Convention

```json
{
  "tooltip.{dock_abbrev}.{widget_name}": "Description | Shortcut"
}
```

**Examples**:
```json
"tooltip.set_ops.file_a": "First JSON file for comparison operations | Ctrl+O",
"tooltip.case.combo_source": "Original case style of your code | Ctrl+Shift+C",
"tooltip.rewriter.btn_run": "Execute JSON rewriting with selected operations | F5"
```

### 6.3 Abbreviations

**Dock Abbreviations**:
- `set_ops` - Set Operations Dock
- `case` - Case Converter Dock
- `rewriter` - JSON Rewriter Dock
- `ai` - AI Processor Dock
- `search` - JSON Search Dock
- `translate` - JSON Translate Dock
- `editor` - JSON Editor Tab
- `tutorials` - Tutorials Dock

---

## 7. Implementation Checklist

### 7.1 Adding New Tooltip

- [ ] Write English tooltip (≤150 chars)
- [ ] Include keyboard shortcut if applicable
- [ ] Add example if operation is complex
- [ ] Add to `src/i18n/en.json` under `tooltip.*`
- [ ] Use `tooltip_tr("dock.widget")` in Python code
- [ ] Test tooltip appears on hover + focus
- [ ] Verify screen reader compatibility
- [ ] (Future) Translate to 6 other languages

### 7.2 Updating Existing Tooltip

- [ ] Edit English version in `en.json`
- [ ] Maintain ≤150 char limit
- [ ] Update translations in other 6 language files
- [ ] Test language switching updates tooltip
- [ ] Verify no breaking changes to formatting

---

## 8. Testing Strategy

### 8.1 Manual Testing

1. **Visual Verification**:
   - Hover over widget → tooltip appears within 500ms
   - Tooltip positioning (doesn't cover widget)
   - Readable font size (system default)
   
2. **Keyboard Testing**:
   - Tab to widget → tooltip appears on focus
   - Shift+Tab → tooltip disappears properly

3. **Language Switching**:
   - Settings → Language → Switch to PT-BR
   - Verify tooltip updates in real-time
   - Repeat for all 7 languages

### 8.2 Automated Testing

**pytest-qt Approach** (v2.9.47+):

```python
def test_tooltip_presence(qtbot):
    """Verify all widgets have non-empty tooltips."""
    dock = SetOperationsDock()
    qtbot.addWidget(dock)
    
    widgets_to_check = [
        dock.ed_file_a,
        dock.btn_browse_a,
        dock.chk_intersection,
        # ... all interactive widgets
    ]
    
    for widget in widgets_to_check:
        tooltip = widget.toolTip()
        assert tooltip != "", f"{widget.objectName()} missing tooltip"
        assert len(tooltip) > 10, f"{widget.objectName()} tooltip too short"
```

**Coverage Target**: 100% of interactive widgets have tooltips

---

## 9. Common Patterns

### 9.1 File Selection Widgets

```
"Path to [file type] for [operation] | Ctrl+O"
"Browse for [file type] | Ctrl+O"
```

### 9.2 Checkboxes (Options)

```
"[Action verb] [what] ([consequence/context])"
```

Example: `"Skip empty strings, null, [], {}, and whitespace-only values"`

### 9.3 Radio Buttons (Modes)

```
"[Mode name]: [behavior description] ([use case])"
```

Example: `"Compare only key paths, ignore values (useful for structure comparison)"`

### 9.4 Action Buttons

```
"[Verb] [object] [with context] | [Shortcut]"
```

Example: `"Execute selected set operations on provided JSON files | F5"`

### 9.5 Combo Boxes (Selection)

```
"[Purpose/role]: [what user selects] ([recommended option])"
```

Example: `"Original case style of your code (auto-detect recommended) | Ctrl+Shift+C"`

---

## 10. Maintenance

### 10.1 Quarterly Review

- Audit tooltips for accuracy (features may have evolved)
- Check character limits still met
- Verify translations reflect latest changes
- Update keyboard shortcuts if changed

### 10.2 User Feedback Integration

- Monitor GitHub issues tagged `tooltip`, `UX`, `accessibility`
- Track most-clicked "?" icons (future analytics)
- Incorporate user suggestions for clarity

### 10.3 Version History

- **v2.9.46** (2025-12-08): Created `tooltip_tr()` helper, 26 tooltips i18n (Set Operations + Case Converter)
- **v2.9.47** (2025-12-09): Added keyboard shortcuts to 26 tooltips, completed JSON Rewriter, created this document

---

## 11. Future Enhancements

### 11.1 Rich Tooltips (v3.0+)

Consider adding:
- **Screenshots/Icons**: Mini-preview of expected result
- **Links**: "Learn more" → opens documentation
- **Animated Examples**: GIF showing operation in action

**Note**: Keep plain text as fallback for accessibility

### 11.2 Context-Aware Tooltips

- Show different tooltip based on current state
- Example: "Execute" button → "Select at least one operation first" (when no operations checked)

### 11.3 Tooltip Analytics

- Track which tooltips are viewed most frequently
- Identify widgets with low tooltip engagement (may need better UX)

---

## 12. References

**Internal Documentation**:
- `src/i18n/translator.py` - `tooltip_tr()` implementation
- `src/i18n/*.json` - Translation files
- `src/shortcut_manager.py` - Keyboard shortcut definitions

**External Standards**:
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Qt Accessibility](https://doc.qt.io/qt-6/accessible.html)
- [Material Design - Tooltips](https://material.io/components/tooltips)

**Related Tasks**:
- TASKS.md § Tooltips Expansion (v2.9.47-v2.9.52)
- TASKS.md § Accessibility Features (v2.9.35)
- CHANGELOG.md § v2.9.46 Tooltips i18n

---

**Questions? Feedback?**  
Open an issue on GitHub or submit a PR with improvements!
