#!/usr/bin/env python3
"""Canonical path helpers for .analysis artifact taxonomy.

This module provides a single source of truth for resolving canonical
.analysis subdirectory paths and classified artifact locations.

Canonical Layout:
    .analysis/
      state/
        delta/          # portable state needed for W-DELTA
      reports/
        quality/        # quality metrics and acceptance-gate outputs
        runtime/        # runtime stats, telemetry, migration reports
      cache/            # regenerable local cache (AST/parse cache)
      quarantine/       # unknown, obsolete, or conflict-preserved artifacts
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, NamedTuple


class AnalysisPaths(NamedTuple):
    """Canonical .analysis path contract.

    Attributes:
        analysis_dir: Base .analysis directory
        state_delta_dir: .analysis/state/delta
        quality_reports_dir: .analysis/reports/quality
        runtime_reports_dir: .analysis/reports/runtime
        cache_dir: .analysis/cache
        quarantine_dir: .analysis/quarantine
    """
    analysis_dir: Path
    state_delta_dir: Path
    quality_reports_dir: Path
    runtime_reports_dir: Path
    cache_dir: Path
    quarantine_dir: Path

    @classmethod
    def from_analysis_dir(cls, analysis_dir: Path) -> AnalysisPaths:
        """Create AnalysisPaths from base .analysis directory."""
        return cls(
            analysis_dir=analysis_dir,
            state_delta_dir=analysis_dir / "state" / "delta",
            quality_reports_dir=analysis_dir / "reports" / "quality",
            runtime_reports_dir=analysis_dir / "reports" / "runtime",
            cache_dir=analysis_dir / "cache",
            quarantine_dir=analysis_dir / "quarantine",
        )

    def ensure_dirs(self) -> None:
        """Create all canonical directories if missing."""
        for dir_path in [
            self.state_delta_dir,
            self.quality_reports_dir,
            self.runtime_reports_dir,
            self.cache_dir,
            self.quarantine_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    # Delta State artifacts (.analysis/state/delta/)
    @property
    def spec_cache(self) -> Path:
        """Path to spec-cache.json."""
        return self.state_delta_dir / "spec-cache.json"

    @property
    def code2spec_config(self) -> Path:
        """Path to code2spec-config.json."""
        return self.state_delta_dir / "code2spec-config.json"

    @property
    def core_manifest(self) -> Path:
        """Path to core-manifest.json."""
        return self.state_delta_dir / "core-manifest.json"

    @property
    def source_deps_map(self) -> Path:
        """Path to source-deps-map.json."""
        return self.state_delta_dir / "source-deps-map.json"

    @property
    def module_groups(self) -> Path:
        """Path to module-groups.yaml."""
        return self.state_delta_dir / "module-groups.yaml"

    @property
    def diff_plan(self) -> Path:
        """Path to diff-plan.json."""
        return self.state_delta_dir / "diff-plan.json"

    @property
    def analysis_progress(self) -> Path:
        """Path to analysis-progress.json."""
        return self.state_delta_dir / "analysis-progress.json"

    # Quality Reports (.analysis/reports/quality/)
    @property
    def quality_metrics(self) -> Path:
        """Path to quality-metrics.json."""
        return self.quality_reports_dir / "quality-metrics.json"

    @property
    def quality_issues(self) -> Path:
        """Path to quality-issues.json."""
        return self.quality_reports_dir / "quality-issues.json"

    # Runtime Reports (.analysis/reports/runtime/)
    @property
    def runtime_stats(self) -> Path:
        """Path to runtime-stats.json."""
        return self.runtime_reports_dir / "runtime-stats.json"

    @property
    def telemetry_events(self) -> Path:
        """Path to telemetry-events.jsonl."""
        return self.runtime_reports_dir / "telemetry-events.jsonl"

    @property
    def migration_report(self) -> Path:
        """Path to migration-report.json."""
        return self.runtime_reports_dir / "migration-report.json"

    # Cache (.analysis/cache/)
    @property
    def ast_output_dir(self) -> Path:
        """Path to code-to-ast output directory."""
        return self.cache_dir / "code-to-ast"

    @property
    def parse_cache(self) -> Path:
        """Path to parse-cache.json."""
        return self.cache_dir / "code-to-ast" / ".cache" / "parse-cache.json"


# Legacy flat paths for migration detection
KNOWN_FLAT_ARTIFACTS = {
    # Delta state
    "spec-cache.json": "state/delta/spec-cache.json",
    "code2spec-config.json": "state/delta/code2spec-config.json",
    "core-manifest.json": "state/delta/core-manifest.json",
    "source-deps-map.json": "state/delta/source-deps-map.json",
    "module-groups.yaml": "state/delta/module-groups.yaml",
    "diff-plan.json": "state/delta/diff-plan.json",
    "analysis-progress.json": "state/delta/analysis-progress.json",
    "modules-traceability.md": "state/delta/modules-traceability.md",
    "context-summary.md": "state/delta/context-summary.md",
    # Quality reports
    "quality-metrics.json": "reports/quality/quality-metrics.json",
    "quality-issues.json": "reports/quality/quality-issues.json",
    # Runtime reports
    "runtime-stats.json": "reports/runtime/runtime-stats.json",
    "telemetry-events.jsonl": "reports/runtime/telemetry-events.jsonl",
    "migration-report.json": "reports/runtime/migration-report.json",
    # Cache
    "code-to-ast": "cache/code-to-ast",
}

PRESERVED_ROOT_ARTIFACTS = {
    "analysis-notes",
    "module-discovery",
    "interface-candidates",
    "interface-candidates.json",
    "interface-candidate-metrics.json",
    "interface-candidate-scan-error.json",
    "message-contract-candidates.md",
    "history.md",
}

REQUIRED_DELTA_STATE = {"spec-cache.json", "code2spec-config.json"}


def get_canonical_paths(analysis_dir: Path) -> AnalysisPaths:
    """Get canonical paths for .analysis artifacts.

    Args:
        analysis_dir: Path to .analysis directory

    Returns:
        AnalysisPaths with all canonical directory and file paths
    """
    return AnalysisPaths.from_analysis_dir(analysis_dir)


def needs_migration(analysis_dir: Path) -> bool:
    """Check if migration from flat layout is needed.

    Migration is needed when:
    - Known flat artifacts exist directly under .analysis
    - OR canonical state/delta/ is missing required delta state while
      old flat required files exist

    Args:
        analysis_dir: Path to .analysis directory

    Returns:
        True if migration is needed, False otherwise
    """
    if not analysis_dir.exists():
        return False

    # Any known artifact at the old flat location needs migration, regardless
    # of whether the canonical state directory already exists.
    for flat_name in KNOWN_FLAT_ARTIFACTS:
        if (analysis_dir / flat_name).exists():
            return True

    return False


def get_flat_artifacts(analysis_dir: Path) -> list[tuple[str, Path]]:
    """Get list of known flat artifacts that need migration.

    Args:
        analysis_dir: Path to .analysis directory

    Returns:
        List of (flat_name, flat_path) tuples for existing flat artifacts
    """
    if not analysis_dir.exists():
        return []

    result = []
    for flat_name in KNOWN_FLAT_ARTIFACTS:
        flat_path = analysis_dir / flat_name
        if flat_path.exists():
            result.append((flat_name, flat_path))
    return result


class MigrationReport:
    """Migration report data structure.

    Attributes:
        schema_version: Report schema version
        run_at: ISO timestamp of migration run
        analysis_dir: Absolute path to .analysis directory
        status: Migration status (not_needed|migrated|partial|failed)
        canonical_layout: Canonical directory mapping
        moved: List of moved file records
        quarantined: List of quarantined file records
        conflicts: List of conflict records
        required_delta_state: Status of required delta state files
        warnings: List of warning messages
    """

    def __init__(self, analysis_dir: Path):
        self.schema_version = 1
        self.run_at = datetime.now().isoformat(timespec="seconds")
        self.analysis_dir = str(analysis_dir.resolve())
        self.status = "not_needed"
        self.canonical_layout = {
            "state_delta": "state/delta",
            "quality_reports": "reports/quality",
            "runtime_reports": "reports/runtime",
            "cache": "cache",
            "quarantine": "quarantine",
        }
        self.moved: list[dict[str, str]] = []
        self.quarantined: list[dict[str, str]] = []
        self.conflicts: list[dict[str, str]] = []
        self.required_delta_state: dict[str, str] = {}
        self.warnings: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "run_at": self.run_at,
            "analysis_dir": self.analysis_dir,
            "status": self.status,
            "canonical_layout": self.canonical_layout,
            "moved": self.moved,
            "quarantined": self.quarantined,
            "conflicts": self.conflicts,
            "required_delta_state": self.required_delta_state,
            "warnings": self.warnings,
        }


def _files_identical(file1: Path, file2: Path) -> bool:
    """Check whether two files or directory trees have identical content."""
    try:
        if file1.is_dir() != file2.is_dir():
            return False
        if file1.is_dir():
            left = sorted(path.relative_to(file1) for path in file1.rglob("*"))
            right = sorted(path.relative_to(file2) for path in file2.rglob("*"))
            if left != right:
                return False
            return all(
                (file1 / rel).is_dir()
                or (file1 / rel).read_bytes() == (file2 / rel).read_bytes()
                for rel in left
            )
        return file1.read_bytes() == file2.read_bytes()
    except OSError:
        return False


def _move_file(src: Path, dst: Path) -> None:
    """Move a file atomically, creating parent directories as needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(str(src), str(dst))


