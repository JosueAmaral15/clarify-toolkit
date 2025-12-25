# Fase 2.3 - Set Operations Dock - Plano de Refatoração

**Arquivo**: `src/gui/set_operations_dock.py`  
**Tamanho inicial**: 1148 linhas  
**Data**: 24/12/2024  
**Status**: 🟡 EM PROGRESSO

---

## 📊 Análise do Arquivo

### Estrutura Atual
```
SetOperationsDock (1 classe principal)
├── __init__ (12 linhas)
├── _setup_ui (232 linhas) ⚠️ GRANDE
├── _connect_signals (24 linhas)
├── _apply_accessibility (92 linhas) ⚠️ EXTRAÍVEL
├── _browse_file (16 linhas)
├── _toggle_multiple_files (17 linhas)
├── _add_file (7 linhas)
├── _remove_file (6 linhas)
├── _clear_files (4 linhas)
├── _get_files (19 linhas)
├── _execute (167 linhas) ⚠️ GRANDE
├── _save_result (19 linhas)
├── _export_result (57 linhas)
├── _store_in_calculator (28 linhas)
├── _view_diff (29 linhas)
├── _view_venn (29 linhas)
├── _merge_to_file (66 linhas)
├── _clear_all (22 linhas)
├── _show_history (9 linhas)
├── _re_execute_from_history (42 linhas)
├── _show_presets (9 linhas)
├── _load_preset (49 linhas)
├── _save_current_as_preset (77 linhas)
├── receive_calculator_data (45 linhas)
└── _show_batch_dialog (13 linhas)
```

### Componentes Identificados para Extração

#### 🔵 Alta Prioridade (>50 linhas)
1. **FileSelectionWidget** (~120 linhas)
   - File A/B inputs + Browse buttons
   - Multiple files checkbox
   - File list widget + Add/Remove/Clear buttons
   - Métodos: `_browse_file`, `_toggle_multiple_files`, `_add_file`, `_remove_file`, `_clear_files`, `_get_files`

2. **OperationOptionsWidget** (~80 linhas)
   - Checkboxes: Intersection, Union, Difference, Symmetric
   - Radio buttons: Comparison modes
   - Options: ignore case, skip empty, arrays ignore order
   - Output format combo

3. **SetOperationExecutor** (~200 linhas)
   - Método `_execute` principal (167 linhas)
   - Lógica de pipeline processing
   - Validação de inputs
   - Execução de operações
   - Geração de estatísticas

4. **ResultExporterHelper** (~90 linhas)
   - `_save_result` (19 linhas)
   - `_export_result` (57 linhas)
   - Conversões para CSV, Excel, YAML, TOML

#### 🟡 Média Prioridade (20-50 linhas)
5. **AccessibilityHelper** (~92 linhas)
   - Método `_apply_accessibility`
   - Labels e descrições para screen readers

6. **HistoryPresetsManager** (~100 linhas)
   - `_show_history`, `_re_execute_from_history`
   - `_show_presets`, `_load_preset`, `_save_current_as_preset`

---

## 🎯 Plano de Execução

### Fase 2.3.1 - FileSelectionWidget
**Objetivo**: Extrair widget de seleção de arquivos  
**Linhas**: ~150 linhas (incluindo UI + lógica)  
**Arquivo destino**: `src/gui/widgets/file_selection_widget.py`

**Componentes**:
- UI: File A/B inputs, Browse buttons, Multiple files mode
- Métodos: browse, toggle, add, remove, clear, get_files
- Sinais: files_changed

**Benefícios**:
- Reutilizável em outros docks
- Testável independentemente
- Reduz _setup_ui

### Fase 2.3.2 - OperationOptionsWidget
**Objetivo**: Extrair widget de opções de operação  
**Linhas**: ~100 linhas  
**Arquivo destino**: `src/gui/widgets/operation_options_widget.py`

**Componentes**:
- UI: Operation checkboxes, Comparison modes, Options
- Métodos: get_operations, get_comparison_mode, get_options
- Sinais: options_changed

**Benefícios**:
- Separação de concerns
- UI reutilizável
- Facilita testes

### Fase 2.3.3 - SetOperationExecutor
**Objetivo**: Extrair lógica de execução de operações  
**Linhas**: ~220 linhas  
**Arquivo destino**: `src/gui/workers/set_operation_executor.py`

**Componentes**:
- Pipeline processing logic
- Validation
- Operations execution
- Statistics generation
- Error handling

**Benefícios**:
- Separação lógica de negócio
- Pode rodar em background thread
- Testável com unit tests

### Fase 2.3.4 - ResultExporter
**Objetivo**: Extrair exportação de resultados  
**Linhas**: ~90 linhas  
**Arquivo destino**: `src/utils/result_exporter.py`

**Componentes**:
- Save to JSON
- Export to CSV, Excel, YAML, TOML
- Format conversions

