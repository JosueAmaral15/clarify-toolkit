"""Lifecycle regressions for File Explorer CSV exporting."""

# pylint: disable=no-name-in-module,protected-access

import builtins
import csv
import threading
from threading import Event, Lock

import pytest
from PySide6.QtCore import QCoreApplication, QThread

import src.gui.csv_export as export_module
import src.gui.file_explorer_dock as dock_module
from src.gui.csv_export import CsvExportPlan
from src.gui.file_explorer_dock import FileExplorerDock
from src.i18n.translator import tr
from src.ui import FeatureType, thread_manager


@pytest.fixture(autouse=True)
def isolated_threads(monkeypatch, qtbot):
    monkeypatch.setattr(thread_manager, "_threads", {})
    monkeypatch.setattr(thread_manager, "_shutdown", False)
    monkeypatch.setattr(
        thread_manager,
        "_feature_locks",
        {feature: threading.Lock() for feature in FeatureType},
    )
    yield
    for info in list(thread_manager._threads.values()):
        if info.thread.isRunning():
            info.cancel_callback()
            info.thread.quit()
            info.thread.wait(3000)
    qtbot.waitUntil(lambda: not thread_manager._threads, timeout=3000)


def build_dock(monkeypatch, tmp_path, name="source.txt"):
    dock = FileExplorerDock()
    source_path = str(tmp_path / name)
    dock.results_tree.populate({source_path: [(2, 3, "  needle  ")]})
    dock.table_manager.populate(
        [
            {
                "name": name,
                "size": 6,
                "mtime": 0,
                "permissions": "rw-r--r--",
                "path": source_path,
                "is_dir": False,
            }
        ]
    )
    table = dock.table_manager.table
    for column, value in enumerate(
        (name, "6 B", "1970-01-01", "rw-r--r--", source_path)
    ):
        table.item(0, column).setText(value)
    feedback = {"info": [], "critical": []}
    monkeypatch.setattr(
        dock_module.QMessageBox,
        "information",
        lambda *_args: feedback["info"].append(
            (_args, QThread.currentThread())
        ),
    )
    monkeypatch.setattr(
        dock_module.QMessageBox,
        "critical",
        lambda *_args: feedback["critical"].append(
            (_args, QThread.currentThread())
        ),
    )
    return dock, feedback, source_path


def select_path(monkeypatch, output_path):
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (str(output_path), "CSV Files (*.csv)"),
    )


@pytest.mark.parametrize("view_index", [0, 1], ids=["search", "browse"])
def test_csv_snapshot_stays_gui_and_save_work_runs_off_gui(
    monkeypatch,
    qtbot,
    tmp_path,
    view_index,
):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(view_index)
    output_path = tmp_path / f"view-{view_index}.csv"
    select_path(monkeypatch, output_path)
    snapshot_threads = []
    serialization_threads = []
    write_threads = []
    original_from_rows = CsvExportPlan.from_rows.__func__
    original_writer = export_module.csv.writer
    original_open = builtins.open

    def observed_from_rows(cls, *args, **kwargs):
        snapshot_threads.append(QThread.currentThread())
        return original_from_rows(cls, *args, **kwargs)

    def observed_writer(*args, **kwargs):
        serialization_threads.append(QThread.currentThread())
        return original_writer(*args, **kwargs)

    def observed_open(*args, **kwargs):
        write_threads.append(QThread.currentThread())
        return original_open(*args, **kwargs)

    monkeypatch.setattr(
        CsvExportPlan,
        "from_rows",
        classmethod(observed_from_rows),
    )
    monkeypatch.setattr(export_module.csv, "writer", observed_writer)
    monkeypatch.setattr(builtins, "open", observed_open)

    dock._export_results_csv()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    gui_thread = QCoreApplication.instance().thread()
    assert snapshot_threads == [gui_thread]
    assert serialization_threads
    assert all(thread is not gui_thread for thread in serialization_threads)
    assert write_threads
    assert all(thread is not gui_thread for thread in write_threads)
    assert feedback["info"] and feedback["info"][0][1] is gui_thread
    assert output_path.exists()


