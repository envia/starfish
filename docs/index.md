# Starfish Documentation Index

**Generated:** June 1, 2026

---

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Type** | Embedded Web Browser Engine |
| **Primary Language** | C++ |
| **Build System** | CMake + Ninja |
| **Architecture** | Layered (Shell → Browser → Core → Platform) |

---

## Quick Reference

- **Tech Stack:** C++ with Escargot JS engine, Cairo/OpenGL graphics
- **Entry Point:** `src/Starfish.cpp`
- **Build Command:** `ninja -C out/efl/release starfish.executable`
- **Test Runner:** `./tool/test_runner.py`

---

## Generated Documentation

- [Project Overview](./project-overview.md) - Executive summary, tech stack, architecture
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure and key files
- [Development Guide](./development-guide.md) - Build, test, and development instructions

---

## Existing Documentation

### Core Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview and build instructions |
| [Specification](./Spec.md) | Complete LWE feature specification (HTML, DOM, CSS, Events, APIs) |
| [Coding Style Guide](./Coding_Style_Guide.md) | C++ coding conventions (Google style based) |

### Platform Guides

| Document | Description |
|----------|-------------|
| [PWA Design](./PWA.md) | Progressive Web App architecture |
| [RPi3 Guide](./RPi3_Guide.md) | Raspberry Pi 3 guide |
| [Debug Utilities](./guide/debug_utilities.md) | Debug utilities |

### API Documentation

| Document | Description |
|----------|-------------|
| [Web API Documentation](./webpages/webapi/) | Generated Web API docs |

---

## Getting Started

### Quick Build (Linux)

```bash
# Install dependencies
sudo apt-get install cmake ninja-build libefl-all-dev libcairo2-dev \
    libicu-dev libcurl4-openssl-dev libssl-dev

# Clone and build
git clone <repository-url>
cd starfish
git submodule init && git submodule update

cmake -Bout/release -DMODE=release -DHOST=linux -DARCH=x64 -G Ninja
ninja -C out/release starfish.executable

# Run
./out/release/bin/lightweight-web-engine 'path/to/file.html'
```

### Key Build Options

| Flag | Description |
|------|-------------|
| `-DWEBGL=1` | Enable WebGL |
| `-DWEBRTC=1` | Enable WebRTC |
| `-DWORKER=1` | Enable Web Workers |
| `-DENABLE_DEBUGGER=1` | Enable JS debugger |

---

## Architecture Layers

```
┌─────────────────────────────────────┐
│           Shell Layer               │  EFL, GLFW, X11, Headless
├─────────────────────────────────────┤
│          Browser Layer              │  History, Navigation
├─────────────────────────────────────┤
│            Core Layer               │  DOM, Layout, Style, Events
├─────────────────────────────────────┤
│          Platform Layer             │  Canvas, Network, File, Media
├─────────────────────────────────────┤
│          Binding Layer             │  JavaScript bindings (IDL)
├─────────────────────────────────────┤
│        JavaScript Engine            │  Escargot
└─────────────────────────────────────┘
```

---

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/core/` | Core engine (DOM, layout, style, events) |
| `src/platform/` | Platform abstraction layer |
| `src/binding/` | JavaScript bindings |
| `inc/` | Public API headers (`LWEWebView.h`) |
| `third_party/` | Bundled dependencies |
| `test/` | Test suites |
| `tool/` | Development tools |

---

## Testing

```bash
# Run all tests
./tool/test_runner.py

# Specific tests
./tool/test_runner.py dom_conformance
./tool/test_runner.py wpt_all
./tool/test_runner.py vendor_test
```

---

## For AI-Assisted Development

When working with AI assistants on this project:

1. **Reference this index** as the primary navigation document
2. **Use `docs/Spec.md`** for feature specifications (HTML, DOM, CSS support)
3. **Check `src/**/*.idl`** files for JavaScript interface definitions
4. **Review `src/core/style/Style.h`** for CSS property support
5. **See `src/core/dom/HTMLDocument.cpp`** for HTML element registration

### Key Files for Context

- `CMakeLists.txt` - Build configuration
- `src/Starfish.cpp` - Main entry point
- `inc/LWEWebView.h` - Public API
- `docs/Spec.md` - Feature specification

---

## CI/CD

- **GitLab CI:** `.gitlab-ci.yml`
- **CI Dashboard:** http://10.113.138.181/overview/444

---

## Governance

All decisions are made by consensus. See [Samsung Inner Source Governance](https://github.sec.samsung.net/InnerSource/SamsungInnerSourceProgram/blob/master/GettingStarted/Governance.md).
