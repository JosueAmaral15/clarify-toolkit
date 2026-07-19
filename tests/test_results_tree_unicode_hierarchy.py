import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.gui.panels.results_tree import (
    ITEM_TYPE_ROOT,
    ITEM_TYPE_ROLE,
    RESULT_PATH_ROLE,
    ResultsTree,
)


def _qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _top_level_by_type(tree: ResultsTree, item_type: str):
    for index in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(index)
        if item.data(0, ITEM_TYPE_ROLE) == item_type:
            return item
    raise AssertionError(f"top-level item not found: {item_type}")


def _child_by_text(parent, text: str):
    for index in range(parent.childCount()):
        child = parent.child(index)
        if child.text(0) == text:
            return child
    raise AssertionError(f"child not found: {text}")


def test_populate_builds_unicode_hierarchy_with_base_path(tmp_path):
    _qapp()
    base = tmp_path / "raiz_acao" / "raiz_ação"
    folder = base / "coração"
    folder.mkdir(parents=True)
    file_path = folder / "maçã_ção.txt"
    file_path.write_text("Olá ação", encoding="utf-8")

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, "Olá ação")]}, base_path=str(base))

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    assert root.text(0).endswith("raiz_ação")
    assert root.text(0).startswith(("Root:", "Raiz:"))
    assert root.toolTip(0) == str(base)

    folder_item = _child_by_text(root, "coração")
    file_item = _child_by_text(folder_item, "maçã_ção.txt")
    match_item = file_item.child(0)

    assert file_item.text(0) == "maçã_ção.txt"
    assert file_item.data(0, RESULT_PATH_ROLE) == str(file_path)
    assert "Olá ação" in match_item.text(0)
    assert match_item.data(0, RESULT_PATH_ROLE) == str(file_path)


def test_incremental_add_keeps_unicode_root_after_clear(tmp_path):
    _qapp()
    base = tmp_path / "projeto_ação"
    folder = base / "dados"
    folder.mkdir(parents=True)
    file_path = folder / "configuração.json"
    file_path.write_text("{}", encoding="utf-8")

    tree = ResultsTree()
    tree.set_base_path(str(base))
    tree.clear()
    tree.add_file_result(str(file_path), [(2, 4, '"ação": true')])

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    folder_item = _child_by_text(root, "dados")
    file_item = _child_by_text(folder_item, "configuração.json")

    assert root.text(0).endswith("projeto_ação")
    assert root.text(0).startswith(("Root:", "Raiz:"))
    assert file_item.data(0, RESULT_PATH_ROLE) == str(file_path)
    assert tree.get_matches_data()[str(file_path)] == [(2, 4, '"ação": true')]


def test_copy_selected_uses_full_unicode_path_not_visible_label(tmp_path):
    app = _qapp()
    base = tmp_path / "raiz_ação"
    folder = base / "coração"
    folder.mkdir(parents=True)
    file_path = folder / "maçã_ção.txt"
    file_path.write_text("Olá ação", encoding="utf-8")

    tree = ResultsTree()
    tree.populate({str(file_path): [(1, 0, "Olá ação")]}, base_path=str(base))

    root = _top_level_by_type(tree, ITEM_TYPE_ROOT)
    file_item = _child_by_text(_child_by_text(root, "coração"), "maçã_ção.txt")
    assert file_item.text(0) == "maçã_ção.txt"

    file_item.setSelected(True)
    tree._copy_selected()

    assert app.clipboard().text().strip() == str(file_path)

    tree.clearSelection()
    match_item = file_item.child(0)
    match_item.setSelected(True)
    tree._copy_selected()

    copied = app.clipboard().text()
    assert str(file_path) in copied
    assert "1:0  Olá ação" in copied
