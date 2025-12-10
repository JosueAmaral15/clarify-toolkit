#!/usr/bin/env python3
# Tests for Template Manager - Sprint v2.9.63

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
from tempfile import TemporaryDirectory
from src.template_manager import TemplateManager, ProjectTemplate, get_template_manager, reset_template_manager


class TestTemplateManager(unittest.TestCase):
    def setUp(self):
        reset_template_manager()
        self.temp_dir = TemporaryDirectory()
        self.manager = TemplateManager(Path(self.temp_dir.name))
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_builtin_templates_loaded(self):
        templates = self.manager.list_templates()
        self.assertGreater(len(templates), 0)
        self.assertTrue(any(t.builtin for t in templates))
    
    def test_get_template(self):
        template = self.manager.get_template("blank")
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "Blank Project")
    
    def test_list_templates_by_category(self):
        web_templates = self.manager.list_templates(category="web")
        self.assertGreater(len(web_templates), 0)
        self.assertTrue(all(t.category == "web" for t in web_templates))
    
    def test_get_categories(self):
        categories = self.manager.get_categories()
        self.assertIn("web", categories)
        self.assertIn("data_science", categories)
    
    def test_create_from_template(self):
        with TemporaryDirectory() as target_dir:
            success = self.manager.create_from_template("blank", Path(target_dir))
            self.assertTrue(success)
            self.assertTrue((Path(target_dir) / "README.md").exists())


if __name__ == '__main__':
    unittest.main()
