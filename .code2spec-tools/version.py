"""code2spec tool version and install build-info helpers.

The release version is informational and is resolved for install/runtime
metadata. Spec-cache schema compatibility is managed by ``SPEC_CACHE_VERSION``
in ``spec_cache.py``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

UNKNOWN_VERSION = "0+unknown"
BUILD_INFO_FILE = "build-info.json"
VERSION_FILE = "VERSION"


def _read_text(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _parse_pyproject_version(path: Path) -> str | None:
    try:
        data = path.read_text(encoding="utf-8")
    except OSError:
        return None

    try:
        import tomllib

        parsed = tomllib.loads(data)
        version = parsed.get("project", {}).get("version")
        if isinstance(version, str) and version:
            return version
    except Exception:
        pass

    match = re.search(r'^version\s*=\s*"([^"]+)"', data, flags=re.MULTILINE)
    return match.group(1) if match else None


def _candidate_roots(start: Path | None = None) -> list[Path]:
    base = (start or Path(__file__).resolve()).resolve()
    if base.is_file():
        base = base.parent
    roots = [base, *base.parents]

    # When running from a source checkout, version.py lives under tools/.
    if base.name == "tools" and base.parent not in roots:
        roots.insert(1, base.parent)
    return roots


def find_build_info(start: Path | None = None) -> Path | None:
    """Find the nearest installed ``build-info.json`` file."""
    for root in _candidate_roots(start):
        direct = root / BUILD_INFO_FILE
        if direct.exists():
            return direct
        nested = root / ".code2spec-tools" / BUILD_INFO_FILE
        if nested.exists():
            return nested
    return None


def read_base_version(repo_root: Path | None = None) -> str:
    """Read the repository's base release version."""
    roots = _candidate_roots(repo_root)
    for root in roots:
        version = _read_text(root / VERSION_FILE)
        if version:
            return version
        pyproject_version = _parse_pyproject_version(root / "pyproject.toml")
        if pyproject_version:
            return pyproject_version
    return UNKNOWN_VERSION


def get_build_info(start: Path | None = None) -> dict[str, Any]:
    """Return install build metadata if present, else a source-tree fallback."""
    build_info = find_build_info(start)
    if build_info is not None:
        try:
            data = json.loads(build_info.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "version": read_base_version(start),
        "source": "source-tree",
    }


def get_code2spec_version(start: Path | None = None) -> str:
    """Resolve the display/release version for installed tools.

    Precedence:
    1. ``CODE2SPEC_VERSION`` environment override
    2. installed ``build-info.json``
    3. installed/source ``VERSION``
    4. ``pyproject.toml`` project version
    5. ``0+unknown``
    """
    env_version = os.environ.get("CODE2SPEC_VERSION", "").strip()
    if env_version:
        return env_version

    build_info = get_build_info(start)
    version = str(build_info.get("version", "")).strip()
    if version:
        return version
    return read_base_version(start)
