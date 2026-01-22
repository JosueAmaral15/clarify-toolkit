# Code Study Session 7 Notes
**Programmer #7 - Source Code Study**  
**Date**: 2026-01-22  
**Session Focus**: Phase 3 - Utility Modules Completion (src/utils/)  
**Files Studied**: 4 files (~1,429 lines)

---

## 📋 Session Overview

**Progress**:
- **Files Studied This Session**: 4 files
- **Lines of Code**: ~1,429 lines
- **Total Progress**: 32/196 files (16.3%)
- **Phase**: Phase 3 - Feature Modules (Utils Module COMPLETE ✅)

**Files Analyzed**:
1. `src/utils/error_handler.py` (471 lines) ✅
2. `src/utils/error_reporter.py` (255 lines) ✅
3. `src/utils/update_checker.py` (286 lines) ✅
4. `src/utils/file_finder.py` (417 lines) ✅

**Utils Module Status**: ✅ **100% COMPLETE** (9/9 files, ~2,304 lines)

---

## 🔍 Detailed Analysis

### 1. error_handler.py (471 lines) - Crash Handler System

**Purpose**: Global exception handler with crash reporting

**Author**: Josué Amaral (Sprint v2.9.61 - Error Reporting & Crash Handler)

**Features**:
- ✅ Global exception handler (catches unhandled exceptions)
- ✅ Error dialog with user-friendly messages (GUI integration)
- ✅ Optional error reporting to GitHub Issues
- ✅ Stack trace capture with context
- ✅ Integration with logging system (v2.9.58)
- ✅ Privacy-aware (strips sensitive paths)
- ✅ Crash report file generation
- ✅ Crash frequency tracking

---

#### **CrashHandler Class** (Lines 47-396)

**Pattern**: Singleton

**Attributes**:
```python
_instance: Optional['CrashHandler'] = None  # Singleton instance
_original_excepthook: Optional[Callable] = None  # Backup of sys.excepthook

enabled: bool  # Whether crash handler is active
show_dialog: bool  # Show error dialog to user (GUI mode)
report_crashes: bool  # Send crash reports to GitHub (opt-in)
callback: Callable  # Custom callback after handling error
_crash_count: int  # Number of crashes in session
_last_crash_time: Optional[datetime]  # Timestamp of last crash
```

**Constructor** (Lines 64-84):
```python
def __init__(
    self,
    show_dialog: bool = True,  # Requires GUI (PySide6)
    report_crashes: bool = False,  # Opt-in
    callback: Optional[Callable[[Exception, str], None]] = None
):
    self.enabled = False
    self.show_dialog = show_dialog
    self.report_crashes = report_crashes
    self.callback = callback
    self._crash_count = 0
    self._last_crash_time = None
```

---

#### **install() Method** (Lines 97-106)

**Purpose**: Install as global exception handler

```python
def install(self):
    if self.enabled:
        logger.warning("Crash handler already installed")
        return
    
    self._original_excepthook = sys.excepthook  # Backup
    sys.excepthook = self._exception_handler  # Override
    self.enabled = True
    logger.info("Crash handler installed successfully")
```

**Key Feature**: Preserves original excepthook for restoration

---

#### **uninstall() Method** (Lines 108-118)

**Purpose**: Restore original exception handler

```python
def uninstall(self):
    if not self.enabled:
        return
    
    if self._original_excepthook:
        sys.excepthook = self._original_excepthook  # Restore
        self._original_excepthook = None
    
    self.enabled = False
    logger.info("Crash handler uninstalled")
```

**Use Case**: Clean shutdown, testing, debugging

---

#### **_exception_handler() Method** (Lines 120-185)

**Purpose**: Handle uncaught exception

**Algorithm**:
```python
def _exception_handler(self, exc_type, exc_value, exc_traceback):
    # 1. Skip KeyboardInterrupt (Ctrl+C)
    if issubclass(exc_type, KeyboardInterrupt):
        if self._original_excepthook:
            self._original_excepthook(exc_type, exc_value, exc_traceback)
        return
    
    # 2. Track crash frequency
    now = datetime.now()
    self._crash_count += 1
    self._last_crash_time = now
    
    # 3. Format traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = ''.join(tb_lines)
    
    # 4. Strip sensitive paths (privacy!)
    tb_text_clean = self._strip_sensitive_paths(tb_text)
    
    # 5. Log error (critical level)
    logger.critical(
        f"Unhandled exception ({self._crash_count} crashes):\n{tb_text_clean}",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # 6. Save crash report to file
    crash_file = self._save_crash_report(exc_type, exc_value, tb_text_clean)
    logger.info(f"Crash report saved to {crash_file}")
    
    # 7. Show dialog to user (if GUI available)
    if self.show_dialog:
        try:
            self._show_error_dialog(exc_value, tb_text_clean, crash_file)
        except Exception as e:
            logger.error(f"Failed to show error dialog: {e}")
    
    # 8. Send report to GitHub (if enabled - not yet implemented)
    if self.report_crashes:
        try:
            self._send_crash_report(exc_value, tb_text_clean)
        except Exception as e:
            logger.error(f"Failed to send crash report: {e}")
    
    # 9. Call custom callback
    if self.callback:
        try:
            self.callback(exc_value, tb_text_clean)
        except Exception as e:
            logger.error(f"Error in crash handler callback: {e}")
    
    # 10. Call original handler (prints to stderr)
    if self._original_excepthook:
        self._original_excepthook(exc_type, exc_value, exc_traceback)
```

