#!/usr/bin/env python3
"""Document indexing commands: source deps map and core manifest."""

from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path

try:
    from ..progress.common import _dedupe_preserve_order, _resolve_spec_root
except ImportError:  # script/installed-tools flat execution
    from progress.common import _dedupe_preserve_order, _resolve_spec_root


def cmd_build_deps_map(args: argparse.Namespace) -> None:
    """모든 Module Design Card 에서 Source Files 섹션을 파싱하여 의존성 맵 구축.

    W3(Finalize) 단계에서 CLI 가 모든 문서를 순회하며 Source Files 섹션을
    파싱하여 source-deps-map.json 을 생성한다.
    """
    try:
        from ..analysis_paths import get_canonical_paths
        from ..delta.spec_cache import (
            DepInfo,
            SourceDepsMap,
            parse_source_files_section,
            parse_source_tags,
            save_source_deps_map,
            validate_and_normalize_source_files,
        )
    except ImportError:  # script/installed-tools flat execution
        from analysis_paths import get_canonical_paths
        from delta.spec_cache import (
            DepInfo,
            SourceDepsMap,
            parse_source_files_section,
            parse_source_tags,
            save_source_deps_map,
            validate_and_normalize_source_files,
        )

    output_dir = Path(args.output_dir)
    spec_root = _resolve_spec_root(output_dir)
    paths = get_canonical_paths(output_dir)
    modules_dir = spec_root / "modules"

    if not modules_dir.exists():
        print(f"[ERROR] modules directory not found: {modules_dir}")
        return

    workspace_root = Path(args.workspace_root) if args.workspace_root else None

    deps: dict[str, DepInfo] = {}
    md_files = sorted(modules_dir.glob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"  ! failed to read {md_file.name}: {exc}")
            continue

        # 1차: Source Files 섹션 파싱
        source_files = parse_source_files_section(content)

        # 2차: [Source: ...] 태그 보충
        source_files.extend(parse_source_tags(content))

        # 중복 제거 + 정규화
        if workspace_root:
            source_files = validate_and_normalize_source_files(
                source_files, workspace_root
            )
        else:
            # workspace_root가 없으면 중복 제거만
            seen: set[str] = set()
            unique: list[str] = []
            for f in source_files:
                if f not in seen:
                    unique.append(f)
                    seen.add(f)
            source_files = unique

        primary_source = source_files[0] if source_files else ""

        # FR 문서 경로 추론
        fr_doc = _find_fr_doc(spec_root, md_file.stem)

        doc_key = str(md_file.relative_to(spec_root))
        deps[doc_key] = DepInfo(
            source_files=source_files,
            primary_source=primary_source,
            fr_doc=fr_doc,
        )

    deps_map = SourceDepsMap(
        built_at=datetime.now().isoformat(timespec="seconds"),
        deps=deps,
    )

    deps_map_path = paths.source_deps_map
    save_source_deps_map(deps_map_path, deps_map)

    print(
        f"[ProgressTracker] build-deps-map: {len(deps)} documents, "
        f"→ {deps_map_path}"
    )


def _find_fr_doc(spec_root: Path, module_stem: str) -> str:
    """FR 문서 경로 추론."""
    fr_dir = spec_root / "functional-requirements"
    if fr_dir.exists():
        # 정확한 이름 매칭 시도
        for pattern in [f"{module_stem}-fr.md", f"{module_stem.lower()}-fr.md"]:
            if (fr_dir / pattern).exists():
                return f"functional-requirements/{pattern}"
        # 유사한 이름 검색
        for f in fr_dir.glob("*-fr.md"):
            if module_stem.lower() in f.stem.lower():
                return f"functional-requirements/{f.name}"
    return ""


def _infer_module_groups_path(output_dir: Path) -> str:
    """누락된 module-groups.yaml 경로를 보수적으로 추론."""
    try:
        from ..analysis_paths import get_canonical_paths
    except ImportError:  # script/installed-tools flat execution
        from analysis_paths import get_canonical_paths

    paths = get_canonical_paths(output_dir)
    groups_path = paths.module_groups
    if not groups_path.exists():
        return ""

    print(
        "[ProgressTracker] inferred --module-groups "
        f"{groups_path} from analysis directory"
    )
    return str(groups_path)


