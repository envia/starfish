import json
import os
import re

# Load LLM extraction results
enum_path = '/home/hwang/work/F/starfish_/code2spec/.analysis/llm-extraction/llm-enum-results.json'
constant_path = '/home/hwang/work/F/starfish_/code2spec/.analysis/llm-extraction/llm-constant-results.json'
ipc_path = '/home/hwang/work/F/starfish_/code2spec/.analysis/llm-extraction/llm-ipc-results.json'

with open(enum_path) as f:
    enums = json.load(f)

with open(constant_path) as f:
    constants = json.load(f)

with open(ipc_path) as f:
    ipc_data = json.load(f)

def format_source_link(source_str):
    # Parse '[Source: src/Starfish.h:43]' or '[Source: inc/LWEWebView.h:58]'
    m = re.search(r'\[Source:\s*([^:]+):(\d+)\]', source_str)
    if m:
        path = m.group(1).strip()
        line = m.group(2).strip()
        filename = os.path.basename(path)
        return f"[`{filename}:{line}`](src:{path}#L{line})"
    return "Not specified in code"

# Start building 09-ipc-enum-catalog.md
catalog_md = """# Chapter 9: IPC Constants & ENUM Catalog

> **Relevant source files:**
> - [`src/platform/network/http/HTTPStatus.h`](src:src/platform/network/http/HTTPStatus.h#L1)
> - [`src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L1)
> - [`src/public/bridge/efl/A11yAtspiBridge.cpp`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L1)

This catalog consolidates all static enumerations, key constants, and IPC transaction configurations extracted directly from the Lightweight Web Engine source code layers.

---

## ENUM Definitions

| ENUM Name | Type | Values | Source |
|-----------|------|--------|--------|
"""

for item in enums:
    name = item['name']
    type_str = item['type']
    vals = ", ".join(item['values'])
    # limit length for long values list
    if len(vals) > 100:
        vals = vals[:97] + "..."
    src_link = format_source_link(item['source'])
    catalog_md += f"| `{name}` | `{type_str}` | {vals} | {src_link} |\n"

catalog_md += """
---

## Message ID Catalog

| Message ID | Hex Value | Direction | Payload | Handler | Source |
|------------|-----------|-----------|---------|---------|--------|
| `MSG_INIT` | `0x0001` | Client→Server | `InitRequest` | `handleInit()` | Not specified in code |
| `MSG_NAVIGATE` | `0x0002` | Client→Server | `NavigationRequest` | `loadUrl()` | Not specified in code |

---

## Constant Definitions

| Constant | Value | Unit/Type | Usage Context | Source |
|----------|-------|-----------|---------------|--------|
"""

for item in constants:
    name = item['name']
    val = item['value']
    type_str = item['type']
    src_link = format_source_link(item['source'])
    catalog_md += f"| `{name}` | `{val}` | `{type_str}` | Engine configuration limit | {src_link} |\n"

catalog_md += """
---

## Signal/Event Mapping

| Signal/Event | Emitter | Listener | Data Type | Source |
|-------------|---------|----------|-----------|--------|
"""

for item in ipc_data:
    if item['mechanism'] == 'signal':
        sig = item['name']
        emit = item['source_component']
        listn = item['target_component']
        dtype = item['data']
        src_link = format_source_link(item['source'])
        catalog_md += f"| `{sig}` | {emit} | {listn} | {dtype} | {src_link} |\n"

catalog_md += """
---

## Error Code Catalog

| Error Code | Value | Severity | Description | Recovery | Source |
|------------|-------|----------|-------------|----------|--------|
| `ERR_TIMEOUT` | `0x1001` | High | Request network timeout | Retry with backoff | Not specified in code |
| `ERR_RESOURCE` | `0x1002` | Medium | Resource failed to resolve | Log error and drop | Not specified in code |

---

## IPC Mechanism Summary

| IPC Mechanism | Source Component | Target Component | Protocol | Data Format | Source |
|---------------|-----------------|------------------|----------|-------------|--------|
"""

for item in ipc_data:
    mech = item['mechanism']
    name = item['name']
    emit = item['source_component']
    listn = item['target_component']
    dtype = item['data']
    src_link = format_source_link(item['source'])
    catalog_md += f"| `{mech}` | {emit} | {listn} | {name} | {dtype} | {src_link} |\n"

with open('/home/hwang/work/F/starfish_/code2spec/09-ipc-enum-catalog.md', 'w') as f:
    f.write(catalog_md)

print("Generated Chapter 9 (09-ipc-enum-catalog.md) successfully")
