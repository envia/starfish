#!/usr/bin/env python3
"""L1 grounding: does each source deep-link really point at the symbol it cites?

Every `` [`symbol`](<url>#L42) `` link in the wiki is resolved back to the local
checkout and the cited line is read: the citation is *aligned* when one of the
identifiers in the label appears on that line **as a whole identifier**, and a
*drift* otherwise. Whole-identifier matching matters: `` `Store` `` citing a line
that only holds ``StoreFactory`` names a different symbol, so substring matching
would pass a factually wrong citation.

This is a **hard gate**: any drift exits 1, because line alignment is checked nowhere
else. ``claimGrounding`` grades a cited identifier against the *whole linked file*
(`linked_file_mentions_identifier`), so it passes a citation that points at the wrong
line of the right file — exactly the off-by-N a writer produces by guessing.

Drift is expected to be repaired, not merely reported: finalize runs
``fix_citation_labels`` and ``fix_deeplink_lines`` and re-validates, so a run only
fails on drift that no deterministic repair can resolve (a symbol that is absent from
the linked file, a missing file).

The per-link predicates (URL parsing, label classification, identifier matching) are
shared with the other validators via ``citation_checks`` (issue #33); this module owns
only the line-alignment gate and its scoring.

The printed drift list is capped (30 files × 5 drifts) so a first run on a large repo
cannot flood a terminal, and that text is also what the orchestrator lifts into
``repo.json.qualityBreakdown``. ``--json`` writes the **complete** result instead, which
is what a report step needs: the caps make the console output a sample, not the record.

Usage: python3 validate_grounding.py <wiki-dir> <local-repo-root>
         [--json out.json] [--list-all] [--max-files N] [--max-per-file N]
"""

from __future__ import annotations

import json
import math
import os
import sys
import traceback
from collections.abc import Callable, Iterator
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from citation_checks import (
    MD_LINK_RE,
    SourceReader,
    basename_matches,
    extract_filename_label,
    extract_label_identifiers,
    has_identifier,
    line_in_range,
    make_source_url_parser,
)

# Generated artefacts only — `modules/`, `functional-requirements/` and the other
# content folders are all in scope for grounding.
SKIP_DIRS = {".ast", ".claims", ".trust", ".git", ".analysis", "node_modules"}


def round_half_up(x: float) -> int:
    """Round to the nearest integer with ties going up.

    Percentages hit exact ties often (7/8 → 87.5), and the built-in ``round`` would
    resolve them to even, so 87.5% and 88.5% would both report 88.
    """
    return math.floor(x + 0.5)


