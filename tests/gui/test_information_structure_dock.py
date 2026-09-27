"""GUI tests for Information Structure integration."""

import json

from src.gui.information_structure_dock import InformationStructureDock
from src.gui.panels.results_tree import ResultsTree


class _PreparedFolderMap:
    def __init__(self):
        self.arguments = None

    def prepare_folder_map(self, root, paths):
        self.arguments = (root, paths)


class _FolderMapWindow:
    def __init__(self):
        self.dock_information_structure = _PreparedFolderMap()
        self.shown = False

    def _show_information_structure(self):
        self.shown = True


def test_file_explorer_paths_can_prepare_folder_map(qapp, tmp_path):
    dock = InformationStructureDock()
    try:
        root = tmp_path / "project"
        dock.prepare_folder_map(str(root), [str(root / "src" / "app.py")])

        output = json.loads(dock.output_edit.toPlainText())
        assert output["type"] == "folder_map"
        assert output["accepted_paths"] == 1
        assert dock.open_editor_button.isEnabled()
    finally:
        dock.close()
        dock.deleteLater()


def test_python_analysis_emits_json_to_editor(qapp):
    dock = InformationStructureDock()
    emitted = []
    dock.open_in_editor_requested.connect(lambda content, name: emitted.append((content, name)))
    try:
        dock.mode_combo.setCurrentIndex(dock.mode_combo.findData("python"))
        dock.identifier_input.setText("custom.module")
        dock.input_edit.setPlainText("def run():\n    print('ok')\n")
        dock.analyze()
        dock._open_in_editor()

        result = json.loads(emitted[0][0])
        assert result["type"] == "python_context_graph"
        assert result["module"] == "custom.module"
        assert emitted[0][1] == "information-structure.json"
    finally:
        dock.close()
        dock.deleteLater()


def test_results_tree_reuses_existing_result_paths_for_folder_map(qapp, tmp_path):
    window = _FolderMapWindow()
    tree = ResultsTree(main_window=window)
    root = tmp_path / "project"
    path = root / "src" / "app.py"
    try:
        tree._base_path = str(root)
        tree._matches_data = {str(path): [(1, 1, "match")]}

        tree._open_folder_map()

        assert window.shown is True
        assert window.dock_information_structure.arguments == (str(root), [str(path)])
    finally:
        tree.close()
        tree.deleteLater()
