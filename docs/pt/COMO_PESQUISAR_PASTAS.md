# Como Pesquisar Pastas no File Explorer

**Criado:** 2026-01-09  
**Versão:** v2.9.120

## Resumo Rápido

Para pesquisar **pastas** (diretórios) no File Explorer:

1. Abra o **File Explorer** dock
2. Informe o diretório base no campo **"Directory"**
3. No filtro **"Type"**, selecione **"Directories Only"** (ou "Apenas Diretórios")
4. Marque **"Recursive"** se quiser buscar em subdiretórios
5. Clique em **"Browse"** ou **"Search"**

---

## Passo a Passo Detalhado

### 1. Campo "Directory" (Diretório Base)

Este é o ponto de partida da busca:

```
┌─────────────────────────────────────────────┐
│ Directory: /home/user/project               │
│ [Browse Directory...]                       │
└─────────────────────────────────────────────┘
```

**O que você pode informar:**
- Caminho absoluto: `/home/user/project`
- Caminho relativo: `./src`
- Diretório atual: `.`

### 2. Filtro "Type" (Tipo de Arquivo)

Este filtro controla **o que será listado**:

```
┌─────────────────────────────────────┐
│ Type: [▼ Directories Only]          │
└─────────────────────────────────────┘
```

**Opções disponíveis:**

| Opção | Valor Técnico | O que mostra |
|-------|---------------|--------------|
| **Any** (Qualquer) | `"any"` | Arquivos + Pastas |
| **Files Only** (Apenas Arquivos) | `"files"` | Somente arquivos |
| **Directories Only** (Apenas Diretórios) | `"dirs"` | Somente pastas ✅ |

**Para pesquisar pastas:** Selecione **"Directories Only"**

### 3. Opção "Recursive" (Recursivo)

Controla se a busca entra em subdiretórios:

```
☑ Recursive (Recursivo)
```

- **Marcado:** Busca em todas as subpastas
- **Desmarcado:** Busca apenas no diretório informado (nível 1)

**Exemplo:**
```
/home/user/project/
├── src/              ← Encontra se Recursive = ON
│   └── core/         ← Encontra se Recursive = ON
├── docs/             ← Sempre encontra
└── tests/            ← Sempre encontra
```

### 4. Filtros Adicionais para Pastas

#### a) Nome da Pasta (Filename Pattern)

Use wildcards para filtrar por nome:

```
┌──────────────────────────────────────┐
│ Filename Pattern: test*              │
└──────────────────────────────────────┘
```

**Exemplos:**
- `test*` → Pastas que começam com "test": `tests/`, `test_data/`
- `*cache*` → Pastas que contém "cache": `.cache/`, `cache_dir/`
- `src` → Exatamente "src"

#### b) Exclude Globs (Excluir Padrões)

Exclui pastas específicas da busca:

```
┌────────────────────────────────────────────────┐
│ Exclude Globs: node_modules;.git;.venv         │
└────────────────────────────────────────────────┘
```

**Separe com ponto-e-vírgula (;)**

**Exemplos comuns:**
- `.git` → Exclui pasta git
- `node_modules` → Exclui dependências Node.js
- `.venv;venv` → Exclui ambientes virtuais Python
- `__pycache__` → Exclui cache Python

#### c) Advanced Conditions (Condições Avançadas)

Para filtros mais complexos, use a seção **"Advanced Conditions"**:

**Exemplo 1: Pastas modificadas recentemente**
```
Field: Modified Time
Operator: greater than
Value: 2026-01-01
```

**Exemplo 2: Pastas com nome específico**
```
Field: Path
Operator: contains
Value: backup
```

---

## Exemplos Práticos

### Exemplo 1: Encontrar todas as pastas `src` no projeto

**Configuração:**
```
Directory: /home/user/project
Type: Directories Only
Recursive: ✓ (marcado)
Filename Pattern: src
```

**Resultado:**
```
/home/user/project/src/
/home/user/project/backend/src/
/home/user/project/frontend/src/
```

---

### Exemplo 2: Encontrar pastas de teste no nível raiz

**Configuração:**
```
Directory: /home/user/project
Type: Directories Only
Recursive: ✗ (desmarcado)
Filename Pattern: test*
```

**Resultado:**
```
/home/user/project/tests/
/home/user/project/test_data/
```

---

### Exemplo 3: Encontrar todas as pastas `.cache` exceto em `node_modules`

