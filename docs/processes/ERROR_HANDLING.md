# Error Handling & Crash Reporting

**Sprint v2.9.61** - Error Reporting & Crash Handler

## Overview

Sistema centralizado de tratamento de erros e crash reporting para Clarify. Captura exceções não tratadas, exibe diálogos amigáveis ao usuário, salva relatórios de crash e integra-se com o sistema de logging.

## Features

✅ **Global Exception Handler**: Captura todas as exceções não tratadas  
✅ **User-Friendly Dialogs**: Mostra mensagens de erro amigáveis  
✅ **Crash Reports**: Salva relatórios detalhados em `~/.config/clarify/crashes/`  
✅ **Privacy-Aware**: Remove paths sensíveis dos relatórios  
✅ **Context Manager**: Handle errors em blocos específicos de código  
✅ **Logging Integration**: Integra com sistema de logging (v2.9.58)  
✅ **Opt-in Reporting**: Envio de relatórios é opcional  

## Installation

O crash handler é instalado automaticamente ao iniciar a aplicação:

```python
from src.utils.error_handler import install_crash_handler

# Install at app startup
handler = install_crash_handler(
    show_dialog=True,      # Show error dialog to user
    report_crashes=False   # Opt-in only for sending reports
)
```

## Usage

### 1. Global Exception Handler

Captura todas as exceções não tratadas automaticamente:

```python
# In src/app.py (MainWindow.__init__):
self.crash_handler = install_crash_handler(
    show_dialog=True,
    report_crashes=False
)
```

Quando ocorre uma exceção não tratada:
- 📝 **Logging**: Erro é logado via sistema de logging
- 💾 **Crash Report**: Relatório salvo em `~/.config/clarify/crashes/crash_YYYYMMDD_HHMMSS.txt`
- 🖥️ **Error Dialog**: Diálogo mostrado ao usuário (se GUI disponível)
- 🔄 **Original Handler**: Handler original é chamado (imprime no stderr)

### 2. Context Manager

Para tratar erros em blocos específicos de código:

```python
from src.utils.error_handler import CrashHandler

# Handle errors in specific section
with CrashHandler.handle_errors(show_dialog=False):
    risky_operation()

# With custom callback
def on_error(exception):
    print(f"Error occurred: {exception}")

with CrashHandler.handle_errors(callback=on_error):
    risky_operation()
```

### 3. Custom Callback

Execute código customizado após tratar erro:

```python
def custom_error_handler(exception, traceback_text):
    # Send email notification
    send_email("admin@example.com", f"Crash: {exception}")
    
    # Update database
    db.log_crash(exception, traceback_text)

handler = install_crash_handler(
    show_dialog=True,
    callback=custom_error_handler
)
```

## Crash Reports

### Report Format

Crash reports são salvos em `~/.config/clarify/crashes/` com o formato:

```
================================================================================
CLARIFY CRASH REPORT
================================================================================

System Information:
--------------------------------------------------------------------------------
platform: Linux-6.8.0-49-generic-x86_64-with-glibc2.39
python_version: 3.12.4
crash_time: 2025-12-10T18:51:21.569234
crash_count: 1
exception_type: ValueError
exception_message: Test crash for demonstration purposes

Traceback:
--------------------------------------------------------------------------------
Traceback (most recent call last):
  File "~/project/clarify/src/app.py", line 4145, in <module>
    raise ValueError("Test crash for demonstration purposes")
ValueError: Test crash for demonstration purposes

================================================================================
End of crash report
================================================================================
```

### Privacy Protection

Crash reports **removem paths sensíveis** automaticamente:

- `$HOME` → `~`
- `$CWD` → `.`
- `/usr/local/lib/python...` → `python...`
- `C:\Users\` → `~\`

### Location

```bash
# Linux/macOS
~/.config/clarify/crashes/crash_20251210_185121.txt

# Windows
C:\Users\<username>\.config\clarify\crashes\crash_20251210_185121.txt
```

## Error Dialog

Quando `show_dialog=True` e uma exceção não tratada ocorre:

**Dialog exibe:**
- ❌ **Error Type & Message**: `ValueError: Test error`
- 📝 **Informative Text**: Recomendação de salvar trabalho e reiniciar
- 📂 **Crash Report Path**: `~/.config/clarify/crashes/crash_....txt`
- 📋 **Details**: Traceback completo (expandível)
- 🐛 **Report Bug Button**: (se `report_crashes=True`)

**Exemplo:**

```
╔═══════════════════════════════════════════════════════════════╗
║ ❌ Clarify - Unexpected Error                                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║ An unexpected error occurred:                                ║
║                                                               ║
║ ValueError: Test crash for demonstration purposes            ║
║                                                               ║
║ The application may be in an unstable state.                 ║
║ It's recommended to save your work and restart.              ║
║                                                               ║
║ Crash report saved to:                                       ║
║ ~/.config/clarify/crashes/crash_20251210_185121.txt         ║
║                                                               ║
║ [ Details ▼ ]                                                ║
║                                                               ║
║     [Report Bug]              [Close]                        ║
╚═══════════════════════════════════════════════════════════════╝
```

## API Reference

### `install_crash_handler()`

Instala o crash handler global.

**Parameters:**
- `show_dialog` (bool): Mostrar diálogo de erro ao usuário (default: `True`)
- `report_crashes` (bool): Enviar relatórios automaticamente (opt-in, default: `False`)
- `callback` (Callable): Callback customizado `(exception, traceback_text) -> None`

**Returns:**
- `CrashHandler`: Instância do handler

**Example:**
```python
handler = install_crash_handler(
    show_dialog=True,
    report_crashes=False,
    callback=lambda exc, tb: print(f"Crash: {exc}")
)
```

### `uninstall_crash_handler()`

Remove o crash handler global e restaura o `sys.excepthook` original.

**Example:**
```python
uninstall_crash_handler()
```

### `CrashHandler.handle_errors()`

Context manager para tratar erros em blocos específicos.

**Parameters:**
- `show_dialog` (bool): Mostrar diálogo se erro ocorrer (default: `False`)
- `callback` (Callable): Callback customizado `(exception) -> None`

**Example:**
```python
with CrashHandler.handle_errors(show_dialog=False):
    risky_operation()
