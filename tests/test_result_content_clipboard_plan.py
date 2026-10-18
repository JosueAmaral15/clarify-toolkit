"""Pure regressions for bounded result-file content clipboard plans."""

from src.gui.panels.result_export import MatchContentClipboardPlan


def test_content_plan_preserves_order_format_unicode_and_limits(tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "coração.txt"
    first.write_text("alpha", encoding="utf-8")
    second.write_text("ação", encoding="utf-8")
    matches = {
        str(first): [(1, 0, "alpha")],
        str(second): [(1, 0, "ação")],
    }

    result = MatchContentClipboardPlan.from_matches(matches).execute(lambda: True)

    assert result is not None
    assert result.text == (f"===== {first} =====\nalpha\n\n===== {second} =====\nação")
    assert result.stats.copied == 2
    assert result.stats.bytes_copied == len("alpha".encode()) + len("ação".encode())


def test_content_plan_reports_each_skip_reason(tmp_path):
    text = tmp_path / "text.txt"
    binary = tmp_path / "binary.bin"
    directory = tmp_path / "directory"
    too_large = tmp_path / "large.txt"
    total_limited = tmp_path / "total.txt"
    missing = tmp_path / "missing.txt"
    text.write_text("ok", encoding="utf-8")
    binary.write_bytes(b"\x00abc")
    directory.mkdir()
    too_large.write_text("x" * 20, encoding="utf-8")
    total_limited.write_text("abcd", encoding="utf-8")
    matches = {
        str(text): [],
        str(binary): [],
        str(directory): [],
        str(missing): [],
        str(too_large): [],
        str(total_limited): [],
    }

    result = MatchContentClipboardPlan.from_matches(matches, max_file_bytes=10, max_total_bytes=5).execute(lambda: True)

    assert result is not None
    assert result.stats.copied == 1
    assert result.stats.skipped_binary == 1
    assert result.stats.skipped_directory == 1
    assert result.stats.skipped_missing == 1
    assert result.stats.skipped_size == 1
    assert result.stats.skipped_total_limit == 1
    assert result.stats.skipped_error == 0


def test_content_plan_reports_late_decode_errors(tmp_path):
    invalid_utf8 = tmp_path / "invalid.txt"
    invalid_utf8.write_bytes((b"a" * 4096) + b"\xff")

    result = MatchContentClipboardPlan.from_matches(
        {str(invalid_utf8): []},
        max_file_bytes=5000,
        max_total_bytes=10000,
    ).execute(lambda: True)

    assert result is not None
    assert result.stats.skipped_size == 0
    assert result.stats.skipped_error == 1
    assert result.stats.copied == 0


def test_content_plan_cancels_cooperatively_during_chunked_read(tmp_path):
    source = tmp_path / "source.txt"
    source.write_bytes(b"a" * (512 * 1024))
    calls = 0

    def checkpoint():
        nonlocal calls
        calls += 1
        return calls < 4

    result = MatchContentClipboardPlan.from_matches({str(source): []}).execute(checkpoint)

    assert result is None
    assert calls == 4


def test_content_plan_rejects_empty_invalid_or_unbounded_inputs():
    for matches, max_file_bytes, max_total_bytes in (
        ({}, 1, 1),
        ({1: []}, 1, 1),
        ({"x" * 4097: []}, 1, 1),
        ({"path": []}, 0, 1),
        ({"path": []}, 1, 0),
    ):
        try:
            MatchContentClipboardPlan.from_matches(
                matches,
                max_file_bytes=max_file_bytes,
                max_total_bytes=max_total_bytes,
            )
        except (TypeError, ValueError, UnicodeError):
            continue
        raise AssertionError("Expected bounded content-plan validation to fail")
