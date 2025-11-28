# Funcionalidade de Escopo em Condições Avançadas

**Data de Implementação**: 24 de Novembro de 2025  
**Versão**: 2.1  
**Status**: ✅ Implementado e Testado

---

## Visão Geral

A funcionalidade de **determinação de escopo** permite que você aplique condições de filtragem apenas ao conteúdo dentro de delimitadores específicos, ao invés de buscar no arquivo inteiro. Isso é extremamente útil para:

- Buscar apenas dentro de blocos de código específicos
- Filtrar conteúdo dentro de tags HTML/XML específicas
- Focar em seções delimitadas por marcadores customizados
- Analisar estruturas de dados aninhadas

---

## Como Usar

### Interface Gráfica

Nas **Advanced Conditions** dos painéis Search/Replace e Insert, você agora tem dois novos campos:

1. **Scope**: Dropdown com tipos de escopo disponíveis
2. **Scope Param**: Campo de texto para parâmetros adicionais (quando necessário)

### Tipos de Escopo Disponíveis

| Tipo de Escopo | Descrição | Requer Scope Param? | Exemplo |
|----------------|-----------|---------------------|---------|
| `none` | Sem escopo (padrão - busca no arquivo todo) | Não | - |
| `brackets` | Apenas entre colchetes `[...]` | Não | `[texto aqui]` |
| `braces` | Apenas entre chaves `{...}` | Não | `{texto aqui}` |
| `parentheses` | Apenas entre parênteses `(...)` | Não | `(texto aqui)` |
| `custom` | Entre delimitadores customizados | Sim | `begin,end` |
| `tag` | Dentro de qualquer tag HTML/XML | Não | `<any>texto</any>` |
| `specific-tag` | Dentro de uma tag específica | Sim | `div` para `<div>texto</div>` |

---

## Exemplos de Uso

### Exemplo 1: Buscar Apenas em Blocos JSON

**Cenário**: Você tem arquivos com comentários e blocos JSON, e quer buscar apenas dentro dos blocos JSON (entre chaves).

**Configuração**:
- Field: `content`
- Operator: `contains`
- Value: `"translation"`
- Scope: `braces`
- Scope Param: *(vazio)*

**Resultado**: Busca apenas dentro de `{...}` ignorando texto fora das chaves.

---

### Exemplo 2: Buscar Apenas em Tags Script

**Cenário**: Você quer encontrar arquivos HTML que contenham código específico apenas dentro de tags `<script>`.

**Configuração**:
- Field: `content`
- Operator: `contains`
- Value: `console.log`
- Scope: `specific-tag`
- Scope Param: `script`

**Resultado**: Busca apenas dentro de `<script>...</script>`, ignorando o resto do HTML.

---

### Exemplo 3: Delimitadores Customizados

**Cenário**: Você tem arquivos com seções delimitadas por `BEGIN` e `END`, e quer buscar apenas nessas seções.

**Configuração**:
- Field: `content`
- Operator: `contains`
- Value: `TODO`
- Scope: `custom`
- Scope Param: `BEGIN,END`

**Resultado**: Busca apenas entre `BEGIN` e `END`.

---

### Exemplo 4: Combinação com Outras Condições

Você pode combinar escopo com outras condições:

**Linha 1**:
- Field: `ext`
- Operator: `equals`
- Value: `tsx`

**Linha 2**:
- Field: `content`
- Operator: `contains`
- Value: `useState`
- Scope: `braces`

**Resultado**: Arquivos `.tsx` que contêm `useState` dentro de blocos `{...}`.

---

## Comportamento com Aninhamento

### Chaves e Parênteses Aninhados

A funcionalidade suporta aninhamento correto:

```javascript
{
  outer: {
    inner: "valor aninhado"
  }
}
```

**Comportamento**: Extrai todo o conteúdo do bloco externo, incluindo blocos internos.

### Colchetes

