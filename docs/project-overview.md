# Starfish - Lightweight Web Browser Engine

## Project Overview

**Starfish** is a lightweight web browser engine designed for TV, mobile, headless, and wearable devices. It provides a complete web platform implementation optimized for resource-constrained embedded environments.

| Attribute | Value |
|-----------|-------|
| **Project Type** | Embedded Web Browser Engine |
| **Repository Type** | Monolith |
| **Primary Language** | C++ (C++11) |
| **Build System** | CMake + Ninja |
| **License** | LGPL-2.1+ |
| **Copyright** | Samsung Electronics Co., Ltd |

## Executive Summary

Starfish implements a comprehensive web platform stack including:
- HTML5 document parsing and rendering
- CSS styling and layout engine
- JavaScript execution via Escargot engine
- DOM API implementation
- Canvas 2D rendering (via Cairo)
- Multimedia playback support
- WebGL support
- Progressive Web App (PWA) features (Service Worker, Shared Worker)

The engine is designed to be portable across multiple platforms including Linux, Tizen, Windows, and Android, with configurable backend options for graphics (Cairo), event loops (GLib, libuv), and window systems (EFL, GLFW, X11).

## Target Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Linux (Ubuntu) | ✅ Primary | Development and testing platform |
| Tizen | ✅ Supported | TV, Mobile, Wearable profiles |
| Windows | ✅ Supported | UWP and Win32 builds |
| Android | ✅ Supported | NDK-based build |

## Key Features

### Web Platform Support
- **HTML5**: Full HTML5 document support with extensive tag coverage
- **CSS**: Comprehensive CSS property support including Flexbox, Transforms, Variables
- **DOM**: Complete DOM Level 3 + HTML5 Living Standard APIs
- **Canvas 2D**: Full Canvas 2D Context API via Cairo
- **WebGL**: WebGL 1.0 and 2.0 support (build-time option)
- **WebAudio**: AudioContext and related APIs
- **WebSocket**: Real-time bidirectional communication

### JavaScript Engine
- **Escargot**: Custom JavaScript engine optimized for embedded systems
- ES6+ feature support
- Optional debugger support (VSCode extension available)
- Optional WebAssembly support

### PWA Features
- Service Worker
- Shared Worker
- Web Workers
- IndexedDB (build-time option)
- HTTP Cache

### Multimedia
- `<video>` and `<audio>` element support
- Multiple codec support (MP4, WebM)
- WebRTC support (build-time option)

## Architecture Highlights

```
┌─────────────────────────────────────────────────────────────┐
│                      Public API Layer                        │
│  (LWEWebView, LWEWorker, Delegates, Bridge Interfaces)      │
├─────────────────────────────────────────────────────────────┤
│                      Shell Layer                             │
│  (EFL, GLFW, X11, Headless, Android, Windows)               │
├─────────────────────────────────────────────────────────────┤
│                      Core Engine                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │   DOM    │ │  Style   │ │  Layout  │ │ Animation│        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  Events  │ │  Fetch   │ │ Storage  │ │  Canvas  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
├─────────────────────────────────────────────────────────────┤
│                      Binding Layer                            │
│  (ScriptWrappable, IDL Bindings, Custom Bindings)           │
├─────────────────────────────────────────────────────────────┤
│                      Platform Layer                           │
│  (Network, Canvas, Events, Multimedia, TTS, Loader)         │
├─────────────────────────────────────────────────────────────┤
│                      Third-Party Libraries                    │
│  (Escargot, Cairo, OpenSSL, libuv, ICU, etc.)               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Reference

| Category | Technology |
|----------|------------|
| **Language** | C++11 |
| **Build System** | CMake + Ninja |
| **JavaScript Engine** | Escargot |
| **Graphics Backend** | Cairo |
| **Event Loop** | GLib / libuv |
| **Network** | libcurl |
| **SSL/TLS** | OpenSSL |
| **Unicode** | ICU |
| **Garbage Collection** | Boehm GC |

## Documentation Index

- [Architecture](./architecture.md) - Detailed architecture documentation
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure and organization
- [Development Guide](./development-guide.md) - Building and development instructions
- [API Specification](./Spec.md) - Complete API surface documentation
- [Coding Style Guide](./Coding_Style_Guide.md) - C++ coding conventions
- [PWA Design](./PWA.md) - Progressive Web App implementation details
- [RPi3 Guide](./RPi3_Guide.md) - Raspberry Pi 3 deployment guide

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

## License

This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.

See [LICENSE.LGPL-2.1+](../LICENSE.LGPL-2.1+) for details.
