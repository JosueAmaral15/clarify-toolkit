"""
Formula Manager for Set Operations
Manages formula definitions and execution with variables/slots.

Author: Josué Amaral
Date: 2025/12/23
Version: 2.9.108
"""

import json
from typing import Any, Dict, List, Optional
from PySide6.QtCore import QSettings


class FormulaStep:
    """
    Represents a single step in a formula.
    
    Attributes:
        operation: Operation type ('∩', '∪', '−', '⊕')
        input_a: Input A identifier ('file_path', 'slot_a', 'slot_b', 'previous')
        input_b: Input B identifier ('file_path', 'slot_a', 'slot_b', etc)
        file_a_path: File path if input_a is 'file_path'
        file_b_path: File path if input_b is 'file_path'
        output_variable: Variable name to store result (e.g., 'result1', 'r1')
        comparison_mode: Comparison mode ('key_value', 'full_path_value', 'key_only')
        options: Dict with ignore_case_keys, ignore_case_values, skip_empty, arrays_ignore_order
    """
    
    def __init__(self, operation: str, input_a: str, input_b: str,
                 file_a_path: str = "", file_b_path: str = "",
                 output_variable: str = "",
                 comparison_mode: str = 'key_value',
                 options: Dict[str, bool] = None):
        """Initialize FormulaStep."""
        self.operation = operation  # '∩', '∪', '−', '⊕'
        self.input_a = input_a
        self.input_b = input_b
        self.file_a_path = file_a_path
        self.file_b_path = file_b_path
        self.output_variable = output_variable or f"r{id(self) % 1000}"
        self.comparison_mode = comparison_mode
        self.options = options or {
            'ignore_case_keys': False,
            'ignore_case_values': False,
            'skip_empty': True,
            'arrays_ignore_order': False
        }
        
        # Execution state
        self.result = None
        self.result_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            'operation': self.operation,
            'input_a': self.input_a,
            'input_b': self.input_b,
            'file_a_path': self.file_a_path,
            'file_b_path': self.file_b_path,
            'output_variable': self.output_variable,
            'comparison_mode': self.comparison_mode,
            'options': self.options
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FormulaStep':
        """Create FormulaStep from dict."""
        return FormulaStep(
            operation=data['operation'],
            input_a=data['input_a'],
            input_b=data['input_b'],
            file_a_path=data.get('file_a_path', ''),
            file_b_path=data.get('file_b_path', ''),
            output_variable=data.get('output_variable', ''),
            comparison_mode=data.get('comparison_mode', 'key_value'),
            options=data.get('options', {})
        )
    
    def get_display_text(self) -> str:
        """
        Get human-readable display text for step.
        
        Returns:
            String like "r1 = A ∩ B" or "r2 = r1 ∪ config.json"
        """
        input_a_display = self._get_input_display(self.input_a, self.file_a_path)
        input_b_display = self._get_input_display(self.input_b, self.file_b_path)
        return f"{self.output_variable} = {input_a_display} {self.operation} {input_b_display}"
    
    def _get_input_display(self, input_type: str, file_path: str) -> str:
        """Get display text for input."""
        if input_type == 'file_path' and file_path:
            import os
            return os.path.basename(file_path)
        elif input_type == 'previous':
            return '(previous)'
        else:
            return input_type  # 'slot_a', 'slot_b', 'r1', etc


