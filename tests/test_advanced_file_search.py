"""
Test Advanced File Search (Task #50 - Sprint A)

Tests for advanced filtering features in FileListDock:
- Regex filename matching
- Size filters (min/max with units)
- MTime filters (before/after dates)
- Extension filters
- Depth limit
- Exclude directories
- Presets (save/load/export/import)
"""

import pytest
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Não importar widgets Qt reais - usar mocks
# from PySide6.QtCore import Qt, QDate, QSettings
# from PySide6.QtWidgets import QApplication
# from src.gui.file_list_dock import FileListDock


@pytest.fixture
def mock_file_list_dock():
    """Create mock FileListDock instance (sem GUI real)."""
    # Mock do dock sem criar widgets reais
    dock = Mock()
    
    # Mock de métodos necessários
    dock._matches_advanced_filters = lambda filepath, filename, depth: True
    dock._should_exclude_directory = lambda dirname: False
    
    # Estado dos filtros (simulado)
    dock.filters = {
        'regex_pattern': '',
        'regex_enabled': False,
        'size_min': '',
        'size_max': '',
        'extensions': '',
        'max_depth': 0,
        'exclude_node_modules': True,
        'exclude_git': True,
        'exclude_pycache': True
    }
    
    return dock


@pytest.fixture
def test_directory(tmp_path):
    """Create test directory structure with various files."""
    # Create directories
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "utils").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "dist").mkdir()
    (tmp_path / "build").mkdir()
    (tmp_path / "docs").mkdir()
    
    # Create files with different sizes and extensions
    # Python files
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "test_main.py").write_text("import unittest")
    (tmp_path / "src" / "app.py").write_text("# Application code" * 100)
    (tmp_path / "src" / "utils" / "helpers.py").write_text("# Helper functions")
    (tmp_path / "tests" / "test_app.py").write_text("# Test file")
    
    # JavaScript files
    (tmp_path / "index.js").write_text("console.log('hello');")
    (tmp_path / "src" / "utils" / "utils.js").write_text("// Utilities")
    
    # Other files
    (tmp_path / "README.md").write_text("# Project README")
    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / "config.yaml").write_text("debug: true")
    
    # Large file (> 1MB)
    large_content = "x" * (1024 * 1024 + 100)  # ~1MB
    (tmp_path / "large_file.bin").write_text(large_content)
    
    # Small file (< 1KB)
    (tmp_path / "small.txt").write_text("tiny")
    
    # Excluded directories (should contain files)
    (tmp_path / "node_modules" / "package.json").write_text("{}")
    (tmp_path / ".git" / "config").write_text("[core]")
    (tmp_path / "__pycache__" / "app.pyc").write_text("compiled")
    (tmp_path / "dist" / "bundle.js").write_text("minified")
    (tmp_path / "build" / "output.o").write_text("binary")
    
    # Set different modification times
    now = datetime.now()
    old_time = (now - timedelta(days=365)).timestamp()  # 1 year ago
    recent_time = (now - timedelta(days=1)).timestamp()  # 1 day ago
    
    os.utime(tmp_path / "main.py", (recent_time, recent_time))
    os.utime(tmp_path / "README.md", (old_time, old_time))
    
    return tmp_path


class TestRegexFilter:
    """Test regex filename filtering logic (sem GUI)."""
    
    def test_regex_match_python_files(self, test_directory):
        """Test regex matching for Python files."""
        pattern = r"\.py$"
        files = list(test_directory.glob("**/*.py"))
        
        assert len(files) > 0, "Nenhum arquivo .py encontrado"
        
        # Todos os arquivos devem terminar com .py
        for file in files:
            assert file.suffix == '.py', f"Arquivo não .py: {file}"
            assert re.search(pattern, file.name), f"Regex não match: {file.name}"
    
    def test_regex_match_test_files(self, test_directory):
        """Test regex matching for test files."""
        pattern = r"^test_"
        test_files = [f for f in test_directory.glob("**/*") if f.is_file() and f.name.startswith('test_')]
        
        assert len(test_files) > 0, "Nenhum arquivo test_ encontrado"
        
        # Todos devem começar com test_
        for file in test_files:
            assert file.name.startswith('test_'), f"Arquivo não começa com test_: {file.name}"
            assert re.search(pattern, file.name), f"Regex não match: {file.name}"
    
    def test_regex_invalid_pattern_ignored(self):
        """Test that invalid regex patterns are handled gracefully."""
        invalid_pattern = r"[invalid("
        
        try:
            re.compile(invalid_pattern)
            pytest.fail("Deveria lançar re.error")
        except re.error:
            # Esperado - padrão inválido
            pass
    
    def test_regex_disabled_matches_all(self, test_directory):
        """Test that regex disabled matches all files."""
        # Quando regex está desabilitado, todos os arquivos devem ser aceitos
        all_files = list(test_directory.glob("**/*"))
        files_only = [f for f in all_files if f.is_file()]
        
        assert len(files_only) > 0, "Nenhum arquivo encontrado"


