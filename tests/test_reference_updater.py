#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for reference_updater.py (Task #23 - v2.9.14)

Tests VALUE EQUALITY strategy for orphaned keys substitution.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import directly from file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "reference_updater",
    project_root / "src" / "rewriter" / "reference_updater.py"
)
reference_updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference_updater)

extract_all_keys_from_obj = reference_updater.extract_all_keys_from_obj
build_substitution_map_by_value = reference_updater.build_substitution_map_by_value
apply_substitutions_to_file = reference_updater.apply_substitutions_to_file
update_references_in_project = reference_updater.update_references_in_project


class TestExtractKeysFromObj(unittest.TestCase):
    """Test extract_all_keys_from_obj with dict and Obj types."""
    
    def test_extract_from_dict_simple(self):
        """Test extraction from simple dict structure."""
        data = {
            'pages': {
                'contact': {
                    'title': 'Contact Us',
                    'description': 'Get in touch'
                }
            }
        }
        
        result = extract_all_keys_from_obj(data, prefix='t')
        
        expected = {
            't.pages.contact.title': 'Contact Us',
            't.pages.contact.description': 'Get in touch'
        }
        
        self.assertEqual(result, expected)
    
    def test_extract_from_dict_nested(self):
        """Test extraction from deeply nested dict."""
        data = {
            'pages': {
                'home': {
                    'hero': {
                        'title': 'Welcome',
                        'subtitle': 'To our site'
                    }
                }
            }
        }
        
        result = extract_all_keys_from_obj(data, prefix='t')
        
        self.assertIn('t.pages.home.hero.title', result)
        self.assertEqual(result['t.pages.home.hero.title'], 'Welcome')
        self.assertEqual(result['t.pages.home.hero.subtitle'], 'To our site')
    
    def test_extract_from_obj_type(self):
        """Test extraction from Obj type (list of tuples)."""
        # Simulate Obj structure from rewriter
        data = [
            ('pages', [
                ('contact', [
                    ('title', 'Contact'),
                    ('description', 'Reach us')
                ])
            ])
        ]
        
        result = extract_all_keys_from_obj(data, prefix='t')
        
        expected = {
            't.pages.contact.title': 'Contact',
            't.pages.contact.description': 'Reach us'
        }
        
        self.assertEqual(result, expected)
    
    def test_extract_ignores_arrays(self):
        """Test that arrays are not treated as reference paths."""
        data = {
            'tips': ['Tip 1', 'Tip 2', 'Tip 3'],
            'pages': {
                'home': {
                    'title': 'Home'
                }
            }
        }
        
        result = extract_all_keys_from_obj(data, prefix='t')
        
        # Should only extract 'home.title', not array items
        self.assertEqual(len(result), 1)
        self.assertIn('t.pages.home.title', result)


class TestBuildSubstitutionMapByValue(unittest.TestCase):
    """Test build_substitution_map_by_value with VALUE EQUALITY."""
    
    def test_simple_substitution_same_value(self):
        """Test 1: Simple case - contactPage eliminated, contact kept."""
        old_keys = {
            't.pages.contact.title': 'Contact Us',
            't.pages.contactPage.title': 'Contact Us'  # DUPLICATE
        }
        
        new_keys = {
            't.pages.contact.title': 'Contact Us'
            # contactPage removed
        }
        
        result = build_substitution_map_by_value(old_keys, new_keys)
        
        expected = {
            't.pages.contactPage.title': 't.pages.contact.title'
        }
        
        self.assertEqual(result, expected)
    
    def test_different_values_no_substitution(self):
        """Test 4: Different values - do NOT substitute."""
        old_keys = {
            't.pages.contact.title': 'Contact Us',
            't.pages.contactPage.title': 'Get in Touch'  # DIFFERENT VALUE
        }
        
        new_keys = {
            't.pages.contact.title': 'Contact Us',
            't.pages.contactPage.title': 'Get in Touch'
        }
        
        result = build_substitution_map_by_value(old_keys, new_keys)
        
        # Should be empty - values are different, so no elimination should happen
        self.assertEqual(result, {})
    
    def test_multiple_substitutions(self):
        """Test 2: Multiple keys eliminated."""
        old_keys = {
            't.pages.home.hero.title': 'Welcome',
            't.pages.home.heroSection.title': 'Welcome',  # DUPLICATE 1
            't.pages.home.description': 'About us',
            't.pages.home.desc': 'About us'  # DUPLICATE 2
        }
        
        new_keys = {
            't.pages.home.hero.title': 'Welcome',
            't.pages.home.description': 'About us'
        }
        
        result = build_substitution_map_by_value(old_keys, new_keys)
        
        expected = {
            't.pages.home.heroSection.title': 't.pages.home.hero.title',
            't.pages.home.desc': 't.pages.home.description'
        }
        
        self.assertEqual(result, expected)
    
    def test_no_substitutions_needed(self):
        """Test 3: No keys eliminated."""
        old_keys = {
            't.pages.home.title': 'Home',
            't.pages.contact.title': 'Contact'
        }
        
        new_keys = {
            't.pages.home.title': 'Home',
            't.pages.contact.title': 'Contact'
        }
        
        result = build_substitution_map_by_value(old_keys, new_keys)
        
        # Should be empty - no keys removed
        self.assertEqual(result, {})
    
    def test_same_parent_priority(self):
        """Test priority: prefer candidate with same parent path."""
        old_keys = {
            't.pages.contact.lookingForQuickAnswers': 'Looking for quick answers?',
            't.pages.contactPage.lookingForQuickAnswers': 'Looking for quick answers?',  # DUPLICATE
            't.common.lookingForQuickAnswers': 'Looking for quick answers?'  # SAME VALUE, different parent
        }
        
        new_keys = {
            't.pages.contact.lookingForQuickAnswers': 'Looking for quick answers?',
            't.common.lookingForQuickAnswers': 'Looking for quick answers?'
        }
        
        result = build_substitution_map_by_value(old_keys, new_keys)
        
        # Should prefer t.pages.contact (same parent 't.pages') over t.common
        expected = {
            't.pages.contactPage.lookingForQuickAnswers': 't.pages.contact.lookingForQuickAnswers'
        }
        
        self.assertEqual(result, expected)


