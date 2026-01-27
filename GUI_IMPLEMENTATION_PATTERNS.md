# CLARIFY GUI v3.0 - IMPLEMENTATION PATTERNS & CODE EXAMPLES

*Practical guide to GUI component patterns used in Clarify*

## DOCK IMPLEMENTATION PATTERNS

### Pattern 1: StandardToolDock (Full-Featured Tool)

**When to use**: Tools that need file input, options, results display, buttons

```python
from src.gui.base_dock import StandardToolDock
from PySide6.QtWidgets import QGroupBox, QVBoxLayout

class TextExtractorDock(StandardToolDock):
    """
    Extract text patterns from files.
    Inherits: file input, results display, validation, action buttons
    """
    
    def __init__(self, parent=None):
        super().__init__('Text Extractor', parent)
    
    def _setup_ui(self):
        # Input section
        lbl_file, ed_file, btn_browse, chk_is_file = self.create_file_input(
            label_text='Select file or folder:',
            placeholder='Path to scan'
        )
        
        lbl_ext, ed_ext = self.create_extension_filter(
            default_extensions='.py,.js,.ts'
        )
        
        # Options section
        options = [
            ('Case sensitive', False, 'Match case exactly'),
            ('Whole words', False, 'Match whole words only'),
            ('Regex mode', False, 'Use regular expressions'),
        ]
        self.chk_options = self.create_checkbox_group(options)
        
        # Results section
        lbl_results, self.txt_results = self.create_results_panel(
            label_text='Extracted patterns:'
        )
        
        # Buttons
        btn_layout = self.create_action_buttons([
            ('Extract', self._on_extract),
            ('Clear', self._on_clear),
        ])
        
        # Assemble
        self.layout.addWidget(lbl_file)
        self.layout.addWidget(ed_file)
        self.layout.addWidget(btn_browse)
        self.layout.addWidget(lbl_ext)
        self.layout.addWidget(ed_ext)
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.txt_results, 1)  # Stretch
        self.layout.addLayout(btn_layout)
        
        # Store references
        self.ed_file = ed_file
        self.btn_browse = btn_browse
        self.ed_ext = ed_ext
    
    def _connect_signals(self):
        self.btn_browse.clicked.connect(self._on_browse)
        # Enable Enter key for execution
        self._setup_enter_key_execution(self.ed_file)
    
    def _execute_action(self):
        self._on_extract()
    
    def _on_browse(self):
        is_file = True  # or get from checkbox
        self.browse_file_or_directory(
            self.ed_file,
            is_file=is_file,
            title='Select file or folder'
        )
    
    def _on_extract(self):
        file_path = self.ed_file.text()
        extensions = self.ed_ext.text()
        
        # Validate
        is_valid, error = self.validate_file_path(file_path)
        if not is_valid:
            self.show_error('Invalid Path', error)
            return
        
        # Process with worker (v2.9.0)
        from src.gui.workers.text_extractor_worker import TextExtractorWorker
        
        self.worker = TextExtractorWorker(file_path, extensions)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_ok.connect(self._on_success)
        self.worker.failed.connect(self._on_error)
        self.worker.start()
    
    def _on_progress(self, message):
        self.append_result(self.txt_results, message)
    
    def _on_success(self, result):
        self.show_info('Success', f'Extracted {result["count"]} items')
    
    def _on_error(self, error):
        self.show_error('Error', error)
    
    def _on_clear(self):
        self.clear_results(self.txt_results)
```

### Pattern 2: BaseDock (Specialized Tool)

**When to use**: Tools with custom UI not covered by mixins

