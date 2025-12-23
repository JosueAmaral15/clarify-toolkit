# Clarify Logging System Documentation

## Overview

The Clarify Logging System provides structured, production-ready logging with:
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Automatic file rotation** (10 MB max size, 5 backups)
- **Dual output** (console with colors + file)
- **Thread-safe operations**
- **Runtime configuration**

## Quick Start

### Basic Usage

```python
from src.utils.logger import get_logger

# Get logger for your module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("General informational message")
logger.warning("Warning: potential issue detected")
logger.error("Error occurred during processing")
logger.critical("Critical failure - application may stop")
```

### Logging Exceptions

```python
try:
    risky_operation()
except Exception:
    logger.error("Operation failed", exc_info=True)  # Includes stack trace
```

### Adding Context

```python
logger.info(
    "User action completed",
    extra={"user_id": 123, "action": "file_save", "duration_ms": 45}
)
```

## Configuration

### Environment Variables

Set `CLARIFY_LOG_LEVEL` to control log verbosity:

```bash
# Linux/Mac
export CLARIFY_LOG_LEVEL=DEBUG

# Windows
set CLARIFY_LOG_LEVEL=DEBUG

# Run application
python clarify.py
```

**Available Levels**:
- `DEBUG`: Detailed information for debugging (most verbose)
- `INFO`: General informational messages (default)
- `WARNING`: Warning messages about potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors causing application malfunction (least verbose)

### Runtime Configuration

```python
from src.utils.logger import set_log_level, get_logger

# Change log level at runtime
set_log_level("DEBUG")  # Enable debug logging

logger = get_logger(__name__)
logger.debug("This will now be logged")

# Revert to INFO
set_log_level("INFO")
```

## Log Files

### Location

Logs are stored in:
- **Linux/Mac**: `~/.clarify/logs/clarify.log`
- **Windows**: `C:\Users\<username>\.clarify\logs\clarify.log`

### File Rotation

- **Max size**: 10 MB per log file
- **Backups**: 5 rotating backups (`clarify.log.1`, `clarify.log.2`, etc.)
- **Total storage**: ~50 MB (10 MB × 5 backups)

### Accessing Log Files

```python
from src.utils.logger import get_log_file

log_file = get_log_file()
print(f"Current log file: {log_file}")

# Read recent logs
with open(log_file, 'r') as f:
    recent_logs = f.readlines()[-100:]  # Last 100 lines
```

### Clearing Logs

```python
from src.utils.logger import clear_all_logs

# WARNING: Permanently deletes all log files!
clear_all_logs()
```

## Integration Examples

### Module-Level Logger

```python
# my_module.py
from src.utils.logger import get_logger

logger = get_logger(__name__)

def process_data(data):
    logger.info(f"Processing {len(data)} items")
    
    try:
        result = heavy_computation(data)
        logger.debug(f"Computation result: {result}")
        return result
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        raise
```

### Class-Based Logger

```python
from src.utils.logger import get_logger

class DataProcessor:
    def __init__(self):
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("DataProcessor initialized")
    
    def process(self, data):
        self.logger.debug(f"Input data: {data}")
        result = self._internal_process(data)
        self.logger.info(f"Processing complete: {len(result)} items")
        return result
```

### GUI Integration

```python
from PySide6.QtWidgets import QMainWindow
from src.utils.logger import get_logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = get_logger("clarify.gui.MainWindow")
        self.logger.info("MainWindow initialized")
        
        self._setup_ui()
    
    def on_button_clicked(self):
        self.logger.debug("Button clicked")
        try:
            self.perform_action()
        except Exception as e:
            self.logger.error(f"Action failed: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", str(e))
```

## Log Format

### Console Output (with colors)

```
2025-12-10 17:21:57 | INFO     | clarify.app:123 | Application started
2025-12-10 17:21:58 | DEBUG    | clarify.core:45 | Processing file: data.json
2025-12-10 17:21:59 | WARNING  | clarify.api:67 | Slow response: 2.5s
2025-12-10 17:22:00 | ERROR    | clarify.db:89 | Connection failed
```

**Format**: `timestamp | level | logger:line | message`

**Colors** (console only):
- 🔵 DEBUG: Cyan
- 🟢 INFO: Green
- 🟡 WARNING: Yellow
- 🔴 ERROR: Red
- 🟣 CRITICAL: Magenta

### File Output (plain text)

Same format as console but without color codes.

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✅ GOOD: Use correct levels
logger.debug("Variable value: x=5, y=10")  # Detailed debugging
logger.info("File saved successfully")     # General information
logger.warning("Disk space low: 5% free")  # Potential issues
logger.error("Failed to connect to API")   # Errors
logger.critical("Database corrupted!")     # Critical failures

# ❌ BAD: Wrong levels
logger.info("x=5, y=10")         # Too verbose for INFO
logger.error("File saved")       # Not an error
logger.debug("Database failure") # Too critical for DEBUG
```

### 2. Include Context

```python
# ✅ GOOD: Contextual information
logger.info(f"User {user_id} saved file '{filename}' ({file_size} bytes)")
logger.error(f"API request failed: {url} (status={status_code})", exc_info=True)

# ❌ BAD: No context
logger.info("File saved")
logger.error("Request failed")
```

### 3. Use exc_info for Exceptions

```python
# ✅ GOOD: Include stack trace
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)

# ❌ BAD: No stack trace (harder to debug)
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

### 4. Avoid Logging Sensitive Data

```python
# ✅ GOOD: Mask sensitive data
logger.info(f"User {user_id} logged in from {ip}")

# ❌ BAD: Exposing passwords/tokens
logger.info(f"Login: user={username}, pass={password}")  # NEVER!
logger.debug(f"API token: {api_key}")  # NEVER!
```

