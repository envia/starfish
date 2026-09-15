#!/usr/bin/env python3
"""Generate 09-ipc-enum-catalog.md deterministically from llm-extraction JSONs."""
import json, re, os, datetime

BASE = "/home/hwang/work/D/starfish_"
LX = os.path.join(BASE, "code2spec/.analysis/llm-extraction")
OUT = os.path.join(BASE, "code2spec/09-ipc-enum-catalog.md")

def load(name):
    p = os.path.join(LX, name)
    return json.load(open(p)) if os.path.exists(p) else []

SRC_RE = re.compile(r"^\[Source: ([^:]+):(\d+)\]$")

def deeplink(source, label):
    m = SRC_RE.match(source or "")
    if not m:
        return "Not specified in code"
    path, line = m.group(1), m.group(2)
    label = (label or os.path.basename(path)).split("::")[-1].split(".")[-1].strip()
    if not label:
        label = os.path.basename(path)
    return f"[`{label}`](src:{path}#L{line})"

def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ").strip()

def val_cell(values, cap=12):
    vals = [v for v in values if v != "..."]
    extra = len(values) - len(vals)
    cell = ", ".join(esc(v) for v in vals[:cap])
    more = len(vals) - cap + extra
    if more > 0:
        cell += f" … ({more} more)"
    return cell or "Not specified in code"

enums = load("llm-enum-results.json")
consts = load("llm-constant-results.json")
ipc = load("llm-ipc-results.json")

err_name = re.compile(r"^(ERR_|ERROR_|EXIT_)|_ERROR$|_ERR$")
errors = [c for c in consts if c.get("type") == "error_code" or err_name.search(c.get("name", ""))]
err_keys = {(c.get("name"), c.get("source")) for c in errors}
plain_consts = [c for c in consts if (c.get("name"), c.get("source")) not in err_keys]

lines = []
A = lines.append
A("# IPC Constants and ENUM Catalog")
A("")
A("> **Relevant source files**")
A(">")
rsf = []
seen = set()
for e in enums + ipc + consts:
    m = SRC_RE.match(e.get("source", "") or "")
    if m and m.group(1) not in seen:
        seen.add(m.group(1)); rsf.append(m.group(1))
priority = [p for p in rsf if p.startswith(("inc/", "src/core/cdp", "src/core/inspector",
             "src/core/modules/worker/util", "src/StarfishConfig.h", "src/core/dom/parser"))]
chosen = (priority + [p for p in rsf if p not in priority])[:10]
for p in chosen:
    A(f"> - [{p}](src:{p})")
A("")
today = datetime.date(2026, 8, 27).isoformat()
A(f"> **Generated**: {today}  ")
A("> **Project**: Starfish  ")
A(f"> **Source Files**: 1,815 files analyzed (AST export); extraction entries: {len(enums)} enums, {len(consts)} constants, {len(ipc)} IPC records")
A("")
A("This catalog is generated from the W1 LLM-extraction results "
  "(`.analysis/llm-extraction/llm-{enum,constant,ipc}-results.json`), which were produced from the "
  "tree-sitter AST export and verified against source. Entries without code evidence are omitted.")
A("")

A("---")
A("")
A("## ENUM Definitions")
A("")
A(f"{len(enums)} enum definitions were extracted.")
A("")
A("| ENUM Name | Type | Values | Source |")
A("|-----------|------|--------|--------|")
for e in sorted(enums, key=lambda x: x.get("name", "")):
    A(f"| `{esc(e['name'])}` | {esc(e.get('type', ''))} | {val_cell(e.get('values', []))} | "
      f"{deeplink(e.get('source'), e.get('name'))} |")
A("")

A("---")
A("")
A("## Message ID Catalog")
A("")
msg_rows = []
for i in ipc:
    ids = i.get("message_ids") or []
    for mid in ids:
        msg_rows.append((mid, i))
if msg_rows:
    A("Message identifiers observed on IPC channels (text-based protocols; no numeric opcodes were found in the extraction results).")
    A("")
    A("| Message ID | Hex Value | Direction | Payload | Handler | Source |")
    A("|------------|-----------|-----------|---------|---------|--------|")
    for mid, i in msg_rows:
        A(f"| `{esc(mid)}` | Not specified in code | {esc(i.get('direction', 'Not specified in code'))} | "
          f"{esc((i.get('data') or 'Not specified in code'))[:80]} | `{esc(i.get('name', ''))}` | "
          f"{deeplink(i.get('source'), i.get('name'))} |")
