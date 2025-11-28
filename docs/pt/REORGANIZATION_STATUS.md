# 📁 Reorganização do Projeto Clarify

## ✅ Status Atual

O projeto foi reorganizado do arquivo monolítico `clarify.py` (3,578 linhas) para uma estrutura modular com **pastas no diretório atual** (não mais dentro de `clarify_app/`).

## 📂 Nova Estrutura (Criada no Diretório Atual)

```
/home/josue/.../clarify/
├── clarify.py              ← Arquivo original (mantido como backup)
├── clarify_patched.py      ← Backup anterior
├── pyproject.toml
├── README.md
├── old/
│   ├── old_other_version_clarify.py
│   └── other_version_clarify.py
│
├── core/                   ✅ CRIADO
│   ├── __init__.py
│   ├── search_replace.py   ← SearchOptions, preserve_case_like, replace_in_text
│   ├── insert.py           ← InsertMode, insert_at_line
│   └── filters.py          ← Condition, filter_files_by_conditions, OPS
│
├── utils/                  ✅ CRIADO
│   ├── __init__.py
│   ├── file_utils.py       ← walk_files, read_text, write_text, safe_backup_file
│   ├── text_utils.py       ← mask/unmask exclusions, compile_value_union_regex
│   └── ts_utils.py         ← load_ts_object, dump_ts_object, strip_export_default
│
├── rewriter/               ✅ CRIADO (PARCIAL)
│   ├── __init__.py
│   ├── types.py            ← Obj, JSONNode, parse_json_preserving_duplicates_text
│   └── rewriter.py         ← sanitize_keys_and_values (COM BUG FIX CRÍTICO ✅)
│
├── translators/            ✅ CRIADO (vazio - aguardando migração)
├── ui/                     ✅ CRIADO (vazio - aguardando migração)
└── cli/                    ✅ CRIADO (vazio - aguardando migração)
```

## 🎯 O Que Foi Feito

### 1. ✅ Removido `clarify_app/`
A estrutura anterior estava **dentro** de `clarify_app/`, o que estava errado. Agora as pastas estão **no diretório atual**.

### 2. ✅ Criadas 6 Pastas Principais
- **core/** - Lógica de negócios (busca, substituição, inserção, filtros)
- **utils/** - Utilitários (arquivos, texto, TypeScript/JavaScript)
- **rewriter/** - JSON Rewriter com dedupe/join/eliminate
- **translators/** - JSON Translator (aguardando migração)
- **ui/** - Interface gráfica PySide6 (aguardando migração)
- **cli/** - Comandos CLI (aguardando migração)

### 3. ✅ Código Extraído e Organizado
Total de **11 arquivos Python** criados até agora com código **extraído do clarify.py**:

#### core/ (4 arquivos)
- `search_replace.py` (70 linhas) - Busca e substituição com regex
- `insert.py` (58 linhas) - Inserção de texto em linhas específicas
- `filters.py` (85 linhas) - Filtros avançados com condições
- `__init__.py` - Exports do módulo

#### utils/ (4 arquivos)
- `file_utils.py` (74 linhas) - Operações de arquivo
- `text_utils.py` (104 linhas) - Processamento de texto
- `ts_utils.py` (93 linhas) - TypeScript/JavaScript utilities
- `__init__.py` - Exports do módulo

#### rewriter/ (3 arquivos)
- `types.py` (37 linhas) - Tipos customizados (Obj, JSONNode)
- `rewriter.py` (105 linhas) - **COM BUG FIX CRÍTICO** ✅
- `__init__.py` - Exports do módulo

### 4. 🐛 Bug Fix Crítico Preservado

O fix para perda de dados no JSON Rewriter foi **preservado** em `rewriter/rewriter.py`:

```python
def walk(v):
    # Handle Obj type (list of key-value tuples used by JSON Rewriter)
    # *** THIS IS THE CRITICAL BUG FIX ***
    if isinstance(v, Obj):
        out = Obj()
        for k, x in v:
            nk = clean_key(k)
            if nk is None:
                continue
            vx = walk(x)
            if drop_empty_values and isinstance(vx, str) and not vx.strip():
                continue
            out.append((nk, vx))
        return out
    # ... rest of code
```

## 📊 Progresso

### ✅ Concluído (34%)
- core/ (100% - 4/4 arquivos)
- utils/ (100% - 4/4 arquivos)
- rewriter/ (30% - 3/10 arquivos esperados)

### 🚧 Pendente (66%)
- rewriter/ - Faltam: ts_parser.py, operations.py, serializer.py
- translators/ - Faltam: translator.py, scopes.py
- ui/ - Faltam: main_window.py, widgets.py, themes.py
- cli/ - Faltam: args_parser.py, commands.py

## 🔄 Próximos Passos

1. Completar módulo **rewriter/** (ts_parser, operations, serializer)
2. Migrar **CodeAwareJSONTranslator** para translators/
3. Extrair GUI components para ui/
4. Extrair CLI commands para cli/
5. Criar **main.py** novo ponto de entrada
6. Criar testes de validação

## 💡 Diferenças da Tentativa Anterior

| Aspecto | ❌ Tentativa Anterior | ✅ Agora |
|---------|----------------------|----------|
| Localização | `clarify_app/core/` | `core/` (raiz) |
| Estrutura | Dentro de package | **Pastas na raiz** |
| Imports | `from clarify_app.core import ...` | `from core import ...` |
| Arquivos movidos | ❌ Nenhum | ✅ Código extraído |

## 🎯 Objetivo Final

Transformar o monólito `clarify.py` em uma **estrutura modular profissional** mantendo:
- ✅ Funcionalidade completa
- ✅ Bug fixes críticos
- ✅ Código organizado e testável
- ✅ Fácil manutenção e extensão

---

**Data**: 2025-01-23  
**Autor**: Josué Amaral