```python
from src.gui.base_dock import BaseDock
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QSpinBox
)
from PySide6.QtCore import Qt

class CalculatorDock(BaseDock):
    """
    Specialized calculator dock with custom UI.
    Doesn't use mixins - fully custom implementation.
    """
    
    def __init__(self, parent=None):
        super().__init__('Calculator', parent)
    
    def _setup_ui(self):
        # Custom UI setup
        main_layout = QVBoxLayout(self.main_widget)
        
        # Number input row
        input_layout = QHBoxLayout()
        lbl_num = QLabel('Enter numbers (comma-separated):')
        self.ed_numbers = QLineEdit()
        input_layout.addWidget(lbl_num)
        input_layout.addWidget(self.ed_numbers)
        main_layout.addLayout(input_layout)
        
        # Operation buttons
        button_layout = QHBoxLayout()
        for op_name, op_symbol in [('Sum', '∑'), ('Mean', 'μ'), ('Median', 'M')]:
            btn = QPushButton(f'{op_name} {op_symbol}')
            btn.clicked.connect(lambda checked, o=op_name: self._on_operation(o))
            button_layout.addWidget(btn)
        main_layout.addLayout(button_layout)
        
        # Results table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['Metric', 'Value'])
        main_layout.addWidget(self.table)
    
    def _on_operation(self, operation):
        try:
            numbers = [float(x.strip()) for x in self.ed_numbers.text().split(',')]
            
            if operation == 'Sum':
                result = sum(numbers)
            elif operation == 'Mean':
                result = sum(numbers) / len(numbers)
            elif operation == 'Median':
                sorted_nums = sorted(numbers)
                n = len(sorted_nums)
                result = sorted_nums[n//2]
            
            # Add to table
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(operation))
            self.table.setItem(row, 1, QTableWidgetItem(str(result)))
        
        except Exception as e:
            self.show_error('Invalid Input', str(e))
```

## WORKER IMPLEMENTATION PATTERN

### Background Processing Worker

```python
from src.gui.base_dock import ProcessorWorkerBase
import time

class TextExtractorWorker(ProcessorWorkerBase):
    """
    Background worker for text extraction.
    Inherits signal interface from ProcessorWorkerBase:
    - progress(str): Emitted during processing
    - finished_ok(object): Emitted with result on success
    - failed(str): Emitted with error message on failure
    """
    
    def __init__(self, file_path, extensions):
        super().__init__()
        self.file_path = file_path
        self.extensions = extensions
    
    def run(self):
        """Main worker thread execution"""
        try:
            self.emit_progress(f'Starting extraction...')
            
            # Check for interrupt at regular intervals
            for i, file in enumerate(self.get_files()):
                if self.check_interrupt():
                    self.emit_error('Operation cancelled')
                    return
                
                # Do work
                results = self.extract_from_file(file)
                
                # Report progress
                self.emit_progress(f'Processed {file}: {len(results)} items')
            
            # Emit success with result
            self.emit_success({
                'count': len(results),
                'data': results
            })
        
        except Exception as e:
            # Emit error
            self.emit_error(f'Error: {str(e)}')
    
    def get_files(self):
        """Get list of files to process"""
        # Implementation...
        pass
    
    def extract_from_file(self, file_path):
        """Extract data from file"""
        # Implementation...
        pass
```

## SIGNAL/SLOT CONNECTION PATTERNS

### Pattern 1: Direct Signal Connection

```python
def _connect_signals(self):
    # Button click
    self.btn_process.clicked.connect(self._on_process)
    
    # Text change
    self.ed_input.textChanged.connect(self._on_text_changed)
    
    # Selection change
    self.combo_option.currentIndexChanged.connect(self._on_option_changed)
```

### Pattern 2: Worker Signal Connection

```python
def _on_process(self):
    worker = MyWorker(data)
    
    # Connect worker signals
    worker.progress.connect(self._on_progress)
    worker.finished_ok.connect(self._on_success)
    worker.failed.connect(self._on_error)
    
    # Store for later access (e.g., to cancel)
    self.worker = worker
    
    # Start processing
    worker.start()

def _on_progress(self, message):
    self.lbl_status.setText(message)

def _on_success(self, result):
    self.display_results(result)
    self.show_info('Success', 'Processing complete')

def _on_error(self, error):
    self.show_error('Error', error)
    self.lbl_status.setText('Error occurred')
```

## MIXIN USAGE PATTERNS

