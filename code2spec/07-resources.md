# 07 — Resources

> **Relevant source files**
> - [`README.md`](README.md)
> - [`docs/Spec.md`](docs:Spec.md)
> - [`docs/wpt.md`](docs:wpt.md)
> - [`docs/Coding_Style_Guide.md`](docs:Coding_Style_Guide.md)
> - [`AGENTS.md`](AGENTS.md)

## Documentation

| Document | Purpose |
|---|---|
| `README.md` | Build, cross-compile, per-platform steps, testing setup |
| `docs/Coding_Style_Guide.md` | C++ style (headers, formatting, classes, nullability, GC) |
| `docs/wpt.md` | WPT structure, tooling, `.res` list workflow |
| `docs/Spec.md` | Supported web surface (HTML tags, DOM interfaces, CSS properties, build flags) |
| `AGENTS.md` | Norms and pointers for coding agents and review bot |

## Test Infrastructure

### Web Platform Tests (WPT)

WPT is the proof of spec compliance [`AGENTS.md`](AGENTS.md). Test lists are curated in `.res` files.

Key WPT scripts:
- `tool/wpt/scripts/wpt_runner.py` — test runner
- `tool/wpt/scripts/wpt_server.py` — WPT server management
- `tool/wpt/scripts/wpt_annotate.py` — test annotation
- `tool/wpt/scripts/wpt_manifest_lists.py` — list rewriting
- `tool/wpt/scripts/wpt_status.py` — status dashboard

### Internal Tests

- `src/shell/test/` — C++ unit tests (APIRecorder, CookieManager, LWE, Settings, WebContainer, WebView)
- `tool/runner/test_runner.py` — main test runner
- `tool/drivers/` — test driver framework

### Lint

- `tool/lint/check_tidy.py` — C++ style check (same as CI)
- `tool/lint/check_contract_abi.py` — contract ABI check

## Third-Party Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Escargot | submodule | JavaScript engine |
| BDWGC | system | Garbage collection |
| libcurl | system | HTTP networking |
| Cairo | system | 2D graphics |
| OpenGL/EGL | system | GPU rendering |
| HarfBuzz | system | Text shaping |
| ICU | system | Internationalization |
| libpng | system | PNG decoding |
| robin_map | vendored | Hash map (`third_party/robin_map/`) |
| nanomsg | optional | Messaging |
| libtuv | optional | libUV for Tizen |

## Source Code Statistics

| Metric | Value |
|---|---|
| Total files (AST scope) | 330 |
| AST nodes | 7,004 |
| AST edges | 31,096 |
| Functions | 5,630 |
| Classes | 373 |
| Constants | 604 |
| Enums | 48 |
| Entry points | 63 |
| Dead code functions | 3,567 |
| Logical modules | 19 |
