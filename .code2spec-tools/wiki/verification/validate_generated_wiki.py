#!/usr/bin/env python3
"""Run the whole validation pyramid over a generated wiki and record the scores.

Each validator is run as a subprocess, its output is scored 0..100 (or None for
"nothing to measure"), and the results are merged into ``<wiki>/repo.json`` under
``qualityScore`` / ``qualityBreakdown`` for the dashboard to read.

A None score is deliberate: an empty denominator — no diagram, no deep-link, no symbol —
must not be reported as a perfect 100. Only the HARD_GATES fail the pipeline;
MEASURE_ONLY axes are recorded and never block.

Usage:
  python3 validate_generated_wiki.py --repo-root <source> --wiki-dir <wiki>
    [--tier wiki-only|full] [--threshold 1.0] [--api-json X] [--deps-json Y]
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from math import floor
from pathlib import Path
from typing import Any

TOOL_DIR = str(Path(__file__).resolve().parent)

_WIKI_DIR = str(Path(__file__).resolve().parent.parent)
if _WIKI_DIR not in sys.path:
    sys.path.insert(0, _WIKI_DIR)

from page_model import CONDITIONAL_CHAPTERS, REQUIRED_SLOTS  # noqa: E402


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        key = argv[i]
        if not key.startswith("--"):
            i += 1
            continue
        nxt = argv[i + 1] if i + 1 < len(argv) else None
        if not nxt or nxt.startswith("--"):
            args[key[2:]] = True
        else:
            args[key[2:]] = nxt
            i += 1
        i += 1
    return args


def opt(args: dict[str, str | bool], key: str) -> str | None:
    """Value of ``--key`` when it was given with a non-empty string."""
    value = args.get(key)
    return value if isinstance(value, str) and value else None


def usage(message: str | None = None) -> None:
    if message:
        print(f"error: {message}", file=sys.stderr)
    print("usage: python3 validate_generated_wiki.py --repo-root <source> "
          "--wiki-dir <wiki> [--tier wiki-only|full]", file=sys.stderr)
    sys.exit(2)


def round_half_up(x: float) -> int:
    """Round to the nearest integer with ties going up.

    Percentages hit exact ties often (7/8 → 87.5), and the built-in ``round`` would
    resolve them to even, so 87.5% and 88.5% would both be recorded as 88.
    """
    return floor(x + 0.5)


# Validation covers the whole SDD output (README + 01..09 + modules/ +
# functional-requirements/): every page follows the same deep-link discipline, so one
# pipeline validates all of them. Only generated-artefact directories are skipped.
WALK_SKIP_DIRS = {
    "node_modules", ".git", ".ast", ".trust", ".claims", ".analysis",
}


def walk_markdown(dir_: str, out: list[str] | None = None) -> list[str]:
    """Every content ``.md`` under ``dir_``, sorted; templates are not content."""
    if out is None:
        out = []
    if not os.path.exists(dir_):
        return out
    for entry in os.scandir(dir_):
        fp = os.path.join(dir_, entry.name)
        if entry.is_dir(follow_symlinks=False):
            if entry.name in WALK_SKIP_DIRS or entry.name.startswith("."):
                continue
            walk_markdown(fp, out)
        elif entry.is_file(follow_symlinks=False) and fp.endswith(".md") \
                and entry.name != "_template.md":
            out.append(fp)
    return sorted(out)


def run(label: str, script_rel: str, args: list[str]) -> dict[str, Any]:
    """Run one validator and capture its verdict.

    stdout and stderr are merged because the validators split their reporting between
    the two, and ``score_from_output`` has to see all of it.
    """
    script = os.path.join(TOOL_DIR, script_rel)
    if not os.path.exists(script):
        return {"label": label, "exit": -1, "output": f"validator not found: {script}"}
    result = subprocess.run([sys.executable, script, *args],
                            capture_output=True, encoding="utf-8", errors="replace")
    return {
        "label": label,
        "exit": result.returncode,
        "output": ((result.stdout or "") + (result.stderr or "")).strip(),
    }


def score_from_output(label: str, result: dict[str, Any]) -> int | None:
    """A validator's output as a 0..100 score, or None when there was nothing to
    measure. An empty denominator must never be scored 100."""
    output = result["output"]
    if label == "requiredSlots":
        return 100 if result["exit"] == 0 else 0
    if label == "astBaseline":
        return 100 if result["exit"] == 0 else 0
    if label == "wikiStructure":
        return 100 if result["exit"] == 0 else 0
    if label == "mermaidSyntax":
        # No diagram at all → N/A; otherwise pass/fail by exit code.
        if re.search(r"\[mermaid\]\s+N/A", output):
            return None
        return 100 if result["exit"] == 0 else 0
    if label == "grounding":
        # No deep-link at all → N/A.
        if re.search(r"\[grounding\]\s+N/A", output):
            return None
        score = re.search(r"score=([0-9]+|N/A)", output)
        if score:
            return None if score.group(1) == "N/A" else int(score.group(1))
        aligned = re.search(r"SCORE\s+—\s+([0-9]+)/([0-9]+)\s+\(([0-9]+(?:\.[0-9]+)?)%\)",
                            output)
        if aligned:
            return round_half_up(float(aligned.group(3)))
        drift = re.search(r"DRIFT\s+—\s+([0-9]+)/([0-9]+)\s+\(([0-9]+(?:\.[0-9]+)?)%",
                          output)
        if drift:
            return max(0, round_half_up(100 - float(drift.group(3))))
        return 100 if result["exit"] == 0 else 0
    if label == "claimGrounding":
        total = re.search(r"claims:\s+([0-9]+)", output)
        if total and int(total.group(1)) == 0:
            return None
        m = re.search(r"supported:\s+[0-9]+\s+\(([0-9]+(?:\.[0-9]+)?)%\)", output)
        return round_half_up(float(m.group(1))) if m \
            else (100 if result["exit"] == 0 else 0)
    if label == "trustNlClaims" or label == "trustEnvClaims":
        return None      # informational enrichment, not a quality axis
    if label == "symbolCoverage":
        # No symbol, or no api.json → N/A.
        if re.search(r"N/A|No symbols found|symbols:\s+0\s+total", output):
            return None
        m = re.search(r"covered:\s+([0-9]+)\s+\(([0-9]+(?:\.[0-9]+)?)%\)", output)
        return round_half_up(float(m.group(2))) if m \
            else (100 if result["exit"] == 0 else 0)
    if label == "packageCoverage":
        # No package discovered → N/A.
        if re.search(r"N/A|No packages discovered|packages:\s+0\s+discovered", output):
            return None
        m = re.search(r"covered:\s+[0-9]+\s+\(([0-9]+(?:\.[0-9]+)?)%\)", output)
        return round_half_up(float(m.group(1))) if m \
            else (100 if result["exit"] == 0 else 0)
    if label == "diagramAccuracy":
        # No parsed edge, or no deps.json → N/A.
        parsed = re.search(r"parsed edges:\s+([0-9]+)", output)
        if (parsed and int(parsed.group(1)) == 0) or re.search(r"N/A", output):
            return None
        m = re.search(r"supported:\s+[0-9]+\s+\(([0-9]+(?:\.[0-9]+)?)%\)", output)
        return round_half_up(float(m.group(1))) if m \
            else (100 if result["exit"] == 0 else 0)
    if label == "moduleFrPairing":
        # Neither modules/ nor functional-requirements/ has content → N/A.
        if re.search(r"N/A", output):
            return None
        m = re.search(r"matched:\s+[0-9]+\s+\(([0-9]+(?:\.[0-9]+)?)%\)", output)
        return round_half_up(float(m.group(1))) if m \
            else (100 if result["exit"] == 0 else 0)
    return 100 if result["exit"] == 0 else 0


def compact(label: str, output: str) -> str:
    """The one or two lines of a validator's output worth storing in repo.json."""
    lines = [line for line in re.split(r"\r?\n", output) if line]

    def find(pred: Callable[[str], bool]) -> str | None:
        return next((line for line in lines if pred(line)), None)

    if label == "astBaseline":
        return find(lambda line: "status:" in line) or output
    if label == "wikiStructure":
        return "\n".join(lines[:6]) if output else "pass"
    if label == "mermaidSyntax":
        return find(lambda line: "[mermaid]" in line) \
            or ((lines[0] if lines else "") if output else "pass")
    if label == "grounding":
        return find(lambda line: "[grounding] SCORE" in line
                    or "[grounding] N/A" in line
                    or "[grounding] ok" in line
                    or "[grounding] DRIFT" in line) or output
    if label == "claimGrounding":
        supported = find(lambda line: line.strip().startswith("supported:"))
        contradicted = find(lambda line: line.strip().startswith("contradicted:"))
        badges = find(lambda line: line.strip().startswith("badge links:"))
        return "\n".join([x for x in (supported, contradicted, badges) if x]) or output
    if label == "trustNlClaims":
        return find(lambda line: line.startswith("merged ")) or output
    if label == "trustEnvClaims":
        return find(lambda line: line.startswith("env claims:")) or output
    if label == "symbolCoverage":
        if re.search(r"N/A|No symbols found|symbols:\s+0\s+total", output):
            return "N/A - no symbols to cover"
        return find(lambda line: line.strip().startswith("covered:")) or output
    if label == "packageCoverage":
        if re.search(r"N/A|No packages discovered|packages:\s+0\s+discovered", output):
            return "N/A - no packages discovered"
        return find(lambda line: line.strip().startswith("covered:")) or output
    if label == "diagramAccuracy":
        parsed = re.search(r"parsed edges:\s+([0-9]+)", output)
        if parsed and int(parsed.group(1)) == 0:
            return "N/A - no graph/flowchart edges parsed"
        return find(lambda line: line.strip().startswith("supported:")) or output
    if label == "moduleFrPairing":
        if re.search(r"N/A", output):
            return find(lambda line: "N/A" in line) or output
        lines_to_keep = [find(lambda line: line.strip().startswith("matched:"))]
        lines_to_keep += [line for line in lines if line.strip().startswith("✗")]
        return "\n".join(x for x in lines_to_keep if x) or output
    return output


