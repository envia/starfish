#!/usr/bin/env python3
"""파싱 캐시 관리자 - 파일 해시 기반 증분 파싱 지원."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from .parser import EdgeInfo, NodeInfo, file_hash
except ImportError:  # script/installed-tools flat execution
    from parser import EdgeInfo, NodeInfo, file_hash

CACHE_VERSION = "1.0"


# ── 데이터 모델 ──────────────────────────────────────────────────────────────


@dataclass
class ParseCacheEntry:
    """단일 파일의 파싱 캐시 항목."""

    file_path: str  # 절대 경로
    file_hash: str  # SHA-256 해시
    nodes: list[dict]  # NodeInfo.to_dict() 리스트
    edges: list[dict]  # EdgeInfo.to_dict() 리스트
    parsed_at: str  # ISO 포맷 타임스탬프

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "nodes": self.nodes,
            "edges": self.edges,
            "parsed_at": self.parsed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ParseCacheEntry:
        return cls(
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            nodes=data["nodes"],
            edges=data["edges"],
            parsed_at=data.get("parsed_at", ""),
        )

    @classmethod
    def from_parse_result(
        cls, file_path: str, file_hash_str: str, nodes: list[NodeInfo], edges: list[EdgeInfo]
    ) -> ParseCacheEntry:
        """파싱 결과로부터 캐시 항목 생성."""
        return cls(
            file_path=file_path,
            file_hash=file_hash_str,
            nodes=[n.to_dict() for n in nodes],
            edges=[e.to_dict() for e in edges],
            parsed_at=datetime.now().isoformat(timespec="seconds"),
        )


@dataclass
class ParseCache:
    """전체 파싱 캐시."""

    version: str = CACHE_VERSION
    entries: dict[str, ParseCacheEntry] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> ParseCache:
        version = data.get("version", "")
        if version != CACHE_VERSION:
            return cls()  # 버전 불일치 → 빈 캐시 반환
        entries = {}
        for k, v in data.get("entries", {}).items():
            entries[k] = ParseCacheEntry.from_dict(v)
        return cls(version=version, entries=entries)

    def get_entry(self, file_path: str) -> ParseCacheEntry | None:
        return self.entries.get(file_path)

    def upsert_entry(self, entry: ParseCacheEntry) -> None:
        self.entries[entry.file_path] = entry


# ── 캐시 I/O ─────────────────────────────────────────────────────────────────


def load_cache(cache_path: Path) -> ParseCache | None:
    """캐시 파일 로드. 파일 없거나 버전 불일치 시 None 반환."""
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        cache = ParseCache.from_dict(data)
        if not cache.entries:
            return None  # 빈 캐시 또는 버전 불일치
        return cache
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def save_cache(cache_path: Path, cache: ParseCache) -> None:
    """캐시 파일 원자적 저장 (tmp → rename)."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(cache.to_dict(), ensure_ascii=False, indent=2) + "\n"
    # 원자적 쓰기: 임시 파일에 쓰고 rename
    fd, tmp_path = tempfile.mkstemp(
        dir=str(cache_path.parent), suffix=".tmp", prefix=".cache_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(cache_path))
    except Exception:
        # 실패 시 임시 파일 정리
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ── 변경 감지 ─────────────────────────────────────────────────────────────────


def find_changed_files(
    source_files: list[Path], cache: ParseCache
) -> tuple[list[Path], list[ParseCacheEntry]]:
    """소스 파일 목록을 변경된 파일과 캐시된 파일로 분리.

    Returns:
        (changed_files, cached_entries) — 변경/신규 파일과 캐시 히트 항목
    """
    changed: list[Path] = []
    cached: list[ParseCacheEntry] = []

    for file_path in source_files:
        abs_path = str(file_path.resolve())
        entry = cache.get_entry(abs_path)
        if entry is None:
            # 캐시에 없는 신규 파일
            changed.append(file_path)
            continue
        # 해시 비교
        try:
            current_hash = file_hash(file_path)
        except OSError:
            # 파일 읽기 실패 → 변경된 것으로 간주
            changed.append(file_path)
            continue
        if current_hash == entry.file_hash:
            cached.append(entry)
        else:
            changed.append(file_path)

    return changed, cached


# ── 결과 병합 ─────────────────────────────────────────────────────────────────


def merge_results(
    cached_entries: list[ParseCacheEntry],
    new_results: list[tuple[list[NodeInfo], list[EdgeInfo]]],
    new_file_paths: list[Path],
) -> tuple[list[NodeInfo], list[EdgeInfo]]:
    """캐시된 결과와 새로 파싱한 결과를 병합.

    Args:
        cached_entries: 캐시 히트 항목
        new_results: 새로 파싱한 (nodes, edges) 리스트
        new_file_paths: 새로 파싱한 파일 경로 (new_results와 동일 순서)

    Returns:
        (all_nodes, all_edges) — 병합된 전체 결과
    """
    all_nodes: list[NodeInfo] = []
    all_edges: list[EdgeInfo] = []

    # 캐시된 결과 복원
    for entry in cached_entries:
        for n_dict in entry.nodes:
            all_nodes.append(NodeInfo.from_dict(n_dict))
        for e_dict in entry.edges:
            all_edges.append(EdgeInfo.from_dict(e_dict))

    # 새로 파싱한 결과 추가
    for nodes, edges in new_results:
        all_nodes.extend(nodes)
        all_edges.extend(edges)

    return all_nodes, all_edges


def build_updated_cache(
    cache: ParseCache,
    new_results: list[tuple[list[NodeInfo], list[EdgeInfo]]],
    new_file_paths: list[Path],
) -> ParseCache:
    """기존 캐시에 새 파싱 결과를 반영하여 갱신된 캐시 반환."""
    for (nodes, edges), file_path in zip(new_results, new_file_paths, strict=False):
        abs_path = str(file_path.resolve())
        try:
            h = file_hash(file_path)
        except OSError:
            continue
        entry = ParseCacheEntry.from_parse_result(abs_path, h, nodes, edges)
        cache.upsert_entry(entry)
    return cache


# ── dict 기반 lazy 병합 (객체 생성 지연) ──────────────────────────────────────


def merge_results_lazy(
    cached_entries: list[ParseCacheEntry],
    new_results: list[tuple[list[NodeInfo], list[EdgeInfo]]],
) -> tuple[list[dict], list[dict]]:
    """캐시된 결과와 새로 파싱한 결과를 **dict 리스트**로 병합 (객체 생성 지연).

    기존 ``merge_results``는 모든 dict를 NodeInfo/EdgeInfo 객체로 변환했으나,
    이 함수는 캐시된 dict를 그대로 반환하고 새 결과만 ``to_dict()``로 변환한다.
    JSON export 등 dict 기반 소비자는 객체 변환 없이 직접 사용 가능하다.

    Returns:
        (all_node_dicts, all_edge_dicts) — 병합된 dict 리스트
    """
    all_node_dicts: list[dict] = []
    all_edge_dicts: list[dict] = []

    # 캐시된 결과: 이미 dict이므로 그대로 extend
    for entry in cached_entries:
        all_node_dicts.extend(entry.nodes)
        all_edge_dicts.extend(entry.edges)

    # 새로 파싱한 결과: to_dict()로 변환
    for nodes, edges in new_results:
        all_node_dicts.extend(n.to_dict() for n in nodes)
        all_edge_dicts.extend(e.to_dict() for e in edges)

    return all_node_dicts, all_edge_dicts


def build_updated_cache_from_dicts(
    cache: ParseCache,
    new_node_dicts: list[dict],
    new_edge_dicts: list[dict],
    new_file_paths: list[Path],
) -> ParseCache:
    """dict 기반 파싱 결과로부터 캐시 갱신 (객체 변환 불필요)."""
    # 파일별로 node/edge를 분할하기 위해 file_path 기반 그룹화
    file_to_nodes: dict[str, list[dict]] = {}
    file_to_edges: dict[str, list[dict]] = {}
    for n in new_node_dicts:
        fp = n.get("file_path", "")
        file_to_nodes.setdefault(fp, []).append(n)
    for e in new_edge_dicts:
        fp = e.get("file_path", "")
        file_to_edges.setdefault(fp, []).append(e)

    for file_path in new_file_paths:
        abs_path = str(file_path.resolve())
        try:
            h = file_hash(file_path)
        except OSError:
            continue
        nodes = file_to_nodes.get(abs_path, [])
        edges = file_to_edges.get(abs_path, [])
        entry = ParseCacheEntry(
            file_path=abs_path,
            file_hash=h,
            nodes=nodes,
            edges=edges,
            parsed_at=datetime.now().isoformat(timespec="seconds"),
        )
        cache.upsert_entry(entry)
    return cache

