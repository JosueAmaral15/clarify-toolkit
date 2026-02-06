# Debug Prints Protocol - Study Notes

**Date**: 2026-01-25 19:53 UTC  
**Source**: `/home/josue/Documents/Informática/Programação/protocolos/en/SIMPLICITY_PROTOCOL_3.md`  
**Section**: 🐛 Debugging Strategies: Print-Based Investigation (Lines 7183-7550)

---

## 📋 KEY LEARNINGS

### When to Use Debug Prints

**✅ IDEAL for:**
- Bug is reproducible but cause is unclear
- Need to trace variable values through execution
- Understanding complex conditional logic flow
- Investigating state changes over time
- Quick debugging without setting up debugger tools

**❌ NOT IDEAL for:**
- Production code (use logging frameworks instead)
- Performance-critical sections (prints are slow)
- Multi-threaded code (output may interleave)
- When proper debugger tools are already set up

---

## 🎯 Standardized Format (MANDATORY)

**Universal Template:**
```
DEBUG [LINE_NUMBER] [function_name()] | variable_name: value
```

**Components:**
1. **DEBUG** - Prefix for easy filtering/removal
2. **[LINE_NUMBER]** - Current code line (helps locate print statement)
3. **[function_name()]** - Function/method where print is located
4. **|** - Separator between identification and value
5. **variable_name: value** - What you're inspecting

---

## 💻 Python Examples (Most Relevant)

### Basic Variable Inspection
```python
def calculate_total(items, tax_rate):
    print(f"DEBUG 42 calculate_total() | items: {items}")
    print(f"DEBUG 43 calculate_total() | tax_rate: {tax_rate}")
    
    subtotal = sum(item['price'] for item in items)
    print(f"DEBUG 45 calculate_total() | subtotal: {subtotal}")
    
    tax = subtotal * tax_rate
    print(f"DEBUG 48 calculate_total() | tax: {tax}")
    
    total = subtotal + tax
    print(f"DEBUG 51 calculate_total() | total: {total}")
    
    return total
```

### Execution Flow Markers
```python
def process_order(order_id):
    print(f"DEBUG 100 process_order() | ENTER | order_id: {order_id}")
    
    order = get_order(order_id)
    print(f"DEBUG 103 process_order() | order: {order}")
    
    if order.status == 'pending':
        print(f"DEBUG 106 process_order() | BRANCH: pending status")
        result = validate_order(order)
        print(f"DEBUG 108 process_order() | validation_result: {result}")
    else:
        print(f"DEBUG 110 process_order() | BRANCH: non-pending status")
        result = None
    
    print(f"DEBUG 114 process_order() | EXIT | result: {result}")
    return result
```

---

## ✅ Best Practices

### 1. Use Meaningful Messages
```python
# ❌ Bad
print(x)
print("here")
print(123)

# ✅ Good
print(f"DEBUG 50 process() | user_id: {x}")
print(f"DEBUG 75 validate() | CHECKPOINT: reached validation")
print(f"DEBUG 123 calculate() | iteration_count: {123}")
```

### 2. Show Variable Names AND Values
```python
# ❌ Bad - just the value
print(total)  # What is 42?

# ✅ Good - context included
print(f"DEBUG 30 checkout() | total: {total}")  # total: 42
```

### 3. Log Execution Flow Markers
```python
print(f"DEBUG 100 function() | ENTER")
print(f"DEBUG 103 function() | BRANCH: condition_a = True")
print(f"DEBUG 115 function() | EXIT | result: {result}")
```

### 4. Use Consistent Formatting
```python
print(f"DEBUG 25 main() | user_count: {len(users)}")
print(f"DEBUG 30 main() | active_sessions: {sessions}")
print(f"DEBUG 35 main() | memory_usage: {memory}MB")
```

### 5. Remove or Comment Out After Fixing
```python
def fixed_function():
    # print(f"DEBUG 10 fixed_function() | ENTER")  # Commented out after fix
    result = do_work()
    # print(f"DEBUG 15 fixed_function() | result: {result}")  # Commented out
    return result
```

---

## 🛠️ When to Use Debugger Tools Instead

**Use Debuggers when:**
- ✅ Need to pause execution and inspect state
- ✅ Want to step through code line-by-line
- ✅ Investigating complex object hierarchies
- ✅ Debugging multi-threaded/concurrent code
- ✅ Already familiar with debugger setup

**Use Print Statements when:**
- ✅ Quick investigation (faster than debugger setup)
- ✅ Remote/headless environments (no GUI debugger)
- ✅ Understanding flow over many iterations
- ✅ Debugging intermittent issues (capture logs)
- ✅ Simple bugs in small code sections

---

## 📊 Production Alternative: Logging

**⚠️ Important:** Debug print statements should be **removed before committing** or replaced with proper logging.

### Python: `logging` module
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"process_data() | ENTER | data: {data}")
    
    result = transform(data)
    logger.debug(f"process_data() | result: {result}")
    
    logger.info(f"Successfully processed {len(data)} items")
    return result

# Can be disabled in production with level=logging.INFO
```

---

## 🎯 Application to Clarify Project

For investigating bugs in Clarify (like the GoogleTranslateDock crash):

### Example: Debugging _show_search_replace()
```python
def _show_search_replace(self):
    """Show Search/Replace tab (v2.9.40.2 - reopen if closed)."""
    print(f"DEBUG 562 _show_search_replace() | ENTER")
    
    tab_name = tr("ui_builder.tab_search")
    print(f"DEBUG 564 _show_search_replace() | tab_name: '{tab_name}'")
    
    tab_count = self.tabs.count()
    print(f"DEBUG 567 _show_search_replace() | tab_count: {tab_count}")
    
    if tab_count > 0:
        current_tab_name = self.tabs.tabText(0)
        print(f"DEBUG 571 _show_search_replace() | current_tab_name: '{current_tab_name}'")
        print(f"DEBUG 572 _show_search_replace() | match: {current_tab_name == tab_name}")
    
    if self.tabs.count() > 0 and self.tabs.tabText(0) == tab_name:
        print(f"DEBUG 575 _show_search_replace() | BRANCH: tab exists, switching")
        self.tabs.setCurrentIndex(0)
    else:
        print(f"DEBUG 578 _show_search_replace() | BRANCH: creating new tab")
        self.tab_search = SearchReplacePanel(parent=self, progress_manager=self.progress_manager)
        self.tabs.insertTab(0, self.tab_search, tab_name)
        self.tabs.setCurrentIndex(0)
        QApplication.processEvents()
    
    print(f"DEBUG 584 _show_search_replace() | EXIT")
```

---

## 📝 Summary

**I understand the protocol about debug prints:**

1. ✅ Use standardized format: `DEBUG [LINE] [function()] | var: value`
2. ✅ Add ENTER/EXIT markers for flow
3. ✅ Add BRANCH markers for conditionals
4. ✅ Include line numbers for easy location
5. ✅ Show variable names AND values
6. ✅ Remove/comment out after fixing
7. ✅ Use logging framework for production

**When to apply:**
- Investigating unclear bugs (like missing methods, wrong behavior)
- Tracing execution flow through complex logic
- Understanding variable states at specific points
- Quick debugging without debugger setup

**Status**: ✅ Protocol section read and understood
