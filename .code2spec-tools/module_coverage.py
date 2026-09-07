#!/usr/bin/env python3
"""Logical module coverage and pattern expansion helpers."""

from __future__ import annotations

import fnmatch
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol


class ModuleLike(Protocol):
    name: str
    files: list[str]
    include: list[str]
    exclude: list[str]


@dataclass
class PatternExpansion:
    """Result of expanding include/exclude patterns against known files."""

    files: list[str] = field(default_factory=list)
    unmatched_patterns: list[str] = field(default_factory=list)
    broad_patterns: list[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Coverage validation result for module group proposals."""

    known_count: int
    assigned_count: int
    assigned_unique_count: int
    missing_files: list[str] = field(default_factory=list)
    unknown_files: list[str] = field(default_factory=list)
    duplicate_files: list[str] = field(default_factory=list)
    empty_modules: list[str] = field(default_factory=list)
    unmatched_patterns: list[str] = field(default_factory=list)
    broad_patterns: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.missing_files
            or self.unknown_files
            or self.duplicate_files
            or self.empty_modules
            or self.unmatched_patterns
            or self.broad_patterns
        )

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "known_count": self.known_count,
            "assigned_count": self.assigned_count,
            "assigned_unique_count": self.assigned_unique_count,
            "missing_files": self.missing_files,
            "unknown_files": self.unknown_files,
            "duplicate_files": self.duplicate_files,
            "empty_modules": self.empty_modules,
            "unmatched_patterns": self.unmatched_patterns,
            "broad_patterns": self.broad_patterns,
        }


def normalize_path(path: str) -> str:
    """Normalize file paths/patterns for repository-relative matching."""
    p = (path or "").replace("\\", "/").strip()
    if p.startswith("./"):
        p = p[2:]
    return p


def _has_glob(pattern: str) -> bool:
    return any(ch in pattern for ch in "*?[]")


def is_broad_include_pattern(pattern: str) -> bool:
    """Return True for include patterns too broad to be meaningful modules."""
    p = normalize_path(pattern).rstrip("/")
    if p in {"*", "**", "**/*", "src/**", "app/**", "lib/**", "packages/**"}:
        return True
    if p in {"**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.py"}:
        return True
    return False


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Compile a POSIX glob where `*` stays within one path segment and `**` recurses."""
    parts = pattern.split('/')
    regex = '^'
    for index, part in enumerate(parts):
        if part == '**':
            if index == len(parts) - 1:
                regex += '(?:/.*)?'
            else:
                regex += '(?:/[^/]+)*'
            continue

        if index > 0:
            regex += '/'
        translated = fnmatch.translate(part)
        body = translated.removeprefix('(?s:').removesuffix(r')\Z')
        regex += body.replace('.*', '[^/]*')
    regex += '$'
    return re.compile(regex)


def match_pattern(pattern: str, known_files: Iterable[str]) -> set[str]:
    """Expand one path, directory path, or glob pattern against known files.

    Single-segment globs such as `src/*.ts` do not cross `/`; use `**` for
    recursive matches.
    """
    p = normalize_path(pattern)
    files = {normalize_path(f) for f in known_files if f}
    if not p:
        return set()

    if _has_glob(p):
        regex = _glob_to_regex(p)
        return {f for f in files if regex.match(f)}

    # Exact file path.
    if p in files:
        return {p}

    # Directory path shorthand: "src/tasks" means "src/tasks/**".
    prefix = p.rstrip("/") + "/"
    return {f for f in files if f.startswith(prefix)}


def expand_patterns(
    include: list[str],
    exclude: list[str],
    known_files: set[str],
    *,
    allow_broad_patterns: bool = False,
) -> PatternExpansion:
    """Expand include/exclude patterns to a deterministic file list."""
    included: set[str] = set()
    unmatched: list[str] = []
    broad: list[str] = []

    for raw in include:
        pattern = normalize_path(raw)
        if not pattern:
            continue
        if is_broad_include_pattern(pattern) and not allow_broad_patterns:
            broad.append(pattern)
        matched = match_pattern(pattern, known_files)
        if not matched:
            unmatched.append(pattern)
        included.update(matched)

    excluded: set[str] = set()
    for raw in exclude:
        pattern = normalize_path(raw)
        if not pattern:
            continue
        matched = match_pattern(pattern, known_files)
        if not matched:
            unmatched.append(pattern)
        excluded.update(matched)

    return PatternExpansion(
        files=sorted(included - excluded),
        unmatched_patterns=sorted(set(unmatched)),
        broad_patterns=sorted(set(broad)),
    )


def validate_module_coverage(modules: list[ModuleLike], known_files: set[str]) -> CoverageReport:
    """Validate that modules cover known files exactly once."""
    known = {normalize_path(f) for f in known_files if f}
    counts: Counter[str] = Counter()
    empty_modules: list[str] = []
    unmatched_patterns: list[str] = []
    broad_patterns: list[str] = []

    for module in modules:
        if not module.files:
            empty_modules.append(module.name)
        for file_path in module.files:
            counts[normalize_path(file_path)] += 1
        unmatched_patterns.extend(getattr(module, "unmatched_patterns", []))
        broad_patterns.extend(getattr(module, "broad_patterns", []))

    assigned = set(counts)
    return CoverageReport(
        known_count=len(known),
        assigned_count=sum(counts.values()),
        assigned_unique_count=len(assigned),
        missing_files=sorted(known - assigned),
        unknown_files=sorted(assigned - known),
        duplicate_files=sorted(f for f, n in counts.items() if n > 1),
        empty_modules=sorted(empty_modules),
        unmatched_patterns=sorted(set(unmatched_patterns)),
        broad_patterns=sorted(set(broad_patterns)),
    )