Para colchetes simples (não aninhados):

```javascript
[item1] texto [item2]
```

**Comportamento**: Extrai `item1` e `item2` separadamente.

---

## Implementação Técnica

### Arquivos Modificados

1. **`src/core/filters.py`**
   - Adicionada função `extract_scope_content()`
   - Classe `Condition` agora aceita `scope_type` e `scope_value`
   - Lógica de matching atualizada para aplicar filtro de escopo

2. **`src/app.py`**
   - Painéis `SearchReplacePanel` e `InsertPanel` atualizados
   - Adicionados campos de UI para Scope e Scope Param
   - Métodos `_conds()`, `enable_buttons()` e `reset_advanced_conditions()` atualizados

3. **`src/core/__init__.py`**
   - Exportação de `extract_scope_content` adicionada

### Função Principal

```python
def extract_scope_content(text: str, scope_type: str, scope_value: str = "") -> str:
    """
    Extract content within specified scope delimiters.
    
    Args:
        text: The full text to extract from
        scope_type: Type of scope ("brackets", "braces", "custom", "tag", "specific-tag", "" for no scope)
        scope_value: Additional value for custom delimiters or specific tag name
    
    Returns:
        Concatenated content within all matching scopes
    """
```

---

## Testes

Um conjunto completo de testes foi criado em `test_scope_feature.py`:

- ✅ Extração de conteúdo entre colchetes
- ✅ Extração de conteúdo entre chaves
- ✅ Extração de conteúdo entre parênteses
- ✅ Delimitadores customizados
- ✅ Tags HTML/XML genéricas
- ✅ Tags HTML/XML específicas
- ✅ Integração com classe `Condition`
- ✅ Aninhamento de chaves

**Status**: Todos os testes passando ✅

---

## Limitações Conhecidas

1. **Regex em Scope Param**: Atualmente, o campo Scope Param não suporta regex, apenas strings literais.

2. **Tags Auto-fechadas**: Tags HTML auto-fechadas (ex: `<img />`) não são consideradas no modo `tag` ou `specific-tag`.

3. **Performance**: Para arquivos muito grandes com muitos blocos aninhados, pode haver impacto de performance. Recomenda-se combinar com outras condições (extensão, tamanho) para otimizar.

---

## Casos de Uso Avançados

### 1. Refatoração de Código React

Buscar props específicos apenas dentro de JSX (entre chaves):

```
Field: content
Operator: contains
Value: onClick
Scope: braces
```

### 2. Análise de Logs

Buscar erros apenas em seções específicas de logs:

```
Field: content
Operator: contains
Value: ERROR
Scope: custom
Scope Param: [ERROR START],[ERROR END]
```

### 3. Extração de Dados de HTML

Buscar conteúdo apenas em divs com classe específica (use regex no value):

```
Field: content
Operator: contains
Value: <seu termo de busca>
Scope: specific-tag
Scope Param: div
```

---

## Roadmap Futuro

Possíveis melhorias futuras:

- [ ] Suporte a regex em Scope Param
- [ ] Escopo baseado em atributos HTML (ex: apenas dentro de `<div class="content">`)
- [ ] Múltiplos tipos de escopo simultâneos (ex: braces E brackets)
- [ ] Escopo negativo (tudo EXCETO dentro de delimitadores)
- [ ] Visualização de preview do conteúdo extraído antes de aplicar condição

---

## Suporte e Feedback

Para reportar bugs ou sugerir melhorias relacionadas a esta funcionalidade:

- **GitHub Issues**: [github.com/JosueAmaral15/clarify/issues](https://github.com/JosueAmaral15/clarify/issues)
- **Documentação**: `docs/pt/SCOPE_FEATURE.md` (este arquivo)

---

**Desenvolvido por**: GitHub Copilot (Claude Sonnet 4.5)  
**Data**: 24 de Novembro de 2025  
**Versão do Clarify**: 2.1
