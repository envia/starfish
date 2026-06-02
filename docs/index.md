# Starfish Documentation Index

**Lightweight Web Browser Engine for TV, Mobile, Headless, and Wearable Devices**

---

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Type** | Embedded Web Browser Engine |
| **Primary Language** | C++ (C++11) |
| **Architecture** | Layered with Platform Abstraction |
| **License** | LGPL-2.1+ |
| **Copyright** | Samsung Electronics Co., Ltd |

---

## Quick Reference

| Category | Technology |
|----------|------------|
| **Build System** | CMake + Ninja |
| **JavaScript Engine** | Escargot |
| **Graphics Backend** | Cairo |
| **Event Loop** | GLib / libuv |
| **Network** | libcurl |
| **SSL/TLS** | OpenSSL |
| **Unicode** | ICU |
| **Garbage Collection** | Boehm GC |

---

## Generated Documentation

### Core Documentation

- **[Project Overview](./project-overview.md)** - Executive summary, features, and quick start guide
- **[Architecture](./architecture.md)** - Detailed architecture documentation including component design, data flow, and extension points
- **[Source Tree Analysis](./source-tree-analysis.md)** - Directory structure and organization
- **[Development Guide](./development-guide.md)** - Building, testing, and development instructions

### API & Specifications

- **[API Specification (Spec.md)](./Spec.md)** - Complete web API surface documentation (HTML, DOM, CSS, Events)
- **[PWA Design (PWA.md)](./PWA.md)** - Progressive Web App implementation (Service Worker, Shared Worker)

### Guides

- **[Coding Style Guide](./Coding_Style_Guide.md)** - C++ coding conventions
- **[RPi3 Guide](./RPi3_Guide.md)** - Raspberry Pi 3 Tizen 4.0 deployment

---

## Getting Started

### Prerequisites (Ubuntu 20.04)

```bash
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
  libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev libgif-dev \
  cmake autoconf automake libtool ninja libwebp-dev libefl-all-dev

pip install Jinja2
```

### Quick Build

```bash
git clone <repository-url>
cd starfish
git submodule update --init --recursive

cmake -Bout/release -DMODE=release -DHOST=linux -DARCH=x64 \
  -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
ninja -C out/release starfish.executable
```

### Run

```bash
./out/release/bin/lightweight-web-engine 'path/to/file.html'
```

---

## Target Platforms

| Platform | Status | Profiles |
|----------|--------|-----------|
| Linux (Ubuntu) | ✅ Primary | Development & Testing |
| Tizen | ✅ Supported | TV, Mobile, Wearable |
| Windows | ✅ Supported | UWP, Win32 |
| Android | ✅ Supported | NDK-based |

---

## Key Features

### Web Platform
- HTML5 document parsing and rendering
- CSS styling (Flexbox, Transforms, Variables)
- DOM Level 3 + HTML5 Living Standard APIs
- Canvas 2D (Cairo backend)
- WebGL 1.0/2.0 (optional)
- WebAudio API
- WebSocket

### JavaScript
- Escargot engine (ES6+)
- Optional debugger (VSCode extension)
- Optional WebAssembly support

### PWA Features
- Service Worker
- Shared Worker
- Web Workers
- IndexedDB (optional)
- HTTP Cache

### Multimedia
- `<video>` / `<audio>` elements
- MP4, WebM codec support
- WebRTC (optional)

---

## Build Options

| Option | Default | Description |
|--------|---------|-------------|
| `WEBGL` | 0 | WebGL support |
| `WEBRTC` | 0 | WebRTC support |
| `WORKER` | 0 | Web Worker support |
| `SERVICE_WORKER` | 0 | Service Worker support |
| `IDB` | 0 | IndexedDB support |
| `ENABLE_DEBUGGER` | 0 | JS debugger support |
| `ENABLE_WASM` | 0 | WebAssembly support |

---

## Directory Structure

```
starfish/
├── binding/          # JavaScript binding layer
├── core/             # Core web platform implementation
├── platform/         # Platform abstraction layer
├── shell/            # Platform shells (EFL, GLFW, etc.)
├── public/           # Public API implementation
├── inc/              # Public API headers
├── build/            # CMake configuration
├── third_party/      # Third-party dependencies
├── test/             # Test suites
├── tool/             # Development tools
└── docs/             # Documentation
```

---

## Testing

```bash
# Run all tests
./tool/test_runner.py

# Specific test suites
./tool/test_runner.py dom_conformance
./tool/test_runner.py wpt_all
./tool/test_runner.py vendor_test
```

---

## Support Platforms

| Profile | Description |
|---------|-------------|
| `tv` | Tizen TV profile |
| `mobile` | Tizen Mobile profile |
| `wearable` | Tizen Wearable profile |
| `headless` | Headless mode (no UI) |

---

## Third-Party Libraries

| Library | Purpose |
|---------|---------|
| Escargot | JavaScript engine |
| Cairo | 2D graphics |
| OpenSSL | TLS/SSL |
| libcurl | HTTP client |
| ICU | Unicode support |
| Boehm GC | Garbage collection |
| libjpeg-turbo | JPEG decoding |
| libpng | PNG decoding |
| libwebp | WebP decoding |
| nanomsg | IPC for workers |
| libwebsockets | WebSocket protocol |

---

## License

This library is free software; you can redistribute it and/or modify it under the terms of the **GNU Lesser General Public License** as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.

See [LICENSE.LGPL-2.1+](../LICENSE.LGPL-2.1+) for details.

---

*Documentation generated on 2026-06-01*
