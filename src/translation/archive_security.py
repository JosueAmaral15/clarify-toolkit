"""Bounded validation for user-selected ZIP-based document formats."""

from dataclasses import dataclass
from typing import Tuple
from zipfile import ZipFile, ZipInfo


@dataclass(frozen=True)
class ZipArchiveLimits:
    """Resource limits applied before a document parser reads ZIP members."""

    max_entries: int
    max_member_bytes: int
    max_total_expanded_bytes: int
    max_total_compressed_bytes: int
    max_compression_ratio: int


DOCUMENT_ARCHIVE_LIMITS = ZipArchiveLimits(
    max_entries=4096,
    max_member_bytes=64 * 1024 * 1024,
    max_total_expanded_bytes=512 * 1024 * 1024,
    max_total_compressed_bytes=512 * 1024 * 1024,
    max_compression_ratio=200,
)


def validate_zip_archive(
    archive: ZipFile,
    *,
    label: str,
    limits: ZipArchiveLimits = DOCUMENT_ARCHIVE_LIMITS,
) -> Tuple[ZipInfo, ...]:
    """Validate ZIP metadata before any member is materialized in memory."""
    members = tuple(archive.infolist())
    if len(members) > limits.max_entries:
        raise ValueError(
            f"{label} archive contains too many entries "
            f"({len(members)} > {limits.max_entries})."
        )

    total_expanded = 0
    total_compressed = 0
    for member in members:
        if member.file_size < 0 or member.compress_size < 0:
            raise ValueError(f"{label} archive member has an invalid size: {member.filename!r}")
        if member.file_size > limits.max_member_bytes:
            raise ValueError(f"{label} archive member is too large: {member.filename!r}")

        total_expanded += member.file_size
        if total_expanded > limits.max_total_expanded_bytes:
            raise ValueError(f"{label} archive exceeds the expanded size limit.")

        total_compressed += member.compress_size
        if total_compressed > limits.max_total_compressed_bytes:
            raise ValueError(f"{label} archive exceeds the compressed size limit.")

        if member.file_size and (
            member.compress_size == 0
            or member.file_size / member.compress_size > limits.max_compression_ratio
        ):
            raise ValueError(
                f"{label} archive member has an unsafe compression ratio: "
                f"{member.filename!r}"
            )

    return members
