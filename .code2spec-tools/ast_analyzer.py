#!/usr/bin/env python3
"""AST 심층 분석기 - PageRank + Z-score 기반 핵심 모듈 분류"""

import argparse
import json
import math
import os
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass

import networkx as nx

# ── Centrality 설정 ──────────────────────────────────────────────────────────


@dataclass
class CentralityConfig:
    """Centrality 알고리즘 설정 (PageRank 일원화)."""

    pagerank_alpha: float = 0.85  # PageRank damping factor
    pagerank_max_iter: int = 100  # PageRank 최대 반복 수


# ── indegree-fallback 전용 임계값 ───────────────────────────────────────────
# module-groups 기반 분류의 정상 경로(module-all-core)에서는 HITL 승인 경계를
# 그대로 Core로 채택하므로 이 값들은 무시된다. Module PageRank가 전부 0인 드문
# indegree-fallback 경로에서만 Z-score Core 선별에 실제로 사용된다.
_FALLBACK_Z_MULTIPLIER = 0.5
_FALLBACK_MAX_CORE = 35


# ── 파일 카테고리 가중치 ────────────────────────────────────────────────────
BUSINESS_PATTERNS = [
    "service",
    "controller",
    "handler",
    "manager",
    "usecase",
    "repository",
    "store",
    "api",
    "domain",
    "facade",
    "interactor",
    "usecase",
    "saga",
    "resolver",
    "action",
    "reducer",
    "route",
    "router",
]
UTILITY_PATTERNS = [
    "utils",
    "helpers",
    "constants",
    "config",
    "types",
    "index",
    "logger",
    "mock",
    "test",
    "spec",
    "fixture",
    "setup",
]


def get_file_weight(file_path: str) -> float:
    """파일명 패턴 기반 카테고리 가중치 반환."""
    name = os.path.basename(file_path).lower().split(".")[0]
    if any(p in name for p in BUSINESS_PATTERNS):
        return 1.5  # 비즈니스 로직 파일 boost
    if any(p in name for p in UTILITY_PATTERNS):
        return 0.1  # 유틸리티/인프라 파일 suppress
    return 1.0


