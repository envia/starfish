#!/usr/bin/env python3
"""Spec-cache maintenance commands used by full and delta workflows."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

try:
    from ..analysis_paths import get_canonical_paths
    from ..progress.common import _resolve_spec_root
    from ..progress.state import _remove_traceability_row
except ImportError:  # script/installed-tools flat execution
    from analysis_paths import get_canonical_paths
    from progress.common import _resolve_spec_root
    from progress.state import _remove_traceability_row

def cmd_spec_update(args: argparse.Namespace) -> None:
    """모듈 한 개의 spec 생성 결과를 spec-cache.json에 기록.

    W2의 모듈 완료 마킹(`update --status done`) 직후에 호출되어,
    다음 실행 시 delta-plan이 unchanged로 분류할 수 있게 한다.

    source-deps-map.json에서 source_dependencies를 자동 추출하고,
    core-manifest.json에서 is_core를 자동 판단한다.
    """
    try:
        from .spec_cache import (
        SpecCache,
        SpecCacheEntry,
        load_core_manifest,
        load_source_deps_map,
        load_spec_cache,
        parse_source_files_section,
        parse_source_tags,
        save_spec_cache,
        validate_and_normalize_source_files,
        )
    except ImportError:  # script/installed-tools flat execution
        from delta.spec_cache import (
            SpecCache,
            SpecCacheEntry,
            load_core_manifest,
            load_source_deps_map,
            load_spec_cache,
            parse_source_files_section,
            parse_source_tags,
            save_spec_cache,
            validate_and_normalize_source_files,
        )

    output_dir = Path(args.output_dir)
    spec_root = _resolve_spec_root(output_dir)
    paths = get_canonical_paths(output_dir)
    spec_cache_path = paths.spec_cache

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"[ERROR] file not found: {file_path}")
        return

    try:
        from ..parser import file_hash
    except ImportError:  # script/installed-tools flat execution
        try:
            from parser import file_hash
        except ImportError:
            print("[ERROR] parser module unavailable; cannot compute file hash.")
            return

    try:
        h = file_hash(file_path)
    except OSError as exc:
        print(f"[ERROR] failed to hash {file_path}: {exc}")
        return

    cache = load_spec_cache(spec_cache_path) or SpecCache()
    # Tool/release version is intentionally not persisted in spec-cache.
    # Spec-cache compatibility is governed by SPEC_CACHE_VERSION.
    if args.mode:
        cache.mode = args.mode
    if args.analysis_scope is not None:
        cache.analysis_scope = args.analysis_scope

    # source_dependencies 자동 추출.
    # 우선 방금 생성/갱신된 Module Design Card를 직접 파싱한다. W3의
    # source-deps-map.json은 다음 실행을 위한 전체 맵이므로, 현재 W2에서
    # spec-update가 실행되는 시점에는 stale할 수 있다.
    source_dependencies: list[str] = []
    sdd_doc = args.sdd_doc or ""
    sdd_path = spec_root / sdd_doc if sdd_doc else None
    if sdd_path and sdd_path.exists():
        try:
            content = sdd_path.read_text(encoding="utf-8")
            raw_sources = parse_source_files_section(content)
            raw_sources.extend(parse_source_tags(content))
            workspace_root = (
                Path(args.workspace_root)
                if getattr(args, "workspace_root", "")
                else spec_root.parent
            )
            source_dependencies = validate_and_normalize_source_files(
                raw_sources, workspace_root
            )
        except OSError as exc:
            print(f"  ! failed to parse source dependencies from {sdd_doc}: {exc}")

    # 하위 호환: 직접 파싱 결과가 없으면 기존 source-deps-map.json에서 조회.
    deps_map_path = paths.source_deps_map
    if deps_map_path.exists():
        deps_map = load_source_deps_map(deps_map_path)
        if not source_dependencies and deps_map and sdd_doc in deps_map.deps:
            source_dependencies = deps_map.deps[sdd_doc].source_files

    # is_core 자동 판단 (core-manifest.json에서)
    is_core = True  # 기본값
    manifest_path = paths.core_manifest
    if manifest_path.exists():
        manifest = load_core_manifest(manifest_path)
        if manifest:
            is_core = str(file_path) in manifest.core_files

    entry = SpecCacheEntry(
        file_path=str(file_path),
        file_hash=h,
        sdd_doc=sdd_doc,
        fr_doc=args.fr_doc or "",
        generated_at=datetime.now().isoformat(timespec="seconds"),
        mode=cache.mode,
        is_core=is_core,
        source_dependencies=source_dependencies,
    )
    cache.upsert_entry(entry)
    save_spec_cache(spec_cache_path, cache)
    print(
        f"[ProgressTracker] spec-cache updated: {file_path.name} "
        f"(hash={h[:12]}…, is_core={is_core}, "
        f"deps={len(source_dependencies)})"
    )


def cmd_cleanup_removed(args: argparse.Namespace) -> None:
    """diff-plan.json의 removed_modules를 정리.

    - modules/<name>.md, functional-requirements/<name>-fr.md 삭제
    - modules-traceability.md에서 행 제거
    - spec-cache.json에서 항목 제거
    """
    try:
        from .spec_cache import load_spec_cache, save_spec_cache
    except ImportError:  # script/installed-tools flat execution
        from delta.spec_cache import load_spec_cache, save_spec_cache

    output_dir = Path(args.output_dir)
    diff_plan_path = Path(args.diff_plan)
    if not diff_plan_path.exists():
        print(f"[ERROR] diff-plan not found: {diff_plan_path}")
        return
    try:
        plan_data = json.loads(diff_plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[ERROR] failed to read diff-plan: {exc}")
        return

    removed = list(plan_data.get("removed_modules", []))
    moved = list(plan_data.get("moved_modules", []))
    if not removed and not moved:
        print("[ProgressTracker] No removed modules to clean up.")
        return

    spec_root = _resolve_spec_root(output_dir)
    spec_cache_path = get_canonical_paths(output_dir).spec_cache
    cache = load_spec_cache(spec_cache_path)

    deleted_docs = 0
    removed_rows = 0
    cache_pops = 0

    # moved는 새 경로를 W2에서 재생성하도록 두고, 이전 경로의 cache/doc/trace
    # 항목만 제거 대상으로 취급한다.
    cleanup_items = removed + [
        {
            "file": item.get("from", ""),
            "sdd_doc": item.get("sdd_doc", ""),
            "fr_doc": item.get("fr_doc", ""),
        }
        for item in moved
    ]

    for item in cleanup_items:
        file_path = item.get("file", "")
        sdd_doc = item.get("sdd_doc", "")
        fr_doc = item.get("fr_doc", "")

        for rel_doc in (sdd_doc, fr_doc):
            if not rel_doc or rel_doc == "-":
                continue
            doc_path = (spec_root / rel_doc).resolve()
            try:
                if doc_path.is_file():
                    doc_path.unlink()
                    deleted_docs += 1
                    print(f"  - deleted {rel_doc}")
            except OSError as exc:
                print(f"  ! failed to delete {rel_doc}: {exc}")

        # traceability 행 제거: 모듈명을 sdd_doc 파일명 또는 file_path로 시도
        candidates: list[str] = []
        if sdd_doc:
            candidates.append(Path(sdd_doc).stem)
            candidates.append(sdd_doc)
        if file_path:
            candidates.append(Path(file_path).name)
            candidates.append(file_path)
        seen: set[str] = set()
        for cand in candidates:
            if cand in seen:
                continue
            seen.add(cand)
            if _remove_traceability_row(output_dir, cand):
                removed_rows += 1
                break

        if cache is not None and file_path:
            if cache.remove_entry(file_path) is not None:
                cache_pops += 1

    if cache is not None:
        save_spec_cache(spec_cache_path, cache)

    print(
        f"[ProgressTracker] cleanup-removed: {deleted_docs} docs, "
        f"{removed_rows} traceability rows, {cache_pops} cache entries"
    )