**Key Features**:
- ✅ Crash frequency tracking (detect crash loops)
- ✅ Privacy protection (path stripping)
- ✅ Multi-channel reporting (log, file, dialog, callback)
- ✅ Graceful degradation (dialog failures don't stop logging)
- ✅ Preserves Ctrl+C behavior (KeyboardInterrupt passthrough)

---

#### **_strip_sensitive_paths() Method** (Lines 187-218)

**Purpose**: Strip sensitive file paths from traceback (GDPR/privacy compliance)

```python
def _strip_sensitive_paths(self, text: str) -> str:
    try:
        home = str(Path.home())
        cwd = str(Path.cwd())
        
        # Replace home directory
        text = text.replace(home, "~")
        
        # Replace current directory
        text = text.replace(cwd, ".")
        
        # Replace common system paths
        text = text.replace("/usr/local/lib/python", "python")
        text = text.replace("/usr/lib/python", "python")
        text = text.replace("C:\\Users\\", "~\\")  # Windows
        text = text.replace("C:\\Program Files\\", "")  # Windows
        
    except Exception as e:
        logger.warning(f"Failed to strip sensitive paths: {e}")
    
    return text
```

**Example**:
```
Before: File "/home/josue/clarify/src/app.py", line 123
After:  File "~/clarify/src/app.py", line 123
```

**Critical**: Prevents leaking username, full paths in crash reports

---

#### **_save_crash_report() Method** (Lines 220-278)

**Purpose**: Save crash report to file

**Location**: `~/.config/clarify/crashes/crash_YYYYMMDD_HHMMSS.txt`

**Algorithm**:
```python
def _save_crash_report(self, exc_type, exc_value, tb_text) -> Path:
    # 1. Create crash reports directory
    crash_dir = Path.home() / ".config" / "clarify" / "crashes"
    crash_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_file = crash_dir / f"crash_{timestamp}.txt"
    
    # 3. Gather system information
    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "crash_time": datetime.now().isoformat(),
        "crash_count": self._crash_count,
        "exception_type": exc_type.__name__,
        "exception_message": str(exc_value),
    }
    
    # 4. Write crash report
    with open(crash_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("CLARIFY CRASH REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("System Information:\n")
        f.write("-" * 80 + "\n")
        for key, value in system_info.items():
            f.write(f"{key}: {value}\n")
        f.write("\n")
        
        f.write("Traceback:\n")
        f.write("-" * 80 + "\n")
        f.write(tb_text)
        f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("End of crash report\n")
        f.write("=" * 80 + "\n")
    
    return crash_file
```

**Report Format**:
```
================================================================================
CLARIFY CRASH REPORT
================================================================================

System Information:
--------------------------------------------------------------------------------
platform: Linux-5.15.0-1051-gcp-x86_64-with-glibc2.35
python_version: 3.12.1
crash_time: 2026-01-22T19:08:30.123456
crash_count: 1
exception_type: ValueError
exception_message: Invalid configuration

Traceback:
--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "~/clarify/src/app.py", line 123, in load_config
    ...
ValueError: Invalid configuration

================================================================================
End of crash report
================================================================================
```

---

#### **_show_error_dialog() Method** (Lines 280-335)

**Purpose**: Show error dialog to user (GUI only)

```python
def _show_error_dialog(self, exception, traceback_text, crash_file):
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        
        # Ensure QApplication exists
        app = QApplication.instance()
        if not app:
            logger.warning("No QApplication instance, cannot show dialog")
            return
        
        # Create error dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Clarify - Unexpected Error")
        msg.setText(
            f"<b>An unexpected error occurred:</b><br><br>"
            f"<code>{type(exception).__name__}: {str(exception)}</code>"
        )
        msg.setInformativeText(
            f"The application may be in an unstable state. "
            f"It's recommended to save your work and restart.<br><br>"
            f"Crash report saved to:<br>"
            f"<code>{crash_file}</code>"
        )
        msg.setDetailedText(traceback_text)  # Expandable section
        msg.setStandardButtons(QMessageBox.Close)
        msg.setDefaultButton(QMessageBox.Close)
        
        # Add "Report Bug" button if reporting enabled
        if self.report_crashes:
            report_btn = msg.addButton("Report Bug", QMessageBox.ActionRole)
        
        result = msg.exec()
        
        # Handle "Report Bug" click
        if self.report_crashes and msg.clickedButton() == report_btn:
            self._send_crash_report(exception, traceback_text)
    
    except ImportError:
        logger.warning("PySide6 not available, cannot show error dialog")
    except Exception as e:
        logger.error(f"Error showing dialog: {e}")
```

**Key Features**:
- ✅ User-friendly message (not raw traceback)
- ✅ Detailed text in expandable section
- ✅ Crash report file path displayed
- ✅ Optional "Report Bug" button
- ✅ Graceful fallback (if dialog fails, logs still work)

---

#### **_send_crash_report() Method** (Lines 337-352)

**Purpose**: Send crash report to GitHub Issues (opt-in, not yet implemented)

```python
def _send_crash_report(self, exception, traceback_text):
    # Note: This is a placeholder for future implementation
    logger.info("Crash report sending not yet implemented")
    
    # Future implementation could:
    # 1. Use GitHub API to create issue
    # 2. Send email with crash details
    # 3. POST to error tracking service (Sentry, Rollbar)
```

**Status**: Placeholder (v2.9.61+)

---

#### **handle_errors() Context Manager** (Lines 354-395)

**Purpose**: Handle errors in specific code blocks

**Usage**:
```python
with CrashHandler.handle_errors():
    risky_operation()
```

**Implementation**:
```python
@staticmethod
@contextmanager
def handle_errors(
    show_dialog: bool = False,
    callback: Optional[Callable[[Exception], None]] = None
):
    try:
        yield
    except Exception as e:
        # Log error
        logger.error(f"Error in handled context: {e}", exc_info=True)
        
        # Show dialog if requested
        if show_dialog:
            try:
                handler = CrashHandler.get_instance()
                tb_text = traceback.format_exc()
                crash_file = handler._save_crash_report(type(e), e, tb_text)
                handler._show_error_dialog(e, tb_text, crash_file)
            except Exception as dialog_error:
                logger.error(f"Failed to show error dialog: {dialog_error}")
        
        # Call custom callback
        if callback:
            try:
                callback(e)
            except Exception as callback_error:
                logger.error(f"Error in callback: {callback_error}")
        
        # Re-raise exception
        raise
```

**Key Feature**: Re-raises exception (doesn't swallow errors)

---

#### **Module Functions** (Lines 398-435)

**install_crash_handler()** (Lines 398-425):
```python
def install_crash_handler(
    show_dialog: bool = True,
    report_crashes: bool = False,
    callback: Optional[Callable[[Exception, str], None]] = None
) -> CrashHandler:
    """Install global crash handler at application startup."""
    handler = CrashHandler(
        show_dialog=show_dialog,
        report_crashes=report_crashes,
        callback=callback
    )
    handler.install()
    return handler
```

**uninstall_crash_handler()** (Lines 428-435):
```python
def uninstall_crash_handler():
    """Uninstall global crash handler. Restores original sys.excepthook."""
    handler = CrashHandler.get_instance()
    handler.uninstall()
```

---

### 2. error_reporter.py (255 lines) - GitHub Issue Reporter

**Purpose**: Global error reporter with GitHub Issues integration

**Note**: Earlier/alternative implementation to error_handler.py

---

#### **ErrorReporter Class** (Lines 16-230)

**Features**:
- Global exception handler
- GitHub issue URL generation
- System info collection
- Settings integration (QSettings)
- Privacy controls (opt-in system info)

**Constructor** (Lines 19-28):
```python
def __init__(self, app_version: str = "2.9.89"):
    self.app_version = app_version
    self.settings = QSettings("Clarify", "Clarify")
    self.dialog = None  # Will be set by app
```

---

#### **Settings Integration** (Lines 34-44)

```python
def is_enabled(self) -> bool:
    return self.settings.value("error_reporting/enabled", True, type=bool)

def should_include_system_info(self) -> bool:
    return self.settings.value("error_reporting/include_system_info", True, type=bool)

def should_auto_open_github(self) -> bool:
    return self.settings.value("error_reporting/auto_open_github", False, type=bool)
```

**Key Feature**: User-controlled privacy settings

---

#### **format_error() Method** (Lines 81-114)

**Purpose**: Format exception into structured dict

```python
def format_error(self, exc_type, exc_value, exc_traceback) -> dict:
    # Extract traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    full_traceback = "".join(tb_lines)
    
    # Get last frame info
    last_frame = traceback.extract_tb(exc_traceback)[-1] if exc_traceback else None
    
    error_info = {
        "type": exc_type.__name__,
        "message": str(exc_value),
        "full_traceback": full_traceback,
        "timestamp": datetime.now().isoformat(),
        "file": last_frame.filename if last_frame else "Unknown",
        "line": last_frame.lineno if last_frame else 0,
        "function": last_frame.name if last_frame else "Unknown",
    }
    
    # Add system info if enabled
    if self.should_include_system_info():
        error_info["system_info"] = self.get_system_info()
    
    return error_info
```

**Output**:
```python
{
    "type": "ValueError",
    "message": "Invalid configuration",
    "full_traceback": "Traceback ...",
    "timestamp": "2026-01-22T19:08:30.123456",
    "file": "/home/user/clarify/src/app.py",
    "line": 123,
    "function": "load_config",
    "system_info": { ... }
}
```

---

#### **get_system_info() Method** (Lines 116-137)

**Purpose**: Collect system information for debugging

```python
def get_system_info(self) -> dict:
    try:
        import PySide6
        pyside_version = PySide6.__version__
    except:
        pyside_version = "Unknown"
    
    return {
        "os": platform.system(),  # Linux, Windows, Darwin
        "os_version": platform.release(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "clarify_version": self.app_version,
        "pyside6_version": pyside_version,
        "architecture": platform.machine(),  # x86_64, arm64
    }
```

---

#### **generate_github_issue_url() Method** (Lines 156-230)

**Purpose**: Generate GitHub issue URL with pre-filled data

**Arguments**:
```python
def generate_github_issue_url(
    self, 
    error_info: dict,
    steps_to_reproduce: str = "",
    expected_behavior: str = "",
    actual_behavior: str = ""
) -> str:
```

**Output Example**:
```
https://github.com/JosueAmaral15/clarify/issues/new?title=%5BBug%5D+ValueError%3A+Invalid+configuration&body=...&labels=bug%2Cneeds-triage
```

**Issue Body Template**:
```markdown
## Bug Report

**Describe the bug**
An error occurred: Invalid configuration

**Steps to Reproduce**
1. (User to fill)

**Expected Behavior**
(User to fill)

**Error Details**
- **Type**: `ValueError`
- **Message**: `Invalid configuration`
- **File**: `~/clarify/src/app.py:123`
- **Function**: `load_config`

**Traceback**
```python
Traceback (most recent call last):
  ...
ValueError: Invalid configuration
```

**System Information**
- **OS**: Linux 5.15.0
- **Python**: 3.12.1
- **Clarify**: 2.9.89
- **PySide6**: 6.10.1
- **Architecture**: x86_64

**Timestamp**: 2026-01-22T19:08:30.123456
```

**Key Feature**: URL-encoded, ready to open in browser

---

#### **Module Functions** (Lines 233-255)

**Global singleton pattern**:
```python
_error_reporter: Optional[ErrorReporter] = None

def get_error_reporter() -> ErrorReporter:
    global _error_reporter
    if _error_reporter is None:
        _error_reporter = ErrorReporter()
    return _error_reporter

def install_error_reporter(app_version: str = "2.9.89"):
    global _error_reporter
    _error_reporter = ErrorReporter(app_version)
    _error_reporter.install()
    return _error_reporter
```

---

### 3. update_checker.py (286 lines) - Version Update Checker

**Purpose**: Check for new versions on GitHub Releases with caching

**Author**: Josué Amaral (v2.9.109)

---

#### **UpdateChecker Class** (Lines 28-258)

**Constants**:
```python
GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
CACHE_DURATION_HOURS = 24  # Cache valid for 24 hours
```

**Constructor** (Lines 34-68):
```python
def __init__(
    self, 
    current_version: str = "2.9.109",
    github_repo: str = "josuearaujo/clarify",
    cache_dir: Optional[str] = None
):
    self.current_version = current_version
    self.github_repo = github_repo
    
    # Parse owner/repo
    parts = github_repo.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repo format: {github_repo}. Expected 'owner/repo'")
    self.owner, self.repo = parts
    
    # Setup cache directory
    if cache_dir is None:
        home = Path.home()
        self.cache_dir = home / ".cache" / "clarify"
    else:
        self.cache_dir = Path(cache_dir)
    
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self.cache_file = self.cache_dir / "update_check.json"
    
    # QSettings for preferences
    self.settings = QSettings("Clarify", "Clarify")
```

**Cache Location**: `~/.cache/clarify/update_check.json`

---

#### **Settings Integration** (Lines 70-88)

**User-controlled update checking**:
```python
def is_check_enabled(self) -> bool:
    return self.settings.value("update_checker/enabled", True, type=bool)

def get_skipped_versions(self) -> list:
    skipped = self.settings.value("update_checker/skipped_versions", [], type=list)
    return skipped if skipped else []

def skip_version(self, version: str):
    skipped = self.get_skipped_versions()
    if version not in skipped:
        skipped.append(version)
        self.settings.setValue("update_checker/skipped_versions", skipped)

def clear_skipped_versions(self):
    self.settings.remove("update_checker/skipped_versions")
```

**Use Case**: User clicks "Skip this version" in update dialog

---

#### **Cache System** (Lines 90-133)

**_read_cache() Method**:
```python
def _read_cache(self) -> Optional[Dict[str, Any]]:
    if not self.cache_file.exists():
        return None
    
    try:
        with open(self.cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        
        # Check expiration
        cached_time = datetime.fromisoformat(cache.get("timestamp", ""))
        expiry = cached_time + timedelta(hours=self.CACHE_DURATION_HOURS)
        
        if datetime.now() > expiry:
            return None  # Expired
        
        return cache
    except (json.JSONDecodeError, ValueError, KeyError):
        return None  # Invalid cache
```

**_write_cache() Method**:
```python
def _write_cache(self, data: Dict[str, Any]):
    cache = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    try:
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass  # Fail silently
```

**Key Feature**: 24-hour cache prevents excessive API calls

---

#### **check_for_updates() Method** (Lines 135-231)

**Purpose**: Check for updates on GitHub Releases

**Algorithm**:
```python
def check_for_updates(self, use_cache: bool = True) -> Dict[str, Any]:
    # 1. Check cache first
    if use_cache:
        cached = self._read_cache()
        if cached:
            return cached.get("data", {})
    
    # 2. Check if requests library is available
    if not REQUESTS_AVAILABLE:
        return {
            "success": False,
            "error": "requests library not installed",
            "update_available": False,
            "current_version": self.current_version
        }
    
    # 3. Check if checking is enabled in settings
    if not self.is_check_enabled():
        return {
            "success": False,
            "error": "Update checking is disabled in settings",
            "update_available": False,
            "current_version": self.current_version
        }
    
    # 4. Fetch from GitHub API
    try:
        url = self.GITHUB_API_URL.format(owner=self.owner, repo=self.repo)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        release = response.json()
        
        # 5. Parse version (remove 'v' prefix)
        latest_version = release.get("tag_name", "").lstrip("v")
        
        # 6. Compare versions
        update_available = self._is_newer_version(latest_version, self.current_version)
        
        # 7. Check if this version is skipped
        if latest_version in self.get_skipped_versions():
            update_available = False
        
        # 8. Build result
        result = {
            "success": True,
            "update_available": update_available,
            "latest_version": latest_version,
            "current_version": self.current_version,
            "download_url": release.get("html_url", ""),
            "release_notes": release.get("body", "")[:500],  # First 500 chars
            "published_at": release.get("published_at", ""),
            "error": None
        }
        
        # 9. Cache result
        self._write_cache(result)
        
        return result
        
    except requests.Timeout:
        return {"success": False, "error": "Connection timeout"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {e}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {e}"}
```

**Return Value**:
```python
{
    "success": True,
    "update_available": True,
    "latest_version": "2.9.110",
    "current_version": "2.9.109",
    "download_url": "https://github.com/josuearaujo/clarify/releases/tag/v2.9.110",
    "release_notes": "### What's New\n\n- Feature X\n- Bug fix Y\n...",
    "published_at": "2026-01-20T10:30:00Z",
    "error": None
}
```

---

#### **_is_newer_version() Method** (Lines 233-252)

**Purpose**: Compare semantic versions

```python
def _is_newer_version(self, latest: str, current: str) -> bool:
    try:
        # Parse versions as tuples of ints
        latest_parts = tuple(int(x) for x in latest.split("."))
        current_parts = tuple(int(x) for x in current.split("."))
        
        return latest_parts > current_parts
    except (ValueError, AttributeError):
        return False  # Invalid format, assume no update
```

**Examples**:
```python
_is_newer_version("2.9.110", "2.9.109")  # True (patch)
_is_newer_version("2.10.0", "2.9.109")   # True (minor)
_is_newer_version("3.0.0", "2.9.109")    # True (major)
_is_newer_version("2.9.109", "2.9.109")  # False (same)
_is_newer_version("2.9.108", "2.9.109")  # False (older)
```

**Algorithm**: Tuple comparison (lexicographic)

---

#### **Module Functions** (Lines 260-286)

**Singleton pattern**:
```python
_update_checker_instance: Optional[UpdateChecker] = None

def get_update_checker(
    current_version: str = "2.9.109",
    github_repo: str = "josuearaujo/clarify"
) -> UpdateChecker:
    global _update_checker_instance
    
    if _update_checker_instance is None:
        _update_checker_instance = UpdateChecker(
            current_version=current_version,
            github_repo=github_repo
        )
    
    return _update_checker_instance
```

---

### 4. file_finder.py (417 lines) - Advanced File Search Dialog

**Purpose**: GUI dialog for advanced file/directory search with filters

**Author**: Josué Amaral (Task #36 - v2.9.11)

---

#### **AdvancedFileSearchDialog Class** (Lines 23-417)

**Features**:
- ✅ Filename regex filter (case-sensitive option)
- ✅ File type filter (Any, Files only, Directories only)
- ✅ Size range filter (MB)
- ✅ Date range filter (modified time)
- ✅ Recursive search option
- ✅ Results table (sortable, tooltips)
- ✅ Export to CSV
- ✅ i18n support (tr() calls)

**Constructor** (Lines 26-35):
```python
def __init__(self, parent=None, initial_dir: str = ""):
    super().__init__(parent)
    self.setWindowTitle("Advanced File Search")
    self.setModal(True)
    self.resize(800, 600)
    
    self.initial_dir = initial_dir or os.getcwd()
    self.results: List[Tuple[str, os.stat_result]] = []
    
    self._setup_ui()
```

---

#### **UI Components** (Lines 37-158)

**Search Directory Group**:
```python
dir_group = QGroupBox(tr("file_finder.group_search_directory"))
self.ed_directory = QLineEdit(self.initial_dir)
btn_browse = QPushButton(tr("file_finder.btn_browse"))
btn_browse.clicked.connect(self._browse_directory)
```

**Filters Group**:
1. **Filename Pattern** (regex):
   ```python
   self.ed_pattern = QLineEdit()
   self.chk_case_sensitive = QCheckBox(tr("file_finder.chk_case_sensitive"))
   ```

2. **File Type Filter**:
   ```python
   self.combo_type = QComboBox()
   self.combo_type.addItems(["Any", "Files only", "Directories only"])
   ```

3. **Size Range** (MB):
   ```python
   self.chk_size_filter = QCheckBox(tr("file_finder.chk_size_filter"))
   self.spin_size_min = QSpinBox()  # 0-100000 MB
   self.spin_size_max = QSpinBox()
   ```

4. **Date Range** (modified time):
   ```python
   self.chk_date_filter = QCheckBox(tr("file_finder.chk_date_filter"))
   self.date_from = QDateTimeEdit()  # Calendar popup
   self.date_to = QDateTimeEdit()
   self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-30))
   ```

5. **Recursive Search**:
   ```python
   self.chk_recursive = QCheckBox(tr("file_finder.chk_recursive"))
   self.chk_recursive.setChecked(True)  # Default ON
   ```

**Results Table**:
```python
self.table = QTableWidget()
self.table.setColumnCount(4)
self.table.setHorizontalHeaderLabels([
    "Name", "Path", "Size (MB)", "Modified"
])
self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
self.table.setSortingEnabled(True)
self.table.setMouseTracking(True)  # Task #41 - v2.9.13: Enable tooltips
```

---

#### **_perform_search() Method** (Lines 171-220)

**Purpose**: Execute search with current filters

**Algorithm**:
```python
def _perform_search(self):
    # 1. Validate directory
    directory = self.ed_directory.text().strip()
    if not directory or not os.path.isdir(directory):
        QMessageBox.warning(self, "Error", "Invalid directory")
        return
    
    # 2. Compile regex pattern (if provided)
    pattern = self.ed_pattern.text().strip()
    if pattern:
        try:
            flags = 0 if self.chk_case_sensitive.isChecked() else re.IGNORECASE
            regex = re.compile(pattern, flags)
        except re.error as e:
            QMessageBox.warning(self, "Invalid Regex", str(e))
            return
    else:
        regex = None
    
    # 3. Extract filter values
    type_filter = self.combo_type.currentText()
    recursive = self.chk_recursive.isChecked()
    
    # Size filter (convert MB to bytes)
    if self.chk_size_filter.isChecked():
        size_min = self.spin_size_min.value() * 1024 * 1024
        size_max = self.spin_size_max.value() * 1024 * 1024
    else:
        size_min = size_max = None
    
    # Date filter (convert QDateTime to timestamp)
    if self.chk_date_filter.isChecked():
        date_min = self.date_from.dateTime().toPyDateTime().timestamp()
        date_max = self.date_to.dateTime().toPyDateTime().timestamp()
    else:
        date_min = date_max = None
    
    # 4. Perform search
    self.results = []
    self._search_directory(
        directory, regex, type_filter, recursive,
        size_min, size_max, date_min, date_max
    )
    
    # 5. Display results
    self._display_results()
```

---

#### **_search_directory() Method** (Lines 222-279)

**Purpose**: Recursively search directory with filters

**Algorithm**:
```python
def _search_directory(
    self, directory, regex, type_filter, recursive,
    size_min, size_max, date_min, date_max
):
    try:
        entries = os.listdir(directory)
    except PermissionError:
        return  # Skip inaccessible directories
    
    for entry in entries:
        path = os.path.join(directory, entry)
        
        # Skip if can't stat
        try:
            stat = os.stat(path)
        except (PermissionError, FileNotFoundError):
            continue
        
        is_dir = os.path.isdir(path)
        is_file = os.path.isfile(path)
        
        # Apply type filter
        if type_filter == "Files only" and not is_file:
            continue
        if type_filter == "Directories only" and not is_dir:
            continue
        
        # Apply filename pattern (regex on basename)
        if regex and not regex.search(entry):
            continue
        
        # Apply size filter (files only)
        if is_file and size_min is not None and size_max is not None:
            if not (size_min <= stat.st_size <= size_max):
                continue
        
        # Apply date filter (modified time)
        if date_min is not None and date_max is not None:
            if not (date_min <= stat.st_mtime <= date_max):
                continue
        
        # Match - add to results
        self.results.append((path, stat))
        
        # Recurse into subdirectories
        if recursive and is_dir:
            self._search_directory(
                path, regex, type_filter, True,
                size_min, size_max, date_min, date_max
            )
```

**Key Features**:
- ✅ Permission error handling (skip inaccessible)
- ✅ Regex on basename (not full path)
- ✅ Size filter only on files (not dirs)
- ✅ Date filter on mtime (modification time)
- ✅ Recursive descent

---

#### **_display_results() Method** (Lines 281-315)

**Purpose**: Display search results in table

```python
def _display_results(self):
    self.table.setRowCount(0)
    self.table.setSortingEnabled(False)  # Disable during population
    
    for path, stat in self.results:
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Name
        name = os.path.basename(path)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        
        # Path
        self.table.setItem(row, 1, QTableWidgetItem(path))
        
        # Size (MB)
        size_mb = stat.st_size / (1024 * 1024)
        size_item = QTableWidgetItem(f"{size_mb:.2f}")
        size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 2, size_item)
        
        # Modified date
        mtime = datetime.fromtimestamp(stat.st_mtime)
        mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
        self.table.setItem(row, 3, QTableWidgetItem(mtime_str))
    
    self.table.setSortingEnabled(True)  # Re-enable sorting
    
    # Update stats label
    total_size = sum(stat.st_size for _, stat in self.results)
    total_size_mb = total_size / (1024 * 1024)
    self.lbl_stats.setText(
        f"Found {len(self.results)} items | Total size: {total_size_mb:.2f} MB"
    )
```

**Key Feature**: Statistics summary (count + total size)

---

#### **_export_results() Method** (Lines 317-350+)

**Purpose**: Export results to CSV file

```python
def _export_results(self):
    if not self.results:
        QMessageBox.information(self, "No Results", "No results to export")
        return
    
    filepath, _ = QFileDialog.getSaveFileName(
        self,
        "Export Results",
        "search_results.csv",
        "CSV Files (*.csv);;All Files (*)"
    )
    
    if not filepath:
        return
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("Name,Path,Size (bytes),Size (MB),Modified\n")
            
            # Data
            for path, stat in self.results:
                name = os.path.basename(path)
                size_mb = stat.st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                
                # Escape commas in path/name (CSV format)
                name = name.replace('"', '""')
                path = path.replace('"', '""')
                
                f.write(f'"{name}","{path}",{stat.st_size},{size_mb:.2f},{mtime_str}\n')
        
        QMessageBox.information(self, "Export Successful", f"Results exported to {filepath}")
    
    except Exception as e:
        QMessageBox.critical(self, "Export Failed", f"Error: {e}")
```

**CSV Format**:
```csv
Name,Path,Size (bytes),Size (MB),Modified
"file.txt","/home/user/file.txt",1024,0.00,2026-01-22 19:08:30
"doc.pdf","/home/user/doc.pdf",2048000,1.95,2026-01-21 10:30:00
```

---

## 🔑 Key Architectural Insights

### **Error Handling Architecture**:

**Two Implementations**:
1. **error_handler.py** (v2.9.61+):
   - More complete (crash reports, frequency tracking)
   - Privacy-aware (path stripping)
   - Context manager support
   - File-based crash reports (`~/.config/clarify/crashes/`)

2. **error_reporter.py** (earlier):
   - Simpler, GitHub-focused
   - URL generation for issues
   - Settings integration
   - QSettings-based privacy controls

**Likely Migration**: v2.9.61 introduced error_handler.py as replacement

---

### **Update Checker Design**:

**Three-Layer Caching**:
1. **Memory**: Singleton instance
2. **Disk**: JSON cache file (24-hour expiry)
3. **Network**: GitHub Releases API (fallback)

**User Controls**:
- ✅ Enable/disable automatic checking
- ✅ Skip specific versions
- ✅ Manual check (bypass cache)

**Graceful Degradation**:
- No `requests` library → Disabled with error message
- Network timeout → Cached result or error
- Invalid response → Error with details

---

### **File Finder Design**:

**Filter Composition**:
```
Directory → Type Filter → Filename Regex → Size Filter → Date Filter → Results
```

**Performance**:
- ✅ Early filtering (type check before regex)
- ✅ Permission error handling (don't stop on inaccessible)
- ✅ Lazy results (populate table after search complete)

**UX Features**:
- ✅ Sortable table (click headers)
- ✅ Statistics summary (count + size)
- ✅ CSV export (escaped, RFC 4180 compliant)
- ✅ Tooltips for file preview (Task #41)
- ✅ i18n support (all strings translatable)

---

### **Design Patterns Identified**:

1. **Singleton** (all 4 modules):
   - `CrashHandler._instance`
   - `_error_reporter` global
   - `_update_checker_instance` global
   - Each dialog is modal (single instance per session)

2. **Context Manager** (error_handler):
   - `CrashHandler.handle_errors()` with `@contextmanager`
   - RAII pattern (Resource Acquisition Is Initialization)

3. **Template Method** (file_finder):
   - `_setup_ui()` defines structure
   - Subclasses could override filter logic

4. **Strategy** (error_handler):
   - Multiple reporting strategies (dialog, file, callback, GitHub)
   - Composable (can enable multiple simultaneously)

5. **Observer** (Qt signals):
   - Button clicks → slot methods
   - Table events → preview tooltips

6. **Cache-Aside** (update_checker):
   - Check cache first
   - Miss → fetch from network → update cache
   - Classic caching pattern

---

### **Critical Code Sections** (Don't Touch):

1. **error_handler.py**:
   - `_strip_sensitive_paths()`: Privacy compliance (GDPR)
   - KeyboardInterrupt passthrough (lines 135-138)
   - Crash frequency tracking (prevents infinite loops)
   - Original excepthook restoration (lines 113-115)

2. **error_reporter.py**:
   - `generate_github_issue_url()`: URL encoding must preserve format
   - System info collection (privacy settings)

3. **update_checker.py**:
   - `_is_newer_version()`: Semantic version comparison
   - 24-hour cache expiry (prevents API rate limiting)
   - Skipped versions list (user experience)

4. **file_finder.py**:
   - Permission error handling (lines 236-237, 244-246)
   - CSV escaping (lines 346-347)
   - Size/date filter units (MB conversion, timestamps)

---

### **Security Considerations**:

**Privacy**:
- ✅ Path stripping (usernames removed)
- ✅ Opt-in system info (user consent)
- ✅ No automatic report sending (user approval required)

**Network Safety**:
- ✅ 10-second timeout (prevent hangs)
- ✅ Exception handling (all network errors caught)
- ✅ Rate limiting via cache (24-hour minimum)

**Filesystem Safety**:
- ✅ Permission error handling (no crashes)
- ✅ Directory creation (exist_ok=True)
- ✅ Fail silently on cache write (don't block app)

---

## 📊 Statistics

**Session 7 Metrics**:
- **Files Read**: 4
- **Lines Analyzed**: ~1,429
- **Functions/Classes Analyzed**: 30+
- **Design Patterns Identified**: 6 (Singleton, Context Manager, Template Method, Strategy, Observer, Cache-Aside)

**Utils Module Complete**:
- **Total Files**: 9 (100%)
- **Total Lines**: ~2,304
- **Categories**: Error Handling (2), System (2), File Operations (2), Text Processing (1), Logging (1), UI Bridge (1)

**Cumulative Progress**:
- **Total Files Studied**: 32 / 196 (16.3%)
- **Total Lines Studied**: ~6,888 / 58,165 (11.8%)
- **Documentation Read**: 242 / 242 (100%)
- **Overall Comprehension**: ~58% (docs 100%, code 16%)

**Phase 3 Status**: 🔄 **IN PROGRESS** (9/~50 feature module files)
- ✅ **Utils module**: 100% COMPLETE (9/9 files)
- ⏳ **Rewriter module**: 0% (9 files, ~2,297 lines)
- ⏳ **GUI docks**: 0% (40+ files)
- ⏳ **AI processor**: 0%

---

## 🎯 Key Takeaways

### **What We Now Understand** (Utils Module Complete):

1. ✅ **Error Handling System**:
   - Global exception handler (sys.excepthook override)
   - Crash reports with privacy protection
   - GitHub Issues integration
   - Multi-channel reporting (log, file, dialog, callback)
   - Crash frequency tracking

2. ✅ **Update Checking System**:
   - GitHub Releases API integration
   - 24-hour caching (prevent rate limiting)
   - Semantic version comparison
   - Skip version feature
   - Graceful degradation (no requests library, no network)

3. ✅ **Advanced File Search**:
   - Multi-criteria filtering (regex, type, size, date)
   - Recursive directory traversal
   - Permission error handling
   - CSV export
   - i18n support

4. ✅ **Complete Utils Architecture**:
   ```
   src/utils/
   ├── Error Handling
   │   ├── error_handler.py    # v2.9.61+ crash handler
   │   └── error_reporter.py   # Earlier GitHub reporter
   │
   ├── System
   │   ├── logger.py           # Structured logging, rotation
   │   └── update_checker.py   # GitHub version checking
   │
   ├── File Operations
   │   ├── file_utils.py       # walk, read/write, backup
   │   └── file_finder.py      # Advanced search dialog
   │
   ├── Text Processing
   │   ├── text_utils.py       # Masking, regex compilation
   │   └── normalization.py    # Token normalization
   │
   └── UI Bridge
       └── advanced_conditions.py  # UI → Condition objects
   ```

### **Utils Module Mission**:
- **Purpose**: Foundational utilities used across entire application
- **Philosophy**: Pure functions, graceful degradation, user control
- **Integration**: All docks/modules depend on utils

### **Reuse Opportunities**:
- ✅ `CrashHandler`: Can be used in any Python/Qt application
- ✅ `UpdateChecker`: Reusable for GitHub-hosted projects
- ✅ `AdvancedFileSearchDialog`: Standalone file finder
- ✅ Path stripping: Privacy pattern for any app
- ✅ Cache-aside pattern: Template for API caching

---

## 📝 Protocol Compliance Check

**SIMPLICITY_PROTOCOL_3 Step 1.2 Progress**:

- [x] Study entry points ✅
- [x] Study main application class ✅
- [x] Study initialization system ✅
- [x] Study UI construction ✅
- [x] Study core business logic ✅
- [x] Study utility modules ✅ **100% COMPLETE**
- [ ] Study rewriter modules (Phase 3 next)
- [ ] Study GUI docks (Phase 3)
- [ ] Study AI processor (Phase 3)
- [ ] Study support systems (Phase 4)
- [ ] Create comprehensive NOTES.md (Phase 5)

**Current Status**: ~52% of Step 1.2 complete

---

**Session 7 Complete! 🎉**  
**Utils Module: 100% COMPLETE! ✅**  
**Next**: Continue Phase 3 - Study rewriter/ module (9 files, ~2,297 lines, operations.py is 36K lines!)