def _quarantine_file(src: Path, quarantine_dir: Path, reason: str) -> Path:
    """Move a file to quarantine with timestamped subdirectory.

    Args:
        src: Source file path
        quarantine_dir: Base quarantine directory
        reason: Reason for quarantine

    Returns:
        Path to quarantined file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    conflict_dir = quarantine_dir / "conflicts" / timestamp
    conflict_dir.mkdir(parents=True, exist_ok=True)
    dst = conflict_dir / src.name
    shutil.move(str(src), str(dst))
    return dst


def _save_migration_report(report: MigrationReport, paths: AnalysisPaths) -> None:
    """Save migration report to canonical location."""
    paths.runtime_reports_dir.mkdir(parents=True, exist_ok=True)
    content = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"

    fd, tmp_path = tempfile.mkstemp(
        dir=str(paths.runtime_reports_dir),
        suffix=".tmp",
        prefix=".migration_report_",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(paths.migration_report))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def migrate_analysis_dir(analysis_dir: Path) -> MigrationReport:
    """Migrate flat .analysis layout to canonical structure.

    Migration process:
    1. Create canonical directories if missing
    2. Classify known flat files and directories
    3. Move known artifacts to canonical locations
    4. Handle conflicts (identical content → remove duplicate,
       different content → quarantine flat file)
    5. Move unknown flat files to quarantine
    6. Write migration report

    Args:
        analysis_dir: Path to .analysis directory

    Returns:
        MigrationReport with details of migration operations
    """
    paths = AnalysisPaths.from_analysis_dir(analysis_dir)
    report = MigrationReport(analysis_dir)

    # Check if migration is needed
    if not needs_migration(analysis_dir):
        # Verify canonical structure exists
        if (paths.state_delta_dir / "spec-cache.json").exists() or \
           (paths.state_delta_dir / "code2spec-config.json").exists():
            report.status = "not_needed"
            return report
        # Check if no flat artifacts exist at all
        if not any(analysis_dir.iterdir()):
            report.status = "not_needed"
            return report

    # Create canonical directories
    paths.ensure_dirs()

    # Track moved and unknown files
    moved_paths: set[str] = set()

    # Process known flat artifacts
    for flat_name, canonical_rel in KNOWN_FLAT_ARTIFACTS.items():
        flat_path = analysis_dir / flat_name
        if not flat_path.exists():
            continue

        canonical_path = analysis_dir / canonical_rel

        if canonical_path.exists():
            # Handle conflict
            if _files_identical(flat_path, canonical_path):
                # Identical content - remove flat duplicate
                if flat_path.is_dir():
                    shutil.rmtree(flat_path)
                else:
                    flat_path.unlink()
                report.moved.append({
                    "from": flat_name,
                    "to": canonical_rel,
                    "note": "duplicate removed (identical content)",
                })
            else:
                # Different content - quarantine flat file
                quarantined_path = _quarantine_file(
                    flat_path, paths.quarantine_dir, "conflict"
                )
                report.conflicts.append({
                    "from": flat_name,
                    "canonical": canonical_rel,
                    "quarantined_to": str(quarantined_path.relative_to(analysis_dir)),
                    "reason": "content differs",
                })
                moved_paths.add(str(flat_path))
        else:
            # Move to canonical location
            canonical_path.parent.mkdir(parents=True, exist_ok=True)
            if flat_path.is_dir():
                shutil.move(str(flat_path), str(canonical_path))
            else:
                _move_file(flat_path, canonical_path)
            report.moved.append({
                "from": flat_name,
                "to": canonical_rel,
            })
            moved_paths.add(str(flat_path))

    # Find and quarantine unknown flat files
    for item in analysis_dir.iterdir():
        if item.name in (
            "state", "reports", "cache", "quarantine", *PRESERVED_ROOT_ARTIFACTS
        ):
            continue
        if str(item) in moved_paths:
            continue
        if item.is_file() or item.is_dir():
            # Quarantine unknown file/directory
            quarantine_dst = paths.quarantine_dir / item.name
            if quarantine_dst.exists():
                # Handle name conflict
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                quarantine_dst = paths.quarantine_dir / f"{item.name}_{timestamp}"

            if item.is_dir():
                shutil.move(str(item), str(quarantine_dst))
            else:
                _move_file(item, quarantine_dst)

            report.quarantined.append({
                "from": item.name,
                "to": str(quarantine_dst.relative_to(analysis_dir)),
                "reason": "unknown artifact",
            })

    # Verify required delta state
    spec_cache_status = "present" if paths.spec_cache.exists() else "missing"
    code2spec_config_status = "present" if paths.code2spec_config.exists() else "missing"

    report.required_delta_state = {
        "spec_cache": spec_cache_status,
        "code2spec_config": code2spec_config_status,
    }

    # Determine final status
    if spec_cache_status == "missing" or code2spec_config_status == "missing":
        report.status = "partial"
        report.warnings.append(
            "Required delta state is missing. Full rebuild recommended: "
            "/code2spec-discovery -> /code2spec-modules -> /code2spec-finalize"
        )
    elif report.moved or report.quarantined or report.conflicts:
        report.status = "migrated"
    else:
        report.status = "not_needed"

    # Save migration report
    _save_migration_report(report, paths)

    return report


def check_required_delta_state(analysis_dir: Path) -> tuple[bool, str]:
    """Check if required delta state is present and valid.

    Args:
        analysis_dir: Path to .analysis directory

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string.
    """
    paths = AnalysisPaths.from_analysis_dir(analysis_dir)

    missing = []
    corrupt = []

    # Check spec-cache.json
    if not paths.spec_cache.exists():
        missing.append("spec-cache.json")
    else:
        try:
            data = json.loads(paths.spec_cache.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                corrupt.append("spec-cache.json")
        except (json.JSONDecodeError, OSError):
            corrupt.append("spec-cache.json")

    # Check code2spec-config.json
    if not paths.code2spec_config.exists():
        missing.append("code2spec-config.json")
    else:
        try:
            data = json.loads(paths.code2spec_config.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                corrupt.append("code2spec-config.json")
        except (json.JSONDecodeError, OSError):
            corrupt.append("code2spec-config.json")

    if missing:
        return False, f"Missing required delta state: {', '.join(missing)}. Run full rebuild."

    if corrupt:
        return False, f"Corrupt delta state: {', '.join(corrupt)}. Run full rebuild."

    return True, ""
