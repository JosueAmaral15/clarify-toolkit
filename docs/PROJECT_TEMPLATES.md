# Project Templates System

## Overview
Quick project setup with pre-configured templates.

## Built-in Templates

### 🌐 json_translation
Multi-language JSON translation project with English and Portuguese files.

### 📝 text_processing
Text processing pipeline with input/output folders and sample data.

### 🔧 json_rewriter
JSON cleanup and reformatting project structure.

### 🤖 ai_processing
AI text processing project with prompts folder.

### 📂 blank
Basic project structure with input/output folders and README.

## Usage

**Create from Template**:
```
File → New from Template... (Ctrl+Shift+N)
```

**Custom Templates**:
```python
from src.template_manager import get_template_manager

manager = get_template_manager()
manager.create_template_from_directory(source_dir, "My Template", "custom")
```

## Storage
Templates: `~/.config/clarify/templates/`
