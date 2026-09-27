"""Tests for the completion-sound preference."""

from src.gui.preferences_dialog import PreferencesDialog


class _QSettings:
    def __init__(self):
        self.values = {"update_checker/enabled": True}

    def value(self, key, default=None, type=None):
        value = self.values.get(key, default)
        return type(value) if type else value

    def setValue(self, key, value):
        self.values[key] = value


class _Settings:
    def __init__(self):
        self.values = {}
        self.qsettings = _QSettings()

    def get(self, key, default=None):
        return self.values.get(key, default)

    def update_multiple(self, values):
        self.values.update(values)


def test_completion_sound_is_opt_in_and_persisted(qapp, monkeypatch):
    settings = _Settings()
    dialog = PreferencesDialog(settings)
    monkeypatch.setattr("src.gui.preferences_dialog.QMessageBox.information", lambda *args: None)
    try:
        assert not dialog.chk_completion_sound.isChecked()

        dialog.chk_completion_sound.setChecked(True)
        dialog._save_and_close()

        assert settings.values["completion_sound"] is True
    finally:
        dialog.deleteLater()
