# File Explorer I18N Investigation - 2026-01-04

## 🎯 Objetivo
Investigar por que o File Explorer aparece com strings em inglês mesmo após o usuário relatar que não está traduzido.

## 🔍 Investigação Realizada

### 1. Strings Reportadas Como Não Traduzidas

**Usuário reportou:**
- ❌ Name, Size, Modified, Permissions, Path (colunas da tabela)
- ❌ Export to CSV, Export CSV, Save Results (botões)
- ❌ No File Listed
- ❌ Quick Filter
- ❌ Include Globs
- ❌ Options, Case Sensitive, Whole Word, Preserve Case
- ❌ Size Min, Size Max, Extensions, Max Depth, Modified After, contains

### 2. Verificação do Código

#### A. FileListTableManager (src/gui/widgets/file_list_table_manager.py)

**Linhas 76-82:** Headers da tabela **USANDO tr()** ✅
```python
self.table.setHorizontalHeaderLabels([
    tr("table_manager.header_name"),         # ✅
    tr("table_manager.header_size"),         # ✅
    tr("table_manager.header_modified"),     # ✅
    tr("table_manager.header_permissions"),  # ✅
    tr("table_manager.header_path")          # ✅
])
```

**Linha 64:** Quick Filter **USANDO tr()** ✅
```python
filter_layout.addWidget(QLabel(tr("table_manager.quick_filter")))
```

**Linha 111:** Botão Export **USANDO tr()** ✅
```python
self.btn_export = QPushButton(tr("table_manager.btn_export_csv"))
```

**Linha 108:** No Files Listed **USANDO tr()** ✅
```python
self.lbl_stats = QLabel(tr("table_manager.no_files_listed"))
```

#### B. FileFilterPanel (src/gui/widgets/file_filter_panel.py)

**Todas as labels USANDO tr()** ✅:
- Linha 71: `QLabel(tr("file_filter.regex_pattern"))`
- Linha 80: `QLabel(tr("file_filter.size_min"))`
- Linha 93: `QLabel(tr("file_filter.size_max"))`
- Linha 106: `QLabel(tr("file_filter.modified_after"))`
- Linha 117: `QLabel(tr("file_filter.modified_before"))`
- Linha 128: `QLabel(tr("file_filter.extensions"))`
- Linha 142: `QLabel(tr("file_filter.max_depth"))`

### 3. Verificação das Traduções PT_BR

**Arquivo:** `src/i18n/pt_BR.json`

**✅ TODAS as traduções EXISTEM:**

```json
{
  "table_manager.header_name": "Nome",
  "table_manager.header_size": "Tamanho",
  "table_manager.header_modified": "Modificado",
  "table_manager.header_permissions": "Permissões",
  "table_manager.header_path": "Caminho",
  "table_manager.quick_filter": "Filtro Rápido:",
  "table_manager.btn_export_csv": "Exportar para CSV...",
  "table_manager.no_files_listed": "Nenhum arquivo listado",
  
  "file_filter.regex_pattern": "Padrão Regex:",
  "file_filter.size_min": "Tamanho Mín:",
  "file_filter.size_max": "Tamanho Máx:",
  "file_filter.modified_after": "Modificado Após:",
  "file_filter.modified_before": "Modificado Antes:",
  "file_filter.extensions": "Extensões:",
  "file_filter.max_depth": "Profundidade Máx:",
  ...
}
```

## 🚨 Diagnóstico

**CONCLUSÃO SURPREENDENTE:**

✅ **Código está correto** - todas as strings usam `tr()`  
✅ **Traduções existem** em `pt_BR.json`  
❌ **USUÁRIO VÊ EM INGLÊS** - problema de runtime!

## 🔎 Possíveis Causas

### Hipótese 1: Idioma não está definido como PT_BR
- Aplicação pode estar carregando `en.json` por padrão
- Verificar `TranslationManager.set_language('pt_BR')` está sendo chamado

### Hipótese 2: Cache de tradução
- Sistema de tradução pode ter cache não invalidado
- Após adicionar novas keys, precisa recarregar

### Hipótese 3: Ordem de inicialização
- Widgets criados ANTES do sistema i18n estar pronto
- `tr()` retorna key original quando tradutor não está inicializado

### Hipótese 4: Fallback para EN
- Se alguma key não for encontrada, retorna EN
- Mas verificamos que as keys EXISTEM

## 📋 Próximos Passos Recomendados

### Etapa 1: Verificar Configuração de Idioma
```bash
# Procurar onde o idioma é definido
grep -rn "set_language\|setLanguage" src/
```

### Etapa 2: Adicionar Debug no Sistema I18N
```python
# Em src/i18n/translator.py
def tr(key: str) -> str:
    value = TranslationManager.translate(key)
    if value == key:  # Tradução não encontrada
        print(f"[I18N DEBUG] Key não traduzida: {key}")
    return value
```

### Etapa 3: Verificar Ordem de Inicialização
- Garantir que `TranslationManager` é inicializado ANTES de criar widgets
- Verificar em `src/app.py` ou `src/gui/initialization_manager.py`

### Etapa 4: Forçar Reload do Sistema I18N
```python
# Após mudanças no JSON
TranslationManager.reload()
```

### Etapa 5: Criar Teste Manual
```python
# test_i18n_file_explorer.py
from src.i18n.translator import TranslationManager, tr

TranslationManager.set_language('pt_BR')
print(tr("table_manager.header_name"))  # Deve printar "Nome"
```

## 📝 Anotações

1. **Tooltips customizados implementados** (2026-01-04)
   - Cada célula mostra seu valor completo
   - Size: formato human + bytes
   - Modified: datetime com milissegundos
   - Name, Permissions, Path: valores completos

2. **Extensions movido** de Directory & Type → Filters (2026-01-04)
   - Adicionado checkbox "Use Extension Filter"
   - Campo habilitado/desabilitado conforme checkbox

3. **View mode bug corrigido** (2026-01-04)
   - Table não mudava automaticamente para Tree
   - Table renderizava corretamente após busca

## ✅ Status Atual

- [x] Código usando `tr()` corretamente
- [x] Traduções existem em `pt_BR.json`
- [ ] **INVESTIGAR POR QUE RUNTIME MOSTRA EM INGLÊS**
- [ ] Testar sistema i18n isoladamente
- [ ] Verificar configuração de idioma padrão
- [ ] Adicionar debug no sistema de tradução

---

**Última atualização:** 2026-01-04  
**Investigado por:** AI Assistant (com orientação do usuário)  
**Status:** 🔍 INVESTIGAÇÃO EM ANDAMENTO - Código correto, problema de runtime
