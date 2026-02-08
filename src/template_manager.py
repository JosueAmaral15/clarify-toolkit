#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project Templates Manager for Clarify
--------------------------------------
Manages project templates for quick project setup with pre-configured settings.

Sprint: v2.9.63 - Project Templates System
Author: Josué Amaral
Date: 2025-12-10
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime



from .utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ProjectTemplate:
    """Represents a project template."""

    id: str
    name: str
    description: str
    category: str  # web, mobile, desktop, cli, data_science, other
    icon: str  # emoji or icon name
    config: Dict[str, Any]  # Template configuration
    files: List[Dict[str, str]]  # Files to create [{path: str, content: str}]
    created_at: str
    author: str = "Clarify"
    builtin: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectTemplate':
        """Create from dictionary."""
        return cls(**data)


class TemplateManager:
    """Manages project templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize template manager.

        Args:
            templates_dir: Directory for custom templates (default: ~/.config/clarify/templates)
        """
        if templates_dir is None:
            templates_dir = Path.home() / ".config" / "clarify" / "templates"

        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self._templates: Dict[str, ProjectTemplate] = {}
        self._load_builtin_templates()
        self._load_custom_templates()

    def _load_builtin_templates(self):
        """Load built-in templates."""

        # Template 1: JSON Translation Project
        self._templates["json_translation"] = ProjectTemplate(
            id="json_translation",
            name="JSON Translation Project",
            description="Multi-language JSON translation setup",
            category="web",
            icon="🌐",
            config={
                "languages": ["en", "pt-br", "es", "fr"],
                "default_language": "en",
                "file_format": "json"
            },
            files=[
                {
                    "path": "locales/en.json",
                    "content": '{\n  "app.title": "My Application",\n  "app.welcome": "Welcome"\n}'
                },
                {
                    "path": "locales/pt-br.json",
                    "content": '{\n  "app.title": "Minha Aplicação",\n  "app.welcome": "Bem-vindo"\n}'
                },
                {
                    "path": "README.md",
                    "content": "# Translation Project\n\nManage translations using Clarify's JSON tools."
                }
            ],
            created_at=datetime.now().isoformat(),
            author="Clarify",
            builtin=True
        )

        # Template 2: Text Processing Pipeline
        self._templates["text_processing"] = ProjectTemplate(
            id="text_processing",
            name="Text Processing Pipeline",
            description="Text extraction and processing workflow",
            category="data_science",
            icon="📝",
            config={
                "input_format": "txt",
                "output_format": "json",
                "processors": ["extract", "clean", "format"]
            },
            files=[
                {
                    "path": "input/sample.txt",
                    "content": "Sample text for processing"
                },
                {
                    "path": "output/.gitkeep",
                    "content": ""
                },
                {
                    "path": "config.json",
                    "content": '{\n  "processors": ["extract", "clean", "format"]\n}'
                }
            ],
            created_at=datetime.now().isoformat(),
            author="Clarify",
            builtin=True
        )

        # Template 3: JSON Rewriter Project
        self._templates["json_rewriter"] = ProjectTemplate(
            id="json_rewriter",
            name="JSON Cleanup Project",
            description="JSON deduplication and cleanup",
            category="web",
            icon="🔧",
            config={
                "dedupe": True,
                "join_keys": True,
                "eliminate_duplicates": True
            },
            files=[
                {
                    "path": "input/data.json",
                    "content": '{\n  "key1": "value1",\n  "key2": "value2"\n}'
                },
                {
                    "path": "output/.gitkeep",
                    "content": ""
                }
            ],
            created_at=datetime.now().isoformat(),
            author="Clarify",
            builtin=True
        )

        # Template 4: AI Processing Project
        self._templates["ai_processing"] = ProjectTemplate(
            id="ai_processing",
            name="AI Text Processing",
            description="AI-powered text processing with OpenAI/Anthropic",
            category="data_science",
            icon="🤖",
            config={
                "provider": "OpenAI",
                "model": "gpt-4",
                "batch_size": 10
            },
            files=[
                {
                    "path": "input/texts.txt",
                    "content": "Text 1\n---\nText 2\n---\nText 3"
                },
                {
                    "path": "prompts/system.txt",
                    "content": "You are a helpful assistant."
                },
                {
                    "path": "output/.gitkeep",
                    "content": ""
                }
            ],
            created_at=datetime.now().isoformat(),
            author="Clarify",
            builtin=True
        )

        # Template 5: Blank Project
        self._templates["blank"] = ProjectTemplate(
            id="blank",
            name="Blank Project",
            description="Empty project with basic structure",
            category="other",
            icon="📂",
            config={},
            files=[
                {
                    "path": "README.md",
                    "content": "# New Project\n\nCreated with Clarify."
                },
                {
                    "path": "input/.gitkeep",
                    "content": ""
                },
                {
                    "path": "output/.gitkeep",
                    "content": ""
                }
            ],
            created_at=datetime.now().isoformat(),
            author="Clarify",
            builtin=True
        )

    def _load_custom_templates(self):
        """Load custom templates from disk."""
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = ProjectTemplate.from_dict(data)
                    self._templates[template.id] = template
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"Failed to load template {template_file}: {e}")

    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """Get template by ID."""
        return self._templates.get(template_id)

    def list_templates(self, category: Optional[str] = None) -> List[ProjectTemplate]:
        """
        List available templates.

        Args:
            category: Filter by category (None = all)

        Returns:
            List of templates
        """
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return sorted(templates, key=lambda t: (not t.builtin, t.name))

    def get_categories(self) -> List[str]:
        """Get all template categories."""
        categories = set(t.category for t in self._templates.values())
        return sorted(categories)

    def create_from_template(
        self,
        template_id: str,
        target_dir: Path,
        overwrite: bool = False
    ) -> bool:
        """
        Create project from template.

        Args:
            template_id: Template ID
            target_dir: Target directory
            overwrite: Overwrite existing files

        Returns:
            True if successful
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        # Create files
        for file_info in template.files:
            file_path = target_dir / file_info["path"]

            if file_path.exists() and not overwrite:
                continue

            file_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_info["content"])
            except (IOError, OSError, PermissionError) as e:
                logger.error(f"Failed to write template file {file_path}: {e}")
                raise RuntimeError(f"Cannot create template file {file_path}: {e}") from e

        return True

    def save_template(self, template: ProjectTemplate) -> bool:
        """
        Save custom template.

        Args:
            template: Template to save

        Returns:
            True if successful
        """
        if template.builtin:
            raise ValueError("Cannot modify built-in templates")

        template_file = self.templates_dir / f"{template.id}.json"

        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2)
        except (IOError, OSError, PermissionError) as e:
            logger.error(f"Failed to save template to {template_file}: {e}")
            raise RuntimeError(f"Cannot save template: {e}") from e

        self._templates[template.id] = template
        return True

    def delete_template(self, template_id: str) -> bool:
        """
        Delete custom template.

        Args:
            template_id: Template ID

        Returns:
            True if successful
        """
        template = self.get_template(template_id)
        if not template:
            return False

        if template.builtin:
            raise ValueError("Cannot delete built-in templates")

        template_file = self.templates_dir / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()

        del self._templates[template_id]
        return True

    def create_template_from_directory(
        self,
        source_dir: Path,
        template_id: str,
        name: str,
        description: str,
        category: str,
        icon: str = "📁"
    ) -> ProjectTemplate:
        """
        Create template from existing directory.

        Args:
            source_dir: Source directory
            template_id: Template ID
            name: Template name
            description: Template description
            category: Template category
            icon: Template icon

        Returns:
            Created template
        """
        source_dir = Path(source_dir)

        if not source_dir.exists():
            raise ValueError(f"Directory not found: {source_dir}")

        # Collect files
        files = []
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(source_dir)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    files.append({
                        "path": str(rel_path),
                        "content": content
                    })
                except Exception:  # pylint: disable=broad-exception-caught
                    # Skip binary files
                    continue

        template = ProjectTemplate(
            id=template_id,
            name=name,
            description=description,
            category=category,
            icon=icon,
            config={},
            files=files,
            created_at=datetime.now().isoformat(),
            author="Custom",
            builtin=False
        )

        return template


# Singleton instance (private, use get_template_manager())
_template_manager: Optional[TemplateManager] = None  # pylint: disable=invalid-name


def get_template_manager() -> TemplateManager:
    """Get singleton TemplateManager instance."""
    global _template_manager  # pylint: disable=global-statement
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager


def reset_template_manager():
    """Reset singleton (for testing)."""
    global _template_manager  # pylint: disable=global-statement
    _template_manager = None


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    logger.error("Template Manager Demo")
    print("=" * 80)

    manager = get_template_manager()

    logger.error(f"\nAvailable templates: {len(manager.list_templates())}")
    logger.error("\nBuilt-in templates:")
    for tmpl in manager.list_templates():  # Renamed to avoid shadowing class method params
        if tmpl.builtin:
            logger.error(f"  {tmpl.icon} {tmpl.name} - {tmpl.description}")

    logger.error("\nCategories:")
    for cat in manager.get_categories():  # Renamed to avoid shadowing class method params
        count = len([t for t in manager.list_templates() if t.category == cat])
        logger.error(f"  {cat}: {count} templates")

    logger.error("\n✅ Template Manager demo complete")
