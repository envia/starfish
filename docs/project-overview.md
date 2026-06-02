# Starfish Project Overview

## Executive Summary

Starfish is a lightweight Web browser engine designed for TV, mobile, headless, and wearable devices. It provides a full web rendering engine with support for HTML5, CSS3, DOM, and modern web APIs, optimized for resource-constrained embedded environments.

## Project Classification

| Attribute | Value |
|-----------|-------|
| **Project Type** | Embedded C++ Web Engine |
| **Repository Type** | Monolith |
| **Primary Language** | C++ |
| **Build System** | CMake + Ninja |
| **Target Platforms** | Ubuntu, Tizen, Windows, Android |
| **Architecture** | Component-based layered architecture |

## Technology Stack

### Core Technologies

| Category | Technology | Version | Notes |
|----------|------------|---------|-------|
| **Language** | C++ | C++11 | C++11 features encouraged |
| **Build System** | CMake | 2.8.12+ | Ninja generator recommended |
| **Graphics Backend** | EFL + Cairo GL | - | Primary backend for Linux |
| **JavaScript Engine** | Escargot | - | Third-party JS engine |
| **Graphics** | Cairo, Skia | - | 2D graphics rendering |
| **Networking** | libcurl, OpenSSL | - | HTTP/HTTPS support |
| **Image Formats** | libpng, libjpeg-turbo, libwebp, giflib | - | Image decoding |
| **Media** | WebRTC, MP4Parse | - | Optional multimedia support |

### Third-Party Dependencies

| Library | Purpose |
|---------|---------|
| escargot | JavaScript engine |
| openssl | Cryptography and TLS |
| libcurl | HTTP client |
| libpng, libjpeg-turbo, libwebp | Image decoding |
| cairo | 2D graphics |
| libtuv | Event loop (libuv-like) |
| nanomsg | Messaging |
| httplib | HTTP server |
| googletest | Testing framework |

## Architecture Pattern

Starfish follows a **layered component architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    Shell Layer                          │
│         (EFL, GLFW, X11, Headless)                     │
├─────────────────────────────────────────────────────────┤
│                    Public API                           │
│         (LWEWebView.h, LWEWorker.h)                    │
├─────────────────────────────────────────────────────────┤
│                    Platform Layer                       │
│    (canvas, network, multimedia, tts, loader)          │
├─────────────────────────────────────────────────────────┤
│                    Core Engine                          │
│  (dom, layout, animation, style, events, fetch, etc.)  │
├─────────────────────────────────────────────────────────┤
│                    Binding Layer                        │
│         (JavaScript bindings via IDL)                   │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### Web Standards Support
- **HTML5**: Full HTML5 document support with extensive tag support
- **CSS3**: Comprehensive CSS property support (see Spec.md for details)
- **DOM**: Complete DOM Level 3 + HTML5 extensions
- **Events**: Full event model (UI, Mouse, Keyboard, Touch, etc.)
- **Canvas 2D**: Complete CanvasRenderingContext2D API
- **WebGL**: Optional WebGL support (build flag)

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

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Ubuntu Linux | ✅ Primary | 18.04, 16.04, 14.04 |
| Tizen | ✅ Supported | TV, Mobile, Wearable |
| Windows | ✅ Supported | Visual Studio 2019+ |
| Android | ✅ Supported | NDK r16b |

## Getting Started

### Prerequisites (Ubuntu)

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
git submodule init
git submodule update

cmake -Bout/efl/release -DMODE=release -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -DTARGETNAME=Starfish -G Ninja
ninja -C out/efl/release starfish.executable
```

### Running

```bash
./out/efl/release/bin/lightweight-web-engine 'path/to/file.html'
```

## Documentation Index

### Generated Documentation
- [Architecture](./architecture.md) - System architecture details
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure
- [Development Guide](./development-guide.md) - Build and development instructions

### Existing Documentation
- [Specification](./Spec.md) - Complete API specification (HTML, DOM, CSS, Events)
- [Coding Style Guide](./Coding_Style_Guide.md) - C++ coding conventions
- [PWA Design](./PWA.md) - Progressive Web App / Service Worker design
- [RPi3 Guide](./RPi3_Guide.md) - Raspberry Pi 3 specific guide
- [Debug Utilities](./guide/debug_utilities.md) - Debugging and tracing tools

## Testing

Starfish uses Web Platform Tests (WPT) and custom test suites:

```bash
# Run all tests
./tool/test_runner.py

# Specific test suites
./tool/test_runner.py dom_conformance
./tool/test_runner.py wpt_all
./tool/test_runner.py vendor_test
```

## CI/CD

- GitLab CI configured (`.gitlab-ci.yml`)
- GBS build for Tizen packaging

## Governance

All decisions are made by consensus, respecting the principles and rules of the community. See [Samsung Inner Source Governance](https://github.sec.samsung.net/InnerSource/SamsungInnerSourceProgram/blob/master/GettingStarted/Governance.md) for details.
