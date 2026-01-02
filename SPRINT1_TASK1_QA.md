# Sprint 1 - Task 1.1: Advanced Filters Bug - Q&A

**Data**: 02/01/2026  
**Etapa 3**: Q&A com IA (Protocolo Simplicidade 3)  
**Status**: ✅ ANÁLISE COMPLETA

---

## 📋 RESPOSTAS ÀS 15 PERGUNTAS

### **Q1: Qual o fluxo de execução dos Advanced Filters?**
✅ **Resposta**:
```
FileExplorerDock._list_files() 
  → _build_filters() [linha 1052] → constrói dict de filtros
  → executor.execute_browse() ou execute_search() [linha 862/958]
    → FileListExecutor.list_files() [linha 110]
      → _collect_files() [linha 91]
        → _matches_filters() [linha 175] → AQUI filtros são aplicados
```

### **Q2: Onde os filtros são construídos (`_build_filters()`)?**
✅ **Resposta**: Linha 1052 em `file_explorer_dock.py`
- **Componentes**:
  - Extension filter (linhas 1062-1070)
  - Include/Exclude globs (linhas 1075-1086)
  - Panel filters: regex, size, mtime (linhas 1091-1119)
- **Output**: Dict `filters` com estrutura correta

### **Q3: Como são passados para o executor?**
✅ **Resposta**:
- `execute_browse(directory, ..., filters=filters)` [linha 958]
- `execute_search(directory, ..., filters=filters)` [linha 862]
- Parâmetro explícito, não há problema aqui

### **Q4: O executor recebe e aplica os filtros corretamente?**
✅ **Resposta**: **SIM**
- `FileListExecutor._matches_filters()` [linha 175-238] aplica todos:
  - Regex (linhas 186-192)
  - Size (linhas 195-207)
  - MTime (linhas 210-222)
  - Extensions (linhas 225-231)
  - Depth (linhas 234-236)
- **Código está correto!**

### **Q5: Há logs de debug para rastrear?**
❌ **Resposta**: **NÃO** - Este é o problema!
- `_build_filters()` não tem logs
- `_matches_filters()` não tem logs
- Impossível debugar se filtros estão vazios ou mal formatados

### **Q6: Condições grid está conectada aos filtros?**
⚠️ **Resposta**: **PARCIALMENTE**
- ConditionsGrid é separado dos filtros básicos
- Passado como parâmetro `conditions` (linha 734)
- **Mas não há código aplicando conditions!** ← PROBLEMA #1

### **Q7: Há validação de filtros antes de aplicar?**
❌ **Resposta**: **NÃO**
- Se regex inválido → passa silenciosamente (linha 192)
- Se size values são inválidos → sem validação

### **Q8: Filtros funcionam em Browse mode? E em Search mode?**
✅ **Resposta**: Sim em ambos
- Browse: chama `execute_browse()` diretamente
- Search: chama `execute_browse()` primeiro (linha 197 de executor)
- **Filtros são compartilhados entre os dois modos**

### **Q9: Há testes automatizados para filters?**
❌ **Resposta**: **NÃO VERIFICADO** (mas provavelmente não há testes específicos)

### **Q10: Qual a diferença entre `filters` dict e `conditions` list?**
✅ **Resposta**:
- **`filters`** (dict): Filtros básicos (size, mtime, regex, extensions)
- **`conditions`** (list): Advanced conditions do ConditionsGrid (AND/OR logic)
- **PROBLEMA**: `conditions` NÃO está sendo aplicada! ← PROBLEMA #2

### **Q11: `FileFilterPanel` está conectada corretamente?**
✅ **Resposta**: SIM
- `self.filter_panel.get_filters()` é chamado [linha 1054]
- Retorna dict com valores corretos

### **Q12: Há conflito entre filtros básicos e avançados?**
⚠️ **Resposta**: **POSSÍVEL**
- Filters são aplicados
- Conditions **NÃO** são aplicados
- Não há conflito porque conditions não fazem nada

### **Q13: Extension filter está sobrescrevendo advanced filters?**
❌ **Resposta**: NÃO
- Extension filter é parte dos advanced filters
- Todos coexistem no mesmo dict

### **Q14: Recursive flag afeta aplicação de filtros?**
✅ **Resposta**: NÃO afeta negativamente
- Recursion apenas controla profundidade de busca
- Filtros são aplicados independentemente