@pytest.mark.parametrize("view_index", [0, 1], ids=["search", "browse"])
def test_csv_formats_and_feedback_contracts(
    monkeypatch,
    qtbot,
    tmp_path,
    view_index,
):
    dock, feedback, source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(view_index)
    output_path = tmp_path / f"format-{view_index}.csv"
    select_path(monkeypatch, output_path)
    exported = []
    dock.table_manager.files_exported.connect(
        lambda path: exported.append((path, QThread.currentThread()))
    )

    dock._export_results_csv()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    with output_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    if view_index == 0:
        assert rows == [
            [
                tr("file_list.csv_header_file"),
                tr("file_list.csv_header_line"),
                tr("file_list.csv_header_column"),
                tr("file_list.csv_header_match"),
            ],
            [source_path, "2", "3", "needle"],
        ]
        assert not exported
    else:
        assert rows == [
            ["Name", "Size", "Modified", "Permissions", "Path"],
            ["source.txt", "6 B", "1970-01-01", "rw-r--r--", source_path],
        ]
        assert exported == [
            (str(output_path), QCoreApplication.instance().thread())
        ]
    assert feedback["info"]
    assert not feedback["critical"]


def test_embedded_table_button_uses_dock_gate(monkeypatch, qtbot, tmp_path):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(1)
    output_path = tmp_path / "button.csv"
    select_path(monkeypatch, output_path)

    assert dock.table_manager._export_handler.__self__ is dock
    assert (
        dock.table_manager._export_handler.__func__
        is FileExplorerDock._export_table_to_csv
    )
    dock.table_manager.btn_export.click()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert output_path.exists()
    assert feedback["info"]


def test_one_export_per_dock_and_independent_docks(
    monkeypatch,
    qtbot,
    tmp_path,
):
    first, _first_feedback, _path = build_dock(
        monkeypatch, tmp_path, name="first.txt"
    )
    second, _second_feedback, _path = build_dock(
        monkeypatch, tmp_path, name="second.txt"
    )
    qtbot.addWidget(first)
    qtbot.addWidget(second)
    first.results_stack.setCurrentIndex(0)
    second.results_stack.setCurrentIndex(0)
    paths = iter((str(tmp_path / "first.csv"), str(tmp_path / "second.csv")))
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: (next(paths), "CSV Files (*.csv)"),
    )
    entered = Event()
    release = Event()
    lock = Lock()
    worker_threads = set()
    original_writer = export_module.csv.writer

    def blocking_writer(*args, **kwargs):
        with lock:
            worker_threads.add(QThread.currentThread())
            if len(worker_threads) == 2:
                entered.set()
        assert release.wait(2)
        return original_writer(*args, **kwargs)

    monkeypatch.setattr(export_module.csv, "writer", blocking_writer)
    try:
        first._export_results_csv()
        second._export_results_csv()
        qtbot.waitUntil(entered.is_set, timeout=3000)
        first_thread = first._worker_thread

        first._export_results_csv()

        assert first._worker_thread is first_thread
        assert not first._launch_operation("browse", {})
        assert thread_manager.get_active_threads()[FeatureType.FILE_EXPLORER] == 2
        release.set()
        qtbot.waitUntil(
            lambda: not first._operation_running()
            and not second._operation_running(),
            timeout=3000,
        )
        assert not thread_manager._threads
    finally:
        release.set()


