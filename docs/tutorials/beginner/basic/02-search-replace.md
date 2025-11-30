---
title: "Search & Replace - Basic Tutorial"
category: "beginner/basic"
difficulty: "easy"
estimated_time: "15 minutes"
keywords: ["search", "replace", "find", "regex", "text", "batch", "refactor"]
prerequisites: []
version: "1.0"
last_updated: "2025-11-30"
---

# Search & Replace - Basic Tutorial

**Learn how to find and replace text across multiple files with powerful options.**

---

## 🎯 What You'll Learn

- Open Search & Replace tool
- Perform basic text search across files
- Replace text with simple and advanced patterns
- Use case sensitivity and whole word matching
- Apply changes safely with preview

**Time**: ~15 minutes  
**Difficulty**: Easy

---

## 📌 What is Search & Replace?

Search & Replace allows you to find and replace text across one or multiple files simultaneously.

**Use Cases:**
- Rename variables across your codebase
- Update API endpoints in configuration files
- Replace hardcoded strings with translation keys
- Refactor component names

**Example:**
Find: `oldFunctionName`  
Replace: `newFunctionName`  
Result: All occurrences updated in selected files

---

## 🚀 Step-by-Step Guide

### Step 1: Open Search & Replace

1. Launch Clarify application
2. Click on **View** menu
3. Hover over **Docks**
4. Click **Search & Replace Panel**

*Alternative:* The Search & Replace panel may already be visible in the main window

---

### Step 2: Select Files

#### Option A: Single File
1. Click **Browse** next to "Input Path"
2. Select a single file (e.g., `App.tsx`)
3. Click **Open**

#### Option B: Directory (Multiple Files)
1. Click **Browse** next to "Input Path"
2. Select a folder (e.g., `src/components/`)
3. **Uncheck** "Is File" checkbox
4. Specify **Extensions** (e.g., `.tsx,.jsx,.ts`)

**Extension Format:**
- Comma-separated: `.tsx,.jsx`
- With or without dots: `.tsx` or `tsx`
- Wildcard: `*` (all files)

---

### Step 3: Enter Search Query

1. In the **Search For** field, type your search text
2. Example: `console.log`

**Tips:**
- Searches are **case-insensitive** by default
- Enable **Case Sensitive** checkbox for exact matches
- Use **Whole Word** checkbox to avoid partial matches

---

### Step 4: Enter Replacement Text

1. In the **Replace With** field, type your replacement
2. Example: `logger.debug`

**Special Cases:**
- **Remove text**: Leave "Replace With" field empty
- **Add text**: Use search for empty string, replace with your text
- **Keep original**: Leave "Replace With" field empty to just preview matches

---

### Step 5: Configure Options

#### Case Sensitive
- **Checked**: `Hello` ≠ `hello`
- **Unchecked**: `Hello` = `hello` (default)

#### Whole Word
- **Checked**: Only matches complete words
  - Find `cat` → Matches `cat` but NOT `catalog`
- **Unchecked**: Matches partial words (default)

#### Regular Expression
- **Checked**: Enables regex patterns (see Advanced section)
- **Unchecked**: Literal text search (default for beginners)

---

### Step 6: Preview Matches (Optional)

1. Click **Search** button (without Replace)
2. Review the **Match Panel** (bottom section)
3. See all matches with:
   - File path
   - Line number
   - Matched text context

**Example Match Panel:**
```
src/App.tsx:15: console.log('User logged in');
src/utils/api.ts:42: console.log('API response:', data);
src/components/Header.tsx:8: console.log('Rendering header');

Total: 3 matches in 3 files
```

---

### Step 7: Replace

1. After previewing matches, click **Replace** button
2. Clarify will:
   - Show progress bar
   - Process each file
   - Display results in Result Panel
3. Review success messages:
   ```
   ✓ Replaced 3 occurrences in src/App.tsx
   ✓ Replaced 1 occurrence in src/utils/api.ts
   ✓ Replaced 1 occurrence in src/components/Header.tsx
   Total: 5 replacements in 3 files
   ```

---

## 🎓 Example Walkthrough

### Scenario 1: Rename a Component

**Goal:** Rename `OldButton` → `NewButton` across entire project

**Steps:**
1. **Input Path**: Select `src/` folder
2. **Is File**: ❌ Uncheck (directory mode)
3. **Extensions**: `.tsx,.jsx`
4. **Search For**: `OldButton`
5. **Replace With**: `NewButton`
6. **Case Sensitive**: ✅ Check (component names are case-sensitive)
7. **Whole Word**: ✅ Check (avoid matching `OldButtonGroup`)
8. Click **Replace**

