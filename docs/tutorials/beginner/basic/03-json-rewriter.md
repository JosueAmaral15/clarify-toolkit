---
title: "JSON Rewriter - Basic Tutorial"
category: "beginner/basic"
difficulty: "easy"
estimated_time: "12 minutes"
keywords: ["json", "rewriter", "transform", "deduplicate", "clean", "merge"]
prerequisites: []
version: "1.0"
last_updated: "2025-11-30"
---

# JSON Rewriter - Basic Tutorial

**Learn how to transform, clean, and optimize JSON structures with powerful operations.**

---

## 🎯 What You'll Learn

- Open JSON Rewriter tool
- Remove duplicate keys from JSON files
- Clean empty values and normalize structure
- Convert between JSON and TypeScript formats
- Understand output options

**Time**: ~12 minutes  
**Difficulty**: Easy

---

## 📌 What is JSON Rewriter?

JSON Rewriter transforms and cleans messy JSON files with intelligent operations.

**Common Problems JSON Rewriter Solves:**
1. **Duplicate Keys**: `{ "title": "A", "title": "B" }` → Merge intelligently
2. **Empty Values**: `{ "name": "", "age": null }` → Remove clutter
3. **Inconsistent Case**: Mix of camelCase/snake_case → Standardize
4. **TypeScript Export**: JSON → `export default { ... }`

---

## 🚀 Step-by-Step Guide

### Step 1: Open JSON Rewriter

1. Launch Clarify application
2. Click **View** menu
3. Hover over **Docks**
4. Select **JSON Rewriter Dock**

*Alternative:* Look for "JSON Rewriter" panel in main window

---

### Step 2: Load Input File

1. In **Input Path** field, click **Browse**
2. Navigate to your JSON file (e.g., `translations.json`)
3. Select the file
4. Click **Open**

**Supported Formats:**
- `.json` (standard JSON)
- `.ts`, `.tsx` (TypeScript with export)
- `.js`, `.jsx` (JavaScript with export)

---

### Step 3: Set Output Path

1. In **Output Path** field, click **Browse**
2. Choose where to save the cleaned JSON
3. Enter filename (e.g., `cleaned.json`)
4. Click **Save**

**Tip:** Use different name to compare before/after

---

### Step 4: Choose Operations

JSON Rewriter offers several powerful operations:

#### ✅ Eliminate Duplicates
**What it does:** Merges duplicate keys intelligently

**Example:**
```json
// Before
{
  "user": {
    "name": "John",
    "name": "Jane"
  }
}

// After
{
  "user": {
    "name": "Jane"  // Keeps last value
  }
}
```

**When to use:**
- After merging multiple translation files
- When you have conflicting keys
- To clean up manual edits

---

#### ✅ Join Keys
**What it does:** Flattens nested duplicate paths

**Example:**
```json
// Before
{
  "pages": {
    "home": { "title": "Home" }
  },
  "pages": {
    "about": { "title": "About" }
  }
}

// After
{
  "pages": {
    "home": { "title": "Home" },
    "about": { "title": "About" }
  }
}
```

---

#### ✅ Skip Empty Values
**What it does:** Removes keys with empty strings or null values

**Example:**
```json
// Before
{
  "name": "John",
  "email": "",
  "phone": null,
  "address": "123 Main St"
}

// After
{
  "name": "John",
  "address": "123 Main St"
}
```

**When to use:**
- After data import/export
- To reduce file size
- Before committing to version control

---

#### ✅ Enforce Consistent Case
**What it does:** Converts all keys to chosen case style

**Options:**
- `camelCase` (default)
- `PascalCase`
- `snake_case`
- `kebab-case`

**Example:**
```json
// Before (mixed)
{
  "user_name": "John",
  "UserEmail": "john@example.com",
  "phone-number": "555-1234"
}

// After (camelCase)
{
  "userName": "John",
  "userEmail": "john@example.com",
  "phoneNumber": "555-1234"
}
```

---

### Step 5: Configure Output Format

#### TypeScript Output
- **Check** "Emit Export Const" for:
  ```ts
  export const translations = { ... };
  ```
- **Uncheck** for plain JSON

#### Indentation
- **Indent Size**: Number of spaces (default: 2)
- Larger = more readable, smaller = smaller file

---

### Step 6: Process

1. Review selected operations:
   - ✅ Eliminate Duplicates
   - ✅ Skip Empty Values
   - ✅ Enforce Consistent Case (camelCase)
2. Click **Process** button
3. Wait for progress indicator
4. Check **Results** panel for summary

**Success Message:**
```
✓ Processed translations.json
✓ Removed 15 duplicate keys
✓ Cleaned 8 empty values
✓ Converted 23 keys to camelCase
✓ Saved to cleaned.json
```

---

## 🎓 Example Walkthrough

### Scenario: Clean Messy Translation File

**Problem:** Merged `en.json` and `en-backup.json`, now have duplicates and inconsistencies

