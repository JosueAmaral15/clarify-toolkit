# Clarify Toolkit Project Icons

**Data**: 21 de Dezembro de 2025  
**Autor**: Josué Amaral  

## 🎨 Identidade Visual

Este documento descreve os ícones usados pelo **Clarify Toolkit** conforme especificado na **Etapa 8** do Protocolo Simplicidade 3.

## 📄 Conceito do Ícone

**Nome**: Clarify (clarificar/esclarecer)  
**Função**: Ferramenta para processamento, busca e transformação de dados JSON  

**Elementos Visuais**:
- 🔍 **Lupa**: Representa busca e análise de dados  
- 📊 **Chaves JSON {}**: Simboliza dados estruturados
- 🟣 **Gradiente Roxo**: Cores profissionais (Indigo #4F46E5 → Purple #7C3AED)
- ⚪ **Pontos de Dados**: Representam informações organizadas

## 📁 Arquivos Gerados

### Estrutura de Pastas
```
clarify/
├── assets/
│   └── icons/
│       ├── icon.svg          # Ícone vetorial principal (1.3 KB)
│       ├── icon.png          # Ícone principal 256x256 (18.9 KB)
│       ├── icon-32.png       # Ícone pequeno 32x32 (1.7 KB)
│       ├── icon-64.png       # Ícone médio 64x64 (3.9 KB)
│       ├── icon-128.png      # Ícone grande 128x128 (8.6 KB)
│       ├── icon-512.png      # Ícone extra-large 512x512 (41.1 KB)
│       └── favicon.ico       # Ícone Windows multi-size (769 bytes)
└── generate_icons.py         # Script de geração
```

### Especificações Técnicas

| Arquivo | Formato | Tamanho | Uso |
|---------|---------|---------|-----|
| `icon.svg` | SVG Vetorial | 100x100 viewBox | Escalável, navegadores modernos |
| `icon.png` | PNG 256x256 | 18.9 KB | Linux desktop, aplicação principal |
| `icon-32.png` | PNG 32x32 | 1.7 KB | Barra de tarefas, menus |
| `icon-64.png` | PNG 64x64 | 3.9 KB | Janelas pequenas |
| `icon-128.png` | PNG 128x128 | 8.6 KB | Dock, listas de apps |
| `icon-512.png` | PNG 512x512 | 41.1 KB | Alta resolução, splash |
| `favicon.ico` | ICO multi-size | 769 bytes | Windows, navegadores |

## 🔧 Integração no Código

### PySide6 (Aplicação Principal)
```python
# Em src/app.py - método _build_icon()
from pathlib import Path

icon_path = Path(__file__).parent.parent / "assets" / "icons" / "icon.svg"
if icon_path.exists():
    icon = QIcon(str(icon_path))
    self.setWindowIcon(icon)
```

### Fallback para PNG
```python
icon_path = Path(__file__).parent.parent / "assets" / "icons" / "icon.png"
if icon_path.exists():
    icon = QIcon(str(icon_path))
    self.setWindowIcon(icon)
```

## 📋 Checklist de Implementação

- [x] ✅ **Pasta de assets criada**: `assets/icons/`
- [x] ✅ **Ícone SVG vetorial**: Profissional com identidade clara
- [x] ✅ **Múltiplos formatos PNG**: 32, 64, 128, 256, 512px
- [x] ✅ **Ícone ICO para Windows**: Multi-size (16, 32, 48, 64px)
- [x] ✅ **Integração no código**: Método `_build_icon()` atualizado
- [x] ✅ **Script de geração**: `generate_icons.py` para automação
- [x] ✅ **Documentação**: Este arquivo README

## 🎯 Uso dos Ícones por Plataforma

### 🐧 Linux Desktop
- **Principal**: `icon.png` (256x256)
- **Barra tarefas**: `icon-32.png`
- **Alt+Tab**: `icon-64.png`
- **Aplicativos**: `icon-128.png`

### 🪟 Windows Desktop  
- **Principal**: `favicon.ico` (multi-size)
- **Fallback**: `icon.png`

### 🍎 macOS (futuro)
- Converter para: `icon.icns`

### 🌐 Web (futuro)
- **Favicon**: `favicon.ico`
- **PWA**: `icon-192.png`, `icon-512.png`

## ⚙️ Regenerar Ícones

Para modificar ou regenerar os ícones:

```bash
# 1. Editar icon.svg
nano assets/icons/icon.svg

# 2. Executar script de geração
python generate_icons.py

# 3. Verificar saída
ls -la assets/icons/
```

## 📝 Créditos

- **Design**: Conceito próprio baseado na funcionalidade do app
- **Ferramentas**: SVG manual + Python (Pillow + cairosvg)
- **Licença**: Mesma do projeto Clarify
- **Protocolo**: Simplicidade 3 - Etapa 8 (Ícones Obrigatórios)

---

**Status**: 🟢 **Completo** - Etapa 8 finalizada conforme Protocolo Simplicidade 3