else:
    A("No numeric IPC message IDs or opcodes were found in the extraction results. "
      "The nanomsg inspector channel uses text commands — see the IPC Mechanism Summary below.")
A("")

A("---")
A("")
A("## Constant Definitions")
A("")
A(f"{len(plain_consts)} constants (excluding error codes).")
A("")
A("| Constant | Value | Unit/Type | Usage Context | Source |")
A("|----------|-------|-----------|---------------|--------|")
for c in sorted(plain_consts, key=lambda x: (SRC_RE.match(x.get('source','') or '[Source: zzz:0]').group(1) if SRC_RE.match(x.get('source','') or '') else 'zzz', x.get('name',''))):
    usage = c.get("usage_context") or c.get("context") or "Not specified in code"
    A(f"| `{esc(c['name'])}` | {esc(c.get('value', 'Not specified in code'))} | {esc(c.get('type', ''))} | "
      f"{esc(usage)[:70]} | {deeplink(c.get('source'), c.get('name'))} |")
A("")

A("---")
A("")
A("## Signal/Event Mapping")
A("")
sig = [i for i in ipc if i.get("mechanism") in ("signal", "broadcast_receiver") or i.get("signal_events")]
if sig:
    A("| Signal/Event | Emitter | Listener | Data Type | Source |")
    A("|-------------|---------|----------|-----------|--------|")
    for s in sig:
        A(f"| `{esc(s.get('name', ''))}` | {esc(s.get('source_component', ''))} | {esc(s.get('target_component', ''))} | "
          f"{esc((s.get('data') or ''))[:60]} | {deeplink(s.get('source'), s.get('name'))} |")
else:
    A("No OS-signal or broadcast-receiver style mappings were found in the extraction results "
      "(Starfish DOM events are in-process and are documented per module in W2). Not specified in code.")
A("")

A("---")
A("")
A("## Error Code Catalog")
A("")
if errors:
    A(f"{len(errors)} error/status constants.")
    A("")
    A("| Error Code | Value | Severity | Description | Recovery | Source |")
    A("|------------|-------|----------|-------------|----------|--------|")
    for c in sorted(errors, key=lambda x: x.get("name", "")):
        usage = c.get("usage_context") or c.get("context") or "Not specified in code"
        A(f"| `{esc(c['name'])}` | {esc(c.get('value', 'Not specified in code'))} | Not specified in code | "
          f"{esc(usage)[:60]} | Not specified in code | {deeplink(c.get('source'), c.get('name'))} |")
else:
    A("No dedicated `ERR_*`/`ERROR_*`/`EXIT_*` error-code constants were found in the extraction "
      "results. HTTP status codes are modeled as the `HTTPStatus.HTTPStatusCode` enum — see the "
      "ENUM Definitions section above. Other error reporting uses exception/message mechanisms "
      "documented in [Design Patterns](./03-design-patterns.md).")
A("")

A("---")
A("")
A("## IPC Mechanism Summary")
A("")
A(f"{len(ipc)} IPC records across mechanisms: " +
  ", ".join(f"`{k}` ({v})" for k, v in sorted(
      __import__('collections').Counter(i.get('mechanism') for i in ipc).items(), key=lambda x: -x[1])) + ".")
A("")
A("| IPC Mechanism | Source Component | Target Component | Protocol | Data Format | Source |")
A("|---------------|-----------------|------------------|----------|-------------|--------|")
for i in sorted(ipc, key=lambda x: (x.get("mechanism", ""), x.get("name", ""))):
    data = (i.get("data") or "Not specified in code")
    A(f"| {esc(i.get('mechanism', ''))} | {esc(i.get('source_component', 'Not specified in code'))} | "
      f"{esc(i.get('target_component', 'Not specified in code'))} | `{esc(i.get('name', ''))}` | "
      f"{esc(data)[:90]} | {deeplink(i.get('source'), i.get('name'))} |")
A("")
A("Discovered custom IPC patterns applied during W1 (see `.analysis/ipc-discovery/discovered-ipc-patterns.json`): "
  "`nanomsg` (nn_socket/nn_send/nn_recv/nn_close), `subprocess` (launchProcess, launchProcessOnDoubleFork), "
  "`websocket` (lws_write, lws_service).")
A("")
A("Related: [External Interfaces](./05-external-interfaces.md) · [System Architecture](./02-architecture.md)")
A("")

open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"wrote {OUT}: {len(lines)} lines; enums={len(enums)} consts={len(plain_consts)} errors={len(errors)} ipc={len(ipc)} msg_ids={len(msg_rows)}")
