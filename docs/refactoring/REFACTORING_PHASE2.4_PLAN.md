# Plano de Refatoração - Fase 2.4: File List Dock

## Contexto
**Arquivo**: `src/gui/file_list_dock.py`  
**Tamanho atual**: 966 linhas  
**Complexidade**: Alta (muitos filtros e opções)

## Análise do Código

### Componentes Identificados

#### 1. **FilterPanel** (~250 linhas)
- Advanced filters panel (collapsible)
- Regex pattern matching
- Size filters (min/max with units)
- MTime filters (before/after dates)
- Extension filters
- Depth limit
- Exclude directories
- **Extração**: Widget reutilizável para filtros

#### 2. **FileListExecutor** (~200 linhas)
- Lógica de listagem de arquivos
- Aplicação de filtros
- Parsing de resultados
- Estatísticas
- **Extração**: Core logic sem Qt

#### 3. **PresetManager** (~150 linhas)
- Sistema de presets
- Save/load/export/import
- Preset list management
- **Extração**: Gerenciador reutilizável

#### 4. **TableManager** (~100 linhas)
- População da tabela
- Sorting
- Context menu
- Quick filter
- **Extração**: Widget para gerenciamento de tabela

#### 5. **ExportManager** (~50 linhas)
- Export to CSV
- Format handling
- **Extração**: Utilitário de exportação

## Plano de Extração

### Fase 2.4.1: FilterPanel (~250 linhas)
**Arquivo**: `src/gui/widgets/file_filter_panel.py`

**Componentes**:
- Regex filter
- Size filters (min/max)
- MTime filters (before/after)
- Extensions filter
- Depth limit
- Exclude directories

**API**:
```python
class FileFilterPanel(QWidget):
    filters_changed = Signal()
    
    def get_filters() -> Dict[str, Any]
    def set_filters(filters: Dict)
    def clear_filters()
    def validate_filters() -> Tuple[bool, str]
```

**Redução estimada**: ~200 linhas

---

### Fase 2.4.2: FileListExecutor (~200 linhas)
**Arquivo**: `src/core/file_list_executor.py`

**Componentes**:
- File listing logic
- Filter application
- Statistics calculation
- Result parsing

**API**:
```python
class FileListExecutor:
    @staticmethod
    def list_files(directory, options, filters) -> ListResult
    
    @staticmethod
    def apply_filters(files, filters) -> List[FileInfo]
    
    @staticmethod
    def calculate_stats(files) -> Dict[str, Any]
```

**Redução estimada**: ~150 linhas

---

### Fase 2.4.3: PresetManager (~150 linhas)
**Arquivo**: `src/core/file_list_preset_manager.py`

**Componentes**:
- Preset CRUD operations
- Import/export
- Validation

**API**:
```python
class FileListPresetManager:
    def save_preset(name, config)
    def load_preset(name) -> Dict
    def delete_preset(name)
    def list_presets() -> List[str]
    def export_preset(name, path)
    def import_preset(path)
```

**Redução estimada**: ~100 linhas

---

### Fase 2.4.4: TableManager (~100 linhas)
**Arquivo**: `src/gui/widgets/file_table_widget.py`

**Componentes**:
- Table population
- Sorting
- Quick filter
- Context menu

**API**:
```python
class FileTableWidget(QTableWidget):
    file_selected = Signal(str)
    files_selected = Signal(list)
    
    def populate(files: List[FileInfo])
    def apply_quick_filter(text: str)
    def get_selected_files() -> List[str]
```

**Redução estimada**: ~80 linhas

---

## Resumo

### Meta de Redução
- **Antes**: 966 linhas
- **Depois**: ~430 linhas (estimado)
- **Redução**: ~530 linhas (-55%)

### Componentes a Criar
1. `file_filter_panel.py` - 250 linhas
2. `file_list_executor.py` - 200 linhas
3. `file_list_preset_manager.py` - 150 linhas
4. `file_table_widget.py` - 100 linhas

### Total Extraído
~700 linhas em 4 componentes reutilizáveis

## Benefícios
- ✅ Filtros reutilizáveis em outros contextos
- ✅ Executor testável sem GUI
- ✅ Preset system compartilhável
- ✅ Table widget reusável

## Ordem de Execução
1. Fase 2.4.1: FilterPanel (mais impacto visual)
2. Fase 2.4.2: FileListExecutor (lógica core)
3. Fase 2.4.3: PresetManager (independente)
4. Fase 2.4.4: TableManager (finalização)

## Status
⏳ **PLANEJAMENTO COMPLETO - PRONTO PARA EXECUÇÃO**
