#!/usr/bin/env python3
"""
Testes de inicialização dos docks modulares.
Verifica se todos os docks podem ser instanciados corretamente.
"""

import sys
import os
from pathlib import Path

# Adiciona raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

def test_imports():
    """Teste 1: Verificar se todos os imports funcionam."""
    print("=" * 60)
    print("TESTE 1: Verificação de Imports")
    print("=" * 60)
    
    errors = []
    
    # Teste base_dock
    try:
        from gui.base_dock import (
            BaseDock, StandardToolDock, ProcessorWorkerBase,
            FileInputMixin, ResultsOutputMixin, ActionButtonsMixin,
            OptionsGroupMixin, ValidationMixin
        )
        print("✓ base_dock imports OK")
    except Exception as e:
        errors.append(f"✗ base_dock: {e}")
        print(f"✗ base_dock: {e}")
    
    # Teste case_converter_dock
    try:
        from gui.case_converter_dock import CaseConverterDock
        print("✓ CaseConverterDock import OK")
    except Exception as e:
        errors.append(f"✗ CaseConverterDock: {e}")
        print(f"✗ CaseConverterDock: {e}")
    
    # Teste placeholder_replacer_dock
    try:
        from gui.placeholder_replacer_dock import PlaceholderReplacerDock
        print("✓ PlaceholderReplacerDock import OK")
    except Exception as e:
        errors.append(f"✗ PlaceholderReplacerDock: {e}")
        print(f"✗ PlaceholderReplacerDock: {e}")
    
    # Teste json_search_dock
    try:
        from gui.json_search_dock import JsonSearchDock
        print("✓ JsonSearchDock import OK")
    except Exception as e:
        errors.append(f"✗ JsonSearchDock: {e}")
        print(f"✗ JsonSearchDock: {e}")
    
    # Teste text_extractor_dock
    try:
        from gui.text_extractor_dock import TextExtractorDock
        print("✓ TextExtractorDock import OK")
    except Exception as e:
        errors.append(f"✗ TextExtractorDock: {e}")
        print(f"✗ TextExtractorDock: {e}")
    
    # Teste ai_processor_dock
    try:
        from gui.ai_processor_dock import AIProcessorDock
        print("✓ AIProcessorDock import OK")
    except Exception as e:
        errors.append(f"✗ AIProcessorDock: {e}")
        print(f"✗ AIProcessorDock: {e}")
    
    # Teste json_translate_dock
    try:
        from gui.json_translate_dock import JsonTranslateDock
        print("✓ JsonTranslateDock import OK")
    except Exception as e:
        errors.append(f"✗ JsonTranslateDock: {e}")
        print(f"✗ JsonTranslateDock: {e}")
    
    # Teste json_rewriter_dock
    try:
        from gui.json_rewriter_dock import JsonRewriterDock
        print("✓ JsonRewriterDock import OK")
    except Exception as e:
        errors.append(f"✗ JsonRewriterDock: {e}")
        print(f"✗ JsonRewriterDock: {e}")
    
    print()
    if errors:
        print(f"❌ TESTE 1 FALHOU: {len(errors)} erro(s)")
        return False
    else:
        print("✅ TESTE 1 PASSOU: Todos os imports funcionam")
        return True


def test_instantiation():
    """Teste 2: Verificar se todos os docks podem ser instanciados."""
    print("\n" + "=" * 60)
    print("TESTE 2: Verificação de Instanciação")
    print("=" * 60)
    
    from PySide6.QtWidgets import QApplication
    
    # Criar QApplication necessário para widgets
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    errors = []
    
    # Teste CaseConverterDock
    try:
        from gui.case_converter_dock import CaseConverterDock
        dock = CaseConverterDock(None)
        assert dock is not None
        assert hasattr(dock, 'input_line')
        assert hasattr(dock, 'process_btn')
        print("✓ CaseConverterDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ CaseConverterDock: {e}")
        print(f"✗ CaseConverterDock: {e}")
    
    # Teste PlaceholderReplacerDock
    try:
        from gui.placeholder_replacer_dock import PlaceholderReplacerDock
        dock = PlaceholderReplacerDock(None)
        assert dock is not None
        assert hasattr(dock, 'input_line')
        assert hasattr(dock, 'process_btn')
        print("✓ PlaceholderReplacerDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ PlaceholderReplacerDock: {e}")
        print(f"✗ PlaceholderReplacerDock: {e}")
    
    # Teste JsonSearchDock
    try:
        from gui.json_search_dock import JsonSearchDock
        dock = JsonSearchDock(None)
        assert dock is not None
        assert hasattr(dock, 'input_line')
        assert hasattr(dock, 'process_btn')
        print("✓ JsonSearchDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ JsonSearchDock: {e}")
        print(f"✗ JsonSearchDock: {e}")
    
    # Teste TextExtractorDock
    try:
        from gui.text_extractor_dock import TextExtractorDock
        dock = TextExtractorDock(None)
        assert dock is not None
        assert hasattr(dock, 'input_line')
        assert hasattr(dock, 'process_btn')
        print("✓ TextExtractorDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ TextExtractorDock: {e}")
        print(f"✗ TextExtractorDock: {e}")
    
    # Teste AIProcessorDock
    try:
        from gui.ai_processor_dock import AIProcessorDock
        dock = AIProcessorDock(None)
        assert dock is not None
        assert hasattr(dock, 'input_line')
        assert hasattr(dock, 'process_btn')
        print("✓ AIProcessorDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ AIProcessorDock: {e}")
        print(f"✗ AIProcessorDock: {e}")
    
    # Teste JsonTranslateDock
    try:
        from gui.json_translate_dock import JsonTranslateDock
        dock = JsonTranslateDock(None)
        assert dock is not None
        # Verifica se widgets foram criados
        assert hasattr(dock, 'line_input')
        print("✓ JsonTranslateDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ JsonTranslateDock: {e}")
        print(f"✗ JsonTranslateDock: {e}")
    
    # Teste JsonRewriterDock
    try:
        from gui.json_rewriter_dock import JsonRewriterDock
        dock = JsonRewriterDock(None)
        assert dock is not None
        assert hasattr(dock, 'line_input')
        print("✓ JsonRewriterDock instanciado OK")
    except Exception as e:
        errors.append(f"✗ JsonRewriterDock: {e}")
        print(f"✗ JsonRewriterDock: {e}")
    
    print()
    if errors:
        print(f"❌ TESTE 2 FALHOU: {len(errors)} erro(s)")
        return False
    else:
        print("✅ TESTE 2 PASSOU: Todos os docks podem ser instanciados")
        return True