def test_cancelled_export_preserves_destination_and_controls(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(0)
    output_path = tmp_path / "cancel.csv"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_writer = export_module.csv.writer

    def blocking_writer(*args, **kwargs):
        entered.set()
        assert release.wait(2)
        return original_writer(*args, **kwargs)

    monkeypatch.setattr(export_module.csv, "writer", blocking_writer)
    try:
        dock._export_results_csv()
        qtbot.waitUntil(entered.is_set, timeout=2000)
        assert not dock._progress_label.pause_button.isEnabled()
        assert not dock.btn_save_results.isEnabled()
        assert not dock.btn_export_csv.isEnabled()
        assert not dock.table_manager.btn_export.isEnabled()
        dock._on_progress_canceled()
        release.set()
        qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

        assert output_path.read_text(encoding="utf-8") == "preserve me"
        assert not list(tmp_path.glob(".clarify-csv-*.tmp"))
        assert dock.btn_save_results.isEnabled()
        assert dock.btn_export_csv.isEnabled()
        assert dock.table_manager.btn_export.isEnabled()
        assert "cancel" in dock.results_status.text().lower()
        assert not feedback["info"]
        assert not feedback["critical"]
    finally:
        release.set()


def test_io_error_is_reported_without_replacing_destination(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(1)
    output_path = tmp_path / "error.csv"
    output_path.write_text("preserve me", encoding="utf-8")
    select_path(monkeypatch, output_path)
    original_open = builtins.open

    def denied_open(path, *args, **kwargs):
        if str(path).endswith(".tmp"):
            raise PermissionError("denied")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", denied_open)

    dock._export_results_csv()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert output_path.read_text(encoding="utf-8") == "preserve me"
    assert feedback["critical"]
    assert "denied" in feedback["critical"][0][0][-1]
    assert feedback["critical"][0][1] is QCoreApplication.instance().thread()
    assert not list(tmp_path.glob(".clarify-csv-*.tmp"))


def test_close_waits_for_export_and_discards_feedback(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.show()
    dock.results_stack.setCurrentIndex(0)
    output_path = tmp_path / "close.csv"
    select_path(monkeypatch, output_path)
    entered = Event()
    release = Event()
    original_writer = export_module.csv.writer

    def blocking_writer(*args, **kwargs):
        entered.set()
        assert release.wait(2)
        return original_writer(*args, **kwargs)

    monkeypatch.setattr(export_module.csv, "writer", blocking_writer)
    dock._export_results_csv()
    qtbot.waitUntil(entered.is_set, timeout=2000)
    dock.close()

    assert dock.isVisible()
    release.set()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)
    qtbot.waitUntil(lambda: not dock.isVisible(), timeout=3000)
    assert not output_path.exists()
    assert not feedback["info"]
    assert not feedback["critical"]
    assert not thread_manager._threads


def test_export_preserves_file_explorer_state(monkeypatch, qtbot, tmp_path):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(1)
    dock.filter_panel.ed_extensions.setText(".txt,.md")
    dock.combo_target_scope.setCurrentIndex(1)
    cache = {"identity": "preserve"}
    dock._last_content_search_universe = cache
    previous_results = dock.results_tree.get_matches_data()
    output_path = tmp_path / "state.csv"
    select_path(monkeypatch, output_path)

    dock._export_results_csv()
    qtbot.waitUntil(lambda: not dock._operation_running(), timeout=3000)

    assert dock.results_stack.currentIndex() == 1
    assert dock.filter_panel.ed_extensions.text() == ".txt,.md"
    assert dock.combo_target_scope.currentIndex() == 1
    assert dock._last_content_search_universe is cache
    assert dock.results_tree.get_matches_data() is previous_results
    assert dock.operation_log.document().blockCount() <= 200
    assert feedback["info"]


def test_csv_plan_rejects_unbounded_or_invalid_inputs(tmp_path):
    output_path = str(tmp_path / "bounded.csv")
    with pytest.raises(ValueError, match="output path"):
        CsvExportPlan.from_rows(("A",), (("x",),), "x" * 4097, source_count=1)
    with pytest.raises(ValueError, match="16-column"):
        CsvExportPlan.from_rows(
            tuple("H" for _ in range(17)),
            (),
            output_path,
            source_count=0,
        )
    with pytest.raises(ValueError, match="column count"):
        CsvExportPlan.from_rows(("A", "B"), (("x",),), output_path, source_count=1)
    with pytest.raises(ValueError, match="must be text"):
        CsvExportPlan.from_rows(("A",), ((1,),), output_path, source_count=1)
    with pytest.raises(ValueError, match="1 MiB"):
        CsvExportPlan.from_rows(
            ("A",),
            (("x" * (1024 * 1024 + 1),),),
            output_path,
            source_count=1,
        )
    with pytest.raises(ValueError, match="100000-item"):
        CsvExportPlan.from_rows(("A",), (), output_path, source_count=100_001)
    large = "x" * (1024 * 1024)
    with pytest.raises(ValueError, match="20 MiB"):
        CsvExportPlan.from_rows(
            tuple(f"H{index}" for index in range(16)),
            (tuple(large for _ in range(16)), tuple(large for _ in range(16))),
            output_path,
            source_count=2,
        )


def test_empty_cancelled_dialog_and_shutdown_rejection_do_not_leak(
    monkeypatch,
    qtbot,
    tmp_path,
):
    dock, feedback, _source_path = build_dock(monkeypatch, tmp_path)
    qtbot.addWidget(dock)
    dock.results_stack.setCurrentIndex(0)
    dock.results_tree.print_message("")

    dock._export_results_csv()
    assert not dock._operation_running()
    assert feedback["info"]

    dock.results_tree.populate({"source": [(1, 0, "needle")]})
    feedback["info"].clear()
    monkeypatch.setattr(
        dock_module.QFileDialog,
        "getSaveFileName",
        lambda *_args, **_kwargs: ("", ""),
    )
    dock._export_results_csv()
    assert not dock._operation_running()
    assert not feedback["info"]
    assert not feedback["critical"]

    select_path(monkeypatch, tmp_path / "rejected.csv")
    thread_manager._shutdown = True
    dock._export_results_csv()
    assert not dock._operation_running()
    assert feedback["critical"]
    assert not thread_manager._threads