```

### `CrashHandler` Class

**Attributes:**
- `enabled` (bool): Se o handler está ativo
- `show_dialog` (bool): Se mostra diálogo ao usuário
- `report_crashes` (bool): Se envia relatórios automaticamente
- `callback` (Callable): Callback customizado

**Methods:**
- `install()`: Instala como handler global
- `uninstall()`: Remove handler global
- `get_instance()`: Retorna singleton instance
- `reset_instance()`: Reset singleton (para testes)

## Integration with Logging System (v2.9.58)

O crash handler integra-se automaticamente com o sistema de logging:

```python
# Errors são logados com nível CRITICAL
logger.critical(
    f"Unhandled exception ({crash_count} crashes):\n{traceback}",
    exc_info=(exc_type, exc_value, exc_traceback)
)

# Info messages para operações
logger.info("Crash handler installed successfully")
logger.info(f"Crash report saved to {crash_file}")
```

**Log Output:**
```
2025-12-10 18:51:21 | CRITICAL | clarify.utils.error_handler:153 | Unhandled exception (1 crashes):
Traceback (most recent call last):
  File "~/project/clarify/src/app.py", line 4145, in <module>
    raise ValueError("Test crash")
ValueError: Test crash
```

## Configuration

### Enable Crash Reporting (Opt-in)

Para habilitar envio automático de crash reports:

```python
handler = install_crash_handler(
    show_dialog=True,
    report_crashes=True  # Opt-in
)
```

**Note:** Implementação de envio ainda não disponível (placeholder). Futuras implementações podem incluir:
- GitHub Issues API
- Email service
- Error tracking (Sentry, Rollbar)

### Disable Error Dialog

Para ambientes CLI ou testes:

```python
handler = install_crash_handler(show_dialog=False)
```

### Custom Callback

Execute código customizado após tratar erro:

```python
def on_crash(exception, traceback_text):
    # Custom logic
    send_notification(f"App crashed: {exception}")

handler = install_crash_handler(callback=on_crash)
```

## Testing

### Run Tests

```bash
# Run all error handler tests
pytest tests/test_error_handler.py -v

# Run with coverage
pytest tests/test_error_handler.py --cov=src.utils.error_handler
```

### Test Results

```
25 tests, 100% passing in 0.36s

✅ TestCrashHandlerInit (4 tests)
✅ TestCrashHandlerInstall (4 tests)
✅ TestCrashHandlerExceptionHandling (5 tests)
✅ TestCrashHandlerPathStripping (3 tests)
✅ TestCrashHandlerSaveReport (2 tests)
✅ TestCrashHandlerContextManager (3 tests)
✅ TestInstallUninstall (3 tests)
✅ TestIntegration (1 test)
```

## Performance

- **Install overhead**: <1ms
- **Exception handling**: <10ms
- **Crash report saving**: <5ms
- **Memory footprint**: <100 KB

## Troubleshooting

### Dialog não aparece

**Causa**: `show_dialog=True` mas `QApplication` não está disponível

**Solução**:
```python
# Verifique se QApplication existe
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
if not app:
    # Create QApplication first
    app = QApplication(sys.argv)
```

### Crash reports não são salvos

**Causa**: Permissões de escrita em `~/.config/clarify/crashes/`

**Solução**:
```bash
# Create directory with correct permissions
mkdir -p ~/.config/clarify/crashes
chmod 755 ~/.config/clarify/crashes
```

### Handler não captura exceções

**Causa**: Outro código está sobrescrevendo `sys.excepthook`

**Solução**:
```python
# Install crash handler APÓS outros frameworks
# Exemplo: após pytest, IPython, etc.
install_crash_handler()
```

## Future Enhancements

- 🚀 **GitHub Issues Integration**: Auto-create issues on crash
- 📧 **Email Notifications**: Send crash reports via email
- 📊 **Error Tracking**: Integration with Sentry/Rollbar
- 🔍 **Stack Trace Analysis**: Automatic duplicate detection
- 📈 **Crash Statistics**: Dashboard com crash analytics
- 🔒 **Encrypted Reports**: Encrypt sensitive crash data

## References

- **Sprint**: v2.9.61 - Error Reporting & Crash Handler
- **Related**: v2.9.58 - Logging System
- **Protocol**: Simplicidade 3 v3.1 (COULD HAVE task #3/23)

## Support

Para reportar bugs ou sugerir melhorias:
- GitHub Issues: https://github.com/JosueAmaral15/clarify/issues
- Email: (crash reports podem ser enviados para admin)

---

**Developed by**: Josué Amaral  
**Date**: 2025-12-10  
**Version**: v2.9.61