def test_inheritance():
    """Teste 3: Verificar hierarquia de herança."""
    print("\n" + "=" * 60)
    print("TESTE 3: Verificação de Hierarquia")
    print("=" * 60)
    
    from PySide6.QtWidgets import QApplication, QDockWidget
    from gui.base_dock import BaseDock, StandardToolDock
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    errors = []
    
    # Verificar herança de BaseDock
    tests = [
        ('CaseConverterDock', 'gui.case_converter_dock', 'CaseConverterDock'),
        ('PlaceholderReplacerDock', 'gui.placeholder_replacer_dock', 'PlaceholderReplacerDock'),
        ('JsonSearchDock', 'gui.json_search_dock', 'JsonSearchDock'),
        ('TextExtractorDock', 'gui.text_extractor_dock', 'TextExtractorDock'),
        ('AIProcessorDock', 'gui.ai_processor_dock', 'AIProcessorDock'),
        ('JsonTranslateDock', 'gui.json_translate_dock', 'JsonTranslateDock'),
        ('JsonRewriterDock', 'gui.json_rewriter_dock', 'JsonRewriterDock'),
    ]
    
    for name, module, cls_name in tests:
        try:
            mod = __import__(module, fromlist=[cls_name])
            cls = getattr(mod, cls_name)
            dock = cls(None)
            
            # Verifica se herda de QDockWidget
            if not isinstance(dock, QDockWidget):
                errors.append(f"✗ {name}: Não herda de QDockWidget")
                print(f"✗ {name}: Não herda de QDockWidget")
            # Verifica se herda de BaseDock
            elif not isinstance(dock, BaseDock):
                errors.append(f"✗ {name}: Não herda de BaseDock")
                print(f"✗ {name}: Não herda de BaseDock")
            else:
                print(f"✓ {name}: Hierarquia OK (QDockWidget > BaseDock)")
        except Exception as e:
            errors.append(f"✗ {name}: {e}")
            print(f"✗ {name}: {e}")
    
    print()
    if errors:
        print(f"❌ TESTE 3 FALHOU: {len(errors)} erro(s)")
        return False
    else:
        print("✅ TESTE 3 PASSOU: Hierarquia correta")
        return True


def test_required_methods():
    """Teste 4: Verificar se métodos essenciais existem."""
    print("\n" + "=" * 60)
    print("TESTE 4: Verificação de Métodos Essenciais")
    print("=" * 60)
    
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    errors = []
    required_methods = ['_setup_ui', '_connect_signals']
    
    tests = [
        ('CaseConverterDock', 'gui.case_converter_dock', 'CaseConverterDock'),
        ('PlaceholderReplacerDock', 'gui.placeholder_replacer_dock', 'PlaceholderReplacerDock'),
        ('JsonSearchDock', 'gui.json_search_dock', 'JsonSearchDock'),
        ('TextExtractorDock', 'gui.text_extractor_dock', 'TextExtractorDock'),
        ('AIProcessorDock', 'gui.ai_processor_dock', 'AIProcessorDock'),
        ('JsonTranslateDock', 'gui.json_translate_dock', 'JsonTranslateDock'),
        ('JsonRewriterDock', 'gui.json_rewriter_dock', 'JsonRewriterDock'),
    ]
    
    for name, module, cls_name in tests:
        try:
            mod = __import__(module, fromlist=[cls_name])
            cls = getattr(mod, cls_name)
            dock = cls(None)
            
            missing = []
            for method in required_methods:
                if not hasattr(dock, method):
                    missing.append(method)
            
            if missing:
                errors.append(f"✗ {name}: Faltam métodos {missing}")
                print(f"✗ {name}: Faltam métodos {missing}")
            else:
                print(f"✓ {name}: Todos os métodos essenciais presentes")
        except Exception as e:
            errors.append(f"✗ {name}: {e}")
            print(f"✗ {name}: {e}")
    
    print()
    if errors:
        print(f"❌ TESTE 4 FALHOU: {len(errors)} erro(s)")
        return False
    else:
        print("✅ TESTE 4 PASSOU: Todos os métodos essenciais presentes")
        return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SUITE DE TESTES DE INICIALIZAÇÃO DOS DOCKS")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Instanciação", test_instantiation()))
    results.append(("Hierarquia", test_inheritance()))
    results.append(("Métodos Essenciais", test_required_methods()))
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL: {passed}/{total} testes passaram")
    print("=" * 60)
    
    sys.exit(0 if all(p for _, p in results) else 1)
