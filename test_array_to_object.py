#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for array_to_object_conversion() function (Task #21 - v2.9.10)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rewriter import Obj, array_to_object_conversion, dump_ts_obj

def test_array_to_object():
    """Test array to object conversion."""
    print("=" * 60)
    print("Testing array_to_object_conversion() (Task #21 - v2.9.10)")
    print("=" * 60)
    
    # Test 1: Simple string array
    print("\n1. Simple string array:")
    test1 = Obj([
        ("messages", [
            "O usuario pode seguir outros usuarios",
            "Clique em OK para continuar",
            "Seu perfil foi atualizado com sucesso"
        ])
    ])
    result1 = array_to_object_conversion(test1)
    print("   ANTES:")
    print("   ", test1[0][1])
    print("\n   DEPOIS:")
    for k, v in result1[0][1]:
        print(f"     {k}: {v}")
    
    # Test 2: Array with accents and special characters
    print("\n2. Array with accents and special characters:")
    test2 = Obj([
        ("errors", [
            "Não é possível acessar esta página!",
            "Você não tem permissão (acesso negado)",
            "E-mail já está cadastrado no sistema"
        ])
    ])
    result2 = array_to_object_conversion(test2)
    print("   DEPOIS:")
    for k, v in result2[0][1]:
        print(f"     {k}: {v}")
    
    # Test 3: Conflicting keys (same start)
    print("\n3. Conflicting keys (same start):")
    test3 = Obj([
        ("items", [
            "Click here to start",
            "Click here to continue",
            "Click here to finish"
        ])
    ])
    result3 = array_to_object_conversion(test3)
    print("   DEPOIS:")
    for k, v in result3[0][1]:
        print(f"     {k}: {v}")
    
    # Test 4: Nested structure
    print("\n4. Nested structure:")
    test4 = Obj([
        ("pages", Obj([
            ("home", Obj([
                ("messages", [
                    "Welcome to our website",
                    "Explore our features",
                    "Get started today"
                ])
            ])),
            ("about", Obj([
                ("info", [
                    "We are a technology company",
                    "Founded in 2020"
                ])
            ]))
        ]))
    ])
    result4 = array_to_object_conversion(test4)
    print("   DEPOIS:")
    print("   pages.home.messages:")
    for k, v in result4[0][1][0][1][0][1]:
        print(f"     {k}: {v}")
    print("   pages.about.info:")
    for k, v in result4[0][1][1][1][0][1]:
        print(f"     {k}: {v}")
    
    # Test 5: Mixed array (strings + numbers) - should NOT convert
    print("\n5. Mixed array (should NOT convert):")
    test5 = Obj([
        ("data", ["text", 123, "more text"])
    ])
    result5 = array_to_object_conversion(test5)
    print("   DEPOIS (não convertido):")
    print("   ", result5[0][1])
    
    # Test 6: Different case styles
    print("\n6. Different case styles:")
    test_text = ["Welcome to our platform"]
    
    test6_camel = Obj([("msg", test_text)])
    result6_camel = array_to_object_conversion(test6_camel, case_style='camel')
    print(f"   camelCase: {list(result6_camel[0][1])[0][0]}")
    
    test6_pascal = Obj([("msg", test_text)])
    result6_pascal = array_to_object_conversion(test6_pascal, case_style='pascal')
    print(f"   PascalCase: {list(result6_pascal[0][1])[0][0]}")
    
    test6_snake = Obj([("msg", test_text)])
    result6_snake = array_to_object_conversion(test6_snake, case_style='snake')
    print(f"   snake_case: {list(result6_snake[0][1])[0][0]}")
    
    test6_kebab = Obj([("msg", test_text)])
    result6_kebab = array_to_object_conversion(test6_kebab, case_style='kebab')
    print(f"   kebab-case: {list(result6_kebab[0][1])[0][0]}")
    
    # Test 7: Real-world example with TS output
    print("\n7. Real-world example (TS format):")
    real_world = Obj([
        ("t", Obj([
            ("pages", Obj([
                ("contact", Obj([
                    ("hints", [
                        "Preencha todos os campos obrigatórios",
                        "Verifique se o e-mail está correto",
                        "Aguarde nossa resposta em até 24 horas"
                    ])
                ]))
            ]))
        ]))
    ])
    result7 = array_to_object_conversion(real_world)
    print("\n   export default " + dump_ts_obj(result7, indent=2, level=0) + ";")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_array_to_object()