def slot_exists(wiki_dir: str, slot: str) -> bool:
    """Whether a required slot is present; a slot ending in ``/`` must be non-empty."""
    target = os.path.join(wiki_dir, slot)
    if slot.endswith("/"):
        try:
            return os.path.isdir(target) and len(os.listdir(target)) > 0
        except OSError:
            return False
    return os.path.exists(target)


def check_required_slots(wiki_dir: str) -> dict[str, Any]:
    """Check the SDD output contract from ``page_model.py``: the core chapters plus the
    structural slots (``modules/``, ``functional-requirements/index.md``).

    A missing *conditional* chapter is not a failure — not generating one for lack of
    evidence is the correct outcome.
    """
    missing = [s for s in REQUIRED_SLOTS if not slot_exists(wiki_dir, s)]
    present_conditional = [f for f in CONDITIONAL_CHAPTERS
                           if os.path.exists(os.path.join(wiki_dir, f))]
    if len(missing) == 0:
        conditional_note = (f" (+ {len(present_conditional)} conditional: "
                            f"{', '.join(present_conditional)})") \
            if present_conditional else " (no conditional chapters generated)"
        return {"label": "requiredSlots", "exit": 0,
                "output": f"all {len(REQUIRED_SLOTS)} required SDD slots present"
                          f"{conditional_note}"}
    return {
        "label": "requiredSlots",
        "exit": 1,
        "output": f"[required-slots] FAIL — missing {len(missing)}/{len(REQUIRED_SLOTS)} "
                  f"required slots:\n" + "\n".join(f"  - {f}" for f in missing),
    }


