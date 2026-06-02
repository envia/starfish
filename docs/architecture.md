# Starfish Architecture

## Executive Summary

Starfish is a lightweight web browser engine built on a layered architecture. It separates concerns between the public API, shell integration, core web engine, JavaScript binding, platform abstraction, and third-party dependencies.

## Technology Stack

| Category | Technology | Version/Notes |
|----------|------------|---------------|
| **Core Language** | C++ | C++11/14 features |
| **Build System** | CMake | 2.8.12+ |
| **Build Generator** | Ninja | Primary |
| **JavaScript Engine** | Escargot | Custom lightweight JS engine |
| **Graphics** | Cairo | OpenGL or software rendering |
| **Image Decoding** | libpng, libjpeg-turbo, libwebp, giflib | |
| **Networking** | libcurl, OpenSSL | HTTP/HTTPS, WebSocket |
| **Garbage Collection** | BDWGC (Boehm GC) | Conservative GC |
| **UI Framework** | EFL (Enlightenment) | Primary shell on Linux/Tizen |
| **Multimedia** | FFmpeg (optional) | Video/Audio playback |

## Architecture Pattern

Starfish follows a **Layered Architecture** with platform abstraction:

```
┌────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Public API (inc/)                         │  │
│  │  LWEWebView, LWEWorker, LWE, WebContainer, Settings          │  │
│  └──────────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────────┤
│                          SHELL LAYER                               │
│  ┌─────────┬─────────┬──────────┬───────────┬─────────┬──────────┐  │
│  │   EFL   │  GLFW   │   X11    │ Headless  │ Android │ Windows  │  │
│  └─────────┴─────────┴──────────┴───────────┴─────────┴──────────┘  │
├────────────────────────────────────────────────────────────────────┤
│                          CORE ENGINE                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        DOM (core/dom)                        │   │
│  │  Document, Element, Node, Event, HTMLElement implementations│   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                      Layout (core/layout)                   │   │
│  │  Box model, Flexbox, Block/Inline layout, Text shaping      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                       CSS (core/style)                       │   │
│  │  Style resolution, Cascade, Animations, Transitions         │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                      Events (core/dom)                      │   │
│  │  MouseEvent, KeyboardEvent, CustomEvent, FocusEvent, etc.   │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                      Fetch (core/fetch)                      │   │
│  │  XMLHttpRequest, Fetch API, Resource loading                │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                     Storage (core/storage)                   │   │
│  │  LocalStorage, SessionStorage, IndexedDB (optional)         │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                     Canvas (core/modules/canvas)            │   │
│  │  CanvasRenderingContext2D, WebGL (optional)                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────────┤
│                    JAVASCRIPT BINDING LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    binding/                                  │   │
│  │  ScriptEngineInstance, ScriptWrappable, Custom Bindings     │   │
│  │  IDL-generated interfaces, WindowProxy                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
├────────────────────────────────────────────────────────────────────┤
│                       PLATFORM LAYER                               │
│  ┌────────────┬────────────┬────────────┬────────────────────┐    │
│  │  Network   │   File     │  Canvas    │   Message Loop     │    │
│  │ (HTTP, WS) │ (I/O)      │ (Native)   │ (Event Loop)       │    │
│  ├────────────┼────────────┼────────────┼────────────────────┤    │
│  │ Multimedia │   TTS      │  Process   │     Event          │    │
│  │ (A/V)      │ (Speech)   │ (Threads)  │   (Platform)      │    │
│  └────────────┴────────────┴────────────┴────────────────────┘    │
├────────────────────────────────────────────────────────────────────┤
│                    THIRD-PARTY LIBRARIES                           │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Escargot (JS) │ Cairo (Graphics) │ OpenSSL (TLS) │ curl   │   │
│  │ libpng, libjpeg-turbo, libwebp, giflib (Images)           │   │
│  │ nanomsg (IPC) │ httplib │ webrtc (optional)               │   │
│  └────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Public API Layer (`inc/`, `src/public/`)

The public API provides the external interface for embedding Starfish:

- **LWE::LWE** - Engine initialization and lifecycle management
- **LWE::WebView** - Web view widget for displaying web content
- **LWE::WebContainer** - Low-level rendering container with buffer/GL output
- **LWE::Settings** - Configuration for user agent, cache, security, etc.
- **LWE::CookieManager** - Cookie storage and management

### 2. Shell Layer (`src/shell/`)

Platform-specific UI integration:

| Shell | Platform | Description |
|-------|----------|-------------|
| `efl/` | Linux, Tizen | Enlightenment Foundation Libraries |
| `glfw/` | Cross-platform | GLFW OpenGL window |
| `x11/` | Linux | X11 native |
| `headless/` | Any | No UI, for testing |
| `glib/` | Linux | GLib main loop integration |
| `libuv/` | Cross-platform | libuv event loop |

### 3. DOM Implementation (`src/core/dom/`)

Complete DOM implementation including:

- **Core Interfaces**: Node, Element, Document, CharacterData
- **HTML Elements**: All HTML5 elements (HTMLInputElement, HTMLImageElement, etc.)
- **Events**: Event, EventTarget, MouseEvent, KeyboardEvent, CustomEvent
- **Traversal**: Range, TreeWalker, NodeIterator
- **CSS OM**: CSSStyleSheet, CSSRule, CSSStyleDeclaration

### 4. Layout Engine (`src/core/layout/`)

Box model implementation:

- Block, Inline, Flexbox layout modes
- Text shaping and line breaking
- Float and positioning
- Table layout

### 5. CSS Engine (`src/core/style/`)

Style processing:

- Selector matching
- Cascade and inheritance
- Property parsing and computation
- Animations and transitions

### 6. JavaScript Binding (`src/binding/`)

Bridge between C++ and Escargot JS engine:

- IDL-based interface generation
- Custom bindings for performance-critical paths
- Garbage collection integration

## Data Flow

### Page Loading Flow

```
URL Input
    │
    ▼
