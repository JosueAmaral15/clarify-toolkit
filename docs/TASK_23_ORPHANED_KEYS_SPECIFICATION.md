# Task #23 - Orphaned Keys/References Update System

**Status**: ⚠️ PARCIALMENTE IMPLEMENTADO (v2.9.10)  
**Priority**: SHOULD HAVE  
**Complexity**: HIGH  
**Sprint Target**: v2.9.14 (COMPLETAR)  

---

## 📋 Problema Original

### Contexto
Quando o **JSON Rewriter** elimina redundâncias de dicionários de tradução (ex: `en.ts`, `pt.ts`), ele remove chaves duplicadas cujos **valores são idênticos**. Porém, arquivos `.tsx`/`.jsx` que referenciam as chaves eliminadas ficam com **referências órfãs**, causando erro `undefined` em runtime.

### Exemplo Real

**Dicionário ANTES** (`tests/files/en.ts`):
```typescript
export const en = {
  pages: {
    contact: {
      lookingForQuickAnswers: "Looking for quick answers? Check out our"
    },
    contactPage: {
      lookingForQuickAnswers: "Looking for quick answers? Check out our"  // ❌ DUPLICADO
    }
  }
}
```

**Dicionário DEPOIS** (eliminação de redundâncias):
```typescript
export const en = {
  pages: {
    contact: {
      lookingForQuickAnswers: "Looking for quick answers? Check out our"
    }
    // ❌ contactPage REMOVIDO (linha maior = prioridade menor)
  }
}
```

**Arquivo JSX AFETADO** (`tests/files/page.tsx`):
```tsx
export default function contact() {
  const {t} = useTranslation();
  return (
    <div>
      {/* ❌ REFERÊNCIA ÓRFÃ: t.pages.contactPage não existe mais! */}
      <p>{t.pages.contactPage.lookingForQuickAnswers}</p>
    </div>
  )
}
```

**Resultado**: `undefined` em runtime porque `t.pages.contactPage` foi eliminado.

---

## ✅ Solução Completa

### Workflow Esperado

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SCAN FASE (ANTES de eliminar redundâncias)              │
├─────────────────────────────────────────────────────────────┤
│   • Ler dicionário original (en.ts, pt.ts)                 │
│   • Extrair TODAS as chaves com valores                    │
│   • old_keys = {                                            │
│       't.pages.contact.lookingForQuickAnswers',             │
│       't.pages.contactPage.lookingForQuickAnswers'          │
│     }                                                        │
│   • old_values = {                                          │
│       't.pages.contact.lookingForQuickAnswers':             │
│         "Looking for quick answers? Check out our",         │
│       't.pages.contactPage.lookingForQuickAnswers':         │
│         "Looking for quick answers? Check out our"          │
│     }                                                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ELIMINAÇÃO DE REDUNDÂNCIAS                               │
├─────────────────────────────────────────────────────────────┤
│   • Detectar valores duplicados:                            │
│     - contact.lookingForQuickAnswers (linha 44)             │
│     - contactPage.lookingForQuickAnswers (linha 266) ❌     │
│   • Prioridade: linha MENOR vence (44 < 266)                │
│   • Resultado: contactPage É ELIMINADO                      │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CONSTRUIR SUBSTITUTION MAP                               │
├─────────────────────────────────────────────────────────────┤
│   • Extrair new_keys após eliminação                        │
│   • removed_keys = old_keys - new_keys                      │
│   • Para cada removed_key:                                  │
│     - Buscar new_key com MESMO VALOR (não similaridade!)    │
│     - Mapear: removed_key → new_key                         │
│   • substitution_map = {                                    │
│       't.pages.contactPage.lookingForQuickAnswers':         │
│         't.pages.contact.lookingForQuickAnswers'            │
│     }                                                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. SCAN PROJECT FILES (Fase de Descoberta)                 │
├─────────────────────────────────────────────────────────────┤
│   • Buscar recursivamente em PROJECT_DIR                    │
│   • Extensões: .tsx, .jsx, .ts, .js                         │
│   • Detectar padrões:                                       │
│     - {t.pages.contactPage.lookingForQuickAnswers}          │
│     - t.pages.contactPage.lookingForQuickAnswers            │
│   • Gerar lista de arquivos afetados                        │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. APLICAR SUBSTITUIÇÕES (Automático)                      │
├─────────────────────────────────────────────────────────────┤
│   • Para cada arquivo afetado:                              │
│     - Criar backup .bak (se enabled)                        │
│     - Substituir TODAS as ocorrências:                      │
│       * {t.pages.contactPage.X} → {t.pages.contact.X}      │
│       * t.pages.contactPage.X → t.pages.contact.X          │
│     - Salvar arquivo atualizado                             │
│   • Gerar relatório de substituições                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementação Técnica

