"""
Cloud Sync Module

Abstraction for cloud storage providers (Google Drive, Dropbox, etc.).
Includes dummy provider for testing.
"""

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
        print("Dummy login performed.")
    def upload_settings(self, settings_path):
        print(f"Dummy upload of {settings_path}")
    def download_settings(self, dest_path):
        print(f"Dummy download to {dest_path}")
