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
- **[]** Durante tradução JSON, preservar uppercase com parâmetro do usuário

---

## 🟡 SHOULD HAVE (Prioridade Média)

### ✅ Tasks Concluídas

- **[x]** Incluir 3 opções de checkbox nas opções avançadas condicionais: case sensitive, match whole word e regular expression *(v2.2.0)*
- **[x]** Incluir possibilidade de busca e lookup de caracteres no painel Insert para inserir caracteres com busca ao invés de somente definir número da linha, estaticamente *(v2.3.0)*
- **[x]** Incluir salvamento de todos os resultados do match panel como arquivo txt *(v2.4.0)*
- **[x]** Incluir barra de progresso para mostrar progresso do processamento *(v2.5.0)*

### 🔨 Tasks Pendentes

#### Interface e Usabilidade
- **[]** Adicionar funcionalidade de reversão de tradução JSON
- **[X]** Adicionar menu com botão direito no painel de matches: copy, copy all, select all, open file, open all files. Suportar CTRL/Shift para seleção múltipla *(v2.9.2 - Context Menu)*
- **[]** Possibilidade de colocar resultados em arquivos separados (cada iteração) ou em arquivo único
- **[]** Habilidade de inserir ranges incluídos/excluídos no Insert, mesmo usando regex
- **[X]** Corrigir mensagem de Loading (só aparece letra L)
- **[X]** Mostrar quantidade de resultados na primeira linha do match panel
- **[X]** Mostrar posição absoluta do caractere/palavra ao passar mouse sobre resultado no match panel

#### JSON Features

