---
name: Translation Improvement
about: Help improve translations in Clarify
title: '[i18n] Improve [LANGUAGE] translations'
labels: i18n, enhancement
assignees: ''

---

## 🌍 Language

Which language are you improving?

- [ ] 🇪🇸 Español (es)
- [ ] 🇫🇷 Français (fr)
- [ ] 🇩🇪 Deutsch (de)
- [ ] 🇨🇳 中文 简体 (zh)
- [ ] 🇯🇵 日本語 (ja)
- [ ] Other: _____________

## 🔍 Issue Type

What kind of translation issue is this?

- [ ] **Incorrect translation** (wrong meaning)
- [ ] **Grammar/spelling error**
- [ ] **Better phrasing** (more natural/idiomatic)
- [ ] **Missing translation** (key not translated)
- [ ] **Inconsistent terminology** (same term translated differently)
- [ ] **Cultural adaptation** (phrase doesn't work in target culture)

## 📝 Current Translation

**File**: `src/i18n/[language].json`

**Key**: 
```
"menu.file.open"
```

**Current value**:
```
"Abrir"
```

## ✅ Proposed Translation

**New value**:
```
"Abrir archivo"
```

## 💬 Explanation

Why is the new translation better?

Example:
- "The current translation is too vague. 'Abrir' alone doesn't specify what to open. 'Abrir archivo' (Open file) is clearer and matches standard UI conventions in Spanish-speaking regions."

## 🔍 Context

Where does this string appear in the UI?

Example:
- Menu bar: File → Open
- Tooltip on button
- Dialog title

## 📚 References

Any references to support your suggestion?

- [ ] Native speaker of this language
- [ ] UI conventions in [OS] (Windows/macOS/Linux)
- [ ] Other software translations (please specify)
- [ ] Translation guidelines/style guides

## ✅ Checklist

- [ ] I am a native or fluent speaker of this language
- [ ] I have checked the context where this string appears
- [ ] I have verified this follows standard UI conventions
- [ ] I have checked for consistency with other translations in the file
