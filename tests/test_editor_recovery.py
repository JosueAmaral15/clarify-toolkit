"""Tests for bounded unsaved-document recovery storage."""

from datetime import datetime, timedelta, timezone
import json
import os
import stat
import subprocess
import sys

import pytest

from src.editor_recovery import (
    DEFAULT_RETENTION_HOURS,
    RecoverySnapshotError,
    UnsavedRecoveryStore,
)
from PySide6.QtCore import QLockFile


def test_snapshot_round_trip_and_atomic_temp_cleanup(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)
    store.save(
        "tab-1",
        title="Notes",
        content="Unsaved text",
        file_path="/tmp/notes.txt",
        extension=".txt",
    )

    assert store.list()[0].content == "Unsaved text"
    assert store.list()[0].file_path == "/tmp/notes.txt"
    assert list(tmp_path.glob("*.tmp")) == []


def test_snapshot_rejects_oversized_document(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_document_bytes=4)

    with pytest.raises(RecoverySnapshotError, match="exceeds recovery limit"):
        store.save("large", title="Large", content="12345")


def test_prune_removes_expired_snapshot(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, retention_hours=24)
    store.save("old", title="Old", content="text")
    path = tmp_path / "old.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["updated_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=25)
    ).isoformat()
    path.write_text(json.dumps(data), encoding="utf-8")

    assert store.list() == []
    assert not path.exists()


def test_default_retention_keeps_twenty_nine_day_snapshot(tmp_path):
    assert DEFAULT_RETENTION_HOURS == 30 * 24
    store = UnsavedRecoveryStore(tmp_path)
    store.save("recent", title="Recent", content="recover me")
    path = tmp_path / "recent.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["updated_at"] = (
        datetime.now(timezone.utc) - timedelta(days=29)
    ).isoformat()
    path.write_text(json.dumps(data), encoding="utf-8")

    assert [snapshot.snapshot_id for snapshot in store.list()] == ["recent"]


def test_recovery_inventory_reports_expired_corrupt_and_quota_cleanup(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_snapshots=1)
    store.save("keep", title="Keep", content="current")

    expired = tmp_path / "expired.json"
    expired.write_text((tmp_path / "keep.json").read_text(encoding="utf-8"), encoding="utf-8")
    expired_data = json.loads(expired.read_text(encoding="utf-8"))
    expired_data["snapshot_id"] = "expired"
    expired_data["updated_at"] = (
        datetime.now(timezone.utc) - timedelta(days=31)
    ).isoformat()
    expired.write_text(json.dumps(expired_data), encoding="utf-8")

    (tmp_path / "corrupt.json").write_text("not json", encoding="utf-8")
    extra = tmp_path / "extra.json"
    extra.write_text((tmp_path / "keep.json").read_text(encoding="utf-8"), encoding="utf-8")
    extra_data = json.loads(extra.read_text(encoding="utf-8"))
    extra_data["snapshot_id"] = "extra"
    extra_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    extra.write_text(json.dumps(extra_data), encoding="utf-8")

    snapshots, report = store.list_with_report()

    assert len(snapshots) == 1
    assert report.expired == 1
    assert report.invalid == 1
    assert report.over_count == 1
    assert report.over_total_bytes == 0


def test_inventory_io_failure_is_reported_without_deleting_snapshot(
    tmp_path, monkeypatch
):
    store = UnsavedRecoveryStore(tmp_path)
    store.save("keep", title="Keep", content="current")
    original_open = os.open

    def fail_snapshot_open(path, flags, *args, **kwargs):
        if str(path).endswith("keep.json"):
            raise OSError("synthetic inventory failure")
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", fail_snapshot_open)

    with pytest.raises(OSError, match="synthetic inventory failure"):
        store.list_with_report()
    assert (tmp_path / "keep.json").exists()


def test_save_reports_count_quota_without_evicting_other_buffers(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_snapshots=2)
    for snapshot_id in ("one", "two"):
        store.save(snapshot_id, title=snapshot_id, content=snapshot_id)
    with pytest.raises(RecoverySnapshotError, match="quota"):
        store.save("three", title="three", content="three")
    assert len(store.list()) == 2
    assert {snapshot.snapshot_id for snapshot in store.list()} == {"one", "two"}


