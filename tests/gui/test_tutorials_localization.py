"""Portuguese tutorial chrome preserves current selection and content state."""

from PySide6.QtCore import QCoreApplication, QEvent, Qt

from src.gui.tutorials_dock import TutorialsDock
from src.i18n import get_translator, tr


def test_tutorial_navigation_and_welcome_translate_without_losing_selection(qapp):
    translator = get_translator()
    translator.switch_language("en")
    dock = TutorialsDock()
    try:
        item = dock.tree.topLevelItem(0).child(0).child(0)
        dock.tree.setCurrentItem(item)
        path = item.data(0, Qt.UserRole)
        dock.search_input.setText("keep this query")
        translator.switch_language("pt_BR")
        assert dock.tree.currentItem() is item
        assert item.data(0, Qt.UserRole) == path
        assert "Tradução JSON" in item.text(0)
        assert "Fácil" in item.toolTip(0)
        assert dock.search_input.text() == "keep this query"
        assert dock.btn_search.text() == tr("tutorials.btn_search")
        assert dock.tree.headerItem().text(0) == tr("tutorials.browse")
        assert tr("tutorials.welcome_heading") in dock.browser.toPlainText()
        assert dock.status_label.text() == tr("tutorials.status_loaded").format(count=3)
        assert dock.btn_ai_assistant.toolTip() == tr("menu.tooltip_ai_assistant")
    finally:
        dock.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        translator.switch_language("en")


def test_portuguese_search_and_no_results_retranslate_in_place(qapp):
    translator = get_translator()
    translator.switch_language("pt_BR")
    dock = TutorialsDock()
    try:
        selected = dock.tree.topLevelItem(0).child(0).child(0)
        dock.tree.setCurrentItem(selected)
        dock.search_input.setText("Tradução")
        dock._perform_search()
        assert len(dock._search_matches) == 1
        assert tr("tutorials.search_heading").format(query="Tradução") in dock.browser.toPlainText()
        assert "Tradução JSON" in dock.browser.toPlainText()
        assert tr("tutorials.search_summary_one").format(count=1) in dock.browser.toPlainText()
        assert dock.tree.currentItem() is selected
        translator.switch_language("en")
        assert len(dock._search_matches) == 1
        assert dock.tree.currentItem() is selected
        assert dock.title_label.text() == tr("tutorials.search_title").format(count=1)
        translator.switch_language("pt_BR")
        dock.search_input.setText("sem-resultados-de-teste")
        dock._perform_search()
        assert dock.status_label.text() == tr("tutorials.no_results_status").format(query="sem-resultados-de-teste")
        assert tr("tutorials.no_results_hint") in dock.browser.toPlainText()
        translator.switch_language("en")
        assert tr("tutorials.no_results_hint") in dock.browser.toPlainText()
    finally:
        dock.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        translator.switch_language("en")


def test_opened_tutorial_keeps_document_while_title_translates(qapp, tmp_path):
    translator = get_translator()
    translator.switch_language("en")
    dock = TutorialsDock()
    try:
        dock.tutorials_path = tmp_path
        file_path = tmp_path / "beginner/basic/01-json-translate.md"
        file_path.parent.mkdir(parents=True)
        file_path.write_text("# Synthetic tutorial\nBody stays unchanged.", encoding="utf-8")
        dock._open_tutorial("beginner/basic/01-json-translate.md")
        before = dock.browser.toPlainText()
        translator.switch_language("pt_BR")
        assert "Tradução JSON" in dock.title_label.text()
        assert dock.browser.toPlainText() == before
        assert dock.current_tutorial == str(file_path)
    finally:
        dock.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        translator.switch_language("en")
