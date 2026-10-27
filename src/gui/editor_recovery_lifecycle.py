"""Qt-owned lifecycle hooks for the Editor's existing recovery store."""

# pylint: disable=no-name-in-module  # PySide and shiboken expose dynamic APIs.

import weakref

from PySide6.QtCore import QEvent, QObject, Slot
from PySide6.QtWidgets import QApplication
from shiboken6 import isValid


class EditorRecoveryLifecycle(QObject):
    """Flush while documents still exist, before Qt destroys a widget subtree."""

    def __init__(self, dock):
        super().__init__(dock)
        self._dock = weakref.ref(dock)
        self._watched = []
        self._watch_ancestors()
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.application_quitting)

    def _watch_ancestors(self):
        for reference in self._watched:
            widget = reference()
            if widget is not None and isValid(widget):
                widget.removeEventFilter(self)
        self._watched.clear()
        widget = self._dock()
        while widget is not None and isValid(widget):
            widget.installEventFilter(self)
            self._watched.append(weakref.ref(widget))
            widget = widget.parent()

    @Slot()
    def schedule(self):
        dock = self._dock()
        if dock is not None and isValid(dock) and not dock._recovery_suspended:
            dock._recovery_timer.start()

    @Slot()
    def application_quitting(self):
        dock = self._dock()
        if dock is not None and isValid(dock):
            dock._flush_recovery_on_close(final=True)

    def eventFilter(self, watched, event):  # pylint: disable=invalid-name
        dock = self._dock()
        if dock is None or not isValid(dock):
            return False
        kind = event.type()
        if kind == QEvent.Type.ParentChange:
            self._watch_ancestors()
        elif kind == QEvent.Type.DeferredDelete:
            dock._flush_recovery_on_close(final=True)
        elif kind == QEvent.Type.Close and watched is not dock:
            notes_saved = dock._flush_temp_note_autosaves()
            recovery_saved = dock._checkpoint_unsaved_tabs()
            if not (notes_saved and recovery_saved):
                event.ignore()
                return True
        elif kind == QEvent.Type.Hide and watched is not dock and watched.isWindow():
            dock._flush_recovery_on_close(final=True)
        elif kind == QEvent.Type.Show and watched is dock:
            dock._recovery_suspended = False
            for index in range(dock.tab_widget.count()):
                dock._apply_auto_save_to_tab(dock.tab_widget.widget(index))
            dock._refresh_external_file_watchers()
        return False
