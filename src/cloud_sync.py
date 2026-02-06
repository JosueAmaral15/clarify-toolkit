"""
Cloud Sync Module

Abstraction for cloud storage providers (Google Drive, Dropbox, etc.).
Includes dummy provider for testing.
"""
# pylint: disable=logging-fstring-interpolation  # F-strings clearer

from .utils.logger import get_logger

logger = get_logger(__name__)


class CloudSyncProvider:
    """
    Abstração para provedores de nuvem.
    Implemente métodos para Google Drive, Dropbox, etc.
    """
    def login(self):
        """Login to cloud provider."""
        raise NotImplementedError()
    def upload_settings(self, settings_path):
        """Upload settings file to cloud."""
        raise NotImplementedError()
    def download_settings(self, dest_path):
        """Download settings file from cloud."""
        raise NotImplementedError()

class DummyProvider(CloudSyncProvider):
    """Provedor fictício para testes."""
    def login(self):
        """Dummy login."""
        logger.info("Dummy login performed.")
    def upload_settings(self, settings_path):
        logger.info(f"Dummy upload of {settings_path}")
    def download_settings(self, dest_path):
        logger.info(f"Dummy download to {dest_path}")
