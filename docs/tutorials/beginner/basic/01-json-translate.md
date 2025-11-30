---
title: "JSON Translate - Basic Tutorial"
category: "beginner/basic"
difficulty: "easy"
estimated_time: "10 minutes"
keywords: ["json", "translate", "i18n", "translation", "internationalization", "react", "vue"]
prerequisites: []
version: "1.0"
last_updated: "2025-11-30"
---

# JSON Translate - Basic Tutorial

**Learn how to extract text from code and create i18n JSON translation files.**

---

## 🎯 What You'll Learn

- Open JSON Translate tool
- Extract text from React/Vue/HTML files
- Generate structured JSON for translations
- Understand the output format

**Time**: ~10 minutes  
**Difficulty**: Easy

---

## 📌 What is JSON Translate?

JSON Translate automatically extracts hardcoded text from your code files and converts them into structured JSON translation files.

**Use Case**: Internationalize your React/Vue app without manually finding every string.

**Before:**
```tsx
function Welcome() {
  return (
    <div>
      <h1>Welcome to our platform</h1>
      <p>Start your journey today</p>
    </div>
  );
}
```

**After (JSON):**
```json
{
  "t": {
    "welcome_to_our_platform": "Welcome to our platform",
    "start_your_journey_today": "Start your journey today"
  }
}
```

---

## 🚀 Step-by-Step Guide

### Step 1: Open JSON Translate

1. Launch Clarify application
2. Click on **Tools** menu (top bar)
3. Select **Open JSON Translate**

*Alternative:* Press `Ctrl+1` (if shortcut is configured)

---

### Step 2: Select Input File

1. In the **Input Path** field, click **Browse** button
2. Navigate to your project folder
3. Select a file (e.g., `HomePage.tsx`, `App.vue`, `index.html`)
4. Click **Open**

**Supported Formats:**
- `.tsx`, `.jsx` (React)
- `.vue` (Vue.js)
- `.html` (Plain HTML)
- `.ts`, `.js` (JavaScript/TypeScript)

---

### Step 3: Choose Output Location

1. In the **Output Path** field, click **Browse** button
2. Navigate to your translations folder (e.g., `locales/`)
3. Type a filename: `en.json` or `translations.json`
4. Click **Save**

**Tip:** Create a `locales/` folder in your project root to organize translations.

---

### Step 4: Configure Options

#### Root Variable Name
- **What it is:** The top-level key in your JSON (default: `t`)
- **Example:** If you use `i18n.pages.home.title` in code, set root to `i18n`
- **Default:** Leave as `t` (most common)

#### Emit Export Const
- **Check this** if you want TypeScript format:
  ```ts
  export const translations = { ... };
  ```
- **Uncheck** for plain JSON:
  ```json
  { ... }
  ```

#### Is File
- **Check this** if processing a single file (default)
- **Uncheck** if processing an entire directory

---

### Step 5: Process

1. Review your settings:
   - ✅ Input file selected
   - ✅ Output path set
   - ✅ Root variable configured
2. Click **Process** button (bottom of panel)
3. Wait for progress indicator (usually 1-5 seconds)
4. Check the **Results** panel for success message

**Success Message:**
```
✓ Processed HomePage.tsx
✓ Extracted 12 translations
✓ Saved to locales/en.json
```

---

### Step 6: Review Output

1. Open the output file (`en.json`) in your code editor
2. Verify the structure:

```json
{
  "t": {
    "homepage": {
      "title": "Welcome to our platform",
      "subtitle": "Start your journey today",
      "button": {
        "get_started": "Get Started",
        "learn_more": "Learn More"
      }
    }
  }
}
```

**Key Features:**
- **Hierarchical structure:** Nested keys match your component structure
- **snake_case keys:** Automatically converted from text
- **Original values:** Preserved exactly as they appear in code

---

## 🎓 Example Walkthrough

### Scenario: Internationalize a Login Page

**Input File: `LoginPage.tsx`**
```tsx
export function LoginPage() {
  return (
    <div>
      <h1>Sign In</h1>
      <p>Enter your credentials</p>
      <button>Login</button>
      <a href="/forgot">Forgot password?</a>
    </div>
  );
}
```

**Steps:**
1. Tools → Open JSON Translate
2. Input Path: `LoginPage.tsx`
3. Output Path: `locales/en.json`
4. Root Variable: `t`
5. Click **Process**

**Output: `en.json`**
```json
{
  "t": {
    "login_page": {
      "sign_in": "Sign In",
      "enter_your_credentials": "Enter your credentials",
      "login": "Login",
      "forgot_password": "Forgot password?"
    }
  }
}
```

**Now use in code:**
```tsx
import { t } from './i18n';

export function LoginPage() {
  return (
    <div>
      <h1>{t.login_page.sign_in}</h1>
      <p>{t.login_page.enter_your_credentials}</p>
      <button>{t.login_page.login}</button>
      <a href="/forgot">{t.login_page.forgot_password}</a>
    </div>
  );
}
```

---

## 💡 Tips & Best Practices

### Tip 1: Organize by Feature
```
locales/
├── en/
│   ├── auth.json      # Authentication strings
│   ├── home.json      # Homepage strings
│   └── settings.json  # Settings strings
└── pt/
    ├── auth.json
    ├── home.json
    └── settings.json
```

### Tip 2: Use Descriptive Keys
✅ **Good:**
```json
{
  "user_dashboard_welcome_message": "Welcome back, {{name}}!"
}
```

❌ **Bad:**
```json
{
  "msg1": "Welcome back, {{name}}!"
}
```

### Tip 3: Handle Plurals
For plurals, use separate keys:
```json
{
  "notification_count_one": "You have 1 notification",
  "notification_count_other": "You have {{count}} notifications"
}
```

### Tip 4: Batch Processing
Process entire directories:
1. **Uncheck** "Is File"
2. **Input Path**: Select folder (e.g., `src/pages/`)
3. **Output Path**: `locales/en.json`
4. All files processed → Single JSON output

---

## ⚠️ Common Issues

### Issue 1: Empty Output
**Problem:** JSON file is empty or has no keys  
**Solution:** Check that your input file contains text strings (not just variables)

### Issue 2: Nested Too Deep
**Problem:** Keys like `t.a.b.c.d.e.f.g.title`  
**Solution:** Simplify component structure or manually edit JSON

### Issue 3: Special Characters
**Problem:** Keys with spaces/symbols: `t.hello world!`  
**Solution:** Clarify automatically converts to snake_case: `t.hello_world`

---

## 🎯 Next Steps

**You've completed JSON Translate basics!** 🎉

### What's Next?
1. [Search & Replace Tutorial](02-search-replace.md) - Replace hardcoded strings with `{t.key}`
2. [JSON Rewriter Tutorial](03-json-rewriter.md) - Clean and merge translation files
3. **Advanced:** Learn about scope filtering and conditional extraction

### Need Help?
- Use **Help → AI Assistant** for questions
- Check [FAQ](../README.md#faq) for common issues
- Report bugs on [GitHub](https://github.com/JosueAmaral15/clarify/issues)

---

**Tutorial by**: Josué Amaral  
**Last Updated**: November 30, 2025
