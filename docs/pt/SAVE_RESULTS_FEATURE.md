# 💾 Funcionalidade de Salvamento de Resultados (v2.4.0)

## Visão Geral

A funcionalidade de salvamento de resultados permite que você exporte todos os resultados de busca ou correspondência para um arquivo de texto formatado. Esta funcionalidade está disponível tanto no painel de busca/substituição quanto no painel de inserção.

## Interface de Usuário

### Botão de Salvamento

Um novo botão **"💾 Save Results"** foi adicionado no cabeçalho da seção de resultados em ambos os painéis:

- **Painel de Busca/Substituição**: Localizado acima da árvore de "Search Results"
- **Painel de Inserção**: Localizado acima da árvore de "Match Results"

### Quando o Botão Está Disponível

O botão permanece sempre visível, mas só funciona quando há resultados para salvar. Se você clicar sem resultados, uma mensagem informativa aparecerá.

## Formato de Exportação

Os resultados são salvos em formato de texto simples (`.txt`) com a seguinte estrutura:

```
================================================================================
CLARIFY - SEARCH RESULTS
================================================================================
Total files with matches: 3
Total matches: 15
================================================================================

📁 /home/user/project/src/main.py
   Matches: 8
--------------------------------------------------------------------------------
   Line 10, Col 5:
      def calculate_total():
   Line 15, Col 8:
      return sum(values)
   Line 20, Col 4:
      result = calculate_total()
   ...

📁 /home/user/project/src/utils.py
   Matches: 5
--------------------------------------------------------------------------------
   Line 5, Col 0:
      import os
   Line 6, Col 0:
      import sys
   ...

📁 /home/user/project/tests/test_main.py
   Matches: 2
--------------------------------------------------------------------------------
   Line 12, Col 4:
      assert result == expected
   Line 18, Col 4:
      assert calculate_total() > 0
```

### Elementos do Formato

1. **Cabeçalho**: Inclui o título e estatísticas gerais
   - Nome do aplicativo (CLARIFY - SEARCH RESULTS)
   - Total de arquivos com correspondências
   - Total de correspondências encontradas

2. **Seção por Arquivo**: Para cada arquivo com correspondências
   - Caminho completo do arquivo com emoji 📁
   - Número de correspondências no arquivo
   - Linha separadora

3. **Detalhes de Correspondências**: Para cada correspondência
   - Número da linha e coluna
   - Trecho do código/texto onde a correspondência foi encontrada
   - Indentação preservada do código original

## Como Usar

### Passo a Passo

1. **Execute uma Busca ou Inserção**
   - No painel de Busca/Substituição: Configure sua busca e clique em "Search"
   - No painel de Inserção: Configure sua inserção e clique em "Insert"

2. **Visualize os Resultados**
   - Os resultados aparecerão na árvore de resultados
   - Verifique se as correspondências estão corretas

3. **Clique em "💾 Save Results"**
   - O botão está localizado no cabeçalho da seção de resultados
   - Se não houver resultados, uma mensagem informará isso

4. **Escolha o Local de Salvamento**
   - Uma caixa de diálogo de salvamento aparecerá
   - Navegue até o diretório desejado
   - Digite um nome para o arquivo (a extensão `.txt` será adicionada automaticamente)
   - Clique em "Save"

5. **Confirmação**
   - Uma mensagem de confirmação aparecerá indicando que os resultados foram salvos
   - O arquivo estará pronto para ser aberto ou compartilhado

### Exemplo de Uso

**Cenário**: Você quer documentar todas as ocorrências de uma função específica em seu projeto.

1. Abra o painel de Busca/Substituição
2. Configure:
   - **Search for**: `calculate_total`
   - **Scope**: `Entire File`
   - **Match Options**: Ative "Match Whole Word"
3. Clique em "Search"
4. Revise os resultados na árvore
5. Clique em "💾 Save Results"
6. Salve como: `calculate_total_occurrences.txt`
7. Abra o arquivo para revisar ou compartilhar com a equipe

## Casos de Uso

### 1. Documentação de Código

Exporte todas as ocorrências de uma função ou classe para criar documentação ou referências cruzadas.

### 2. Revisão de Código

Salve resultados de busca para revisar offline ou compartilhar com outros desenvolvedores.

### 3. Auditoria de Código

Documente padrões específicos encontrados no código para auditorias ou análises de qualidade.

### 4. Rastreamento de TODOs

Encontre e exporte todos os comentários TODO, FIXME ou similares para planejamento de sprints.

### 5. Análise de Dependências

Identifique e documente todas as importações ou dependências de módulos específicos.

### 6. Relatórios de Refatoração

Antes de refatorar, exporte todas as ocorrências do código antigo para rastrear mudanças.

## Características Técnicas

### Codificação

- Arquivos são salvos com codificação **UTF-8**
- Suporta caracteres especiais e Unicode
- Preserva formatação e indentação do código original

### Tamanho dos Arquivos

- Não há limite teórico para o número de correspondências
- Arquivos grandes podem levar alguns segundos para serem gerados
- O formato de texto simples mantém os arquivos relativamente pequenos

### Tratamento de Erros

- Verifica se há resultados antes de permitir o salvamento
- Trata erros de permissão de arquivo
- Informa o usuário sobre problemas de escrita

### Compatibilidade

- Funciona em Windows, macOS e Linux
- Arquivos `.txt` podem ser abertos em qualquer editor de texto
- Formato é compatível com ferramentas de análise de texto e diff

## Limitações

1. **Apenas Formato de Texto**
   - Atualmente, apenas exportação para `.txt` é suportada
   - Não há exportação para JSON, CSV ou outros formatos

2. **Sem Filtros de Exportação**
   - Todos os resultados são exportados
   - Não é possível filtrar quais arquivos ou correspondências incluir

3. **Sem Metadados Adicionais**
   - Não inclui data/hora da busca
   - Não inclui parâmetros de busca usados
   - Não inclui informações de versão do arquivo

## Versão

Funcionalidade introduzida na versão **2.4.0** do Clarify.

## Arquivos Modificados

- `src/app.py`:
  - Classe `ResultsTree`: Métodos `get_matches_data()` e `export_to_text()`
  - Classe `SearchReplacePanel`: Método `_save_results()`
  - Classe `InsertPanel`: Método `_save_results()`

## Testes

Veja `test_save_results_feature.py` para testes automatizados completos da funcionalidade.

## Feedback

Se você tiver sugestões para melhorias no formato de exportação ou funcionalidades adicionais, entre em contato com os desenvolvedores.
