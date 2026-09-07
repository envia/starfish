#!/usr/bin/env python3
"""code2spec wiki launcher (deterministic stages).

deep-wiki 기계장치(ast-adapter · repo.json/deepLink · spec-cache · 검증 파이프라인 ·
delta diff-plan)를 code2spec 기존 파이프라인 위에 얹어 순차 실행하는 런처.

Target B 원칙:
  - 별도 wiki 페이지 세트를 만들지 않는다. 산출 대상은 기존 SDD 루트(``<target>/code2spec``)
    하나이며, ``.ast/`` · ``repo.json`` 만 그 아래에 추가된다.
  - 경로는 절대 flat 하드코딩하지 않고 ``analysis_paths.get_canonical_paths()`` 로 해석한다.
  - base 도구(``cli.py export`` · ``group_cli.py``)를 재사용한다(재구현 금지).

canonical 경로 (wiki-dir = ``<target>/code2spec``, analysis-dir = ``<wiki-dir>/.analysis``):
  graph-raw.json   → ``.analysis/cache/code-to-ast/graph-raw.json`` (base export 산출)
  .ast/{api,deps}  → ``code2spec/.ast/{api,deps}.json``            (ast-adapter 산출)
  repo.json        → ``code2spec/repo.json``                        (prepare-code-wiki 산출)
  module-groups    → ``.analysis/state/delta/module-groups.yaml``   (group_cli 산출)
  spec-cache.json  → ``.analysis/state/delta/spec-cache.json``       (spec-cache-manager 산출)
  diff-plan.json   → ``.analysis/state/delta/diff-plan.json``        (compute-diff-plan 산출)

서브커맨드:
  prepare       export(옵션) → ast-adapter → prepare-code-wiki → group_cli discover(옵션)
  group-review  group_cli review → module-groups.yaml
  finalize      write-wiki-metadata → spec-cache mark-all → validate-generated-wiki --tier full
                (W3 전용 — runtime-stats로 W2 완료를 확인, W1/W2 도중 조기 실행 시 거부)
  diff          compute-diff-plan --from-git

Usage:
  python wiki_cli.py prepare      --repo <target> [--skip-export] [--skip-discover] [--remote-url URL] [--branch NAME]
  python wiki_cli.py group-review --repo <target> --response <llm-response.md>
  python wiki_cli.py finalize     --repo <target>
  python wiki_cli.py diff         --repo <target>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent

# analysis_paths 는 같은 tools/ 디렉토리에 있다(설치 시 .code2spec-tools/ 로 함께 복사됨).
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
from analysis_paths import get_canonical_paths  # noqa: E402

# ── 도구 경로 (설치 후에도 tools/ 상대 배치가 보존됨) ──────────────────────────
WIKI_TOOLS = TOOLS_DIR / "wiki"
ADAPTER = WIKI_TOOLS / "ast_adapter.py"
PREPARE = WIKI_TOOLS / "prepare_code_wiki.py"
WRITE_META = WIKI_TOOLS / "write_wiki_metadata.py"
SPEC_CACHE = WIKI_TOOLS / "spec_cache_manager.py"
CONVERT_TAGS = WIKI_TOOLS / "convert_source_tags.py"
QUOTE_MERMAID = WIKI_TOOLS / "quote_mermaid_labels.py"
FIX_CITATION_LABELS = WIKI_TOOLS / "fix_citation_labels.py"
FIX_DEEPLINK_LINES = WIKI_TOOLS / "fix_deeplink_lines.py"
COMPUTE_DIFF = WIKI_TOOLS / "compute_diff_plan.py"
VALIDATE = WIKI_TOOLS / "verification" / "validate_generated_wiki.py"
LAYOUT = WIKI_TOOLS / "verification" / "validate_layout.py"
CLI_PY = TOOLS_DIR / "cli.py"
GROUP_CLI = TOOLS_DIR / "group_cli.py"


class Paths:
    """--repo (분석 대상) 기준으로 canonical 경로를 해석한 묶음."""

    def __init__(self, repo: Path, output_dir: Path | None) -> None:
        self.repo = repo.resolve()
        # wiki-dir = SDD 루트. 기본값은 <repo>/code2spec (scoped 분석이면 --output-dir로 override).
        self.wiki_dir = (output_dir.resolve() if output_dir else self.repo / "code2spec")
        self.analysis_dir = self.wiki_dir / ".analysis"
        cp = get_canonical_paths(self.analysis_dir)
        self.ast_output_dir = cp.ast_output_dir          # .analysis/cache/code-to-ast
        self.graph_json = self.ast_output_dir / "graph-raw.json"
        self.state_dir = cp.state_delta_dir              # .analysis/state/delta
        self.module_groups = cp.module_groups            # state/delta/module-groups.yaml
        self.spec_cache = cp.spec_cache                  # state/delta/spec-cache.json
        self.runtime_stats = cp.runtime_stats            # reports/runtime/runtime-stats.json
        # base W-DELTA가 canonical diff-plan.json(다른 스키마)을 쓰므로, wiki delta는
        # 충돌을 피해 별도 파일(wiki-diff-plan.json)에 산출한다.
        self.wiki_diff_plan = self.state_dir / "wiki-diff-plan.json"
        self.ast_out_dir = self.wiki_dir / ".ast"        # .ast/{api,deps}.json
        self.disco_dir = self.analysis_dir / "module-discovery"

    def ensure(self) -> None:
        for d in (self.ast_output_dir, self.state_dir, self.ast_out_dir, self.wiki_dir):
            d.mkdir(parents=True, exist_ok=True)


def _python(args: argparse.Namespace) -> str:
    """python 인터프리터 해석: --python > env CODE2SPEC_PYTHON > 현재 인터프리터(=venv)."""
    return args.python or os.environ.get("CODE2SPEC_PYTHON") or sys.executable


def run(cmd: Sequence[object], cwd: Path, *, pythonpath: str | None = None,
        check: bool = True) -> int:
    """단계 실행 헬퍼. check=True면 실패 시 hard-exit, False면 rc를 반환한다."""
    env = os.environ.copy()
    if pythonpath:
        prev = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = pythonpath + (os.pathsep + prev if prev else "")
    printable = " ".join(str(c) for c in cmd)
    print(f"[wiki_cli] $ {printable}", flush=True)
    rc = subprocess.call([str(c) for c in cmd], cwd=str(cwd), env=env)
    if check and rc != 0:
        print(f"[wiki_cli] step failed (rc={rc}): {printable}", file=sys.stderr)
        sys.exit(rc)
    return rc


# ── 서브커맨드 ────────────────────────────────────────────────────────────────

def _build_ast_and_repo_json(p: Paths, args: argparse.Namespace, *,
                             skip_export: bool) -> None:
    """결정적 산출(.ast/{api,deps}.json + repo.json) 생성. prepare와 finalize self-heal이 공유.

    export(옵션) → ast-adapter → prepare-code-wiki 순. 대시보드가 요구하는 최소 산출을
    보장하는 코어 단계다(모듈 그룹핑 discover는 제외).
    """
    py = _python(args)
    pp = str(TOOLS_DIR)

    # 1. base AST export → graph-raw.json (canonical cache 경로).
    if skip_export:
        if not p.graph_json.exists():
            print(f"[wiki_cli] --skip-export 이지만 graph-raw.json 이 없습니다: {p.graph_json}",
                  file=sys.stderr)
            sys.exit(1)
        print(f"[wiki_cli] skip export — reuse {p.graph_json}")
    else:
        run([py, CLI_PY, "export", "--repo", p.repo, "--output-dir", p.ast_output_dir],
            cwd=p.repo, pythonpath=pp)
        if not p.graph_json.exists():
            print(f"[wiki_cli] export did not produce {p.graph_json}", file=sys.stderr)
            sys.exit(1)

    # 2. AST 어댑터 → code2spec/.ast/{api,deps}.json
    run([py, ADAPTER,
         "--repo-root", p.repo,
         "--graph", p.graph_json,
         "--out", p.ast_out_dir / "api.json",
         "--out-deps", p.ast_out_dir / "deps.json"], cwd=p.repo)

    # 3. repo.json + deepLink (SDD 루트에). remote/branch override 견고화(플랜 PR2 요구).
    prepare_cmd = [py, PREPARE, "--repo-root", p.repo, "--out", p.wiki_dir]
    if args.remote_url:
        prepare_cmd += ["--remote-url", args.remote_url]
    if args.branch:
        prepare_cmd += ["--branch", args.branch]
    run(prepare_cmd, cwd=p.repo)


# W1이 만드는 인덱스 껍데기 파일명(모듈 카드가 아님).
_INDEX_SHELLS = {"readme.md", "index.md"}
# W1 placeholder 마커 — 실제 작성 전 "W2에서 생성" 류 문구를 담은 껍데기 표시.
_PLACEHOLDER_MARKERS = ("W2에서 생성", "생성 예정", "to be generated", "코드 내 식별 불가 (W2")


def _has_real_module_cards(wiki_dir: Path) -> bool:
    """`modules/` 에 실제 모듈 카드(인덱스·placeholder 껍데기 제외)가 하나라도 있는지.

    W2 완료 신호로 쓴다. `modules/README.md`(인덱스)나 'W2에서 생성' placeholder만 있으면
    W2 미완료로 본다.
    """
    modules_dir = wiki_dir / "modules"
    if not modules_dir.is_dir():
        return False
    for f in modules_dir.glob("*.md"):
        if f.name.lower() in _INDEX_SHELLS:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(m in text for m in _PLACEHOLDER_MARKERS):
            continue
        return True
    return False


def _w2_confirmed_via_runtime_stats(runtime_stats_path: Path) -> bool | None:
    """runtime-stats.json 기반 **결정적** W2-완료 판별 (파일 휴리스틱보다 우선).

    W2(`code2spec-modules`)는 종료 시 `workflows.W2.end_time`을, W3는 `workflows.W3.start_time`을,
    W-DELTA는 `workflows.W-DELTA.start_time`을 runtime-stats에 기록한다. 이 신호가 검증(finalize)이
    실행돼도 되는 "W3/W-DELTA 맥락"인지를 LLM이 조작할 수 없는 방식으로 알려준다.

    반환:
      True  — W2 종료(또는 W3 시작/W-DELTA 활성) → 검증 허용 맥락
      False — runtime-stats는 있으나 위 신호가 없음(=아직 W1/W2 진행 중) → 검증 차단
      None  — runtime-stats 부재/파싱 불가 → 상태로 판단 불가(모듈 카드 휴리스틱에 위임)
    """
    try:
        data = json.loads(Path(runtime_stats_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    wf = data.get("workflows")
    if not isinstance(wf, dict):
        return None

    def _has(name: str, key: str) -> bool:
        v = wf.get(name)
        return isinstance(v, dict) and bool(v.get(key))

    if _has("W-DELTA", "start_time") or _has("W3", "start_time") or _has("W2", "end_time"):
        return True
    return False


def _wiki_artifacts_present(p: Paths) -> bool:
    """대시보드 필수 결정적 산출(.ast/{api,deps}.json + repo.json)이 모두 있는지."""
    return (
        (p.ast_out_dir / "api.json").exists()
        and (p.ast_out_dir / "deps.json").exists()
        and (p.wiki_dir / "repo.json").exists()
    )


def cmd_prepare(args: argparse.Namespace) -> None:
    p = Paths(Path(args.repo), Path(args.output_dir) if args.output_dir else None)
    p.ensure()
    py = _python(args)
    pp = str(TOOLS_DIR)

    _build_ast_and_repo_json(p, args, skip_export=args.skip_export)

    # 4. 모듈 그룹핑 프롬프트 (base group_cli). W1/W2가 이미 수행했으면 --skip-discover.
    if args.skip_discover:
        print("[wiki_cli] skip discover — 기존 module-discovery/module-groups.yaml 재사용")
    else:
        p.disco_dir.mkdir(parents=True, exist_ok=True)
        run([py, GROUP_CLI, "discover", "--ast-dir", p.ast_output_dir, "--output-dir", p.disco_dir],
            cwd=p.repo, pythonpath=pp)

    print("\n[wiki_cli] prepare 완료.")
    print(f"  - .ast:        {p.ast_out_dir}")
    print(f"  - repo.json:   {p.wiki_dir / 'repo.json'}")
    if not args.skip_discover:
        print(f"  - 다음: {p.disco_dir / 'llm-prompt.md'} 로 모듈 그룹을 검토한 뒤 "
              f"`wiki_cli.py group-review --repo {p.repo} --response <응답파일>` 실행")


def cmd_group_review(args: argparse.Namespace) -> None:
    p = Paths(Path(args.repo), Path(args.output_dir) if args.output_dir else None)
    p.state_dir.mkdir(parents=True, exist_ok=True)
    py = _python(args)
    response = Path(args.response).resolve()
    if not response.exists():
        print(f"[wiki_cli] --response 파일이 없습니다: {response}", file=sys.stderr)
        sys.exit(1)
    # module-groups.yaml 을 canonical state/delta 에 직접 산출.
    run([py, GROUP_CLI, "review",
         "--ast-dir", p.ast_output_dir,
         "--output-dir", p.state_dir,
         "--llm-response", response,
         "--output", "module-groups.yaml"], cwd=p.repo, pythonpath=str(TOOLS_DIR))
    print("\n[wiki_cli] group-review 완료.")
    print(f"  - module-groups: {p.module_groups}")
    print("  - 다음: 모듈/FR/챕터 문서를 작성한 뒤 `wiki_cli.py finalize` 실행")


# finalize가 hard gate 실패 후 결정적 교정을 다시 적용하는 최대 횟수. 한 라운드가 아무 파일도
# 바꾸지 못하면 그 전에 멈춘다 — 라운드는 "교정이 새 교정을 가능하게 하는" 연쇄(라벨 교정 →
# 심볼 인식 → 라인 교정)를 흘려보내기 위한 것이지, 같은 작업의 무한 반복이 아니다.
MAX_REPAIR_ROUNDS = 3

_DIGEST_SKIP_DIRS = {".ast", ".claims", ".trust", ".git", ".analysis", "node_modules"}


def _md_digest(wiki_dir: Path) -> str:
    """위키 .md 전체의 내용 해시. 교정 라운드가 실제로 뭔가 바꿨는지 판별한다."""
    h = hashlib.sha256()
    for md in sorted(wiki_dir.rglob("*.md")):
        if any(part in _DIGEST_SKIP_DIRS for part in md.parts):
            continue
        h.update(str(md.relative_to(wiki_dir)).encode("utf-8"))
        try:
            h.update(md.read_bytes())
        except OSError:
            pass
    return h.hexdigest()


def _repair_wiki(py: str, p: Paths) -> None:
    """사람 판단이 필요 없는 결정적 교정만 순서대로 적용한다(모두 비치명적).

    순서에 의미가 있다: `[Source:]`가 먼저 링크가 되어야 라벨·라인 교정이 그 링크를 보고,
    라벨이 먼저 백틱 심볼이 되어야 라인 교정이 그것을 심볼 인용으로 인식한다.
    """
    # [Source: path:L#] → deep-link. [Source:]는 렌더도 검증도 되지 않는 평문이므로
    # 생성물에 남은 code2spec 인용을 `src:` 축약 deep-link로 굳힌다.
    run([py, CONVERT_TAGS, "--wiki-dir", p.wiki_dir], cwd=p.repo, check=False)
    # mermaid 라벨 auto-quote. mermaidSyntax는 hard gate라, 따옴표 안 된 특수문자 라벨
    # 하나로 빌드가 실패하는 것을 막는다.
    run([py, QUOTE_MERMAID, "--wiki-dir", p.wiki_dir], cwd=p.repo, check=False)
    # 백틱 없는 인용 라벨(`[출처]` 등) → 백틱 심볼/파일명 라벨. grounding은 백틱 라벨만
    # 검사하므로, 이 교정 없이는 틀린 라인이 검증에서 빠진 채 남는다(이슈 #29).
    run([py, FIX_CITATION_LABELS, "--wiki-dir", p.wiki_dir], cwd=p.repo, check=False)
    # 심볼 deep-link의 #L을 .ast/api.json 정의 라인(없으면 소스 스캔)으로 맞춘다 →
    # grounding drift 자동 해소. owner 중복 경로도 정규화한다.
    run([py, FIX_DEEPLINK_LINES, "--wiki-dir", p.wiki_dir, "--repo-root", p.repo],
        cwd=p.repo, check=False)


def _remove_atomic_claims_artifacts(p: Paths) -> None:
    """제거된 atomic-claims 서브시스템의 잔존 산출물을 치운다.

    claim 산출(`.claims/*.claims.jsonl`)과 그 판정(`.trust/atomic-claims.json`)은
    claimGrounding hard gate가 같은 술어로 이미 검사하던 것의 재측정이라 제거됐다.
    링크별 신뢰 배지 데이터는 `.trust/claims.json`의 `links[]`가 대신한다.
    남겨두면 옛 판정이 대시보드에 그대로 렌더되므로 finalize가 지운다.
    """
    claims_dir = Path(p.wiki_dir) / ".claims"
    if claims_dir.is_dir():
        for f in claims_dir.glob("*.claims.jsonl"):
            f.unlink()
        if not any(claims_dir.iterdir()):
            claims_dir.rmdir()
    stale = Path(p.wiki_dir) / ".trust" / "atomic-claims.json"
    if stale.is_file():
        stale.unlink()


def cmd_finalize(args: argparse.Namespace) -> None:
    p = Paths(Path(args.repo), Path(args.output_dir) if args.output_dir else None)
    p.ensure()
    py = _python(args)

    # 0-a. 순서 가드: 검증은 오직 W3(또는 W-DELTA)에서만 수행한다. W1/W2 도중 조기 검증 금지.
    #      finalize 본문(메타·spec-cache 스냅샷·변환·검증)은 전부 이 가드 뒤에 있으므로,
    #      가드 하나가 W1/W2에서 실행될 수 있는 모든 부분을 함께 막는다.
    #
    #      판별은 두 신호를 결합한다(--force로만 우회):
    #        (1) runtime-stats.json (결정적·우선) — W2 종료/W3 시작/W-DELTA 활성 여부.
    #            W1은 자기 자신만 workflow-end 하므로 W1 종료 시점엔 W2.end_time이 없다 →
    #            LLM이 finalize를 조기 호출해도 여기서 확실히 차단된다.
    #        (2) 실제 모듈 카드 존재 (휴리스틱·폴백) — runtime-stats가 없을 때만 사용.
    #            인덱스 껍데기(modules/README.md)·"W2에서 생성" placeholder는 카드로 세지 않는다.
    if not args.force:
        state = _w2_confirmed_via_runtime_stats(p.runtime_stats)   # True/False/None
        has_cards = _has_real_module_cards(p.wiki_dir)
        blocked = (state is False) or (state is None and not has_cards)
        if blocked:
            if state is False:
                why = ("runtime-stats.json 에 W2 종료(W2.end_time)·W3 시작 기록이 없습니다 "
                       "— 아직 W1/W2 진행 중입니다.")
            else:
                why = ("실제 모듈 카드가 없습니다(W2 미완료). 'modules/README.md' 같은 인덱스 껍데기와 "
                       "'W2에서 생성' placeholder는 아직 작성된 내용이 아닙니다.")
            print(
                f"[wiki_cli] finalize 중단 — {why}\n"
                "  검증은 W3(finalize)에서만 수행합니다. W1(챕터)·W2(모듈 카드/FR)가 모두 끝난 뒤\n"
                "  전체를 대상으로 한 번만 검증하세요.\n"
                "  순서: code2spec-discovery(W1) → code2spec-modules(W2) → code2spec-finalize(W3).\n"
                "  W2를 먼저 완료하세요. 부분 산출을 의도적으로 검증하려면 --force.",
                file=sys.stderr,
            )
            sys.exit(2)

    # 0. self-heal: 대시보드 필수 산출(.ast/{api,deps}.json + repo.json)이 없으면
    #    prepare 코어를 자동 수행한다. W1(discovery)의 prepare 단계가 스킵됐어도
    #    finalize 한 번으로 산출이 반드시 생성되도록 보장한다(이슈 #16 작업 A2).
    if not _wiki_artifacts_present(p):
        print("[wiki_cli] .ast/repo.json 누락 — prepare 코어 자동 수행(self-heal)")
        _build_ast_and_repo_json(p, args, skip_export=p.graph_json.exists())

    # 1. 대시보드 메타데이터 (description/languages/defaultBranch).
    run([py, WRITE_META, "--repo-root", p.repo, "--wiki-dir", p.wiki_dir], cwd=p.repo)

    # 2. spec-cache 스냅샷 (git ls-files 전체 → 마지막 문서화 상태). delta 기준점.
    run([py, SPEC_CACHE, "--action", "mark-all",
         "--root", p.repo, "--analysis-dir", p.state_dir], cwd=p.repo)

    # 2.5 결정적 교정(안전망). 비치명적 — deepLink 미해석(local) 시 각 도구가 스스로 건너뛴다.
    _repair_wiki(py, p)

    # 2.6 레이아웃 lint(결정적). sdd/ 오배치·비표준 loose 파일·[Source:] 잔존을 명확히 보고한다.
    #     오배치는 아래 requiredSlots hard gate로도 잡히지만, 여기서 원인을 또렷이 알려준다.
    run([py, LAYOUT, "--wiki-dir", p.wiki_dir], cwd=p.repo, check=False)

    # 2.7 제거된 atomic-claims 산출물 정리(옛 실행이 남긴 것). claimGrounding이
    #     같은 인용을 hard gate로 검사하고 배지 데이터도 그쪽에서 나온다.
    _remove_atomic_claims_artifacts(p)

    # 3. 검증 → (실패 시) 결정적 교정 → 재검증 루프.
    #    hard gate 실패를 즉시 종료로 취급하지 않는다: drift 대부분은 기계적으로 교정 가능하고
    #    (틀린 #L, 백틱 없는 라벨), 그 교정은 사람 판단이 필요 없다. 교정이 더 이상 아무것도
    #    바꾸지 못할 때까지 돌린 뒤에야 실패로 판정한다 — 그때 남은 것은 실제로 사람/LLM이
    #    고쳐야 하는 항목(존재하지 않는 심볼명, 없는 파일)뿐이다.
    rc = 0
    for round_no in range(1, MAX_REPAIR_ROUNDS + 1):
        rc = run([py, VALIDATE, "--repo-root", p.repo, "--wiki-dir", p.wiki_dir,
                  "--tier", "full"], cwd=p.repo, check=False)
        if rc == 0:
            if round_no > 1:
                print(f"[wiki_cli] hard gate 통과 — 결정적 교정 {round_no - 1}라운드 후.")
            break
        if round_no == MAX_REPAIR_ROUNDS:
            print(f"[wiki_cli] 교정 라운드 한도({MAX_REPAIR_ROUNDS}) 도달 — 남은 실패는 "
                  f"기계적으로 교정되지 않습니다.", file=sys.stderr)
            break
        print(f"\n[wiki_cli] hard gate 실패 (rc={rc}) — 결정적 교정 재적용 "
              f"({round_no}/{MAX_REPAIR_ROUNDS - 1}) 후 재검증합니다.")
        before = _md_digest(p.wiki_dir)
        _repair_wiki(py, p)
        if _md_digest(p.wiki_dir) == before:
            print("[wiki_cli] 교정으로 바뀐 내용 없음 — 남은 실패는 서술 정정이 필요합니다"
                  "(존재하지 않는 심볼명·없는 파일·부정확한 주장).", file=sys.stderr)
            break
        # claimGrounding은 매 라운드 본문에서 직접 인용을 파싱하므로 별도 재산출이 없다.

    repo_json = p.wiki_dir / "repo.json"
    if repo_json.exists():
        try:
            data = json.loads(repo_json.read_text(encoding="utf-8"))
            if "qualityScore" in data:
                print(f"[wiki_cli] qualityScore: {data['qualityScore']}")
            if "qualityBreakdown" in data:
                print(f"[wiki_cli] qualityBreakdown: "
                      f"{json.dumps(data['qualityBreakdown'], ensure_ascii=False)}")
        except (ValueError, OSError):
            pass

    # 점수만으로는 신뢰 근거가 되지 않는다: 리포트가 없으면 성공/실패 어느 쪽이든
    # 매 라운드 상기시킨다. 리포트는 축별 근거(잔여 drift/contradicted/미지원 edge
    # 목록 또는 "잔여 0건")를 담아야 하며, 점수 나열만으로는 무효다.
    if not (p.wiki_dir / "verification-report.md").exists():
        print("[wiki_cli] ⚠️ verification-report.md 미생성 — 점수만 기록된 상태는 W3 완료가\n"
              "  아닙니다. code2spec-verification-report 스킬로 리포트를 생성하세요\n"
              "  (각 hard gate 축의 근거 목록 필수; 점수만 나열한 리포트는 무효).",
              file=sys.stderr)

    if rc != 0:
        print(f"[wiki_cli] 검증 hard gate 실패 (rc={rc}) — 결정적 교정으로는 해결되지 않습니다.\n"
              f"  ⚠️ 이 종료는 '완료'가 아니라 LLM 교정 차례라는 신호입니다: 위 검증 출력의 실패 축과\n"
              f"  {p.wiki_dir / '.trust'} 리포트를 보고 본문을 정정한 뒤 finalize를 다시 실행하고,\n"
              f"  hard gate가 모두 통과할 때까지 이 교정→재실행 루프를 반복하세요(상한 5라운드).\n"
              f"  실패 상태로 작업을 완료로 보고하지 않습니다. 남는 유형은 보통 다음입니다:\n"
              f"    - grounding: 링크된 파일에 그 이름의 심볼이 없음(잘못된 심볼명) → 실제 이름으로 정정\n"
              f"    - claimGrounding: 코드와 어긋나는 주장 → 서술 정정·삭제 (.trust/claims.json의\n"
              f"      contradicted 항목이 page:line과 사유를 제공)\n"
              f"    - diagramAccuracy: .ast/deps.json에 없는 edge → deps.json의 실제 관계로 edge를\n"
              f"      교정(끝점·방향 수정)이 우선, 외부 시스템은 external 표시, 삭제는 최후 수단",
              file=sys.stderr)
        sys.exit(rc)
    print("\n[wiki_cli] finalize 완료 — 검증 통과.")


def cmd_diff(args: argparse.Namespace) -> None:
    p = Paths(Path(args.repo), Path(args.output_dir) if args.output_dir else None)
    py = _python(args)
    # 마지막 finalize 스냅샷(spec-cache) 대비 현재 git 상태 diff → wiki-diff-plan.json
    # (base W-DELTA의 diff-plan.json을 덮어쓰지 않도록 별도 파일명 사용)
    rc = run([py, COMPUTE_DIFF, "--root", p.repo, "--from-git",
              "--analysis-dir", p.state_dir, "--out", p.wiki_diff_plan.name],
             cwd=p.repo, check=False)
    if rc != 0:
        print("[wiki_cli] diff 실패 — 먼저 `wiki_cli.py finalize` 로 full 빌드를 수행하세요.",
              file=sys.stderr)
        sys.exit(rc)
    print("\n[wiki_cli] diff 완료.")
    print(f"  - wiki-diff-plan: {p.wiki_diff_plan}")
    print(f"  - 다음: `{py} {WIKI_TOOLS / 'parse_wiki_rsf.py'} --wiki-dir {p.wiki_dir} "
          f"--repo-root {p.repo} --diff-plan {p.wiki_diff_plan}` 로 재생성 대상 페이지를 판정")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="wiki_cli", description="code2spec wiki launcher (Target B)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--repo", required=True, help="분석 대상 루트 (ANALYSIS_TARGET)")
        sp.add_argument("--output-dir", default=None,
                        help="SDD/wiki 출력 루트 (기본: <repo>/code2spec)")
        sp.add_argument("--python", default=None, help="python 인터프리터 override")

    sp = sub.add_parser("prepare", help="export → ast-adapter → repo.json → discover")
    add_common(sp)
    sp.add_argument("--skip-export", action="store_true",
                    help="기존 graph-raw.json 재사용 (W1이 이미 export한 경우)")
    sp.add_argument("--skip-discover", action="store_true",
                    help="group_cli discover 생략 (W1/W2가 그룹핑을 수행하는 경우)")
    sp.add_argument("--remote-url", default=None, help="deep-link remote URL override")
    sp.add_argument("--branch", default=None, help="deep-link branch override")
    sp.set_defaults(func=cmd_prepare)

    sp = sub.add_parser("group-review", help="group_cli review → module-groups.yaml")
    add_common(sp)
    sp.add_argument("--response", required=True, help="LLM 그룹핑 응답 파일")
    sp.set_defaults(func=cmd_group_review)

    sp = sub.add_parser("finalize", help="metadata → spec-cache → validate --tier full")
    add_common(sp)
    # self-heal(.ast/repo.json 자동 생성)에서 deep-link 해석에 사용.
    sp.add_argument("--remote-url", default=None, help="deep-link remote URL override (self-heal 시)")
    sp.add_argument("--branch", default=None, help="deep-link branch override (self-heal 시)")
    sp.add_argument("--force", action="store_true",
                    help="W2 미완료(modules/ 비어있음)여도 검증 강행(부분 산출 검증용)")
    sp.set_defaults(func=cmd_finalize)

    sp = sub.add_parser("diff", help="compute-diff-plan --from-git")
    add_common(sp)
    sp.set_defaults(func=cmd_diff)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