### 1. Extração de Keys do Tipo `Obj` (CORRIGIR)

**Problema Atual**: `extract_all_keys_from_dict()` só funciona com `dict`, mas o rewriter usa tipo `Obj` (lista de tuplas).

**Código Atual** (`reference_updater.py:317-344`):
```python
def extract_all_keys_from_dict(data: dict, prefix: str = 't') -> Set[str]:
    """Extract all possible reference paths from a dictionary."""
    keys: Set[str] = set()
    
    def recurse(obj, path: str):
        keys.add(path)
        
        if isinstance(obj, dict):  # ❌ NÃO FUNCIONA COM Obj!
            for key, value in obj.items():
                new_path = f"{path}.{key}"
                recurse(value, new_path)
        elif isinstance(obj, list):
            pass
    
    recurse(data, prefix)
    return keys
```

**Solução**:
```python
from ..utils.json_types import Obj

def extract_all_keys_from_obj(data, prefix: str = 't') -> Dict[str, str]:
    """
    Extract all reference paths AND their values from Obj/dict.
    
    Returns:
        Dict mapping path → value
        Example: {'t.pages.contact.title': 'Contact Us'}
    """
    keys_values: Dict[str, str] = {}
    
    def recurse(obj, path: str):
        if isinstance(obj, Obj):
            for key, value in obj:  # ✅ Suporta Obj (lista de tuplas)
                new_path = f"{path}.{key}"
                if isinstance(value, (str, int, float, bool)):
                    keys_values[new_path] = str(value)
                else:
                    recurse(value, new_path)
        
        elif isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}"
                if isinstance(value, (str, int, float, bool)):
                    keys_values[new_path] = str(value)
                else:
                    recurse(value, new_path)
        
        elif isinstance(obj, list):
            pass  # Arrays não são reference paths
    
    recurse(data, prefix)
    return keys_values
```

---

### 2. Build Substitution Map (REESCREVER)

**Problema Atual**: Usa similaridade de strings ao invés de detectar **valores duplicados**.

**Código Atual** (`reference_updater.py:131-210`):
```python
def build_substitution_map(old_keys: Set[str], new_keys: Set[str]) -> Dict[str, str]:
    """❌ ERRADO: usa string_similarity() ao invés de valores"""
    def string_similarity(s1: str, s2: str) -> float:
        # ... código de similaridade textual
        pass
```

**Solução Correta**:
```python
def build_substitution_map_by_value(
    old_keys_values: Dict[str, str],
    new_keys_values: Dict[str, str]
) -> Dict[str, str]:
    """
    Build substitution map based on VALUE equality (not string similarity).
    
    Strategy:
    1. Identify removed keys: keys in old but not in new
    2. For each removed key, find new key with SAME VALUE
    3. If multiple candidates, prefer key with same parent path
    
    Args:
        old_keys_values: Dict of path → value BEFORE elimination
        new_keys_values: Dict of path → value AFTER elimination
    
    Returns:
        Dict mapping removed_path → kept_path
        Example: {'t.pages.contactPage.title': 't.pages.contact.title'}
    """
    substitution_map = {}
    
    old_paths = set(old_keys_values.keys())
    new_paths = set(new_keys_values.keys())
    removed_paths = old_paths - new_paths
    
    for removed_path in removed_paths:
        removed_value = old_keys_values[removed_path]
        
        # Find candidates with SAME VALUE
        candidates = [
            new_path for new_path, new_value in new_keys_values.items()
            if new_value == removed_value  # ✅ VALUE EQUALITY
        ]
        
        if not candidates:
            continue
        
        # If multiple candidates, prefer same parent path
        if len(candidates) == 1:
            substitution_map[removed_path] = candidates[0]
        else:
            # Get parent path (e.g., "t.pages" from "t.pages.contactPage.title")
            removed_parts = removed_path.split('.')
            removed_parent = '.'.join(removed_parts[:-1])
            
            # Prefer candidate with same parent
            best_match = None
            for candidate in candidates:
                candidate_parts = candidate.split('.')
                candidate_parent = '.'.join(candidate_parts[:-1])
                
                if candidate_parent == removed_parent:
                    best_match = candidate
                    break
            
            if best_match:
                substitution_map[removed_path] = best_match
            else:
                # If no same-parent match, use first candidate
                substitution_map[removed_path] = candidates[0]
    
    return substitution_map
```

