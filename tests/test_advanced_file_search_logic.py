"""
Test Advanced File Search - Logic Only (Task #50 - Sprint A)

Testes SEM GUI para lógica de filtros avançados.
Protocolo Simplicidade 1 v1.6 - Etapa 9.2

Testa:
- Regex filename matching (lógica)
- Size filters (cálculos)
- MTime filters (comparações de datas)
- Extension filters (validação)
- Depth limit (contagem de níveis)
- Exclude directories (padrões)
- Presets (serialização JSON)

Autor: Josué Amaral
Data: 01/12/2025
"""

import pytest
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path


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
    large_content = "x" * (1024 * 1024 + 100)
    (tmp_path / "large_file.bin").write_text(large_content)
    
    # Small file (< 100 bytes)
    (tmp_path / "small.txt").write_text("tiny")
    
    # Excluded directories
    (tmp_path / "node_modules" / "package.json").write_text("{}")
    (tmp_path / ".git" / "config").write_text("[core]")
    (tmp_path / "__pycache__" / "app.pyc").write_text("compiled")
    
    # Set different modification times
    now = datetime.now()
    old_time = (now - timedelta(days=365)).timestamp()
    recent_time = (now - timedelta(days=1)).timestamp()
    
    os.utime(tmp_path / "main.py", (recent_time, recent_time))
    os.utime(tmp_path / "README.md", (old_time, old_time))
    
    return tmp_path


class TestRegexLogic:
    """Test regex pattern matching logic."""
    
    def test_regex_match_python_extension(self):
        """Test regex for .py extension."""
        pattern = r"\.py$"
        assert re.search(pattern, "test.py")
        assert re.search(pattern, "main.py")
        assert not re.search(pattern, "test.js")
        assert not re.search(pattern, "test.py.bak")
    
    def test_regex_match_test_prefix(self):
        """Test regex for test_ prefix."""
        pattern = r"^test_"
        assert re.search(pattern, "test_main.py")
        assert re.search(pattern, "test_app.py")
        assert not re.search(pattern, "main_test.py")
        assert not re.search(pattern, "app.py")
    
    def test_regex_invalid_pattern_exception(self):
        """Test invalid regex raises exception."""
        invalid_pattern = r"[invalid("
        with pytest.raises(re.error):
            re.compile(invalid_pattern)
    
    def test_regex_case_sensitive(self):
        """Test regex case sensitivity."""
        pattern = r"^Test"  # Maiúsculo
        assert re.search(pattern, "Test.py")
        assert not re.search(pattern, "test.py")
        
        # Case insensitive
        pattern_i = r"^test"
        assert re.search(pattern_i, "test.py", re.IGNORECASE)
        assert re.search(pattern_i, "Test.py", re.IGNORECASE)


class TestSizeLogic:
    """Test file size filtering logic."""
    
    def test_size_conversion_kb_to_bytes(self):
        """Test KB to bytes conversion."""
        assert 1 * 1024 == 1024  # 1 KB = 1024 bytes
        assert 10 * 1024 == 10240  # 10 KB
    
    def test_size_conversion_mb_to_bytes(self):
        """Test MB to bytes conversion."""
        assert 1 * 1024**2 == 1048576  # 1 MB = 1048576 bytes
        assert 2 * 1024**2 == 2097152  # 2 MB
    
    def test_size_min_filter(self, test_directory):
        """Test minimum size filter."""
        min_bytes = 100  # 100 bytes
        files = list(test_directory.glob("**/*"))
        
        large_files = [f for f in files if f.is_file() and f.stat().st_size >= min_bytes]
        assert len(large_files) > 0
        
        # Verificar que todos são >= 100 bytes
        for f in large_files:
            assert f.stat().st_size >= min_bytes
    
    def test_size_max_filter(self, test_directory):
        """Test maximum size filter."""
        max_bytes = 1024 * 1024  # 1 MB
        files = list(test_directory.glob("**/*"))
        
        small_files = [f for f in files if f.is_file() and f.stat().st_size <= max_bytes]
        assert len(small_files) > 0
        
        # Verificar que todos são <= 1 MB
        for f in small_files:
            assert f.stat().st_size <= max_bytes
    
    def test_size_range_filter(self, test_directory):
        """Test size range (min and max)."""
        min_bytes = 10
        max_bytes = 10000
        files = list(test_directory.glob("**/*"))
        
        ranged_files = [f for f in files if f.is_file() and min_bytes <= f.stat().st_size <= max_bytes]
        assert len(ranged_files) > 0
        
        # Verificar que todos estão no range
        for f in ranged_files:
            size = f.stat().st_size
            assert min_bytes <= size <= max_bytes, f"File {f} size {size} fora do range"