### Using FileInputMixin

```python
class MyDock(BaseDock, FileInputMixin):
    def _setup_ui(self):
        # Create file input with browse button
        lbl, line_edit, btn_browse, is_file_chk = self.create_file_input(
            label_text='Select source:',
            placeholder='File or folder path',
            with_is_file_checkbox=True
        )
        
        # Create extension filter
        lbl_ext, ed_ext = self.create_extension_filter(
            default_extensions='.json,.yaml,.xml'
        )
        
        self.layout.addWidget(lbl)
        self.layout.addWidget(line_edit)
        self.layout.addWidget(btn_browse)
        self.layout.addWidget(is_file_chk)
        self.layout.addWidget(lbl_ext)
        self.layout.addWidget(ed_ext)
    
    def _connect_signals(self):
        btn_browse.clicked.connect(lambda: self.browse_file_or_directory(
            line_edit,
            is_file=True,
            title='Select file'
        ))
```

### Using ResultsOutputMixin

```python
class MyDock(BaseDock, ResultsOutputMixin):
    def _setup_ui(self):
        # Create results panel with search and context menu
        lbl_results, self.txt_results = self.create_results_panel(
            label_text='Results:'
        )
        
        # Add 'Open in Editor' button
        btn_layout = QHBoxLayout()
        self.add_open_in_editor_button(
            self.txt_results,
            btn_layout,
            button_text='Edit in Editor'
        )
        
        self.layout.addWidget(lbl_results)
        self.layout.addWidget(self.txt_results)
        self.layout.addLayout(btn_layout)
    
    def _on_process(self):
        for item in items:
            self.append_result(self.txt_results, f'Processed: {item}')
        
        self.clear_results(self.txt_results)  # Clear when done
```

## INPUT VALIDATION PATTERNS

### Using ValidationMixin

```python
class MyDock(BaseDock, ValidationMixin):
    def _on_process(self):
        file_path = self.ed_file.text()
        output_path = self.ed_output.text()
        
        # Validate input file
        is_valid, error = self.validate_file_path(file_path, must_exist=True)
        if not is_valid:
            self.show_error('Invalid input', error)
            return
        
        # Validate output path writable
        is_valid, error = self.validate_file_writable(output_path)
        if not is_valid:
            self.show_error('Invalid output', error)
            return
        
        # Validate required field
        is_valid, error = self.validate_not_empty(
            self.ed_pattern.text(),
            'Search pattern'
        )
        if not is_valid:
            self.show_error('Missing field', error)
            return
        
        # All valid, proceed
        self._process()
```

## DOCK CREATION WITH FACTORY

### Using DockFactory

```python
from src.gui.dock_factory import DockFactory
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._create_docks()
    
    def _create_docks(self):
        # Create dock with factory
        DockFactory.create_dock(
            self,
            TextExtractorDock,  # Class
            'dock_text_extractor',  # Attribute name
            area=Qt.RightDockWidgetArea,
            hide=True,  # Initially hidden
            signal_connections={
                'files_changed': self._on_files_changed,
                'results_ready': self._on_results_ready,
            }
        )
        
        # Lazy create dock (only if accessed)
        DockFactory.create_dock_lazy(
            self,
            JsonRewriterDock,
            'dock_json_rewriter'
        )
```

## CREATING CUSTOM WIDGETS

### Custom Widget Template

```python
# Place in src/gui/widgets/my_custom_widget.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal

class MyCustomWidget(QWidget):
    """Custom widget for specific UI needs"""
    
    # Define custom signals
    data_changed = Signal(object)  # Emitted when data changes
    action_triggered = Signal(str)  # Emitted on action
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.lbl = QLabel('Custom Widget')
        self.btn = QPushButton('Click me')
        layout.addWidget(self.lbl)
        layout.addWidget(self.btn)
    
    def _connect_signals(self):
        self.btn.clicked.connect(self._on_button_click)
    
    def _on_button_click(self):
        data = {'action': 'button_clicked'}
        self.data_changed.emit(data)
        self.action_triggered.emit('clicked')
    
    def set_data(self, data):
        """Set widget data"""
        self.lbl.setText(str(data))
```

