#!/usr/bin/env python3
"""
Migration Base Class - v2.9.91

Base class for all migrations.
"""

from abc import ABC
from typing import Any, Dict


class Migration(ABC):
    """
    Base class for database migrations.
    
    Subclass this to create version-specific migrations.
    """
    
    version: str = "0.0.0"  # Override in subclass
    
    def migrate_qsettings(self, settings) -> bool:
        """
        Migrate QSettings structure (optional).
        
        Args:
            settings: QSettings instance
        
        Returns:
            True if migration succeeded
        """
        return True  # No-op by default
    
    def migrate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate config.yaml structure (optional).
        
        Args:
            config: Config dictionary
        
        Returns:
            Modified config dictionary
        """
        return config  # No-op by default
    
    def __str__(self):
        return f"Migration {self.version}"