def cmd_save_core_manifest(args: argparse.Namespace) -> None:
    """Core 모듈 목록을 core-manifest.json 으로 저장.

    W1 Step 3-4 에서 Core 선정 완료 시 호출되며, W-DELTA 에서 Core 변경 감지에 사용된다.
    """
    try:
        from ..analysis_paths import get_canonical_paths
        from ..delta.spec_cache import CoreManifest, save_core_manifest
    except ImportError:  # script/installed-tools flat execution
        from analysis_paths import get_canonical_paths
        from delta.spec_cache import CoreManifest, save_core_manifest

    output_dir = Path(args.output_dir)
    paths = get_canonical_paths(output_dir)

    # --module-groups 인자 처리. 이 값이 누락되면
    # module-priority의 모듈명을 실제 파일 경로로 확장하지 못한다.
    module_groups_path = getattr(args, "module_groups", "") or ""
    if not module_groups_path:
        module_groups_path = _infer_module_groups_path(output_dir)
    if not module_groups_path:
        print(
            "[ProgressTracker] ✗ module-groups.yaml not found. "
            "모듈 경계 정보 없이 core-manifest를 저장할 수 없습니다. "
            "W1 discovery(Module Discovery)를 먼저 실행하세요."
        )
        raise SystemExit(2)

    core_files: list[str] = []
    if args.priority_file:
        priority_path = Path(args.priority_file)
        if not priority_path.exists():
            # Fallback: module-review가 생략되면
            # module-priority-reviewed.md가 없을 수 있음.
            # module-priority.md로 대체 시도
            fallback = priority_path.parent / "module-priority.md"
            if (
                priority_path.name == "module-priority-reviewed.md"
                and fallback.exists()
            ):
                print(
                    f"[ProgressTracker] ⚠ {priority_path.name} not found, "
                    f"using module-priority.md as fallback"
                )
                priority_path = fallback
        if priority_path.exists():
            workspace_root = (
                Path(args.workspace_root)
                if getattr(args, "workspace_root", "")
                else None
            )
            core_files = _parse_core_files_from_priority(
                priority_path, workspace_root, module_groups_path
            )

    analysis_scope = args.analysis_scope if args.analysis_scope is not None else None
    mode = args.mode or ""

    # module-groups.yaml의 상대경로를 output_dir 기준으로 저장
    try:
        module_groups_file = str(Path(module_groups_path).relative_to(output_dir))
    except ValueError:
        # 상대경로 변환 불가 시 절대경로 그대로 저장
        module_groups_file = module_groups_path

    manifest = CoreManifest(
        analysis_scope=analysis_scope,
        mode=mode,
        core_files=core_files,
        generated_at=datetime.now().isoformat(timespec="seconds"),
        module_groups_file=module_groups_file,
    )

    manifest_path = paths.core_manifest
    save_core_manifest(manifest_path, manifest)

    print(
        f"[ProgressTracker] save-core-manifest: {len(core_files)} core files, "
        f"module_groups={module_groups_file} → {manifest_path}"
    )


def _parse_core_files_from_priority(
    priority_path: Path,
    workspace_root: Path | None = None,
    module_groups_path: str = "",
) -> list[str]:
    """module-priority-reviewed.md에서 Core 파일 목록 추출.

    Logical Module 모드(--module-groups 제공 시)에는 첫 번째 컬럼이
    모듈 이름(예: 'user-management')일 수 있으며, 이 경우 module-groups.yaml에서
    파일 경로를 확장하여 개별 파일 경로를 core_files에 저장한다.
    """
    try:
        from ..delta.spec_cache import expand_module_to_files
    except ImportError:  # script/installed-tools flat execution
        from delta.spec_cache import expand_module_to_files

    core_files: list[str] = []
    try:
        content = priority_path.read_text(encoding="utf-8")
    except OSError:
        return core_files

    for line in content.splitlines():
        line = line.strip()
        if (
            line.startswith("|")
            and not line.startswith("| 모듈")
            and not line.startswith("|---")
        ):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts:
                raw_value = parts[0].strip().strip("`")
                if not raw_value:
                    continue
                # Logical Module 모드: 정규화 전 원본 값으로 모듈 이름 감지
                # 모듈 이름은 확장자가 없고 절대경로가 아닌 값 (예: "user-management")
                is_module_name = module_groups_path and (
                    not Path(raw_value).suffix and not os.path.isabs(raw_value)
                )
                if is_module_name:
                    expanded = expand_module_to_files(raw_value, module_groups_path)
                    if expanded:
                        # 확장된 파일 경로를 절대경로로 정규화
                        for fp in expanded:
                            norm = _normalize_core_file(fp, workspace_root)
                            if norm:
                                core_files.append(norm)
                        continue
                    # 확장 실패 시 원래 값 정규화하여 저장
                    value = _normalize_core_file(raw_value, workspace_root)
                else:
                    value = _normalize_core_file(raw_value, workspace_root)
                if value:
                    core_files.append(value)
    return _dedupe_preserve_order(core_files)


def _normalize_core_file(value: str, workspace_root: Path | None = None) -> str:
    cleaned = value.strip().strip("`")
    if not cleaned:
        return ""
    path = Path(cleaned)
    if workspace_root and not path.is_absolute():
        return str((workspace_root / path).resolve())
    return str(path.resolve()) if path.is_absolute() else cleaned