---

### 3. Integração com JSON Rewriter Dock

**Localização**: `src/gui/json_rewriter_dock.py` linha ~53-61

**Código Atual** (INCORRETO):
```python
substitution_map = {}
if args.eliminate_duplicates:
    old_keys = rw.extract_all_keys_from_dict(obj.data if hasattr(obj, 'data') else obj)
    obj = rw.eliminate_duplicates(obj)
    new_keys = rw.extract_all_keys_from_dict(obj.data if hasattr(obj, 'data') else obj)
    substitution_map = rw.build_substitution_map(old_keys, new_keys)  # ❌
```

**Código Correto**:
```python
substitution_map = {}
if args.eliminate_duplicates:
    # Extract keys AND values before elimination
    old_keys_values = rw.extract_all_keys_from_obj(obj, prefix='t')  # ✅
    
    # Eliminate duplicates
    obj = rw.eliminate_duplicates(obj)
    
    # Extract keys AND values after elimination
    new_keys_values = rw.extract_all_keys_from_obj(obj, prefix='t')  # ✅
    
    # Build substitution map based on VALUE equality
    substitution_map = rw.build_substitution_map_by_value(
        old_keys_values,
        new_keys_values
    )  # ✅
```

---

## 📦 Parâmetros e Configurações

### GUI Elements (JSON Rewriter Dock)

1. **Checkbox**: `chk_update_refs` (✅ já existe)
   - Label: "Update orphaned references (Task #23)"
   - Tooltip: "Scan project files and update t.key.path references after eliminating duplicates"

2. **Line Edit**: `ed_project_dir` (✅ já existe)
   - Label: "Project Directory"
   - Placeholder: "/path/to/react/project"
   - Button: "Browse..." (QFileDialog)

3. **Checkbox**: `chk_ref_backup` (✅ já existe)
   - Label: "Create .bak backups"
   - Tooltip: "Create backup files (.bak) before updating references"
   - Default: **CHECKED**

### Default Values

```python
DEFAULT_EXTENSIONS = ['.tsx', '.jsx', '.ts', '.js']
DEFAULT_PREFIX = 't'
DEFAULT_BACKUP = True
MAX_KEY_LENGTH = 30  # caracteres
DEFAULT_CASE = 'camelCase'
```

---

## 🎯 Regras de Prioridade

### 1. Linha Menor Vence
Quando dois keys têm **mesmo valor**, o key na **linha menor** do arquivo tem prioridade.

```typescript
// Linha 44
contact: { title: "Contact Us" }  // ✅ MANTÉM (linha 44)

// Linha 266
contactPage: { title: "Contact Us" }  // ❌ REMOVE (linha 266)
```

### 2. Estrutura Mais Antiga Vence
Se ambos estão na mesma linha (improvável), priorizar estrutura declarada primeiro no arquivo.

### 3. Paths Diferentes, Mesmo Pai
Se `t.pages.contact.title` e `t.pages.contactPage.title` têm mesmo valor, priorizar o caminho mais curto (`contact` < `contactPage`).

---

## 🧪 Casos de Teste

### Test 1: Eliminação Simples com Substituição

