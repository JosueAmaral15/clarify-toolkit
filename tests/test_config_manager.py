"""
Tests for Configuration Manager - Sprint v2.9.60

Tests the ConfigManager class functionality.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Import ConfigManager
from src.config_manager import ConfigManager, get_config, reset_config_instance


class TestConfigManagerInit:
    """Test ConfigManager initialization."""
    
    def test_init_with_defaults(self, tmp_path):
        """Test initialization creates config with defaults."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        assert config.config_file == config_file
        assert config.get("app.theme") == "system"
        assert config.get("logging.level") == "INFO"
        assert config.get("editor.font_size") == 12
    
    def test_init_creates_file(self, tmp_path):
        """Test initialization creates config file."""
        config_file = tmp_path / "config.yaml"
        ConfigManager(str(config_file))
        
        assert config_file.exists()
        
        # Verify YAML content
        with open(config_file, "r") as f:
            content = yaml.safe_load(f)
        
        assert "app" in content
        assert "logging" in content
        assert "editor" in content
    
    def test_init_with_existing_file(self, tmp_path):
        """Test initialization loads existing config."""
        config_file = tmp_path / "config.yaml"
        
        # Create existing config
        existing = {"app": {"theme": "dark", "language": "pt-br"}}
        with open(config_file, "w") as f:
            yaml.dump(existing, f)
        
        config = ConfigManager(str(config_file))
        
        assert config.get("app.theme") == "dark"
        assert config.get("app.language") == "pt-br"
        # Should merge with defaults
        assert config.get("logging.level") == "INFO"


class TestConfigManagerGetSet:
    """Test get/set operations."""
    
    def test_get_existing_value(self, tmp_path):
        """Test getting existing value."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        assert config.get("app.theme") == "system"
    
    def test_get_nested_value(self, tmp_path):
        """Test getting nested value with dot notation."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        assert config.get("editor.font_size") == 12
    
    def test_get_with_default(self, tmp_path):
        """Test getting non-existent value with default."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        assert config.get("nonexistent.key", "default") == "default"
    
    def test_set_value(self, tmp_path):
        """Test setting value."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.set("app.theme", "dark", save=False)
        
        assert config.get("app.theme") == "dark"
    
    def test_set_nested_value(self, tmp_path):
        """Test setting nested value."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.set("editor.font_size", 16, save=False)
        
        assert config.get("editor.font_size") == 16
    
    def test_set_creates_intermediate_keys(self, tmp_path):
        """Test setting value creates intermediate keys."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.set("new.nested.key", "value", save=False)
        
        assert config.get("new.nested.key") == "value"


