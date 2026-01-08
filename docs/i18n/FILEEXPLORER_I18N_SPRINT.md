# Sprint: File Explorer i18n Completo

**Data Início:** 2026-01-04  
**Objetivo:** Traduzir TODAS as strings hardcoded do File Explorer

---

## 📋 FASE 1: AUDITORIA COMPLETA

### Task 1.1: Identificar Strings Não Traduzidas
**Status:** ✅ CONCLUÍDA

### ✅ RESULTADO DA AUDITORIA PROFUNDA

#### Arquivos Auditados:
- ✅ `src/gui/file_explorer_dock.py` 
- ✅ `src/gui/widgets/file_filter_panel.py`
- ✅ `src/gui/widgets/file_list_table_manager.py`

---

### 🎯 SITUAÇÃO REAL (Pós-Auditoria)

#### ✅ **JÁ TRADUZIDO (Código usa tr() com keys existentes):**
1. **Colunas da Tabela (file_list_table_manager.py:76-82):**
   - `table_manager.header_name` ✅
   - `table_manager.header_size` ✅
   - `table_manager.header_modified` ✅
   - `table_manager.header_permissions` ✅
   - `table_manager.header_path` ✅

2. **Labels/Placeholders (file_filter_panel.py):**
   - `file_filter.regex_pattern` ✅
   - `file_filter.size_min`, `file_filter.size_max` ✅
   - `file_filter.modified_after`, `file_filter.modified_before` ✅
   - `file_filter.extensions` ✅
   - `file_filter.max_depth` ✅
   - Todos os checkboxes ✅

3. **Outros:**
   - `table_manager.quick_filter` ✅
   - `table_manager.no_files_listed` ✅
   - `table_manager.btn_export_csv` ✅

---

### ❌ **AINDA HARDCODED (Código NÃO usa tr()):**

#### 1. **file_list_table_manager.py - Linha 202**
```python
f"Listed {total_count} items ({file_count} files, {dir_count} dirs) | Total size: {total_str}"
```
**Problema:** Mensagem de estatísticas hardcoded  
**Solução:** Criar key `table_manager.stats_summary` e usar tr()

#### 2. **file_list_table_manager.py - Linha 321**
```python
writer.writerow(["Name", "Size", "Modified", "Permissions", "Path"])
```
**Problema:** Headers do CSV hardcoded  
**Solução:** Usar `tr("table_manager.header_name")` etc para cada header

#### 3. **file_explorer_dock.py - Linhas 916-919**
```python
if type_filter == "Files Only":
    filters["type"] = "files"
elif type_filter == "Directories Only":
    filters["type"] = "dirs"
```
**Problema:** Comparação com strings traduzidas (pode quebrar em PT)  
**Solução:** Comparar com índice do combo ao invés de texto

---

### 📊 RESUMO
- ✅ **90% JÁ TRADUZIDO** (labels, placeholders, buttons já usam tr())
- ❌ **3 locais precisam correção:** stats message, CSV headers, type filter comparison

---

## 📋 FASE 2: CORREÇÕES

### Task 2.1: Corrigir Stats Message (file_list_table_manager.py:202)
**Status:** 🔴 TODO  
**Dependência:** Task 1.1  
**Arquivos:** 
- `src/gui/widgets/file_list_table_manager.py`
- `src/i18n/en.json`
- `src/i18n/pt_BR.json`

**Steps:**
1. Adicionar key `table_manager.stats_summary` nos JSON (en + pt_BR)
2. Substituir linha 202 por `tr("table_manager.stats_summary").format(...)`
3. Testar mudança de idioma

### Task 2.2: Corrigir CSV Headers (file_list_table_manager.py:321)
**Status:** 🔴 TODO  
**Dependência:** Task 2.1  
**Arquivos:** 
- `src/gui/widgets/file_list_table_manager.py`

**Steps:**
1. Substituir `["Name", "Size", "Modified", "Permissions", "Path"]`
2. Por `[tr("table_manager.header_name"), tr("table_manager.header_size"), ...]`
3. Testar export CSV em PT e EN

### Task 2.3: Corrigir Type Filter Comparison (file_explorer_dock.py:916-919)
**Status:** 🔴 TODO  
**Dependência:** Task 2.2  
**Arquivos:** 
- `src/gui/file_explorer_dock.py`

**Steps:**
1. Mudar comparação de string para índice do combo
2. Usar `self.combo_type.currentIndex()` ao invés de `currentText()`
3. Testar filtro "Files Only" / "Directories Only" em PT

---

## 📋 FASE 3: TESTES

### Task 3.1: Teste Manual GUI
**Status:** 🔴 TODO

**Checklist:**
- [ ] Colunas da tabela traduzidas
- [ ] Botões traduzidos
- [ ] Labels traduzidos
- [ ] Placeholders traduzidos
- [ ] Mensagens traduzidas
- [ ] Trocar idioma EN → PT funciona
- [ ] Trocar idioma PT → EN funciona

---

## 📋 FASE 4: DOCUMENTAÇÃO

### Task 4.1: Atualizar Documentação
**Status:** 🔴 TODO

---

## 🎯 PRÓXIMO PASSO

**AGORA:** Executar Task 1.1 - Grep em cada arquivo do File Explorer