### Using Custom Widget in Dock

```python
from src.gui.widgets.my_custom_widget import MyCustomWidget

class MyDock(BaseDock):
    def _setup_ui(self):
        self.my_widget = MyCustomWidget()
        self.layout.addWidget(self.my_widget)
    
    def _connect_signals(self):
        self.my_widget.data_changed.connect(self._on_widget_data_changed)
        self.my_widget.action_triggered.connect(self._on_action)
    
    def _on_widget_data_changed(self, data):
        print(f'Widget data: {data}')
```

## BEST PRACTICES

### 1. Always Use Inheritance Over Copy-Paste

❌ **Bad**: Copy dock code and modify
```python
class Tool1Dock(QDockWidget):
    def __init__(self):
        # Repeated code...

class Tool2Dock(QDockWidget):
    def __init__(self):
        # Same repeated code...
```

✅ **Good**: Inherit from StandardToolDock
```python
class Tool1Dock(StandardToolDock):
    def _setup_ui(self):
        # Only custom code

class Tool2Dock(StandardToolDock):
    def _setup_ui(self):
        # Only custom code
```

### 2. Use Mixins for Composition

❌ **Bad**: Large base class with everything
```python
class MegaDock(BaseDock):
    # 1000 lines of mixed concerns
```

✅ **Good**: Compose with mixins
```python
class SpecialDock(BaseDock, FileInputMixin, ValidationMixin):
    # Only needed concerns
```

### 3. Always Use Background Workers for Long Operations

❌ **Bad**: Blocking UI
```python
def _process(self):
    for file in files:  # Blocks UI!
        process_file(file)
```

✅ **Good**: Use worker thread
```python
def _process(self):
    worker = ProcessWorker(files)
    worker.progress.connect(self._on_progress)
    worker.finished_ok.connect(self._on_success)
    worker.start()  # Non-blocking
```

### 4. Validate Early

```python
def _on_execute(self):
    # Validate inputs first
    is_valid, error = self.validate_file_path(self.ed_path.text())
    if not is_valid:
        self.show_error('Invalid', error)
        return
    
    # Then process
    self._process()
```

### 5. Connect Related Signals Together

```python
def _connect_signals(self):
    # Related: file selection and extension filter
    self.btn_browse.clicked.connect(self._on_browse)
    self.ed_file.textChanged.connect(self._on_file_changed)
    
    # Related: option changes
    for chk in self.chk_options:
        chk.stateChanged.connect(self._on_options_changed)
```

## DEBUGGING TIPS

### Debugging Signal Connections

```python
def _connect_signals(self):
    # Add debug print to track emissions
    self.btn.clicked.connect(
        lambda: print('Button clicked!') or self._on_button_click()
    )
    
    # Or use wrapper
    def debug_wrapper(slot):
        def wrapper(*args):
            print(f'Signal triggered: {slot.__name__}')
            return slot(*args)
        return wrapper
    
    self.btn.clicked.connect(debug_wrapper(self._on_button_click))
```

### Checking Worker Status

```python
def _on_process(self):
    worker = MyWorker(data)
    
    # Add status tracking
    worker.progress.connect(lambda msg: print(f'Progress: {msg}'))
    worker.finished_ok.connect(lambda r: print(f'Success: {r}'))
    worker.failed.connect(lambda e: print(f'Error: {e}'))
    
    worker.start()
```

---

## QUICK REFERENCE

| Need | Use |
|------|-----|
| Standard tool | StandardToolDock + mixins |
| Custom UI | BaseDock |
| File selection | FileInputMixin |
| Text results | ResultsOutputMixin |
| Background work | ProcessorWorkerBase |
| Custom widget | widgets/ subdirectory |
| Dialog | Inherit from QDialog |
| Dock creation | DockFactory |

*For more examples, see dock implementations in the codebase*