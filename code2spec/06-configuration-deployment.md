# 06 — Configuration and Deployment

> **Relevant source files**
> - [`README.md`](README.md)
> - [`docs/Spec.md`](docs:Spec.md)
> - [`src/StarfishConfig.h`](src:src/StarfishConfig.h)
> - [`src/shell/ShellConfig.h`](src/shell/ShellConfig.h)

## Build System

Starfish uses CMake with Ninja as the build generator [`README.md`](README.md#L51).

### Build Commands

```sh
cmake -Bout/release -DCMAKE_BUILD_TYPE=Release -DBACKEND=glib_cairo_gl -DSHELL=x11 -DTARGETNAME=Starfish -G Ninja
ninja -C out/release starfish.executable
```

### Build Targets

| Target | Output |
|---|---|
| `starfish.executable` | Standalone executable |
| `starfish.shared_library` | `liblightweight-web-engine.so` |
| `starfish.static_library` | `liblightweight-web-engine.a` |

### Build Options

| Option | Default | Description |
|---|---|---|
| `CMAKE_SYSTEM_NAME` | native | Linux, Tizen, Windows |
| `CMAKE_BUILD_TYPE` | Release | Debug or Release |
| `BACKEND` | glib_cairo_gl | glib_cairo_gl or uv_cairo_gl |
| `CMAKE_SYSTEM_PROCESSOR` | x86_64 | x86_64, aarch64, arm, x86 |
| `LTO` | 0 | Link-time optimization |
| `ENABLE_DEBUGGER` | 0 | Enable debugger |
| `TARGETNAME` | lightweight-web-engine | Output name |
| `COVERAGE` | 0 | gcov coverage |
| `WEBGL` | off | WebGL support |
| `WORKER` | off | Web Workers |
| `SHARED_WORKER` | off | Shared Workers |
| `SERVICE_WORKER` | off | Service Workers |
| `IDB` | off | IndexedDB |
| `WEBRTC` | off | WebRTC |
| `ENABLE_WASM` | off | WebAssembly |

### IDL Binding Generation

JS bindings are generated from `src/**/*.idl` at cmake configure time. After any `.idl` change, re-run cmake (incremental `ninja` does not regenerate bindings) [`README.md`](README.md#L55).

## Supported Platforms

| Platform | Status |
|---|---|
| Ubuntu 24.04 / 22.04 (x64) | Supported |
| Ubuntu (aarch64 / armhf / x86 cross) | Supported |
| Tizen | Supported |
| Windows | Supported |
| Android | Supported |

## Renderer Types

Defined in [`Starfish.h`](src:src/Starfish.h#L43):
- `kOpenGL` — GPU-accelerated rendering
- `kSoftware` — CPU rendering (Cairo)
- `kHeadless` — no display output

## Deployment

### Shared Library

The engine is deployed as `liblightweight-web-engine.so` (or `.a`). Embedders include `inc/LWEWebView.h` and link against the library.

### Shell

The `MiniBrowser` shell (`src/shell/MiniBrowser.cpp`) provides a standalone browser executable for testing and development.

### Testing

All test runs must be wrapped in `xvfb-run -s '-screen 0 1920x1080x24' -a` [`AGENTS.md`](AGENTS.md). Test suites run 8-way in parallel.

| Touched | Run |
|---|---|
| Any C++ | `./tool/lint/check_tidy.py` |
| Contract ABI | `./tool/lint/check_contract_abi.py` |
| DOM APIs | `wpt_serve_testharness_dom internal_test` |
| CSS/selectors | `wpt_serve_testharness_css` |
| HTML parsing | `wpt_serve_testharness_html` |
| Layout/paint | `wpt_serve_reftest` |
