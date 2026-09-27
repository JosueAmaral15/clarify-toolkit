"""GUI test for algorithm analysis preparation."""

import json

from src.gui.algorithm_analysis_dock import AlgorithmAnalysisDock


def test_preflight_must_run_before_ai_preparation(qapp, tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("def run():\n    return 1\n", encoding="utf-8")
    dock = AlgorithmAnalysisDock()
    emitted = []
    dock.prepare_ai_requested.connect(lambda *arguments: emitted.append(arguments))
    try:
        dock.path_input.setText(str(source))
        dock.prepare_ai()
        assert emitted == []

        dock.run_preflight()
        preview = json.loads(dock.preview_edit.toPlainText())
        assert preview["processing_started"] is False
        assert dock.prepare_button.isEnabled()

        dock.prepare_ai()
        assert emitted[0][1] == [str(source.resolve())]
    finally:
        dock.close()
        dock.deleteLater()
