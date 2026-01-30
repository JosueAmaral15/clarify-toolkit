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
        print("Dummy login performed.")
    def upload_settings(self, settings_path):
        print(f"Dummy upload of {settings_path}")
    def download_settings(self, dest_path):
        print(f"Dummy download to {dest_path}")
