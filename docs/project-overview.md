# Starfish (Lightweight Web Engine) - Project Overview

**Generated:** 2026-06-01  
**Project Type:** Embedded / Web Browser Engine  
**Repository Type:** Monolith

---

## Executive Summary

Starfish is a lightweight web browser engine designed for TV, mobile, headless, and wearable devices. It provides a full-featured web rendering engine optimized for resource-constrained embedded environments while maintaining broad compatibility with web standards including HTML5, CSS3, DOM, and modern JavaScript APIs.

---

## Quick Reference

| Category | Technology |
|----------|------------|
| **Primary Language** | C++ (C++11 features encouraged) |
| **Build System** | CMake |
| **Target Platforms** | Linux, Tizen, Windows, Android |
| **Architecture** | Component-based embedded browser engine |
| **JavaScript Engine** | Escargot (Samsung) |
| **Graphics Backends** | EFL/Cairo, Cairo-GL, Skia |
| **Rendering** | HTML5, CSS3, DOM Level 3+ |
| **License** | Multiple (Apache-2.0, MIT, BSD, LGPL, BSL-1.0) |

---

## Project Structure

```
starfish/
├── src/                    # Main source code
│   ├── core/               # Core engine components
│   │   ├── animation/      # CSS animations
│   │   ├── dom/            # DOM implementation
│   │   ├── event/          # Event handling
│   │   ├── layout/         # Layout engine
│   │   ├── page/           # Page management
│   │   ├── style/          # CSS style system
│   │   └── storage/        # Storage APIs
│   ├── platform/           # Platform abstraction layer
│   │   ├── canvas/         # Canvas rendering
│   │   ├── multimedia/     # Audio/Video
│   │   ├── network/        # Network stack
│   │   └── tts/            # Text-to-speech
│   ├── browser/            # Browser functionality
│   ├── shell/              # Shell implementations
│   └── public/             # Public API
├── inc/                    # Public headers
├── third_party/            # Third-party dependencies
├── build/                  # Build configuration
├── test/                   # Test suites
├── docs/                   # Documentation
└── tool/                   # Development tools
```

---

## Key Features

### Web Standards Support
- **HTML5**: Full HTML5 document support with extensive tag support
- **CSS3**: Comprehensive CSS property support including Flexbox, Transforms, Animations
- **DOM Level 3+**: Extensive DOM API implementation
- **Canvas 2D**: Full Canvas 2D rendering context
- **WebGL**: Optional WebGL support (build flag)
- **WebAudio**: Audio synthesis and processing
- **WebSocket**: Real-time bidirectional communication

### Optional Features (Build Flags)
| Feature | CMake Flag | Default |
|---------|------------|---------|
| Canvas | `STARFISH_ENABLE_CANVAS` | ON |
| WebGL | `WEBGL=1` | ON |
| WebAudio | `STARFISH_ENABLE_WEBAUDIO` | ON (x64) |
| WebSocket | `STARFISH_ENABLE_WEBSOCKET` | ON (x64) |
| WebRTC | `WEBRTC=1` | OFF |
| Workers | `WORKER=1` | OFF |
| Service Worker | `SERVICE_WORKER=1` | OFF |
| IndexedDB | `IDB=1` | OFF |
| Debugger | `ENABLE_DEBUGGER=1` | OFF |

### Platform Support
- **Linux**: Ubuntu 18.04+ (primary development)
- **Tizen**: TV, Mobile, Wearable profiles
- **Windows**: Visual Studio 2019+
- **Android**: NDK r16b

---

## Architecture Pattern

Starfish follows a **layered component architecture**:

1. **Platform Abstraction Layer** (`src/platform/`) - OS-agnostic interfaces
2. **Core Engine** (`src/core/`) - DOM, layout, style, events
3. **Browser Layer** (`src/browser/`) - Browser-specific functionality
4. **Shell Layer** (`src/shell/`) - Application shell implementations

---

## Entry Points

| Entry Point | Description |
|-------------|-------------|
| `Starfish.cpp` | Main engine initialization |
| `src/shell/` | Shell executables (EFL, GLFW, X11) |
| `src/launcher/` | Application launcher |

---

## Third-Party Dependencies

| Library | Purpose |
|---------|---------|
| Escargot | JavaScript engine |
| Cairo | 2D graphics |
| libpng, libjpeg-turbo, libwebp | Image decoding |
| OpenSSL | TLS/SSL |
| libwebsockets | WebSocket |
| nanomsg | IPC |
| WebRTC | Real-time communication |

---

## Getting Started

### Prerequisites (Ubuntu)
```bash
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev \
    libgif-dev cmake autoconf automake libtool ninja \
    libwebp-dev libefl-all-dev python-pip
pip install Jinja2
```

### Build (Linux)
```bash
git clone <repository>
cd starfish
git submodule init && git submodule update

cmake -Bout/efl/release -DMODE=release -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -DTARGETNAME=Starfish -G Ninja
ninja -C out/efl/release starfish.executable
```

### Run
```bash
./out/release/lightweight-web-engine 'path/to/file.html'
```

---

## Related Documentation

- [API Specification](./Spec.md) - Complete API surface documentation
- [Coding Style Guide](./Coding_Style_Guide.md) - C++ coding conventions
- [PWA Support](./PWA.md) - Progressive Web App features
- [RPi3 Guide](./RPi3_Guide.md) - Raspberry Pi 3 build guide
- [Debug Utilities](./guide/debug_utilities.md) - Debugging tools

---

## Verification

- **Tests executed**: Web Platform Tests, DOM Conformance Tests, Bidi Tests
- **Outstanding risks**: None identified
- **Recommended checks before PR**: Run `./tool/test_runner.py` for regression tests