**Input File: `messy-translations.json`**
```json
{
  "auth": {
    "login_title": "Sign In",
    "LoginTitle": "Log In",  // duplicate (different case)
    "forgot_password": "Forgot Password",
    "email_placeholder": "",  // empty
    "password_hint": null  // null
  },
  "auth": {  // duplicate section
    "SignupTitle": "Create Account"
  }
}
```

**Steps:**
1. **Input Path**: `messy-translations.json`
2. **Output Path**: `clean-translations.json`
3. **Operations:**
   - ✅ Eliminate Duplicates
   - ✅ Join Keys
   - ✅ Skip Empty Values
   - ✅ Enforce Consistent Case (camelCase)
4. Click **Process**

**Output File: `clean-translations.json`**
```json
{
  "auth": {
    "loginTitle": "Log In",
    "forgotPassword": "Forgot Password",
    "signupTitle": "Create Account"
  }
}
```

**What happened:**
1. ✅ Merged duplicate `auth` sections
2. ✅ Kept last value for `login_title` → `loginTitle`
3. ✅ Removed empty `email_placeholder`
4. ✅ Removed null `password_hint`
5. ✅ Converted all keys to camelCase

---

## 💡 Tips & Best Practices

### Tip 1: Process in Stages
For complex JSON:
1. **First pass**: Eliminate Duplicates only
2. **Review** output
3. **Second pass**: Skip Empty Values
4. **Review** again
5. **Third pass**: Enforce Consistent Case

**Why?** Easier to verify each transformation

---

### Tip 2: Keep Original
Always output to a **different file**:
- ✅ `translations-cleaned.json`
- ❌ Overwriting `translations.json` directly

**Why?** Easy to compare and rollback if needed

---

### Tip 3: Use TypeScript Export for Type Safety
If using TypeScript:
```ts
// Enable "Emit Export Const"
export const translations = {
  auth: {
    loginTitle: "Sign In"
  }
};

// Now get autocomplete!
import { translations } from './translations';
console.log(translations.auth.loginTitle); // ✓ Type-safe
```

---

### Tip 4: Choose Right Case Style
| Case Style | Best For | Example |
|------------|----------|---------|
| `camelCase` | JavaScript/TypeScript objects | `userName` |
| `PascalCase` | Component names, classes | `UserName` |
| `snake_case` | Python, database columns | `user_name` |
| `kebab-case` | CSS classes, URLs | `user-name` |

---

### Tip 5: Combine with JSON Translate
Workflow:
1. **JSON Translate**: Extract text from code → `raw.json`
2. **JSON Rewriter**: Clean `raw.json` → `clean.json`
3. **Search & Replace**: Use `clean.json` keys in code

---

## ⚠️ Common Issues

### Issue 1: Keys Disappear
**Problem:** Output has fewer keys than expected  
**Solution:** 
- Check if "Skip Empty Values" removed them (intended)
- Verify duplicates were merged (intended)
- Disable operations one by one to find culprit

### Issue 2: TypeScript Export Invalid
**Problem:** `.ts` file won't compile  
**Solution:**
- Ensure "Emit Export Const" is checked
- Verify output has proper TypeScript syntax
- Check for special characters in keys (use quotes)

### Issue 3: Case Conversion Wrong
**Problem:** `HTTPSConnection` → `httpsConnection` (wanted `httpsConnection`)  
**Solution:**
- This is expected behavior (acronyms lowercase)
- Manually edit if specific acronym capitalization needed
- Or don't use "Enforce Consistent Case"

---

## 🔧 Advanced Operations

### Normalize Escaping
**What it does:** Fixes over-escaped strings

**Example:**
```json
// Before
{
  "quote": "He said \\\"Hello\\\""
}

// After
{
  "quote": "He said \"Hello\""
}
```

**When to use:** After importing from external sources

---

### Array to Object Conversion
**What it does:** Converts arrays to objects with generated keys

**Example:**
```json
// Before
{
  "items": ["Apple", "Banana", "Cherry"]
}

// After
{
  "items": {
    "apple": "Apple",
    "banana": "Banana",
    "cherry": "Cherry"
  }
}
```

**When to use:** When you need key-based access instead of index-based

---

## 🎯 Next Steps

**You've mastered JSON Rewriter basics!** 🎉

### What's Next?
1. **Practice**: Clean your own project's JSON files
2. **Combine Tools**: JSON Translate → JSON Rewriter → Search & Replace
3. **Advanced**: Learn about scope filtering and conditional processing

### Recommended Workflow
```
1. JSON Translate: Extract text → messy.json
2. JSON Rewriter: Clean messy.json → clean.json
3. Search & Replace: Use clean.json keys in code
4. Repeat for other languages (es.json, fr.json, etc.)
```

### Need Help?
- **AI Assistant**: Help → AI Assistant → "How do I merge JSON files?"
- **Tutorials**: Check [Tutorial Index](../../README.md)
- **Issues**: [GitHub](https://github.com/JosueAmaral15/clarify/issues)

---

**Tutorial by**: Josué Amaral  
**Last Updated**: November 30, 2025
