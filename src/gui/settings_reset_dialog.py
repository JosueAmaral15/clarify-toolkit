"""User-facing preview and confirmation for resetting Clarify preferences."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..config_manager import get_config
from ..gui.window_settings import WindowSettings
from ..i18n import tr
from ..settings_reset import SettingsResetError, SettingsResetService


class SettingsResetDialog(QDialog):
    """Preview reset categories without exposing protected application data."""

    def __init__(self, parent, service: SettingsResetService):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle(tr("settings_reset.title"))
        self.setMinimumSize(520, 440)
        self.setModal(True)
        self._checks = {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        introduction = QLabel(tr("settings_reset.introduction"))
        introduction.setWordWrap(True)
        layout.addWidget(introduction)

        self.select_all = QCheckBox(tr("settings_reset.all"))
        self.select_all.setChecked(True)
        self.select_all.toggled.connect(self._set_all_categories)
        layout.addWidget(self.select_all)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        contents = QWidget(scroll)
        categories_layout = QVBoxLayout(contents)
        for category in self.service.categories():
            group = QGroupBox()
            group_layout = QVBoxLayout(group)
            check = QCheckBox(tr(category.label_key))
            check.setChecked(True)
            check.toggled.connect(self._update_selection)
            detail = QLabel(tr(category.description_key))
            detail.setWordWrap(True)
            detail.setTextInteractionFlags(Qt.TextSelectableByMouse)
            group_layout.addWidget(check)
            group_layout.addWidget(detail)
            categories_layout.addWidget(group)
            self._checks[category.category_id] = check
        categories_layout.addStretch(1)
        scroll.setWidget(contents)
        layout.addWidget(scroll, 1)

        protected = QLabel(tr("settings_reset.protected"))
        protected.setWordWrap(True)
        protected.setObjectName("settingsResetProtectedNotice")
        layout.addWidget(protected)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Reset | QDialogButtonBox.Cancel)
        self.buttons.button(QDialogButtonBox.Reset).setText(tr("settings_reset.reset_selected"))
        self.buttons.accepted.connect(self._confirm)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def selected_categories(self) -> tuple[str, ...]:
        return tuple(key for key, check in self._checks.items() if check.isChecked())

    def _set_all_categories(self, checked: bool) -> None:
        for check in self._checks.values():
            check.blockSignals(True)
            check.setChecked(checked)
            check.blockSignals(False)
        self._update_selection()

    def _update_selection(self) -> None:
        selected = self.selected_categories()
        all_selected = len(selected) == len(self._checks)
        self.select_all.blockSignals(True)
        self.select_all.setChecked(all_selected)
        self.select_all.blockSignals(False)
        self.buttons.button(QDialogButtonBox.Reset).setEnabled(bool(selected))

    def _confirm(self) -> None:
        names = [
            tr(category.label_key)
            for category in self.service.categories()
            if category.category_id in self.selected_categories()
        ]
        message = tr("settings_reset.confirm").format(categories="\n- " + "\n- ".join(names))
        answer = QMessageBox.question(
            self,
            tr("settings_reset.confirm_title"),
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.accept()


def show_settings_reset(main_window, service: SettingsResetService | None = None) -> None:
    """Run the confirmed reset and hot-reload appearance only."""
    service = service or SettingsResetService(main_window.settings, get_config())
    dialog = SettingsResetDialog(main_window, service)
    if dialog.exec() != QDialog.Accepted:
        return
    try:
        result = service.reset(dialog.selected_categories())
    except (OSError, ValueError, SettingsResetError) as error:
        QMessageBox.critical(
            main_window,
            tr("settings_reset.error_title"),
            tr("settings_reset.error").format(error=error),
        )
        return

    if "appearance" in result.categories:
        WindowSettings.apply_saved_settings(main_window)
    message_key = "settings_reset.success_restart" if result.restart_required else "settings_reset.success"
    QMessageBox.information(
        main_window,
        tr("settings_reset.success_title"),
        tr(message_key).format(backup=str(result.backup_path)),
    )
