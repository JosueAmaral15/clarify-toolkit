# Uso do Extension Filter (v2.9.1)

## 📌 Visão Geral

A partir da versão **2.9.1**, o Extension Filter é **opcional** e controlado por um checkbox na interface.

---

## 🎯 Como Usar

### Interface Gráfica (GUI)

#### 1. Habilitar/Desabilitar o Filtro

```
☑ Use extension filter
Extensions: [.ts,.tsx,.js,.jsx,.py,.md]
```

- **Checkbox marcado** = Filtro **ativo** (extensões serão filtradas)
- **Checkbox desmarcado** = Filtro **inativo** (processará todos os arquivos)

#### 2. Definir Extensões

Quando o checkbox estiver marcado:

```
.py,.js,.tsx       # Com pontos
py,js,tsx          # Sem pontos (auto-adiciona)
.py; .js; .tsx     # Ponto e vírgula também funciona
```

#### 3. Exemplo Prático

**Cenário**: Buscar "TODO" apenas em arquivos Python

1. Marque ☑ "Use extension filter"
2. Digite `.py` no campo Extensions
3. Configure os outros campos (Root Dir, Search Text, etc.)
4. Clique em "Execute"

**Resultado**: Apenas arquivos `.py` serão processados

---

## 🔍 Onde o Filtro Está Disponível

### ✅ Módulos com Extension Filter

| Módulo | Motivo |
|--------|--------|
| **Search/Replace** | Processa qualquer tipo de arquivo de texto |
| **Insert** | Insere texto em qualquer arquivo |

**Esses módulos são genéricos** e podem trabalhar com qualquer extensão.

### ❌ Módulos SEM Extension Filter

| Módulo | Motivo |
|--------|--------|
| **JSON Search** | Apenas `.json`, `.ts`, `.tsx`, `.js`, `.jsx` |
| **JSON Translate** | Dicionário deve ser JSON/TS |
| **JSON Rewriter** | Apenas arquivos JSON/TS |

**Esses módulos já têm extensões fixas**, adicionar filtro seria redundante.

---

## 🧩 Integração com Include/Exclude Globs

O Extension Filter trabalha **em conjunto** com globs:

### Exemplo 1: Extensões + Diretório Específico

```
☑ Use extension filter
Extensions: .py
Include: src/**
```

**Resultado**: Apenas arquivos `.py` dentro de `src/`

### Exemplo 2: Desabilitar Filtro, Usar Apenas Glob

```
☐ Use extension filter  (desmarcado)
Include: tests/**/*.test.js
```

**Resultado**: Apenas arquivos `.test.js` em `tests/` (filtro manual via glob)

### Exemplo 3: Combinar Ambos

```
☑ Use extension filter
Extensions: .tsx,.jsx
Include: src/components/**
Exclude: **/*.test.*
```

**Resultado**: Componentes React em `src/components/`, excluindo testes

---

## 💡 Casos de Uso

### Caso 1: "Quero processar TODOS os arquivos"

```
☐ Use extension filter  (desmarcado)
Include: (vazio)
Exclude: (vazio)
```

### Caso 2: "Apenas Python e JavaScript"

```
☑ Use extension filter
Extensions: .py,.js
```

### Caso 3: "Componentes React no diretório `src`"

```
☑ Use extension filter
Extensions: .tsx,.jsx
Include: src/**
```

### Caso 4: "Markdown fora de node_modules"

```
☑ Use extension filter
Extensions: .md
Exclude: **/node_modules/**
```

---

## ⚙️ Padrão (Default)

- **Checkbox**: ☑ Marcado (habilitado)
- **Extensões**: `.ts,.tsx,.js,.jsx,.py,.md`
- **Comportamento**: Filtra automaticamente esses arquivos

**Motivo**: Retrocompatibilidade com v2.9.0

---

## 🚀 Performance

### Quando o Filtro Ajuda

- ✅ Projetos grandes com muitos tipos de arquivo
- ✅ Evita processar arquivos desnecessários (imagens, binários, etc.)
- ✅ Reduz tempo de execução em 50-80%

### Quando Desabilitar

- ❌ Projetos pequenos (< 100 arquivos)
- ❌ Quando você quer processar TUDO
- ❌ Quando usar globs avançados já é suficiente

---

## 🛠️ Troubleshooting

### "Filtro não está funcionando"

**Possível causa**: Checkbox desmarcado

**Solução**: Marque ☑ "Use extension filter"

### "Extensão não está sendo filtrada"

**Possível causa**: Formato incorreto

**Soluções**:
- ✅ Use `.py` (com ponto)
- ✅ Ou `py` (sem ponto, auto-adiciona)
- ❌ Não use `*.py` (glob, use em include)

### "Quero usar apenas globs, sem filtro simples"

**Solução**: Desmarque ☐ "Use extension filter"

---

## 🔗 Documentos Relacionados

- [EXTENSION_FILTER.md](./EXTENSION_FILTER.md) - Documentação completa
- [EXTENSION_FILTER_ANALYSIS.md](./EXTENSION_FILTER_ANALYSIS.md) - Análise técnica
- [CHANGELOG.md](../../CHANGELOG.md) - Histórico de versões

---

## 📝 Resumo

| Aspecto | Detalhes |
|---------|----------|
| **Versão** | 2.9.1+ |
| **Controle** | Checkbox "Use extension filter" |
| **Default** | Habilitado (retrocompatibilidade) |
| **Disponível em** | Search/Replace, Insert |
| **Indisponível em** | JSON Search, JSON Translate, JSON Rewriter |
| **Sintaxe** | `.py,.js,.tsx` ou `py,js,tsx` |
| **Integração** | Funciona com include/exclude globs |
| **Objetivo** | Simplificar seleção de extensões comuns |

---

**Versão do documento**: 2.9.1  
**Última atualização**: 2025-11-28
