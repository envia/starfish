#!/usr/bin/env python3
"""Deterministic claim-candidate validator for a whole wiki.

Only claims that can be derived mechanically from a markdown source link are
extracted — no attempt is made to understand natural-language prose:

* the linked source file exists in the local repo (line-anchored **and** whole-file
  links: an RSF block's ``[src/foo.ts](…/src/foo.ts)`` is graded too)
* the linked source line exists
* a filename label (`` [`foo.ts`](…) ``) matches the linked file's basename
* a backticked identifier in the link text appears in the linked file
* a backticked call signature (`` `Foo.issue(userId, email)` ``) matches the actual
  parameter names of that method/function **at the cited line**

Exits 1 as soon as one candidate is contradicted, which makes this the hard
``claimGrounding`` gate.

The per-link predicates are shared with the other validators via ``citation_checks``
(issue #33); this module owns only which claims are extracted, the hard gate, and the
``.trust/claims.json`` artefact.

``.trust/claims.json`` is also the **per-link trust badge** data the dashboard viewer
reads. ``results[]`` holds one record per *predicate*, so the artefact additionally
carries ``links[]``: one rolled-up verdict per cited URL (the badge the viewer places
next to the link). This used to live in ``.trust/atomic-claims.json``, whose axis
re-graded these same predicates and was removed.

Usage: python3 validate_wiki_claims.py <wiki-dir> <repo-root> [--top 50]
         [--json <report.json>]
"""

from __future__ import annotations

import json
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from citation_checks import (
    MD_LINK_RE,
    SourceReader,
    basename_matches,
    code_like_text,
    extract_code_identifiers,
    extract_filename_label,
    find_method,
    has_identifier,
    line_at_offset,
    line_in_range,
    make_file_only_parser,
    make_source_url_parser,
    parse_call_signature,
    parse_parameters,
)

DEFAULT_TOP = 50


def usage(message: str | None = None) -> None:
    if message:
        print(f"error: {message}", file=sys.stderr)
    print("usage: python3 validate_wiki_claims.py <wiki-dir> "
          "<repo-root> [--top 50]", file=sys.stderr)
    sys.exit(2)


def parse_args(argv: list[str]) -> dict[str, Any]:
    """Parse ``--key value`` / ``--flag`` pairs plus positionals.

    A flag given without a value becomes True, and a repeated flag keeps its last
    value.
    """
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


def parse_top(value: str | None) -> int:
    """``--top`` as a non-negative row limit, falling back to the default."""
    if value is None:
        return DEFAULT_TOP
    m = re.match(r"\s*([0-9]+)", value)
    return int(m.group(1)) if m else DEFAULT_TOP


