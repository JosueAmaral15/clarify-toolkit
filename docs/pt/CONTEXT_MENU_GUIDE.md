# Guia do Menu de Contexto - Results Panel (v2.9.2)

## 📋 Visão Geral

A partir da versão **2.9.2**, o painel de resultados (à direita) possui um **menu de contexto** completo acessível com **botão direito do mouse**, além de suporte para **seleção múltipla** com CTRL/Shift.

---

## 🖱️ Seleção Múltipla

### Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| **CTRL + Click** | Adicionar/remover item da seleção |
| **Shift + Click** | Selecionar intervalo entre cliques |
| **CTRL + A** | Selecionar todos os itens |

### Exemplos de Uso

#### 1. Selecionar múltiplos arquivos não consecutivos
```
1. Click no primeiro arquivo
2. CTRL + Click no segundo arquivo
3. CTRL + Click no terceiro arquivo
...resultado: 3 arquivos selecionados
```

#### 2. Selecionar intervalo de resultados
```
1. Click no primeiro resultado
2. Shift + Click no último resultado
...resultado: todos os itens entre os cliques ficam selecionados
```

#### 3. Selecionar tudo
```
CTRL + A (ou botão direito > Select All)
...resultado: todos os itens ficam selecionados
```

---

## 📝 Menu de Contexto (Botão Direito)

### Como Acessar
1. **Clique com botão direito** em qualquer lugar do painel de resultados
2. Menu aparece com as seguintes opções:

### Opções Disponíveis

#### 📋 Copy
- **Atalho**: CTRL + C (quando suportado)
- **Função**: Copia itens selecionados para a área de transferência
- **Formato**: Texto formatado com arquivos e matches
- **Requisito**: Pelo menos 1 item selecionado
- **Feedback**: "✅ Copied X item(s) to clipboard"

**Exemplo de saída:**
```
📁 /path/to/file1.py
--------------------------------------------------------------------------------
   12:5  result_text = "example"

📁 /path/to/file2.js
--------------------------------------------------------------------------------
   45:10  const value = 123;
```

#### 📋 Copy All Results
- **Função**: Copia **todos** os resultados da busca
- **Formato**: Texto completo com cabeçalho e estatísticas
- **Requisito**: Pelo menos 1 resultado de busca
- **Feedback**: "✅ Copied all results (X matches) to clipboard"

**Exemplo de saída:**
```
================================================================================
CLARIFY - SEARCH RESULTS
================================================================================
Total files with matches: 5
Total matches: 23
================================================================================

📁 /path/to/file1.py
   Matches: 3
--------------------------------------------------------------------------------
   Line 12, Col 5:
      result_text = "example"
   Line 25, Col 8:
      another_example = True
...
```

#### ✅ Select All
- **Atalho**: CTRL + A
- **Função**: Seleciona todos os itens do painel
- **Uso**: Útil para copiar ou abrir todos os arquivos

#### 📂 Open File
- **Função**: Abre arquivo(s) selecionado(s) no aplicativo padrão do sistema
- **Requisito**: Pelo menos 1 item selecionado
- **Comportamento**:
  - Se selecionar um match (linha), abre o arquivo pai
  - Se selecionar múltiplos matches do mesmo arquivo, abre o arquivo 1 vez
  - Se selecionar matches de arquivos diferentes, abre todos os arquivos
- **Feedback**: "✅ Opened X file(s)"

**Sistemas operacionais suportados:**
- **macOS**: `open`
- **Windows**: `start`
- **Linux**: `xdg-open`

#### 📂 Open All Files
- **Função**: Abre **todos** os arquivos dos resultados
- **Requisito**: Pelo menos 1 resultado de busca
- **Proteção**: Confirma antes de abrir mais de 10 arquivos
- **Feedback**: "✅ Opened X file(s)"

**Exemplo de confirmação (>10 arquivos):**
```
┌─────────────────────────────────────┐
│ Open Many Files                     │
├─────────────────────────────────────┤
│ You are about to open 25 files.    │
│ Continue?                           │
│                                     │
│         [Yes]        [No]           │
└─────────────────────────────────────┘
```

---

## 🎯 Casos de Uso Práticos

### Caso 1: Copiar resultados específicos
```
1. CTRL + Click nos arquivos desejados
2. Botão direito > Copy
3. Cole em editor de texto ou email
```