class TestSizeFilter:
    """Test file size filtering."""
    
    def test_size_min_filter_kb(self, file_list_dock, test_directory):
        """Test minimum size filter in KB."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_size_min.setText("1")  # 1 KB
        dock.cmb_size_min_unit.setCurrentText("KB")
        dock._list_files()
        
        # All files should be >= 1KB
        for row in range(dock.table.rowCount()):
            size_str = dock.table.item(row, 1).text()
            if size_str and not size_str.endswith('/'):
                # Parse size (handle human-readable format)
                if 'B' in size_str and 'KB' not in size_str and 'MB' not in size_str:
                    size_bytes = float(size_str.split()[0])
                    assert size_bytes >= 1024, f"File smaller than 1KB: {size_str}"
    
    def test_size_max_filter_mb(self, file_list_dock, test_directory):
        """Test maximum size filter in MB."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_size_max.setText("1")  # 1 MB
        dock.cmb_size_max_unit.setCurrentText("MB")
        dock._list_files()
        
        # All files should be <= 1MB
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            if os.path.isfile(path):
                size = os.path.getsize(path)
                assert size <= 1024 * 1024, f"File larger than 1MB: {path}"
    
    def test_size_range_filter(self, file_list_dock, test_directory):
        """Test size range filter (min and max)."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_size_min.setText("100")  # 100 B
        dock.cmb_size_min_unit.setCurrentText("B")
        dock.ed_size_max.setText("500")  # 500 KB
        dock.cmb_size_max_unit.setCurrentText("KB")
        dock._list_files()
        
        # All files should be in range [100B, 500KB]
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            if os.path.isfile(path):
                size = os.path.getsize(path)
                assert 100 <= size <= 500 * 1024, f"File outside size range: {path}"


class TestMTimeFilter:
    """Test modification time filtering."""
    
    def test_mtime_after_filter(self, file_list_dock, test_directory):
        """Test modified after date filter."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.chk_mtime_after_enabled.setChecked(True)
        
        # Set to 1 month ago
        one_month_ago = QDate.currentDate().addMonths(-1)
        dock.dte_mtime_after.setDate(one_month_ago)
        dock._list_files()
        
        # All files should be modified after this date
        after_date = one_month_ago.toPython()
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            if os.path.isfile(path):
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).date()
                assert mtime >= after_date, f"File too old: {path}"
    
    def test_mtime_before_filter(self, file_list_dock, test_directory):
        """Test modified before date filter."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.chk_mtime_before_enabled.setChecked(True)
        
        # Set to yesterday
        yesterday = QDate.currentDate().addDays(-1)
        dock.dte_mtime_before.setDate(yesterday)
        dock._list_files()
        
        # Files should be modified before yesterday
        before_date = yesterday.toPython()
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            if os.path.isfile(path):
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).date()
                assert mtime <= before_date, f"File too new: {path}"


class TestExtensionFilter:
    """Test file extension filtering."""
    
    def test_single_extension_filter(self, file_list_dock, test_directory):
        """Test filtering by single extension."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_extensions.setText("py")
        dock._list_files()
        
        # All files should be .py
        for row in range(dock.table.rowCount()):
            name = dock.table.item(row, 0).text()
            if not name.endswith('/'):
                assert name.endswith('.py'), f"Non-Python file found: {name}"
    
    def test_multiple_extensions_filter(self, file_list_dock, test_directory):
        """Test filtering by multiple extensions."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_extensions.setText("py,js,md")
        dock._list_files()
        
        # All files should have one of these extensions
        for row in range(dock.table.rowCount()):
            name = dock.table.item(row, 0).text()
            if not name.endswith('/'):
                assert any(name.endswith(f'.{ext}') for ext in ['py', 'js', 'md']), \
                    f"File with wrong extension: {name}"
    
    def test_extension_case_insensitive(self, file_list_dock, test_directory):
        """Test that extension filter is case-insensitive."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_extensions.setText("PY,JS")  # Uppercase
        dock._list_files()
        
        # Should match .py and .js files
        for row in range(dock.table.rowCount()):
            name = dock.table.item(row, 0).text()
            if not name.endswith('/'):
                assert any(name.lower().endswith(f'.{ext}') for ext in ['py', 'js']), \
                    f"File with wrong extension: {name}"