**Result:**
```tsx
// Before
import { OldButton } from './OldButton';
<OldButton onClick={...} />

// After
import { NewButton } from './NewButton';
<NewButton onClick={...} />
```

---

### Scenario 2: Update API Endpoint

**Goal:** Change `https://api.old.com` → `https://api.new.com`

**Steps:**
1. **Input Path**: Select `src/config/` folder
2. **Search For**: `https://api.old.com`
3. **Replace With**: `https://api.new.com`
4. **Extensions**: `.ts,.js,.json`
5. Click **Replace**

**Result:**
```ts
// Before
const API_URL = 'https://api.old.com/v1';

// After
const API_URL = 'https://api.new.com/v1';
```

---

### Scenario 3: Remove Debug Logs

**Goal:** Remove all `console.log` statements

**Steps:**
1. **Input Path**: Select entire project folder
2. **Search For**: `console.log(.*);` (enable **Regex**)
3. **Replace With**: *(leave empty)*
4. **Regular Expression**: ✅ Check
5. Click **Replace**

**Result:**
```tsx
// Before
console.log('Debug message');
const user = getUser();
console.log('User:', user);

// After
const user = getUser();
```

---

## 💡 Tips & Best Practices

### Tip 1: Always Preview First
✅ Click **Search** before **Replace**  
❌ Don't click **Replace** blindly

**Why?** Preview shows exactly what will change, avoiding mistakes.

---

### Tip 2: Use Whole Word for Identifiers
When replacing variable/function names:
- ✅ Enable **Whole Word**
- ❌ Don't use partial matching

**Example:**
```
Find: cat
Whole Word: ✅

Matches: cat
Skips: catalog, concatenate, scatter
```

---

### Tip 3: Backup Before Large Replacements
For project-wide changes:
1. Commit your code to Git first
2. Or use Clarify's built-in backup feature
3. Verify changes after replacement
4. Rollback if needed (Git: `git reset --hard`)

---

### Tip 4: Test on Small Sample
Before processing 1000 files:
1. Test on 1 file first
2. Verify the replacement is correct
3. Then process entire directory

---

### Tip 5: Use Extensions Filter
Avoid processing irrelevant files:
- ✅ Specify: `.tsx,.ts` (only TypeScript)
- ❌ Don't use: `*` (all files, including images/binaries)

---

## ⚠️ Common Issues

### Issue 1: Too Many Matches
**Problem:** Replaced 10,000 occurrences (unexpected)  
**Solution:**
- Enable **Whole Word** to narrow matches
- Use **Case Sensitive** for exact matches
- Add more context to search query

### Issue 2: No Matches Found
**Problem:** "0 matches" but text exists  
**Solution:**
- Check **Case Sensitive** (maybe it's wrong case)
- Verify **Extensions** filter includes your file types
- Try searching in parent directory

### Issue 3: Regex Not Working
**Problem:** Regex pattern doesn't match  
**Solution:**
- Verify **Regular Expression** checkbox is enabled
- Test regex online first: [regex101.com](https://regex101.com)
- Remember: Python regex syntax

---

## 🔥 Advanced: Basic Regex

Enable **Regular Expression** checkbox for power features:

### Pattern 1: Match Numbers
```
Find: \d+
Matches: 123, 42, 9999
```

### Pattern 2: Match Words
```
Find: \w+
Matches: hello, user_name, Component123
```

### Pattern 3: Match Optional Text
```
Find: colou?r
Matches: color, colour
```

### Pattern 4: Capture Groups
```
Find: user_(\w+)
Replace: person_$1
Result: user_name → person_name
```

**Learn more:** [Advanced Search & Replace Tutorial](../advanced/01-search-replace-advanced.md)

---

## 🎯 Next Steps

**You've mastered Search & Replace basics!** 🎉

### What's Next?
1. [JSON Rewriter Tutorial](03-json-rewriter.md) - Transform JSON files
2. **Practice:** Try replacing text in your own project
3. **Advanced:** Learn regex patterns and capture groups

### Need Help?
- Use **Help → AI Assistant**: "How do I use regex in Search & Replace?"
- Check [Tutorial Index](../../README.md)
- Report issues: [GitHub](https://github.com/JosueAmaral15/clarify/issues)

---

**Tutorial by**: Josué Amaral  
**Last Updated**: November 30, 2025
