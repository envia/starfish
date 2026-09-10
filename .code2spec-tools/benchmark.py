"""Phase-level benchmark instrumentation for AST export pipeline.

Provides a context manager and helpers to measure per-phase timing, peak RSS,
and artifact sizes.  Activated via ``CODE2SPEC_BENCHMARK=1`` env var or the
``--benchmark`` CLI flag.
"""

from __future__ import annotations

import json
import os
import resource
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PhaseRecord:
    """Single phase measurement."""

    name: str
    elapsed: float = 0.0
    items: int = 0
    detail: dict = field(default_factory=dict)


@dataclass
class BenchmarkReport:
    """Aggregated benchmark report for one ``export_graph`` run."""

    phases: list[PhaseRecord] = field(default_factory=list)
    peak_rss_kb: int = 0
    total_elapsed: float = 0.0
    workers: int = 1
    cache_hit_rate: float = 0.0
    total_nodes: int = 0
    total_edges: int = 0
    artifact_bytes: dict[str, int] = field(default_factory=dict)

    def add_phase(
        self, name: str, elapsed: float, items: int = 0, **detail
    ) -> None:
        self.phases.append(
            PhaseRecord(name=name, elapsed=elapsed, items=items, detail=detail)
        )

    def to_dict(self) -> dict:
        return {
            "total_elapsed": round(self.total_elapsed, 3),
            "peak_rss_mb": round(self.peak_rss_kb / 1024, 1),
            "workers": self.workers,
            "cache_hit_rate": round(self.cache_hit_rate, 4),
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "artifact_bytes": self.artifact_bytes,
            "phases": [
                {
                    "name": p.name,
                    "elapsed": round(p.elapsed, 3),
                    "items": p.items,
                    "detail": p.detail,
                }
                for p in self.phases
            ],
        }

    def print_summary(self) -> None:
        print("\n" + "=" * 60)
        print("  BENCHMARK REPORT")
        print("=" * 60)
        print(f"  Total elapsed : {self.total_elapsed:.3f}s")
        print(f"  Peak RSS      : {self.peak_rss_kb / 1024:.1f} MB")
        print(f"  Workers       : {self.workers}")
        print(f"  Cache hit rate: {self.cache_hit_rate:.2%}")
        print(f"  Nodes         : {self.total_nodes:,}")
        print(f"  Edges         : {self.total_edges:,}")
        print("-" * 60)
        print(f"  {'Phase':<30} {'Time':>10} {'Items':>10}")
        print("-" * 60)
        for p in self.phases:
            items_str = f"{p.items:,}" if p.items else "-"
            print(f"  {p.name:<30} {p.elapsed:>9.3f}s {items_str:>10}")
        print("-" * 60)
        if self.artifact_bytes:
            total_art = sum(self.artifact_bytes.values())
            print(f"  Total artifacts: {total_art / 1024 / 1024:.1f} MB")
            for name, size in sorted(
                self.artifact_bytes.items(), key=lambda x: -x[1]
            ):
                print(f"    {name}: {size / 1024 / 1024:.1f} MB")
        print("=" * 60 + "\n")


def _get_rss_kb() -> int:
    """Get current process RSS in KB (ru_maxrss)."""
    # On Linux ru_maxrss is in KB; on macOS it's in bytes.
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss


def is_enabled() -> bool:
    """Check if benchmark mode is enabled."""
    return os.environ.get("CODE2SPEC_BENCHMARK", "").lower() in (
        "1",
        "true",
        "yes",
    )


@contextmanager
def phase(report: BenchmarkReport | None, name: str, items: int = 0, **detail):
    """Context manager to measure a single phase.

    Usage::

        with phase(report, "parse_files", items=len(files)):
            results = _parse_files_parallel(...)
    """
    if report is None:
        yield
        return
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    report.add_phase(name, elapsed, items=items, **detail)


def measure_artifact(
    report: BenchmarkReport | None, name: str, path: Path
) -> None:
    """Record artifact file size in the report."""
    if report is None:
        return
    try:
        report.artifact_bytes[name] = path.stat().st_size
    except OSError:
        pass


def save_report(report: BenchmarkReport | None, path: Path) -> None:
    """Save benchmark report as JSON."""
    if report is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
