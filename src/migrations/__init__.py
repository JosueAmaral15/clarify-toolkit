#!/usr/bin/env python3
"""
Migration Base Class - v2.9.91

Base class for all migrations. Subclass this to create version-specific migrations.

Example:
    from src.migrations.base import Migration
    
    class MigrationV2_9_91(Migration):
        version = "2.9.91"
        
        def migrate_qsettings(self, settings):
            # Migrate QSettings keys
            old_val = settings.value("old_key")
            settings.setValue("new_key", old_val)
            settings.remove("old_key")
            return True
        
        def migrate_config(self, config):
            # Migrate config.yaml structure
            if "old_section" in config:
                config["new_section"] = config.pop("old_section")
            return config
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class Migration(ABC):
    """
    Base class for database migrations.
    
    Each migration must:
    1. Set version attribute (e.g., "2.9.91")
    2. Implement migrate_qsettings() and/or migrate_config()
    """
    
    version: str = "0.0.0"  # Override in subclass
    
    @abstractmethod
    def migrate_qsettings(self, settings) -> bool:
        """
        Migrate QSettings structure.
        
        Args:
            settings: QSettings instance
        
        Returns:
            True if migration succeeded, False otherwise
        
        Example:
            # Rename key
            old_val = settings.value("old/path")
            settings.setValue("new/path", old_val)
            settings.remove("old/path")
            return True
        """
        pass
    
    @abstractmethod
    def migrate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate config.yaml structure.
        
        Args:
            config: Config dictionary (from config.yaml)
        
        Returns:
            Modified config dictionary
        
        Example:
            # Rename section
            if "old_section" in config:
                config["new_section"] = config.pop("old_section")
            return config
        """
        pass
    
    def __str__(self):
        return f"Migration {self.version}"
    
    def __repr__(self):
        return f"<Migration version={self.version}>"
