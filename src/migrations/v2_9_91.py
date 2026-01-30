#!/usr/bin/env python3
"""
Migration v2.9.90 → v2.9.91

Changes:
- Adds app.version field to config.yaml for version tracking
- No QSettings changes (this is the first migration, establishes baseline)

This migration establishes the version tracking system.
Future migrations can reference this as an example.
"""

from typing import Dict, Any

from src.migrations.base import Migration


class MigrationV2_9_91(Migration):
    """
    First migration: Establish version tracking system.

    v2.9.90 → v2.9.91
    """

    version = "2.9.91"

    def migrate_qsettings(self, settings) -> bool:
        """
        No QSettings changes in this version.
        Just saves version for future migrations.
        """
        # Save version (already handled by MigrationManager)
        return True

    def migrate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add app.version field to config.yaml if missing.
        """
        # Ensure app section exists
        if "app" not in config:
            config["app"] = {}

        # Add version tracking
        if "version" not in config.get("app", {}):
            config["app"]["version"] = self.version

        return config