### **Q15: Há erro silencioso (try/except engolindo exceções)?**
✅ **Resposta**: SIM, múltiplos pontos:
- Regex error → `pass` [linha 192]
- OSError em size → `pass` [linha 207]
- OSError em mtime → `pass` [linha 222]
- **Erros são silenciados sem logging!** ← PROBLEMA #3

---

## 🎯 PROBLEMAS IDENTIFICADOS

### **🔴 PROBLEMA #1: Advanced Conditions NÃO sendo aplicadas**
**Localização**: `file_explorer_executor.py` linha 165-300  
**Causa Raiz**: Parâmetro `conditions` é recebido mas NUNCA usado

**Código atual**:
```python
def execute_search(
    ...
    conditions: List[Dict[str, Any]] = None,
    logic_operator: str = "AND",
) -> Dict[str, Any]:
    # ...
    browse_result = self.execute_browse(directory, show_hidden, recursive, filters)
    # conditions é ignorado!
```

**Solução**: Aplicar conditions após execute_browse, antes de retornar resultados

---

### **🟡 PROBLEMA #2: Falta de logging para debug**
**Localização**: Múltiplos pontos  
**Causa Raiz**: Código não tem instrumentação adequada

**Solução**: Adicionar logs em:
- `_build_filters()`: log do dict construído
- `_matches_filters()`: log quando filtro rejeita arquivo
- `execute_browse/search()`: log de quantos files passaram nos filtros

---

### **🟡 PROBLEMA #3: Exceções silenciadas sem logging**
**Localização**: `file_list_executor.py` linhas 192, 207, 222  
**Causa Raiz**: Try/except com `pass` sem log

**Solução**: Substituir `pass` por `logger.debug(f"Filter error: {e}")`

---

## 🔧 PLANO DE CORREÇÃO

### **Fase 1: Adicionar Logging (Etapa 5.1)** ⏱️ ~20min
```python
# Em _build_filters() [linha 1052]
filters = {...}
logger.debug(f"Built filters dict", extra={"filters": filters})
return filters

# Em _matches_filters() [linha 175]
def _matches_filters(...):
    if not filters:
        logger.debug(f"No filters, accepting file: {filepath}")
        return True
    
    # Para cada filtro que rejeita
    if not re.search(regex_config['pattern'], filename):
        logger.debug(f"Regex filter rejected", extra={"file": filename, "pattern": regex_config['pattern']})
        return False
```

### **Fase 2: Aplicar Conditions (Etapa 5.2)** ⏱️ ~30min
```python
# Em execute_search() após linha 200
files_to_search = [sr.file_info for sr in browse_result["files"]]

# NOVO: Apply advanced conditions
if conditions:
    from ..core.filters import filter_files_by_conditions
    
    file_paths = [f.path for f in files_to_search]
    filtered_paths, filtered_out = filter_files_by_conditions(
        file_paths, conditions, logic_operator
    )
    
    logger.info(f"Applied {len(conditions)} conditions", extra={
        "filtered_out": filtered_out,
        "remaining": len(filtered_paths)
    })
    
    # Keep only files that passed conditions
    files_to_search = [f for f in files_to_search if f.path in filtered_paths]
```

### **Fase 3: Tratar Exceções (Etapa 5.3)** ⏱️ ~10min
```python
# Substituir em _matches_filters()
except re.error:
    logger.debug(f"Invalid regex pattern", extra={"pattern": regex_config['pattern']})
    pass  # Mantém o pass mas com log

except OSError as e:
    logger.debug(f"Failed to get file size", extra={"file": filepath, "error": str(e)})
    pass  # Mantém o pass mas com log
```

---

## ✅ PRÓXIMAS AÇÕES

**Etapa 4**: Implementar correções em ordem de prioridade
1. ✅ Q&A completo (este documento)
2. ⏭️ Implementar Fase 1 (logging)
3. ⏭️ Implementar Fase 2 (conditions)
4. ⏭️ Implementar Fase 3 (exception handling)
5. ⏭️ Testar manualmente
6. ⏭️ Code review
7. ⏭️ Commit

**Tempo estimado restante**: 1h (20+30+10 = 60min de código)

---

**Status**: ✅ ANÁLISE COMPLETA - PROBLEMAS IDENTIFICADOS  
**Próximo**: Etapa 5 (Implementação) - Começar por Fase 1 (logging)
