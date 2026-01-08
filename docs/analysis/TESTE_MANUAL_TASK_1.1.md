# 🧪 INSTRUÇÕES DE TESTE MANUAL - Task 1.1 (Advanced Filters)

**Data**: 02/01/2026  
**Tarefa**: Sprint 1 - Task 1.1 - Etapa 7  
**Duração Estimada**: 15-20 minutos  
**Commit**: 57b34f1

---

## 🎯 OBJETIVO

Validar que os **Advanced Filters** do File Explorer agora funcionam corretamente após as correções implementadas:
1. ✅ Logging adicionado para debug
2. ✅ Conditions aplicadas ANTES do content search (otimização)
3. ✅ Duplicate conditions application removida
4. ✅ Exception handling melhorado

---

## 🚀 PREPARAÇÃO

### Passo 1: Iniciar Aplicação
```bash
cd /home/josue/Documents/Informática/Programação/programming\ workspace/System\ Management\ JSON\ Files\ -\ Clarify\ project/clarify
python -m src
```

### Passo 2: Abrir File Explorer
- Menu: **Tools** → **File Explorer**
- Ou atalho: **Ctrl+Shift+F** (se configurado)

---

## 📋 TESTES MANUAIS

### ✅ TESTE 1: Filtro de Tamanho (>1MB)

**Objetivo**: Verificar que filtro de tamanho funciona

**Passos**:
1. No File Explorer, selecione um diretório com vários arquivos (ex: `/home/josue/Documents`)
2. Expandir seção **⚙️ Filters** (clicar no título se collapsible)
3. Configurar filtro de tamanho:
   - **Size**: Marcar checkbox
   - **Operator**: `>` (maior que)
   - **Value**: `1` 
   - **Unit**: `MB`
4. Clicar em **🔍 Search** ou **📁 Browse**
5. Verificar resultados

**Resultado Esperado**:
- ✅ Apenas arquivos maiores que 1MB aparecem
- ✅ Log no console/arquivo mostra: `Built filters dictionary` com `size_filter: true`
- ✅ Arquivos pequenos (<1MB) NÃO aparecem

**Se Falhar**:
- ❌ Verificar log: `tail -f logs/clarify.log | grep "Built filters"`
- ❌ Todos os arquivos aparecem = filtro não aplicado

---

### ✅ TESTE 2: Filtro de Extensão (.py)

**Objetivo**: Verificar que filtro de extensão funciona

**Passos**:
1. No File Explorer, selecione diretório do projeto: `/home/josue/Documents/.../clarify/src`
2. Expandir **⚙️ Filters**
3. Configurar extensões:
   - **Extensions**: Campo de texto
   - Digite: `.py`
4. Clicar em **🔍 Search**
5. Verificar resultados

**Resultado Esperado**:
- ✅ Apenas arquivos `.py` aparecem
- ✅ Log mostra: `extensions: ['.py']`
- ✅ Arquivos `.md`, `.json`, etc. NÃO aparecem

**Se Falhar**:
- ❌ Verificar se campo de extensões está visível
- ❌ Todos os arquivos aparecem = filtro ignorado

---

### ✅ TESTE 3: Filtro de Data (Últimos 7 Dias)

**Objetivo**: Verificar que filtro de data modificada funciona

**Passos**:
1. No File Explorer, selecione um diretório
2. Expandir **⚙️ Filters**
3. Configurar data:
   - **Modified**: Checkbox marcado
   - **After**: Data de 7 dias atrás (ex: `2025-12-26`)
4. Clicar em **🔍 Search**
5. Verificar resultados

**Resultado Esperado**:
- ✅ Apenas arquivos modificados após `2025-12-26` aparecem
- ✅ Log mostra: `mtime_filter: true`
- ✅ Arquivos antigos NÃO aparecem

**Se Falhar**:
- ❌ Verificar formato da data no campo
- ❌ Arquivos antigos aparecem = filtro não aplicado

---

### ✅ TESTE 4: Múltiplos Filtros (AND Logic)

**Objetivo**: Verificar que múltiplos filtros funcionam em conjunto

**Passos**:
1. No File Explorer, selecione: `/home/josue/Documents/.../clarify/src`
2. Expandir **⚙️ Filters**
3. Configurar MÚLTIPLOS filtros:
   - **Extensions**: `.py`
   - **Size**: `> 1 KB` (maior que 1 kilobyte)