**Benefícios**:
- Reutilizável em outros módulos
- Centraliza lógica de export

---

## 📝 Checklist de Implementação

### Fase 2.3.1 - FileSelectionWidget
- [ ] Criar `src/gui/widgets/file_selection_widget.py`
- [ ] Extrair UI de seleção de arquivos
- [ ] Extrair métodos browse/toggle/add/remove/clear
- [ ] Definir sinais (files_changed)
- [ ] Atualizar `src/gui/widgets/__init__.py`
- [ ] Integrar no SetOperationsDock
- [ ] Testar import e funcionalidade
- [ ] Commit: "refactor(v2.9.114): Phase 2.3.1 - Extract FileSelectionWidget"

### Fase 2.3.2 - OperationOptionsWidget
- [ ] Criar `src/gui/widgets/operation_options_widget.py`
- [ ] Extrair checkboxes de operações
- [ ] Extrair radio buttons de comparação
- [ ] Extrair opções adicionais
- [ ] Definir métodos getters
- [ ] Atualizar `src/gui/widgets/__init__.py`
- [ ] Integrar no SetOperationsDock
- [ ] Testar import e funcionalidade
- [ ] Commit: "refactor(v2.9.114): Phase 2.3.2 - Extract OperationOptionsWidget"

### Fase 2.3.3 - SetOperationExecutor
- [ ] Criar `src/gui/workers/set_operation_executor.py`
- [ ] Extrair método _execute
- [ ] Implementar validation logic
- [ ] Implementar pipeline processing
- [ ] Implementar statistics generation
- [ ] Definir sinais (progress, success, error)
- [ ] Atualizar `src/gui/workers/__init__.py`
- [ ] Integrar no SetOperationsDock
- [ ] Testar execução
- [ ] Commit: "refactor(v2.9.114): Phase 2.3.3 - Extract SetOperationExecutor"

### Fase 2.3.4 - ResultExporter
- [ ] Criar `src/utils/result_exporter.py`
- [ ] Extrair save_result
- [ ] Extrair export_result
- [ ] Implementar conversores (CSV, Excel, YAML, TOML)
- [ ] Atualizar `src/utils/__init__.py`
- [ ] Integrar no SetOperationsDock
- [ ] Testar exports
- [ ] Commit: "refactor(v2.9.114): Phase 2.3.4 - Extract ResultExporter"

### Investigação Final
- [ ] Testar todos os imports (4 novos módulos)
- [ ] Testar instanciação do dock
- [ ] Verificar referências cruzadas
- [ ] Testar cenários de uso completos
- [ ] Executar aplicação completa
- [ ] Commit: "docs(v2.9.114): Phase 2.3 completion report"

---

## 📈 Métricas Esperadas

### Antes da Refatoração
```
set_operations_dock.py: 1148 linhas
Módulos widgets: 2 (PathEntry, ...)
Módulos workers: 2 (AIProcessorWorker, ...)
Módulos utils: 3 (stats_formatter, ...)
```

### Depois da Refatoração
```
set_operations_dock.py: ~600 linhas (estimativa)
Módulos widgets: +2 (FileSelection, OperationOptions)
Módulos workers: +1 (SetOperationExecutor)
Módulos utils: +1 (ResultExporter)
Redução: ~548 linhas (-48%)
```

---

## 🐛 Riscos e Precauções

### Riscos Identificados
1. **Sinais Qt**: Verificar se todos os sinais são mantidos
2. **History/Presets**: Integração com managers existentes
3. **Calculator integration**: Signal `store_in_calculator_requested`
4. **Batch operations**: Dialog de batch pode ter dependências

### Precauções
1. Testar cada extração individualmente
2. Manter backward compatibility
3. Documentar sinais e métodos públicos
4. Criar testes de integração

---

## 📋 Notas de Implementação

### FileSelectionWidget
```python
# Sinais a serem emitidos:
- files_changed(list[str])  # Quando lista de arquivos muda

# Métodos públicos:
- get_files() -> List[str]
- set_files(files: List[str])
- clear()
```

### OperationOptionsWidget
```python
# Métodos públicos:
- get_selected_operations() -> List[str]
- get_comparison_mode() -> str
- get_options() -> dict
- set_configuration(config: dict)
```

### SetOperationExecutor
```python
# Worker que herda de QThread ou ProcessorWorkerBase
# Sinais:
- progress(int)
- success(dict)  # results + statistics
- error(str)

# Métodos:
- execute(files, operations, options)
```

### ResultExporter
```python
# Funções utilitárias:
- save_json(data, filepath)
- export_csv(data, filepath)
- export_excel(data, filepath)
- export_yaml(data, filepath)
- export_toml(data, filepath)
```

---

**Status**: 📝 PLANEJAMENTO COMPLETO  
**Próximo passo**: Iniciar Fase 2.3.1 - FileSelectionWidget