class TestApplySubstitutions(unittest.TestCase):
    """Test apply_substitutions_to_file with real file operations."""
    
    def test_apply_substitutions_tsx_file(self):
        """Test substitution in .tsx file with {t.path} and t.path patterns."""
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
            f.write('''
export default function ContactPage() {
  const {t} = useTranslation();
  return (
    <div>
      <h1>{t.pages.contactPage.title}</h1>
      <p>{t.pages.contactPage.description}</p>
      <span>{t.pages.contactPage.lookingForQuickAnswers}</span>
    </div>
  );
}
''')
            temp_path = f.name
        
        try:
            # Apply substitutions
            substitution_map = {
                't.pages.contactPage.title': 't.pages.contact.title',
                't.pages.contactPage.description': 't.pages.contact.description',
                't.pages.contactPage.lookingForQuickAnswers': 't.pages.contact.lookingForQuickAnswers'
            }
            
            count = apply_substitutions_to_file(temp_path, substitution_map, create_backup=True)
            
            # Check count (counts both {t.path} and t.path patterns, so 3 matches × 2 = 6)
            self.assertEqual(count, 6)
            
            # Read updated file
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Verify substitutions
            self.assertIn('t.pages.contact.title', content)
            self.assertIn('t.pages.contact.description', content)
            self.assertIn('t.pages.contact.lookingForQuickAnswers', content)
            self.assertNotIn('t.pages.contactPage', content)
            
            # Check backup created
            backup_path = temp_path + '.bak'
            self.assertTrue(os.path.exists(backup_path))
            
            # Cleanup backup
            os.remove(backup_path)
        
        finally:
            os.remove(temp_path)
    
    def test_no_changes_if_no_matches(self):
        """Test that file is not modified if no substitutions match."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
            f.write('<h1>{t.pages.home.title}</h1>')
            temp_path = f.name
        
        try:
            substitution_map = {
                't.pages.contact.title': 't.pages.newcontact.title'
            }
            
            count = apply_substitutions_to_file(temp_path, substitution_map, create_backup=False)
            
            # No substitutions should be made
            self.assertEqual(count, 0)
        
        finally:
            os.remove(temp_path)


class TestUpdateReferencesInProject(unittest.TestCase):
    """Test update_references_in_project with directory scanning."""
    
    def test_update_multiple_files(self):
        """Test updating references across multiple files in a directory."""
        # Create temp directory with multiple files
        with tempfile.TemporaryDirectory() as temp_dir:
            # File 1: home.tsx
            home_path = os.path.join(temp_dir, 'home.tsx')
            with open(home_path, 'w') as f:
                f.write('<h1>{t.pages.contactPage.title}</h1>')
            
            # File 2: header.tsx
            header_path = os.path.join(temp_dir, 'header.tsx')
            with open(header_path, 'w') as f:
                f.write('<nav>{t.pages.contactPage.title}</nav>')
            
            # File 3: unrelated.txt (should be ignored)
            txt_path = os.path.join(temp_dir, 'readme.txt')
            with open(txt_path, 'w') as f:
                f.write('Some text')
            
            # Apply substitutions
            substitution_map = {
                't.pages.contactPage.title': 't.pages.contact.title'
            }
            
            results = update_references_in_project(
                temp_dir,
                substitution_map,
                extensions=['.tsx', '.jsx'],
                create_backup=False
            )
            
            # Should update 2 files (home.tsx and header.tsx)
            self.assertEqual(len(results), 2)
            self.assertIn(home_path, results)
            self.assertIn(header_path, results)
            # Each file has 2 substitutions: {t.path} and t.path
            self.assertEqual(results[home_path], 2)
            self.assertEqual(results[header_path], 2)
            
            # Verify files were updated
            with open(home_path, 'r') as f:
                self.assertIn('t.pages.contact.title', f.read())
            
            with open(header_path, 'r') as f:
                self.assertIn('t.pages.contact.title', f.read())


if __name__ == '__main__':
    unittest.main()