4. Clicar em **🔍 Search**
5. Verificar resultados

**Resultado Esperado**:
- ✅ Apenas arquivos `.py` E maiores que 1KB aparecem
- ✅ Log mostra: `total_filters: 2` ou mais
- ✅ Arquivos `.py` pequenos (<1KB) NÃO aparecem
- ✅ Arquivos grandes mas não-`.py` NÃO aparecem

**Se Falhar**:
- ❌ Todos os `.py` aparecem = filtro de size ignorado
- ❌ Todos os arquivos aparecem = ambos ignorados

---

### ✅ TESTE 5: Advanced Conditions (Se disponível)

**Objetivo**: Verificar que Advanced Conditions Grid funciona

**Passos**:
1. No File Explorer, selecione um diretório
2. Expandir **🎯 Advanced Conditions** (se existir)
3. Adicionar condição:
   - **Field**: `ext` (extensão)
   - **Operator**: `=` (igual)
   - **Value**: `.py`
4. Clicar em **🔍 Search**
5. Verificar resultados

**Resultado Esperado**:
- ✅ Apenas arquivos `.py` aparecem
- ✅ Log mostra: `Applied X advanced conditions EARLY`
- ✅ Conditions funcionam

**Se Falhar**:
- ❌ Verificar se ConditionsGrid existe na UI
- ❌ Conditions podem não estar implementadas ainda

---

## 📊 CHECKLIST FINAL

Após executar todos os testes, marque os resultados:

- [ ] ✅ **Teste 1**: Filtro de tamanho PASSOU
- [ ] ✅ **Teste 2**: Filtro de extensão PASSOU
- [ ] ✅ **Teste 3**: Filtro de data PASSOU
- [ ] ✅ **Teste 4**: Múltiplos filtros PASSOU
- [ ] ✅ **Teste 5**: Advanced Conditions PASSOU (ou N/A)

### Logs Verificados:
- [ ] ✅ Log `Built filters dictionary` aparece no console
- [ ] ✅ Filtros mostram valores corretos (extensions, size, mtime)
- [ ] ✅ Sem erros `ERROR` ou `CRITICAL` no log

---

## 🐛 SE ALGO FALHAR

### Problema: Filtros não aplicam (todos os arquivos aparecem)

**Diagnóstico**:
```bash
# Ver logs em tempo real
tail -f logs/clarify.log | grep -E "Built filters|Filter.*rejected"
```

**Possíveis Causas**:
1. ❌ Logging não funciona → verificar se logger configurado
2. ❌ Filtros construídos mas não passados → verificar `_build_filters()` chamado
3. ❌ Executor ignora filtros → verificar `execute_browse(filters=...)`

### Problema: Aplicação não inicia

**Solução**:
```bash
# Verificar se há erros de import
python -m src 2>&1 | grep -E "ImportError|ModuleNotFoundError"

# Se houver, executar:
python -m black src/gui/file_explorer_dock.py src/core/file_explorer_executor.py src/core/file_list_executor.py
```

---

## ✅ APÓS TODOS OS TESTES PASSAREM

**Marcar no TODO do projeto**:
```markdown
- [x] Etapa 7: Testar (COMPLETO - XX/XX TESTES PASSARAM)
```

**Próximos Passos**:
- [ ] Etapa 12: Deploy local (reiniciar aplicação)
- [ ] Etapa 13: Monitorar (usar por 1 dia, verificar logs)

---

## 📝 RELATAR RESULTADOS

**Formato**:
```
TESTE 1 (Tamanho >1MB): ✅ PASSOU / ❌ FALHOU
TESTE 2 (Extensão .py): ✅ PASSOU / ❌ FALHOU
TESTE 3 (Data modificada): ✅ PASSOU / ❌ FALHOU
TESTE 4 (Múltiplos filtros): ✅ PASSOU / ❌ FALHOU
TESTE 5 (Advanced Conditions): ✅ PASSOU / ❌ FALHOU / ⚠️ N/A

Logs verificados: ✅ SIM / ❌ NÃO
Erros encontrados: [descrição ou "nenhum"]
```

**Me informe os resultados** para eu continuar com Task 1.2 ou corrigir problemas encontrados.

---

**Tempo Estimado**: 15-20 minutos  
**Status**: 🟡 AGUARDANDO EXECUÇÃO PELO USUÁRIO
