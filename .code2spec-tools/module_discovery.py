#!/usr/bin/env python3
"""LLM Module Discovery - AST 그래프 기반으로 Logical Module 경계 발견."""

from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass, field
from pathlib import PurePosixPath

try:
    from .config_loader import ModuleGroup, ModuleGroupConfig
    from .module_coverage import expand_patterns, normalize_path
except ImportError:  # script/installed-tools flat execution
    from config_loader import ModuleGroup, ModuleGroupConfig
    from module_coverage import expand_patterns, normalize_path


@dataclass
class DiscoveredModule:
    """LLM 이 발견한 모듈."""
    name: str
    files: list[str] = field(default_factory=list)
    rationale: str = ""
    confidence: float = 0.0
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    unmatched_patterns: list[str] = field(default_factory=list)
    broad_patterns: list[str] = field(default_factory=list)

    def to_module_group(self) -> ModuleGroup:
        """ModuleGroup 으로 변환."""
        return ModuleGroup(
            name=self.name,
            files=self.files,
            rationale=self.rationale,
            hitl_review=f"confidence: {self.confidence}",
        )


class ModuleDiscovery:
    """LLM 기반 Module Discovery 엔진."""

    def __init__(self, ast_dir: str, output_dir: str):
        self.ast_dir = ast_dir
        self.output_dir = output_dir
        self._nodes: list[dict] = []
        self._edges: list[dict] = []
        self._files: list[str] = []
        self._repo_root: str | None = None

    def load_graph(self) -> None:
        """AST 그래프 로드 (graph-summary.json 우선, 대용량 graph-raw.json 회피).

        graph-summary.json (수십 KB)이 있으면 파일 목록과 요약 통계만 로드.
        없으면 graph-raw.json (수백 MB)으로 fallback.
        """
        summary_path = os.path.join(self.ast_dir, 'graph-summary.json')
        json_path = os.path.join(self.ast_dir, 'graph-raw.json')
        md_path = os.path.join(self.ast_dir, 'graph-raw.md')

        if os.path.exists(summary_path):
            # 경량 요약 파일 로드 (수십 KB)
            with open(summary_path, encoding='utf-8') as f:
                data = json.load(f)
            # 파일 목록 직접 사용
            raw_files = data.get('files', [])
            self._repo_root = self._infer_repo_root(raw_files)
            self._files = self._normalize_paths(raw_files)
            # 요약 통계로 node/edge kind 카운트만 설정
            self._node_kinds = data.get('node_kinds', {})
            self._edge_kinds = data.get('edge_kinds', {})
            self._total_nodes = data.get('metadata', {}).get('total_nodes', 0)
            self._total_edges = data.get('metadata', {}).get('total_edges', 0)
            # _nodes/_edges는 빈 리스트 (프롬프트 생성에 불필요)
            self._nodes = []
            self._edges = []
        elif os.path.exists(json_path):
            # 전체 graph-raw.json 로드 (fallback, 수백 MB)
            with open(json_path, encoding='utf-8') as f:
                data = json.load(f)
            self._nodes = data.get('nodes', [])
            self._edges = data.get('edges', [])
            # 파일 목록 추출
            raw_files = [
                n.get('file_path', n.get('file', ''))
                for n in self._nodes
                if n.get('kind') == 'File'
            ]
            self._repo_root = self._infer_repo_root(raw_files)
            self._files = self._normalize_paths(raw_files)
        elif os.path.exists(md_path):
            self._parse_graph_md(md_path)
            raw_files = [
                n.get('file_path', n.get('file', ''))
                for n in self._nodes
                if n.get('kind') == 'File'
            ]
            self._repo_root = self._infer_repo_root(raw_files)
            self._files = self._normalize_paths(raw_files)
        else:
            raise FileNotFoundError(f"No graph-summary.json, graph-raw.json, or graph-raw.md in {self.ast_dir}")

    def _parse_graph_md(self, md_path: str) -> None:
        """graph-raw.md 파싱 (fallback)."""
        with open(md_path, encoding='utf-8') as f:
            f.read()

        # 간단한 파싱 - 실제 구현은 ast_analyzer.py 의 parse_graph_raw 참고
        self._nodes = []
        self._edges = []
        # TODO: Implement full MD parsing if needed

    def _infer_repo_root(self, paths: list[str]) -> str | None:
        """Infer a stable repository root from absolute File node paths."""
        absolute_paths = [normalize_path(p) for p in paths if normalize_path(p).startswith('/')]
        if not absolute_paths:
            return None

        common_root = os.path.commonpath(absolute_paths)
        if common_root in ('', '/'):
            return None
        if os.path.splitext(common_root)[1]:
            common_root = os.path.dirname(common_root)

        # If every file is under a conventional source directory, commonpath can
        # become /repo/src. Step back to /repo so output remains src/foo.ts.
        if os.path.basename(common_root) in ('src', 'lib', 'app', 'main', 'tests', 'test', 'scripts', 'public'):
            common_root = os.path.dirname(common_root)
        return normalize_path(common_root) or None

    def _normalize_paths(self, paths: list[str]) -> list[str]:
        """절대경로를 repo-relative에 가깝게 정규화."""
        inferred_root = self._repo_root or self._infer_repo_root(paths)
        normalized = []
        for raw in paths:
            p = normalize_path(raw)
            if not p:
                continue
            if p.startswith('/') and inferred_root:
                try:
                    rel = os.path.relpath(p, inferred_root).replace('\\', '/')
                    if rel and not rel.startswith('..') and rel != '.':
                        p = rel
                    else:
                        p = self._fallback_normalize_absolute_path(p)
                except ValueError:
                    p = self._fallback_normalize_absolute_path(p)
            elif '/code2spec-example/' in p:
                p = p.split('/code2spec-example/', 1)[1]
            elif p.startswith('/'):
                p = self._fallback_normalize_absolute_path(p)
            normalized.append(normalize_path(p))
        return sorted({p for p in normalized if p})

    def _fallback_normalize_absolute_path(self, path: str) -> str:
        """Best-effort absolute path fallback when repo root cannot be inferred."""
        p = normalize_path(path)
        if '/code2spec-example/' in p:
            return p.split('/code2spec-example/', 1)[1]
        parts = p.split('/')
        for i, part in enumerate(parts):
            if part in ('src', 'lib', 'app', 'main', 'tests', 'test', 'scripts', 'public'):
                return '/'.join(parts[i:])
        return os.path.basename(p)

    def get_graph_summary(self) -> dict:
        """그래프 요약 정보.

        graph-summary.json에서 로드한 경우 _nodes/_edges가 비어있으므로
        캐시된 _node_kinds/_edge_kinds/_total_nodes/_total_edges를 사용.
        """
        if self._nodes:
            # graph-raw.json에서 로드한 경우: 실시간 계산
            node_kinds = {}
            for n in self._nodes:
                kind = n.get('kind', 'Unknown')
                node_kinds[kind] = node_kinds.get(kind, 0) + 1
            edge_kinds = {}
            for e in self._edges:
                kind = e.get('kind', 'Unknown')
                edge_kinds[kind] = edge_kinds.get(kind, 0) + 1
            return {
                'total_nodes': len(self._nodes),
                'total_edges': len(self._edges),
                'file_count': len(self._files),
                'node_kinds': node_kinds,
                'edge_kinds': edge_kinds,
            }
        else:
            # graph-summary.json에서 로드한 경우: 캐시된 통계 사용
            return {
                'total_nodes': getattr(self, '_total_nodes', 0),
                'total_edges': getattr(self, '_total_edges', 0),
                'file_count': len(self._files),
                'node_kinds': getattr(self, '_node_kinds', {}),
                'edge_kinds': getattr(self, '_edge_kinds', {}),
            }

    def build_prompt(
        self,
        template: str = 'A',
        prompt_file_limit: int = 1000,
        large_repo_mode: str = 'auto',
        hierarchy_max_modules: int = 100,
    ) -> str:
        """LLM 프롬프트 생성.

        ``large_repo_mode`` controls only the prompt used when the file-count
        threshold is reached. Small repositories keep the flat file-list prompt.
        """
        if prompt_file_limit < 0:
            raise ValueError("prompt_file_limit must be >= 0")
        if large_repo_mode not in {"auto", "hierarchy", "semantic"}:
            raise ValueError("large_repo_mode must be one of: auto, hierarchy, semantic")
        if hierarchy_max_modules < 1:
            raise ValueError("hierarchy_max_modules must be >= 1")

        summary = self.get_graph_summary()
        if template == 'B':
            return self._build_prompt_b(
                summary,
                prompt_file_limit=prompt_file_limit,
                large_repo_mode=large_repo_mode,
                hierarchy_max_modules=hierarchy_max_modules,
            )
        return self._build_prompt_a(
            summary,
            prompt_file_limit=prompt_file_limit,
            large_repo_mode=large_repo_mode,
            hierarchy_max_modules=hierarchy_max_modules,
        )

    def _build_prompt_a(
        self,
        summary: dict,
        prompt_file_limit: int = 1000,
        large_repo_mode: str = 'auto',
        hierarchy_max_modules: int = 100,
    ) -> str:
        """프롬프트 A: 파일 목록 또는 large-repo Logical Module Discovery."""
        total_files = len(self._files)
        if prompt_file_limit == 0 or total_files < prompt_file_limit:
            return self._build_prompt_full_list(summary, prompt_file_limit)
        if large_repo_mode in {"auto", "hierarchy"}:
            return self._build_prompt_logical_hierarchy(
                summary,
                prompt_file_limit,
                max_modules=hierarchy_max_modules,
            )
        return self._build_prompt_directory_summary(summary, prompt_file_limit)

    def _build_prompt_b(
        self,
        summary: dict,
        prompt_file_limit: int = 1000,
        large_repo_mode: str = 'auto',
        hierarchy_max_modules: int = 100,
    ) -> str:
        """프롬프트 B: 그래프 + 코드 스니펫 (TODO 구현)."""
        return self._build_prompt_a(
            summary,
            prompt_file_limit=prompt_file_limit,
            large_repo_mode=large_repo_mode,
            hierarchy_max_modules=hierarchy_max_modules,
        )

    def _build_prompt_full_list(self, summary: dict, prompt_file_limit: int) -> str:
        shown_files = self._files if prompt_file_limit == 0 else self._files[:prompt_file_limit]
        files_not_listed = len(self._files) - len(shown_files)
        files_text = '\n'.join(shown_files)
        prompt_mode = 'flat-full-list'

        return f"""# Task: Logical Module Boundary Discovery

## Context
You are a senior software architect analyzing a project.
Your task is to discover human-readable Logical Module boundaries from the project file list.

## Project Information
- **Total Files**: {summary['file_count']}
- **Prompt Mode**: {prompt_mode}
- **Prompt File Limit**: {prompt_file_limit}
- **Files Listed In Prompt**: {len(shown_files)}
- **Files Not Listed**: {files_not_listed}
- **AST Nodes**: {summary['total_nodes']} ({', '.join(f'{k}: {v}' for k, v in summary['node_kinds'].items())})
- **AST Edges**: {summary['total_edges']} ({', '.join(f'{k}: {v}' for k, v in summary['edge_kinds'].items())})

## File List
All project files are listed below. Your YAML must cover every listed file exactly once.

```
{files_text}
```

## Task Request
Based on the file structure and dependency hints, propose Logical Module boundaries.
Prefer product/domain/function boundaries over purely technical groupings.

### Criteria for Grouping
1. **Functional Cohesion**: Files that work together should be in the same module
2. **Architecture Layers**: Consider layers (Components, Contexts, Hooks, Services, Utils)
3. **Domain Boundaries**: Look for domain-specific clusters (User, Task, Settings, etc.)
4. **Reviewability**: Module names and boundaries should be understandable by humans

## Output Format
You MUST output ONLY in the following YAML format:

```yaml
modules:
  - name: "module-name"
    files:
      - "src/path/to/file1.tsx"
      - "src/path/to/file2.tsx"
    rationale: "Why these files are grouped together"
    confidence: 0.85
```

### Rules
- Assign every listed file to exactly one module.
- Do not omit listed files.
- Do not invent file paths.
- Do not include files that are not present in the file list.
- Module names must be kebab-case (e.g., "user-management", "task-core").
- Do NOT create an "other" module unless explicitly instructed.
- Provide meaningful names for all modules.
- Include confidence score (0.0-1.0) for each module.
"""

    def _build_prompt_directory_summary(self, summary: dict, prompt_file_limit: int) -> str:
        directory_summary = self._render_directory_summary()
        prompt_mode = 'directory-summary'
        return f"""# Task: Logical Module Boundary Discovery (Directory Summary Mode)

## Context
You are a senior software architect analyzing a large project.
The project has reached the configured prompt file limit, so the full file list is compressed into directory summaries.
Your task is to propose human-readable Logical Module boundaries using directory/path patterns.

## Project Information
- **Total Files**: {summary['file_count']}
- **Prompt Mode**: {prompt_mode}
- **Prompt File Limit**: {prompt_file_limit}
- **Files Listed In Prompt**: 0 full-list entries; representative samples are shown by directory
- **Full File List Entries Omitted**: {len(self._files)}
- **AST Nodes**: {summary['total_nodes']} ({', '.join(f'{k}: {v}' for k, v in summary['node_kinds'].items())})
- **AST Edges**: {summary['total_edges']} ({', '.join(f'{k}: {v}' for k, v in summary['edge_kinds'].items())})

## Warning
The full file list is not printed. Do not invent paths.
Use include/exclude patterns or directory paths. Python will expand patterns against the known file manifest and validate full coverage.

## Directory Summary
{directory_summary}

## Task Request
Propose Logical Module boundaries using directory and glob patterns.
Prefer product/domain/function boundaries over raw directory names when possible.

## Output Format
You MUST output ONLY in the following YAML format:

```yaml
modules:
  - name: "task-management"
    include:
      - "src/components/tasks/**"
      - "src/contexts/Task*.ts*"
      - "src/hooks/useTask*.ts"
    exclude:
      - "src/components/tasks/**/*.test.*"
    rationale: "Task creation, rendering, sorting, editing, and task state management"
    confidence: 0.86
```

### Rules
- Use `include` / `exclude` patterns instead of listing every file.
- Directory paths are allowed and mean all files under that directory.
- Do not use overly broad patterns such as `src/**`, `**/*`, or `**/*.ts` as module includes.
- Use individual file paths only for boundary exceptions.
- Module names must be kebab-case and semantically meaningful.
- Do NOT create placeholder names like `shared-ui-2` or `settings-2`.
- Explain how tests, styles, constants, types, and config files are assigned.
- Python will reject missing files, duplicate files, unmatched patterns, and overly broad patterns.
"""

    def _build_prompt_logical_hierarchy(
        self,
        summary: dict,
        prompt_file_limit: int,
        *,
        max_modules: int,
    ) -> str:
        hierarchy_max_entries = 80
        summary_max_dirs = 25
        summary_sample_size = 3
        directory_summary = self._render_directory_summary(
            max_dirs=summary_max_dirs,
            sample_size=summary_sample_size,
        )
        hierarchy_overview = self._render_hierarchy_overview(max_entries=hierarchy_max_entries)
        prompt_mode = 'logical-hierarchy'
        return f"""# Task: Logical Hierarchy Module Discovery

## Context
You are reviewing a large repository where the full file list is too long for reliable semantic file-by-file review.
Your task is to derive human-reviewable logical modules from the directory hierarchy.

## Project Information
- **Total Files**: {summary['file_count']}
- **Prompt Mode**: {prompt_mode}
- **Prompt File Limit**: {prompt_file_limit}
- **Files Listed In Prompt**: 0 full-list entries; representative samples are shown by directory
- **Full File List Entries Omitted**: {len(self._files)}
- **Maximum Module Count**: {max_modules}
- **Hierarchy Overview Max Entries**: {hierarchy_max_entries}
- **Directory Summary Max Dirs**: {summary_max_dirs}
- **Representative Files Per Directory**: {summary_sample_size}
- **AST Nodes**: {summary['total_nodes']} ({', '.join(f'{k}: {v}' for k, v in summary['node_kinds'].items())})
- **AST Edges**: {summary['total_edges']} ({', '.join(f'{k}: {v}' for k, v in summary['edge_kinds'].items())})

## Hierarchy Policy
Use directory hierarchy as the primary module boundary. This is not a flat semantic review.
Prefer stable directory-level modules over inferred cross-cutting product workflows.

### Boundary Rules
1. Choose module boundaries at directory depth 2-3 by default.
2. Do not use overly broad roots such as `src`, `src/**`, `ui`, `ui/**`, `**/*`, or extension-wide globs.
3. Do not split every leaf directory into its own module; merge sibling leaf directories when they are one review surface.
4. Only merge across distant directories when names strongly match, such as `ConfluenceBuilder` with `useSkill.ts` and `model/skill.ts`.
5. Do not turn generated/vendor/bundle directories into business logical modules. If they must be covered, group them as support/generated artifacts with a non-business name such as `support-generated-artifacts`.
6. Do not infer names like `design-system-bundle` only from paths such as `ds-bundle`; directory names are structural evidence, not final domain names.
7. Keep shared UI foundation, app shell/config, backend runtime/config, backend data, backend realtime, and test/logging support separate when the hierarchy clearly shows those surfaces.
8. Use include/exclude patterns. Python will expand them against the full known file manifest and reject missing, duplicate, unknown, unmatched, empty, or overly broad modules.
9. Produce no more than the maximum module count. If preserving meaningful boundaries would require more modules, flag that conflict for human review instead of merging unrelated areas.

## Hierarchy Overview
{hierarchy_overview}

## Directory Summary
This section is intentionally capped. Use it as representative evidence only; module include/exclude patterns will be validated against the full known manifest outside the LLM prompt.

{directory_summary}

## Output Format
You MUST output ONLY YAML in this shape:

```yaml
modules:
  - name: "ui-chat-experience"
    include:
      - "ui/components/Chat"
      - "ui/components/ChatWindow"
      - "ui/components/MessageInputActions"
      - "ui/hooks/useSearchState.ts"
    exclude:
      - "ui/components/ChatWindow/*.test.tsx"
    rationale: "Chat/search UI directories and strongly named supporting hooks"
    confidence: 0.86
```

### Review Checklist
- Produce no more than {max_modules} modules. If preserving meaningful boundaries would require more modules, flag that conflict for human review instead of merging unrelated areas.
- Every known file must be covered exactly once after pattern expansion.
- Prefer directory paths over long file lists.
- Use file paths only for root files and boundary exceptions.
- Explain whether tests, styles, constants, generated files, and config files stay with their directory module or move to support/generated modules.
- Generated/vendor/bundle paths should be labeled as support artifacts, not product/domain modules.
"""

    def _render_directory_summary(self, max_dirs: int | None = None, sample_size: int = 12) -> str:
        """Render compact directory inventory for large prompts."""
        by_dir: dict[str, list[str]] = {}
        for f in self._files:
            directory = os.path.dirname(f) or "."
            by_dir.setdefault(directory, []).append(f)

        entries = sorted(by_dir.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        visible_entries = entries if max_dirs is None else entries[:max_dirs]

        lines: list[str] = []
        for directory, files in visible_entries:
            ext_counts = Counter(PurePosixPath(f).suffix or "<none>" for f in files)
            ext_text = ", ".join(f"{ext} {count}" for ext, count in ext_counts.most_common(6))
            keywords = self._keywords_for_files(files)
            lines.append(f"### {directory}/ ({len(files)} files)")
            lines.append(f"Extensions: {ext_text}")
            if keywords:
                lines.append(f"Likely keywords: {', '.join(keywords[:8])}")
            lines.append("Representative files:")
            for f in sorted(files)[:sample_size]:
                lines.append(f"- {f}")
            if len(files) > sample_size:
                lines.append(f"... {len(files) - sample_size} more")
            lines.append("")
        if max_dirs is not None and len(by_dir) > max_dirs:
            lines.append(f"... {len(by_dir) - max_dirs} more directories omitted from summary")
        return "\n".join(lines).rstrip()

    def _render_hierarchy_overview(self, max_depth: int = 3, max_entries: int | None = None) -> str:
        """Render bounded directory tree counts for hierarchy review."""
        counts: Counter[str] = Counter()
        for file_path in self._files:
            parts = PurePosixPath(file_path).parts[:-1]
            if not parts:
                counts['.'] += 1
                continue
            for depth in range(1, min(len(parts), max_depth) + 1):
                counts['/'.join(parts[:depth])] += 1

        def sort_key(directory: str) -> tuple[int, int, str]:
            depth = 0 if directory == '.' else directory.count('/') + 1
            return (depth, -counts[directory], directory)

        directories = sorted(counts, key=sort_key)
        visible_directories = directories if max_entries is None else directories[:max_entries]

        lines: list[str] = []
        for directory in visible_directories:
            label = '.' if directory == '.' else directory + '/'
            lines.append(f"- {label} ({counts[directory]} files)")
        if max_entries is not None and len(directories) > max_entries:
            lines.append(f"... {len(directories) - max_entries} more hierarchy entries omitted")
        return '\n'.join(lines)

    def _keywords_for_files(self, files: list[str]) -> list[str]:
        tokens: Counter[str] = Counter()
        stop = {"src", "components", "component", "index", "test", "tests", "utils", "hooks", "types"}
        for f in files:
            stem = PurePosixPath(f).stem.replace("_", "-")
            parts = []
            chunk = ""
            for ch in stem:
                if ch.isupper() and chunk:
                    parts.append(chunk.lower())
                    chunk = ch
                elif ch in "-. ":
                    if chunk:
                        parts.append(chunk.lower())
                    chunk = ""
                else:
                    chunk += ch
            if chunk:
                parts.append(chunk.lower())
            for part in parts:
                if len(part) > 2 and part not in stop:
                    tokens[part] += 1
        return [token for token, _ in tokens.most_common(12)]

    def parse_llm_response(self, response: str) -> list[DiscoveredModule]:
        """LLM 응답 파싱 (YAML 추출)."""
        import re

        # YAML 블록 추출
        yaml_match = re.search(r'```yaml\s*(.*?)\s*```', response, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
        else:
            yaml_content = response

        # YAML 파싱
        import yaml
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("LLM response must be a YAML mapping")

        modules = []
        for mod_data in data.get('modules', []) or []:
            modules.append(DiscoveredModule(
                name=mod_data.get('name', ''),
                files=mod_data.get('files', []) or [],
                rationale=mod_data.get('rationale', ''),
                confidence=mod_data.get('confidence', 0.0),
                include=mod_data.get('include', []) or [],
                exclude=mod_data.get('exclude', []) or [],
            ))

        return modules

    def discover(self, llm_response: str, allow_broad_patterns: bool = False) -> list[DiscoveredModule]:
        """LLM 응답으로 Module Discovery 수행."""
        modules = self.parse_llm_response(llm_response)
        known_files = set(self._files)

        for mod in modules:
            mod.files = self._normalize_paths(mod.files)
            mod.include = [normalize_path(p) for p in mod.include if p]
            mod.exclude = [normalize_path(p) for p in mod.exclude if p]
            if mod.include:
                expansion = expand_patterns(
                    mod.include,
                    mod.exclude,
                    known_files,
                    allow_broad_patterns=allow_broad_patterns,
                )
                mod.files = expansion.files
                mod.unmatched_patterns = expansion.unmatched_patterns
                mod.broad_patterns = expansion.broad_patterns

        return modules

    def save_results(self, modules: list[DiscoveredModule], output_path: str) -> None:
        """발견된 모듈을 YAML 로 저장."""
        config = ModuleGroupConfig(
            version=1,
            modules=[m.to_module_group() for m in modules],
            auto_grouping_enabled=True,
            auto_grouping_algorithm='llm',
        )
        config.save(output_path)
        print(f"[ModuleDiscovery] Saved {len(modules)} modules to {output_path}")


def run_discovery(ast_dir: str, output_dir: str, llm_response: str, output_file: str) -> list[DiscoveredModule]:
    """Module Discovery 실행."""
    discovery = ModuleDiscovery(ast_dir, output_dir)
    discovery.load_graph()

    print(f"[ModuleDiscovery] Loaded {len(discovery._files)} files")
    print(f"[ModuleDiscovery] Graph: {len(discovery._nodes)} nodes, {len(discovery._edges)} edges")

    modules = discovery.discover(llm_response)
    print(f"[ModuleDiscovery] Discovered {len(modules)} modules")

    output_path = os.path.join(output_dir, output_file)
    discovery.save_results(modules, output_path)

    return modules