**Input** (`en.ts`):
```typescript
export const en = {
  pages: {
    contact: { title: "Contact" },        // linha 3
    contactPage: { title: "Contact" }     // linha 4 → REMOVER
  }
}
```

**Project File** (`page.tsx`):
```tsx
<h1>{t.pages.contactPage.title}</h1>
```

**Expected**:
- Substitution Map: `{'t.pages.contactPage.title': 't.pages.contact.title'}`
- Updated `page.tsx`: `<h1>{t.pages.contact.title}</h1>`
- Backup created: `page.tsx.bak`

---

### Test 2: Múltiplas Substituições

**Input** (`en.ts`):
```typescript
export const en = {
  pages: {
    home: {
      hero: { title: "Welcome" },         // linha 4
      heroSection: { title: "Welcome" }   // linha 5 → REMOVER
    }
  }
}
```

**Project Files**:
- `home.tsx`: `{t.pages.home.heroSection.title}`
- `header.tsx`: `{t.pages.home.heroSection.title}`

**Expected**:
- 2 arquivos atualizados
- Ambos com `{t.pages.home.hero.title}`

---

### Test 3: Sem Substituições Necessárias

**Scenario**: Nenhuma key foi eliminada (sem redundâncias).

**Expected**:
- `substitution_map = {}`
- Mensagem: "No orphaned references found in project."

---

### Test 4: Valores Diferentes, Mesma Key

**Input**:
```typescript
export const en = {
  pages: {
    contact: { title: "Contact Us" },
    contactPage: { title: "Get in Touch" }  // ✅ VALOR DIFERENTE
  }
}
```

**Expected**:
- **NÃO ELIMINAR** `contactPage` (valores diferentes)
- `substitution_map = {}`

---

## 📊 Output Examples

### Console Output (Success)

```
✅ References Updated

Updated 5 references in 2 files:
  - page.tsx: 3 changes
  - header.tsx: 2 changes

Substitutions applied:
  t.pages.contactPage.title → t.pages.contact.title
  t.pages.contactPage.description → t.pages.contact.description

Backups created in: /path/to/project/*.bak
```

### QMessageBox (GUI)

```
References Updated

Updated 5 references in 2 files:

  - page.tsx: 3 changes
  - header.tsx: 2 changes
  ... and 0 more files
```

---

## 🚫 Edge Cases e Limitações

### 1. Keys com Mesmo Nome em Paths Diferentes

**Scenario**:
```typescript
{
  pages: { home: { title: "Home" } },
  components: { home: { title: "Home" } }  // ✅ MESMO NOME, PATH DIFERENTE
}
```

**Behavior**: **NÃO MEXER** - não são duplicatas porque paths completos são diferentes.

---

### 2. Keys com Valores Similares (Não Idênticos)

**Scenario**:
```typescript
{
  contact: { msg: "Looking for quick answers? Check out our FAQ" },
  contactPage: { msg: "Looking for quick answers? Check out FAQ" }
}
```

**Behavior**: **NÃO ELIMINAR** - valores diferentes (presença de "our").

---

### 3. Arrays com Valores Duplicados

**Scenario**:
```typescript
{
  tips: ["Speak clearly", "Speak clearly", "Use good intonation"]
}
```

