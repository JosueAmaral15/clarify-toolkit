# Funcionalidade de Tooltip de Posição (v2.5.1)

## Visão Geral

A funcionalidade de tooltip de posição fornece informações detalhadas sobre a linha e coluna de resultados de busca/matches ao passar o mouse sobre itens no painel de resultados.

## Funcionalidades

### 1. Tooltip ao Passar o Mouse
Quando você passa o mouse sobre qualquer resultado de match, um tooltip aparece mostrando:
- **Caminho do arquivo**: Caminho completo até o arquivo
- **Número da linha**: Linha onde o match foi encontrado
- **Número da coluna**: Posição da coluna onde o match começa

Exemplo de tooltip:
```
File: /home/user/project/src/main.py
Line: 42
Column: 15
```

### 2. Barra de Status
Uma barra de status na parte inferior do painel de resultados atualiza continuamente para mostrar as informações de posição do item atualmente sob o cursor do mouse.

Formato: `📍 Position: Line X, Column Y | File: [caminho]`

Exemplo:
```
📍 Position: Line 42, Column 15 | File: /home/user/project/src/main.py
```

## Layout Visual

```
┌─────────────────────────────────────────────────────────────┐
│  Search Results                              [💾 Save]      │
├─────────────────────────────────────────────────────────────┤
│  📊 Results: 45 matches in 12 file(s)                       │
│  ├─ /path/to/file1.py                                       │
│  │  ├─ 10:5  def test_function():          ← Passe aqui    │
│  │  └─ 25:10    return test_value                           │
│  ├─ /path/to/file2.py                                       │
│  │  ├─ 5:0  import test_module                              │
│  │  └─ 15:8  test_var = 42                                  │
│  ...                                                         │
├─────────────────────────────────────────────────────────────┤
│  📍 Position: Line 10, Column 5 | File: /path/to/file1.py  │ ← Barra status
└─────────────────────────────────────────────────────────────┘
```

## Como Funciona

### Detalhes de Implementação

1. **Rastreamento do Mouse**: 
   - `ResultsTree` tem rastreamento de mouse habilitado
   - Sinal `itemEntered` conectado ao método `_on_item_hover`

2. **Extração de Posição**:
   - Itens de resultado armazenam posição como "linha:coluna" no início
   - Formato: `"10:5  trecho de código..."`
   - Parser extrai linha e coluna deste formato

3. **Geração de Tooltip**:
   - Ao passar o mouse sobre um item de match (filho do item de arquivo)
   - Extrai posição do texto do item
   - Obtém caminho do arquivo do item pai
   - Cria tooltip multilinha com todas as informações

4. **Atualização da Barra de Status**:
   - Widget de label de status passado para `ResultsTree` via `set_status_label()`
   - Atualizado continuamente conforme o mouse se move
   - Limpo quando não está sobre itens de match

## Benefícios

1. **Sem Necessidade de Abrir Arquivo**: Veja a posição exata sem abrir o arquivo
2. **Referência Rápida**: Saiba instantaneamente linha e coluna para navegação
3. **Amigável para Copiar-Colar**: Pode copiar informações de posição do tooltip
4. **Feedback Visual**: Barra de status fornece atualizações contínuas de posição
5. **Não Intrusivo**: Aparece apenas ao passar o mouse, não sobrecarrega a UI

## Casos de Uso

### 1. Verificação Rápida de Posição
Passe o mouse sobre um match para ver onde ele está sem abrir o arquivo.

### 2. Navegação Manual
Copie a informação linha:coluna para navegar manualmente em seu editor.

### 3. Revisão de Código
Veja rapidamente posições de todos os matches para fins de revisão de código.

### 4. Análise de Múltiplos Matches
Compare posições de múltiplos matches para entender a estrutura do código.

### 5. Documentação
Referencie posições exatas ao documentar mudanças no código.

## Detalhes Técnicos

### Arquivos Modificados
- `src/app.py`:
  - `ResultsTree.__init__()`: Adicionado rastreamento de mouse e conexão de sinal
  - `ResultsTree._on_item_hover()`: Novo método para lidar com eventos de hover
  - `ResultsTree.set_status_label()`: Novo método para conectar label de status
  - `SearchReplacePanel.__init__()`: Adicionado widget de label de status
  - `InsertPanel.__init__()`: Adicionado widget de label de status

### Dependências
- Usa sinal `QTreeWidget.itemEntered` embutido do Qt
- Nenhuma dependência externa necessária

### Performance
- Overhead mínimo: Apenas analisa texto ao passar o mouse
- Sem impacto na performance de busca/match
- Parsing de string eficiente (split e extract)

## Configuração

Atualmente, a funcionalidade está sempre habilitada sem opções de configuração. Melhorias futuras poderiam incluir:
- Opção para desabilitar tooltips
- Formato de barra de status customizável
- Opções de formato de posição (base-0 vs base-1)

## Compatibilidade

Funciona com:
- ✅ Painel Search/Replace
- ✅ Painel Insert
- ✅ Todos os tipos de arquivo
- ✅ Buscas regex e texto simples
- ✅ Todos os sistemas operacionais (Linux, Windows, macOS)

## Histórico de Versões

- **v2.5.1**: Implementação inicial
  - Tooltip ao passar o mouse
  - Barra de status na parte inferior do painel de resultados
  - Funciona em ambos os painéis Search/Replace e Insert

## Testes

Suíte de testes abrangente em `test_position_tooltip.py`:
- Extração de posição do texto
- Formatação de tooltip
- Formatação de barra de status
- Casos edge (0:0, números grandes)
- Tratamento de formato inválido
- Caminhos de arquivo longos

Todos os testes passando ✓