def format_percent(x: float) -> str:
    """A percentage to one decimal place, with ties rounded up.

    Ties are reached at realistic denominators (13/16 → 81.25), and the built-in
    formatter would resolve them to even and report 81.2.
    """
    return str(Decimal(x).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def normalize_path(value: str) -> str:
    return value.replace(os.sep, "/")


def read_deep_link(dir_: str) -> Any:
    """``repo.json``'s deepLink config, or None (with a warning) when unreadable."""
    try:
        with open(os.path.join(dir_, "repo.json"), encoding="utf-8",
                  errors="replace") as f:
            repo_json = json.loads(f.read())
    except Exception as e:
        print(f"warning: could not read repo.json deepLink config ({e}); "
              f"only `src:` links will be checkable", file=sys.stderr)
        return None
    return (repo_json.get("deepLink") if isinstance(repo_json, dict) else None) or None


def walk_markdown(root: str) -> list[str]:
    """Every content ``.md`` under ``root``, sorted; templates are not content."""
    out: list[str] = []

    def walk(dir_: str) -> None:
        for entry in os.scandir(dir_):
            if entry.name.startswith(".") and entry.name != ".code-wiki":
                continue
            if entry.name == "node_modules":
                continue
            fp = os.path.join(dir_, entry.name)
            if entry.is_dir(follow_symlinks=False):
                walk(fp)
            elif entry.is_file(follow_symlinks=False) and fp.endswith(".md") \
                    and entry.name not in ("_template.md", "FR.md"):
                out.append(fp)
    walk(root)
    return sorted(out)


def extract_markdown_links(text: str) -> list[dict[str, Any]]:
    return [{"text": m.group(1), "url": m.group(2),
             "line": line_at_offset(text, m.start())}
            for m in MD_LINK_RE.finditer(text)]


def result(input_: dict[str, Any]) -> dict[str, Any]:
    """One claim record. Empty optional fields are dropped, not emitted as blanks."""
    target = input_["target"]
    out = {
        "status": input_["status"],
        "type": input_["type"],
        "page": input_["page"],
        "line": input_["line"],
        "text": input_["text"],
        "target": f"{target['file']}#L{target['line']}" if target["line"]
                  else f"{target['file']}",
    }
    if target.get("url"):
        out["url"] = target["url"]
    if input_.get("evidence"):
        out["evidence"] = input_["evidence"]
    if input_.get("reason"):
        out["reason"] = input_["reason"]
    return out


def rollup_links(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One badge verdict per cited link, in page order.

    The viewer renders a badge beside a link, not beside a predicate, so the several
    records a single link produces (existence, line, label, signature, identifier)
    are folded into one: the worst verdict wins — a link is only trustworthy when
    every predicate about it held. Reasons of the deciding records are kept so the
    badge can explain itself without the viewer re-joining ``results[]``.
    """
    order: list[str] = []
    by_link: dict[str, dict[str, Any]] = {}
    rank = {"supported": 0, "unresolved": 1, "contradicted": 2}
    for r in results:
        key = f"{r['page']}\t{r['line']}\t{r.get('url') or r['target']}"
        entry = by_link.get(key)
        if entry is None:
            order.append(key)
            entry = {"page": r["page"], "line": r["line"], "text": r["text"],
                     "target": r["target"], "status": r["status"], "checks": 0,
                     "reasons": []}
            if r.get("url"):
                entry["url"] = r["url"]
            by_link[key] = entry
        entry["checks"] += 1
        if rank[r["status"]] > rank[entry["status"]]:
            entry["status"] = r["status"]
        if r.get("reason"):
            entry["reasons"].append(r["reason"])
    out = []
    for key in order:
        entry = by_link[key]
        if not entry["reasons"]:
            del entry["reasons"]
        out.append(entry)
    return out


def print_result(r: dict[str, Any]) -> None:
    print(f"  [{r['type']}] {r['page']}:{r['line']}")
    print(f"    text: {r['text']}")
    print(f"    target: {r['target']}")
    if r.get("evidence"):
        print(f"    evidence: {r['evidence']}")
    if r.get("reason"):
        print(f"    reason: {r['reason']}")


def main() -> int:
    args = parse_args(sys.argv[1:])
    positional = args["positional"]
    wiki_dir_arg = positional[0] if len(positional) > 0 else None
    repo_root_arg = positional[1] if len(positional) > 1 else None
    if not wiki_dir_arg or not repo_root_arg:
        usage("missing args")

    wiki_dir = os.path.abspath(wiki_dir_arg)
    repo_root = os.path.abspath(repo_root_arg)
    top_n = parse_top(opt(args, "top"))
    if not os.path.exists(wiki_dir):
        usage(f"wiki dir not found: {wiki_dir}")
    if not os.path.exists(repo_root):
        usage(f"repo root not found: {repo_root}")

    deep_link = read_deep_link(wiki_dir)
    parse_source_url = make_source_url_parser(deep_link)
    # RSF blocks link whole files with no `#L`; a broken one is just as much a false
    # claim as a broken line anchor, so those links are graded too — by existence
    # only, since there is no line to check (issue #33).
    parse_file_only = make_file_only_parser(deep_link)

    reader = SourceReader(repo_root)

    def validate_source_link(rel_md: str, link: dict[str, Any],
                             target: dict[str, Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        abs_ = reader.path(target["file"])
        exists = os.path.exists(abs_)
        out.append(result({
            "status": "supported" if exists else "contradicted",
            "type": "source_target_exists",
            "page": rel_md,
            "line": link["line"],
            "text": link["text"],
            "target": target,
            "evidence": target["file"] if exists else "",
            "reason": "" if exists else f"source target not found: {target['file']}",
        }))
        if not exists:
            return out

        if not os.path.isfile(abs_):
            return out
        source = reader.read(target["file"])
        if source is None:
            return out

        if target["line"] is not None:
            in_range = line_in_range(source["lines"], target["line"])
            out.append(result({
                "status": "supported" if in_range else "contradicted",
                "type": "source_line_exists",
                "page": rel_md,
                "line": link["line"],
                "text": link["text"],
                "target": target,
                "evidence": f"{target['file']}:{target['line']}" if in_range else "",
                "reason": "" if in_range else
                          f"line {target['line']} out of range; file has "
                          f"{len(source['lines'])} lines",
            }))

        # A filename label claims "this link shows file X" — graded by basename,
        # since a filename never appears as text inside its own source lines.
        # grounding checks the same predicate but only for backticked labels;
        # requiring no backtick here keeps the gate closed for whatever
        # fix_citation_labels did not repair.
        filename_label = extract_filename_label(link["text"], require_backtick=False)
        if filename_label:
            label_ok = basename_matches(target["file"], filename_label)
            out.append(result({
                "status": "supported" if label_ok else "contradicted",
                "type": "filename_label_matches",
                "page": rel_md,
                "line": link["line"],
                "text": link["text"],
                "target": target,
                "evidence": target["file"] if label_ok else "",
                "reason": "" if label_ok else
                          f'label filename "{filename_label}" does not match linked '
                          f'file basename "{os.path.basename(target["file"])}"',
            }))
            # A filename label is graded above by basename only. The identifier/
            # signature checks below assume the label names a *symbol* the file's
            # text should contain — but per the module docstring, a filename is a
            # distinct claim type from a backticked identifier, and (per
            # extract_filename_label's own contract) a filename never appears as
            # literal text inside its own source lines. Running those checks here
            # too would treat the filename's dot-separated parts as identifiers to
            # search for and always spuriously contradict an already-graded claim.
            return out

        code_text = code_like_text(link["text"])
        if not code_text:
            return out

        signature = parse_call_signature(code_text)
        if signature:
            # The cited line disambiguates same-named declarations: the signature is
            # graded against the declaration the citation actually points at.
            method = find_method(source["text"], signature["method"],
                                 near_line=target["line"])
            if not method:
                out.append(result({
                    "status": "contradicted",
                    "type": "signature_matches",
                    "page": rel_md,
                    "line": link["line"],
                    "text": link["text"],
                    "target": target,
                    "reason": f"method/function {signature['method']} not found in "
                              f"{target['file']}",
                }))
            else:
                actual = parse_parameters(method["signature"])
                ok = actual == signature["params"]
                out.append(result({
                    "status": "supported" if ok else "contradicted",
                    "type": "signature_matches",
                    "page": rel_md,
                    "line": link["line"],
                    "text": link["text"],
                    "target": target,
                    "evidence": f"{target['file']}:{method['line']}" if ok else "",
                    "reason": "" if ok else
                              f"documented params ({', '.join(signature['params'])}), "
                              f"actual params ({', '.join(actual)}) at "
                              f"{target['file']}:{method['line']}",
                }))

        identifiers = extract_code_identifiers(code_text)
        if len(identifiers) > 0:
            # Judged against the whole file on purpose: the line-alignment axis is
            # grounding's hard gate, and double-gating it here would report every
            # off-by-N twice. The cited line only sharpens the evidence.
            haystack = source["lines"][target["line"] - 1] \
                if (target["line"] and 0 <= target["line"] - 1 < len(source["lines"])
                    and source["lines"][target["line"] - 1]) else ""
            file_matched = any(has_identifier(source["text"], i) for i in identifiers)
            line_matched = bool(haystack) and \
                any(has_identifier(haystack, i) for i in identifiers)
            line_suffix = f":{target['line']}" if (line_matched and target["line"]) else ""
            out.append(result({
                "status": "supported" if file_matched else "contradicted",
                "type": "linked_file_mentions_identifier",
                "page": rel_md,
                "line": link["line"],
                "text": link["text"],
                "target": target,
                "evidence": f"{target['file']}{line_suffix}" if file_matched else "",
                "reason": "" if file_matched else
                          f"none of ({', '.join(identifiers)}) found in linked file",
            }))

        return out

    md_files = walk_markdown(wiki_dir)
    results: list[dict[str, Any]] = []
    source_links = 0

    for md_path in md_files:
        with open(md_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
        rel_md = normalize_path(os.path.relpath(md_path, wiki_dir))
        for link in extract_markdown_links(text):
            target = parse_source_url(link["url"]) or parse_file_only(link["url"])
            if not target:
                continue
            source_links += 1
            results.extend(validate_source_link(rel_md, link, target))

    counts = {
        "supported": len([r for r in results if r["status"] == "supported"]),
        "contradicted": len([r for r in results if r["status"] == "contradicted"]),
        "unresolved": len([r for r in results if r["status"] == "unresolved"]),
    }
    links = rollup_links(results)
    total = len(results)
    # An empty denominator (no claim extracted) reports N/A rather than a fake 100%.
    supported_ratio = None if total == 0 else counts["supported"] / total
    contradicted = [r for r in results if r["status"] == "contradicted"]
    unresolved = [r for r in results if r["status"] == "unresolved"]

    print("Wiki Claim Candidate Validation")
    print(f"  wiki:          {wiki_dir}")
    print(f"  repo:          {repo_root}")
    print(f"  pages:         {len(md_files)}")
    print(f"  source links:  {source_links}")
    print(f"  claims:        {total}")
    ratio_text = "N/A" if supported_ratio is None \
        else format_percent(supported_ratio * 100) + "%"
    print(f"    supported:    {counts['supported']} ({ratio_text})")
    print(f"    contradicted: {counts['contradicted']}")
    print(f"    unresolved:   {counts['unresolved']}")
    print(f"  badge links:   {len(links)} "
          f"(trusted {len([x for x in links if x['status'] == 'supported'])})")
    print()

    for label, rows in (("Contradicted", contradicted), ("Unresolved", unresolved)):
        if not rows:
            continue
        print(f"{label} claim candidates (top {min(top_n, len(rows))}):")
        for r in rows[:top_n]:
            print_result(r)
        if len(rows) > top_n:
            print(f"  ... (+{len(rows) - top_n} more)")
        print()

    json_path_arg = opt(args, "json")
    if json_path_arg:
        json_path = os.path.abspath(json_path_arg)
        os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
        with open(json_path, "w", encoding="utf-8", newline="") as f:
            f.write(json.dumps({
                "wikiDir": wiki_dir,
                "repoRoot": repo_root,
                "pages": len(md_files),
                "sourceLinks": source_links,
                "counts": counts,
                # One verdict per cited link — the viewer's badge data.
                "links": links,
                "results": results,
            }, indent=2, ensure_ascii=False) + "\n")
        print(f"Wrote {json_path}")

    if counts["contradicted"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