class TestConfigManagerUpdate:
    """Test bulk update operations."""
    
    def test_update_multiple_values(self, tmp_path):
        """Test updating multiple values at once."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.update({
            "app.theme": "dark",
            "editor.font_size": 14,
            "logging.level": "DEBUG"
        }, save=False)
        
        assert config.get("app.theme") == "dark"
        assert config.get("editor.font_size") == 14
        assert config.get("logging.level") == "DEBUG"


class TestConfigManagerSave:
    """Test save/load operations."""
    
    def test_save_creates_file(self, tmp_path):
        """Test save creates YAML file."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.set("app.theme", "dark", save=True)
        
        assert config_file.exists()
        
        # Verify saved content
        with open(config_file, "r") as f:
            content = yaml.safe_load(f)
        
        assert content["app"]["theme"] == "dark"
    
    def test_save_creates_backup(self, tmp_path):
        """Test save creates backup of existing file."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        # First save
        config.save()
        
        # Second save should create backup
        config.set("app.theme", "dark", save=True)
        
        # Check for backup files
        backups = list(config_file.parent.glob("*.yaml.bak"))
        assert len(backups) > 0
    
    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML falls back to defaults."""
        config_file = tmp_path / "config.yaml"
        
        # Create invalid YAML
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content: {\n")
        
        config = ConfigManager(str(config_file))
        
        # Should use defaults
        assert config.get("app.theme") == "system"
        
        # Should create backup of invalid file
        backups = list(config_file.parent.glob("*_invalid.yaml.bak"))
        assert len(backups) > 0


class TestConfigManagerMerge:
    """Test config merging."""
    
    def test_merge_with_defaults(self, tmp_path):
        """Test loaded config merges with defaults."""
        config_file = tmp_path / "config.yaml"
        
        # Create partial config
        partial = {"app": {"theme": "dark"}}
        with open(config_file, "w") as f:
            yaml.dump(partial, f)
        
        config = ConfigManager(str(config_file))
        
        # Should have custom value
        assert config.get("app.theme") == "dark"
        # Should have default values
        assert config.get("app.language") == "en"
        assert config.get("logging.level") == "INFO"


class TestConfigManagerReset:
    """Test reset functionality."""
    
    def test_reset_to_defaults(self, tmp_path):
        """Test resetting config to defaults."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        # Modify settings
        config.set("app.theme", "dark", save=False)
        config.set("editor.font_size", 16, save=False)
        
        # Reset
        config.reset_to_defaults()
        
        # Should be back to defaults
        assert config.get("app.theme") == "system"
        assert config.get("editor.font_size") == 12
    
    def test_reset_creates_backup(self, tmp_path):
        """Test reset creates backup before resetting."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.set("app.theme", "dark", save=True)
        config.reset_to_defaults()
        
        # Should create backup
        backups = list(config_file.parent.glob("*_before_reset.yaml.bak"))
        assert len(backups) > 0


class TestConfigManagerMigration:
    """Test migration from legacy formats."""
    
    def test_migrate_from_json(self, tmp_path):
        """Test migration from JSON format."""
        config_file = tmp_path / "config.yaml"
        json_file = tmp_path / ".clarify_settings.json"
        
        # Create old JSON settings
        old_settings = {
            "theme": "dark",
            "language": "pt-br",
            "max_recent_files": 20,
        }
        with open(json_file, "w") as f:
            json.dump(old_settings, f)
        
        # Mock Path.home() to return tmp_path
        with patch("src.config_manager.Path.home", return_value=tmp_path):
            config = ConfigManager(str(config_file))
        
        # Should migrate settings
        assert config.get("app.theme") == "dark"
        assert config.get("app.language") == "pt-br"
        assert config.get("app.max_recent_files") == 20
        
        # Should backup old file
        assert (tmp_path / ".clarify_settings.json.migrated").exists()


class TestConfigManagerGlobal:
    """Test global instance functions."""
    
    def test_get_config_singleton(self):
        """Test get_config returns singleton."""
        reset_config_instance()
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_reset_config_instance(self):
        """Test resetting global instance."""
        config1 = get_config()
        reset_config_instance()
        config2 = get_config()
        
        assert config1 is not config2


class TestConfigManagerEdgeCases:
    """Test edge cases."""
    
    def test_get_all(self, tmp_path):
        """Test getting entire configuration."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        all_config = config.get_all()
        
        assert isinstance(all_config, dict)
        assert "app" in all_config
        assert "logging" in all_config
        assert "editor" in all_config
    
    def test_set_with_empty_string(self, tmp_path):
        """Test setting value with empty string."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        config.set("app.language", "", save=False)
        
        assert config.get("app.language") == ""
    
    def test_get_with_none_default(self, tmp_path):
        """Test getting non-existent key with None default."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        assert config.get("nonexistent.key") is None


class TestConfigManagerIntegration:
    """Integration tests."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow: create, modify, save, reload."""
        config_file = tmp_path / "config.yaml"
        
        # Create and modify
        config1 = ConfigManager(str(config_file))
        config1.update({
            "app.theme": "dark",
            "editor.font_size": 16,
            "logging.level": "DEBUG"
        })
        
        # Reload from file
        config2 = ConfigManager(str(config_file))
        
        # Should have saved values
        assert config2.get("app.theme") == "dark"
        assert config2.get("editor.font_size") == 16
        assert config2.get("logging.level") == "DEBUG"
    
    def test_backup_limit(self, tmp_path):
        """Test backup file limit (max 5)."""
        config_file = tmp_path / "config.yaml"
        config = ConfigManager(str(config_file))
        
        # Create 10 saves (should generate backups)
        for i in range(10):
            config.set("app.theme", f"theme{i}", save=True)
        
        # Should have max 5 backups
        backups = list(config_file.parent.glob("*.yaml.bak"))
        assert len(backups) <= 5


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
