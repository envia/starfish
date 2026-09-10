#!/usr/bin/env python3
"""Fill the dashboard metadata in ``repo.json``: description, languages, defaultBranch.

Runs on top of what ``prepare_code_wiki.py`` wrote and deletes any stale
``qualityScore`` / ``qualityBreakdown`` before the real validation runs, so a
placeholder score can never be mistaken for a verified one. ``--keep-quality``
opts out of that deletion.

Usage:
  python3 write_wiki_metadata.py --repo-root <source> --wiki-dir <wiki>
    [--description <text>] [--branch <name>] [--languages <csv>] [--keep-quality]
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Any


def parse_args(argv: list[str]) -> dict[str, str | bool]:
    """Parse ``--key value`` / ``--flag`` pairs; a flag without a value becomes True."""
    args: dict[str, str | bool] = {}
    i = 0
    while i < len(argv):
        key = argv[i]
        if key.startswith("--"):
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
    print("usage: python3 write_wiki_metadata.py --repo-root <source> --wiki-dir <wiki>",
          file=sys.stderr)
    sys.exit(2)


def read_context(wiki_dir: str) -> dict[str, Any]:
    """repo.json as a dict, or ``{}`` when it is missing or unreadable."""
    repo_json_path = os.path.join(wiki_dir, "repo.json")
    if not os.path.exists(repo_json_path):
        return {}
    try:
        with open(repo_json_path, encoding="utf-8", errors="replace") as f:
            loaded = json.loads(f.read())
    except (OSError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def git(repo_root: str, args: list[str], fallback: str = "") -> str:
    """Run git and return its trimmed stdout, or ``fallback`` when it fails.
    stderr is inherited so git's diagnostics still reach the user."""
    try:
        proc = subprocess.run(
            ["git", *args], cwd=repo_root,
            stdout=subprocess.PIPE, encoding="utf-8", errors="replace",
        )
    except OSError:
        return fallback
    if proc.returncode != 0:
        return fallback
    return proc.stdout.strip()


# Language detection is a `git ls-files` extension tally: it counts files (not bytes)
# and reports the top 3. AI-agent config directories are excluded because they are
# full of JS/JSON tooling that is not part of the repo's own codebase and would
# otherwise make any repository look JavaScript-dominant.
_EXCLUDE_RE = re.compile(
    r"(^|/)(node_modules|dist|build|out|target|vendor|third_party"
    r"|\.claude|\.codex|\.cline|\.cursor)/")

# Extension → language, using GitHub Linguist's names. Only programming/markup
# languages are listed; data and prose formats (JSON, YAML, Markdown) are omitted
# so they cannot dominate the tally.
_EXT_MAP = {
    "ts": "TypeScript", "tsx": "TypeScript",
    "js": "JavaScript", "mjs": "JavaScript", "cjs": "JavaScript",
    "py": "Python", "pyi": "Python", "pyw": "Python",
    "c": "C", "h": "C",
    "cc": "C++", "cpp": "C++", "cxx": "C++", "hpp": "C++",
    "hh": "C++", "hxx": "C++", "ipp": "C++",
    "cs": "C#", "rb": "Ruby", "swift": "Swift",
    "m": "Objective-C", "mm": "Objective-C++",
    "java": "Java", "kt": "Kotlin", "kts": "Kotlin", "go": "Go", "rs": "Rust",
    "scala": "Scala", "dart": "Dart", "lua": "Lua",
    "pl": "Perl", "pm": "Perl", "r": "R", "R": "R", "jl": "Julia",
    "hs": "Haskell", "ex": "Elixir", "exs": "Elixir", "erl": "Erlang", "hrl": "Erlang",
    "clj": "Clojure", "cljs": "Clojure", "groovy": "Groovy", "vala": "Vala",
    "zig": "Zig", "nim": "Nim",
    "f": "Fortran", "f90": "Fortran", "f95": "Fortran",
    "s": "Assembly", "S": "Assembly", "asm": "Assembly",
    "php": "PHP",
    "sh": "Shell", "bash": "Shell", "zsh": "Shell",
    "ps1": "PowerShell", "bat": "Batchfile", "cmd": "Batchfile",
    "cmake": "CMake",
    "html": "HTML", "htm": "HTML", "css": "CSS", "scss": "SCSS", "less": "Less",
    "vue": "Vue", "svelte": "Svelte",
}


