#!/usr/bin/env python3
"""Print exact package requirements from a Poetry 2 lock file."""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path

PACKAGE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def locked_requirements(lock_path: Path) -> list[str]:
    """Return sorted, unique and exact requirements from *lock_path*."""
    data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    requirements: set[str] = set()
    for package in data.get("package", []):
        name = package.get("name")
        version = package.get("version")
        if not isinstance(name, str) or not PACKAGE_NAME.fullmatch(name):
            raise ValueError(f"Invalid package name in {lock_path}: {name!r}")
        if not isinstance(version, str) or not version or any(char.isspace() for char in version):
            raise ValueError(f"Invalid version for {name!r} in {lock_path}: {version!r}")
        requirements.add(f"{name}=={version}")
    if not requirements:
        raise ValueError(f"No packages found in {lock_path}")
    return sorted(requirements, key=str.casefold)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lock", nargs="?", type=Path, default=Path("poetry.lock"))
    args = parser.parse_args()
    print("\n".join(locked_requirements(args.lock)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
