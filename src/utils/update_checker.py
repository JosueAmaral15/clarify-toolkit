"""
Update Checker Module

Checks for new versions of Clarify on GitHub Releases.
Caches results to avoid excessive API calls.

Author: Josué Amaral
Date: 2025-12-23
Version: 2.9.109
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from PySide6.QtCore import QSettings  # pylint: disable=no-name-in-module  # Qt dynamic


class UpdateChecker:
    """Checks for application updates via GitHub Releases API."""

    GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"
    CACHE_DURATION_HOURS = 24

    def __init__(
        self,
        current_version: str = "2.9.109",
        github_repo: str = "josuearaujo/clarify",
        cache_dir: Optional[str] = None
    ):
        """
        Initialize update checker.

        Args:
            current_version: Current application version (semver format)
            github_repo: GitHub repository in format 'owner/repo'
            cache_dir: Directory for cache file (default: ~/.cache/clarify/)
        """
        self.current_version = current_version
        self.github_repo = github_repo

        # Parse owner/repo
        parts = github_repo.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repo format: {github_repo}. Expected 'owner/repo'")
        self.owner, self.repo = parts

        # Setup cache directory
        if cache_dir is None:
            home = Path.home()
            self.cache_dir = home / ".cache" / "clarify"
        else:
            self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "update_check.json"

        # QSettings for preferences
        self.settings = QSettings("Clarify", "Clarify")

    def is_check_enabled(self) -> bool:
        """Check if automatic update checking is enabled."""
        return self.settings.value("update_checker/enabled", True, type=bool)

    def get_skipped_versions(self) -> list:
        """Get list of versions user chose to skip."""
        skipped = self.settings.value("update_checker/skipped_versions", [], type=list)
        return skipped if skipped else []

    def skip_version(self, version: str):
        """Mark a version as skipped."""
        skipped = self.get_skipped_versions()
        if version not in skipped:
            skipped.append(version)
            self.settings.setValue("update_checker/skipped_versions", skipped)

    def clear_skipped_versions(self):
        """Clear all skipped versions."""
        self.settings.remove("update_checker/skipped_versions")

    def _read_cache(self) -> Optional[Dict[str, Any]]:
        """
        Read cached update check result.

        Returns:
            Cached data if valid and not expired, None otherwise
        """
        if not self.cache_file.exists():
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            # Check expiration
            cached_time = datetime.fromisoformat(cache.get("timestamp", ""))
            expiry = cached_time + timedelta(hours=self.CACHE_DURATION_HOURS)

            if datetime.now() > expiry:
                return None  # Expired

            return cache
        except (json.JSONDecodeError, ValueError, KeyError):
            # Invalid cache, ignore
            return None

    def _write_cache(self, data: Dict[str, Any]):
        """
        Write update check result to cache.

        Args:
            data: Data to cache
        """
        cache = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except Exception:  # pylint: disable=broad-exception-caught  # Cache write robustness
            # Fail silently on cache write errors
            pass

    # pylint: disable=too-many-return-statements  # Update check requires multiple validation paths
    def check_for_updates(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Check for updates on GitHub Releases.

        Args:
            use_cache: Whether to use cached results (default True)

        Returns:
            Dict with keys:
                - success: bool (True if check succeeded)
                - update_available: bool (True if newer version exists)
                - latest_version: str (latest version number)
                - current_version: str (current version)
                - download_url: str (URL to download page)
                - release_notes: str (changelog excerpt)
                - error: str (error message if success=False)
        """
        # Check cache first
        if use_cache:
            cached = self._read_cache()
            if cached:
                return cached.get("data", {})

        # Check if requests is available
        if not REQUESTS_AVAILABLE:
            return {
                "success": False,
                "error": "requests library not installed. Install with: pip install requests",
                "update_available": False,
                "current_version": self.current_version
            }

        # Check if checking is enabled
        if not self.is_check_enabled():
            return {
                "success": False,
                "error": "Update checking is disabled in settings",
                "update_available": False,
                "current_version": self.current_version
            }

        # Fetch from GitHub API
        try:
            url = self.GITHUB_API_URL.format(owner=self.owner, repo=self.repo)
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            release = response.json()

            # Parse version (remove 'v' prefix if present)
            latest_version = release.get("tag_name", "").lstrip("v")

            # Compare versions
            update_available = self._is_newer_version(latest_version, self.current_version)

            # Check if this version is skipped
            if latest_version in self.get_skipped_versions():
                update_available = False

            # Build result
            result = {
                "success": True,
                "update_available": update_available,
                "latest_version": latest_version,
                "current_version": self.current_version,
                "download_url": release.get("html_url", ""),
                "release_notes": release.get("body", "")[:500],  # First 500 chars
                "published_at": release.get("published_at", ""),
                "error": None
            }

            # Cache result
            self._write_cache(result)

            return result

        except requests.Timeout:
            return {
                "success": False,
                "error": "Connection timeout. Check your internet connection.",
                "update_available": False,
                "current_version": self.current_version
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "update_available": False,
                "current_version": self.current_version
            }
        except Exception as e:  # pylint: disable=broad-exception-caught  # Update check robustness
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "update_available": False,
                "current_version": self.current_version
            }

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        Compare semantic versions.

        Args:
            latest: Latest version string (e.g., "2.9.110")
            current: Current version string (e.g., "2.9.109")

        Returns:
            True if latest > current
        """
        try:
            # Parse versions as tuples of ints
            latest_parts = tuple(int(x) for x in latest.split("."))
            current_parts = tuple(int(x) for x in current.split("."))

            return latest_parts > current_parts
        except (ValueError, AttributeError):
            # Invalid version format, assume no update
            return False

    def clear_cache(self):
        """Delete cache file."""
        if self.cache_file.exists():
            self.cache_file.unlink()


# Singleton instance
_update_checker_instance: Optional[UpdateChecker] = None


def get_update_checker(
    current_version: str = "2.9.109",
    github_repo: str = "josuearaujo/clarify"
) -> UpdateChecker:
    """
    Get singleton UpdateChecker instance.

    Args:
        current_version: Current app version
        github_repo: GitHub repository

    Returns:
        UpdateChecker singleton
    """
    global _update_checker_instance  # pylint: disable=global-statement  # Singleton pattern

    if _update_checker_instance is None:
        _update_checker_instance = UpdateChecker(
            current_version=current_version,
            github_repo=github_repo
        )

    return _update_checker_instance