class Formula:
    """
    Represents a complete formula with multiple steps.
    
    Attributes:
        name: Formula name
        description: Human-readable description
        steps: List of FormulaStep
    """
    
    def __init__(self, name: str, description: str = "", steps: List[FormulaStep] = None):
        """Initialize Formula."""
        self.name = name
        self.description = description
        self.steps = steps or []
    
    def add_step(self, step: FormulaStep):
        """Add step to formula."""
        self.steps.append(step)
    
    def remove_step(self, index: int):
        """Remove step at index."""
        if 0 <= index < len(self.steps):
            self.steps.pop(index)
    
    def get_formula_text(self) -> str:
        """
        Get complete formula as text.
        
        Returns:
            String like "(A ∩ B) ∪ (C − D)"
        """
        if not self.steps:
            return ""
        
        lines = []
        for i, step in enumerate(self.steps, 1):
            lines.append(f"Step {i}: {step.get_display_text()}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'steps': [step.to_dict() for step in self.steps]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Formula':
        """Create Formula from dict."""
        steps = [FormulaStep.from_dict(s) for s in data.get('steps', [])]
        return Formula(
            name=data['name'],
            description=data.get('description', ''),
            steps=steps
        )


class FormulaManager:
    """
    Manages formula templates using QSettings.
    Similar to PresetsManager but for complete formulas.
    """
    
    SETTINGS_KEY = "formula_templates"
    
    # Default formulas (created on first run)
    DEFAULT_FORMULAS = [
        {
            'name': 'Simple Merge',
            'description': 'Merge two configs with common keys',
            'steps': [
                {
                    'operation': '∩',
                    'input_a': 'file_path',
                    'input_b': 'file_path',
                    'file_a_path': '',
                    'file_b_path': '',
                    'output_variable': 'common',
                    'comparison_mode': 'key_value',
                    'options': {'ignore_case_keys': False, 'ignore_case_values': False,
                                'skip_empty': True, 'arrays_ignore_order': False}
                }
            ]
        },
        {
            'name': 'Config Merge with Exclusions',
            'description': 'Merge configs but exclude specific keys',
            'steps': [
                {
                    'operation': '∩',
                    'input_a': 'file_path',
                    'input_b': 'file_path',
                    'file_a_path': '',
                    'file_b_path': '',
                    'output_variable': 'r1',
                    'comparison_mode': 'key_value',
                    'options': {'ignore_case_keys': False, 'ignore_case_values': False,
                                'skip_empty': True, 'arrays_ignore_order': False}
                },
                {
                    'operation': '∪',
                    'input_a': 'previous',
                    'input_b': 'file_path',
                    'file_a_path': '',
                    'file_b_path': '',
                    'output_variable': 'r2',
                    'comparison_mode': 'key_value',
                    'options': {'ignore_case_keys': False, 'ignore_case_values': False,
                                'skip_empty': True, 'arrays_ignore_order': False}
                },
                {
                    'operation': '−',
                    'input_a': 'previous',
                    'input_b': 'file_path',
                    'file_a_path': '',
                    'file_b_path': '',
                    'output_variable': 'final',
                    'comparison_mode': 'key_value',
                    'options': {'ignore_case_keys': False, 'ignore_case_values': False,
                                'skip_empty': True, 'arrays_ignore_order': False}
                }
            ]
        }
    ]
    
    def __init__(self):
        """Initialize FormulaManager."""
        self.settings = QSettings("Clarify", "Clarify")
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """Ensure default formulas exist."""
        formulas = self.get_formulas()
        
        if not formulas:
            for formula_data in self.DEFAULT_FORMULAS:
                formula = Formula.from_dict(formula_data)
                self.save_formula(formula)
    
    def get_formulas(self) -> List[Formula]:
        """
        Get list of all saved formulas.
        
        Returns:
            List of Formula objects
        """
        formulas_data = self.settings.value(self.SETTINGS_KEY, [])
        
        if not isinstance(formulas_data, list):
            return []
        
        formulas = []
        for data in formulas_data:
            try:
                formula = Formula.from_dict(data)
                formulas.append(formula)
            except (KeyError, TypeError):
                continue
        
        return formulas
    
    def get_formula(self, name: str) -> Optional[Formula]:
        """
        Get specific formula by name.
        
        Args:
            name: Formula name
        
        Returns:
            Formula object or None if not found
        """
        formulas = self.get_formulas()
        
        for formula in formulas:
            if formula.name == name:
                return formula
        
        return None
    
    def save_formula(self, formula: Formula):
        """
        Save formula (create or update).
        
        Args:
            formula: Formula to save
        """
        formulas = self.get_formulas()
        
        # Remove existing formula with same name
        formulas = [f for f in formulas if f.name != formula.name]
        
        # Add new/updated formula
        formulas.append(formula)
        
        # Save to QSettings
        formulas_data = [f.to_dict() for f in formulas]
        self.settings.setValue(self.SETTINGS_KEY, formulas_data)
    
    def delete_formula(self, name: str):
        """
        Delete formula by name.
        
        Args:
            name: Formula name to delete
        """
        formulas = self.get_formulas()
        formulas = [f for f in formulas if f.name != name]
        
        formulas_data = [f.to_dict() for f in formulas]
        self.settings.setValue(self.SETTINGS_KEY, formulas_data)
    
    def rename_formula(self, old_name: str, new_name: str):
        """
        Rename formula.
        
        Args:
            old_name: Current name
            new_name: New name
        """
        formula = self.get_formula(old_name)
        
        if formula:
            self.delete_formula(old_name)
            formula.name = new_name
            self.save_formula(formula)


class FormulaExecutor:
    """
    Executes formulas by running steps sequentially.
    Uses set_operations module for actual operations.
    """
    
    def __init__(self):
        """Initialize FormulaExecutor."""
        self.variables = {}  # Storage for intermediate results
    
    def execute(self, formula: Formula, initial_files: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Execute formula with given initial files.
        
        Args:
            formula: Formula to execute
            initial_files: Dict mapping input types to file paths
                          (e.g., {'file_a': '/path/a.json', 'file_b': '/path/b.json'})
        
        Returns:
            Dict with 'success': bool, 'result': data, 'variables': dict, 'error': str
        """
        from src.set_operations import (
            intersection, union, difference, symmetric_difference,
            compare_files
        )
        
        self.variables = {}
        initial_files = initial_files or {}
        previous_result = None
        
        operation_map = {
            '∩': intersection,
            '∪': union,
            '−': difference,
            '⊕': symmetric_difference
        }
        
        try:
            for i, step in enumerate(formula.steps, 1):
                # Get input A data
                input_a_data = self._get_input_data(
                    step.input_a, step.file_a_path, initial_files, previous_result
                )
                
                # Get input B data
                input_b_data = self._get_input_data(
                    step.input_b, step.file_b_path, initial_files, previous_result
                )
                
                # Execute operation
                operation_func = operation_map.get(step.operation)
                if not operation_func:
                    return {
                        'success': False,
                        'error': f"Unknown operation: {step.operation}",
                        'step': i
                    }
                
                # Prepare options dict
                options = {
                    'comparison_mode': step.comparison_mode,
                    'ignore_case_keys': step.options.get('ignore_case_keys', False),
                    'ignore_case_values': step.options.get('ignore_case_values', False),
                    'skip_empty': step.options.get('skip_empty', True),
                    'arrays_ignore_order': step.options.get('arrays_ignore_order', False)
                }
                
                # Execute operation with both inputs
                result = operation_func([input_a_data, input_b_data], **options)
                
                # Store result
                step.result = result
                step.result_count = len(result) if isinstance(result, dict) else 0
                self.variables[step.output_variable] = result
                previous_result = result
            
            return {
                'success': True,
                'result': previous_result,
                'variables': self.variables,
                'steps_executed': len(formula.steps)
            }
        
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f"File not found: {str(e)}",
                'step': i if 'i' in locals() else 0
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Invalid JSON: {str(e)}",
                'step': i if 'i' in locals() else 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'step': i if 'i' in locals() else 0
            }
    
    def _get_input_data(self, input_type: str, file_path: str,
                        initial_files: Dict[str, str],
                        previous_result: Any) -> Dict[str, Any]:
        """
        Get input data based on input type.
        
        Args:
            input_type: Type of input ('file_path', 'previous', 'slot_a', variable name)
            file_path: File path if input_type is 'file_path'
            initial_files: Initial files mapping
            previous_result: Result from previous step
        
        Returns:
            Data dict
        """
        if input_type == 'file_path':
            if not file_path:
                # Try to get from initial_files
                file_path = initial_files.get('file_a') or initial_files.get('file_b', '')
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        
        elif input_type == 'previous':
            return previous_result if previous_result else {}
        
        elif input_type in self.variables:
            return self.variables[input_type]
        
        elif input_type in initial_files:
            file_path = initial_files[input_type]
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        else:
            return {}
