Teste
# Guia de Tradução Manual - File Explorer

## 📋 Status
**Data:** 2026-01-05  
**Strings não traduzidas encontradas:** 15+  
**Arquivos afetados:** 2

---

## 🎯 Strings Não Traduzidas Encontradas na GUI

Você reportou as seguintes strings visíveis mas NÃO traduzidas:

### File Explorer - Modo Table
- [ ] `Name` (coluna)
- [ ] `Size` (coluna)
- [ ] `Modified` (coluna)
- [ ] `Permissions` (coluna)
- [ ] `Path` (coluna)

### Botões
- [ ] `Export to CSV` ou `Export CSV`
- [ ] `Save Results`

### Mensagens
- [ ] `No File Listed`

### Filtros/Labels
- [ ] `Quick Filter`
- [ ] `Include Globs`
- [ ] `Options`
- [ ] `Case Sensitive`
- [ ] `Whole Word`
- [ ] `Preserve Case`
- [ ] `Size Min`
- [ ] `Size Max`
- [ ] `Extensions`
- [ ] `Max Depth`
- [ ] `Modified After`
- [ ] `contains`

---

## 📁 Arquivos a Modificar

### 1. **src/gui/widgets/file_list_table_manager.py**

Este arquivo gerencia a **tabela de resultados** (modo Table) do File Explorer.

#### 🔍 O que procurar:
Strings hardcoded para os **headers das colunas**:
- `"Name"`, `"Size"`, `"Modified"`, `"Permissions"`, `"Path"`

#### ✏️ Como traduzir:

**ANTES** (linha aproximada 50-100):
```python
# Headers hardcoded
self.table.setColumnCount(5)
self.table.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Permissions", "Path"])
```

**DEPOIS**:
```python
# Headers traduzidos
self.table.setColumnCount(5)
self.table.setHorizontalHeaderLabels([
    tr("file_list.header_name"),
    tr("file_list.header_size"),
    tr("file_list.header_modified"),
    tr("file_list.header_permissions"),
    tr("file_list.header_path")
])
```

**IMPORTANTE:** Você precisa adicionar o import no topo do arquivo:
```python
from src.i18n.translator import tr
```

---

### 2. **config/locales/pt_BR.json**

Adicionar as traduções correspondentes:

```json
{
  "file_list": {
    "header_name": "Nome",
    "header_size": "Tamanho",
    "header_modified": "Modificado",
    "header_permissions": "Permissões",
    "header_path": "Caminho"
  }
}
```

---

### 3. **src/gui/widgets/file_list_table_manager.py** (continuação)

#### 🔍 O que procurar:
Método `retranslateUi()` - se NÃO existir, você precisa criar!

#### ✏️ Como traduzir:

Adicione este método na classe `FileListTableManager`:

```python
def retranslateUi(self):
    """Atualiza headers quando idioma muda."""
    self.table.setHorizontalHeaderLabels([
        tr("file_list.header_name"),
        tr("file_list.header_size"),
        tr("file_list.header_modified"),
        tr("file_list.header_permissions"),
        tr("file_list.header_path")
    ])
```

**ATENÇÃO:** Este método precisa ser **conectado ao sinal de mudança de idioma**. Procure por `language_changed.connect()` no arquivo `file_explorer_dock.py` e adicione:

```python
# Em FileExplorerDock.__init__() ou em _connect_signals()
app.language_changed.connect(self.table_manager.retranslateUi)
```

---

### 4. **Botões Export CSV e Save Results**

#### 🔍 Localização:
Arquivo: `src/gui/file_explorer_dock.py`  
Linhas: ~551-563

**VERIFICAÇÃO:** Estes botões JÁ ESTÃO TRADUZIDOS:
```python
self.btn_save_results = QPushButton(tr("file_list.btn_save_results"))
self.btn_export_csv = QPushButton(tr("file_list.btn_export_csv"))
```

**Se você ainda vê em inglês:**
1. Verifique se `config/locales/pt_BR.json` tem as chaves:
   ```json
   {
     "file_list": {
       "btn_save_results": "Salvar Resultados",
       "btn_export_csv": "Exportar CSV"
     }
   }
   ```

2. Reinicie a aplicação após mudar para português.

---

### 5. **Mensagem "No File Listed"**

#### 🔍 O que procurar:
Esta mensagem pode estar em:
- `file_list_table_manager.py` - método `clear()` ou `set_data()`
- `file_explorer_dock.py` - ao mostrar status vazio

#### ✏️ Como traduzir:

**ANTES**:
```python
self.lbl_status.setText("No File Listed")
```

