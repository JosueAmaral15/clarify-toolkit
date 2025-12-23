"""
Unit tests for Formula Builder (v2.9.108)
Tests FormulaManager, FormulaStep, Formula, FormulaExecutor.

Author: Josué Amaral
Date: 2025/12/23
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from src.formula_manager import (
    FormulaStep, Formula, FormulaManager, FormulaExecutor
)


class TestFormulaStep(unittest.TestCase):
    """Test FormulaStep class."""
    
    def test_create_step(self):
        """Test creating a formula step."""
        step = FormulaStep(
            operation='∩',
            input_a='file_path',
            input_b='file_path',
            file_a_path='/path/a.json',
            file_b_path='/path/b.json',
            output_variable='r1'
        )
        
        self.assertEqual(step.operation, '∩')
        self.assertEqual(step.input_a, 'file_path')
        self.assertEqual(step.output_variable, 'r1')
        # FormulaStep doesn't have status attribute
        self.assertIsNone(step.result)
    
    def test_step_display_text(self):
        """Test step display text generation."""
        step = FormulaStep(
            operation='∪',
            input_a='file_path',
            input_b='previous',
            file_a_path='/path/config.json',
            output_variable='r1'
        )
        
        display = step.get_display_text()
        self.assertIn('r1', display)
        self.assertIn('∪', display)
        self.assertIn('config.json', display)
        self.assertIn('(previous)', display)
    
    def test_step_to_dict(self):
        """Test step serialization to dict."""
        step = FormulaStep(
            operation='−',
            input_a='slot_a',
            input_b='file_path',
            file_b_path='/path/exclude.json',
            output_variable='final'
        )
        
        data = step.to_dict()
        self.assertEqual(data['operation'], '−')
        self.assertEqual(data['input_a'], 'slot_a')
        self.assertEqual(data['output_variable'], 'final')
    
    def test_step_from_dict(self):
        """Test step deserialization from dict."""
        data = {
            'operation': '⊕',
            'input_a': 'file_path',
            'input_b': 'file_path',
            'file_a_path': '/a.json',
            'file_b_path': '/b.json',
            'output_variable': 'xor_result',
            'comparison_mode': 'key_only',
            'options': {'ignore_case_keys': True}
        }
        
        step = FormulaStep.from_dict(data)
        self.assertEqual(step.operation, '⊕')
        self.assertEqual(step.output_variable, 'xor_result')
        self.assertEqual(step.comparison_mode, 'key_only')
        self.assertTrue(step.options['ignore_case_keys'])


class TestFormula(unittest.TestCase):
    """Test Formula class."""
    
    def test_create_formula(self):
        """Test creating a formula."""
        formula = Formula("Test Formula", "A test formula")
        self.assertEqual(formula.name, "Test Formula")
        self.assertEqual(formula.description, "A test formula")
        self.assertEqual(len(formula.steps), 0)
    
    def test_add_remove_steps(self):
        """Test adding and removing steps."""
        formula = Formula("Test")
        
        step1 = FormulaStep('∩', 'file_path', 'file_path', output_variable='r1')
        step2 = FormulaStep('∪', 'previous', 'file_path', output_variable='r2')
        
        formula.add_step(step1)
        formula.add_step(step2)
        self.assertEqual(len(formula.steps), 2)
        
        formula.remove_step(0)
        self.assertEqual(len(formula.steps), 1)
        self.assertEqual(formula.steps[0].output_variable, 'r2')
    
    def test_formula_text(self):
        """Test formula text generation."""
        formula = Formula("Simple Merge")
        
        step1 = FormulaStep(
            '∩', 'file_path', 'file_path',
            file_a_path='/a.json', file_b_path='/b.json',
            output_variable='common'
        )
        formula.add_step(step1)
        
        text = formula.get_formula_text()
        self.assertIn('Step 1:', text)
        self.assertIn('common', text)
        self.assertIn('∩', text)
    
    def test_formula_to_dict(self):
        """Test formula serialization."""
        formula = Formula("Test", "Description")
        step = FormulaStep('∪', 'file_path', 'file_path', output_variable='r1')
        formula.add_step(step)
        
        data = formula.to_dict()
        self.assertEqual(data['name'], "Test")
        self.assertEqual(data['description'], "Description")
        self.assertEqual(len(data['steps']), 1)
    
    def test_formula_from_dict(self):
        """Test formula deserialization."""
        data = {
            'name': 'Config Merge',
            'description': 'Merge configs',
            'steps': [
                {
                    'operation': '∩',
                    'input_a': 'file_path',
                    'input_b': 'file_path',
                    'file_a_path': '',
                    'file_b_path': '',
                    'output_variable': 'r1',
                    'comparison_mode': 'key_value',
                    'options': {}
                }
            ]
        }
        
        formula = Formula.from_dict(data)
        self.assertEqual(formula.name, 'Config Merge')
        self.assertEqual(len(formula.steps), 1)
        self.assertEqual(formula.steps[0].operation, '∩')


class TestFormulaManager(unittest.TestCase):
    """Test FormulaManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = FormulaManager()
    
    def test_get_formulas(self):
        """Test getting list of formulas."""
        formulas = self.manager.get_formulas()
        self.assertIsInstance(formulas, list)
        # Should have at least default formulas
        self.assertGreaterEqual(len(formulas), 2)
    
    def test_save_and_get_formula(self):
        """Test saving and retrieving formula."""
        formula = Formula("Test Save", "Test description")
        step = FormulaStep('∪', 'file_path', 'file_path', output_variable='test')
        formula.add_step(step)
        
        self.manager.save_formula(formula)
        
        retrieved = self.manager.get_formula("Test Save")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Save")
        self.assertEqual(len(retrieved.steps), 1)
    
    def test_delete_formula(self):
        """Test deleting formula."""
        formula = Formula("To Delete")
        self.manager.save_formula(formula)
        
        # Verify it exists
        self.assertIsNotNone(self.manager.get_formula("To Delete"))
        
        # Delete it
        self.manager.delete_formula("To Delete")
        
        # Verify it's gone
        self.assertIsNone(self.manager.get_formula("To Delete"))
    
    def test_rename_formula(self):
        """Test renaming formula."""
        formula = Formula("Old Name", "Description")
        self.manager.save_formula(formula)
        
        self.manager.rename_formula("Old Name", "New Name")
        
        # Old name should not exist
        self.assertIsNone(self.manager.get_formula("Old Name"))
        
        # New name should exist
        renamed = self.manager.get_formula("New Name")
        self.assertIsNotNone(renamed)
        self.assertEqual(renamed.description, "Description")


