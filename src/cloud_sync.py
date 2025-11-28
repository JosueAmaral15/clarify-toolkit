import os
import json

class CloudSyncProvider:
    """
    Abstração para provedores de nuvem.
    Implemente métodos para Google Drive, Dropbox, etc.
    """
    def login(self):
        raise NotImplementedError()
    def upload_settings(self, settings_path):
        raise NotImplementedError()
    def download_settings(self, dest_path):
        raise NotImplementedError()

class DummyProvider(CloudSyncProvider):
    """Provedor fictício para testes."""
    def login(self):
        print("Login fictício realizado.")
    def upload_settings(self, settings_path):
        print(f"Upload fictício de {settings_path}")
    def download_settings(self, dest_path):
        print(f"Download fictício para {dest_path}")