**Behavior**: Tratado separadamente por `remove_duplicate_array_values()` (Task #8).

---

## 📝 Documentação de Código

### Docstrings Obrigatórias

Todas as funções devem ter:
1. **Description**: O que a função faz
2. **Args**: Parâmetros com tipos
3. **Returns**: Tipo e descrição do retorno
4. **Example**: Exemplo de uso (opcional mas recomendado)
5. **Raises**: Exceções lançadas (se aplicável)

**Exemplo**:
```python
def extract_all_keys_from_obj(data, prefix: str = 't') -> Dict[str, str]:
    """
    Extract all reference paths and their values from Obj/dict structure.
    
    Args:
        data: Obj or dict structure from JSON rewriter
        prefix: Prefix for keys (default 't')
    
    Returns:
        Dictionary mapping full path → value
        Example: {'t.pages.contact.title': 'Contact Us'}
    
    Example:
        >>> obj = Obj([('pages', Obj([('contact', Obj([('title', 'Contact')]))]))])
        >>> extract_all_keys_from_obj(obj)
        {'t': '', 't.pages': '', 't.pages.contact': '', 't.pages.contact.title': 'Contact'}
    """
```

---

## ✅ Checklist de Implementação

### Fase 1: Correção do Core (reference_updater.py)

- [ ] **1.1**: Reescrever `extract_all_keys_from_dict()` → `extract_all_keys_from_obj()`
  - [ ] Suportar tipo `Obj` (lista de tuplas)
  - [ ] Retornar `Dict[str, str]` (path → value)
  - [ ] Incluir valores primitivos (str, int, float, bool)

- [ ] **1.2**: Reescrever `build_substitution_map()` → `build_substitution_map_by_value()`
  - [ ] Remover lógica de `string_similarity()`
  - [ ] Comparar por **VALUE EQUALITY**
  - [ ] Implementar prioridade por linha (se possível)
  - [ ] Preferir keys com mesmo parent path

- [ ] **1.3**: Adicionar função `extract_line_numbers()`
  - [ ] Parser de TypeScript para detectar linha de cada key
  - [ ] Usar regex ou AST (opcional, se viável)

### Fase 2: Integração com JSON Rewriter Dock

- [ ] **2.1**: Atualizar `cli_dedupe()` (linha ~53-61)
  - [ ] Substituir `extract_all_keys_from_dict()` por `extract_all_keys_from_obj()`
  - [ ] Substituir `build_substitution_map()` por `build_substitution_map_by_value()`

- [ ] **2.2**: Verificar campos GUI
  - [ ] `ed_project_dir` existe e funciona
  - [ ] `chk_update_refs` existe e funciona
  - [ ] `chk_ref_backup` existe e funciona

### Fase 3: Testes Unitários

- [ ] **3.1**: Test `test_extract_keys_from_obj()`
  - [ ] Testar com tipo `Obj`
  - [ ] Testar com tipo `dict`
  - [ ] Verificar valores corretos

- [ ] **3.2**: Test `test_build_substitution_map_by_value()`
  - [ ] Valores idênticos → substituição
  - [ ] Valores diferentes → sem substituição
  - [ ] Múltiplos candidatos → priorizar same parent

- [ ] **3.3**: Test `test_update_references_integration()`
  - [ ] Criar arquivos TSX de teste
  - [ ] Aplicar substituições
  - [ ] Verificar arquivos atualizados
  - [ ] Verificar backups criados

### Fase 4: Documentação

- [ ] **4.1**: Atualizar `TASKS.md`
  - [ ] Marcar Task #23 como `[X]` completa
  - [ ] Adicionar nota: "v2.9.14 - Task #23: Orphaned Keys Update System (COMPLETO)"

- [ ] **4.2**: Criar changelog entry
  - [ ] Documentar mudanças na v2.9.14
  - [ ] Explicar diferença entre v2.9.10 (parcial) e v2.9.14 (completo)

- [ ] **4.3**: Atualizar README (se necessário)

---

## 🔍 Referências

- **Arquivo Original**: `src/rewriter/reference_updater.py`
- **GUI Integration**: `src/gui/json_rewriter_dock.py` (linha ~390)
- **Tipo Obj**: `src/utils/json_types.py`
- **Tests**: `tests/files/en.ts`, `tests/files/page.tsx`
- **Task History**: TASKS.md (linha 105)

---

## 📅 Timeline

| Fase | Estimativa | Status |
|------|-----------|--------|
| Fase 1 (Core) | 2h | ⚠️ PENDENTE |
| Fase 2 (Integration) | 1h | ⚠️ PENDENTE |
| Fase 3 (Tests) | 1.5h | ⚠️ PENDENTE |
| Fase 4 (Docs) | 0.5h | ✅ COMPLETO (este documento) |
| **TOTAL** | **5h** | **20% COMPLETO** |

---

**Autor**: Josué Amaral  
**Data Criação**: 30/11/2025  
**Última Atualização**: 30/11/2025  
**Sprint**: v2.9.14 (Target)