def main() -> int:
    args = parse_args(sys.argv[1:])
    repo_root_arg = opt(args, "repo-root")
    wiki_dir_arg = opt(args, "wiki-dir")
    if not repo_root_arg or not wiki_dir_arg:
        usage("missing --repo-root or --wiki-dir")
        return 2
    repo_root = os.path.abspath(repo_root_arg)
    wiki_dir = os.path.abspath(wiki_dir_arg)
    tier = opt(args, "tier") or "full"
    threshold = opt(args, "threshold") or "1.0"
    md_files = walk_markdown(wiki_dir)
    if len(md_files) == 0:
        usage(f"no markdown files under {wiki_dir}")

    results: list[dict[str, Any]] = []
    results.append(check_required_slots(wiki_dir))
    results.append(run("wikiStructure", "validate_wiki_structure.py", md_files))
    results.append(run("mermaidSyntax", "validate_mermaid.py", md_files))
    results.append(run("moduleFrPairing", "validate_module_fr_pairing.py",
                       [wiki_dir, "--threshold", threshold]))

    if tier != "wiki-only":
        api_json = opt(args, "api-json") or os.path.join(wiki_dir, ".ast", "api.json")
        deps_json = opt(args, "deps-json") or os.path.join(wiki_dir, ".ast", "deps.json")
        results.append(run("astBaseline", "validate_ast_baseline.py", [
            "--repo-root", repo_root,
            "--wiki-dir", wiki_dir,
            "--api-json", api_json,
            "--deps-json", deps_json,
        ]))
        results.append(run("grounding", "validate_grounding.py", [wiki_dir, repo_root]))
        # The trust artefact the dashboard viewer reads.
        trust_json = os.path.join(wiki_dir, ".trust", "claims.json")
        os.makedirs(os.path.dirname(trust_json), exist_ok=True)
        results.append(run("claimGrounding", "validate_wiki_claims.py",
                           [wiki_dir, repo_root, "--json", trust_json]))
        if os.path.exists(api_json):
            results.append(run("symbolCoverage", "validate_symbol_coverage.py",
                               [api_json, wiki_dir, "--threshold", threshold]))
        else:
            results.append({"label": "symbolCoverage", "exit": 0,
                            "output": "[symbol-coverage] N/A — api.json absent"})
        results.append(run("packageCoverage", "validate_package_coverage.py",
                           [repo_root, wiki_dir, "--threshold", threshold]))
        if os.path.exists(deps_json):
            results.append(run("diagramAccuracy", "validate_diagram_accuracy.py",
                               [deps_json, wiki_dir, "--threshold", threshold]))
        else:
            results.append({"label": "diagramAccuracy", "exit": 0,
                            "output": "[diagram-accuracy] N/A — deps.json absent"})

    # Recorded, but never allowed to fail the pipeline.
    MEASURE_ONLY = {"trustEnvClaims", "trustNlClaims"}
    # Only these fail the run when they exit non-zero.
    HARD_GATES = {
        "requiredSlots", "astBaseline", "wikiStructure", "mermaidSyntax",
        "grounding", "claimGrounding", "diagramAccuracy", "moduleFrPairing",
    }
    quality_score: dict[str, int | None] = {}
    validators: dict[str, str] = {}
    failed = False
    for result in results:
        label = result["label"]
        quality_score[label] = score_from_output(label, result)
        validators[label] = compact(label, result["output"])
        if result["exit"] > 0 and label in HARD_GATES and label not in MEASURE_ONLY:
            failed = True
        score = quality_score[label]
        # `null`, not `None`: this is the same value that lands in repo.json as JSON.
        print(f"[{label}] exit={result['exit']} "
              f"score={'null' if score is None else score}")
        if result["output"]:
            print(result["output"])

    repo_json_path = os.path.join(wiki_dir, "repo.json")
    repo_json: dict[str, Any] = {}
    if os.path.exists(repo_json_path):
        with open(repo_json_path, encoding="utf-8", errors="replace") as f:
            repo_json = json.loads(f.read())
    previous_breakdown = repo_json.get("qualityBreakdown") or {}
    merged_validators = {**(previous_breakdown.get("validators") or {}), **validators} \
        if tier == "wiki-only" else validators
    repo_json["qualityScore"] = {**(repo_json.get("qualityScore") or {}),
                                 **quality_score}
    repo_json["qualityBreakdown"] = {
        "verifiedAt": datetime.now(UTC)
                      .isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "method": "deterministic wiki-only hook validators; existing full-validator "
                  "entries are preserved when present"
                  if tier == "wiki-only"
                  else "deterministic validators only; CodeWikiBench and "
                       "LLM-as-judge excluded",
        "validators": merged_validators,
    }
    if previous_breakdown.get("details"):
        repo_json["qualityBreakdown"]["details"] = previous_breakdown["details"]
    with open(repo_json_path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(repo_json, indent=2, ensure_ascii=False) + "\n")
    print(f"updated {repo_json_path}")

    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
