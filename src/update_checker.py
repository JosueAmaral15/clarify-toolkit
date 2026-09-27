#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update Checker - GitHub Releases API Integration

Checks for new Clarify versions from GitHub Releases API with:
- Semantic version comparison
- 24-hour caching to avoid rate limits
- Offline-friendly error handling
- Non-blocking async operation

Author: Josué Amaral
Date: 2025-12-08
Version: 2.9.45
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError



from .utils.logger import get_logger

logger = get_logger(__name__)

class UpdateChecker:
    """
    Check for Clarify updates from GitHub Releases API.

    Features:
    - Compares current version with latest GitHub release
    - Caches results for 24 hours to avoid rate limits
    - Handles offline scenarios gracefully
    - Returns release info (version, URL, changelog)
    """

    GITHUB_API_URL = "https://api.github.com/repos/JosueAmaral15/clarify/releases/latest"
    CACHE_DURATION_HOURS = 24
    CACHE_FILE = Path.home() / ".cache" / "clarify" / "update_check.json"

    def __init__(self, current_version: str):
        """
        Initialize UpdateChecker.

        Args:
            current_version: Current installed version (e.g., "2.9.44")
        """
        self.current_version = current_version
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        try:
            self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # Updates can still be checked without a writable cache.

    def check_for_updates(self, force: bool = False) -> Tuple[bool, Optional[Dict]]:
        """
        Check if a new version is available.

        Args:
            force: If True, bypass cache and force API call

        Returns:
            Tuple of (has_update: bool, release_info: dict or None)

            release_info contains:
            - version: str (e.g., "2.9.45")
            - url: str (GitHub release page)
            - changelog_url: str (direct link to CHANGELOG.md)
            - published_at: str (ISO 8601 date)
            - body: str (release notes)

        Examples:
            >>> checker = UpdateChecker("2.9.44")
            >>> has_update, info = checker.check_for_updates()
            >>> if has_update:
            ...     logger.error(f"New version: {info['version']}")
        """
        # Check cache first (unless forced)
        if not force:
            cached = self._load_cache()
            if cached:
                return cached

        # Fetch from GitHub API
        try:
            release_info = self._fetch_latest_release()
            if not release_info:
                return False, None

            # Compare versions
            latest_version = release_info['version']
            has_update = self._is_newer_version(latest_version)

            # Cache result
            self._save_cache(has_update, release_info)

            return has_update, release_info

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Offline or network error - fail gracefully
            logger.error(f"Update check failed (offline?): {e}")
            return False, None

    def _fetch_latest_release(self) -> Optional[Dict]:
        """
        Fetch latest release from GitHub API.

        Returns:
            Dict with release info or None if failed
        """
        try:
            # Add User-Agent header (GitHub requires it)
            headers = {
                'User-Agent': 'Clarify-Update-Checker',
                'Accept': 'application/vnd.github.v3+json'
            }

            request = Request(self.GITHUB_API_URL, headers=headers)

            with urlopen(request, timeout=5) as response:
                if response.status != 200:
                    return None

                data = json.loads(response.read().decode('utf-8'))

                # Extract relevant info
                tag_name = data.get('tag_name', '')
                # Remove 'v' prefix if present (v2.9.45 → 2.9.45)
                version = tag_name.lstrip('v')

                changelog_version = version.replace('.', '')
                return {
                    'version': version,
                    'url': data.get('html_url', ''),
                    'changelog_url': (
                        f"https://github.com/JosueAmaral15/clarify/blob/main/CHANGELOG.md#v{changelog_version}"
                    ),
                    'published_at': data.get('published_at', ''),
                    'body': data.get('body', '')
                }

        except HTTPError as e:
            # 404 means no releases published yet - don't spam console
            if e.code != 404:
                logger.error(f"Failed to fetch release info: HTTP {e.code}")
            return None
        except (URLError, json.JSONDecodeError, TimeoutError) as e:
            logger.error(f"Failed to fetch release info: {e}")
            return None

    def _is_newer_version(self, latest: str) -> bool:
        """
        Compare versions using semantic versioning.

        Args:
            latest: Latest version from GitHub (e.g., "2.9.45")

        Returns:
            True if latest > current

        Examples:
            >>> checker = UpdateChecker("2.9.44")
            >>> checker._is_newer_version("2.9.45")
            True
            >>> checker._is_newer_version("2.9.44")
            False
            >>> checker._is_newer_version("2.10.0")
            True
        """
        try:
            # Parse semantic versions (major.minor.patch)
            current_parts = [int(x) for x in self.current_version.split('.')]
            latest_parts = [int(x) for x in latest.split('.')]

            # Pad with zeros if needed (2.9 → 2.9.0)
            while len(current_parts) < 3:
                current_parts.append(0)
            while len(latest_parts) < 3:
                latest_parts.append(0)

            # Compare tuples (major, minor, patch)
            return tuple(latest_parts) > tuple(current_parts)

        except (ValueError, AttributeError):
            # Invalid version format - assume not newer
            return False

    def _load_cache(self) -> Optional[Tuple[bool, Optional[Dict]]]:
        """
        Load cached update check result.

        Returns:
            Cached result if valid and not expired, None otherwise
        """
        if not self.CACHE_FILE.exists():
            return None

        try:
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)

            # Check expiry (24h)
            cached_at = datetime.fromisoformat(cache.get('timestamp', ''))
            if datetime.now() - cached_at > timedelta(hours=self.CACHE_DURATION_HOURS):
                return None  # Expired

            # Check if version changed (app was updated)
            if cache.get('checked_version') != self.current_version:
                return None  # Invalidate cache

            has_update = cache.get('has_update', False)
            release_info = cache.get('release_info')

            return has_update, release_info

        except (OSError, json.JSONDecodeError, ValueError, KeyError):
            # Corrupted cache - ignore
            return None

    def _save_cache(self, has_update: bool, release_info: Optional[Dict]) -> None:
        """
        Save update check result to cache.

        Args:
            has_update: Whether an update is available
            release_info: Release information dict
        """
        cache = {
            'timestamp': datetime.now().isoformat(),
            'checked_version': self.current_version,
            'has_update': has_update,
            'release_info': release_info
        }

        try:
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
        except IOError:
            # Failed to save cache - not critical
            pass

    @staticmethod
    def clear_cache() -> None:
        """Delete cache file (useful for testing or troubleshooting)."""
        cache_file = UpdateChecker.CACHE_FILE
        if cache_file.exists():
            cache_file.unlink()


# Convenience function for quick checks
def check_for_updates(current_version: str, force: bool = False) -> Tuple[bool, Optional[Dict]]:
    """
    Quick function to check for updates.

    Args:
        current_version: Current installed version
        force: Bypass cache if True

    Returns:
        Tuple of (has_update, release_info)

    Example:
        >>> from src import __version__
        >>> has_update, info = check_for_updates(__version__)
        >>> if has_update:
        ...     logger.error(f"Update available: {info['version']}")
    """
    checker = UpdateChecker(current_version)
    return checker.check_for_updates(force=force)
