# Starfish Documentation Index

> Generated: 2026-06-01 | Project Type: Embedded C++ Web Engine

## Project Overview

- **Type:** Monolith (single cohesive codebase)
- **Primary Language:** C++
- **Architecture:** Layered Component Architecture
- **Target Platforms:** Ubuntu, Tizen, Windows, Android

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Build System** | CMake + Ninja |
| **Graphics Backend** | EFL + Cairo GL |
| **JavaScript Engine** | Escargot |
| **Web Standards** | HTML5, CSS3, DOM Level 3+ |

## Generated Documentation

### Core Documentation
- [Project Overview](./project-overview.md) - Executive summary, technology stack, and getting started
- [Architecture](./architecture.md) - System architecture and component design
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure and key files
- [Development Guide](./development-guide.md) - Build, test, and development instructions

## Existing Documentation

### Specifications
- [Specification (Spec.md)](./Spec.md) - Complete API specification (HTML, DOM, CSS, Events, HTTP)
- [Coding Style Guide](./Coding_Style_Guide.md) - C++ coding conventions

### Feature Documentation
- [PWA Design](./PWA.md) - Progressive Web App / Service Worker design
- [RPi3 Guide](./RPi3_Guide.md) - Raspberry Pi 3 specific guide

### Developer Guides
- [Debug Utilities](./guide/debug_utilities.md) - Debugging and tracing tools

### Resources
- [Class Diagrams](./resources/) - PWA class diagrams

## Getting Started

### Quick Build (Linux)

```bash
# Prerequisites
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev libgif-dev \
    cmake autoconf automake libtool ninja libwebp-dev libefl-all-dev
pip install Jinja2

# Clone and build
git clone <repository-url>
cd starfish
git submodule init && git submodule update

cmake -Bout/efl/release -DMODE=release -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
ninja -C out/efl/release starfish.executable

# Run
./out/efl/release/bin/lightweight-web-engine 'path/to/file.html'
```

### Running Tests

```bash
./tool/test_runner.py              # All tests
./tool/test_runner.py wpt_all      # Web Platform Tests
./tool/test_runner.py dom_conformance  # DOM tests
```

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/core/` | Core web engine (DOM, layout, style, events) |
| `src/platform/` | Platform abstraction (canvas, network, multimedia) |
| `src/shell/` | Shell implementations (EFL, GLFW, headless) |
| `inc/` | Public API headers |
| `third_party/` | Third-party dependencies |
| `build/` | Build configuration |
| `tool/` | Development tools |
| `test/` | Test suites |

## Build Flags

| Feature | Flag | Default |
|---------|------|---------|
| Canvas 2D | `STARFISH_ENABLE_CANVAS` | ON |
| WebGL | `WEBGL=1` | ON |
| WebAudio | `STARFISH_ENABLE_WEBAUDIO` | ON (x64) |
| WebSocket | `STARFISH_ENABLE_WEBSOCKET` | ON (x64) |
| WebRTC | `WEBRTC=1` | OFF |
| Workers | `WORKER=1` | OFF |
| Service Worker | `SERVICE_WORKER=1` | OFF |
| IndexedDB | `IDB=1` | OFF |
| Debugger | `ENABLE_DEBUGGER=1` | OFF |

## Third-Party Libraries

| Library | Purpose |
|---------|---------|
| Escargot | JavaScript engine |
| OpenSSL | TLS/SSL cryptography |
| libcurl | HTTP client |
| Cairo | 2D graphics |
| libpng, libjpeg-turbo, libwebp | Image decoding |
| libtuv | Event loop |
| nanomsg | Messaging |

## Additional Resources

- [Web Platform Tests](https://github.com/w3c/web-platform-tests)
- [Escargot JavaScript Engine](https://github.com/Samsung/escargot)
- [EFL Documentation](https://www.enlightenment.org/)
- [Escargot VSCode Extension](https://github.com/Samsung/escargot-vscode-extension) - JS Debugging

## Governance

All decisions are made by consensus. See [Samsung Inner Source Governance](https://github.sec.samsung.net/InnerSource/SamsungInnerSourceProgram/blob/master/GettingStarted/Governance.md) for details.