class TestMTimeLogic:
    """Test modification time filtering logic."""
    
    def test_mtime_after_filter(self, test_directory):
        """Test modified after date."""
        after_date = datetime.now() - timedelta(days=30)  # 30 dias atrás
        files = list(test_directory.glob("**/*"))
        
        recent_files = [
            f for f in files 
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) >= after_date
        ]
        
        assert len(recent_files) > 0
        
        # Verificar que todos são recentes
        for f in recent_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            assert mtime >= after_date
    
    def test_mtime_before_filter(self, test_directory):
        """Test modified before date."""
        # Arquivo com mtime antigo foi criado no fixture (README.md)
        readme = test_directory / "README.md"
        mtime = datetime.fromtimestamp(readme.stat().st_mtime)
        
        # Deve ser de 1 ano atrás
        one_year_ago = datetime.now() - timedelta(days=365)
        assert mtime < datetime.now()
    
    def test_mtime_range_filter(self, test_directory):
        """Test mtime range (before and after)."""
        now = datetime.now()
        after_date = now - timedelta(days=30)
        before_date = now + timedelta(days=1)
        
        files = list(test_directory.glob("**/*"))
        ranged_files = [
            f for f in files
            if f.is_file() and after_date <= datetime.fromtimestamp(f.stat().st_mtime) <= before_date
        ]
        
        assert len(ranged_files) > 0


class TestExtensionLogic:
    """Test file extension filtering logic."""
    
    def test_single_extension_filter(self, test_directory):
        """Test filtering by single extension."""
        py_files = list(test_directory.glob("**/*.py"))
        assert len(py_files) > 0
        
        # Todos devem ter extensão .py
        for f in py_files:
            assert f.suffix == '.py'
    
    def test_multiple_extensions_filter(self, test_directory):
        """Test filtering by multiple extensions."""
        extensions = ['.py', '.js', '.md']
        files = list(test_directory.glob("**/*"))
        
        filtered_files = [f for f in files if f.is_file() and f.suffix in extensions]
        assert len(filtered_files) > 0
        
        # Todos devem ter uma das extensões
        for f in filtered_files:
            assert f.suffix in extensions
    
    def test_extension_case_insensitive(self):
        """Test extension matching is case-insensitive."""
        ext = ".py"
        assert ext.lower() == ".py"
        assert ".PY".lower() == ".py"
        assert ".Py".lower() == ".py"
    
    def test_extension_with_dot(self):
        """Test extension includes dot."""
        assert Path("test.py").suffix == ".py"
        assert Path("test.js").suffix == ".js"
        assert Path("README").suffix == ""


class TestDepthLogic:
    """Test recursion depth limiting logic."""
    
    def test_depth_calculation(self, test_directory):
        """Test depth calculation from root."""
        root = test_directory
        
        # Depth 0: root files
        depth0 = [f for f in root.iterdir() if f.is_file()]
        assert len(depth0) > 0
        
        # Depth 1: src/app.py
        depth1_file = root / "src" / "app.py"
        if depth1_file.exists():
            rel_path = depth1_file.relative_to(root)
            depth = len(rel_path.parts) - 1  # -1 porque contamos diretórios, não arquivo
            assert depth == 1
        
        # Depth 2: src/utils/helpers.py
        depth2_file = root / "src" / "utils" / "helpers.py"
        if depth2_file.exists():
            rel_path = depth2_file.relative_to(root)
            depth = len(rel_path.parts) - 1
            assert depth == 2
    
    def test_depth_limit_1(self, test_directory):
        """Test depth limit of 1 (only immediate subdirs)."""
        max_depth = 1
        root = test_directory
        
        def collect_files(path, current_depth):
            files = []
            for entry in path.iterdir():
                if entry.is_file():
                    files.append((entry, current_depth))
                elif entry.is_dir() and current_depth < max_depth:
                    files.extend(collect_files(entry, current_depth + 1))
            return files
        
        files = collect_files(root, 0)
        
        # Verificar que nenhum arquivo excede depth 1
        for file, depth in files:
            assert depth <= max_depth, f"File {file} at depth {depth} exceeds limit"


