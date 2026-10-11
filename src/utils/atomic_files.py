"""Atomic, conflict-aware writes for regular UTF-8 text files."""

import os
import stat
import tempfile


def file_revision(info):
    """Identity and metadata used to detect edits since the original read."""
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _copy_bounded_metadata(path, temp_path, info):
    """Preserve ownership, permissions and a bounded set of extended attributes."""
    if hasattr(os, "chown"):
        os.chown(temp_path, info.st_uid, info.st_gid)
    if hasattr(os, "listxattr"):
        names = os.listxattr(path)
        if len(names) > 128:
            raise ValueError("File metadata exceeds the 128 attributes limit")
        metadata_bytes = 0
        for name in names:
            value = os.getxattr(path, name)
            metadata_bytes += len(value)
            if metadata_bytes > 1024 * 1024:
                raise ValueError("File metadata exceeds the 1 MiB limit")
            os.setxattr(temp_path, name, value)
    os.chmod(temp_path, stat.S_IMODE(info.st_mode))


def write_text_atomically(path, content):
    """Create or replace one regular file atomically without following links."""
    target = os.path.abspath(os.fspath(path))
    parent = os.path.dirname(target) or os.curdir
    if not os.path.isdir(parent):
        raise FileNotFoundError(f"Parent directory does not exist: {parent}")

    original = None
    if os.path.lexists(target):
        original = os.lstat(target)
        if not stat.S_ISREG(original.st_mode) or original.st_nlink != 1:
            raise ValueError("Saving requires a regular file without links")
        if hasattr(os, "geteuid") and original.st_uid != os.geteuid():
            raise PermissionError("Saving would change file ownership")

    fd, temp_path = tempfile.mkstemp(prefix=".clarify-save-", suffix=".tmp", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        if original is not None:
            _copy_bounded_metadata(target, temp_path, original)
            if file_revision(os.lstat(target)) != file_revision(original):
                raise ValueError("File changed during save; save cancelled")
        elif os.path.lexists(target):
            raise FileExistsError("File appeared during save; save cancelled")
        os.replace(temp_path, target)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def write_existing_text_atomically(path, content, expected_revision):
    """Replace one file, preserving permissions and rejecting stale/link targets."""
    info = os.lstat(path)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("Replacement requires a regular file without hard links")
    if file_revision(info) != expected_revision:
        raise ValueError("File changed since it was read; replacement cancelled")
    if hasattr(os, "geteuid") and info.st_uid != os.geteuid():
        raise PermissionError("Replacement would change file ownership")

    fd, temp_path = tempfile.mkstemp(prefix=".clarify-replace-", suffix=".tmp", dir=os.path.dirname(path) or os.curdir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        _copy_bounded_metadata(path, temp_path, info)
        if file_revision(os.lstat(path)) != expected_revision:
            raise ValueError("File changed before write; replacement cancelled")
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
