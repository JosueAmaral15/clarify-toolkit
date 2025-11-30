# Clarify - Programming Tasks

**Author**: Josué Amaral  
**Date**: 2025/10/01  
**Last Update**: 2025/11/24

Este documento contém todas as tarefas de desenvolvimento do Clarify organizadas por prioridade usando o método MoSCoW (Must Have, Should Have, Could Have, Would Have).

---

## 📊 Legenda

- `[X]` - Tarefa completada
- `[]` - Tarefa pendente
- **MUST HAVE** - Funcionalidades críticas/essenciais
- **SHOULD HAVE** - Funcionalidades importantes mas não críticas
- **COULD HAVE** - Funcionalidades desejáveis se houver tempo
- **WOULD HAVE LATER** - Funcionalidades futuras de longo prazo

---

## 🔴 MUST HAVE (Alta Prioridade)

### ✅ Tasks Concluídas

- **[X]** Implementar threads para busca de arquivos
- **[X]** Incluir arquivos individuais e não apenas diretórios
- **[X]** Substituir texto do dropdown relativo ao painel de inserção
- **[X]** Resolver o erro: `json.decoder.JSONDecodeError: Expecting ':' delimiter: line 4629 column 21 (char 185171)`
- **[X]** Evitar override: impedir que JSON Translate sobrescreva nomes de traduções (ex: `{t.pages.Prac{t.pages.Navbar.blog}HistoryPage.blank}`)
- **[X]** Ajustar JSON Translate para traduzir apenas em escopo de código (ex: `children: React.ReactNode` não deve ser traduzido)
- **[X]** Nome da variável do primeiro objeto: permitir customização do nome root (ex: `t`, `i18n`, `translations`)
- **[X]** Adicionar possibilidade de usar expressões regulares em substituições para não substituir certos caracteres
- **[X]** **[CRÍTICO]** Corrigir problema sério no JSON Rewriter onde alguns dados são perdidos durante processamento, omitindo chaves e valores

### ✅ Tasks Concluídas

- **[X]** Adicionar determinação de escopo nas opções avançadas condicionais com múltiplas opções:
  - ✅ Apenas entre colchetes `[...]`
  - ✅ Apenas entre chaves `{...}`
  - ✅ Apenas entre parênteses `(...)`
  - ✅ Apenas entre delimitadores customizados (ex: `begin...end`)
  - ✅ Apenas entre tags HTML/XML (ex: `<div>...</div>`)
  - ✅ Apenas dentro de uma tag específica (ex: apenas dentro de `<script>`)
  - ✅ Implementado como opção em Advanced Conditions com campos Scope e Scope Param
  - ✅ Funciona em combinação com outras condições (filename, path, ext, size, mtime, content)
  - ✅ Suporta busca em múltiplos níveis de aninhamento
  - **Data de conclusão**: 24 de Novembro de 2025

### 🔨 Tasks Pendentes

- **[]** Evitar comportamento: `{t.pages.onboarding.navigationHints.skip} if stuck - unanswered = zero {t.pages.PracticeHistoryPage.points}`
- **[X]** Durante tradução JSON, preservar uppercase com parâmetro do usuário **(v2.9.8)**

---

## 🟡 SHOULD HAVE (Prioridade Média)

### ✅ Tasks Concluídas

- **[x]** Incluir 3 opções de checkbox nas opções avançadas condicionais: case sensitive, match whole word e regular expression *(v2.2.0)*
- **[x]** Incluir possibilidade de busca e lookup de caracteres no painel Insert para inserir caracteres com busca ao invés de somente definir número da linha, estaticamente *(v2.3.0)*
- **[x]** Incluir salvamento de todos os resultados do match panel como arquivo txt *(v2.4.0)*
- **[x]** Incluir barra de progresso para mostrar progresso do processamento *(v2.5.0)*

### 🔨 Tasks Pendentes