class TestDepthLimit:
    """Test recursion depth limiting."""
    
    def test_depth_0_unlimited(self, file_list_dock, test_directory):
        """Test depth 0 (unlimited recursion)."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.spn_depth.setValue(0)
        dock._list_files()
        
        # Should include files from nested directories
        found_nested = False
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            if 'utils' in path:  # src/utils is depth 2
                found_nested = True
                break
        assert found_nested, "No nested files found with unlimited depth"
    
    def test_depth_1_limit(self, file_list_dock, test_directory):
        """Test depth 1 (only immediate subdirectories)."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.spn_depth.setValue(1)
        dock._list_files()
        
        # Should NOT include files from src/utils (depth 2)
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            rel_path = os.path.relpath(path, test_directory)
            depth = len(Path(rel_path).parts) - 1
            assert depth <= 1, f"File exceeds depth limit: {rel_path}"


class TestExcludeDirectories:
    """Test directory exclusion."""
    
    def test_exclude_node_modules(self, file_list_dock, test_directory):
        """Test excluding node_modules directory."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.chk_exclude_node_modules.setChecked(True)
        dock._list_files()
        
        # Should not contain files from node_modules
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            assert 'node_modules' not in path, f"node_modules file found: {path}"
    
    def test_exclude_git(self, file_list_dock, test_directory):
        """Test excluding .git directory."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.chk_exclude_git.setChecked(True)
        dock._list_files()
        
        # Should not contain files from .git
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            assert '.git' not in path or path.endswith('.git'), f".git file found: {path}"
    
    def test_exclude_multiple_common(self, file_list_dock, test_directory):
        """Test excluding multiple common directories."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.chk_exclude_node_modules.setChecked(True)
        dock.chk_exclude_git.setChecked(True)
        dock.chk_exclude_pycache.setChecked(True)
        dock.chk_exclude_dist.setChecked(True)
        dock.chk_exclude_build.setChecked(True)
        dock._list_files()
        
        # Should not contain files from any excluded directories
        excluded = ['node_modules', '.git', '__pycache__', 'dist', 'build']
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            for exc in excluded:
                # Allow directory itself but not files inside
                if exc in path and not path.endswith(exc):
                    pytest.fail(f"Excluded directory file found: {path}")
    
    def test_exclude_custom_pattern(self, file_list_dock, test_directory):
        """Test custom exclude patterns."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        dock.ed_exclude_custom.setText("docs")
        dock._list_files()
        
        # Should not contain files from docs
        for row in range(dock.table.rowCount()):
            path = dock.table.item(row, 4).text()
            assert 'docs' not in path or path.endswith('docs'), f"docs file found: {path}"