**DEPOIS**:
```python
self.lbl_status.setText(tr("file_list.no_files_listed"))
```

**Adicionar ao pt_BR.json**:
```json
{
  "file_list": {
    "no_files_listed": "Nenhum arquivo listado"
  }
}
```

---

### 6. **Quick Filter**

#### 🔍 Localização provável:
Arquivo: `src/gui/widgets/file_list_table_manager.py` ou similar  
Procure por: `QLineEdit` com placeholder "Quick Filter"

#### ✏️ Como traduzir:

**ANTES**:
```python
self.ed_quick_filter = QLineEdit()
self.ed_quick_filter.setPlaceholderText("Quick Filter")
```

**DEPOIS**:
```python
self.ed_quick_filter = QLineEdit()
self.ed_quick_filter.setPlaceholderText(tr("file_list.placeholder_quick_filter"))
```

**Adicionar ao pt_BR.json**:
```json
{
  "file_list": {
    "placeholder_quick_filter": "Filtro Rápido"
  }
}
```

---

### 7. **Include Globs, Options, Case Sensitive, etc.**

Estes provavelmente estão em:
- `src/gui/widgets/file_filter_panel.py`
- `src/gui/widgets/search_options_panel.py`
- `src/gui/widgets/filename_query_panel.py`
- `src/gui/widgets/content_query_panel.py`

#### 📝 Método de busca manual:

1. **Abra cada arquivo listado acima**
2. **Procure por (Ctrl+F):**
   - `QLabel("Include Globs")`
   - `QLabel("Options")`
   - `QCheckBox("Case Sensitive")`
   - `QCheckBox("Whole Word")`
   - `QCheckBox("Preserve Case")`
   - `QLabel("Size Min")`
   - `QLabel("Size Max")`
   - `QLabel("Extensions")`
   - `QLabel("Max Depth")`
   - `QLabel("Modified After")`
   - Qualquer texto `"contains"`

3. **Substitua por chamadas `tr()`:**
   - `QLabel("Size Min")` → `QLabel(tr("file_filter.size_min"))`
   - `QCheckBox("Case Sensitive")` → `QCheckBox(tr("search_options.case_sensitive"))`

4. **Adicione ao pt_BR.json** as traduções correspondentes.

---

## 🔧 Verificação de Import

**TODOS os arquivos modificados precisam ter no topo:**

```python
from src.i18n.translator import tr
```

Se já existir `from src.i18n.translator import tr, tooltip_tr`, está OK!

---

## ✅ Checklist de Validação

Após fazer as mudanças:

1. [ ] Adicionei `from src.i18n.translator import tr` onde necessário
2. [ ] Adicionei TODAS as chaves no `config/locales/pt_BR.json`
3. [ ] Reiniciei a aplicação
4. [ ] Mudei o idioma para Português via menu
5. [ ] Verifiquei CADA string reportada visualmente na GUI
6. [ ] Testei modo Tree E modo Table
7. [ ] Testei com Advanced Filters habilitado
8. [ ] Todas as strings agora aparecem em português ✅

---

## 🚨 Problema Comum: "Mudei mas não aparece"

### Possíveis causas:

1. **Arquivo JSON com erro de sintaxe**
   - Validar com: https://jsonlint.com/
   - Ou rodar: `python -m json.tool config/locales/pt_BR.json`

2. **Cache do Qt**
   - Limpar: `rm -rf ~/.cache/Clarify/`
   - Reiniciar aplicação

3. **Método retranslateUi() não conectado**
   - Procurar por `language_changed.connect()` no código
   - Adicionar conexão do widget ao sinal

4. **Import path errado**
   - Usar: `from src.i18n.translator import tr` (relativo ao src/)
   - NÃO usar: `from utils.i18n import tr`

---

## 📞 Checklist Final

Se TUDO falhar, verifique:

- [ ] O arquivo `pt_BR.json` está bem formatado (sem vírgulas extras, etc)?
- [ ] As chaves em `tr("file_list.header_name")` batem EXATAMENTE com o JSON?
- [ ] O widget tem método `retranslateUi()` E está conectado ao signal?
- [ ] A aplicação foi **reiniciada** após as mudanças?
- [ ] O idioma foi trocado para Português depois de reiniciar?

---

**BOA SORTE!** 🎯

Se encontrar alguma string que NÃO está neste guia, siga o mesmo padrão:
1. Encontre o texto hardcoded
2. Substitua por `tr("categoria.chave")`
3. Adicione tradução no `pt_BR.json`
4. Reinicie e teste
