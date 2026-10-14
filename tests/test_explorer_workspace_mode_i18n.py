"""Runtime localization and narrow-layout checks for the shared file workspace."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.gui.file_explorer_dock import FileExplorerDock
from src.i18n.translator import get_translator, tr

EXPECTED = {
    "en": ("Workspace", "Compact Mode", "Advanced Mode"),
    "pt_BR": ("Área de trabalho", "Modo compacto", "Modo avançado"),
    "es": ("Espacio de trabajo", "Modo compacto", "Modo avanzado"),
    "fr": ("Espace de travail", "Mode compact", "Mode avancé"),
    "de": ("Arbeitsbereich", "Kompakter Modus", "Erweiterter Modus"),
    "ja": ("ワークスペース", "コンパクトモード", "詳細モード"),
    "zh": ("工作区", "紧凑模式", "高级模式"),
}


def test_workspace_modes_retranslate_without_replacing_tool_identity(qapp, qtbot):
    translator = get_translator()
    original_language = translator.current_language
    dock = FileExplorerDock()
    dock.workspace_mode.setFixedWidth(220)
    dock.show()
    try:
        for language, expected in EXPECTED.items():
            translator.switch_language(language)
            qapp.processEvents()

            title, compact, advanced = expected
            assert dock.windowTitle() == tr("file_list.title")
            assert dock.workspace_mode.title() == title
            assert dock.workspace_mode.buttons["compact"].text() == compact
            assert dock.workspace_mode.buttons["advanced"].text() == advanced

            functional_names = {
                tr("file_list.title"),
                tr("menu.tools.search_replace"),
            }
            for button in dock.workspace_mode.buttons.values():
                assert button.text() not in functional_names
                assert button.toolTip() == button.text()
                assert button.accessibleName() == button.text()
                assert button.sizeHint().width() <= dock.workspace_mode.width()
                assert button.width() <= dock.workspace_mode.width()
    finally:
        translator.switch_language(original_language)
        dock.close()
        dock.deleteLater()
        qtbot.wait(10)
