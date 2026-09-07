#!/usr/bin/env python3
"""W3 검증 산출물 질의 도구 — 대형 JSON을 **통째로 읽지 않고** 필요한 행만 뽑는다.

W3(Step 2-W)의 교정 루프가 참조하는 산출물은 실제 저장소에서 수 MB급으로 커진다:

  ``<wiki>/.trust/claims.json``          claimGrounding 판정 (results[] 수천 건,
                                         links[] = 링크별 배지 롤업)
  ``<wiki>/.ast/api.json``               파일별 export 심볼 전체
  ``<wiki>/.ast/deps.json``              관계 엣지 전체

교정에 실제로 필요한 것은 "contradicted 15건의 page:line·reason", "이 파일의 export
라인", "이 두 노드 사이 엣지" 같은 **소량의 좌표**다. 파일 전체를 컨텍스트에 올리면
필요한 정보의 수백 배를 토큰으로 지불하게 되므로, 이 도구가 필터·집계·절단을 대신
수행하고 한 줄 TSV로 돌려준다.

절단은 항상 드러낸다 — 출력 마지막 줄의 ``# source=... matched=M shown=S``가 몇 건이
잘렸는지 알려주므로, 조용한 top-N으로 "전부 봤다"고 오해할 여지가 없다.

Usage:
  python3 query_artifacts.py <wiki-dir> summary
  python3 query_artifacts.py <wiki-dir> list  --source claims --status contradicted [--page SUB]
                                              [--type SUB] [--grep RE] [--limit 30] [--offset 0]
                                              [--fields a,b,c] [--full] [--format tsv|json]
  python3 query_artifacts.py <wiki-dir> pages --source claims [--status contradicted]
  python3 query_artifacts.py <wiki-dir> list  --source links --status contradicted
  python3 query_artifacts.py <wiki-dir> symbols --file src/foo.ts
  python3 query_artifacts.py <wiki-dir> symbols --name RetrieverService
  python3 query_artifacts.py <wiki-dir> edges --node RetrieverService [--to BaseService]
                                              [--kind implements,calls]

  <wiki-dir> = 분석 대상의 ``code2spec/`` (SDD 루트, = OUTPUT_DIR)
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

MODES = ("summary", "list", "pages", "symbols", "edges")

# --source 이름 → (상대 경로, 레코드 추출기 종류)
SOURCES: dict[str, tuple[str, str]] = {
    "claims": (".trust/claims.json", "results"),
    # 같은 파일의 링크별 롤업(대시보드 배지 데이터) — 인용 하나당 한 줄.
    "links": (".trust/claims.json", "links"),
}

# 소스별 기본 출력 컬럼. --fields 로 덮어쓸 수 있다.
DEFAULT_FIELDS: dict[str, list[str]] = {
    "claims": ["status", "page", "line", "type", "text", "target", "reason"],
    "links": ["status", "page", "line", "text", "target", "url", "reasons"],
}

DEFAULT_LIMIT = 30
DEFAULT_WIDTH = 120

# deps.json 에서 엣지로 취급하는 키. files 는 목록이라 제외한다.
EDGE_KINDS = ("internal", "external", "calls", "unresolved_calls", "tested_by",
              "depends_on", "inherits", "implements", "contains")


def usage(message: str | None = None) -> None:
    if message:
        print(f"error: {message}", file=sys.stderr)
    print(__doc__ or "", file=sys.stderr)
    sys.exit(2)


def parse_args(argv: list[str]) -> dict[str, Any]:
    """``--key value`` / ``--flag`` 쌍과 positional 을 파싱한다(검증기들과 같은 방식)."""
    out: dict[str, Any] = {"positional": []}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith("--"):
            key = arg[2:]
            nxt = argv[i + 1] if i + 1 < len(argv) else None
            if nxt is None or nxt.startswith("--"):
                out[key] = True
            else:
                out[key] = nxt
                i += 1
        else:
            out["positional"].append(arg)
        i += 1
    return out


def opt(args: dict[str, Any], key: str) -> str | None:
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def opt_int(args: dict[str, Any], key: str, default: int) -> int:
    raw = opt(args, key)
    if raw is None:
        return default
    m = re.match(r"\s*(-?[0-9]+)", raw)
    return int(m.group(1)) if m else default


def csv_set(value: str | None) -> set[str] | None:
    """``a,b`` → {"a","b"}. 값이 없으면 None(필터 없음)."""
    if not value:
        return None
    items = {v.strip() for v in value.split(",") if v.strip()}
    return items or None


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8", errors="replace") as f:
        return json.load(f)


def load_records(wiki_dir: str, source: str) -> list[dict[str, Any]]:
    """소스 파일에서 레코드 목록을 읽는다. 파일이 없으면 종료(1)."""
    if source not in SOURCES:
        usage(f"unknown --source: {source} (choose from {', '.join(SOURCES)})")
    rel, kind = SOURCES[source]
    path = os.path.join(wiki_dir, *rel.split("/"))
    if not os.path.exists(path):
        print(f"error: not found: {path}", file=sys.stderr)
        sys.exit(1)
    if kind == "jsonl":
        records = []
        with open(path, encoding="utf-8", errors="replace") as f:
            for raw in f:
                if not raw.strip():
                    continue
                try:
                    rec = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if isinstance(rec, dict):
                    records.append(rec)
        return records
    data = load_json(path)
    records = data.get(kind) if isinstance(data, dict) else None
    return [r for r in (records or []) if isinstance(r, dict)]


def cell(rec: dict[str, Any], field: str) -> str:
    """레코드의 한 컬럼을 문자열로. 중첩 구조는 한 줄로 요약한다."""
    if field == "reasons":
        # links[] 롤업은 판정 사유를 여러 개 모을 수 있다 — 한 줄로 잇는다.
        reasons = rec.get("reasons")
        if isinstance(reasons, list):
            return "; ".join(str(x) for x in reasons)
        return "" if reasons is None else str(reasons)
    value = rec.get(field)
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def clip(text: str, width: int) -> str:
    """TSV 한 줄을 유지하도록 개행·탭을 눕히고 폭을 제한한다."""
    flat = text.replace("\t", " ").replace("\r", " ").replace("\n", " ").strip()
    if width > 0 and len(flat) > width:
        return flat[: width - 1] + "…"
    return flat


def matches(rec: dict[str, Any], *, statuses: set[str] | None, types: str | None,
            page: str | None, grep: re.Pattern[str] | None) -> bool:
    if statuses is not None and str(rec.get("status") or "") not in statuses:
        return False
    if types is not None and types not in str(rec.get("type") or ""):
        return False
    if page is not None and page not in str(rec.get("page") or ""):
        return False
    if grep is not None:
        blob = json.dumps(rec, ensure_ascii=False)
        if not grep.search(blob):
            return False
    return True


def emit_rows(rows: list[dict[str, Any]], fields: list[str], *,
              fmt: str, width: int) -> None:
    if fmt == "json":
        for rec in rows:
            print(json.dumps({f: rec.get(f) for f in fields if f in rec},
                             ensure_ascii=False, separators=(",", ":")))
        return
    print("\t".join(fields))
    for rec in rows:
        print("\t".join(clip(cell(rec, f), width) for f in fields))


def footer(source: str, matched: int, shown: int, limit: int, offset: int) -> None:
    line = f"# source={source} matched={matched} shown={shown}"
    if offset:
        line += f" offset={offset}"
    print(line)
    if matched > offset + shown:
        remaining = matched - (offset + shown)
        print(f"# {remaining} more — rerun with --offset {offset + limit} "
              f"(or raise --limit)")


# ── mode: summary ─────────────────────────────────────────────────────────────

def mode_summary(wiki_dir: str) -> int:
    """리포트 1절에 그대로 옮길 숫자만 출력한다(값 재계산 없음)."""
    repo_path = os.path.join(wiki_dir, "repo.json")
    if os.path.exists(repo_path):
        repo = load_json(repo_path)
        qs = repo.get("qualityScore") or {}
        qb = repo.get("qualityBreakdown") or {}
        print(f"verifiedAt: {qb.get('verifiedAt')}")
        print("== qualityScore ==")
        for k, v in qs.items():
            print(f"  {k}: {v}")
        print("== qualityBreakdown.validators (first line each) ==")
        for k, v in (qb.get("validators") or {}).items():
            head = str(v).splitlines()[0] if v else v
            print(f"  {k}: {head}")
    else:
        print(f"repo.json: 없음 ({repo_path})")

    rel, _ = SOURCES["claims"]
    path = os.path.join(wiki_dir, *rel.split("/"))
    if not os.path.exists(path):
        print(f"== {rel} == 없음")
        return 0
    data = load_json(path)
    links = data.get("links") or []
    untrusted = len([x for x in links
                     if isinstance(x, dict) and x.get("status") != "supported"])
    print(f"== {rel} ==")
    print(f"  counts: {data.get('counts')} sourceLinks: {data.get('sourceLinks')}")
    print(f"  badge links: {len(links)} (untrusted {untrusted})")
    return 0


# ── mode: list / pages ────────────────────────────────────────────────────────

def mode_list(wiki_dir: str, args: dict[str, Any]) -> int:
    source = opt(args, "source") or "claims"
    records = load_records(wiki_dir, source)
    grep_raw = opt(args, "grep")
    grep = re.compile(grep_raw) if grep_raw else None
    selected = [r for r in records
                if matches(r, statuses=csv_set(opt(args, "status")),
                           types=opt(args, "type"), page=opt(args, "page"), grep=grep)]

    limit = opt_int(args, "limit", DEFAULT_LIMIT)
    offset = max(0, opt_int(args, "offset", 0))
    window = selected[offset:] if limit <= 0 else selected[offset:offset + limit]

    fields_opt = opt(args, "fields")
    fields = ([f.strip() for f in fields_opt.split(",") if f.strip()] if fields_opt
              else DEFAULT_FIELDS.get(source, ["status", "page", "type", "text"]))
    width = 0 if args.get("full") else opt_int(args, "width", DEFAULT_WIDTH)

    emit_rows(window, fields, fmt=(opt(args, "format") or "tsv"), width=width)
    footer(source, len(selected), len(window), max(limit, 1), offset)
    return 0


def mode_pages(wiki_dir: str, args: dict[str, Any]) -> int:
    """page × status 집계 — 어느 페이지를 고쳐야 하는지만 뽑는 가장 싼 질의."""
    source = opt(args, "source") or "claims"
    records = load_records(wiki_dir, source)
    statuses = csv_set(opt(args, "status"))
    page_filter = opt(args, "page")

    per_page: dict[str, dict[str, int]] = {}
    seen_statuses: list[str] = []
    for rec in records:
        page = str(rec.get("page") or "(no page)")
        if page_filter is not None and page_filter not in page:
            continue
        status = str(rec.get("status") or "unknown")
        if statuses is not None and status not in statuses:
            continue
        if status not in seen_statuses:
            seen_statuses.append(status)
        per_page.setdefault(page, {})
        per_page[page][status] = per_page[page].get(status, 0) + 1

    order = [s for s in ("contradicted", "stale", "unresolved", "supported")
             if s in seen_statuses] + [s for s in sorted(seen_statuses)
                                       if s not in ("contradicted", "stale",
                                                    "unresolved", "supported")]
    print("\t".join(["page", *order, "total"]))
    rows = sorted(per_page.items(),
                  key=lambda kv: (-sum(kv[1].get(s, 0) for s in order
                                       if s != "supported"), kv[0]))
    limit = opt_int(args, "limit", 0)
    window = rows if limit <= 0 else rows[:limit]
    for page, counts in window:
        total = sum(counts.values())
        print("\t".join([page, *[str(counts.get(s, 0)) for s in order], str(total)]))
    footer(source, len(rows), len(window), max(limit, 1), 0)
    return 0


# ── mode: symbols / edges (.ast) ──────────────────────────────────────────────

def load_ast(wiki_dir: str, name: str) -> Any:
    path = os.path.join(wiki_dir, ".ast", name)
    if not os.path.exists(path):
        print(f"error: not found: {path}", file=sys.stderr)
        sys.exit(1)
    return load_json(path)


def mode_symbols(wiki_dir: str, args: dict[str, Any]) -> int:
    """api.json 조회: 파일의 export 목록, 또는 심볼이 정의된 파일·라인."""
    file_filter = opt(args, "file")
    name_filter = opt(args, "name")
    grep_raw = opt(args, "grep")
    grep = re.compile(grep_raw) if grep_raw else None
    if not (file_filter or name_filter or grep):
        usage("symbols: --file, --name, --grep 중 하나는 필요하다 "
              "(api.json 전체 덤프는 이 도구의 용도가 아니다)")

    api = load_ast(wiki_dir, "api.json")
    rows: list[list[str]] = []
    for rec in (api.get("files") or []):
        path = str(rec.get("path") or "")
        if file_filter is not None and file_filter not in path:
            continue
        for ex in (rec.get("exports") or []):
            name = str(ex.get("name") or "")
            if name_filter is not None and name != name_filter:
                continue
            if grep is not None and not grep.search(name):
                continue
            rows.append([path, str(ex.get("line") or ""), str(ex.get("kind") or ""),
                         str(ex.get("signature") or name),
                         str(ex.get("parent_name") or "")])

    limit = opt_int(args, "limit", DEFAULT_LIMIT)
    window = rows if limit <= 0 else rows[:limit]
    print("\t".join(["path", "line", "kind", "signature", "parent"]))
    for row in window:
        print("\t".join(clip(c, DEFAULT_WIDTH) for c in row))
    footer("api.json", len(rows), len(window), max(limit, 1), 0)
    return 0


def edge_row(kind: str, edge: dict[str, Any]) -> tuple[str, str, str]:
    """엣지 종류별로 다른 필드명을 (from, to, line) 로 정규화한다."""
    frm = edge.get("from") or edge.get("file") or edge.get("production") or ""
    to = edge.get("to") or edge.get("callee") or edge.get("class") or edge.get("test") or ""
    return str(frm), str(to), str(edge.get("line") or "")


def mode_edges(wiki_dir: str, args: dict[str, Any]) -> int:
    """deps.json 조회: 노드가 실제로 갖는 관계(방향 포함)를 확인한다."""
    node = opt(args, "node")
    frm_filter = opt(args, "from")
    to_filter = opt(args, "to")
    if not (node or frm_filter or to_filter):
        usage("edges: --node, --from, --to 중 하나는 필요하다 "
              "(deps.json 전체 덤프는 이 도구의 용도가 아니다)")

    deps = load_ast(wiki_dir, "deps.json")
    kinds = csv_set(opt(args, "kind")) or set(EDGE_KINDS)
    rows: list[list[str]] = []
    for kind in EDGE_KINDS:
        if kind not in kinds:
            continue
        for edge in (deps.get(kind) or []):
            if not isinstance(edge, dict):
                continue
            frm, to, line = edge_row(kind, edge)
            if node is not None and node not in frm and node not in to:
                continue
            if frm_filter is not None and frm_filter not in frm:
                continue
            if to_filter is not None and to_filter not in to:
                continue
            rows.append([kind, frm, to, line])

    limit = opt_int(args, "limit", DEFAULT_LIMIT)
    window = rows if limit <= 0 else rows[:limit]
    print("\t".join(["kind", "from", "to", "line"]))
    for row in window:
        print("\t".join(clip(c, DEFAULT_WIDTH) for c in row))
    footer("deps.json", len(rows), len(window), max(limit, 1), 0)
    return 0


def main() -> int:
    args = parse_args(sys.argv[1:])
    positional = args["positional"]
    if len(positional) < 1:
        usage("missing <wiki-dir>")
    wiki_dir = os.path.abspath(positional[0])
    mode = positional[1] if len(positional) > 1 else "summary"
    if mode not in MODES:
        usage(f"unknown mode: {mode} (choose from {', '.join(MODES)})")
    if not os.path.isdir(wiki_dir):
        usage(f"wiki dir not found: {wiki_dir}")

    if mode == "summary":
        return mode_summary(wiki_dir)
    if mode == "list":
        return mode_list(wiki_dir, args)
    if mode == "pages":
        return mode_pages(wiki_dir, args)
    if mode == "symbols":
        return mode_symbols(wiki_dir, args)
    return mode_edges(wiki_dir, args)


if __name__ == "__main__":
    sys.exit(main())