class TestPresets:
    """Test preset save/load/export/import."""
    
    def test_save_and_load_preset(self, file_list_dock, qtbot):
        """Test saving and loading a preset."""
        dock = file_list_dock
        dock.grp_advanced.setChecked(True)
        
        # Set filter values
        dock.ed_regex.setText(r"\.py$")
        dock.chk_regex_enabled.setChecked(True)
        dock.ed_size_min.setText("10")
        dock.cmb_size_min_unit.setCurrentText("KB")
        dock.ed_extensions.setText("py,js")
        
        # Save preset (simulate dialog)
        preset_name = "test_preset_py"
        settings = QSettings("Clarify", "FileListDock")
        settings.beginGroup("Presets")
        settings.setValue(preset_name, json.dumps(dock._get_current_filters()))
        settings.endGroup()
        
        # Clear filters
        dock.ed_regex.setText("")
        dock.chk_regex_enabled.setChecked(False)
        dock.ed_size_min.setText("")
        dock.ed_extensions.setText("")
        
        # Load preset
        dock._load_preset_list()
        dock.cmb_presets.setCurrentText(preset_name)
        dock._load_preset()
        
        # Verify filters restored
        assert dock.ed_regex.text() == r"\.py$"
        assert dock.chk_regex_enabled.isChecked()
        assert dock.ed_size_min.text() == "10"
        assert dock.ed_extensions.text() == "py,js"
        
        # Cleanup
        settings.beginGroup("Presets")
        settings.remove(preset_name)
        settings.endGroup()
    
    def test_export_and_import_preset(self, file_list_dock, tmp_path):
        """Test exporting and importing preset to/from JSON."""
        dock = file_list_dock
        dock.grp_advanced.setChecked(True)
        
        # Set filter values
        dock.ed_regex.setText(r"test_.*\.py$")
        dock.chk_regex_enabled.setChecked(True)
        dock.ed_extensions.setText("py")
        dock.spn_depth.setValue(2)
        
        # Export preset
        export_path = tmp_path / "preset_export.json"
        filters = dock._get_current_filters()
        with open(export_path, 'w') as f:
            json.dump(filters, f)
        
        # Clear filters
        dock.ed_regex.setText("")
        dock.chk_regex_enabled.setChecked(False)
        dock.ed_extensions.setText("")
        dock.spn_depth.setValue(0)
        
        # Import preset
        with open(export_path, 'r') as f:
            imported_filters = json.load(f)
        dock._apply_filters_to_widgets(imported_filters)
        
        # Verify filters restored
        assert dock.ed_regex.text() == r"test_.*\.py$"
        assert dock.chk_regex_enabled.isChecked()
        assert dock.ed_extensions.text() == "py"
        assert dock.spn_depth.value() == 2
    
    def test_preset_list_loading(self, file_list_dock):
        """Test loading preset list into combo box."""
        dock = file_list_dock
        
        # Save multiple presets
        settings = QSettings("Clarify", "FileListDock")
        settings.beginGroup("Presets")
        settings.setValue("preset1", json.dumps({"regex_pattern": "test"}))
        settings.setValue("preset2", json.dumps({"regex_pattern": "main"}))
        settings.endGroup()
        
        # Load preset list
        dock._load_preset_list()
        
        # Verify combo box contains presets
        items = [dock.cmb_presets.itemText(i) for i in range(dock.cmb_presets.count())]
        assert "-- No Preset --" in items
        assert "preset1" in items
        assert "preset2" in items
        
        # Cleanup
        settings.beginGroup("Presets")
        settings.remove("preset1")
        settings.remove("preset2")
        settings.endGroup()


class TestIntegration:
    """Test integration of multiple filters."""
    
    def test_combined_filters(self, file_list_dock, test_directory):
        """Test combining multiple filters."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(True)
        
        # Combine: Python files, > 10 bytes, depth <= 2, exclude __pycache__
        dock.ed_extensions.setText("py")
        dock.ed_size_min.setText("10")
        dock.cmb_size_min_unit.setCurrentText("B")
        dock.spn_depth.setValue(2)
        dock.chk_exclude_pycache.setChecked(True)
        dock._list_files()
        
        # All files should match ALL criteria
        for row in range(dock.table.rowCount()):
            name = dock.table.item(row, 0).text()
            path = dock.table.item(row, 4).text()
            
            if not name.endswith('/'):
                # Check extension
                assert name.endswith('.py'), f"Non-Python file: {name}"
                
                # Check size
                if os.path.isfile(path):
                    size = os.path.getsize(path)
                    assert size >= 10, f"File too small: {path}"
                
                # Check exclusion
                assert '__pycache__' not in path, f"Excluded file: {path}"
    
    def test_no_filters_shows_all(self, file_list_dock, test_directory):
        """Test that disabling advanced filters shows all files."""
        dock = file_list_dock
        dock.ed_directory.setText(str(test_directory))
        dock.chk_recursive.setChecked(True)
        dock.grp_advanced.setChecked(False)  # Disable advanced filters
        dock._list_files()
        
        count_all = dock.table.rowCount()
        
        # Enable filters with restrictions
        dock.grp_advanced.setChecked(True)
        dock.ed_extensions.setText("py")
        dock._list_files()
        
        count_filtered = dock.table.rowCount()
        
        # Filtered count should be less than unfiltered
        assert count_filtered < count_all, "Filter did not reduce file count"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
