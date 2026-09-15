#!/usr/bin/env python3
"""W1 Step 6 validation: required outputs + format discipline checks."""
import os, re, sys, json

OUT = "/home/hwang/work/D/starfish_/code2spec"
fails, warns = [], []

required = [
    "01-introduction.md", "02-architecture.md", "03-design-patterns.md",
    "04-data-layer.md", "05-external-interfaces.md",
    "06-configuration-deployment.md", "07-resources.md",
    "08-security-quality.md", "09-ipc-enum-catalog.md",
    "diagrams/architecture.mmd", "diagrams/dependency-heatmap.mmd",
    "functional-requirements/index.md",
    ".analysis/state/delta/module-groups.yaml",
    ".analysis/state/delta/analysis-progress.json",
    ".analysis/state/delta/core-manifest.json",
    ".analysis/state/delta/code2spec-config.json",
    ".analysis/state/delta/modules-traceability.md",
    ".analysis/analysis-notes/module-priority.md",
    ".analysis/analysis-notes/module-priority-reviewed.md",
    ".analysis/llm-extraction/llm-enum-results.json",
    ".analysis/llm-extraction/llm-constant-results.json",
    ".analysis/llm-extraction/llm-ipc-results.json",
    ".analysis/llm-extraction/llm-extraction-results.json",
    ".analysis/ipc-discovery/discovered-ipc-patterns.json",
    ".analysis/interface-candidates.json",
    ".analysis/cache/code-to-ast/graph-raw.json",
    ".ast/api.json", ".ast/deps.json", "repo.json",
]
for r in required:
    if not os.path.exists(os.path.join(OUT, r)):
        fails.append(f"MISSING: {r}")

md_files = [f for f in os.listdir(OUT) if f.endswith(".md")] + ["functional-requirements/index.md"]
for f in sorted(set(md_files)):
    p = os.path.join(OUT, f)
    if not os.path.exists(p):
        continue
    text = open(p, encoding="utf-8").read()
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        fails.append(f"{f}: missing H1 on first line")
        continue
    # RSF block directly under H1 (allow one blank line)
    idx = 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines) or not lines[idx].startswith("> **Relevant source files**"):
        fails.append(f"{f}: missing 'Relevant source files' block directly under H1")
    if re.search(r"\]\(https?://", text):
        fails.append(f"{f}: contains absolute http(s) source link")
    if "[Source:" in text:
        warns.append(f"{f}: contains raw '[Source:' marker (should be deep link)")
    n_deep = len(re.findall(r"\]\(src:[^)]+\)", text))
    n_line = len(re.findall(r"\]\(src:[^)]+#L\d+\)", text))
    print(f"  {f}: {len(lines)} lines, {n_deep} src links ({n_line} with #L)")
    # mermaid quick check: unquoted pipe-edge labels with special chars
    for m in re.finditer(r'--?>\|([^|"]*[ /:.()][^|"]*)\|', text):
        fails.append(f"{f}: unquoted mermaid edge label: {m.group(1)[:40]}")

# diagram files sanity
for d in ["diagrams/architecture.mmd", "diagrams/dependency-heatmap.mmd"]:
    p = os.path.join(OUT, d)
    if os.path.exists(p):
        head = open(p, encoding="utf-8").readline().strip()
        if not head.startswith(("graph", "flowchart")):
            fails.append(f"{d}: first line is not a mermaid graph header: {head!r}")

print()
for w in warns:
    print("WARN:", w)
for f_ in fails:
    print("FAIL:", f_)
print(f"\nRESULT: {'PASS' if not fails else 'FAIL'} ({len(fails)} failures, {len(warns)} warnings)")
sys.exit(1 if fails else 0)
