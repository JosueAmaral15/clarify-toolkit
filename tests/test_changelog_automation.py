"""
Tests for Changelog Automation Script - Sprint v2.9.59

Tests the generate_changelog.py script functionality.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import functions from script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_changelog import (
    format_changelog_entry,
    generate_changelog_section,
    group_commits_by_type,
    parse_commit_message,
)


class TestParseCommitMessage:
    """Test commit message parsing."""
    
    def test_parse_conventional_commit_with_scope(self):
        """Test parsing conventional commit with scope."""
        message = "feat(logging): Add structured logging system"
        commit_type, scope, description, body = parse_commit_message(message)
        
        assert commit_type == "feat"
        assert scope == "logging"
        assert description == "Add structured logging system"
        assert body == ""
    
    def test_parse_conventional_commit_without_scope(self):
        """Test parsing conventional commit without scope."""
        message = "fix: Resolve save issue in editor"
        commit_type, scope, description, body = parse_commit_message(message)
        
        assert commit_type == "fix"
        assert scope == ""
        assert description == "Resolve save issue in editor"
        assert body == ""
    
    def test_parse_commit_with_body(self):
        """Test parsing commit with body."""
        message = "feat(tooltips): Add comprehensive tooltips\n\nAdded tooltips to:\n- Set Operations\n- JSON Editor"
        commit_type, scope, description, body = parse_commit_message(message)
        
        assert commit_type == "feat"
        assert scope == "tooltips"
        assert description == "Add comprehensive tooltips"
        assert "Added tooltips to:" in body
        assert "- Set Operations" in body
    
    def test_parse_non_conventional_commit(self):
        """Test parsing non-conventional commit."""
        message = "Updated README with installation instructions"
        commit_type, scope, description, body = parse_commit_message(message)
        
        assert commit_type == "chore"
        assert scope == ""
        assert description == "Updated README with installation instructions"
    
    def test_parse_commit_with_multiple_colons(self):
        """Test parsing commit with multiple colons."""
        message = "docs: Update API: add new endpoints"
        commit_type, scope, description, body = parse_commit_message(message)
        
        assert commit_type == "docs"
        assert "Update API: add new endpoints" in description


class TestGroupCommitsByType:
    """Test commit grouping."""
    
    def test_group_single_type(self):
        """Test grouping commits of single type."""
        commits = [
            {"hash": "abc1234", "subject": "feat(logging): Add logging", "body": "", "author": "Dev", "date": "2025-12-10"},
            {"hash": "def5678", "subject": "feat(editor): Add editor", "body": "", "author": "Dev", "date": "2025-12-10"},
        ]
        
        grouped = group_commits_by_type(commits)
        
        assert "feat" in grouped
        assert len(grouped["feat"]) == 2
        assert grouped["feat"][0]["scope"] == "logging"
        assert grouped["feat"][1]["scope"] == "editor"
    
    def test_group_multiple_types(self):
        """Test grouping commits of multiple types."""
        commits = [
            {"hash": "abc1234", "subject": "feat(logging): Add logging", "body": "", "author": "Dev", "date": "2025-12-10"},
            {"hash": "def5678", "subject": "fix(editor): Fix bug", "body": "", "author": "Dev", "date": "2025-12-10"},
            {"hash": "ghi9012", "subject": "docs: Update README", "body": "", "author": "Dev", "date": "2025-12-10"},
        ]
        
        grouped = group_commits_by_type(commits)
        
        assert len(grouped) == 3
        assert "feat" in grouped
        assert "fix" in grouped
        assert "docs" in grouped
        assert len(grouped["feat"]) == 1
        assert len(grouped["fix"]) == 1
        assert len(grouped["docs"]) == 1
    
    def test_group_empty_commits(self):
        """Test grouping empty commit list."""
        commits = []
        grouped = group_commits_by_type(commits)
        assert grouped == {}


class TestFormatChangelogEntry:
    """Test changelog entry formatting."""
    
    def test_format_entry_with_scope(self):
        """Test formatting entry with scope."""
        commit = {
            "hash": "abc1234",
            "scope": "logging",
            "description": "Add structured logging",
            "body": "",
            "author": "Dev",
            "date": "2025-12-10",
        }
        
        entry = format_changelog_entry(commit, include_body=False)
        
        assert "**logging**:" in entry
        assert "Add structured logging" in entry
        assert "(abc1234)" in entry
    
    def test_format_entry_without_scope(self):
        """Test formatting entry without scope."""
        commit = {
            "hash": "def5678",
            "scope": "",
            "description": "Update documentation",
            "body": "",
            "author": "Dev",
            "date": "2025-12-10",
        }
        
        entry = format_changelog_entry(commit, include_body=False)
        
        assert "**" not in entry
        assert "Update documentation" in entry
        assert "(def5678)" in entry
    
    def test_format_entry_with_body(self):
        """Test formatting entry with body."""
        commit = {
            "hash": "ghi9012",
            "scope": "tooltips",
            "description": "Add tooltips",
            "body": "Added tooltips to:\nSet Operations\nJSON Editor",
            "author": "Dev",
            "date": "2025-12-10",
        }
        
        entry = format_changelog_entry(commit, include_body=True)
        
        assert "**tooltips**:" in entry
        assert "Add tooltips" in entry
        assert "  * Added tooltips to:" in entry
        assert "  * Set Operations" in entry
    
    def test_format_entry_exclude_body(self):
        """Test formatting entry excluding body."""
        commit = {
            "hash": "ghi9012",
            "scope": "tooltips",
            "description": "Add tooltips",
            "body": "This should not appear",
            "author": "Dev",
            "date": "2025-12-10",
        }
        
        entry = format_changelog_entry(commit, include_body=False)
        
        assert "This should not appear" not in entry


class TestGenerateChangelogSection:
    """Test changelog section generation."""
    
    def test_generate_section_single_type(self):
        """Test generating section with single type."""
        grouped = {
            "feat": [
                {
                    "hash": "abc1234",
                    "scope": "logging",
                    "description": "Add logging system",
                    "body": "",
                    "author": "Dev",
                    "date": "2025-12-10",
                }
            ]
        }
        
        section = generate_changelog_section(grouped, "2.9.59")
        
        assert "## [2.9.59]" in section
        assert "### ✨ Features" in section
        assert "**logging**: Add logging system" in section
    
    def test_generate_section_multiple_types(self):
        """Test generating section with multiple types."""
        grouped = {
            "feat": [
                {
                    "hash": "abc1234",
                    "scope": "logging",
                    "description": "Add logging",
                    "body": "",
                    "author": "Dev",
                    "date": "2025-12-10",
                }
            ],
            "fix": [
                {
                    "hash": "def5678",
                    "scope": "editor",
                    "description": "Fix bug",
                    "body": "",
                    "author": "Dev",
                    "date": "2025-12-10",
                }
            ],
        }
        
        section = generate_changelog_section(grouped, "Unreleased")
        
        assert "## [Unreleased]" in section
        assert "### ✨ Features" in section
        assert "### 🐛 Bug Fixes" in section
    
    def test_generate_section_ordering(self):
        """Test section ordering (feat before fix)."""
        grouped = {
            "fix": [{"hash": "def5678", "scope": "", "description": "Fix", "body": "", "author": "Dev", "date": "2025-12-10"}],
            "feat": [{"hash": "abc1234", "scope": "", "description": "Feature", "body": "", "author": "Dev", "date": "2025-12-10"}],
        }
        
        section = generate_changelog_section(grouped)
        
        # Features should come before Bug Fixes
        feat_idx = section.index("### ✨ Features")
        fix_idx = section.index("### 🐛 Bug Fixes")
        assert feat_idx < fix_idx


class TestIntegration:
    """Integration tests for the script."""
    
    def test_script_help(self):
        """Test script help message."""
        result = subprocess.run(
            ["python", "scripts/generate_changelog.py", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0
        assert "Generate changelog from git commits" in result.stdout
    
    def test_script_execution_dry_run(self):
        """Test script can be imported and syntax is valid."""
        # This test just verifies the script can be imported without errors
        result = subprocess.run(
            ["python", "-m", "py_compile", "scripts/generate_changelog.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )
        
        assert result.returncode == 0, f"Syntax error: {result.stderr}"


class TestEdgeCases:
    """Test edge cases."""
    
    def test_parse_empty_message(self):
        """Test parsing empty commit message."""
        message = ""
        commit_type, scope, description, body = parse_commit_message(message)
        
        assert commit_type == "chore"
        assert scope == ""
        assert description == ""
    
    def test_format_entry_special_characters(self):
        """Test formatting entry with special characters."""
        commit = {
            "hash": "abc1234",
            "scope": "test & debug",
            "description": "Add tests with <special> chars",
            "body": "",
            "author": "Dev",
            "date": "2025-12-10",
        }
        
        entry = format_changelog_entry(commit)
        
        assert "test & debug" in entry
        assert "<special>" in entry
    
    def test_group_commits_with_unknown_type(self):
        """Test grouping commits with unknown type."""
        commits = [
            {"hash": "abc1234", "subject": "unknown: Some message", "body": "", "author": "Dev", "date": "2025-12-10"},
        ]
        
        grouped = group_commits_by_type(commits)
        
        assert "unknown" in grouped
        assert len(grouped["unknown"]) == 1


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