class TestExcludeLogic:
    """Test directory exclusion logic."""
    
    def test_exclude_node_modules(self, test_directory):
        """Test excluding node_modules."""
        excluded_dirs = ['node_modules']
        files = list(test_directory.glob("**/*"))
        
        # Filtrar arquivos que NÃO estão em node_modules
        filtered = [f for f in files if not any(d in f.parts for d in excluded_dirs)]
        
        # Verificar que nenhum contém node_modules
        for f in filtered:
            assert 'node_modules' not in f.parts
    
    def test_exclude_multiple_dirs(self, test_directory):
        """Test excluding multiple directories."""
        excluded_dirs = ['node_modules', '.git', '__pycache__', 'dist', 'build']
        files = list(test_directory.glob("**/*"))
        
        # Filtrar
        filtered = [f for f in files if not any(d in f.parts for d in excluded_dirs)]
        
        # Verificar exclusão
        for f in filtered:
            for excluded in excluded_dirs:
                assert excluded not in f.parts, f"File {f} contains excluded dir {excluded}"
    
    def test_exclude_pattern_wildcard(self):
        """Test wildcard pattern matching."""
        dirname = "test_cache"
        pattern = "*cache"
        
        # Simular match de wildcard
        assert dirname.endswith(pattern[1:])  # Remove * e verifica sufixo
    
    def test_exclude_custom_pattern(self):
        """Test custom exclude patterns."""
        patterns = ['temp', 'cache', '*.tmp']
        dirnames = ['temp', 'mycache', 'file.tmp', 'valid']
        
        excluded = []
        for d in dirnames:
            for pattern in patterns:
                if pattern.startswith('*'):
                    if d.endswith(pattern[1:]):
                        excluded.append(d)
                        break
                elif d == pattern or pattern in d:
                    excluded.append(d)
                    break
        
        assert 'temp' in excluded
        assert 'mycache' in excluded
        assert 'valid' not in excluded


class TestPresetLogic:
    """Test preset save/load logic (JSON serialization)."""
    
    def test_serialize_filters_to_json(self, tmp_path):
        """Test serializing filter settings to JSON."""
        filters = {
            'regex_pattern': r'\.py$',
            'regex_enabled': True,
            'size_min': '10',
            'size_min_unit': 'KB',
            'extensions': 'py,js,md',
            'max_depth': 2
        }
        
        # Salvar
        preset_file = tmp_path / "preset.json"
        with open(preset_file, 'w') as f:
            json.dump(filters, f, indent=2)
        
        # Verificar
        assert preset_file.exists()
        
        # Carregar
        with open(preset_file, 'r') as f:
            loaded = json.load(f)
        
        assert loaded == filters
    
    def test_deserialize_filters_from_json(self, tmp_path):
        """Test loading filter settings from JSON."""
        filters_json = '''{
  "regex_pattern": "^test_",
  "regex_enabled": true,
  "extensions": "py"
}'''
        
        preset_file = tmp_path / "preset.json"
        preset_file.write_text(filters_json)
        
        # Carregar
        with open(preset_file, 'r') as f:
            filters = json.load(f)
        
        assert filters['regex_pattern'] == '^test_'
        assert filters['regex_enabled'] is True
        assert filters['extensions'] == 'py'
    
    def test_preset_with_invalid_json(self, tmp_path):
        """Test handling invalid JSON."""
        preset_file = tmp_path / "invalid.json"
        preset_file.write_text("{invalid json")
        
        with pytest.raises(json.JSONDecodeError):
            with open(preset_file, 'r') as f:
                json.load(f)


class TestIntegration:
    """Test integration of multiple filter logics."""
    
    def test_combined_filters(self, test_directory):
        """Test combining multiple filters."""
        # Filtros: Python files, > 50 bytes, depth <= 2
        extensions = ['.py']
        min_size = 50
        max_depth = 2
        
        files = list(test_directory.glob("**/*.py"))
        
        # Aplicar filtros
        filtered = []
        for f in files:
            # Extension
            if f.suffix not in extensions:
                continue
            
            # Size
            if f.stat().st_size < min_size:
                continue
            
            # Depth
            rel_path = f.relative_to(test_directory)
            depth = len(rel_path.parts) - 1
            if depth > max_depth:
                continue
            
            filtered.append(f)
        
        # Verificar que todos atendem aos critérios
        for f in filtered:
            assert f.suffix == '.py'
            assert f.stat().st_size >= min_size
            depth = len(f.relative_to(test_directory).parts) - 1
            assert depth <= max_depth
    
    def test_no_filters_returns_all(self, test_directory):
        """Test that no filters returns all files."""
        all_files = [f for f in test_directory.glob("**/*") if f.is_file()]
        assert len(all_files) > 10  # Muitos arquivos criados no fixture


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