### Caso 2: Abrir arquivos relevantes
```
1. Shift + Click para selecionar intervalo
2. Botão direito > Open File
3. Arquivos abrem no editor padrão
```

### Caso 3: Exportar todos os resultados
```
1. Botão direito > Copy All Results
2. Cole em relatório ou documentação
3. Resultados incluem estatísticas completas
```

### Caso 4: Revisar rapidamente todos os arquivos
```
1. Botão direito > Open All Files
2. Confirme se > 10 arquivos
3. Todos os arquivos abrem para revisão
```

---

## 💡 Dicas e Truques

### Dica 1: Seleção Eficiente
- **Para poucos itens**: Use CTRL + Click
- **Para muitos itens consecutivos**: Use Shift + Click
- **Para todos**: Use CTRL + A ou Select All

### Dica 2: Feedback Visual
- Após ações de Copy/Open, observe a **barra de status** no rodapé
- Feedback desaparece automaticamente após 3 segundos
- Verde = Sucesso, Vermelho = Erro

### Dica 3: Organização de Resultados
- **Summary header** (primeira linha) não é copiado
- Apenas arquivos e matches reais são incluídos
- Formato mantém hierarquia de árvore

### Dica 4: Integração com Sistema
- Arquivos abrem no aplicativo padrão do SO
- Para abrir em editor específico, configure as associações do SO
- Linux: Use `xdg-mime` para configurar padrões

---

## ⚙️ Configuração Avançada

### Modificar Aplicativo Padrão (Linux)

```bash
# Abrir arquivos .py no VS Code
xdg-mime default code.desktop text/x-python

# Abrir arquivos .js no Sublime Text
xdg-mime default sublime_text.desktop text/javascript
```

### Modificar Aplicativo Padrão (macOS)

```bash
# Abrir arquivos .py no VS Code
defaults write com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers -array-add '{LSHandlerContentType=public.python-script;LSHandlerRoleAll=com.microsoft.VSCode;}'
```

### Modificar Aplicativo Padrão (Windows)

```
1. Botão direito no arquivo > "Open with"
2. Escolha "Choose another app"
3. Marque "Always use this app"
4. Selecione o aplicativo desejado
```

---

## 🐛 Troubleshooting

### Problema: "Copy não funciona"
**Causa**: Nenhum item selecionado  
**Solução**: Selecione pelo menos 1 item antes de copiar

### Problema: "Open File não abre nada"
**Causa**: Arquivo não existe ou caminho inválido  
**Solução**: Verifique se o arquivo foi movido/deletado após a busca

### Problema: "Open All Files abre apenas alguns"
**Causa**: Alguns arquivos podem não existir  
**Solução**: Verifique o console para mensagens de erro

### Problema: "Menu de contexto não aparece"
**Causa**: Possível bug ou configuração do SO  
**Solução**: Tente clicar em uma área com resultados (não em espaço vazio)

### Problema: "CTRL/Shift não funciona para seleção"
**Causa**: Foco não está no painel de resultados  
**Solução**: Clique no painel de resultados antes de usar atalhos

---

## 📊 Comparação com Versões Anteriores

| Recurso | v2.9.1 e anteriores | v2.9.2 |
|---------|---------------------|--------|
| **Seleção** | Apenas 1 item | Múltipla (CTRL/Shift) |
| **Copy** | Não disponível | ✅ Copy e Copy All |
| **Select All** | Manual | ✅ CTRL + A |
| **Open File** | Via botão separado | ✅ Menu de contexto |
| **Open All** | Não disponível | ✅ Com confirmação |
| **Feedback** | Nenhum | ✅ Status bar |

---

## 🔗 Documentos Relacionados

- [CHANGELOG.md](../../CHANGELOG.md) - Histórico de versões
- [TASKS.md](./TASKS.md) - Tarefas e roadmap
- [README.md](../../README.md) - Documentação principal

---

## 📝 Resumo Rápido

| Ação | Método |
|------|--------|
| **Selecionar múltiplos** | CTRL/Shift + Click |
| **Selecionar tudo** | CTRL + A |
| **Copiar selecionados** | Botão direito > Copy |
| **Copiar tudo** | Botão direito > Copy All |
| **Abrir arquivos** | Botão direito > Open File(s) |
| **Abrir tudo** | Botão direito > Open All Files |

---

**Versão do documento**: 2.9.2  
**Última atualização**: 28 de Novembro de 2025  
**Autor**: Josué Amaral
