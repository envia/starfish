# 08 — Security and Quality

> **Relevant source files**
> - [`src/binding/ScriptBindingSecurity.h`](src:src/binding/ScriptBindingSecurity.h)
> - [`src/binding/WindowProxy.h`](src:src/binding/WindowProxy.h)
> - [`src/platform/network/http/HTTPTransaction.h`](src:src/platform/network/http/HTTPTransaction.h)
> - [`AGENTS.md`](AGENTS.md)

## Security

### Same-Origin Policy

`ScriptBindingSecurity` [`src/binding/ScriptBindingSecurity.h`](src:src/binding/ScriptBindingSecurity.h) enforces same-origin policy for JavaScript access to DOM objects.

`WindowProxy` [`src/binding/WindowProxy.h`](src:src/binding/WindowProxy.h) implements the security boundary for cross-origin window access per the HTML spec.

### CORS

CORS (Cross-Origin Resource Sharing) is supported in the HTTP layer. The `HTTPTransaction` [`src/platform/network/http/HTTPTransaction.h`](src:src/platform/network/http/HTTPTransaction.h) handles HTTP requests with CORS headers.

### Content Security Policy

CSP is listed as a supported feature in [`docs/Spec.md`](docs:Spec.md#L20).

### Cookie Scoping

`CookieManagerDelegate` [`src/public/contract/CookieManagerDelegate.h`](src:src/public/contract/CookieManagerDelegate.h) defines the cookie management contract interface.

### TLS

TLS certificate verification is handled by libcurl in the network layer. `STARFISH_ENABLE_HTTPCACHE` gates HTTP cache features.

### Security Review Rules (from AGENTS.md)

Per `AGENTS.md`, the review bot enforces:
- Web content, network data, files, and inputs crossing script/native or process boundaries are treated as attacker-controlled
- Memory corruption, code/command injection, path traversal, and unauthorized data access paths are flagged
- Same-origin checks, CORS, CSP, cookie/storage scoping, permissions, and TLS verification are preserved
- Explicit developer/embedder opt-outs are acceptable only when opt-in and not web-content-enabled

## Quality

### Coding Standards

Defined in [`docs/Coding_Style_Guide.md`](docs/Coding_Style_Guide.md) with emphases in `AGENTS.md`:
- `Optional<T>` for nullable values (not raw pointers with nullptr)
- `GCVector`/`GCTightVector` for GC-managed pointer containers
- Plain pointer parameters are expected valid (GC-based object graph)
- Assert only invariants the type system can't express
- Fix root causes, don't paper over symptoms

### Lint

- `check_tidy.py` — C++ style check (CI gate)
- `check_contract_abi.py` — contract ABI stability check (CI gate)

### Test Coverage

Per `AGENTS.md`, behavior changes must land with test coverage:
- WPT tests activated in `.res` lists when WPT covers the behavior
- Internal tests (using `console.assert` and `testEnd()`) when WPT doesn't cover
- Unit tests for public embedding API via `Starfish unit-test`

### Spec Compliance

The relevant WHATWG/W3C/ECMA-262 spec is the source of truth for behavior [`AGENTS.md`](AGENTS.md). Interface shape comes from `.idl` files which mirror the specs.

### Memory Efficiency

Low runtime memory usage is the core constraint [`AGENTS.md`](AGENTS.md). The review bot actively proposes concrete memory reduction strategies. Memory savings must not degrade rendering performance on hot paths (layout, paint, style resolution, event handling).