def test_invalid_identifier_cannot_escape_recovery_root(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)

    with pytest.raises(RecoverySnapshotError, match="Invalid"):
        store.save("../escape", title="Unsafe", content="text")


def test_private_directory_and_snapshot_permissions(tmp_path):
    root = tmp_path / 'recovery'
    store = UnsavedRecoveryStore(root)
    store.save('one', title='notes', content='private')
    assert stat.S_IMODE(root.stat().st_mode) == 0o700
    assert stat.S_IMODE((root / 'one.json').stat().st_mode) == 0o600


def test_total_quota_rejects_new_snapshot_without_eviction(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_total_bytes=512)
    store.save('one', title='one', content='a' * 100)
    with pytest.raises(RecoverySnapshotError, match='quota'):
        store.save('two', title='two', content='b' * 100)
    assert [item.snapshot_id for item in store.list()] == ['one']


def test_overwrite_counts_only_other_snapshots_in_quota(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_snapshots=1, max_total_bytes=512)
    store.save('one', title='notes', content='old')
    store.save('one', title='notes', content='latest')
    assert store.list()[0].content == 'latest'


def test_failed_atomic_replace_preserves_previous_snapshot(tmp_path, monkeypatch):
    store = UnsavedRecoveryStore(tmp_path)
    store.save('one', title='notes', content='old')
    def fail(*args):
        raise OSError('synthetic atomic failure')
    monkeypatch.setattr(os, 'replace', fail)
    with pytest.raises(OSError):
        store.save('one', title='notes', content='latest')
    assert store.list()[0].content == 'old'
    assert not list(tmp_path.glob('*.tmp'))


@pytest.mark.parametrize('change', [
    {'content': 1}, {'updated_at': 1}, {'updated_at': 'not-a-date'},
    {'source_signature': [1]}, {'source_signature': ['x'] * 5},
    {'kind': 'unknown'}, {'kind': 'reference'}, {'cursor_position': -1},
    {'cursor_position': 'x'}, {'snapshot_id': '../outside'},
    {'content': None}, {'title': 'x' * 4097},
])
def test_corrupt_snapshot_is_pruned_without_crashing(tmp_path, change):
    store = UnsavedRecoveryStore(tmp_path)
    store.save('one', title='notes', content='old')
    path = tmp_path / 'one.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    data.update(change)
    path.write_text(json.dumps(data), encoding='utf-8')
    assert store.list() == []
    assert not path.exists()


def test_legacy_snapshot_without_session_fields_still_loads(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)
    store.save('one', title='notes', content='legacy')
    path = tmp_path / 'one.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for key in ('kind', 'source_signature', 'cursor_position'):
        del data[key]
    path.write_text(json.dumps(data), encoding='utf-8')
    assert store.list()[0].kind == 'buffer'
    assert store.list()[0].content == 'legacy'


def test_saved_reference_round_trip_and_revision_check(tmp_path):
    source = tmp_path / 'original.txt'
    source.write_text('saved\ntext', encoding='utf-8')
    store = UnsavedRecoveryStore(tmp_path / 'recovery')
    signature = store.source_signature(str(source))
    store.save_reference('one', title=source.name, file_path=str(source),
                         source_signature=signature, cursor_position=4)
    snapshot = store.list()[0]
    assert snapshot.content == ''
    assert snapshot.cursor_position == 4
    assert store.read_reference(snapshot) == 'saved\ntext'
    source.write_text('changed', encoding='utf-8')
    with pytest.raises(RecoverySnapshotError, match='missing or changed'):
        store.read_reference(snapshot)


def test_reference_does_not_follow_replaced_source_symlink(tmp_path):
    source = tmp_path / 'original.txt'
    target = tmp_path / 'target.txt'
    source.write_text('saved', encoding='utf-8')
    target.write_text('do not read', encoding='utf-8')
    store = UnsavedRecoveryStore(tmp_path / 'recovery')
    snapshot = store.save_reference('one', title='original', file_path=str(source),
                                    source_signature=store.source_signature(str(source)))
    source.unlink()
    source.symlink_to(target)
    with pytest.raises(RecoverySnapshotError):
        store.read_reference(snapshot)
    assert target.read_text(encoding='utf-8') == 'do not read'