**Configuração:**
```
Directory: /home/user/project
Type: Directories Only
Recursive: ✓ (marcado)
Filename Pattern: .cache
Exclude Globs: node_modules;.git
```

**Resultado:**
```
/home/user/project/.cache/
/home/user/.cache/
(não mostra /home/user/project/node_modules/.cache/)
```

---

### Exemplo 4: Pastas criadas na última semana

**Configuração:**
```
Directory: /home/user/project
Type: Directories Only
Recursive: ✓ (marcado)

Advanced Conditions:
  Field: Modified Time
  Operator: greater than
  Value: 2026-01-02
  Logic: AND
```

---

## Como Funciona Internamente

### Fluxo de Execução

1. **`FileListExecutor.list_files()`** coleta todos os arquivos e pastas
2. **Filtro de tipo** aplica:
   ```python
   if type_filter == "dirs":
       file_list = [f for f in file_list if f.is_dir]
   ```
3. **Exclude globs** remove pastas excluídas
4. **Filename pattern** filtra por nome (wildcards)
5. **Advanced conditions** aplica filtros extras
6. **Resultado** é exibido na tabela

### Código Relevante

**Arquivo:** `src/core/file_explorer_executor.py`  
**Linhas:** 123-129

```python
# Apply type filter
type_filter = filters.get("type", "any")
if type_filter == "files":
    file_list = [f for f in file_list if not f.is_dir]
elif type_filter == "dirs":
    file_list = [f for f in file_list if f.is_dir]
# "any": keep all
```

---

## Dicas e Truques

### 1. Busca Rápida de Pastas Comuns

**Pastas de cache:**
```
Filename Pattern: *cache*
Type: Directories Only
```

**Pastas de configuração:**
```
Filename Pattern: .*
Type: Directories Only
```

**Pastas de build:**
```
Filename Pattern: *build*;dist;out
Type: Directories Only
```

### 2. Excluir Pastas Grandes

Ao buscar recursivamente, exclua pastas que não precisa:

```
Exclude Globs: node_modules;.venv;venv;.git;dist;build;__pycache__
```

Isso torna a busca **muito mais rápida**.

### 3. Usar com Replace

Você **não pode** fazer Replace em pastas (só em arquivos).  
Mas pode usar a busca para **mapear estrutura** antes de operações em massa.

### 4. Export para CSV

Depois de encontrar as pastas, exporte para CSV:

```
[Export to CSV]
```

Útil para:
- Documentação de estrutura de projeto
- Auditoria de diretórios
- Scripts de automação

---

## Limitações Conhecidas

1. **Content Search não funciona em pastas**
   - Pastas não têm "conteúdo" para buscar
   - Use apenas filtros de nome/path/data

2. **Permissions podem bloquear acesso**
   - Se não tem permissão para ler um diretório, ele será pulado
   - Erros aparecem na seção de erros

3. **Symlinks seguem comportamento padrão**
   - Links simbólicos são seguidos
   - Cuidado com loops infinitos!

---

## Perguntas Frequentes

### P: Como busco pastas vazias?

**R:** Não há filtro direto para isso. Mas você pode:
1. Listar todas as pastas
2. Exportar para CSV
3. Usar script Python para verificar se estão vazias

### P: Como busco pastas por tamanho?

**R:** Pastas não têm "tamanho" direto. Mas você pode:
- Usar `du` do sistema operacional
- Criar condição avançada no campo `size` (soma dos arquivos internos)

### P: Posso selecionar múltiplas pastas?

**R:** Sim! Em modo dialog:
1. Configure o filtro
2. Clique "Search"
3. Segure Ctrl/Cmd e clique nas pastas
4. Clique "OK"

### P: Como excluo pastas ocultas?

**R:** Desmarque a opção **"Show Hidden Files"**

```
☐ Show Hidden Files (Mostrar arquivos ocultos)
```

---

## Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| **Ctrl+B** | Browse (listar) |
| **Ctrl+F** | Search (buscar) |
| **Ctrl+E** | Export CSV |
| **F5** | Refresh |

---

## Resumo Final

**Para buscar pastas:**
1. ✅ Informe o diretório base
2. ✅ Selecione "Type: Directories Only"
3. ✅ Marque "Recursive" (se quiser subpastas)
4. ✅ Use filtros adicionais (opcional)
5. ✅ Clique "Browse" ou "Search"

**O resultado mostrará apenas pastas!** 📁

---

**Versão do guia:** v2.9.120  
**Última atualização:** 2026-01-09  
**Mais informações:** Consulte a documentação principal do Clarify
