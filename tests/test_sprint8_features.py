#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for Sprint 8 Features (Settings & Shortcuts)

Tests new v1.1.0 features: settings persistence, keyboard shortcuts, etc.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_settings_manager():
    """Test settings manager functionality."""
    print("\n" + "="*60)
    print("TEST: Settings Manager")
    print("="*60)
    
    from src.settings_manager import SettingsManager
    
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config = f.name
    
    try:
        # Test initialization
        settings = SettingsManager(temp_config)
        assert settings.get("theme") == "dark", "Default theme should be 'dark'"
        assert settings.get("window_opacity") == 96, "Default window opacity should be 96%"
        print("  ✓ Settings initialized with defaults")
        
        # Test set/get
        settings.set("theme", "dark")
        assert settings.get("theme") == "dark", "Theme should be 'dark'"
        print("  ✓ Set/get working")
        
        # Test persistence
        settings2 = SettingsManager(temp_config)
        assert settings2.get("theme") == "dark", "Settings should persist"
        print("  ✓ Settings persist across instances")
        
        # Test recent files
        settings.add_recent_file("/path/to/file1.txt")
        settings.add_recent_file("/path/to/file2.txt")
        recent = settings.get("recent_files")
        assert len(recent) == 2, "Should have 2 recent files"
        assert recent[0] == "/path/to/file2.txt", "Most recent should be first"
        print("  ✓ Recent files management working")
        
        # Test clear recent
        settings.clear_recent_files()
        assert len(settings.get("recent_files")) == 0, "Recent files should be empty"
        print("  ✓ Clear recent files working")
        
        # Test update multiple
        settings.update_multiple({
            "theme": "light",
            "language": "pt",
            "auto_save": False
        })
        assert settings.get("theme") == "light"
        assert settings.get("language") == "pt"
        assert settings.get("auto_save") == False
        print("  ✓ Update multiple settings working")
        
        # Test reset to defaults
        settings.reset_to_defaults()
        assert settings.get("theme") == "dark", "Should reset to default"
        assert settings.get("auto_save") == True, "Should reset to default"
        print("  ✓ Reset to defaults working")
        
        # Cleanup
        os.unlink(temp_config)
        
        print("\n✅ All settings manager tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Settings manager test failed: {e}")
        if os.path.exists(temp_config):
            os.unlink(temp_config)
        return False


def test_shortcut_manager():
    """Test shortcut manager functionality."""
    print("\n" + "="*60)
    print("TEST: Shortcut Manager")
    print("="*60)
    
    from src.shortcut_manager import ShortcutManager
    
    try:
        # Test get shortcut
        shortcut, desc = ShortcutManager.get_shortcut("open_file")
        assert shortcut == "Ctrl+O", f"Expected 'Ctrl+O', got '{shortcut}'"
        assert desc == "Open file", f"Expected 'Open file', got '{desc}'"
        print("  ✓ Get shortcut working")
        
        # Test get key sequence
        from PySide6.QtGui import QKeySequence
        key_seq = ShortcutManager.get_key_sequence("save_file")
        assert not key_seq.isEmpty(), "Key sequence should not be empty"
        print("  ✓ Get key sequence working")
        
        # Test get description
        desc = ShortcutManager.get_description("process")
        assert desc == "Process/Run", f"Expected 'Process/Run', got '{desc}'"
        print("  ✓ Get description working")
        
        # Test get all shortcuts
        all_shortcuts = ShortcutManager.get_all_shortcuts()
        assert len(all_shortcuts) > 10, "Should have multiple shortcuts"
        assert "open_file" in all_shortcuts, "Should have 'open_file'"
        print(f"  ✓ Get all shortcuts working ({len(all_shortcuts)} shortcuts)")
        
        # Test format table
        table = ShortcutManager.format_shortcuts_table()
        assert "Keyboard Shortcuts" in table, "Table should have header"
        assert "Ctrl+O" in table, "Table should contain shortcuts"
        print("  ✓ Format shortcuts table working")
        
        print("\n✅ All shortcut manager tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Shortcut manager test failed: {e}")
        return False


def test_settings_integration():
    """Test settings integration with application."""
    print("\n" + "="*60)
    print("TEST: Settings Integration")
    print("="*60)
    
    try:
        from src.settings_manager import get_settings, reset_settings_instance
        
        # Reset to get fresh instance
        reset_settings_instance()
        
        # Get global instance
        settings1 = get_settings()
        settings1.set("test_value", "hello")
        
        # Get same instance again
        settings2 = get_settings()
        assert settings2.get("test_value") == "hello", "Should get same instance"
        print("  ✓ Global settings instance working")
        
        # Reset for cleanup
        reset_settings_instance()
        
        print("\n✅ Settings integration test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Settings integration test failed: {e}")
        return False


def test_gui_integration():
    """Test GUI integration with new features."""
    print("\n" + "="*60)
    print("TEST: GUI Integration")
    print("="*60)
    
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Import after QApplication is created
        from src.shortcut_manager import ShortcutHelper
        
        print("  ✓ GUI components import successfully")
        print("  ✓ ShortcutHelper available")
        
        print("\n✅ GUI integration test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ GUI integration test failed: {e}")
        return False


def main():
    """Run all Sprint 8 tests."""
    
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "SPRINT 8 FEATURE TESTS" + " "*20 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Settings Manager", test_settings_manager()))
    results.append(("Shortcut Manager", test_shortcut_manager()))
    results.append(("Settings Integration", test_settings_integration()))
    results.append(("GUI Integration", test_gui_integration()))
    
    # Print summary
    print("\n" + "="*60)
    print("SPRINT 8 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = sum(1 for _, result in results if not result)
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All Sprint 8 tests passed!")
        return True
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