#### Interface e Usabilidade
- **[X]** Adicionar funcionalidade de reversão de tradução JSON (Swap Dictionaries + Undo with Backup) **(v2.9.8)**
- **[X]** Adicionar menu com botão direito no painel de matches: copy, copy all, select all, open file, open all files. Suportar CTRL/Shift para seleção múltipla *(v2.9.2 - Context Menu)*
- **[X]** Possibilidade de colocar resultados em arquivos separados (cada iteração) ou em arquivo único **(v2.9.7 - Save Results)**
- **[X]** Habilidade de inserir ranges incluídos/excluídos no Insert, mesmo usando regex **(v2.9.9 - Hierarchical Ranges)**
- **[X]** Corrigir mensagem de Loading (só aparece letra L)
- **[X]** Mostrar quantidade de resultados na primeira linha do match panel
- **[X]** Mostrar posição absoluta do caractere/palavra ao passar mouse sobre resultado no match panel
- **[X]** Adicionar busca por nome de arquivo com suporte a wildcards, prefix e regex **(v2.9.7 - Filename Search)**

#### JSON Features

- **[X]** Incluir possibilidade de mudar case de palavras-chave (camelCase, PascalCase, snake_case, kebab-case) *(v3.0.0 - Case Converter)*
- **[]** Incluir possibilidade de remover certa sub-estrutura JSON de uma estrutura maior
- **[X]** Incluir checkbox "is file" no JSON translate
- **[X]** Ajustar opção 'Emit Export default' do JSON Translate **(v2.9.7)**
- **[X]** Resultado do JSON Translate não deve conter três barras invertidas (`\\\`) **(v2.9.7 - Fix Backslash Escaping)**
- **[X]** Evitar valores vazios no output do JSON Extractor **(v2.9.6)**
- **[X]** Incluir 'avoid childs keys with the same name' no output do JSON Extractor **(v2.9.7 - Avoid Duplicate Child Keys)**
- **[X]** Adicionar opção 'not include number keys' no JSON Extractor **(v2.9.6)**
- **[X]** Ordenar todos os resultados, incluindo output do JSON Rewriter **(v2.9.5 - Parcial: implementado para SearchReplacePanel e InsertPanel)**
- **[X]** Corrigir issue de case onde output tem chaves com pascal-case ou camel-case inconsistente **(v2.9.9 - Case Validator Dialog)**
- **[]** Corrigir situações problemáticas:
  ```javascript
  retelllecture: '\'RetellLecture\', \'Retell Lecture\', \'Re-tell Lecture\',',
  answershortquestion: ['\'AnswerShortQuestion\', \'Answer Short Question\','],
  respondtosituation: ['\'RespondToSituation\', \'Respond to a Situation\',']
  ```
- **[X]** Evitar chaves repetidas em arrays (remove duplicados consecutivos e totais) **(v2.9.8)**
  ```javascript
  whyItSWrong: ['Why it\'s wrong:', 'Why it\'s wrong:'] → ['Why it\'s wrong:']
  ```
- **[X]** Adicionar feature para substituir listas por objetos/dicionários em arquivos JSON com restrições de escopo (ex: apenas em `t.pages`) **(v2.9.10 - Task #21)**
- **[X]** Normalizar escaping excessivo automaticamente (detectar `\\\\'` ou mais → `\\'`) **(v2.9.10 - Task #22)**
- **[X]** Converter arrays para objetos com geração inteligente de chaves (camelCase, primeiras 30 chars, remove acentos) **(v2.9.10 - Task #21)**
- **[X]** Atualizar referências órfãs em arquivos do projeto após eliminação de duplicatas **(v2.9.10 - Task #23)**
- **[X]** Incluir possibilidade de filtrar extensões (ex: `.jsx`) em todos os módulos e funcionalidades *(v2.9.0 - Extension Filter)*;
- **[X]** Resolver issue de tradução quando texto tem parênteses (ex: `'Multiple Choice (Multiple)'`) **(v2.9.9 - Parentheses Support)**
- **[]** Evitar problema onde JSON Translate não substitui object keys de arquivos afetados ao remover keys do dicionário, causando omissão e erro 'undefined'
- **[X]** Forçar aplicação e JSON translate a obedecer regras de sintaxe e case (enforce consistent case) **(v2.9.8)**
- **[X]** Incluir whole word, case sensitive e regex nas condições avançadas *(v2.2.0 - Implementado em Search/Replace e Insert panels)*
- **[X]** Adicionar tipo de filtro nas condições avançadas: operadores AND e OR *(v2.6.0 - Dropdown com AND/OR em ambos panels)*
- **[]** Valor após chave em JSON é valor atômico, lista também é valor atômico. Ambos precisam ser iguais para ser eliminados ao remover redundâncias

#### System Features

- **[X]** Adicionar classe de modal screen para mostrar loading sem travar tela, permitindo minimizar/maximizar modal, continuar navegando e fazer processamento paralelo (com threads), mas sem permitir processar mesma feature simultaneamente *(v2.7.0 - ThreadManager + ProcessingModal)*
- **[]** Corrigir reversão de JSON translate (ChatGPT não resolveu): fazer reverso de tradução (texto para objeto) para texto do objeto, ou seja, se um arquivo está como {t.pages.home.features.title}, então deve ser buscado em qual parte do JSON está essa informação para depois reverter para o que estava antes, por exemplo, em um HTML ou react: "Lista de Tarefas", que era o título de antes.
- **[]** Adicionar feature para interromper processamento enquanto carrega resultados, ou seja, um botão para cancelar quaisquer tipo de processamentos, carregamentos e threads, por exemplo, de busca ou de tradução;
- **[]** Incluir possibilidade de listar arquivos com parâmetros ls/dir com ferramentas de busca avançadas;
- **[]** Inserção de arquivos e diretórios de forma assíncrona e selecionável, ou seja, se pode selecionar múltiplos arquivos e diretórios para uma mesma funcionalidade, por exemplo, de busca, em que os processamentos podem ser paralelos para cada arquivo com threads a cada processamento de uma mesma funcionalidade;
- **[X]** Incluir query para inteligência artificial sem arquivos/diretórios, apenas com texto do usuário *(v3.0.0 - AI File Processor)*
- **[X]** Identificar tags, chaves curvas, colchetes e parênteses para evitar erros no JSON Rewriter e uso de editor de texto ros ls/dir com ferramentas de busca avançadas
- **[X]** Incluir query para inteligência artificial sem arquivos/diretórios, apenas com texto do usuário *(v3.0.0 - AI File Processor)*
- **[X]** Identificar tags, chaves curvas, colchetes e parênteses para evitar erros no JSON Rewriter e uso de editor de texto *(v3.0.0 - Text Extractor)*
- **[X]** Incluir busca avançada onde usuário pode buscar com múltiplas queries separadas por novas linhas com possibilidade de usar regex (cada linha = nova query de busca) *(v2.8.0 - Multi-Query Search)*
- **[X]** Remover erros ` ```typescript` e ` ``` ` no output ao usar IA query *(v3.0.0 - AI File Processor com strip_code_fences)*
- **[X]** Incluir busca onde word key tem contagem de ocorrências (Top 5 files/keys, total count) **(v2.9.8)**
- **[X]** Interrupt Request no ChatGPT File Processor não funciona. Resolver issue *(v3.0.0 - AI File Processor com worker.request_interrupt())*

---

## 🟢 COULD HAVE (Prioridade Baixa)

### ✅ Tasks Concluídas

*(Nenhuma task nesta categoria foi concluída ainda)*

### 🔨 Tasks Pendentes

#### Editor Features

- **[]** Incluir habilidade de abrir e ler arquivos, diferenciar escopo com temas de cores diferentes
- **[]** Incluir editores JSON como abas
- **[]** Adicionar novo painel 'Smart file editing - AI' com o 'ChatGPT File Processor', ou seja, processamento de arquivos com inteligências artificiais;
- **[]** Incluir habilidade de conectar ao Google Translate e realizar operações de tradução online no programa por meio de API's;
- **[X]** Incluir Gemini na lista de IAs a serem usadas *(v3.0.0 - AI File Processor com suporte OpenAI e Gemini)*
- **[]** Adicionar opções avançadas condicionais também no painel Smart Edit File (AI)
- **[]** Incluir todas features de Search/Replace e Insert no Smart Edit File (AI) e editores JSON
- **[]** Possibilidade de mudanças feitas apenas no editor de texto do próprio Clarify, não mais em arquivos
- **[]** Adicionar feature onde resultado pode ser reutilizado no editor de texto do Clarify

#### JSON Advanced Features

- **[X]** Possibilidade de buscar chaves e valores JSON (ex: `t.auth.brandTitle`) *(v3.0.0 - JSON Search)*
- **[X]** Incluir 'is file' em outros lugares para pegar mais arquivos com caminhos de diretórios **(v2.9.6)**
- **[]** Adicionar feature para inserir novos chaves/valores em chaves existentes com regex e conceito de registrador de memória
- **[]** Incluir possibilidade de inserir novo valor em modo grupo, onde word keys podem ser usadas para inserir novo valor entre essas word keys, em linha separada ou coluna específica. Usuário pode entrar contagem de ocorrências tolerada (threshold)
- **[]** Adicionar possibilidade de reescrever JSON substituindo chave e objeto em outros lugares se valor da chave é mesmo e chaves têm diferentes
- **[]** Permitir usuário escolher className names ao invés de tag names para fazer chaves JSON. Usuário pode escolher pegar apenas diferença entre className names
- **[]** Adicionar parâmetro para não permitir chaves com hierarquia serial (sequência de chaves sem siblings). Com este parâmetro, apenas chaves com siblings são parte do output
- **[]** Quando usuário precisa reestruturar JSON e transformar texto em objeto JSON, aplicação deve permitir colar conteúdo de texto na GUI e então performar reestruturação
- **[]** Ao buscar outras chaves e objetos JSON (ex: `t.pages.contact.title` com word-key 'contact'), não apenas chaves devem ser encontradas, valores à direita das chaves também
- **[]** Incluir possibilidade de não permitir fazer chave que não tem sibling, ou remover chaves que não têm sibling key
- **[]** Ferramenta de busca pode incluir busca por nome de arquivo
- **[]** Para busca de arquivos/diretórios, ao invés de escrever ou buscar com ferramenta pobre, incluir possibilidade de buscar com condições avançadas tanto arquivos quanto diretórios (ex: com regex e estrutura de condições), incluindo simultaneamente. Muito útil para encontrar arquivos/diretórios com mais precisão

---

## 🔵 WOULD HAVE LATER (Longo Prazo / Futuro)

### ✅ Tasks Concluídas

*(Nenhuma task nesta categoria foi concluída ainda)*

### 🔨 Tasks Pendentes

#### UI/UX Improvements

- **[X]** Incluir botão 'clear all conditions' nas opções avançadas condicionais **(v2.9.5)**
- **[X]** Adicionar scroll nos painéis 'search/replace' e 'insert' **(v2.9.5)**
- **[X]** Incluir histórico de atividades como feature do Google Translate **(v2.9.6 - History Dock)**
- **[X]** Incluir possibilidade de adicionar nova linha de opções avançadas condicionais (mínimo 3, sem limite máximo) **(v2.9.7 - Dynamic Condition Lines)**
- **[X]** Fornecer habilidade de mudar aparência da aplicação para background transparente **(v2.9.9 - Transparency Slider)**
- **[X]** Mudar caixas de texto de insert, query e replacement para caixas redimensionáveis pelo usuário **(v2.9.6)**
- **[X]** Incluir tooltips na aplicação Clarify **(v2.9.3)**
- **[X]** Adicionar sistema de temas (Light, Dark, System) em toda a aplicação **(v2.9.4)**
- **[X]** Adicionar opções de undo e redo para mudanças feitas (Command Pattern, Ctrl+Z/Ctrl+Y, 10 níveis) **(v2.9.8)**
- **[X]** Traduzir aplicação para idiomas mais falados do mundo **(v2.9.10 - Task #24: Sistema i18n com EN/PT-BR)**

#### Advanced Features

- **[]** Além de fornecer tutoriais, modelos de uso de código, métodos Python disponíveis e código Python pronto para usuários que querem automatizar projetos no Clarify, aplicação pode aprender padrões de uso e apresentar ideias de algoritmos, passos ou instruções para completar tarefas repetitivas. Incluir programação em blocos
- **[]** Incluir tutoriais de uso
- **[]** Incluir busca com ajuda de inteligência artificial
- **[]** Embutir assistente virtual para uso com IAOnde mostrar a contagem?
Nova coluna "Count" na tabela de resultados do JSON Search?
Campo de texto embaixo dos resultados: "Total occurrences: 5"?
Contagem deve ser:
Por arquivo: en.json (3 occurrências), pt.json (2 ocorrências)
Total geral: 5 occurrências
Ambos?
- **[]** Pesquisar possibilidade de embutir Clarify no gerenciador de aplicativos Linux e quanto se ganha fazendo isso. Uma vez instalado, compilar código antes de enviar;
- **[]** Adicionar backup de dados do usuário para undo/redo com ECC, ou usar arquitetura de comando Gof
- **[]** Adicionar backup de dados com arquitetura de comando, com Egg Cell Compactor e IA para armazenar todas mudanças feitas pelo usuário mesmo por longo período
- **[]** Permitir usuário fazer macros e algoritmos com features da aplicação para utilidades mais complexas, com código Python ou programação em blocos
- **[]** Quando usuário clicar em resultado de busca ou insert, aplicação deve abrir arquivo em editor próprio
- **[]** Fazer Clarify capaz de criar algoritmos para performar tarefas do usuário, e não apenas isso, também compilar ou traduzir para linguagem de programação (Python, React, Javascript). Esses algoritmos 

#### Calculator & Set Operations

- **[]** Calculator: Adicionar conceitos de calculadora como registrador de memória, adição, concatenação e recall de memória padrão com histórico de modificações. A ideia seria a seguinte: o registro de memória seria o resultado do processamento, por exemplo, de busca, do painel de resultado de buscas. A adição significa: adicione um resultado de busca com outro resultado de forma que estes se complementem, por exemplo, em ordem alfabética ou unindo resultados de um mesmo arquivo (quando é em formato de árvore) no painel de resultados. Concatenação iria concatenar um resultado a outro, colocando o segundo resultado debaixo do primeiro no painel de resultados. O recall de memória iria chamar resultados salvos e jogar no painel de resultados, como pesquisas pela palavra "span".
- **[]** Set: Adicionar operações de conjunto lógico de arquivos JSON como interseção, diferença, união e diferença exclusiva. Incluir checkboxes para incluir chaves e/ou valores nesta operação de conjunto, em que, por exemplo, se for escolhida a intersecção entre arquivo A e arquivo B, ambos JSON, se tem valores equivalentes tanto em A quanto em B no sentido de chave e valor (title: "Tarefas de Casa"), no sentido de caminhos de chave e valor (t.pages.home.features.title, title: "Tarefas de Casa"), e somente no sentido de caminhos de chave (t.pages.home.features.title);

---

## 📝 Notas de Implementação

### Tarefas Críticas Completadas

#### ✅ JSON Rewriter Bug Fix (Completada)
**Problema**: Perda de dados ao processar tipo `Obj` (lista de tuplas chave-valor).

**Solução Aplicada**: 
- **Arquivo**: `rewriter/rewriter.py`
- **Função**: `sanitize_keys_and_values()`
- **Linhas**: ~40-55
- **Fix**: Adicionado suporte para tipo `Obj` ANTES do tratamento de `dict`

```python
def walk(v):
    if isinstance(v, Obj):  # ⭐ CRITICAL FIX
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
    # ... continua com dict e list
```

**Status**: ✅ Corrigido e validado em 23/11/2025

---

## 📊 Estatísticas

### Por Categoria

| Categoria | Total | Completas | Pendentes | % Completo |
|-----------|-------|-----------|-----------|------------|
| MUST HAVE | 12 | 11 | 1 | 91.7% |
| SHOULD HAVE | 46 | 32 | 14 | 69.6% |
| COULD HAVE | 18 | 0 | 18 | 0% |
| WOULD HAVE LATER | 24 | 12 | 12 | 50.0% |
| **TOTAL** | **100** | **55** | **45** | **55.0%** |

### Notas

- Este é um projeto ambicioso com roadmap de longo prazo
- Funcionalidades MUST HAVE essenciais praticamente completas (91.7%)
- **v2.9.9**: Melhorias em tradução, validação de case, ranges hierárquicos e transparência
- **v3.0.0**: Adicionadas 5 ferramentas profissionais (Case Converter, JSON Search, Text Extractor, Placeholder Replacer, AI File Processor)
- Projeto funcional e utilizável no estado atual com ferramentas avançadas
- 55% do projeto total completo - em progressão constante
- Categorias SHOULD/COULD/WOULD são melhorias e features avançadas

### Marcos Importantes

- **v3.0.0 (24/11/2025)**: +6 tasks completadas (SHOULD HAVE)
  - Case Converter integrado
  - JSON Search com suporte TS
  - Text Extractor HTML/JSX
  - Placeholder Replacer com scope filtering
  - AI File Processor (OpenAI + Gemini)
  - Interrupção de processamento IA

---

## 🔗 Referências

- **Repositório**: [github.com/JosueAmaral15/clarify](https://github.com/JosueAmaral15/clarify)
- **Documentação Principal**: `README.md`
- **Status de Migração**: `docs/MIGRATION_FINAL_STATUS.md`
- **Estrutura do Projeto**: `docs/project_structure.txt`

---

---

## 🎯 Marcos Recentes

- **v2.9.10 (30/11/2025)**: +4 tasks completadas (SHOULD HAVE + WOULD HAVE LATER) - **100% COMPLETO** ✅
  - ✅ Task #24: Sistema de internacionalização (i18n) com alternância runtime EN↔PT-BR
  - ✅ Task #22: Normalizar escaping excessivo automaticamente (`\\\\'` → `\\'`)
  - ✅ Task #21: Converter arrays para objetos com geração inteligente de chaves
  - ✅ Task #23: Atualizar referências órfãs após eliminação de duplicatas

- **v2.9.9 (29/11/2025)**: +6 tasks completadas (MUST HAVE + SHOULD HAVE + WOULD HAVE LATER)
  - ✅ Task #17: Validated dynamic condition lines (already complete in v2.9.7)
  - ✅ Task #15: Case inconsistency validator (before/after preview dialog, apply/cancel)
  - ✅ Task #14: Hierarchical include/exclude ranges (syntax: "include div#test1, exclude #test2")
  - ✅ Task #16: Parentheses in translation (treated as part of translatable text)
  - ✅ Task #13: Auto-consolidate fragmented placeholders (merge adjacent refs into single unit)
  - ✅ Task #18: Transparent background slider (0-100%, persistent settings)

- **v2.9.8 (28/11/2025)**: +6 tasks completadas (MUST HAVE + SHOULD HAVE + WOULD HAVE LATER)
  - ✅ Task #8: Remove duplicate array values (consecutive & all duplicates)
  - ✅ Task #9: Enforce consistent case (camelCase, PascalCase, snake_case, kebab-case)
  - ✅ Task #7: Preserve uppercase keys durante tradução JSON
  - ✅ Task #11: Occurrence count in JSON search (Top 5 files/keys, total)
  - ✅ Task #10: Reverse translation (Swap Dictionaries + Undo with Backup)
  - ✅ Task #12: Undo/Redo system (Command Pattern, Ctrl+Z/Y, 10 níveis)

- **v2.9.7 (28/11/2025)**: +6 tasks completadas (MUST HAVE + SHOULD HAVE)
  - ✅ Emit export const (backend integration)
  - ✅ Fix backslash escaping (esc_single normalization)
  - ✅ Avoid duplicate child keys (parent.child.child → parent.child)
  - ✅ Filename search (wildcards, prefix "filename:", regex)
  - ✅ Save results (single file, per file, per query)
  - ✅ Dynamic condition lines (Add/Remove buttons, min 3, no max)

- **v2.9.6 (28/11/2025)**: +5 tasks completadas (SHOULD HAVE + WOULD HAVE LATER)
  - ✅ Exclude numeric keys (Text Extractor + JSON Rewriter)
  - ✅ Skip empty values (Text Extractor + JSON Rewriter)
  - ✅ Resizable text boxes (ed_query, ed_repl, ed_text)
  - ✅ History Panel (View → History com 10 entradas)
  - ✅ "Is File" consistency em todos os módulos JSON

- **v2.9.5 (28/11/2025)**: +3 tasks completadas (UI/UX Improvements)
  - ✅ Clear All Conditions button
  - ✅ Scroll em painéis principais
  - ✅ Ordenação alfabética de resultados

---

**Última atualização**: 28 de Novembro de 2025  
**Mantido por**: Josué Amaral