┌─────────────┐
│ Resource    │ ─── HTTP/HTTPS request ─── OpenSSL/curl
│ Loader      │
└─────────────┘
    │
    ▼
┌─────────────┐
│ HTML        │ ─── Tokenization ─── Tree Construction
│ Parser      │
└─────────────┘
    │
    ▼
┌─────────────┐
│ DOM         │ ─── Document, Element nodes
│ Tree        │
└─────────────┘
    │
    ▼
┌─────────────┐
│ CSS         │ ─── Style resolution, Cascade
│ Parser      │
└─────────────┘
    │
    ▼
┌─────────────┐
│ Layout      │ ─── Box tree, positioning
│ Engine      │
└─────────────┘
    │
    ▼
┌─────────────┐
│ Painter     │ ─── Cairo drawing commands
│             │
└─────────────┘
    │
    ▼
┌─────────────┐
│ Compositor  │ ─── OpenGL rendering
│             │
└─────────────┘
    │
    ▼
  Screen
```

## Threading Model

Starfish supports both single-threaded and multi-threaded modes:

### Single-Threaded Mode (Default)
- All operations on main thread
- Event loop processes: I/O, timers, UI events
- Simpler, lower memory footprint

### Multi-Threaded Mode (`isThreadMode = true`)
- Main thread: UI and rendering
- Worker threads: JavaScript execution (with Workers enabled)
- Thread-safe garbage collection

## Memory Management

Starfish uses the **Boehm-Demers-Weiser Garbage Collector (BDWGC)**:

- Conservative garbage collection
- Automatic memory management for DOM objects
- Configurable GC frequency (`gcFrequency`)
- Root set management for thread mode

## Build-Time Feature Flags

Major compile-time features controlled by CMake flags:

| Flag | Effect |
|------|--------|
| `STARFISH_ENABLE_CANVAS` | Canvas 2D API |
| `STARFISH_ENABLE_MULTIMEDIA` | `<video>`, `<audio>` elements |
| `WEBGL=1` | WebGL API |
| `WEBRTC=1` | WebRTC, MediaStream |
| `WORKER=1` | Web Workers |
| `SHARED_WORKER=1` | Shared Workers |
| `SERVICE_WORKER=1` | Service Workers, Cache API |
| `IDB=1` | IndexedDB |
| `STARFISH_ENABLE_WEBAUDIO` | Web Audio API |
| `STARFISH_ENABLE_WEBSOCKET` | WebSocket API |
| `STARFISH_ENABLE_TTS` | Speech Synthesis API |
| `ENABLE_DEBUGGER=1` | JavaScript debugger support |
| `ENABLE_WASM=1` | WebAssembly support |

## Platform-Specific Notes

### Linux (EFL)
- Primary development platform
- Requires EFL libraries
- OpenGL ES rendering

### Tizen
- Tizen-specific packaging (TPK)
- Device API integration
- Tizen-specific manifest

### Android
- AAR and APK packaging
- JNI bridge
- Gradle build integration

### Windows
- WinForms shell
- Visual Studio build
- Native Windows graphics

## Extension Points

1. **Custom Shells**: Implement shell interface in `src/shell/`
2. **Platform Backends**: Implement platform abstraction in `src/platform/`
3. **Custom Bindings**: Add JavaScript interfaces via IDL files
4. **Delegate Pattern**: Use `LWEDelegate` for custom behavior injection
