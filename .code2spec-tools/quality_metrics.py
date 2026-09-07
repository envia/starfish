#!/usr/bin/env python3
"""Quality metrics computation for Code2Spec generated documents.

Computes 4 metrics:
1. Evidence Precision — valid [Source: ...] tags / total [Source: ...] tags
2. Source Coverage — referenced source files / total source files
3. Core Coverage — referenced core files / total core files
4. Broken Source Link Rate — broken source links / total source tags
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from .analysis_paths import get_canonical_paths
    from .delta.spec_cache import (
        load_core_manifest,
        load_source_deps_map,
    )
except ImportError:  # script/installed-tools flat execution
    from analysis_paths import get_canonical_paths
    from delta.spec_cache import (
        load_core_manifest,
        load_source_deps_map,
    )

try:
    from .progress.common import _load_json, _resolve_spec_root
    from .progress.telemetry import append_telemetry_event
except ImportError:  # script/installed-tools flat execution
    from progress.common import _load_json, _resolve_spec_root
    from progress.telemetry import append_telemetry_event


# ── 데이터 모델 ──────────────────────────────────────────────────────────────


QUALITY_METRICS_VERSION = "1.0"
QUALITY_ISSUES_VERSION = "1.0"
QUALITY_METRICS_FILE = "quality-metrics.json"
QUALITY_ISSUES_FILE = "quality-issues.json"


@dataclass
class SourceTagDetail:
    """개별 Source 태그의 검증 결과."""

    raw_tag: str           # 원본 태그 문자열 (예: "[Source: /path/file.ts:L42]")
    file_path: str         # 파싱된 파일 경로
    line_number: int | None  # 파싱된 라인 번호 (없으면 None)
    file_exists: bool      # 파일 존재 여부
    line_valid: bool       # 라인 번호가 파일 라인 수 이내인지
    is_broken: bool        # 파일이 존재하지 않거나 열 수 없음
    source_doc: str        # 이 태그가 포함된 스펙 문서 경로 (spec_root 상대)

    def to_dict(self) -> dict:
        return {
            "raw_tag": self.raw_tag,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "file_exists": self.file_exists,
            "line_valid": self.line_valid,
            "is_broken": self.is_broken,
            "source_doc": self.source_doc,
        }


@dataclass
class QualityMetrics:
    """code2spec 생성 문서의 품질 메트릭 결과."""

    version: str = QUALITY_METRICS_VERSION

    # Evidence Precision
    evidence_precision: float = 0.0   # 유효 Source 태그 수 / 전체 Source 태그 수
    total_source_tags: int = 0        # 전체 [Source: ...] 태그 수
    valid_source_tags: int = 0        # 파일 존재 + 라인 번호 범위 내 태그 수

    # Source Coverage
    source_coverage: float = 0.0     # 참조된 소스 파일 수 / 전체 소스 파일 수
    total_source_files: int = 0       # AST 파싱된 전체 소스 파일 수
    referenced_source_files: int = 0  # 스펙 문서에서 참조된 소스 파일 수

    # Core Coverage
    core_coverage: float = 0.0        # 참조된 Core 파일 수 / 전체 Core 파일 수
    total_core_files: int = 0         # Core 파일 수
    referenced_core_files: int = 0    # 스펙 문서에서 참조된 Core 파일 수

    # Core Coverage 단위: 모듈 고정
    core_coverage_unit: str = "module"
    total_core_modules: int = 0       # module-groups 전체 Core 모듈 수
    referenced_core_modules: int = 0  # 카드가 생성된 Core 모듈 수

    # Broken Source Link Rate
    broken_source_link_rate: float = 0.0  # 깨진 Source 링크 수 / 전체 Source 태그 수
    total_source_links: int = 0           # 전체 Source 태그 수
    broken_source_links: int = 0          # 파일이 존재하지 않거나 열 수 없는 Source 태그 수

    # 메타 정보
    computed_at: str = ""
    analysis_target: str = ""

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "evidence_precision": self.evidence_precision,
            "total_source_tags": self.total_source_tags,
            "valid_source_tags": self.valid_source_tags,
            "source_coverage": self.source_coverage,
            "total_source_files": self.total_source_files,
            "referenced_source_files": self.referenced_source_files,
            "core_coverage": self.core_coverage,
            "total_core_files": self.total_core_files,
            "referenced_core_files": self.referenced_core_files,
            "core_coverage_unit": self.core_coverage_unit,
            "total_core_modules": self.total_core_modules,
            "referenced_core_modules": self.referenced_core_modules,
            "broken_source_link_rate": self.broken_source_link_rate,
            "total_source_links": self.total_source_links,
            "broken_source_links": self.broken_source_links,
            "computed_at": self.computed_at,
            "analysis_target": self.analysis_target,
        }

    @classmethod
    def from_dict(cls, data: dict) -> QualityMetrics:
        return cls(
            version=data.get("version", QUALITY_METRICS_VERSION),
            evidence_precision=data.get("evidence_precision", 0.0),
            total_source_tags=data.get("total_source_tags", 0),
            valid_source_tags=data.get("valid_source_tags", 0),
            source_coverage=data.get("source_coverage", 0.0),
            total_source_files=data.get("total_source_files", 0),
            referenced_source_files=data.get("referenced_source_files", 0),
            core_coverage=data.get("core_coverage", 0.0),
            total_core_files=data.get("total_core_files", 0),
            referenced_core_files=data.get("referenced_core_files", 0),
            core_coverage_unit=data.get("core_coverage_unit", "file"),
            total_core_modules=data.get("total_core_modules", 0),
            referenced_core_modules=data.get("referenced_core_modules", 0),
            broken_source_link_rate=data.get("broken_source_link_rate", 0.0),
            total_source_links=data.get("total_source_links", 0),
            broken_source_links=data.get("broken_source_links", 0),
            computed_at=data.get("computed_at", ""),
            analysis_target=data.get("analysis_target", ""),
        )


@dataclass
class QualityGateThresholds:
    """Acceptance gate threshold values."""

    evidence_precision_min: float = 0.95
    broken_source_link_rate_max: float = 0.01
    core_coverage_min: float = 0.90
    source_coverage_drop_warn: float = 0.20

    def to_dict(self) -> dict:
        return {
            "evidence_precision_min": self.evidence_precision_min,
            "broken_source_link_rate_max": self.broken_source_link_rate_max,
            "core_coverage_min": self.core_coverage_min,
            "source_coverage_drop_warn": self.source_coverage_drop_warn,
        }


# ── I/O ──────────────────────────────────────────────────────────────────────


def save_quality_metrics(path: Path, metrics: QualityMetrics) -> None:
    """quality-metrics.json 원자적 저장."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(metrics.to_dict(), ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".quality_metrics_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def load_quality_metrics(path: Path) -> QualityMetrics | None:
    """quality-metrics.json 로드."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    return QualityMetrics.from_dict(data)


# ── Source 태그 파싱 ──────────────────────────────────────────────────────────


# [Source: /path/file.ts:L42] 또는 [Source: /path/file.ts:L42-L50] 또는 [Source: /path/file.ts]
_SOURCE_TAG_RE = re.compile(
    r"\[Source:\s*([^\]:]+?)(?::L(\d+)(?:-L?(\d+))?)?\]",
    re.IGNORECASE,
)

# 백틱 deep-link 인용: [`Sym`](src:path/file.ts#L42) — 축약형(이슈 #54) 및 전체 URL
# [`Sym`](https://host/owner/repo/blob/branch/path/file.ts#L42) 둘 다.
# code2spec-wiki deep-link 규율로 작성된 FR/모듈/챕터 인용을 [Source:]와 동일하게 집계한다.
# 라인 앵커는 host별로 #L42(github/gitlab/bitbucket·축약형) · #n42(cgit) · #l42(gerrit) · #lines-42(bitbucket range).
_DEEPLINK_TAG_RE = re.compile(
    r"\]\((?P<url>(?:src:|https?://)[^)\s]+?)#(?:L|n|l|lines-)(?P<line>\d+)(?:-[A-Za-z]?\d+)?\)",
    re.IGNORECASE,
)


def _deeplink_repo_path(url: str) -> str | None:
    """deep-link URL에서 repo-상대 파일 경로를 추출.

    축약형(`src:<repo-상대경로>`)은 경로가 곧 값이다. 전체 URL은 host별 blob/src/tree
    마커 뒤를 취한다: github(`/blob/<branch>/`)·gitlab(`/-/blob/<branch>/`)·
    bitbucket(`/src/<branch>/`)·cgit(`/tree/`). 인식 못 하면 None(집계 제외 — 기존 동작과
    동일하게 안전).
    """
    if url.lower().startswith("src:"):
        path = url[4:].split("?")[0].split("#")[0]
        return path or None
    # 프로토콜·host 제거, query/fragment 제거
    m = re.match(r"https?://[^/]+(/.*)$", url)
    if not m:
        return None
    pathname = m.group(1).split("?")[0].split("#")[0]
    for pat in (
        r"/-/blob/[^/]+/(.+)$",   # gitlab
        r"/(?:blob|src|raw)/[^/]+/(.+)$",  # github / bitbucket / raw
        r"/tree/(.+)$",           # cgit
    ):
        mm = re.search(pat, pathname)
        if mm:
            return mm.group(1)
    return None


def _parse_source_tags_with_lines(content: str) -> list[tuple[str, str, int | None]]:
    """``[Source: /path/file.ts:L#]``에서 파일 경로와 라인 번호를 모두 추출.

    쉼표로 구분된 다중 파일 참조도 개별 태그로 분리합니다:
      [Source: a.ts, b.ts] → [("a.ts", None), ("b.ts", None)]

    Returns:
        [(raw_tag, file_path, line_number)] 리스트
    """
    results: list[tuple[str, str, int | None]] = []
    seen: set[str] = set()

    for match in _SOURCE_TAG_RE.finditer(content):
        raw_content = match.group(1).strip()
        # L1-L10 형식의 라인 범위만 있는 경우 (파일 경로 없음) 건너뜀
        if re.fullmatch(r"L\d+(?:-L?\d+)?", raw_content, flags=re.IGNORECASE):
            continue

        line_str = match.group(2)
        line_number = int(line_str) if line_str else None

        raw_tag = match.group(0)

        # 쉼표로 구분된 다중 파일 참조 분리
        # 예: "vite.config.ts, src/router.tsx" → ["vite.config.ts", "src/router.tsx"]
        file_paths = [p.strip() for p in raw_content.split(",")]

        for file_path in file_paths:
            if not file_path:
                continue

            # 비파일 참조 제외: 한글/일본어 문자, 설명 텍스트가 포함된 경우
            # 파일 경로에 공백+비영어 문자가 포함되면 비파일 참조로 간주
            if re.search(r"[가-힣ㄱ-ㅎㅏ-ㅣ一-龯]", file_path):
                continue
            # "IMPORTS_FROM 엣지" 같은 설명 텍스트 포함 제외
            if re.search(r"\s+(엣지|기반|구조|기준|디렉토리|폴더|내용|참조)\b", file_path):
                continue

            # 중복 제거 (같은 파일+같은 라인)
            dedup_key = f"{file_path}:{line_number}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            results.append((raw_tag, file_path, line_number))

    # 백틱 deep-link 인용도 동일하게 집계 (code2spec-wiki deep-link 규율).
    for match in _DEEPLINK_TAG_RE.finditer(content):
        file_path = _deeplink_repo_path(match.group("url"))
        if not file_path:
            continue
        line_number = int(match.group("line"))
        dedup_key = f"{file_path}:{line_number}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        results.append((match.group(0), file_path, line_number))

    return results


# ── 검증 헬퍼 ────────────────────────────────────────────────────────────────


def _validate_source_tag(
    file_path: str,
    line_number: int | None,
    workspace_root: Path | None,
    basename_index: dict[str, list[str]] | None = None,
) -> tuple[bool, bool, bool, str | None]:
    """개별 Source 태그 검증.

    1차로 경로 기준 resolve, 실패 시 basename_index로 fallback.
    파일명이 인덱스에 유일하게 존재하면 그 파일로 간주(valid 가능),
    2개 이상(모호)이면 매칭하지 않고 broken 처리.

    Returns:
        (file_exists, line_valid, is_broken, resolved_path) 튜플
        resolved_path: 검증에 사용된 절대경로 (없으면 None)
    """
    p: Path | None = Path(file_path)

    # 상대경로면 workspace_root 기준으로 resolve
    if not p.is_absolute() and workspace_root is not None:
        p = (workspace_root / p).resolve()
    else:
        try:
            p = p.resolve()
        except OSError:
            p = None

    # 1차 경로가 존재하지 않으면 basename fallback
    if (p is None or not p.exists()) and basename_index is not None:
        candidates = basename_index.get(Path(file_path).name, [])
        if len(candidates) == 1:
            p = Path(candidates[0])
        elif len(candidates) > 1:
            # 모호한 basename → 자동 매칭 불가, broken 처리
            return False, False, True, None

    if p is None or not p.exists():
        return False, False, True, None

    resolved = str(p)

    # 디렉토리 참조 허용 (예: [Source: src/hooks/])
    if p.is_dir():
        return True, True, False, resolved

    # 파일 존재 확인
    if not p.is_file():
        return False, False, True, None

    # 라인 번호 범위 확인
    if line_number is not None:
        try:
            line_count = p.read_text(encoding="utf-8").count("\n") + 1
            if line_number < 1 or line_number > line_count:
                return True, False, False, resolved
        except OSError:
            return True, False, False, resolved

    return True, True, False, resolved


def _collect_all_source_tags(
    spec_root: Path,
) -> list[tuple[str, str, int | None, str]]:
    """spec_root 하위 모든 .md 파일에서 Source 태그 수집.

    Returns:
        [(raw_tag, file_path, line_number, source_doc_relative_path)] 리스트
    """
    results: list[tuple[str, str, int | None, str]] = []

    md_files = [
        path
        for path in spec_root.glob("**/*.md")
        if ".analysis" not in path.parts and path.name != "history.md"
    ]

    for md_file in sorted(md_files):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        try:
            rel_path = str(md_file.relative_to(spec_root))
        except ValueError:
            rel_path = md_file.name

        for raw_tag, file_path, line_number in _parse_source_tags_with_lines(content):
            results.append((raw_tag, file_path, line_number, rel_path))

    return results


def _get_total_source_files(analysis_dir: Path, workspace_root: Path | None) -> int:
    """전체 소스 파일 수 조회 (runtime-stats.json에서)."""
    stats = _load_json(get_canonical_paths(analysis_dir).runtime_stats)
    if stats:
        code_size = stats.get("code_size", {})
        total = code_size.get("total_files", 0)
        if total > 0:
            return total

    # 폴백: exporter.get_code_size() 사용
    if workspace_root:
        try:
            try:
                from .exporter import get_code_size
            except ImportError:
                from exporter import get_code_size
            code_size = get_code_size(workspace_root)
            return code_size.total_files
        except Exception:
            pass

    return 0


def _get_core_files(analysis_dir: Path) -> set[str]:
    """Core 파일 집합 조회 (core-manifest.json에서)."""
    manifest = load_core_manifest(get_canonical_paths(analysis_dir).core_manifest)
    if manifest is None:
        return set()

    # core_files는 list[str] 형태
    raw_files = manifest.core_files
    normalized: set[str] = set()
    for item in raw_files:
        f = item["file"] if isinstance(item, dict) else item
        try:
            normalized.add(str(Path(f).resolve()))
        except OSError:
            normalized.add(f)
    return normalized


def _load_core_manifest_meta(analysis_dir: Path) -> str:
    """core-manifest.json에서 module_groups_file 반환. 매니페스트가 없으면 ""."""
    manifest = load_core_manifest(get_canonical_paths(analysis_dir).core_manifest)
    if manifest is None:
        return ""
    return manifest.module_groups_file


def _resolve_module_groups_path(
    analysis_dir: Path,
    module_groups_file: str,
) -> Path:
    """module-groups.yaml의 실제 경로를 계산 (존재 여부는 확인하지 않음)."""
    group_ref = Path(module_groups_file or "module-groups.yaml")
    if group_ref.is_absolute():
        return group_ref
    if group_ref.parent != Path("."):
        return analysis_dir / group_ref
    return get_canonical_paths(analysis_dir).state_delta_dir / group_ref.name


def _load_module_groups(
    analysis_dir: Path,
    module_groups_file: str,
    workspace_root: Path | None,
) -> dict[str, list[str]]:
    """module-groups.yaml을 {module_name: [절대경로 소스 파일]} 형태로 로드.

    파일이 없거나 파싱 실패 시 빈 dict 반환.
    """
    path = _resolve_module_groups_path(analysis_dir, module_groups_file)
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}

    result: dict[str, list[str]] = {}
    for group in data.get("modules", []) or []:
        name = group.get("name")
        if not name:
            continue
        abspaths: list[str] = []
        for f in group.get("files", []) or []:
            p = Path(f)
            if not p.is_absolute() and workspace_root is not None:
                p = workspace_root / p
            try:
                abspaths.append(str(p.resolve()))
            except OSError:
                abspaths.append(str(p))
        result[name] = abspaths
    return result


def _require_module_groups(
    analysis_dir: Path,
    workspace_root: Path | None,
) -> dict[str, list[str]]:
    """module-groups.yaml을 로드하되, 없거나 비어있으면 원인별로 안내 후 중단.

    - 파일 자체가 없음: 레거시 Physical 산출물 또는 W1 미실행 → 전체 재분석 필요
    - 파일은 있으나 modules 목록이 비어있음 → Module Discovery 재실행 필요
    """
    mg_file = _load_core_manifest_meta(analysis_dir)
    groups_path = _resolve_module_groups_path(analysis_dir, mg_file)
    if not groups_path.exists():
        raise SystemExit(
            "[QualityMetrics] ✗ module-groups.yaml 파일이 없습니다 — "
            "레거시 Physical 산출물이거나 W1 미실행 상태입니다. "
            "W1 discovery 전체 재분석이 필요합니다."
        )

    module_files = _load_module_groups(analysis_dir, mg_file, workspace_root)
    if not module_files:
        raise SystemExit(
            "[QualityMetrics] ✗ module-groups.yaml의 modules 목록이 비어있습니다 — "
            "Module Discovery를 재실행하세요."
        )
    return module_files


def _generated_module_cards(spec_root: Path) -> set[str]:
    """modules/<name>.md 로 실제 생성된 모듈 이름 집합."""
    modules_dir = spec_root / "modules"
    if not modules_dir.is_dir():
        return set()
    return {p.stem for p in modules_dir.glob("*.md")}


def _build_basename_index(source_files: set[str]) -> dict[str, list[str]]:
    """{basename: [절대경로]} 인덱스 — bare filename Source 태그 fallback용."""
    idx: dict[str, list[str]] = {}
    for f in source_files:
        idx.setdefault(Path(f).name, []).append(f)
    return idx


def _get_all_source_files_for_index(
    analysis_dir: Path,
    module_files: dict[str, list[str]],
) -> set[str]:
    """basename fallback 인덱스 구성용 전체 소스 파일 절대경로 집합.

    module-groups.yaml의 모든 파일 ∪ core-manifest.core_files.
    """
    files: set[str] = set()
    for flist in module_files.values():
        files.update(flist)
    files |= _get_core_files(analysis_dir)
    return files


def _get_referenced_source_files(analysis_dir: Path) -> set[str]:
    """스펙에서 참조된 소스 파일 집합 조회 (source-deps-map.json에서)."""
    deps_map = load_source_deps_map(get_canonical_paths(analysis_dir).source_deps_map)
    if deps_map is None:
        return set()

    referenced: set[str] = set()
    for dep_info in deps_map.deps.values():
        for src_file in dep_info.source_files:
            try:
                referenced.add(str(Path(src_file).resolve()))
            except OSError:
                referenced.add(src_file)
    return referenced


# ── 메트릭 계산 ──────────────────────────────────────────────────────────────


def compute_quality_metrics(
    spec_root: Path,
    analysis_dir: Path,
    workspace_root: Path | None = None,
) -> QualityMetrics:
    """4개 메트릭을 계산하여 QualityMetrics 객체 반환.

    Args:
        spec_root: code2spec/ 경로
        analysis_dir: .analysis/ 경로
        workspace_root: 프로젝트 루트 경로
    """
    # 0. 모듈 경계 자료 로드 (module-groups.yaml 필수)
    module_files = _require_module_groups(analysis_dir, workspace_root)
    generated_cards = _generated_module_cards(spec_root)
    basename_index = _build_basename_index(
        _get_all_source_files_for_index(analysis_dir, module_files)
    )

    # 1. Source 태그 수집 및 검증
    all_tags = _collect_all_source_tags(spec_root)

    total_source_tags = len(all_tags)
    valid_source_tags = 0
    broken_source_links = 0

    # 참조된 소스 파일 추적 (Source 태그 기준)
    referenced_via_tags: set[str] = set()

    for _raw_tag, file_path, line_number, _source_doc in all_tags:
        file_exists, line_valid, is_broken, resolved = _validate_source_tag(
            file_path, line_number, workspace_root, basename_index
        )

        if file_exists and resolved is not None:
            referenced_via_tags.add(resolved)

        if is_broken:
            broken_source_links += 1
        elif file_exists and line_valid:
            valid_source_tags += 1
        elif file_exists and line_number is None:
            # 라인 번호 없는 태그는 파일 존재만으로 유효
            valid_source_tags += 1

    # 2. Source Coverage 계산 (파일 단위 — 모드 무관)
    total_source_files = _get_total_source_files(analysis_dir, workspace_root)

    # source-deps-map.json에서도 참조된 파일 수집
    referenced_via_deps = _get_referenced_source_files(analysis_dir)

    # 카드가 생성된 모듈의 멤버 파일을 referenced로 보강(멤버십)
    referenced_via_membership: set[str] = set()
    for name, flist in module_files.items():
        if name in generated_cards:
            referenced_via_membership.update(flist)

    # Source 태그 + source-deps-map + 멤버십 합집합
    all_referenced = (
        referenced_via_tags | referenced_via_deps | referenced_via_membership
    )
    # 멤버십/태그 집합이 AST 카운트(total_source_files) universe보다 클 수 있어
    # (min_lines 미만 파일 등) 참조 수와 비율을 분모 기준으로 clamp.
    referenced_source_files = (
        min(len(all_referenced), total_source_files)
        if total_source_files > 0
        else len(all_referenced)
    )

    source_coverage = (
        referenced_source_files / total_source_files
        if total_source_files > 0
        else 0.0
    )

    # 3. Core Coverage 계산 (모듈 단위): 전체 Core 모듈 중 카드가 생성된 모듈 비율
    core_files = _get_core_files(analysis_dir)
    total_core_files = len(core_files)
    referenced_core_files = len(all_referenced & core_files) if total_core_files else 0

    core_coverage_unit = "module"
    total_core_modules = len(module_files)
    referenced_core_modules = len(set(module_files) & generated_cards)
    core_coverage = (
        referenced_core_modules / total_core_modules if total_core_modules > 0 else 0.0
    )

    # 4. Evidence Precision 계산
    evidence_precision = (
        valid_source_tags / total_source_tags if total_source_tags > 0 else 0.0
    )

    # 5. Broken Source Link Rate 계산
    broken_source_link_rate = (
        broken_source_links / total_source_tags if total_source_tags > 0 else 0.0
    )

    # analysis_target 추출
    analysis_target = ""
    stats = _load_json(get_canonical_paths(analysis_dir).runtime_stats)
    if stats:
        analysis_target = stats.get("analysis_target", "") or stats.get(
            "target_path", ""
        )

    return QualityMetrics(
        version=QUALITY_METRICS_VERSION,
        evidence_precision=round(evidence_precision, 4),
        total_source_tags=total_source_tags,
        valid_source_tags=valid_source_tags,
        source_coverage=round(source_coverage, 4),
        total_source_files=total_source_files,
        referenced_source_files=referenced_source_files,
        core_coverage=round(core_coverage, 4),
        total_core_files=total_core_files,
        referenced_core_files=referenced_core_files,
        core_coverage_unit=core_coverage_unit,
        total_core_modules=total_core_modules,
        referenced_core_modules=referenced_core_modules,
        broken_source_link_rate=round(broken_source_link_rate, 4),
        total_source_links=total_source_tags,
        broken_source_links=broken_source_links,
        computed_at=datetime.now().isoformat(timespec="seconds"),
        analysis_target=analysis_target,
    )


# ── Acceptance Gate ──────────────────────────────────────────────────────────


def save_quality_issues(path: Path, data: dict) -> None:
    """quality-issues.json 원자적 저장."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), suffix=".tmp", prefix=".quality_issues_"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, str(path))
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def load_quality_issues(path: Path) -> dict | None:
    """quality-issues.json 로드."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _normalize_source_path(file_path: str, workspace_root: Path | None) -> str:
    p = Path(file_path)
    if not p.is_absolute() and workspace_root is not None:
        p = workspace_root / p
    try:
        return str(p.resolve())
    except OSError:
        return str(p)


def _source_tag_diagnostics(
    spec_root: Path,
    workspace_root: Path | None,
    basename_index: dict[str, list[str]] | None = None,
) -> tuple[list[dict], set[str]]:
    """Source 태그별 검증 상세와 참조 파일 집합을 반환."""
    diagnostics: list[dict] = []
    referenced: set[str] = set()

    for raw_tag, file_path, line_number, source_doc in _collect_all_source_tags(spec_root):
        file_exists, line_valid, is_broken, resolved = _validate_source_tag(
            file_path, line_number, workspace_root, basename_index
        )
        normalized = resolved or _normalize_source_path(file_path, workspace_root)
        if file_exists:
            referenced.add(normalized)

        reason = "valid"
        if is_broken:
            reason = "file_missing_or_unreadable"
        elif not line_valid:
            reason = "line_out_of_range"

        diagnostics.append(
            {
                "source_doc": source_doc,
                "raw_tag": raw_tag,
                "file_path": file_path,
                "normalized_path": normalized,
                "line_number": line_number,
                "file_exists": file_exists,
                "line_valid": line_valid,
                "is_broken": is_broken,
                "reason": reason,
            }
        )

    return diagnostics, referenced


def _all_referenced_sources(analysis_dir: Path, tag_references: set[str]) -> set[str]:
    return tag_references | _get_referenced_source_files(analysis_dir)


def _issue(
    *,
    metric: str,
    severity: str,
    message: str,
    affected_docs: list[str],
    repair_action: str,
    affected_sources: list[str] | None = None,
    evidence: list[dict] | None = None,
    regeneration_mode: str = "patch",
) -> dict:
    item = {
        "metric": metric,
        "severity": severity,
        "message": message,
        "affected_docs": sorted(set(affected_docs)),
        "affected_sources": sorted(set(affected_sources or [])),
        "repair_action": repair_action,
        "regeneration_mode": regeneration_mode,
    }
    if evidence:
        item["evidence"] = evidence
    return item


def evaluate_quality_gate(
    metrics: QualityMetrics,
    *,
    spec_root: Path,
    analysis_dir: Path,
    workspace_root: Path | None = None,
    run_type: str = "full",
    thresholds: QualityGateThresholds | None = None,
) -> dict:
    """Acceptance gate 판정과 targeted repair issue payload를 생성."""
    thresholds = thresholds or QualityGateThresholds()
    normalized_run_type = (run_type or "full").lower()

    # 모듈 경계 자료 로드 (module-groups.yaml 필수)
    module_files = _require_module_groups(analysis_dir, workspace_root)
    generated_cards = _generated_module_cards(spec_root)
    basename_index = _build_basename_index(
        _get_all_source_files_for_index(analysis_dir, module_files)
    )

    diagnostics, tag_references = _source_tag_diagnostics(
        spec_root, workspace_root, basename_index
    )
    all_referenced = _all_referenced_sources(analysis_dir, tag_references)
    for name, flist in module_files.items():
        if name in generated_cards:
            all_referenced.update(flist)

    # 누락 = 카드가 생성되지 않은 Core 모듈 이름
    missing_core_files = sorted(set(module_files) - generated_cards)

    issues: list[dict] = []

    invalid_tags = [d for d in diagnostics if d["is_broken"] or not d["line_valid"]]
    broken_tags = [d for d in diagnostics if d["is_broken"]]

    if metrics.evidence_precision < thresholds.evidence_precision_min:
        issues.append(
            _issue(
                metric="evidence_precision",
                severity="fail",
                message="Evidence Precision is below threshold.",
                affected_docs=[d["source_doc"] for d in invalid_tags],
                affected_sources=[d["normalized_path"] for d in invalid_tags],
                evidence=[
                    {
                        "source_doc": d["source_doc"],
                        "raw_tag": d["raw_tag"],
                        "reason": d["reason"],
                    }
                    for d in invalid_tags
                ],
                repair_action="repair_invalid_source_evidence",
                regeneration_mode="section",
            )
        )

    if metrics.broken_source_link_rate > thresholds.broken_source_link_rate_max:
        issues.append(
            _issue(
                metric="broken_source_link_rate",
                severity="fail",
                message="Broken Source Link Rate exceeded threshold.",
                affected_docs=[d["source_doc"] for d in broken_tags],
                affected_sources=[d["normalized_path"] for d in broken_tags],
                evidence=[
                    {
                        "source_doc": d["source_doc"],
                        "raw_tag": d["raw_tag"],
                        "reason": d["reason"],
                    }
                    for d in broken_tags
                ],
                repair_action="fix_broken_source_tags",
                regeneration_mode="patch",
            )
        )

    core_severity = "fail" if normalized_run_type == "full" else "warn"
    if metrics.core_coverage < thresholds.core_coverage_min:
        issues.append(
            _issue(
                metric="core_coverage",
                severity=core_severity,
                message="Core Coverage is below threshold.",
                affected_docs=[],
                affected_sources=missing_core_files,
                evidence=[
                    {"source_path": path, "reason": "missing_core_reference"}
                    for path in missing_core_files
                ],
                repair_action="regenerate_missing_core_docs",
                regeneration_mode="document",
            )
        )

    status = "PASS"
    if any(issue["severity"] == "fail" for issue in issues):
        status = "FAIL"
    elif issues:
        status = "WARN"

    allowed_docs = sorted(
        {
            doc
            for issue in issues
            for doc in issue.get("affected_docs", [])
            if doc
        }
    )

    return {
        "version": QUALITY_ISSUES_VERSION,
        "status": status,
        "computed_at": datetime.now().isoformat(timespec="seconds"),
        "analysis_target": metrics.analysis_target,
        "run_type": normalized_run_type,
        "thresholds": thresholds.to_dict(),
        "metrics": metrics.to_dict(),
        "repair_scope": {
            "allowed_docs": allowed_docs,
            "blocked_docs": [],
            "allow_full_regeneration": False,
        },
        "issues": issues,
    }


def cmd_quality_gate(args: argparse.Namespace) -> None:
    """CLI 진입점: quality-metrics.json 을 acceptance gate 로 판정."""
    output_dir = Path(args.output_dir)
    spec_root = _resolve_spec_root(output_dir)
    paths = get_canonical_paths(output_dir)
    metrics_path = paths.quality_metrics
    issues_path = paths.quality_issues
    metrics = load_quality_metrics(metrics_path)
    if metrics is None:
        print(f"[ERROR] No valid {QUALITY_METRICS_FILE} found: {metrics_path}")
        raise SystemExit(2)

    thresholds = QualityGateThresholds(
        evidence_precision_min=args.evidence_precision_min,
        broken_source_link_rate_max=args.broken_source_link_rate_max,
        core_coverage_min=args.core_coverage_min,
        source_coverage_drop_warn=args.source_coverage_drop_warn,
    )
    workspace_root = Path(args.workspace_root) if args.workspace_root else None
    result = evaluate_quality_gate(
        metrics,
        spec_root=spec_root,
        analysis_dir=output_dir,
        workspace_root=workspace_root,
        run_type=args.run_type,
        thresholds=thresholds,
    )
    save_quality_issues(issues_path, result)
    append_telemetry_event(
        output_dir,
        "quality_gate_evaluated",
        payload={
            "status": result["status"],
            "issue_count": len(result.get("issues", [])),
            "artifact_paths": [str(issues_path)],
        },
    )

    print(f"[ProgressTracker] quality-gate: {result['status']}")
    print(f"  Evidence Precision: {metrics.evidence_precision:.2%} >= {thresholds.evidence_precision_min:.2%}")
    print(f"  Broken Source Link: {metrics.broken_source_link_rate:.2%} <= {thresholds.broken_source_link_rate_max:.2%}")
    print(f"  Core Coverage:      {metrics.core_coverage:.2%} >= {thresholds.core_coverage_min:.2%}")
    print(f"  Issues: {len(result['issues'])}")
    print(f"  → {issues_path}")

    if result["status"] == "FAIL":
        raise SystemExit(2)


# ── CLI ──────────────────────────────────────────────────────────────────────


def cmd_compute_metrics(args: argparse.Namespace) -> None:
    """CLI 진입점: 메트릭 계산 후 quality-metrics.json 에 저장."""
    output_dir = Path(args.output_dir)
    spec_root = _resolve_spec_root(output_dir)
    paths = get_canonical_paths(output_dir)

    workspace_root = Path(args.workspace_root) if args.workspace_root else None

    metrics = compute_quality_metrics(spec_root, output_dir, workspace_root)

    metrics_path = paths.quality_metrics
    save_quality_metrics(metrics_path, metrics)
    append_telemetry_event(
        output_dir,
        "metrics_computed",
        payload={
            "evidence_precision": metrics.evidence_precision,
            "source_coverage": metrics.source_coverage,
            "core_coverage": metrics.core_coverage,
            "broken_source_link_rate": metrics.broken_source_link_rate,
            "artifact_paths": [str(metrics_path)],
        },
    )

    print("[ProgressTracker] compute-metrics:")
    print(f"  Evidence Precision: {metrics.evidence_precision:.2%} "
          f"({metrics.valid_source_tags}/{metrics.total_source_tags} 태그 유효)")
    print(f"  Source Coverage:    {metrics.source_coverage:.2%} "
          f"({metrics.referenced_source_files}/{metrics.total_source_files} 파일 참조)")
    if metrics.core_coverage_unit == "module":
        print(f"  Core Coverage:      {metrics.core_coverage:.2%} "
              f"({metrics.referenced_core_modules}/{metrics.total_core_modules} Core 모듈 카드)")
    else:
        print(f"  Core Coverage:      {metrics.core_coverage:.2%} "
              f"({metrics.referenced_core_files}/{metrics.total_core_files} Core 파일 참조)")
    print(f"  Broken Source Link:  {metrics.broken_source_link_rate:.2%} "
          f"({metrics.broken_source_links}/{metrics.total_source_links} 링크 깨짐)")
    print(f"  → {metrics_path}")
