# Starfish Documentation Index

**Starfish** is a lightweight web browser engine for TV, mobile, headless, and wearable devices.

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Type** | Embedded Web Browser Engine |
| **Language** | C++ |
| **Build System** | CMake + Ninja |
| **Platforms** | Linux, Tizen, Windows, Android |

## Generated Documentation

- [Project Overview](./project-overview.md) - Introduction and key features
- [Architecture](./architecture.md) - System architecture and components
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure and organization
- [Development Guide](./development-guide.md) - Building, testing, and development

## Existing Documentation

- [Specification (Spec.md)](./Spec.md) - Complete API specification (HTML, DOM, CSS, Events)
- [Coding Style Guide](./Coding_Style_Guide.md) - Code style conventions
- [PWA Support](./PWA.md) - Progressive Web App support
- [RPi3 Guide](./RPi3_Guide.md) - Raspberry Pi 3 specific guide

## Getting Started

### Quick Build (Linux/EFL)

```bash
# Prerequisites (Ubuntu 20.04+)
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev cmake ninja libefl-all-dev

# Clone and build
git clone <repository-url>
cd starfish
git submodule init && git submodule update

cmake -Bout/release -DMODE=release -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
ninja -C out/release starfish.executable

# Run
./out/release/bin/lightweight-web-engine 'file.html'
```

## Key Features

| Feature | Build Flag | Default |
|---------|------------|---------|
| Canvas 2D | `STARFISH_ENABLE_CANVAS` | On |
| WebGL | `WEBGL=1` | Off |
| Multimedia | `STARFISH_ENABLE_MULTIMEDIA` | On |
| WebSocket | `STARFISH_ENABLE_WEBSOCKET` | On |
| WebRTC | `WEBRTC=1` | Off |
| Web Workers | `WORKER=1` | Off |
| Service Workers | `SERVICE_WORKER=1` | Off |
| IndexedDB | `IDB=1` | Off |
| Debugger | `ENABLE_DEBUGGER=1` | Off |

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           Public API Layer              │
│  (LWEWebView, WebContainer, Settings)   │
├─────────────────────────────────────────┤
│           Shell Layer                    │
│  (EFL, GLFW, X11, Headless, Android)    │
├─────────────────────────────────────────┤
│           Core Engine                    │
│  (DOM, Layout, CSS, Events, Canvas)     │
├─────────────────────────────────────────┤
│       JavaScript Binding Layer           │
│  (Escargot integration, IDL bindings)    │
├─────────────────────────────────────────┤
│         Platform Layer                   │
│  (Network, File, Multimedia, TTS)       │
├─────────────────────────────────────────┤
│       Third-Party Libraries              │
│  (Escargot, Cairo, OpenSSL, curl)       │
└─────────────────────────────────────────┘
```

## Testing

```bash
# Run all tests
./tool/test_runner.py

# Specific test suites
./tool/test_runner.py wpt_all        # Web Platform Tests
./tool/test_runner.py dom_conformance # DOM tests
./tool/test_runner.py internal_test   # Internal tests
```

## Public API

The public embedding API is defined in `inc/`:

- **LWE::LWE** - Engine initialization and lifecycle
- **LWE::WebView** - Web view widget
- **LWE::WebContainer** - Low-level rendering container
- **LWE::Settings** - Configuration options
- **LWE::CookieManager** - Cookie management

## Source Directories

| Directory | Purpose |
|-----------|---------|
| `src/core/` | Core web engine (DOM, Layout, CSS) |
| `src/platform/` | Platform abstraction |
| `src/shell/` | Platform UI integration |
| `src/binding/` | JavaScript bindings |
| `src/public/` | Public API implementation |
| `third_party/` | External dependencies |

## License

LGPL-2.1-or-later. See [LICENSE.LGPL-2.1+](../LICENSE.LGPL-2.1+) for details.

---

*Documentation generated on 2026-06-01*