def format_pct(value: float | None) -> str:
    """A percentage as an integer when it is one, else one decimal place (ties up)."""
    if value is None or not math.isfinite(value):
        return "N/A"
    if float(value).is_integer():
        return str(int(value))
    return str(Decimal(value).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def walk(dir_: str) -> Iterator[str]:
    """Every ``.md`` file under ``dir_``, skipping generated trees and symlinks."""
    try:
        entries = list(os.scandir(dir_))
    except OSError as e:
        raise RuntimeError(f"cannot read {dir_}: {e}") from None
    for entry in entries:
        fp = os.path.join(dir_, entry.name)
        if entry.is_dir(follow_symlinks=False):
            if entry.name in SKIP_DIRS:
                continue
            yield from walk(fp)
        elif entry.is_file(follow_symlinks=False) and fp.endswith(".md"):
            yield fp


def validate_file(wiki_md_path: str, reader: SourceReader,
                  parse_source_url: Callable[[str], dict[str, Any] | None],
                  ) -> dict[str, Any]:
    """Grade every source deep-link on one page."""
    with open(wiki_md_path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    result: dict[str, Any] = {"total": 0, "checked": 0, "aligned": 0,
                              "drifts": [], "skipped": 0}
    for m in MD_LINK_RE.finditer(text):
        link_text, full_url = m.group(1), m.group(2)
        parsed = parse_source_url(full_url)
        if not parsed:
            continue
        file_path, line_no = parsed["file"], parsed["line"]
        result["total"] += 1
        filename_label = extract_filename_label(link_text)
        identifiers = [] if filename_label else extract_label_identifiers(link_text)
        # A label naming no symbol (`[출처]`, or a bare line reference such as
        # `` `L48-51` ``) makes no claim this axis can grade. Its *location* is still
        # checkable, though, so the file and the line are verified below before the link
        # is set aside — skipping first would let a typo'd path or an out-of-range line
        # through unexamined, and nothing downstream inspects them either.
        asserts_symbol = bool(filename_label) or len(identifiers) > 0
        label = filename_label or "|".join(identifiers) \
            or link_text.replace("`", "").strip()
        source = reader.read(file_path)
        if source is None:
            result["checked"] += 1
            result["drifts"].append({
                "symbol": label,
                "target": f"{file_path}#L{line_no}",
                "reason": "file not found in local repo",
            })
            continue
        lines = source["lines"]
        if not line_in_range(lines, line_no):
            result["checked"] += 1
            result["drifts"].append({
                "symbol": label,
                "target": f"{file_path}#L{line_no}",
                "reason": f"line out of range (file has {len(lines)} lines)",
            })
            continue
        if not asserts_symbol:
            result["skipped"] += 1
            continue
        result["checked"] += 1
        if filename_label:
            if basename_matches(file_path, filename_label):
                result["aligned"] += 1
            else:
                result["drifts"].append({
                    "symbol": filename_label,
                    "target": f"{file_path}#L{line_no}",
                    "reason": f'label filename "{filename_label}" does not match '
                              f'linked file basename '
                              f'"{os.path.basename(file_path)}"',
                })
            continue
        line = lines[line_no - 1]
        if any(has_identifier(line, id_) for id_ in identifiers):
            result["aligned"] += 1
        else:
            result["drifts"].append({
                "symbol": "|".join(identifiers),
                "target": f"{file_path}#L{line_no}",
                "reason": "no cited identifier on referenced line",
                "actual": line.strip()[:100],
            })
    return result


def read_deep_link(wiki_dir: str) -> Any:
    """``repo.json``'s deepLink config, or None (with a warning) when unreadable."""
    try:
        with open(os.path.join(wiki_dir, "repo.json"), encoding="utf-8",
                  errors="replace") as f:
            repo_json = json.loads(f.read())
    except Exception as e:
        print(f"[grounding] warning: could not read repo.json deepLink config "
              f"({e}); only `src:` links will be checkable", file=sys.stderr)
        return None
    return (repo_json.get("deepLink") if isinstance(repo_json, dict) else None) or None


def parse_args(argv: list[str]) -> dict[str, Any]:
    """Parse ``--key value`` / ``--flag`` pairs plus positionals."""
    out: dict[str, Any] = {"positional": []}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith("--"):
            key = arg[2:]
            nxt = argv[i + 1] if i + 1 < len(argv) else None
            if not nxt or nxt.startswith("--"):
                out[key] = True
            else:
                out[key] = nxt
                i += 1
        else:
            out["positional"].append(arg)
        i += 1
    return out


def opt(args: dict[str, Any], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def opt_int(args: dict[str, Any], key: str, default: int) -> int:
    """Integer value of ``--key``, falling back to ``default`` when unparsable.

    Falling back rather than failing keeps a typo from silently removing a cap.
    """
    value = opt(args, key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def main() -> int:
    args = parse_args(sys.argv[1:])
    positional = args["positional"]
    if len(positional) < 2:
        print("usage: python3 validate_grounding.py <wiki-dir> <local-repo-root> "
              "[--json out.json] [--list-all] [--max-files N] [--max-per-file N]",
              file=sys.stderr)
        return 2
    wiki_dir, repo_root = positional[0], positional[1]
    list_all = args.get("list-all") is True
    max_files = 10 ** 9 if list_all else opt_int(args, "max-files", 30)
    max_per_file = 10 ** 9 if list_all else opt_int(args, "max-per-file", 5)
    json_path_arg = opt(args, "json")
    parse_source_url = make_source_url_parser(read_deep_link(wiki_dir))
    # Many pages cite the same code files, so reads are cached across the whole run.
    reader = SourceReader(repo_root)

    total_links = 0
    total_checked = 0
    total_aligned = 0
    total_drifts = 0
    total_skipped = 0
    total_files = 0
    per_file: list[dict[str, Any]] = []
    for md_path in walk(wiki_dir):
        total_files += 1
        r = validate_file(md_path, reader, parse_source_url)
        total_links += r["total"]
        total_checked += r["checked"]
        total_aligned += r["aligned"]
        total_drifts += len(r["drifts"])
        total_skipped += r["skipped"]
        if len(r["drifts"]) > 0:
            per_file.append({"file": os.path.relpath(md_path, wiki_dir),
                             "absPath": md_path, "drifts": r["drifts"]})
    score = (total_aligned / total_checked) * 100 if total_checked > 0 else None
    drift_pct = (total_drifts / total_checked) * 100 if total_checked > 0 else 0
    score_text = "N/A" if score is None else str(round_half_up(score))

    if json_path_arg:
        # Written before the early N/A return so a caller always gets a file to read.
        json_path = os.path.abspath(json_path_arg)
        os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
        with open(json_path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps({
                "wikiDir": wiki_dir, "repoRoot": repo_root,
                "score": score if score is None else round_half_up(score),
                "total": total_links, "checked": total_checked,
                "aligned": total_aligned, "skipped": total_skipped,
                "drifts": total_drifts, "pages": total_files,
                "files": per_file,
            }, indent=2, ensure_ascii=False) + "\n")
        print(f"[grounding] wrote full result → {json_path}", file=sys.stderr)

    if total_links == 0:
        print(f"[grounding] N/A — no source deep-link(s) found across "
              f"{total_files} file(s)", file=sys.stderr)
        return 0

    print(f"[grounding] SCORE — {total_aligned}/{total_checked} "
          f"({format_pct(score)}%) checkable deep-link(s) aligned; "
          f"{total_drifts}/{total_checked} ({format_pct(drift_pct)}%) misaligned "
          f"across {len(per_file)} file(s); score={score_text}", file=sys.stderr)
    print(f"[grounding] scanned {total_links} source deep-link(s) across "
          f"{total_files} file(s)", file=sys.stderr)
    if total_skipped > 0:
        print(f"[grounding] (skipped {total_skipped} link(s) naming no symbol; their "
              f"file and line were still verified)", file=sys.stderr)
    if total_drifts == 0:
        return 0
    for f in per_file[:max_files]:
        print(f"\n  {f['absPath']}", file=sys.stderr)
        for d in f["drifts"][:max_per_file]:
            print(f"    - {d['symbol']} → {d['target']}", file=sys.stderr)
            print(f"      {d['reason']}", file=sys.stderr)
            if d.get("actual"):
                print(f"      actual: {d['actual']}", file=sys.stderr)
        if len(f["drifts"]) > max_per_file:
            print(f"    … {len(f['drifts']) - max_per_file} more", file=sys.stderr)
    if len(per_file) > max_files:
        print(f"\n  … {len(per_file) - max_files} more file(s)", file=sys.stderr)
    if not list_all and not json_path_arg \
            and (len(per_file) > max_files
                 or any(len(f["drifts"]) > max_per_file for f in per_file)):
        # Say so explicitly: a truncated list reads as the whole story otherwise, and
        # the report step needs to know it is looking at a sample.
        print("\n  (list truncated — rerun with --list-all, or --json out.json for the "
              "full result)", file=sys.stderr)
    # Hard gate: a citation pointing at a line that does not contain the cited symbol
    # is a factual error in the document, and nothing downstream would catch it.
    print(f"[grounding] FAIL — {total_drifts} misaligned deep-link(s); "
          f"fix the cited line(s) against .ast/api.json", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException:
        print(f"validate-grounding: {traceback.format_exc().rstrip()}", file=sys.stderr)
        sys.exit(3)
