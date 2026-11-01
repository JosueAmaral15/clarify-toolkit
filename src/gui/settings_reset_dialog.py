"""Safe global or section-level settings reset dialog."""

# pylint: disable=no-name-in-module  # PySide6 exposes extension types dynamically.

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QRadioButton,
    QVBoxLayout,
)

from ..i18n import tr
from ..settings_reset import (
    ALL_RESET_SECTIONS,
    ResetSection,
    SettingsResetCoordinator,
    SettingsResetError,
    SettingsResetResult,
)


class SettingsResetDialog(QDialog):
    """Preview and confirm a bounded, backed-up preference reset."""

    def __init__(self, coordinator: SettingsResetCoordinator, parent=None):
        super().__init__(parent)
        self.coordinator = coordinator
        self.reset_result: SettingsResetResult | None = None
        self.setObjectName("settingsResetDialog")
        self.setWindowTitle(tr("settings_reset.title"))
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        intro = QLabel(tr("settings_reset.intro"), self)
        intro.setWordWrap(True)
        layout.addWidget(intro)

        scope_box = QGroupBox(tr("settings_reset.scope"), self)
        scope_layout = QVBoxLayout(scope_box)
        self.all_radio = QRadioButton(tr("settings_reset.all"), scope_box)
        self.selected_radio = QRadioButton(tr("settings_reset.selected"), scope_box)
        self.all_radio.setObjectName("settingsResetAll")
        self.selected_radio.setObjectName("settingsResetSelected")
        self.all_radio.setChecked(True)
        scope_layout.addWidget(self.all_radio)
        scope_layout.addWidget(self.selected_radio)

        self.section_checks: dict[ResetSection, QCheckBox] = {}
        for section in ALL_RESET_SECTIONS:
            check = QCheckBox(tr(f"settings_reset.section.{section.value}"), scope_box)
            check.setObjectName(f"settingsResetSection_{section.value}")
            check.setChecked(True)
            check.setEnabled(False)
            check.toggled.connect(self._update_preview)
            self.section_checks[section] = check
            scope_layout.addWidget(check)
        layout.addWidget(scope_box)

        self.preview = QPlainTextEdit(self)
        self.preview.setObjectName("settingsResetPreview")
        self.preview.setReadOnly(True)
        self.preview.setMaximumBlockCount(100)
        self.preview.setAccessibleName(tr("settings_reset.preview"))
        layout.addWidget(self.preview)

        protected = QLabel(tr("settings_reset.protected"), self)
        protected.setWordWrap(True)
        layout.addWidget(protected)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel, parent=self)
        self.reset_button = self.buttons.addButton(
            tr("settings_reset.action"), QDialogButtonBox.AcceptRole
        )
        self.reset_button.setObjectName("settingsResetConfirmButton")
        self.buttons.rejected.connect(self.reject)
        self.reset_button.clicked.connect(self._confirm_reset)
        layout.addWidget(self.buttons)

        self.all_radio.toggled.connect(self._scope_changed)
        self.selected_radio.toggled.connect(self._scope_changed)
        self._update_preview()

    def selected_sections(self) -> tuple[ResetSection, ...]:
        """Return the reset sections represented by the current controls."""
        if self.all_radio.isChecked():
            return ALL_RESET_SECTIONS
        return tuple(
            section for section, check in self.section_checks.items() if check.isChecked()
        )

    def _scope_changed(self) -> None:
        selective = self.selected_radio.isChecked()
        for check in self.section_checks.values():
            check.setEnabled(selective)
        self._update_preview()

    def _update_preview(self) -> None:
        sections = self.selected_sections()
        lines = [tr("settings_reset.preview")]
        lines.extend(
            f"- {tr(f'settings_reset.section.{section.value}')}: "
            f"{tr(f'settings_reset.section.{section.value}.detail')}"
            for section in sections
        )
        if ResetSection.ADVANCED in sections:
            lines.extend(("", tr("settings_reset.restart")))
        self.preview.setPlainText("\n".join(lines))
        self.reset_button.setEnabled(bool(sections))

    def _confirm_reset(self) -> None:
        sections = self.selected_sections()
        if not sections:
            return
        answer = QMessageBox.question(
            self,
            tr("settings_reset.confirm_title"),
            tr("settings_reset.confirm"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self.reset_result = self.coordinator.reset(sections)
        except (SettingsResetError, OSError, ValueError) as exc:
            QMessageBox.critical(
                self,
                tr("settings_reset.error_title"),
                tr("settings_reset.error").format(error=str(exc)),
            )
            return
        self.accept()