- **[X]** Incluir possibilidade de mudar case de palavras-chave (camelCase, PascalCase, snake_case, kebab-case) *(v3.0.0 - Case Converter)*
- **[]** Incluir possibilidade de remover certa sub-estrutura JSON de uma estrutura maior
- **[X]** Incluir checkbox "is file" no JSON translate
- **[]** Ajustar opção 'Emit Export default' do JSON Translate
- **[]** Resultado do JSON Translate não deve conter três barras invertidas (`\\\`)
- **[]** Evitar valores vazios no output do JSON Extractor
- **[]** Incluir 'avoid childs keys with the same name' no output do JSON Extractor
- **[]** Adicionar opção 'not include number keys' no JSON Extractor
- **[]** Ordenar todos os resultados, incluindo output do JSON Rewriter
- **[]** Corrigir issue de case onde output tem chaves com pascal-case ou camel-case inconsistente
- **[]** Corrigir situações problemáticas:
  ```javascript
  retelllecture: '\'RetellLecture\', \'Retell Lecture\', \'Re-tell Lecture\',',
  answershortquestion: ['\'AnswerShortQuestion\', \'Answer Short Question\','],
  respondtosituation: ['\'RespondToSituation\', \'Respond to a Situation\',']
  ```
- **[]** Evitar chaves repetidas:
  ```javascript
  whyItSWrong: ['Why it\'s wrong:', 'Why it\'s wrong:']
  ```
- **[]** Adicionar feature para substituir listas por objetos/dicionários em arquivos JSON com restrições de escopo (ex: apenas em `t.pages`)
- **[X]** Incluir possibilidade de filtrar extensões (ex: `.jsx`) em todos os módulos e funcionalidades *(v2.9.0 - Extension Filter)*;
- **[]** Resolver issue de tradução quando texto tem parênteses (ex: `'Multiple Choice (Multiple)'`)
- **[]** Evitar problema onde JSON Translate não substitui object keys de arquivos afetados ao remover keys do dicionário, causando omissão e erro 'undefined'
- **[]** Forçar aplicação e JSON translate a obedecer regras de sintaxe e case
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
- **[X]** Identificar tags, curly brackets {}, colchetes [] e parênteses () para evitar erros no JSON Rewriter e uso de editor de texto
- **[X]** Incluir query para inteligência artificial sem arquivos/diretórios, apenas com texto do usuário *(v3.0.0 - AI File Processor)*
- **[X]** Identificar tags, curly brackets {}, colchetes [] e parênteses () para evitar erros no JSON Rewriter e uso de editor de texto *(v3.0.0 - Text Extractor)*
- **[X]** Incluir busca avançada onde usuário pode buscar com múltiplas queries separadas por novas linhas com possibilidade de usar regex (cada linha = nova query de busca) *(v2.8.0 - Multi-Query Search)*
- **[X]** Remover erros ` ```typescript` e ` ``` ` no output ao usar IA query *(v3.0.0 - AI File Processor com strip_code_fences)*
- **[]** Incluir busca onde word key tem contagem de ocorrências (ex: apenas chaves com mais de 2 ocorrências). Usar operações relacionais;
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
- **[X]** Incluir todas features de Search/Replace e Insert no Smart Edit File (AI) e editores JSON (v2.9.110)
- **[]** Possibilidade de mudanças feitas apenas no editor de texto do próprio Clarify, não mais em arquivos
- **[]** Adicionar feature onde resultado pode ser reutilizado no editor de texto do Clarify

#### JSON Advanced Features

- **[X]** Possibilidade de buscar chaves e valores JSON (ex: `t.auth.brandTitle`) *(v3.0.0 - JSON Search)*
- **[]** Incluir 'is file' em outros lugares para pegar mais arquivos com caminhos de diretórios
- **[]** Adicionar feature para inserir novos chaves/valores em chaves existentes com regex e conceito de registrador de memória
- **[]** Incluir possibilidade de inserir novo valor em modo grupo, onde word keys podem ser usadas para inserir novo valor entre essas word keys, em linha separada ou coluna específica. Usuário pode entrar contagem de ocorrências tolerada (threshold)
- **[]** Adicionar possibilidade de reescrever JSON substituindo chave e objeto em outros lugares se valor da chave é mesmo e chaves têm diferentes
- **[]** Permitir usuário escolher className names ao invés de tag names para fazer chaves JSON. Usuário pode escolher pegar apenas diferença entre className names
- **[]** Adicionar parâmetro para não permitir chaves com hierarquia serial (sequência de chaves sem siblings). Com este parâmetro, apenas chaves com siblings são parte do output
- **[]** Quando usuário precisa reestruturar JSON e transformar texto em objeto JSON, aplicação deve permitir colar conteúdo de texto na GUI e então performar reestruturação
- **[]** Ao buscar outras chaves e objetos JSON (ex: `t.pages.contact.title` com word-key 'contact'), não apenas chaves devem ser encontradas, valores à direita das chaves também
- **[]** Incluir possibilidade de não permitir fazer chave que não tem sibling, ou remover chaves que não têm sibling key
- **[]** Ferramenta de busca pode incluir busca por nome de arquivo
- **[]** Para busca de arquivos/diretórios, ao invés de usar ferramenta básica, incluir possibilidade de buscar com condições avançadas tanto arquivos quanto diretórios (ex: com regex e estrutura de condições), incluindo simultaneamente. Muito útil para encontrar arquivos/diretórios com mais precisão

---

## 🔵 WOULD HAVE LATER (Longo Prazo / Futuro)

### ✅ Tasks Concluídas

*(Nenhuma task nesta categoria foi concluída ainda)*

### 🔨 Tasks Pendentes

#### UI/UX Improvements

- **[]** Incluir botão 'clear all conditions' nas opções avançadas condicionais
- **[]** Adicionar scroll nos painéis 'search/replace' e 'insert'
- **[]** Incluir histórico de atividades como feature do Google Translate
- **[]** Incluir possibilidade de adicionar nova linha de opções avançadas condicionais (mínimo 3, sem limite máximo)
- **[]** Fornecer habilidade de mudar aparência da aplicação para background transparente
- **[]** Mudar caixas de texto de insert, query e replacement para caixas redimensionáveis pelo usuário
- **[X]** Incluir tooltips na aplicação Clarify **(v2.9.3)**
- **[]** Adicionar opções de undo e redo para mudanças feitas
- **[]** Traduzir aplicação para idiomas mais falados do mundo

#### Advanced Features

- **[]** Além de fornecer tutoriais, modelos de uso de código, métodos Python disponíveis e código Python pronto para usuários que querem automatizar projetos no Clarify, aplicação pode aprender padrões de uso e apresentar ideias de algoritmos, passos ou instruções para completar tarefas repetitivas. Incluir programação em blocos
- **[]** Incluir tutoriais de uso
- **[]** Incluir busca com ajuda de inteligência artificial
- **[]** Embutir assistente virtual para uso com IA
- **[]** Incluir taxa de uso de IA de 50% a mais que valor real para minha conta + 1% para permanecer na reserva de caixa, usuário deve fazer pagamento usando IA, totalizando ~151% do valor real. Informar usuário que paga em tokens
- **[]** Pesquisar possibilidade de embutir Clarify no gerenciador de aplicativos Linux e quanto se ganha fazendo isso. Uma vez instalado, compilar código antes de enviar;
- **[]** Adicionar backup de dados do usuário para undo/redo com ECC, ou usar arquitetura de comando Gof
- **[]** Adicionar backup de dados com arquitetura de comando, com Egg Cell Compactor e IA para armazenar todas mudanças feitas pelo usuário mesmo por longo período
- **[]** Permitir usuário fazer macros e algoritmos com features da aplicação para utilidades mais complexas, com código Python ou programação em blocos
- **[]** Quando usuário clicar em resultado de busca ou insert, aplicação deve abrir arquivo em editor próprio
- **[]** Fazer Clarify capaz de criar algoritmos para performar tarefas do usuário, e não apenas isso, também compilar ou traduzir para linguagem de programação (Python, React, Javascript)

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
| MUST HAVE | 12 | 10 | 2 | 83.3% |
| SHOULD HAVE | 46 | 18 | 28 | 39.1% |
| COULD HAVE | 18 | 0 | 18 | 0% |
| WOULD HAVE LATER | 21 | 0 | 21 | 0% |
| **TOTAL** | **97** | **28** | **69** | **28.9%** |

### Notas

- Este é um projeto ambicioso com roadmap de longo prazo
- Funcionalidades MUST HAVE essenciais já implementadas (83.3%)
- **v3.0.0**: Adicionadas 5 ferramentas profissionais (Case Converter, JSON Search, Text Extractor, Placeholder Replacer, AI File Processor)
- Projeto funcional e utilizável no estado atual com ferramentas avançadas
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

**Última atualização**: 28 de Novembro de 2025  
**Mantido por**: Josué Amaral