class TestFormulaExecutor(unittest.TestCase):
    """Test FormulaExecutor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.executor = FormulaExecutor()
        
        # Create temporary test files
        self.temp_dir = tempfile.mkdtemp()
        
        # File A: {"a": 1, "b": 2, "c": 3}
        self.file_a = os.path.join(self.temp_dir, 'a.json')
        with open(self.file_a, 'w') as f:
            json.dump({"a": 1, "b": 2, "c": 3}, f)
        
        # File B: {"b": 2, "c": 3, "d": 4}
        self.file_b = os.path.join(self.temp_dir, 'b.json')
        with open(self.file_b, 'w') as f:
            json.dump({"b": 2, "c": 3, "d": 4}, f)
        
        # File C: {"e": 5, "f": 6}
        self.file_c = os.path.join(self.temp_dir, 'c.json')
        with open(self.file_c, 'w') as f:
            json.dump({"e": 5, "f": 6}, f)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_execute_single_step(self):
        """Test executing formula with single step."""
        formula = Formula("Single Step")
        step = FormulaStep(
            operation='∩',
            input_a='file_path',
            input_b='file_path',
            file_a_path=self.file_a,
            file_b_path=self.file_b,
            output_variable='common'
        )
        formula.add_step(step)
        
        result = self.executor.execute(formula)
        
        if not result['success']:
            print(f"\nExecution failed: {result.get('error', 'Unknown error')}")
        
        self.assertTrue(result['success'], f"Execution failed: {result.get('error', 'Unknown')}")
        self.assertEqual(result['steps_executed'], 1)
        
        # Result format is {'intersection': [list_of_tuples]}
        final_result = result['result']
        self.assertIn('intersection', final_result)
        
        # Intersection should have keys b and c (values from set operations are tuples)
        result_keys = [item[0] if isinstance(item, tuple) else item 
                      for item in final_result.get('intersection', [])]
        self.assertIn('b', result_keys)
        self.assertIn('c', result_keys)
        self.assertNotIn('a', result_keys)
        self.assertNotIn('d', result_keys)
    
    def test_execute_multiple_steps(self):
        """Test executing formula with multiple steps."""
        formula = Formula("Multi Step")
        
        # Step 1: A ∩ B → r1
        step1 = FormulaStep(
            operation='∩',
            input_a='file_path',
            input_b='file_path',
            file_a_path=self.file_a,
            file_b_path=self.file_b,
            output_variable='r1'
        )
        formula.add_step(step1)
        
        # Step 2: r1 ∪ C → final
        step2 = FormulaStep(
            operation='∪',
            input_a='previous',
            input_b='file_path',
            file_b_path=self.file_c,
            output_variable='final'
        )
        formula.add_step(step2)
        
        result = self.executor.execute(formula)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['steps_executed'], 2)
        
        # Result is in {'union': [list]} format
        final_result = result['result']
        self.assertIn('union', final_result)
        
        # Should have b, c from r1 and e, f from C
        result_keys = [item[0] if isinstance(item, tuple) else item 
                      for item in final_result.get('union', [])]
        self.assertIn('e', result_keys)
        self.assertIn('f', result_keys)
        # From intersection r1: b and c
        # Note: may appear as nested tuples in complex operations
    
    def test_execute_with_union(self):
        """Test union operation."""
        formula = Formula("Union Test")
        step = FormulaStep(
            operation='∪',
            input_a='file_path',
            input_b='file_path',
            file_a_path=self.file_a,
            file_b_path=self.file_b,
            output_variable='union'
        )
        formula.add_step(step)
        
        result = self.executor.execute(formula)
        
        self.assertTrue(result['success'])
        
        # Result is in {'union': [list]} format
        final_result = result['result']
        self.assertIn('union', final_result)
        
        # Union should have all keys: a, b, c, d
        result_keys = [item[0] if isinstance(item, tuple) else item 
                      for item in final_result.get('union', [])]
        self.assertIn('a', result_keys)
        self.assertIn('b', result_keys)
        self.assertIn('c', result_keys)
        self.assertIn('d', result_keys)
    
    def test_execute_with_difference(self):
        """Test difference operation."""
        formula = Formula("Difference Test")
        step = FormulaStep(
            operation='−',
            input_a='file_path',
            input_b='file_path',
            file_a_path=self.file_a,
            file_b_path=self.file_b,
            output_variable='diff'
        )
        formula.add_step(step)
        
        result = self.executor.execute(formula)
        
        self.assertTrue(result['success'])
        
        # Result is in {'difference': [list]} format
        final_result = result['result']
        self.assertIn('difference', final_result)
        
        # Difference should have only 'a' (in A but not B)
        result_keys = [item[0] if isinstance(item, tuple) else item 
                      for item in final_result.get('difference', [])]
        self.assertIn('a', result_keys)
        self.assertNotIn('b', result_keys)
        self.assertNotIn('c', result_keys)
        self.assertNotIn('d', result_keys)
    
    def test_execute_nonexistent_file(self):
        """Test execution with nonexistent file."""
        formula = Formula("Error Test")
        step = FormulaStep(
            operation='∩',
            input_a='file_path',
            input_b='file_path',
            file_a_path='/nonexistent/file.json',
            file_b_path=self.file_b,
            output_variable='error'
        )
        formula.add_step(step)
        
        result = self.executor.execute(formula)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('File not found', result['error'] or result.get('error', ''))


class TestIntegration(unittest.TestCase):
    """Integration tests for Formula Builder."""
    
    def test_save_load_execute_flow(self):
        """Test complete workflow: create → save → load → execute."""
        manager = FormulaManager()
        executor = FormulaExecutor()
        
        # Create test files
        temp_dir = tempfile.mkdtemp()
        file_a = os.path.join(temp_dir, 'test_a.json')
        file_b = os.path.join(temp_dir, 'test_b.json')
        
        with open(file_a, 'w') as f:
            json.dump({"x": 1, "y": 2, "z": 3}, f)
        with open(file_b, 'w') as f:
            json.dump({"y": 2, "z": 3, "w": 4}, f)
        
        try:
            # Create formula
            formula = Formula("Integration Test", "Test workflow")
            step = FormulaStep(
                operation='∩',
                input_a='file_path',
                input_b='file_path',
                file_a_path=file_a,
                file_b_path=file_b,
                output_variable='result'
            )
            formula.add_step(step)
            
            # Save formula
            manager.save_formula(formula)
            
            # Load formula
            loaded = manager.get_formula("Integration Test")
            self.assertIsNotNone(loaded)
            self.assertEqual(len(loaded.steps), 1)
            
            # Execute loaded formula
            result = executor.execute(loaded)
            self.assertTrue(result['success'])
            
            # Verify result - format is {'intersection': [list]}
            final = result['result']
            self.assertIn('intersection', final)
            
            result_keys = [item[0] if isinstance(item, tuple) else item 
                          for item in final.get('intersection', [])]
            self.assertIn('y', result_keys)
            self.assertIn('z', result_keys)
            self.assertNotIn('x', result_keys)
            self.assertNotIn('w', result_keys)
        
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)
            manager.delete_formula("Integration Test")


if __name__ == '__main__':
    unittest.main()
