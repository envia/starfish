# Starfish Project Overview

**Generated:** June 1, 2026

---

## Executive Summary

Starfish is a lightweight Web browser engine designed for TV, mobile, headless, and wearable devices. It provides a full-featured web rendering engine optimized for embedded and resource-constrained environments.

---

## Project Classification

| Attribute | Value |
|-----------|-------|
| **Project Name** | Starfish (Lightweight Web Engine) |
| **Type** | Embedded Web Browser Engine |
| **Repository Type** | Monolith |
| **Primary Language** | C++ |
| **Build System** | CMake + Ninja |
| **License** | Multiple (Apache-2.0, MIT, BSD, LGPL, etc.) |

---

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Ubuntu Linux | ✅ Primary | 18.04, 16.04, 14.04 |
| Tizen | ✅ Supported | TV, Mobile, Wearable |
| Windows | ✅ Supported | x86 build via Visual Studio |
| Android | ✅ Supported | NDK r16b |

---

## Technology Stack

### Core Technologies

| Category | Technology | Version/Notes |
|----------|------------|---------------|
| **Language** | C++ | C++11 features encouraged |
| **Build System** | CMake | 2.8.12+ |
| **Build Generator** | Ninja | Primary |
| **JavaScript Engine** | Escargot | Samsung's lightweight JS engine |
| **Graphics Backend** | Cairo/OpenGL | efl_cairo_gl (default) |
| **UI Shell** | EFL | Enlightenment Foundation Libraries |

### Third-Party Dependencies

| Library | Purpose |
|---------|---------|
| Escargot | JavaScript engine |
| OpenSSL | Cryptography/TLS |
| libwebp | WebP image format |
| libpng | PNG image format |
| libjpeg-turbo | JPEG image format |
| Cairo | 2D graphics |
| ICU | Internationalization |
| libcurl | HTTP client |
| nanomsg | Messaging |
| WebRTC | Real-time communication (optional) |
| googletest | Testing framework |

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Shell Layer                             │
│  (EFL, GLFW, X11, Headless)                                 │
├─────────────────────────────────────────────────────────────┤
│                      Browser Layer                           │
│  (History, Navigation)                                       │
├─────────────────────────────────────────────────────────────┤
│                      Core Layer                              │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐        │
│  │   DOM   │  Layout │  Style  │  Events │ Storage │        │
│  ├─────────┼─────────┼─────────┼─────────┼─────────┤        │
│  │  Fetch  │  FileAPI│ Animation│  CSP   │  Page   │        │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Platform Layer                            │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┐        │
│  │ Canvas  │ Network │  File   │  Event  │ Media   │        │
│  ├─────────┼─────────┼─────────┼─────────┼─────────┤        │
│  │  TTS    │ Process │ Loader  │ MessageLoop│      │        │
│  └─────────┴─────────┴─────────┴─────────┴─────────┘        │
├─────────────────────────────────────────────────────────────┤
│                    Binding Layer                             │
│  (JavaScript bindings via IDL files)                        │
├─────────────────────────────────────────────────────────────┤
│                    JavaScript Engine                         │
│  (Escargot)                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/` | Main source code |
| `src/core/` | Core engine (DOM, layout, style, events) |
| `src/platform/` | Platform abstraction layer |
| `src/browser/` | Browser functionality |
| `src/launcher/` | Application launcher |
| `src/shell/` | UI shell implementations |
| `src/binding/` | JavaScript bindings |
| `inc/` | Public API headers |
| `third_party/` | Third-party libraries |
| `build/` | Build configuration |
| `test/` | Test suites |
| `tool/` | Development tools |
| `docs/` | Documentation |

---

## Key Features

### Web Standards Support

- **HTML5** - Full HTML5 document support
- **CSS** - Extensive CSS property support (see Spec.md)
- **DOM** - Complete DOM Level 2/3 support
- **Events** - UI Events, Custom Events
- **Canvas 2D** - Full 2D canvas API
- **WebGL** - Optional (WEBGL=1 flag)
- **WebAudio** - Audio API support
- **WebSocket** - Real-time communication
- **WebRTC** - Optional (WEBRTC=1 flag)

### Build Options

| Flag | Default | Description |
|------|---------|-------------|
| `HOST` | linux | Target platform (linux, tizen, windows) |
| `MODE` | release | Build mode (debug, release) |
| `ARCH` | x64 | Architecture (x64, arm) |
| `BACKEND` | efl_cairo_gl | Graphics backend |
| `WEBGL` | 0 | Enable WebGL |
| `WEBRTC` | 0 | Enable WebRTC |
| `WORKER` | 0 | Enable Web Workers |
| `SERVICE_WORKER` | 0 | Enable Service Workers |
| `IDB` | 0 | Enable IndexedDB |
| `ENABLE_DEBUGGER` | 0 | Enable JavaScript debugger |

---

## Getting Started

### Prerequisites (Ubuntu)

```bash
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev \
    libgif-dev cmake autoconf automake libtool ninja \
    libwebp-dev libefl-all-dev

pip install Jinja2
```

### Quick Build

```bash
git clone <repository-url>
cd starfish
git submodule init
git submodule update

cmake -Bout/efl/release -DMODE=release -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -DTARGETNAME=Starfish -G Ninja
ninja -C out/efl/release starfish.executable
```

### Running

```bash
./out/release/bin/lightweight-web-engine 'path/to/file.html'
```

---

## Documentation Index

### Generated Documentation

- [Source Tree Analysis](./source-tree-analysis.md)
- [Development Guide](./development-guide.md)

### Existing Documentation

- [README.md](../README.md) - Project overview and build instructions
- [Specification](./Spec.md) - Complete LWE feature specification
- [Coding Style Guide](./Coding_Style_Guide.md) - C++ coding conventions
- [PWA Design](./PWA.md) - Progressive Web App architecture
- [RPi3 Guide](./RPi3_Guide.md) - Raspberry Pi 3 guide
- [Debug Utilities](./guide/debug_utilities.md) - Debug utilities

---

## Testing

### Test Categories

- **DOM Conformance Tests** - `./tool/test_runner.py dom_conformance`
- **Web Platform Tests** - `./tool/test_runner.py wpt_all`
- **Vendor Tests** - `./tool/test_runner.py vendor_test`
- **Bidi Tests** - `./tool/test_runner.py bidi_test`
- **Internal Tests** - `./tool/test_runner.py internal_test`

### Pixel Tests

```bash
ELM_ENGINE="shot:file=capture.png" ./run.sh file.html \
    --pixel-test --width=800 --height=600
```

---

## CI/CD

- CI Infrastructure: http://10.113.138.181/overview/444
- GitLab CI: `.gitlab-ci.yml`

---

## Governance

All decisions are made by consensus, respecting the principles and rules of the community. See [Samsung Inner Source Governance](https://github.sec.samsung.net/InnerSource/SamsungInnerSourceProgram/blob/master/GettingStarted/Governance.md) for details.
