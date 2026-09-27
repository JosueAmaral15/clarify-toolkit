#!/usr/bin/env python3
# pylint: disable=import-outside-toplevel  # Avoid circular imports
# pylint: disable=broad-exception-caught  # Migration must handle all errors gracefully
"""
Migration Manager - v2.9.91

Automatic migration system for QSettings and config.yaml when app structure changes.

Features:
- Detects app version and runs pending migrations
- Migrates both QSettings and config.yaml
- Fail-safe with automatic backup
- Logging to ~/.clarify/logs/migrations.log
- No rollback (uses backups for manual recovery)

Usage:
    from src.migration_manager import run_migrations
    run_migrations()  # Call at app startup, before loading config/settings
"""

import json
import logging
import sys
from .utils.logger import get_logger, get_log_file

logger = get_logger(__name__)
from datetime import datetime
from pathlib import Path
from typing import List

try:
    from PySide6.QtCore import QSettings
    HAS_QT = True
except ImportError:
    HAS_QT = False
    QSettings = None


class MigrationManager:
    """
    Manages database migrations for QSettings and config.yaml.

    Automatically detects current version and runs pending migrations.
    """

    CURRENT_VERSION = "2.9.91"

    def __init__(self):
        self.logger = self._setup_logging()
        self.migrations_dir = Path(__file__).parent / "migrations"

    def _setup_logging(self) -> logging.Logger:
        """Setup migrations logger."""
        log_dir = get_log_file().parent
        log_file = log_dir / "migrations.log"

        logger = logging.getLogger("migrations")
        logger.setLevel(logging.INFO)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # RotatingFileHandler (5MB, 3 backups)
        from logging.handlers import RotatingFileHandler
        try:
            handler = RotatingFileHandler(
                log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
            logger.addHandler(handler)
        except OSError:
            # Diagnostic file availability must not prevent migrations.
            pass

        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(console)

        return logger

    def get_current_version(self) -> str:
        """
        Get current app version from QSettings or config.yaml.

        Returns:
            Version string (e.g., "2.9.90") or "0.0.0" if not found.
        """
        # Try QSettings first
        if HAS_QT:
            try:
                settings = QSettings("Clarify", "ClarifyApp")
                version = settings.value("app/version", None)
                if version:
                    return str(version)
            except Exception as e:
                self.logger.warning("Failed to read version from QSettings: %s", e)

        # Try config.yaml
        try:
            from src.config_manager import get_config
            config = get_config()
            version = config.get("app.version", None)
            if version:
                return str(version)
        except Exception as e:
            self.logger.warning("Failed to read version from config.yaml: %s", e)

        # Default: first run or very old version
        return "0.0.0"

    def set_current_version(self, version: str):
        """Save current version to QSettings and config.yaml."""
        # QSettings
        if HAS_QT:
            try:
                settings = QSettings("Clarify", "ClarifyApp")
                settings.setValue("app/version", version)
                settings.sync()
            except Exception as e:
                self.logger.error("Failed to save version to QSettings: %s", e)

        # config.yaml
        try:
            from src.config_manager import get_config
            config = get_config()
            config.set("app.version", version, save=True)
        except Exception as e:
            self.logger.error("Failed to save version to config.yaml: %s", e)

    def discover_migrations(self) -> List:
        """
        Discover all migration classes in migrations/ folder.

        Returns:
            List of Migration instances, sorted by version.
        """
        migrations = []

        if not self.migrations_dir.exists():
            return migrations

        # Import all v*.py files
        for migration_file in sorted(self.migrations_dir.glob("v*.py")):
            try:
                module_name = migration_file.stem
                spec = __import__(f"src.migrations.{module_name}", fromlist=["*"])

                # Find Migration subclass
                for attr_name in dir(spec):
                    attr = getattr(spec, attr_name)
                    if (isinstance(attr, type) and
                        hasattr(attr, "version") and
                        attr_name.startswith("Migration")):
                        migrations.append(attr())
            except Exception as e:
                self.logger.error("Failed to load migration {migration_file}: %s", e)

        # Sort by version
        migrations.sort(key=lambda m: self._version_tuple(m.version))
        return migrations

    def _version_tuple(self, version: str) -> tuple:
        """Convert version string to tuple for comparison."""
        try:
            return tuple(map(int, version.split(".")))
        except (ValueError, AttributeError):
            return (0, 0, 0)

    def backup_before_migration(self):
        """Create backups before running migrations."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Backup QSettings
        if HAS_QT:
            try:
                settings = QSettings("Clarify", "ClarifyApp")
                backup_file = Path.home() / ".clarify" / f"qsettings_backup_{timestamp}.json"
                backup_file.parent.mkdir(parents=True, exist_ok=True)

                # Export all keys
                data = {}
                for key in settings.allKeys():
                    data[key] = settings.value(key)

                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

                self.logger.info("QSettings backed up to %s", backup_file)
            except Exception as e:
                self.logger.error("QSettings backup failed: %s", e)

        # config.yaml backup (handled by config_manager.py automatically)
        self.logger.info("config.yaml backup handled by ConfigManager")

    def run_pending_migrations(self) -> bool:
        """
        Run all pending migrations.

        Returns:
            True if all migrations succeeded, False otherwise.
        """
        current_version = self.get_current_version()
        self.logger.info("Current version: %s", current_version)

        migrations = self.discover_migrations()
        if not migrations:
            self.logger.info("No migrations found")
            return True

        pending = [
            m for m in migrations
            if self._version_tuple(m.version) > self._version_tuple(current_version)
        ]

        if not pending:
            self.logger.info("No pending migrations")
            return True

        self.logger.info("Found %s pending migrations", len(pending))

        # Backup before starting
        self.backup_before_migration()

        # Run each migration
        for migration in pending:
            try:
                self.logger.info("Running migration %s...", migration.version)

                # Migrate QSettings
                if HAS_QT and hasattr(migration, "migrate_qsettings"):
                    settings = QSettings("Clarify", "ClarifyApp")
                    success = migration.migrate_qsettings(settings)
                    if success:
                        settings.sync()
                        self.logger.info("  ✓ QSettings migrated")

                # Migrate config.yaml
                if hasattr(migration, "migrate_config"):
                    from src.config_manager import get_config
                    config = get_config()
                    config_dict = config.get_all()
                    new_config = migration.migrate_config(config_dict)
                    config.update(new_config, save=True)
                    self.logger.info("  ✓ config.yaml migrated")

                # Update version
                self.set_current_version(migration.version)
                self.logger.info("✓ Migration %s complete", migration.version)

            except Exception as e:
                self.logger.error("✗ Migration {migration.version} failed: %s", e)
                self.logger.error("Aborting migrations. Restore from backup if needed.")
                return False

        self.logger.info("All migrations complete. Current version: %s", self.CURRENT_VERSION)
        return True


def run_migrations() -> bool:
    """
    Run all pending migrations at app startup.

    Call this BEFORE loading config/settings in app.__init__().

    Returns:
        True if migrations succeeded, False otherwise.
    """
    try:
        manager = MigrationManager()
        return manager.run_pending_migrations()
    except Exception as e:
        logger.critical(f"Migration system failed: {e}")
        return False
