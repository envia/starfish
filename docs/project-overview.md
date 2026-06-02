# Starfish - Lightweight Web Engine

## Project Overview

**Starfish** is a lightweight web browser engine designed for TV, mobile, headless, and wearable devices. It is a complete web rendering engine written in C++ that implements web standards including HTML5, CSS, DOM, and JavaScript APIs.

### Key Facts

| Attribute | Value |
|-----------|-------|
| **Project Type** | Embedded System / Web Browser Engine |
| **Primary Language** | C++ |
| **Build System** | CMake + Ninja |
| **License** | LGPL-2.1-or-later |
| **JavaScript Engine** | Escargot |
| **Supported Platforms** | Linux, Tizen, Windows, Android |

### Purpose

Starfish provides a lightweight, embeddable web rendering engine optimized for resource-constrained devices such as:
- Smart TVs
- Mobile devices
- Wearable devices
- Headless applications

### Key Features

- **HTML5 Support**: Comprehensive HTML5 element and attribute support
- **CSS Support**: Extensive CSS properties including Flexbox, Transforms, Animations
- **DOM API**: Full DOM Level 2/3 support with modern extensions
- **Canvas 2D**: Complete CanvasRenderingContext2D implementation
- **WebGL**: Optional WebGL support (build flag: `WEBGL=1`)
- **Multimedia**: Video and audio element support
- **WebSocket**: Real-time bidirectional communication
- **WebRTC**: Real-time communication (optional, `WEBRTC=1`)
- **Workers**: Web Workers, Shared Workers, Service Workers (optional)
- **WebAudio**: Audio processing API
- **TTS**: Text-to-Speech API support

### Architecture Highlights

```
┌─────────────────────────────────────────────────────────────┐
│                      Public API Layer                        │
│  (LWEWebView, LWEWorker, WebContainer, Settings, etc.)      │
├─────────────────────────────────────────────────────────────┤
│                      Shell Layer                             │
│  (EFL, GLFW, X11, Headless, Android, Windows shells)        │
├─────────────────────────────────────────────────────────────┤
│                      Core Engine                             │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│  │    DOM      │   Layout    │    CSS      │  Animation   │ │
│  ├─────────────┼─────────────┼─────────────┼─────────────┤ │
│  │   Events   │   Fetch     │   Storage   │   Canvas    │ │
│  └─────────────┴─────────────┴─────────────┴─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   JavaScript Binding                         │
│  (ScriptEngineInstance, Escargot integration)               │
├─────────────────────────────────────────────────────────────┤
│                      Platform Layer                          │
│  (Network, File I/O, Multimedia, Canvas, Message Loop)      │
├─────────────────────────────────────────────────────────────┤
│                   Third-Party Libraries                      │
│  (Escargot, Cairo, OpenSSL, libwebp, libpng, etc.)          │
└─────────────────────────────────────────────────────────────┘
```

### Build Configuration

Starfish uses CMake with extensive build options:

| Option | Default | Description |
|--------|---------|-------------|
| `HOST` | `linux` | Target platform (`linux`, `tizen`, `windows`) |
| `MODE` | `release` | Build mode (`debug`, `release`) |
| `BACKEND` | `efl_cairo_gl` | Graphics backend |
| `ARCH` | `x64` | Architecture (`x64`, `arm`) |
| `WEBGL` | `0` | Enable WebGL |
| `WEBRTC` | `0` | Enable WebRTC |
| `WORKER` | `0` | Enable Web Workers |
| `SERVICE_WORKER` | `0` | Enable Service Workers |
| `IDB` | `0` | Enable IndexedDB |
| `ENABLE_DEBUGGER` | `0` | Enable JavaScript debugger |

### Quick Start

```bash
# Clone and initialize
git clone <repository-url>
cd starfish
git submodule init
git submodule update

# Build (Linux/EFL)
cmake -Bout/efl/release -DMODE=release -DHOST=linux -DARCH=x64 \
      -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
ninja -C out/efl/release starfish.executable

# Run
./out/efl/release/bin/lightweight-web-engine 'file.html'
```

### Documentation Index

- [Architecture](./architecture.md) - Detailed architecture documentation
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure and organization
- [Development Guide](./development-guide.md) - Building and development instructions
- [Specification](./Spec.md) - Complete API specification (existing)
- [Coding Style Guide](./Coding_Style_Guide.md) - Code style conventions (existing)
- [PWA Support](./PWA.md) - Progressive Web App support (existing)
