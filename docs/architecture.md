# Starfish Architecture

**Generated:** 2026-06-01  
**Architecture Pattern:** Layered Component Architecture

---

## Executive Summary

Starfish implements a layered component architecture optimized for embedded systems. The engine is structured in four primary layers: Platform Abstraction, Core Engine, Browser Functionality, and Application Shell. This design enables portability across Linux, Tizen, Windows, and Android platforms while maintaining a small memory footprint.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Shell Layer                    │
│         (EFL Shell, GLFW Shell, X11 Shell, Headless)         │
├─────────────────────────────────────────────────────────────┤
│                    Browser Functionality                      │
│        (Navigation, History, Settings, Window Management)    │
├─────────────────────────────────────────────────────────────┤
│                       Core Engine                             │
│   ┌──────────┬──────────┬──────────┬──────────┬──────────┐   │
│   │   DOM    │  Layout  │  Style   │  Events  │ Animation│   │
│   └──────────┴──────────┴──────────┴──────────┴──────────┘   │
│   ┌──────────┬──────────┬──────────┬──────────┐              │
│   │ Storage  │  Fetch   │   CSP    │  XML     │              │
│   └──────────┴──────────┴──────────┴──────────┘              │
├─────────────────────────────────────────────────────────────┤
│                  Platform Abstraction Layer                   │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐    │
│  │ Canvas │ Network│Multimedia│ File  │  TTS   │ Event  │    │
│  └────────┴────────┴────────┴────────┴────────┴────────┘    │
├─────────────────────────────────────────────────────────────┤
│                     Third-Party Libraries                     │
│    Escargot (JS) │ Cairo (Graphics) │ OpenSSL │ libwebsockets │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### 1. Platform Abstraction Layer (`src/platform/`)

Provides OS-agnostic interfaces for platform-specific functionality.

| Component | Purpose |
|-----------|---------|
| `canvas/` | Canvas 2D rendering abstraction |
| `event/` | Platform event handling |
| `file/` | File system operations |
| `loader/` | Resource loading |
| `message_loop/` | Event loop management |
| `multimedia/` | Audio/Video playback |
| `network/` | HTTP, WebSocket networking |
| `process/` | Process management |
| `tts/` | Text-to-speech |
| `public/` | Public platform API |

### 2. Core Engine (`src/core/`)

The heart of the browser engine implementing web standards.

| Component | Purpose |
|-----------|---------|
| `dom/` | DOM tree, elements, documents |
| `event/` | Event propagation, custom events |
| `layout/` | Box model, flexbox, grid layout |
| `style/` | CSS parsing, cascade, computed styles |
| `animation/` | CSS animations and transitions |
| `page/` | Page lifecycle, navigation |
| `storage/` | localStorage, sessionStorage |
| `fetch/` | Fetch API implementation |
| `csp/` | Content Security Policy |
| `xml/` | XML parsing and DOM |
| `serialize/` | HTML serialization |
| `util/` | Utility functions |
| `extra/` | Extended features |
| `inspector/` | DevTools protocol |
| `modules/` | ES6 modules |

### 3. Browser Functionality (`src/browser/`)

Browser-level features built on the core engine.

- Navigation controller
- History management
- Settings and preferences
- Window management
- Tab management (where applicable)

### 4. Shell Layer (`src/shell/`)

Application shells that embed the engine.

| Shell | Platform | Description |
|-------|----------|-------------|
| EFL Shell | Linux/Tizen | Enlightenment Foundation Libraries UI |
| GLFW Shell | Linux | Cross-platform window |
| X11 Shell | Linux | X11 native |
| Headless | All | No UI for testing |

---

## Key Design Patterns

### Memory Management
- Custom garbage collection integration
- Careful pointer management with `NULLABLE` annotations
- Assertion-based validation (`STARFISH_ASSERT`)
- No RTTI (Run-Time Type Information)

### Rendering Pipeline
```
HTML/CSS Input → Parser → DOM Tree → Style Resolution → Layout → Paint
                                    ↓
                              JavaScript (Escargot)
```

### Event Flow
```
Platform Event → Platform Abstraction → DOM Events → JavaScript Handlers
```

---

## Threading Model

- **Main Thread**: DOM, layout, rendering, JavaScript execution
- **Worker Threads**: Optional (build flag `WORKER=1`)
- **Platform Threads**: Network I/O, multimedia decoding

---

## Build Configuration

### Build Flags

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `HOST` | linux, tizen, windows | linux | Target platform |
| `MODE` | debug, release | release | Build mode |
| `BACKEND` | efl_cairo_gl, uv_cairo_gl, glib_cairo_gl | efl_cairo_gl | Graphics backend |
| `ARCH` | x64, arm | x64 | Target architecture |
| `SHELL` | efl, efl_headless, glfw, x11 | efl | Shell type |

### Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `WEBGL` | 1 | WebGL support |
| `WEBRTC` | 0 | WebRTC support |
| `WORKER` | 0 | Web Workers |
| `SHARED_WORKER` | 0 | Shared Workers |
| `SERVICE_WORKER` | 0 | Service Workers |
| `IDB` | 0 | IndexedDB |
| `ENABLE_DEBUGGER` | 0 | DevTools debugger |
| `ENABLE_WASM` | 0 | WebAssembly |
| `ENABLE_CODECACHE` | 0 | Code caching |
| `USE_FFMPEG_MEDIA_PLAYER` | 0 | FFmpeg media backend |

---

## JavaScript Integration

Starfish uses **Escargot** as its JavaScript engine, providing:
- ES6+ feature support
- DOM binding integration
- Web API implementations
- Just-In-Time compilation (where supported)

### IDL-Based API Generation
Web APIs are defined in `.idl` files under `src/**/*.idl`:
- Interface definitions
- Method signatures
- Attribute declarations
- Build-conditional exposure (`[STARFISH_ENABLE_*]`)

---

## Data Flow

### Page Load Sequence
```
1. URL Resolution → File/Network Load
2. HTML Parsing → DOM Construction
3. CSS Parsing → Style Rules
4. Style Resolution → Computed Styles
5. Layout → Box Tree
6. Paint → Graphics Backend
7. JavaScript Execution → DOM Manipulation
8. Re-layout/Repaint as needed
```

### Resource Loading
```
Resource Request → Platform Loader → Cache Check → Network/File → Decode → Use
```

---

## Security Model

- **Content Security Policy (CSP)**: Implemented in `src/core/csp/`
- **CORS**: Cross-Origin Resource Sharing support
- **TLS/SSL**: Via OpenSSL
- **Sandboxing**: Platform-specific where available

---

## Testing Architecture

```
test/
├── reftest/              # Reftests (reference comparisons)
│   └── web-platform-tests/  # W3C WPT suite
├── unit/                 # Unit tests
└── internal/             # Internal tests
```

Test runner: `tool/test_runner.py`

---

## Extension Points

1. **New HTML Elements**: Add to `src/core/dom/` with IDL definition
2. **CSS Properties**: Extend `src/core/style/Style.h` macros
3. **Platform Ports**: Implement `src/platform/` interfaces
4. **Shells**: Create new shell in `src/shell/`

---

## Performance Considerations

- Minimal memory allocation in hot paths
- Lazy initialization of features
- Build-time feature exclusion (no dead code)
- Efficient string handling with atomic strings
- Layout caching and incremental updates

---

## Related Documentation

- [Project Overview](./project-overview.md)
- [API Specification](./Spec.md)
- [Development Guide](./development-guide.md)
- [Source Tree Analysis](./source-tree-analysis.md)