def detect_languages(repo_root: str) -> list[str]:
    """Top 3 languages by tracked-file count."""
    files = [f for f in re.split(r"\r?\n", git(repo_root, ["ls-files"])) if f]
    counts: dict[str, int] = {}
    for file in files:
        if _EXCLUDE_RE.search(file):
            continue
        ext = file.split(".")[-1]
        if file.endswith("CMakeLists.txt"):
            ext = "cmake"
        lang = _EXT_MAP.get(ext)
        if lang is None:
            continue
        counts[lang] = counts.get(lang, 0) + 1
    # Stable sort: languages with the same count keep first-seen order.
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [name for name, _ in ranked[:3]]


def first_readme_sentence(wiki_dir: str) -> str:
    """First complete sentence of README.md's first paragraph, as plain text.

    ``description`` has to be a single introductory sentence, so headings,
    blockquotes, code fences and markdown emphasis are stripped first and the cut is
    made only at a sentence boundary (period followed by whitespace or end of text) —
    never in the middle of a word or a dotted identifier such as ``v2_11.0``.
    """
    readme = os.path.join(wiki_dir, "README.md")
    if not os.path.exists(readme):
        return ""
    with open(readme, encoding="utf-8", errors="replace") as f:
        text = f.read()
    # A BOM survives plain utf-8 decoding and is invisible in the output; drop all of them.
    text = text.replace("\ufeff", "")
    text = re.sub(r"```[\s\S]*?```", "", text)                  # code fences
    text = re.sub(r"^\s*#{1,6}\s.*$", "", text, flags=re.M)     # ATX headings
    text = re.sub(r"^\s*>.*$", "", text, flags=re.M)            # blockquotes
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)        # links → label
    text = re.sub(r"[`*_]", "", text).strip()                   # backticks / emphasis
    first_para = next((p for p in (x.strip() for x in re.split(r"\n\s*\n", text)) if p), "")
    normalized = re.sub(r"\s+", " ", first_para).strip()
    if not normalized:
        return ""
    m = re.match(r"^.*?[.。](?=\s|$)", normalized)
    sentence = (m.group(0) if m else normalized).strip()
    if len(sentence) > 200:
        sentence = re.sub(r"\s+\S*$", "", sentence[:200]).strip()
    return sentence


def main() -> int:
    args = parse_args(sys.argv[1:])
    if not opt(args, "repo-root") or not opt(args, "wiki-dir"):
        usage("missing --repo-root or --wiki-dir")
    repo_root = os.path.abspath(str(args["repo-root"]))
    wiki_dir = os.path.abspath(str(args["wiki-dir"]))
    context = {**read_context(wiki_dir), "repoRoot": repo_root, "outDir": wiki_dir}
    repo_json_path = os.path.join(wiki_dir, "repo.json")
    repo_json: dict[str, Any] = {}
    if os.path.exists(repo_json_path):
        # Deliberately not guarded: a repo.json that cannot be parsed here means the
        # dashboard context is broken, and silently rewriting it would hide that.
        with open(repo_json_path, encoding="utf-8", errors="replace") as f:
            repo_json = json.loads(f.read())

    repo_json["description"] = (
        opt(args, "description")
        or repo_json.get("description")
        or first_readme_sentence(wiki_dir)
        or f"{context.get('repo') or os.path.basename(repo_root)} code wiki."
    )
    repo_json["defaultBranch"] = (
        opt(args, "branch")
        or repo_json.get("defaultBranch")
        or context.get("branch")
        or git(repo_root, ["rev-parse", "--abbrev-ref", "HEAD"], "main")
    )
    languages_csv = opt(args, "languages")
    if languages_csv:
        repo_json["languages"] = [
            s for s in (t.strip() for t in languages_csv.split(",")) if s]
    else:
        repo_json["languages"] = (repo_json.get("languages")
                                  or detect_languages(repo_root))

    if not args.get("keep-quality"):
        repo_json.pop("qualityScore", None)
        repo_json.pop("qualityBreakdown", None)

    with open(repo_json_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(repo_json, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"repoJsonPath": repo_json_path}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