# ── 프로젝트 타입 감지 ────────────────────────────────────────────────────────
def detect_project_type(repo_root: str) -> str:
    """메타파일 기반 프로젝트 타입 자동 감지."""
    # android: AndroidManifest.xml 기반 감지
    if os.path.exists(os.path.join(repo_root, "AndroidManifest.xml")) or any(
        os.path.exists(os.path.join(r, d, "AndroidManifest.xml"))
        for r, dirs, _ in os.walk(repo_root)
        for d in dirs
        if d == "main"
    ):
        return "android"
    # android: build.gradle / build.gradle.kts 기반 감지 (Android 플러그인 포함 시)
    for gradle_file in ["build.gradle", "build.gradle.kts"]:
        gradle_path = os.path.join(repo_root, gradle_file)
        if os.path.exists(gradle_path):
            try:
                content = open(gradle_path, encoding="utf-8").read()
                if (
                    "com.android.application" in content
                    or "com.android.library" in content
                ):
                    return "android"
            except Exception:
                pass
    # ios: Swift Package Manager
    if os.path.exists(os.path.join(repo_root, "Package.swift")):
        return "ios"
    # ios: Xcode project/workspace
    if any(
        d.endswith(".xcodeproj") or d.endswith(".xcworkspace")
        for r, dirs, _ in os.walk(repo_root)
        for d in dirs
    ):
        return "ios"
    # tizen
    if os.path.exists(os.path.join(repo_root, "tizen-manifest.xml")):
        return "tizen"
    # web-backend: package.json with express/fastapi/flask/django/koa/hapi/nest
    pkg_path = os.path.join(repo_root, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8") as f:
                pkg = json.load(f)
            all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            web_frameworks = {
                "express",
                "fastapi",
                "koa",
                "hapi",
                "@nestjs/core",
                "fastify",
                "restify",
            }
            if any(fw in all_deps for fw in web_frameworks):
                return "web-backend"
        except Exception:
            pass
    # python web backend: requirements.txt / pyproject.toml with flask/django/fastapi
    for req_file in ["requirements.txt", "requirements-dev.txt"]:
        req_path = os.path.join(repo_root, req_file)
        if os.path.exists(req_path):
            try:
                content = open(req_path).read().lower()
                if any(
                    fw in content
                    for fw in [
                        "flask",
                        "django",
                        "fastapi",
                        "aiohttp",
                        "tornado",
                        "sanic",
                    ]
                ):
                    return "web-backend"
            except Exception:
                pass
    # platform-framework: has setup.py or pyproject.toml with [build-system]
    if os.path.exists(os.path.join(repo_root, "setup.py")):
        return "platform-framework"
    pyproject_path = os.path.join(repo_root, "pyproject.toml")
    if os.path.exists(pyproject_path):
        try:
            content = open(pyproject_path).read()
            if "[build-system]" in content:
                return "platform-framework"
        except Exception:
            pass
    # general python
    if any(
        os.path.exists(os.path.join(repo_root, f))
        for f in ["main.py", "app.py", "run.py"]
    ):
        return "python-app"
    return "unknown"


def get_forced_core_files(project_type: str, repo_root: str, nodes: list) -> set:
    """프로젝트 타입별로 Core에 강제 포함할 파일 집합 반환."""
    forced = set()
    project_files = {n["file"] for n in nodes if n["kind"] == "File"}

    if project_type == "web-backend":
        # routes/ 또는 router/ 디렉토리 파일, route/router 패턴 파일 강제 포함
        for f in project_files:
            parts = f.replace("\\", "/").split("/")
            if any(
                p
                in (
                    "routes",
                    "route",
                    "router",
                    "routers",
                    "controllers",
                    "handlers",
                    "middlewares",
                    "middleware",
                    "middewares",
                )
                for p in parts
            ):
                forced.add(f)

    elif project_type == "android":
        # AndroidManifest.xml 파싱하여 선언된 Activity/Service/BroadcastReceiver 클래스명 기반 파일 강제 포함
        manifest_paths = []
        for root, _dirs, files in os.walk(repo_root):
            for fname in files:
                if fname == "AndroidManifest.xml":
                    manifest_paths.append(os.path.join(root, fname))
        for manifest_path in manifest_paths:
            try:
                content = open(manifest_path, encoding="utf-8").read()
                class_names = re.findall(r'android:name=["\']([^"\']+)["\']', content)
                for cls in class_names:
                    simple = cls.split(".")[-1].lower()
                    for f in project_files:
                        if simple in os.path.basename(f).lower():
                            forced.add(f)
            except Exception:
                pass

    elif project_type == "tizen":
        tizen_manifest = os.path.join(repo_root, "tizen-manifest.xml")
        if os.path.exists(tizen_manifest):
            try:
                content = open(tizen_manifest, encoding="utf-8").read()
                exec_names = re.findall(r'exec=["\']([^"\']+)["\']', content)
                entry_names = re.findall(r'entry-point=["\']([^"\']+)["\']', content)
                for name in exec_names + entry_names:
                    simple = os.path.basename(name).lower()
                    for f in project_files:
                        if simple in os.path.basename(f).lower():
                            forced.add(f)
            except Exception:
                pass

    elif project_type == "ios":
        # iOS/Swift 진입점 파일 강제 포함
        ios_entry_files = {
            "appdelegate.swift",
            "scenedelegate.swift",
            "app.swift",
            "main.swift",
        }
        for f in project_files:
            basename = os.path.basename(f).lower()
            if basename in ios_entry_files:
                forced.add(f)
        # @main 속성이 있는 Swift 파일도 진입점으로 포함
        for f in project_files:
            if f.lower().endswith(".swift"):
                try:
                    filepath = os.path.join(repo_root, f) if not os.path.isabs(f) else f
                    if os.path.exists(filepath):
                        content = open(filepath, encoding="utf-8").read()
                        if "@main" in content:
                            forced.add(f)
                except Exception:
                    pass

    elif project_type == "platform-framework":
        for f in project_files:
            if os.path.basename(f) in ("__init__.py", "index.ts", "index.js", "mod.rs"):
                parts = f.replace("\\", "/").split("/")
                if len(parts) <= 3:  # 루트 근처 파일만
                    forced.add(f)

    return forced


# ── 파싱 ────────────────────────────────────────────────────────────────────
def parse_graph_json(ast_dir):
    """graph-raw.json을 파싱하여 노드/엣지 데이터를 반환한다.

    JSON 포맷은 ast_analyzer.py가 빠르게 로드하기 위한 포맷이다.
    반환 타입은 parse_graph_raw()와 동일하게 dict 리스트이다.
    """
    json_path = os.path.join(ast_dir, "graph-raw.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"graph-raw.json not found: {json_path}")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    nodes = []
    for n in data.get("nodes", []):
        nodes.append(
            {
                "kind": n.get("kind", ""),
                "name": n.get("name", ""),
                "file": n.get("file_path", ""),
                "lines": f"{n.get('line_start', 0)}-{n.get('line_end', 0)}",
                "parent": n.get("parent_name") or None,
            }
        )

    edges = []
    for e in data.get("edges", []):
        edges.append(
            {
                "kind": e.get("kind", ""),
                "source": e.get("source", ""),
                "target": e.get("target", ""),
                "file": e.get("file_path", ""),
                "line": str(e.get("line", 0)),
            }
        )

    return nodes, edges


def parse_graph_raw(ast_dir):
    """graph-raw.json 또는 graph-raw.md를 파싱하여 노드/엣지 데이터를 반환한다.

    JSON 파일이 있으면 우선 사용 (빠른 로드), 없으면 Markdown fallback.
    """
    # JSON 우선 시도
    json_path = os.path.join(ast_dir, "graph-raw.json")
    if os.path.exists(json_path):
        try:
            return parse_graph_json(ast_dir)
        except Exception:
            pass  # JSON 파싱 실패 시 Markdown fallback

    # Markdown fallback
    graph_path = os.path.join(ast_dir, "graph-raw.md")
    if not os.path.exists(graph_path):
        raise FileNotFoundError(
            f"Neither graph-raw.json nor graph-raw.md found in: {ast_dir}"
        )

    with open(graph_path, encoding="utf-8") as f:
        content = f.read()

    nodes = []
    edges = []
    section = None

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## Nodes"):
            section = "nodes"
            continue
        elif stripped.startswith("## Edges"):
            section = "edges"
            continue
        elif stripped.startswith("## Summary"):
            section = "summary"
            continue

        if (
            not stripped.startswith("|")
            or stripped.startswith("| Kind")
            or stripped.startswith("|---")
        ):
            continue

        cells = [c.strip().strip("`") for c in stripped.split("|")[1:-1]]

        if section == "nodes" and len(cells) >= 5:
            nodes.append(
                {
                    "kind": cells[0],
                    "name": cells[1],
                    "file": cells[2],
                    "lines": cells[3],
                    "parent": cells[4] if cells[4] != "-" else None,
                }
            )
        elif section == "edges" and len(cells) >= 5:
            edges.append(
                {
                    "kind": cells[0],
                    "source": cells[1],
                    "target": cells[2],
                    "file": cells[3],
                    "line": cells[4],
                }
            )

    return nodes, edges


# ── in-degree (dead code / entry point 용, 기존 유지) ───────────────────────
def compute_in_degree(nodes, edges):
    """CALLS 엣지 기반 in-degree 계산. dead code 탐지 및 entry point 식별에 사용."""
    in_degree = defaultdict(int)
    calls_edges = [e for e in edges if e["kind"] == "CALLS"]
    for e in calls_edges:
        in_degree[e["target"]] += 1
    return dict(in_degree)


# ── TypeScript 경로 해석 ──────────────────────────────────────────────────────
_RESOLVE_EXTENSIONS = [".ts", ".tsx", ".js", ".jsx"]


def _load_ts_aliases(repo_root: str) -> dict:
    """tsconfig.json에서 compilerOptions.paths alias 로드 (예: @/ → src/)."""
    aliases = {}
    for name in ["tsconfig.json", "tsconfig.base.json", "tsconfig.app.json"]:
        tsconfig_path = os.path.join(repo_root, name)
        if not os.path.exists(tsconfig_path):
            continue
        try:
            with open(tsconfig_path, encoding="utf-8") as f:
                content = re.sub(r"//[^\n]*", "", f.read())  # // 주석 제거
            cfg = json.loads(content)
            opts = cfg.get("compilerOptions", {})
            base_url = opts.get("baseUrl", ".")
            for alias, targets in opts.get("paths", {}).items():
                clean_alias = alias.rstrip("/*")
                if targets:
                    clean_target = targets[0].rstrip("/*")
                    abs_target = os.path.normpath(
                        os.path.join(repo_root, base_url, clean_target)
                    )
                    aliases[clean_alias] = abs_target
            break
        except Exception:
            continue
    return aliases


def _try_file(path: str, project_files_set: set) -> str | None:
    """경로에 확장자를 붙이거나 /index를 붙여 프로젝트 파일 매칭 시도."""
    if path in project_files_set:
        return path
    for ext in _RESOLVE_EXTENSIONS:
        if path + ext in project_files_set:
            return path + ext
        idx = path + "/index" + ext
        if idx in project_files_set:
            return idx
    return None


def _resolve_import(
    source_file: str,
    target: str,
    project_files_set: set,
    stem_index: dict,
    alias_map: dict,
    repo_root: str,
) -> str | None:
    """Import target(alias/상대경로/네임스페이스)를 실제 프로젝트 파일 상대경로로 해석."""
    # 1. alias 해석 (예: @/foo/bar → src/foo/bar.ts)
    for alias_prefix, alias_abs in alias_map.items():
        if target == alias_prefix or target.startswith(alias_prefix + "/"):
            rest = target[len(alias_prefix) :].lstrip("/")
            abs_path = os.path.join(alias_abs, rest)
            rel = _try_file(os.path.relpath(abs_path, repo_root), project_files_set)
            if rel:
                return rel

    # 2. 상대 경로 해석 (./foo, ../bar)
    if target.startswith("./") or target.startswith("../"):
        source_dir = os.path.dirname(os.path.join(repo_root, source_file))
        abs_target = os.path.normpath(os.path.join(source_dir, target))
        rel = _try_file(os.path.relpath(abs_target, repo_root), project_files_set)
        if rel:
            return rel

    # 3. C# 네임스페이스 해석 (예: MyApp.Services → Services/*.cs)
    #    네임스페이스를 디렉토리 경로로 해석하거나 파일명 stem과 매칭
    if "." in target and not target.startswith("."):
        # C# namespace: MyApp.Services.UserService → stem "UserService"
        # 또는 using MyApp.Services; → Services/ 디렉토리 내 파일들
        namespace_parts = target.split(".")

        # 3-1. 디렉토리 기반 매칭 (뒤에서부터 디렉토리 경로 시도)
        # 예: Samsung.USS.DemoPlay.Log → Log/ 디렉토리 내 파일들
        for i in range(len(namespace_parts) - 1, -1, -1):
            # 네임스페이스 뒷부분을 디렉토리 경로로 간주
            dir_path = "/".join(namespace_parts[i:])
            # 해당 디렉토리 내 파일들 찾기
            for f in project_files_set:
                f_normalized = f.replace("\\", "/")
                if f_normalized.startswith(dir_path + "/"):
                    return f

        # 3-2. stem 매칭 (기존 로직)
        # 뒤에서부터 stem 매칭 시도 (더 구체적인 이름 우선)
        for i in range(len(namespace_parts) - 1, -1, -1):
            stem = namespace_parts[i].split(",")[0].strip()  # generic 쉼표 제거
            if stem:
                matches = stem_index.get(stem, [])
                if len(matches) == 1:
                    return matches[0]
                # 여러 매칭이면 경로 일치율로 선택
                if len(matches) > 1:
                    # 소스 파일과 같은 디렉토리 계층 구조를 가진 파일 우선
                    source_parts = source_file.replace("\\", "/").split("/")
                    best_match = None
                    best_score = -1
                    for m in matches:
                        match_parts = m.replace("\\", "/").split("/")
                        # 공통 prefix 길이 계산
                        common_len = 0
                        for j in range(min(len(source_parts) - 1, len(match_parts))):
                            if source_parts[j] == match_parts[j]:
                                common_len += 1
                            else:
                                break
                        if common_len > best_score:
                            best_score = common_len
                            best_match = m
                    if best_match:
                        return best_match

    # 4. stem 유일 매칭 (최후 수단)
    stem = os.path.basename(target).split(".")[0]
    matches = stem_index.get(stem, [])
    if len(matches) == 1:
        return matches[0]

    return None


# ── 파일 의존성 그래프 ────────────────────────────────────────────────────────
def build_file_graph(nodes, edges, repo_root: str = ""):
    """IMPORTS_FROM + CALLS 엣지로 파일 단위 DiGraph 구성.

    CALLS 엣지는 qualified name 형식("path/file.cs::Class.Method")에서
    파일 경로를 추출하여 파일 간 의존성을 생성한다.
    """
    project_files = {
        n["file"] for n in nodes if n["kind"] == "File" and _is_project_file(n["file"])
    }
    stem_index: dict[str, list[str]] = defaultdict(list)
    for file_path in project_files:
        stem_index[os.path.splitext(os.path.basename(file_path))[0]].append(file_path)
    alias_map = _load_ts_aliases(repo_root) if repo_root else {}

    G = nx.DiGraph()
    for e in edges:
        if e["kind"] == "IMPORTS_FROM":
            src = e["source"]
            tgt = (
                _resolve_import(
                    src,
                    e["target"],
                    project_files,
                    stem_index,
                    alias_map,
                    repo_root,
                )
                if repo_root
                else e["target"]
            )
        elif e["kind"] == "CALLS":
            # Qualified name에서 파일 경로 추출
            src = _extract_file_from_qualified(e["source"])
            tgt = _extract_file_from_qualified(e["target"])
        elif e["kind"] == "IPC":
            # IPC edges: source is qualified name, target is external process/service
            src = _extract_file_from_qualified(e["source"])
            tgt = e["target"]  # IPC target is the external process/service name
            if src and tgt:
                G.add_edge(src, tgt)
            continue
        else:
            continue
        if src and tgt and src != tgt:
            G.add_edge(src, tgt)
    return G


# ── 공통 유틸 ─────────────────────────────────────────────────────────────────
def _is_project_file(path: str) -> bool:
    """외부 라이브러리가 아닌 실제 프로젝트 파일 여부 판별 (확장자 존재 기준)."""
    return "." in os.path.basename(path)


def _extract_file_from_qualified(name: str) -> str | None:
    """Qualified name에서 파일 경로를 추출.

    Qualified name 형식: "path/to/file.cs::ClassName.MethodName"
    반환: "path/to/file.cs" 또는 None
    """
    if "::" in name:
        return name.split("::")[0]
    return None


def _make_file_entry(file_path: str, score: float, ep_files: set) -> dict:
    """Core/Peripheral 항목 딕셔너리 생성."""
    category = (
        "business"
        if get_file_weight(file_path) > 1.0
        else "utility" if get_file_weight(file_path) < 1.0 else "neutral"
    )
    if file_path in ep_files:
        category = "entry-point"
    return {
        "file": file_path,
        "centrality_score": round(score, 6),
        "category": category,
    }


def _apply_zscore_threshold(ranked, ep_files, z_multiplier, max_core):
    """Z-score 임계값 + entry-point 자동 포함 + MAX_CORE 상한 적용."""
    values = [s for _, s in ranked]
    if len(values) < 2:
        threshold = 0.0
    else:
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        threshold = mean + z_multiplier * std

    core_files = {f for f, s in ranked if s >= threshold} | ep_files
    if len(core_files) > max_core:
        # ep_files 우선 포함, 남은 슬롯을 ranked 순서로 채움
        non_ep_ranked = [f for f, _ in ranked if f not in ep_files]
        remaining = max(0, max_core - len(ep_files))
        core_files = ep_files | set(non_ep_ranked[:remaining])
        # ep_files 자체가 max_core 초과 시 ranked 기준으로 자름
        if len(core_files) > max_core:
            core_files = {f for f, _ in ranked[:max_core]}

    core = [_make_file_entry(f, s, ep_files) for f, s in ranked if f in core_files]
    peripheral = [
        _make_file_entry(f, s, ep_files) for f, s in ranked if f not in core_files
    ]
    return core, peripheral


# ── Fallback: IMPORTS_FROM in-degree (소규모/단순 그래프용) ──────────────────
def _classify_by_imports_indegree(
    nodes,
    edges,
    entry_points,
    z_multiplier=1.0,
    max_core=20,
    forced_core=None,
    repo_root="",
):
    """소규모·단순 그래프 fallback: IMPORTS_FROM + CALLS in-degree 기반 분류.

    Betweenness Centrality가 모두 0인 경우(선형·팬-인 그래프)에 자동 사용됨.
    IMPORTS_FROM이 해석되지 않으면 CALLS 엣지 기반으로 fallback.
    외부 라이브러리(math, sys 등)는 제외하고 프로젝트 파일만 대상으로 한다.
    """
    ep_files = {ep["file"] for ep in entry_points} | (forced_core or set())

    # 실제 프로젝트 파일만 (확장자 있는 경로)
    project_files = {
        n["file"] for n in nodes if n["kind"] == "File" and _is_project_file(n["file"])
    }
    if not project_files:
        return [], []

    stem_index: dict[str, list[str]] = defaultdict(list)
    for file_path in project_files:
        stem_index[os.path.splitext(os.path.basename(file_path))[0]].append(file_path)

    alias_map = _load_ts_aliases(repo_root) if repo_root else {}

    # 1차: IMPORTS_FROM 기반 in-degree 계산
    import_count: dict[str, int] = defaultdict(int)
    for e in edges:
        if e["kind"] != "IMPORTS_FROM":
            continue
        target = e["target"]
        resolved = (
            _resolve_import(
                e["source"],
                target,
                project_files,
                stem_index,
                alias_map,
                repo_root,
            )
            if repo_root
            else target
        )
        if resolved in project_files:
            import_count[resolved] += 1

    # IMPORTS_FROM으로 해석된 파일이 있으면 그대로 사용
    if any(count > 0 for count in import_count.values()):
        scored = {f: import_count.get(f, 0) for f in project_files}
    else:
        # 2차 fallback: CALLS 엣지 기반 파일 in-degree 계산
        # (C# 등 네임스페이스 기반 import가 해석되지 않는 경우)
        calls_count: dict[str, int] = defaultdict(int)
        for e in edges:
            if e["kind"] != "CALLS":
                continue
            # Qualified name에서 파일 경로 추출
            tgt_file = _extract_file_from_qualified(e["target"])
            if tgt_file and tgt_file in project_files:
                calls_count[tgt_file] += 1
        scored = {f: calls_count.get(f, 0) for f in project_files}

    ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    return _apply_zscore_threshold(ranked, ep_files, z_multiplier, max_core)


# ── 순수 Python PageRank (numpy/scipy 의존 없음) ──────────────────────────
def _pagerank_pure(G, alpha=0.85, max_iter=100, tol=1.0e-6):
    """순수 Python PageRank 구현. numpy/scipy 의존성 없이 동작.

    Power iteration 방식으로 O(V+E) per iteration.
    networkx.pagerank와 동일한 알고리즘이지만 scipy 미설치 환경에서도 동작.
    """
    try:
        return nx.pagerank(G, alpha=alpha, max_iter=max_iter, tol=tol)
    except (ImportError, ModuleNotFoundError):
        pass  # scipy/numpy 없음 → 직접 구현 사용

    nodes = list(G.nodes)
    N = len(nodes)
    if N == 0:
        return {}

    node_idx = {n: i for i, n in enumerate(nodes)}
    # 인접 리스트 구성
    out_degree = [0] * N
    in_neighbors: list[list[int]] = [[] for _ in range(N)]
    for u, v in G.edges():
        ui, vi = node_idx[u], node_idx[v]
        out_degree[ui] += 1
        in_neighbors[vi].append(ui)
    # 무방향 그래프: 양방향 엣지
    if not G.is_directed():
        for u, v in G.edges():
            ui, vi = node_idx[u], node_idx[v]
            in_neighbors[ui].append(vi)
            out_degree[vi] += 1

    # 초기값: 1/N
    rank = [1.0 / N] * N
    dangling_sum = sum(1.0 / N for i in range(N) if out_degree[i] == 0)

    for _ in range(max_iter):
        new_rank = [0.0] * N
        # dangling 노드 기여
        dangling_contrib = alpha * dangling_sum / N
        for i in range(N):
            new_rank[i] = (1.0 - alpha) / N + dangling_contrib
            for j in in_neighbors[i]:
                if out_degree[j] > 0:
                    new_rank[i] += alpha * rank[j] / out_degree[j]

        # 수렴 확인
        err = sum(abs(new_rank[i] - rank[i]) for i in range(N))
        rank = new_rank
        dangling_sum = sum(rank[i] for i in range(N) if out_degree[i] == 0)
        if err < tol:
            break

    return {nodes[i]: rank[i] for i in range(N)}


# ── PageRank 기반 분류 ──────────────────────────────────────────────────────
def _classify_by_pagerank(
    nodes,
    edges,
    entry_points,
    z_multiplier=1.0,
    max_core=20,
    forced_core=None,
    repo_root="",
    alpha=0.85,
    max_iter=100,
):
    """PageRank 기반 핵심 모듈 분류. O(V+E) 시간복잡도로 대규모 그래프에 적합.

    Args:
        alpha: PageRank damping factor (기본값: 0.85)
        max_iter: PageRank 최대 반복 수 (기본값: 100)

    Returns:
        (core, peripheral, method) — method="pagerank"
    """
    G = build_file_graph(nodes, edges, repo_root=repo_root)
    if len(G.nodes) == 0:
        return [], [], "pagerank"

    ep_files = {ep["file"] for ep in entry_points} | (forced_core or set())

    # PageRank 계산 (undirected로 변환하여 안정성 확보)
    if G.is_directed():
        U = G.to_undirected()
    else:
        U = G
    pr = _pagerank_pure(U, alpha=alpha, max_iter=max_iter)

    # 가중치 적용
    weighted = {f: pr.get(f, 0.0) * get_file_weight(f) for f in G.nodes}

    # Fallback: 모든 pagerank=0 → IMPORTS_FROM in-degree 사용
    if all(v == 0.0 for v in weighted.values()):
        print("[AST Analyzer] ⚠ PageRank 모두 0 → IMPORTS_FROM in-degree fallback 사용")
        core, peripheral = _classify_by_imports_indegree(
            nodes,
            edges,
            entry_points,
            z_multiplier,
            max_core,
            forced_core=forced_core,
            repo_root=repo_root,
        )
        return core, peripheral, "indegree-fallback"

    ranked = sorted(weighted.items(), key=lambda x: x[1], reverse=True)
    core, peripheral = _apply_zscore_threshold(ranked, ep_files, z_multiplier, max_core)
    return core, peripheral, "pagerank"


# ── 핵심 모듈 분류 (파일 단위, PageRank + Z-score) ─────────────────────
def classify_files_by_centrality(
    nodes,
    edges,
    entry_points,
    z_multiplier=1.0,
    max_core=20,
    project_type="unknown",
    repo_root="",
    centrality_config=None,
):
    """PageRank + Z-score 기반 핵심 모듈 분류.

    PageRank(O(V+E))를 기본 알고리즘으로 사용하여 일관된 성능 보장.

    Args:
        z_multiplier: Z-score 임계값 배수 (0.5=광범위, 1.0=기본, 2.0=집중)
        max_core: Core 모듈 최대 수 (안전 상한)
        project_type: 프로젝트 타입 (web-backend, android, tizen 등)
        repo_root: 프로젝트 루트 경로
        centrality_config: CentralityConfig 인스턴스 (None이면 기본값)

    Returns:
        (core, peripheral, method) — 각 항목: {"file", "centrality_score", "category"}
        method: "pagerank" | "indegree-fallback"
    """
    if centrality_config is None:
        centrality_config = CentralityConfig()

    # 프로젝트 타입별 강제 Core 파일
    forced_core = get_forced_core_files(project_type, repo_root, nodes)
    if forced_core:
        print(
            f"[AST Analyzer] Forced core files ({project_type}): {len(forced_core)}개"
        )

    return _classify_by_pagerank(
        nodes,
        edges,
        entry_points,
        z_multiplier=z_multiplier,
        max_core=max_core,
        forced_core=forced_core,
        repo_root=repo_root,
        alpha=centrality_config.pagerank_alpha,
        max_iter=centrality_config.pagerank_max_iter,
    )


# ── 모듈 단위 분류 (--granularity module 용) ──────────────────────────────
def classify_modules_by_groups(
    nodes,
    edges,
    module_groups_path,
    entry_points,
    z_multiplier=1.0,
    max_core=20,
    project_type="unknown",
    repo_root="",
    centrality_config=None,
):
    """module-groups.yaml 기반 Logical Module 단위 PageRank 분류.

    각 모듈 그룹의 파일 점수를 합산하여 모듈 단위 PageRank 계산.
    모듈 간 의존성 그래프를 구성하고 PageRank + Z-score 로 Core 식별.

    Args:
        module_groups_path: module-groups.yaml 파일 경로
        나머지 인자는 classify_files_by_centrality 와 동일

    Returns:
        (core, peripheral, method) — 각 항목: {"file", "centrality_score", "category", "files"}
        method: "module-pagerank" | "module-indegree-fallback"
    """
    import yaml

    if centrality_config is None:
        centrality_config = CentralityConfig()

    if not module_groups_path or not os.path.exists(module_groups_path):
        raise SystemExit(
            "[AST Analyzer] ✗ module-groups.yaml not found — "
            "Module Discovery(W1) 산출물이 필요합니다. 전체 재분석을 먼저 실행하세요."
        )

    with open(module_groups_path, encoding="utf-8") as f:
        groups_data = yaml.safe_load(f)

    modules_list = groups_data.get("modules", [])
    if not modules_list:
        raise SystemExit(
            "[AST Analyzer] ✗ module-groups.yaml has no modules — "
            "Module Discovery(W1) 산출물이 비어 있습니다. 전체 재분석을 먼저 실행하세요."
        )

    # 1. 파일 단위 그래프 구성
    G = build_file_graph(nodes, edges, repo_root=repo_root)

    # 2. 파일 → 모듈 매핑 구성
    file_to_module: dict[str, str] = {}
    module_files: dict[str, list[str]] = {}
    for mod in modules_list:
        mod_name = mod.get("name", "")
        mod_file_list = mod.get("files", [])
        module_files[mod_name] = mod_file_list
        for fp in mod_file_list:
            # 정규화: 앞의 슬래시 제거, 역슬래시 → 슬래시
            normalized = fp.replace("\\", "/").lstrip("/")
            file_to_module[normalized] = mod_name

    # 3. 모듈 간 의존성 그래프 구성
    MG = nx.DiGraph()
    for mod_name in module_files:
        MG.add_node(mod_name)

    for src_file in G.nodes:
        src_mod = file_to_module.get(src_file)
        if not src_mod:
            continue
        for tgt_file in G.successors(src_file):
            tgt_mod = file_to_module.get(tgt_file)
            if not tgt_mod or tgt_mod == src_mod:
                continue
            MG.add_edge(src_mod, tgt_mod)

    print(
        f"[AST Analyzer] Module graph: {MG.number_of_nodes()} modules, {MG.number_of_edges()} inter-module edges"
    )

    # 4. 모듈 단위 PageRank 계산
    if MG.number_of_nodes() == 0:
        return [], [], "module-pagerank"

    ep_files = {ep["file"] for ep in entry_points}
    # Entry point 가 포함된 모듈
    forced_core = set()
    for ep_file in ep_files:
        mod = file_to_module.get(ep_file)
        if mod:
            forced_core.add(mod)

    # 프로젝트 타입별 강제 core 파일이 속한 모듈도 포함
    file_forced = get_forced_core_files(project_type, repo_root, nodes)
    for ff in file_forced:
        mod = file_to_module.get(ff)
        if mod:
            forced_core.add(mod)

    if forced_core:
        print(
            f"[AST Analyzer] Forced core modules ({project_type}): {len(forced_core)}개"
        )

    if MG.is_directed():
        MU = MG.to_undirected()
    else:
        MU = MG
    pr = _pagerank_pure(
        MU,
        alpha=centrality_config.pagerank_alpha,
        max_iter=centrality_config.pagerank_max_iter,
    )

    # 모듈 가중치: 파일 수 기반 (큰 모듈일수록 중요도 약간 boost)
    weighted = {}
    for mod_name in module_files:
        file_count = len(module_files[mod_name])
        weight = 1.0 + (file_count * 0.05)  # 파일당 0.05 boost
        weighted[mod_name] = pr.get(mod_name, 0.0) * weight

    # Fallback
    if all(v == 0.0 for v in weighted.values()):
        print("[AST Analyzer] ⚠ Module PageRank 모두 0 → in-degree fallback")
        ranked = sorted(weighted.items(), key=lambda x: x[1], reverse=True)
        # in-degree fallback: 모듈 간 엣지 in-degree
        mod_indegree = defaultdict(int)
        for _, tgt in MG.edges():
            mod_indegree[tgt] += 1
        weighted = {mod: mod_indegree.get(mod, 0) for mod in module_files}
        ranked = sorted(weighted.items(), key=lambda x: x[1], reverse=True)
        core_mods, peripheral_mods = _apply_zscore_threshold(
            ranked, forced_core, z_multiplier, max_core
        )
        core = _convert_module_entries(core_mods, module_files, forced_core)
        peripheral = _convert_module_entries(peripheral_mods, module_files, forced_core)
        return core, peripheral, "module-indegree-fallback"

    ranked = sorted(weighted.items(), key=lambda x: x[1], reverse=True)

    # Logical Module: 모든 모듈을 Core로 분류
    # 사용자가 HITL 리뷰에서 승인한 모듈 경계이므로 Core/Peripheral 분류 생략
    print("[AST Analyzer] Logical Module: 모든 모듈을 Core로 분류 (HITL 승인 경계)")

    core = []
    for mod_name, score in ranked:
        is_forced = mod_name in forced_core
        category = "entry-point" if is_forced else "core"
        files = module_files.get(mod_name, [])
        # module-groups.yaml에서 rationale/confidence 추출
        rationale = ""
        confidence = 0.0
        for mod in modules_list:
            if mod.get("name") == mod_name:
                rationale = mod.get("rationale", "")
                hitl = mod.get("hitl_review", "")
                if hitl and "confidence:" in hitl:
                    try:
                        confidence = float(hitl.split("confidence:")[-1].strip())
                    except (ValueError, IndexError):
                        pass
                break
        core.append(
            {
                "file": mod_name,
                "centrality_score": round(score, 6),
                "category": category,
                "files": files,
                "rationale": rationale,
                "confidence": confidence,
            }
        )

    return core, [], "module-all-core"


def _convert_module_entries(module_entries, module_files, forced_core):
    """모듈 단위 Core/Peripheral 항목을 파일 단위와 호환되는 형식으로 변환."""
    result = []
    for entry in module_entries:
        mod_name = entry["file"]  # _apply_zscore_threshold 가 "file" 키를 사용
        score = entry["centrality_score"]
        category = entry["category"]
        files = module_files.get(mod_name, [])
        result.append(
            {
                "file": mod_name,
                "centrality_score": score,
                "category": category,
                "files": files,
            }
        )
    return result


# ── function 단위 분류 (--granularity function 용, 기존 유지) ────────────────
def classify_modules(in_degree, nodes):
    """in-degree 상위 20%를 core, 나머지를 peripheral로 분류한다. (function 단위)"""
    func_class_nodes = [n for n in nodes if n["kind"] in ("Function", "Class")]
    scored = []
    for n in func_class_nodes:
        name = n["name"]
        deg = in_degree.get(name, 0)
        scored.append(
            {"name": name, "kind": n["kind"], "file": n["file"], "in_degree": deg}
        )
    scored.sort(key=lambda x: x["in_degree"], reverse=True)
    if not scored:
        return [], []
    threshold_idx = max(1, math.ceil(len(scored) * 0.2))
    return scored[:threshold_idx], scored[threshold_idx:]


# ── dead code 탐지 ────────────────────────────────────────────────────────────
def detect_dead_code(in_degree, nodes):
    """in-degree=0 + Function 타입 + 이름이 main/index/handler/constructor 아닌 것."""
    exclude_names = {"main", "index", "handler", "constructor", "default"}
    dead = []
    for n in nodes:
        if n["kind"] != "Function":
            continue
        name = n["name"]
        if name.lower() in exclude_names:
            continue
        if any(
            kw in name.lower()
            for kw in ["route", "handler", "middleware", "main", "index"]
        ):
            continue
        if in_degree.get(name, 0) == 0:
            dead.append({"name": name, "file": n["file"], "lines": n["lines"]})
    return dead


# ── dependency heatmap ───────────────────────────────────────────────────────
def build_dependency_heatmap(edges):
    """IMPORTS_FROM + CALLS 엣지 기반 파일별 의존성 횟수 계산.

    IMPORTS_FROM: 네임스페이스/모듈 기반 의존성
    CALLS: 함수 호출 기반 파일 의존성 (qualified name에서 파일 경로 추출)
    """
    dep_count: dict[str, int] = defaultdict(int)

    for e in edges:
        if e["kind"] == "IMPORTS_FROM":
            # 네임스페이스/모듈 기반 의존성
            dep_count[e["target"]] += 1
        elif e["kind"] == "CALLS":
            # CALLS 엣지에서 파일 경로 추출하여 카운트
            tgt_file = _extract_file_from_qualified(e["target"])
            if tgt_file:
                dep_count[tgt_file] += 1
        elif e["kind"] == "IPC":
            # IPC edges: count external process/service dependencies
            dep_count[e["target"]] += 1

    return dict(dep_count)


def build_dependency_edges(edges):
    """(source → target) 방향 의존 엣지와 그 가중치(횟수) 집계.

    build_dependency_heatmap 이 target 별 피의존 횟수(노드 카운트)만 남기는 것과 달리,
    이 함수는 방향성 있는 관계 엣지 자체를 보존한다. dependency heatmap/matrix 를
    그리려면 노드 카운트뿐 아니라 이 엣지(누가 무엇에 의존하는가)가 필요하다.

    반환: {(source_file, target): weight}
    """
    edge_weight: dict[tuple[str, str], int] = defaultdict(int)

    for e in edges:
        kind = e["kind"]
        if kind == "IMPORTS_FROM":
            src = e.get("source", "")
            tgt = e["target"]
        elif kind == "CALLS":
            # CALLS 엣지: 양쪽 qualified name 에서 파일 경로 추출
            src = _extract_file_from_qualified(e.get("source", ""))
            tgt = _extract_file_from_qualified(e["target"])
        elif kind == "IPC":
            src = _extract_file_from_qualified(e.get("source", ""))
            tgt = e["target"]  # 외부 프로세스/서비스명
        else:
            continue
        if src and tgt and src != tgt:
            edge_weight[(src, tgt)] += 1

    return dict(edge_weight)


# ── entry points ─────────────────────────────────────────────────────────────
def find_entry_points(in_degree, nodes):
    """in-degree=0인 Function 중 route/handler 관련 또는 File 노드의 진입점 식별."""
    entry_points = []
    file_nodes = [n for n in nodes if n["kind"] == "File"]
    for n in file_nodes:
        file_path = n["file"]
        if any(
            kw in file_path.lower()
            for kw in ["route", "app.", "index.", "server.", "main."]
        ):
            entry_points.append(
                {"name": n["name"], "file": n["file"], "type": "file-entry"}
            )
    for n in nodes:
        if n["kind"] != "Function":
            continue
        name = n["name"]
        deg = in_degree.get(name, 0)
        if deg == 0 and any(
            kw in name.lower() for kw in ["route", "handler", "middleware"]
        ):
            entry_points.append(
                {"name": name, "file": n["file"], "type": "function-entry"}
            )
    return entry_points


# ── 파일 출력 ─────────────────────────────────────────────────────────────────
def write_module_priority(
    core, peripheral, output_dir, granularity="module", method="module-pagerank"
):
    """module-priority.md (Core만) + peripheral-modules.md (참고용) 분리 출력."""
    if granularity == "module":
        if method == "module-all-core":
            header = (
                "| 모듈 | centrality_score | category | files | confidence | 근거 |"
            )
            sep = "|------|-----------------|----------|-------|-----------|------|"
            desc = "Logical Module (HITL 승인 경계) — 모든 모듈 Core 분류"

            def row(m):
                files_str = ", ".join(m.get("files", []))
                confidence = m.get("confidence", 0.0)
                rationale = m.get("rationale", "")
                # rationale 이 너무 길면 자름
                if len(rationale) > 80:
                    rationale = rationale[:77] + "..."
                return f"| {m['file']} | {m['centrality_score']} | {m['category']} | {files_str} | {confidence} | {rationale} |"

        else:
            header = "| 모듈 | centrality_score | category | files |"
            sep = "|------|-----------------|----------|-------|"
            if method == "module-pagerank":
                desc = "Logical Module PageRank × module_weight, Z-score 기반 Core 선별"
            elif method == "module-indegree-fallback":
                desc = "Logical Module in-degree fallback, Z-score 기반 Core 선별"
            else:
                desc = "Logical Module 기반 Core 선별"

            def row(m):
                files_str = ", ".join(m.get("files", []))
                return f"| {m['file']} | {m['centrality_score']} | {m['category']} | {files_str} |"

    else:
        header = "| Name | Kind | File | In-Degree |"
        sep = "|------|------|------|-----------|"
        desc = "CALLS 엣지 in-degree 상위 20% = Core  |  granularity=function"

        def row(m):
            return f"| {m['name']} | {m['kind']} | {m['file']} | {m['in_degree']} |"

    # Core만 module-priority.md에 출력 (LLM이 읽는 파일)
    core_path = os.path.join(output_dir, "module-priority.md")
    core_lines = [
        "# Module Priority\n",
        f"분석 기준: {desc}\n",
        f"Core: {len(core)}개\n",
        "",
        header,
        sep,
    ]
    for m in core:
        core_lines.append(row(m))
    with open(core_path, "w", encoding="utf-8") as f:
        f.write("\n".join(core_lines) + "\n")
    print(f"  -> {core_path}")

    # Peripheral은 별도 파일에 참고용으로 출력 (W2 분석 대상 아님)
    peri_path = os.path.join(output_dir, "peripheral-modules.md")
    peri_lines = [
        "# Peripheral Modules (참고용)\n",
        "> W2 분석 대상 아님. 중심성이 낮아 Core에서 제외된 파일 목록.\n",
        f"Peripheral: {len(peripheral)}개\n",
        "",
        header,
        sep,
    ]
    for m in peripheral:
        peri_lines.append(row(m))
    with open(peri_path, "w", encoding="utf-8") as f:
        f.write("\n".join(peri_lines) + "\n")
    print(f"  -> {peri_path}")


def write_dead_code(dead, output_dir):
    """dead-code.md 출력."""
    path = os.path.join(output_dir, "dead-code.md")
    lines = [
        "# Dead Code 탐지 결과\n",
        "기준: in-degree=0 + Function 타입 + 진입점/생성자 제외\n",
        f"탐지 건수: {len(dead)}개\n",
        "",
        "| Name | File | Lines |",
        "|------|------|-------|",
    ]
    for d in dead:
        lines.append(f"| {d['name']} | {d['file']} | {d['lines']} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  -> {path}")


def write_dependency_heatmap(heatmap, output_dir, edge_weights=None):
    """dependency-heatmap.mmd (Mermaid graph) 출력 — 노드(피의존 횟수) + 관계 엣지.

    노드는 top 30 피의존 파일을 카운트/색상과 함께 표기하고, edge_weights 가 주어지면
    hotspot(top 노드) 으로 향하는 (source → target) 의존을 가중치 라벨과 함께 그린다.
    edge_weights 가 None 이면 노드만 출력(기존 동작 유지).
    """
    path = os.path.join(output_dir, "dependency-heatmap.mmd")
    sorted_deps = sorted(heatmap.items(), key=lambda x: x[1], reverse=True)
    top_deps = sorted_deps[:30]
    top_targets = {t for t, _ in top_deps}

    def _sid(name):
        return re.sub(r"[^a-zA-Z0-9_]", "_", name)

    lines = ["graph LR"]
    declared = set()
    for target, count in top_deps:
        safe_id = _sid(target)
        declared.add(safe_id)
        label = target.replace('"', "'")
        size = min(count, 10)
        lines.append(f'  {safe_id}["{label} ({count})"]')
        if size >= 5:
            lines.append(f"  style {safe_id} fill:#f66,stroke:#333")
        elif size >= 3:
            lines.append(f"  style {safe_id} fill:#fc6,stroke:#333")

    # 관계 엣지: hotspot(top 노드)로 향하는 의존을 가중치와 함께 표기.
    # 가독성을 위해 가중치 상위 40개 엣지로 제한한다.
    if edge_weights:
        hot_edges = sorted(
            (
                (src, tgt, weight)
                for (src, tgt), weight in edge_weights.items()
                if tgt in top_targets
            ),
            key=lambda x: x[2],
            reverse=True,
        )[:40]
        for src, tgt, weight in hot_edges:
            s_id, t_id = _sid(src), _sid(tgt)
            if s_id not in declared:
                declared.add(s_id)
                lines.append(f'  {s_id}["{src.replace(chr(34), chr(39))}"]')
            lines.append(f'  {s_id} -->|"{weight}"| {t_id}')

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  -> {path}")


def write_entry_points(entry_points, output_dir):
    """entry-points.md 출력."""
    path = os.path.join(output_dir, "entry-points.md")
    lines = [
        "# Entry Points (진입점)\n",
        f"탐지 건수: {len(entry_points)}개\n",
        "",
        "| Name | File | Type |",
        "|------|------|------|",
    ]
    for ep in entry_points:
        lines.append(f"| {ep['name']} | {ep['file']} | {ep['type']} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  -> {path}")


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AST 심층 분석기 - PageRank 기반 핵심 모듈 분류"
    )
    parser.add_argument(
        "--ast-dir", required=True, help="graph-raw.md가 위치한 디렉토리"
    )
    parser.add_argument("--output-dir", required=True, help="분석 결과 저장 디렉토리")
    parser.add_argument(
        "--granularity",
        choices=["function", "module"],
        default="module",
        help="모듈 분류 단위: module(도메인/기능 단위, 기본값), function(함수/클래스 단위)",
    )
    parser.add_argument(
        "--module-groups",
        default="",
        help="module-groups.yaml 경로 (--granularity module 시 필수)",
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="프로젝트 루트 경로 (프로젝트 타입 자동 감지에 사용)",
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"[AST Analyzer] Parsing {args.ast_dir}/graph-raw.md ...")
    nodes, edges = parse_graph_raw(args.ast_dir)
    print(f"  Nodes: {len(nodes)}, Edges: {len(edges)}")

    print("[AST Analyzer] Computing in-degree (dead code / entry points용) ...")
    in_degree = compute_in_degree(nodes, edges)

    print("[AST Analyzer] Finding entry points ...")
    entry_points = find_entry_points(in_degree, nodes)

    # 프로젝트 타입 감지
    repo_root = args.repo_root or os.getcwd()
    project_type = detect_project_type(repo_root)
    print(f"[AST Analyzer] Project type detected: {project_type}")

    if args.granularity == "module":
        print("[AST Analyzer] Classifying modules by Logical Module PageRank ...")
        centrality_config = CentralityConfig()
        # z_multiplier/max_core 는 indegree-fallback 경로에서만 유효 (상수 정의 참조)
        core, peripheral, method = classify_modules_by_groups(
            nodes,
            edges,
            args.module_groups,
            entry_points,
            z_multiplier=_FALLBACK_Z_MULTIPLIER,
            max_core=_FALLBACK_MAX_CORE,
            project_type=project_type,
            repo_root=repo_root,
            centrality_config=centrality_config,
        )
    else:
        print("[AST Analyzer] Classifying functions by in-degree ...")
        core, peripheral = classify_modules(in_degree, nodes)
        method = "function-indegree"

    write_module_priority(
        core, peripheral, args.output_dir, granularity=args.granularity, method=method
    )

    print("[AST Analyzer] Detecting dead code ...")
    dead = detect_dead_code(in_degree, nodes)
    write_dead_code(dead, args.output_dir)

    print("[AST Analyzer] Building dependency heatmap ...")
    heatmap = build_dependency_heatmap(edges)
    heatmap_edges = build_dependency_edges(edges)
    write_dependency_heatmap(heatmap, args.output_dir, heatmap_edges)

    write_entry_points(entry_points, args.output_dir)

    print("\n[AST Analyzer] Complete.")
    print(f"  Core modules: {len(core)}")
    print(f"  Peripheral modules: {len(peripheral)}")
    print(f"  Dead code: {len(dead)}")
    print(f"  Entry points: {len(entry_points)}")
    print(f"  Dependency targets: {len(heatmap)}")


if __name__ == "__main__":
    main()