def test_symlink_recovery_root_is_rejected(tmp_path):
    target = tmp_path / 'other'
    target.mkdir()
    root = tmp_path / 'recovery'
    root.symlink_to(target, target_is_directory=True)
    with pytest.raises(RecoverySnapshotError, match='symlink'):
        UnsavedRecoveryStore(root).save('one', title='notes', content='text')
    assert list(target.iterdir()) == []


def test_utf8_size_and_json_encoding_limits_are_explicit(tmp_path):
    store = UnsavedRecoveryStore(tmp_path, max_document_bytes=4)
    store.save('one', title='notes', content='\u00e9\u00e9')
    with pytest.raises(RecoverySnapshotError, match='recovery limit'):
        store.save('one', title='notes', content='\u00e9\u00e9x')
    assert store.list()[0].content == '\u00e9\u00e9'
    larger = UnsavedRecoveryStore(tmp_path, max_document_bytes=100_000)
    with pytest.raises(RecoverySnapshotError, match='Encoded'):
        larger.save('escaped', title='notes', content='\x01' * 100_000)


@pytest.mark.parametrize('kind', ['invalid', 'reference'])
def test_invalid_snapshot_kind_is_rejected(tmp_path, kind):
    with pytest.raises(RecoverySnapshotError, match='kind'):
        UnsavedRecoveryStore(tmp_path).save('one', title='notes', content='content', kind=kind)


def test_persistent_snapshot_survives_new_process(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)
    store.save('one', title='notes', content='durable draft')
    result = subprocess.run([
        sys.executable, '-c',
        'import sys; from src.editor_recovery import UnsavedRecoveryStore; '
        'assert UnsavedRecoveryStore(sys.argv[1]).list()[0].content == "durable draft"',
        str(tmp_path),
    ], timeout=10, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr.decode()


def test_busy_store_reports_failure_without_waiting_or_eviction(tmp_path):
    store = UnsavedRecoveryStore(tmp_path)
    store.save('one', title='notes', content='preserve')
    lock = QLockFile(str(tmp_path / '.recovery.lock'))
    assert lock.tryLock(0)
    try:
        with pytest.raises(RecoverySnapshotError, match='busy'):
            store.save('two', title='other', content='new')
        with pytest.raises(RecoverySnapshotError, match='busy'):
            store.discard('one')
    finally:
        lock.unlock()
    assert store.list()[0].content == 'preserve'


def test_reading_empty_store_does_not_create_directory(tmp_path):
    root = tmp_path / 'absent'
    store = UnsavedRecoveryStore(root)
    store.prune()
    assert store.list() == []
    store.discard('one')
    store.discard_all()
    assert not root.exists()


@pytest.mark.parametrize('payload', [b'\xff', b'binary\x00text'])
def test_non_text_reference_is_not_silently_restored(tmp_path, payload):
    source = tmp_path / 'original'
    source.write_bytes(payload)
    store = UnsavedRecoveryStore(tmp_path / 'recovery')
    snapshot = store.save_reference('one', title='original', file_path=str(source),
                                    source_signature=store.source_signature(str(source)))
    with pytest.raises(RecoverySnapshotError, match='not UTF-8 text'):
        store.read_reference(snapshot)
    assert source.read_bytes() == payload


@pytest.mark.parametrize('signature', [(), (1, 2, 3, 4), ('x',) * 5, (-1,) * 5])
def test_invalid_source_revision_is_rejected_before_success(tmp_path, signature):
    store = UnsavedRecoveryStore(tmp_path)
    with pytest.raises(RecoverySnapshotError, match='revision'):
        store.save_reference('one', title='notes', file_path='/unused', source_signature=signature)
    assert store.list() == []


def test_non_text_identifier_is_rejected(tmp_path):
    with pytest.raises(RecoverySnapshotError, match='identifier'):
        UnsavedRecoveryStore(tmp_path).save(None, title='notes', content='text')


def test_deep_corrupt_json_is_pruned(tmp_path):
    path = tmp_path / 'corrupt.json'
    path.write_text('[' * 2000 + '0' + ']' * 2000, encoding='utf-8')
    assert UnsavedRecoveryStore(tmp_path).list() == []
    assert not path.exists()