### 5. Use Module-Level Loggers

```python
# ✅ GOOD: Consistent logger naming
logger = get_logger(__name__)  # Will be "clarify.module_name"

# ❌ BAD: Hardcoded names
logger = get_logger("my_logger")  # Inconsistent
```

## Performance Considerations

### Log Level Filtering

Logging is **cheap when disabled**:

```python
# When log level is INFO, this debug call has minimal overhead
logger.debug(f"Heavy computation: {expensive_function()}")  # Not executed!
```

The message formatting only happens if the log level is enabled.

### Avoid Complex Formatting in Arguments

```python
# ✅ GOOD: Simple formatting
logger.debug("Processing item %s", item_id)

# ❌ BAD: Complex computation in f-string
logger.debug(f"Stats: {compute_heavy_statistics()}")  # Always computed!
```

Use lazy evaluation:

```python
# Formatting only happens if DEBUG is enabled
logger.debug("Stats: %s", lambda: compute_heavy_statistics())
```

## Troubleshooting

### Logs Not Appearing

**Problem**: No log output in console or file.

**Solutions**:
1. Check log level: `set_log_level("DEBUG")`
2. Verify logger name starts with `clarify.`
3. Check file permissions: `~/.clarify/logs/`

### Log File Too Large

**Problem**: Log file exceeds disk quota.

**Solutions**:
1. Reduce `MAX_LOG_SIZE` in `logger.py`
2. Decrease `BACKUP_COUNT`
3. Clear old logs: `clear_all_logs()`
4. Increase log level: `set_log_level("WARNING")`

### Colors Not Working

**Problem**: ANSI codes visible instead of colors.

**Solutions**:
1. Use a terminal with color support (modern terminals)
2. On Windows: Use Windows Terminal or enable ANSI in cmd
3. Disable colors (edit `ColoredFormatter` in `logger.py`)

## API Reference

### Functions

#### `get_logger(name: str) -> logging.Logger`

Get a configured logger instance.

**Parameters**:
- `name`: Logger name (use `__name__` for automatic module naming)

**Returns**: Configured `logging.Logger` instance

**Example**:
```python
logger = get_logger(__name__)
```

#### `set_log_level(level: str) -> None`

Change global log level at runtime.

**Parameters**:
- `level`: Log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Example**:
```python
set_log_level("DEBUG")
```

#### `get_log_file() -> Path`

Get path to current log file.

**Returns**: `Path` object pointing to log file

**Example**:
```python
log_path = get_log_file()
print(f"Logs: {log_path}")
```

#### `clear_all_logs() -> None`

Permanently delete all log files (use with caution!).

**Example**:
```python
clear_all_logs()  # Deletes clarify.log and all backups
```

### Classes

#### `ClarifyLogger`

Singleton logger manager (use `get_logger()` instead of instantiating directly).

**Methods**:
- `get_logger(name: str) -> logging.Logger`
- `set_level(level: str) -> None`
- `get_log_file_path() -> Path`
- `clear_logs() -> None`

### Constants

- `DEFAULT_LOG_LEVEL = logging.INFO`
- `MAX_LOG_SIZE = 10 * 1024 * 1024`  # 10 MB
- `BACKUP_COUNT = 5`  # Keep 5 backups
- `DEFAULT_LOG_DIR = Path.home() / ".clarify" / "logs"`

## Examples

### Complete Example: File Processor

```python
from src.utils.logger import get_logger
from pathlib import Path

logger = get_logger(__name__)

def process_files(directory: str):
    """Process all JSON files in directory."""
    logger.info(f"Starting file processing in: {directory}")
    
    files = list(Path(directory).glob("*.json"))
    logger.info(f"Found {len(files)} JSON files")
    
    processed = 0
    errors = 0
    
    for file in files:
        try:
            logger.debug(f"Processing: {file.name}")
            process_single_file(file)
            processed += 1
            logger.debug(f"Successfully processed: {file.name}")
        except Exception as e:
            errors += 1
            logger.error(
                f"Failed to process {file.name}: {e}",
                exc_info=True,
                extra={"file": str(file), "error_type": type(e).__name__}
            )
    
    logger.info(
        f"Processing complete: {processed} successful, {errors} errors",
        extra={"total": len(files), "success_rate": processed/len(files)*100}
    )
    
    return processed, errors

def process_single_file(file: Path):
    """Process a single JSON file."""
    logger.debug(f"Reading file: {file}")
    
    with open(file, 'r') as f:
        data = json.load(f)
    
    logger.debug(f"File contains {len(data)} items")
    
    # Process data...
    result = transform_data(data)
    
    logger.debug(f"Writing result to: {file}")
    with open(file, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"File processed: {file.name} ({len(result)} items)")
```

### Testing with Logging

```python
import pytest
from src.utils.logger import get_logger, set_log_level

@pytest.fixture(autouse=True)
def setup_logging():
    """Enable DEBUG logging for tests."""
    set_log_level("DEBUG")
    yield
    set_log_level("INFO")  # Restore

def test_my_function(caplog):
    """Test with log capture."""
    logger = get_logger(__name__)
    
    my_function()
    
    # Assert specific logs appeared
    assert "Expected log message" in caplog.text
    assert any(record.levelname == "ERROR" for record in caplog.records)
```

## Version History

- **v2.9.58** (2025-12-10): Initial release
  - Structured logging with rotation
  - Multiple log levels
  - Console and file output
  - Thread-safe operations
  - Runtime configuration

## Support

For issues or questions about the logging system:
1. Check this documentation
2. Review log file: `~/.clarify/logs/clarify.log`
3. Open GitHub issue: https://github.com/JosueAmaral15/clarify/issues
