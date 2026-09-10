#!/usr/bin/env python3
"""Spec 문서 생성 단계의 증분 업데이트 지원 캐시.

`cache_manager.py`(AST 단계)와 같은 패턴이지만, 한 단계 위 — LLM이 생성한
Module Design Card / FR 문서가 어떤 소스 파일 hash로부터 만들어졌는지를 기록한다.

이를 parse-cache(file_path → file_hash + nodes/edges)와 결합하면, 두 번째
실행 시 변경되지 않은 모듈의 spec 문서 재생성을 건너뛸 수 있다.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from ..parser import file_hash
except ImportError:  # script/installed-tools flat execution
    from parser import file_hash

SPEC_CACHE_VERSION = "1.0"
DIFF_PLAN_VERSION = "1.0"
CORE_MANIFEST_VERSION = "1.0"
SOURCE_DEPS_MAP_VERSION = "1.0"


# ── 데이터 모델 ──────────────────────────────────────────────────────────────


@dataclass
class SpecCacheEntry:
    """단일 모듈 파일의 spec 생성 캐시 항목."""

    file_path: str  # 절대 경로 (모듈 소스 파일)
    file_hash: str  # 마지막 spec 생성 시점의 SHA-256
    sdd_doc: str  # modules/<name>.md (spec_root 상대 경로)
    fr_doc: str  # functional-requirements/<name>-fr.md (없으면 빈 문자열)
    generated_at: str  # ISO 포맷
    mode: str = ""  # light | standard | detail | full | custom (생성 시점)
    is_core: bool = True  # Core/Peripheral 구분 (정보용, 삭제 기준 아님)
    source_dependencies: list[str] = field(
        default_factory=list
    )  # 문서 생성 시 참조한 소스 파일 목록

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "sdd_doc": self.sdd_doc,
            "fr_doc": self.fr_doc,
            "generated_at": self.generated_at,
            "mode": self.mode,
            "is_core": self.is_core,
            "source_dependencies": self.source_dependencies,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SpecCacheEntry:
        return cls(
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            sdd_doc=data.get("sdd_doc", ""),
            fr_doc=data.get("fr_doc", ""),
            generated_at=data.get("generated_at", ""),
            mode=data.get("mode", ""),
            is_core=data.get("is_core", True),
            source_dependencies=data.get("source_dependencies", []),
        )


@dataclass
class SpecCache:
    """전체 spec 캐시 (모듈 file_path → SpecCacheEntry)."""

    version: str = SPEC_CACHE_VERSION
    entries: dict[str, SpecCacheEntry] = field(default_factory=dict)
    mode: str = ""
    analysis_scope: int | None = None

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "mode": self.mode,
            "analysis_scope": self.analysis_scope,
            "entries": {k: v.to_dict() for k, v in self.entries.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> SpecCache:
        version = data.get("version", "")
        if version != SPEC_CACHE_VERSION:
            return cls()
        entries: dict[str, SpecCacheEntry] = {}
        for k, v in data.get("entries", {}).items():
            entries[k] = SpecCacheEntry.from_dict(v)
        return cls(
            version=version,
            entries=entries,
            mode=data.get("mode", ""),
            analysis_scope=data.get("analysis_scope"),
        )

    def get_entry(self, file_path: str) -> SpecCacheEntry | None:
        return self.entries.get(file_path)

    def upsert_entry(self, entry: SpecCacheEntry) -> None:
        self.entries[entry.file_path] = entry

    def remove_entry(self, file_path: str) -> SpecCacheEntry | None:
        return self.entries.pop(file_path, None)


# ── CoreManifest 데이터 모델 ────────────────────────────────────────────────


@dataclass
class CoreManifest:
    """Core 모듈 목록을 관리하는 매니페스트."""

    version: str = CORE_MANIFEST_VERSION
    analysis_scope: int | None = None
    mode: str = ""
    core_files: list[str] = field(default_factory=list)  # 절대 경로 목록
    generated_at: str = ""
    module_groups_file: str = ""  # module-groups.yaml 상대경로

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "analysis_scope": self.analysis_scope,
            "mode": self.mode,
            "core_files": self.core_files,
            "generated_at": self.generated_at,
            "module_groups_file": self.module_groups_file,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CoreManifest:
        # 레거시(Physical 모드) 매니페스트에 남아 있는 granularity 키는 무시한다.
        # module_groups_file 부재가 곧 레거시 산출물의 판별 기준.
        return cls(
            version=data.get("version", CORE_MANIFEST_VERSION),
            analysis_scope=data.get("analysis_scope"),
            mode=data.get("mode", ""),
            core_files=data.get("core_files", []),
            generated_at=data.get("generated_at", ""),
            module_groups_file=data.get("module_groups_file", ""),
        )


# ── SourceDepsMap 데이터 모델 ───────────────────────────────────────────────


@dataclass
class DepInfo:
    """단일 문서의 소스 의존성 정보."""

    source_files: list[str] = field(default_factory=list)
    primary_source: str = ""
    fr_doc: str = ""

    def to_dict(self) -> dict:
        return {
            "source_files": self.source_files,
            "primary_source": self.primary_source,
            "fr_doc": self.fr_doc,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DepInfo:
        return cls(
            source_files=data.get("source_files", []),
            primary_source=data.get("primary_source", ""),
            fr_doc=data.get("fr_doc", ""),
        )


@dataclass
class SourceDepsMap:
    """문서↔소스 파일 의존성 맵."""

    version: str = SOURCE_DEPS_MAP_VERSION
    built_at: str = ""
    deps: dict[str, DepInfo] = field(default_factory=dict)  # doc_path → DepInfo

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "built_at": self.built_at,
            "deps": {k: v.to_dict() for k, v in self.deps.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> SourceDepsMap:
        deps: dict[str, DepInfo] = {}
        for k, v in data.get("deps", {}).items():
            deps[k] = DepInfo.from_dict(v)
        return cls(
            version=data.get("version", SOURCE_DEPS_MAP_VERSION),
            built_at=data.get("built_at", ""),
            deps=deps,
        )


# ── 캐시 I/O ─────────────────────────────────────────────────────────────────


def load_spec_cache(cache_path: Path) -> SpecCache | None:
    """Spec 캐시 파일을 로드. 없거나 버전 불일치 시 None."""
    if not cache_path.exists():
        return None
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    # 원본 데이터의 버전을 직접 확인 (from_dict은 mismatch 시 기본 버전으로
    # 빈 캐시를 만들어 반환하므로 여기서 사전 차단)
    if data.get("version") != SPEC_CACHE_VERSION:
        return None
    return SpecCache.from_dict(data)


def save_spec_cache(cache_path: Path, cache: SpecCache) -> None:
    """원자적 저장 (tmp → rename). cache_manager.save_cache와 동일 패턴."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(cache.to_dict(), ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=str(cache_path.parent), suffix=".tmp", prefix=".spec_cache_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(cache_path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ── CoreManifest I/O ────────────────────────────────────────────────────────


def load_core_manifest(manifest_path: Path) -> CoreManifest | None:
    """Core manifest 파일을 로드. 없거나 파싱 실패 시 None."""
    if not manifest_path.exists():
        return None
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return CoreManifest.from_dict(data)


def save_core_manifest(manifest_path: Path, manifest: CoreManifest) -> None:
    """Core manifest 원자적 저장."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=str(manifest_path.parent), suffix=".tmp", prefix=".core_manifest_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(manifest_path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ── SourceDepsMap I/O ────────────────────────────────────────────────────────


def load_source_deps_map(deps_map_path: Path) -> SourceDepsMap | None:
    """Source deps map 파일을 로드. 없거나 파싱 실패 시 None."""
    if not deps_map_path.exists():
        return None
    try:
        data = json.loads(deps_map_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return SourceDepsMap.from_dict(data)


def save_source_deps_map(deps_map_path: Path, deps_map: SourceDepsMap) -> None:
    """Source deps map 원자적 저장."""
    deps_map_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(deps_map.to_dict(), ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=str(deps_map_path.parent), suffix=".tmp", prefix=".source_deps_map_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(deps_map_path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ── Source Files 파싱 ────────────────────────────────────────────────────────


def parse_source_files_section(content: str) -> list[str]:
    """Module Design Card의 Source Files 섹션을 파싱.

    지원 형식:
    1. > **Source Files**: `a.cs`, `b.cs`  (표준, 백틱)
    2. > **Source Files**: a.cs, b.cs       (백틱 생략)
    3. > **Source Files**:\n> - `a.cs`\n> - `b.cs`  (불릿 리스트)

    Returns:
        파싱된 파일 경로 목록 (중복 제거, 순서 유지)
    """
    files: list[str] = []
    seen: set[str] = set()

    # 패턴 1: > **Source Files**: 이후 같은 줄에 나열
    inline_pattern = re.compile(
        r"^\s*>\s*\*\*Source Files\*\*\s*:\s*(.+)$",
        re.MULTILINE,
    )
    inline_match = inline_pattern.search(content)
    if inline_match:
        rest = inline_match.group(1).strip()
        # 백틱으로 감싸진 파일 경로 추출
        backtick_files = re.findall(r"`([^`]+)`", rest)
        if backtick_files:
            for f in backtick_files:
                f = f.strip()
                if f and f not in seen:
                    files.append(f)
                    seen.add(f)
        else:
            # 백틱이 없으면 쉼표로 분리
            for part in rest.split(","):
                part = part.strip().strip("`").strip()
                if part and part not in seen:
                    files.append(part)
                    seen.add(part)

    # 패턴 2: > **Source Files**: 이후 불릿 리스트 (다음 줄부터)
    # > - `a.cs` 또는 > * `a.cs` 형식
    bullet_pattern = re.compile(
        r"^\s*>\s*[-*]\s+`?([^`\n]+?)`?\s*$",
        re.MULTILINE,
    )
    # Source Files 섹션 이후, 빈 줄이나 다른 섹션 전까지의 불릿 매칭
    section_start = inline_match.start() if inline_match else -1
    if section_start >= 0:
        after_section = content[section_start:]
        for match in bullet_pattern.finditer(after_section):
            f = match.group(1).strip()
            if f and f not in seen and not f.startswith("**"):
                files.append(f)
                seen.add(f)

    return files


def parse_source_tags(content: str) -> list[str]:
    """[Source: /path/file.ts:L#] 태그에서 파일 경로 추출.

    Returns:
        파일 경로 목록 (중복 제거, 순서 유지)
    """
    files: list[str] = []
    seen: set[str] = set()

    # [Source: path/to/file.ts:L##] 또는 [Source: path/to/file.ts:L##-L##]
    # L##-L## 형식도 지원 (두 번째 L 포함)
    pattern = re.compile(
        r"\[Source:\s*([^\]:]+?)(?::L\d+(?:-L?\d+)?)?\]", re.IGNORECASE
    )
    for match in pattern.finditer(content):
        f = match.group(1).strip()
        if _is_line_range_only_source(f):
            continue
        if f and f not in seen:
            files.append(f)
            seen.add(f)

    return files


def _is_line_range_only_source(value: str) -> bool:
    """Return True for source markers like ``[Source: L1-L10]`` without a file."""
    return bool(re.fullmatch(r"L\d+(?:-L?\d+)?", value, flags=re.IGNORECASE))


def _is_generated_code2spec_artifact(path: Path, workspace_root: Path) -> bool:
    """Return True for generated Code2Spec/Codex artifacts, not source inputs."""
    try:
        rel = path.resolve().relative_to(workspace_root.resolve())
    except (OSError, ValueError):
        return False
    if not rel.parts:
        return False
    return rel.parts[0] in {
        "code2spec",
        ".code-to-ast",
        ".code2spec-tools",
        ".code2spec-venv",
        ".codex",
    }


def validate_and_normalize_source_files(
    source_files: list[str],
    workspace_root: Path | None = None,
) -> list[str]:
    """파일 경로를 검증하고 정규화.

    - 존재하지 않는 경로는 환각으로 간주하여 무시 + 경고 로그
    - 상대경로/절대경로 혼용 허용, 최종적으로 절대경로로 정규화
    - 중복 제거
    """
    normalized: list[str] = []
    seen: set[str] = set()

    for f in source_files:
        p = Path(f)
        # 절대경로가 아니면 workspace_root 기준으로 resolve 시도
        if not p.is_absolute() and workspace_root is not None:
            p = (workspace_root / p).resolve()
        else:
            try:
                p = p.resolve()
            except OSError:
                continue

        if workspace_root is not None and _is_generated_code2spec_artifact(
            p, workspace_root
        ):
            continue

        abs_str = str(p)

        # 파일 존재 검증 (workspace_root가 제공된 경우에만)
        if workspace_root is not None and not p.exists():
            warnings.warn(
                f"Source file does not exist (possible hallucination): {f}",
                stacklevel=2,
            )
            continue

        if abs_str not in seen:
            normalized.append(abs_str)
            seen.add(abs_str)

    return normalized


# ── Diff 계산 ────────────────────────────────────────────────────────────────


@dataclass
class DiffPlan:
    """W-DELTA가 W2/W3에 전달하는 변경 분류 결과."""

    unchanged: list[dict]  # [{file, file_hash, sdd_doc, fr_doc}]
    changed: list[dict]  # [{file, old_hash, new_hash, sdd_doc, fr_doc}]
    new: list[dict]  # [{file, new_hash}]  (하위 호환)
    promoted: list[dict]  # [{file, new_hash}]  (이전 Core가 아닌 새 Core)
    dependent_changed: list[dict]  # [{file, sdd_doc, fr_doc, changed_dep}]
    removed: list[dict]  # [{file, sdd_doc, fr_doc, file_hash?}]
    peripheral_new: list[dict]  # [{file, new_hash}]  (HITL 선택)
    peripheral_changed: list[dict]  # [{file, old_hash, new_hash}]  (HITL 선택)
    moved: list[dict]  # [{from, to, file_hash}]  (rename/move 감지)
    invalidated: bool = False  # 캐시 무효화로 full rebuild 권장
    invalidated_reason: str = ""

    @property
    def total(self) -> int:
        return (
            len(self.unchanged)
            + len(self.changed)
            + len(self.new)
            + len(self.promoted)
            + len(self.dependent_changed)
            + len(self.removed)
            + len(self.peripheral_new)
            + len(self.peripheral_changed)
            + len(self.moved)
        )

    @property
    def needs_work(self) -> bool:
        return bool(
            self.changed
            or self.new
            or self.promoted
            or self.dependent_changed
            or self.removed
            or self.moved
        )

    @property
    def regen_ratio(self) -> float:
        """재생성 대상 비율 (changed + promoted + dependent_changed) / total_core."""
        total_core = (
            len(self.unchanged)
            + len(self.changed)
            + len(self.promoted)
            + len(self.dependent_changed)
        )
        if total_core == 0:
            return 0.0
        regen_count = (
            len(self.changed) + len(self.promoted) + len(self.dependent_changed)
        )
        return regen_count / total_core

    def to_dict(self, computed_at: str | None = None) -> dict:
        return {
            "version": DIFF_PLAN_VERSION,
            "computed_at": computed_at or datetime.now().isoformat(timespec="seconds"),
            "invalidated": self.invalidated,
            "invalidated_reason": self.invalidated_reason,
            "summary": {
                "unchanged": len(self.unchanged),
                "changed": len(self.changed),
                "new": len(self.new),
                "promoted": len(self.promoted),
                "dependent_changed": len(self.dependent_changed),
                "removed": len(self.removed),
                "peripheral_new": len(self.peripheral_new),
                "peripheral_changed": len(self.peripheral_changed),
                "moved": len(self.moved),
            },
            "unchanged_modules": self.unchanged,
            "changed_modules": self.changed,
            "new_modules": self.new,
            "promoted_modules": self.promoted,
            "dependent_changed_modules": self.dependent_changed,
            "removed_modules": self.removed,
            "peripheral_new_modules": self.peripheral_new,
            "peripheral_changed_modules": self.peripheral_changed,
            "moved_modules": self.moved,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DiffPlan:
        return cls(
            unchanged=list(data.get("unchanged_modules", [])),
            changed=list(data.get("changed_modules", [])),
            new=list(data.get("new_modules", [])),
            promoted=list(data.get("promoted_modules", [])),
            dependent_changed=list(data.get("dependent_changed_modules", [])),
            removed=list(data.get("removed_modules", [])),
            peripheral_new=list(data.get("peripheral_new_modules", [])),
            peripheral_changed=list(data.get("peripheral_changed_modules", [])),
            moved=list(data.get("moved_modules", [])),
            invalidated=bool(data.get("invalidated", False)),
            invalidated_reason=data.get("invalidated_reason", ""),
        )


def expand_module_to_files(module_name: str, module_groups_path: str) -> list[str]:
    """module-groups.yaml에서 모듈 이름에 해당하는 파일 목록을 절대경로로 반환.

    Args:
        module_name: 모듈 이름 (예: 'user-management')
        module_groups_path: module-groups.yaml 파일 경로

    Returns:
        모듈에 속한 파일의 절대경로 목록. 찾지 못하면 빈 리스트.
    """
    import yaml

    if not module_groups_path or not os.path.exists(module_groups_path):
        return []

    with open(module_groups_path, encoding="utf-8") as f:
        groups_data = yaml.safe_load(f)

    modules_list = groups_data.get("modules", [])
    for mod in modules_list:
        if mod.get("name", "") == module_name:
            return mod.get("files", [])
    return []


def normalize_path_for_matching(path: str, repo_root: Path | None = None) -> str:
    """상대경로를 절대경로로 정규화 (비교 목적).

    Args:
        path: 정규화할 파일 경로
        repo_root: 상대경로 해석 기준 루트

    Returns:
        정규화된 절대경로 문자열
    """
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.resolve())
        except OSError:
            return path
    if repo_root is not None:
        try:
            return str((repo_root / p).resolve())
        except OSError:
            return path
    # repo_root도 없고 상대경로면 슬래시 정규화만 수행
    return path.replace("\\", "/")


def compute_diff_plan(
    source_files: list[Path],
    spec_cache: SpecCache | None,
    core_manifest: CoreManifest | None = None,
    source_deps_map: SourceDepsMap | None = None,
    module_groups_path: str = "",
    repo_root: Path | None = None,
) -> DiffPlan:
    """현재 소스 파일 목록과 spec_cache를 비교해 변경 분류 plan 생성.

    Args:
        source_files: 현재 시점의 분석 대상 소스 파일 (절대경로 권장)
        spec_cache: 이전 실행에서 저장된 spec_cache (없으면 모두 new로 분류)
        core_manifest: 현재 Core 모듈 목록
        source_deps_map: 문서↔소스 의존성 맵
        module_groups_path: module-groups.yaml 경로 (Logical Module 시 모듈 이름→파일 확장)
        repo_root: 저장소 루트 경로 (상대경로 정규화용, Logical Module 시 필수)

    Returns:
        DiffPlan — unchanged / changed / new / promoted / dependent_changed /
                   removed / peripheral_new / peripheral_changed / moved
    """
    unchanged: list[dict] = []
    changed: list[dict] = []
    new: list[dict] = []
    promoted: list[dict] = []
    dependent_changed: list[dict] = []
    removed: list[dict] = []
    peripheral_new: list[dict] = []
    peripheral_changed: list[dict] = []
    moved: list[dict] = []

    # 현재 Core 파일 집합
    # core_manifest가 없으면 모든 파일을 Core로 취급 (하위 호환)
    has_core_manifest = core_manifest is not None
    if has_core_manifest:
        # module-groups 정보가 있으면 모듈 이름→파일 경로 확장
        raw_core_files = list(core_manifest.core_files)
        if module_groups_path or core_manifest.module_groups_file:
            mg_path = module_groups_path or core_manifest.module_groups_file
            expanded_files: list[str] = []
            for item in raw_core_files:
                f = item["file"] if isinstance(item, dict) else item
                # 모듈 이름인지 확인: 파일 경로에 확장자가 없으면 모듈 이름으로 간주
                if not Path(f).suffix or not os.path.isabs(f):
                    # module-groups.yaml에서 파일 목록 확장
                    module_files = expand_module_to_files(f, mg_path)
                    if module_files:
                        expanded_files.extend(module_files)
                    else:
                        # 확장 실패 시 원래 값 유지
                        expanded_files.append(f)
                else:
                    expanded_files.append(f)
            # 확장된 파일 경로를 절대경로로 정규화
            current_core: set[str] = {
                normalize_path_for_matching(fp, repo_root) for fp in expanded_files
            }
        else:
            # core_files는 list[dict] 형태: [{'file': path, 'is_core': True}, ...]
            current_core = {
                item["file"] if isinstance(item, dict) else item
                for item in raw_core_files
            }
    else:
        # core_manifest가 없으면 source_files의 모든 파일을 Core로 간주
        current_core = {str(f.resolve()) for f in source_files}

    # 이전 Core 파일 집합 (spec-cache에서 is_core=True인 항목)
    previous_core: set[str] = set()
    if spec_cache:
        for path, entry in spec_cache.entries.items():
            if entry.is_core:
                previous_core.add(path)

    # 파일 해시 맵 구축
    file_hashes: dict[str, str] = {}
    for f in source_files:
        abs_path = str(f.resolve())
        try:
            file_hashes[abs_path] = file_hash(f)
        except OSError:
            continue

    # 캐시 엔트리 맵
    cache_entries: dict[str, SpecCacheEntry] = (
        dict(spec_cache.entries) if spec_cache else {}
    )
    seen_keys: set[str] = set()

    # 변경된 파일 집합 (hash가 다른 파일)
    changed_file_set: set[str] = set()

    for file_path in source_files:
        abs_path = str(file_path.resolve())
        seen_keys.add(abs_path)
        current_hash = file_hashes.get(abs_path, "")

        if not current_hash:
            # 읽기 실패 → 변경된 것으로 간주
            entry = cache_entries.get(abs_path)
            if entry is None:
                new.append({"file": abs_path, "new_hash": ""})
            else:
                changed.append(
                    {
                        "file": abs_path,
                        "old_hash": entry.file_hash,
                        "new_hash": "",
                        "sdd_doc": entry.sdd_doc,
                        "fr_doc": entry.fr_doc,
                    }
                )
            changed_file_set.add(abs_path)
            continue

        entry = cache_entries.get(abs_path)

        if abs_path in current_core:
            # ── Core 파일 분류 ──
            if entry is None:
                # 캐시에 없고 Core → 승격 또는 신규 Core
                if not has_core_manifest:
                    # 하위 호환: Core manifest가 없는 legacy 실행에서는
                    # 기존 4분류(new) 의미를 유지한다.
                    new.append({"file": abs_path, "new_hash": current_hash})
                elif module_groups_path or core_manifest.module_groups_file:
                    # 모듈 단위 분석: 모든 모듈 내 파일이 Core이므로
                    # promoted가 아님. 캐시에 없는 파일은 추적되지 않았으므로
                    # new로 분류 (모듈 단위 집계 시 changed_file_set에 포함됨)
                    new.append({"file": abs_path, "new_hash": current_hash})
                elif abs_path in previous_core:
                    # 이전에도 Core였으나 캐시에서 누락 (비정상)
                    promoted.append({"file": abs_path, "new_hash": current_hash})
                else:
                    promoted.append({"file": abs_path, "new_hash": current_hash})
            elif entry.file_hash != current_hash:
                changed.append(
                    {
                        "file": abs_path,
                        "old_hash": entry.file_hash,
                        "new_hash": current_hash,
                        "sdd_doc": entry.sdd_doc,
                        "fr_doc": entry.fr_doc,
                    }
                )
                changed_file_set.add(abs_path)
            else:
                unchanged.append(
                    {
                        "file": abs_path,
                        "file_hash": current_hash,
                        "sdd_doc": entry.sdd_doc,
                        "fr_doc": entry.fr_doc,
                    }
                )
        else:
            # ── Peripheral 파일 분류 ──
            if entry is None:
                # 캐시에 없음 → peripheral_new
                peripheral_new.append({"file": abs_path, "new_hash": current_hash})
            elif entry.file_hash != current_hash:
                peripheral_changed.append(
                    {
                        "file": abs_path,
                        "old_hash": entry.file_hash,
                        "new_hash": current_hash,
                    }
                )
                changed_file_set.add(abs_path)
            # 캐시에 있고 hash 동일 → Peripheral이지만 이미 캐시에 있음 (강등 등)
            # 별도 분류하지 않음

    # 캐시에는 있지만 현재 파일 목록에 없는 항목 → removed
    removed_file_set: set[str] = set()
    for key, entry in cache_entries.items():
        if key in seen_keys:
            continue
        removed.append(
            {
                "file": entry.file_path,
                "sdd_doc": entry.sdd_doc,
                "fr_doc": entry.fr_doc,
                "file_hash": entry.file_hash,
            }
        )
        removed_file_set.add(key)

    # ── 간접 의존성 분류 ──
    # 변경된 파일 + 삭제된 파일 모두 의존성 무효화 트리거로 작동
    # 캐시에서 삭제된 파일 + 현재 소스에 없는 의존성 파일도 포함
    invalidated_sources = changed_file_set | removed_file_set
    if source_deps_map:
        for dep_info in source_deps_map.deps.values():
            for src_file in dep_info.source_files:
                if src_file not in seen_keys:
                    invalidated_sources.add(src_file)

    if source_deps_map:
        already_classified: set[str] = set()
        for item in changed:
            already_classified.add(item["file"])
        for item in promoted:
            already_classified.add(item["file"])

        for dep_info in source_deps_map.deps.values():
            primary = dep_info.primary_source
            if not primary or primary in already_classified:
                continue
            if primary not in current_core:
                continue
            for src_file in dep_info.source_files:
                if src_file in invalidated_sources:
                    # 이 문서를 소유한 Core 모듈을 dependent_changed에 추가
                    # 캐시에서 sdd_doc, fr_doc 정보 조회
                    cache_entry = cache_entries.get(primary)
                    dependent_changed.append(
                        {
                            "file": primary,
                            "sdd_doc": cache_entry.sdd_doc if cache_entry else "",
                            "fr_doc": cache_entry.fr_doc if cache_entry else "",
                            "changed_dep": src_file,
                        }
                    )
                    already_classified.add(primary)
                    break

    # ── moved 감지 ──
    # removed + 신규 후보 중 hash가 같은 쌍을 찾아 moved로 재분류한다.
    # 각 원본 리스트를 직접 넘겨야 moved로 확정된 항목이 중복 분류로
    # 남지 않는다.
    _detect_moved(removed, new, moved)
    _detect_moved(removed, peripheral_new, moved)
    _detect_moved(removed, promoted, moved)

    return DiffPlan(
        unchanged=unchanged,
        changed=changed,
        new=new,
        promoted=promoted,
        dependent_changed=dependent_changed,
        removed=removed,
        peripheral_new=peripheral_new,
        peripheral_changed=peripheral_changed,
        moved=moved,
    )


def aggregate_diff_plan_by_modules(
    plan: DiffPlan, module_groups_path: str, repo_root: Path | None = None
) -> DiffPlan:
    """파일 단위 DiffPlan 을 module-groups.yaml 기반으로 모듈 단위로 집계.

    Logical Module 에서는 파일이 아닌 모듈이 재생성 단위이므로,
    모듈 내 1 개 파일이라도 changed/removed 면 해당 모듈 전체를 changed 로 분류합니다.

    Args:
        plan: 파일 단위 DiffPlan
        module_groups_path: module-groups.yaml 파일 경로
        repo_root: 경로 정규화 기준 루트 (상대경로→절대경로 변환용)

    Returns:
        모듈 단위로 집계된 DiffPlan
    """
    import yaml

    if not module_groups_path or not os.path.exists(module_groups_path):
        return plan

    with open(module_groups_path, encoding="utf-8") as f:
        groups_data = yaml.safe_load(f)

    modules_list = groups_data.get("modules", [])
    if not modules_list:
        return plan

    # 모듈 이름 → 파일 목록 매핑 (정규화된 절대경로)
    module_files: dict[str, list[str]] = {}
    # 정규화된 절대경로 → 모듈 이름 매핑
    file_to_module: dict[str, str] = {}
    for mod in modules_list:
        mod_name = mod.get("name", "")
        mod_file_list = mod.get("files", [])
        normalized_files: list[str] = []
        for fp in mod_file_list:
            norm = normalize_path_for_matching(fp, repo_root)
            normalized_files.append(norm)
            file_to_module[norm] = mod_name
        module_files[mod_name] = normalized_files

    # 변경된 파일 집합 수집 (정규화된 절대경로)
    # 주의: removed 는 삭제된 파일이지 변경된 파일이 아님 - 제외
    # dependent_changed 는 직접 변경이 아닌 간접 의존성 변경이므로
    # changed_file_set 에서 제외 (별도 분류 유지)
    changed_file_set: set[str] = set()
    for item in plan.changed:
        changed_file_set.add(normalize_path_for_matching(item["file"], repo_root))
    for item in plan.new:
        changed_file_set.add(normalize_path_for_matching(item["file"], repo_root))
    for item in plan.promoted:
        changed_file_set.add(normalize_path_for_matching(item["file"], repo_root))
    for item in plan.peripheral_new:
        changed_file_set.add(normalize_path_for_matching(item["file"], repo_root))
    for item in plan.peripheral_changed:
        changed_file_set.add(normalize_path_for_matching(item["file"], repo_root))
    # dependent_changed 는 제외: 이 파일들은 직접 변경되지 않았으나
    # 참조하는 다른 파일이 변경되어 재생성 대상이 된 것임
    # 모듈 집계 시 dependent_changed 는 별도 카테고리로 유지되어야 함
    # removed 제외: 삭제된 파일은 모듈 전체를 changed 로 만들지 않음
    # moved 는 from/to 모두 현재 존재하지 않거나 새 위치이므로 제외

    # removed 파일 집합 (별도 추적 - 모듈 삭제 판단용)
    removed_file_set: set[str] = set()
    for item in plan.removed:
        removed_file_set.add(normalize_path_for_matching(item["file"], repo_root))

    # moved 파일 집합 (별도 추적)
    moved_from_set: set[str] = set()
    moved_to_set: set[str] = set()
    for item in plan.moved:
        moved_from_set.add(normalize_path_for_matching(item.get("from", ""), repo_root))
        moved_to_set.add(normalize_path_for_matching(item.get("to", ""), repo_root))

    # 모듈 단위 분류
    unchanged_modules: list[dict] = []
    changed_modules: list[dict] = []
    removed_modules: list[dict] = []
    moved_modules: list[dict] = []

    for mod_name, files in module_files.items():
        # changed_file_set 에 속하는 파일이 있는지 확인
        mod_has_change = any(norm_fp in changed_file_set for norm_fp in files)

        # removed_file_set 에 속하는 파일이 있는지 확인 (모듈 삭제 판단)
        mod_has_removed = any(norm_fp in removed_file_set for norm_fp in files)

        # moved 파일이 있는지 확인
        mod_has_moved_from = any(norm_fp in moved_from_set for norm_fp in files)
        mod_has_moved_to = any(norm_fp in moved_to_set for norm_fp in files)
        mod_has_moved = mod_has_moved_from or mod_has_moved_to

        # 분류 로직:
        # 1. moved 가 있으면 moved_modules 로 (재생성 필요)
        # 2. removed 만 있고 changed 가 없으면 removed_modules 로
        # 3. changed 가 있으면 changed_modules 로
        # 4. 없으면 unchanged_modules 로
        if mod_has_moved:
            moved_modules.append(
                {
                    "file": mod_name,
                    "files": files,
                    "category": "moved",
                }
            )
        elif mod_has_removed and not mod_has_change:
            # removed 만 있는 경우: 모듈 전체가 삭제된 것으로 간주
            removed_modules.append(
                {
                    "file": mod_name,
                    "files": files,
                    "category": "removed",
                }
            )
        elif mod_has_change or mod_has_removed:
            # changed 가 있거나, removed + changed 가 함께 있으면 changed 로 처리
            changed_modules.append(
                {
                    "file": mod_name,
                    "files": files,
                    "category": "changed",
                }
            )
        else:
            unchanged_modules.append(
                {
                    "file": mod_name,
                    "files": files,
                    "category": "unchanged",
                }
            )

    print(
        f"[delta-plan] Logical Module aggregation: "
        f"{len(unchanged_modules)} unchanged, {len(changed_modules)} changed, "
        f"{len(removed_modules)} removed, {len(moved_modules)} moved modules"
    )

    # dependent_changed 정보 유지: 모듈 단위로 재계산
    # 주의: changed_modules 에 이미 포함된 모듈은 중복 제외
    dependent_changed_modules: list[dict] = []
    if plan.dependent_changed:
        # 이미 changed/moved 로 분류된 모듈 집합
        already_in_changed: set[str] = {
            item["file"] for item in changed_modules
        }
        already_in_changed.update(item["file"] for item in moved_modules)

        # dependent_changed 파일들이 속한 모듈을 찾아서 추가
        dep_modules_seen: set[str] = set()
        for item in plan.dependent_changed:
            norm_fp = normalize_path_for_matching(item["file"], repo_root)
            mod_name = file_to_module.get(norm_fp)
            # changed/moved 에 이미 포함된 모듈은 제외
            if mod_name and mod_name not in dep_modules_seen and mod_name not in already_in_changed:
                dep_modules_seen.add(mod_name)
                # 해당 모듈의 파일 목록 가져오기
                mod_files = module_files.get(mod_name, [])
                dependent_changed_modules.append(
                    {
                        "file": mod_name,
                        "files": mod_files,
                        "category": "dependent_changed",
                    }
                )

    return DiffPlan(
        unchanged=unchanged_modules,
        changed=changed_modules,
        new=[],
        promoted=[],
        dependent_changed=dependent_changed_modules,
        removed=removed_modules,
        peripheral_new=[],
        peripheral_changed=[],
        moved=moved_modules,
        invalidated=plan.invalidated,
        invalidated_reason=plan.invalidated_reason,
    )


def _detect_moved(
    removed: list[dict],
    new_items: list[dict],
    moved: list[dict],
) -> None:
    """removed + new 중 hash가 같은 쌍을 찾아 moved로 재분류."""
    for rem in removed[:]:
        rem_hash = rem.get("file_hash", "")
        if not rem_hash:
            continue
        for new_item in new_items[:]:
            new_hash = new_item.get("new_hash", "")
            if new_hash == rem_hash:
                moved.append(
                    {
                        "from": rem["file"],
                        "to": new_item["file"],
                        "file_hash": rem_hash,
                        "sdd_doc": rem.get("sdd_doc", ""),
                        "fr_doc": rem.get("fr_doc", ""),
                    }
                )
                removed.remove(rem)
                new_items.remove(new_item)
                break


# ── Diff plan 저장 헬퍼 ─────────────────────────────────────────────────────


def save_diff_plan(diff_plan_path: Path, plan: DiffPlan) -> None:
    """diff-plan.json 원자적 저장."""
    diff_plan_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(plan.to_dict(), ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=str(diff_plan_path.parent), suffix=".tmp", prefix=".diff_plan_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(diff_plan_path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def load_diff_plan(diff_plan_path: Path) -> DiffPlan | None:
    if not diff_plan_path.exists():
        return None
    try:
        data = json.loads(diff_plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return DiffPlan.from_dict(data)
