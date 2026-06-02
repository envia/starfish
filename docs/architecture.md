# Starfish Architecture

## Executive Summary

Starfish is a lightweight web browser engine built on a layered component architecture. It separates concerns into distinct layers: shell, public API, platform abstraction, core engine, and JavaScript binding. This design enables portability across multiple platforms (Linux, Tizen, Windows, Android) while maintaining a consistent web standards implementation.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  EFL Shell  │  │ GLFW Shell  │  │ X11 Shell   │  │ Headless  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                          PUBLIC API LAYER                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  LWEWebView.h / LWEWorker.h / PlatformIntegrationData.h    │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                       PLATFORM ABSTRACTION LAYER                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Canvas  │ │ Network  │ │Multimedia│ │   TTS    │ │  Loader  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │  Event   │ │  File    │ │ Process  │ │ Message  │              │
│  │          │ │          │ │          │ │  Loop    │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
├─────────────────────────────────────────────────────────────────────┤
│                          CORE ENGINE LAYER                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │   DOM    │ │  Layout  │ │  Style   │ │ Animation│ │  Event   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Fetch   │ │ FileAPI  │ │ Storage  │ │   CSP    │ │   XML    │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │  Page    │ │Serialize │ │ Modules  │ │Inspector │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
├─────────────────────────────────────────────────────────────────────┤
│                       BINDING LAYER (IDL → C++)                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  binding_generator/ + src/binding/ (JavaScript Bindings)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                     JAVASCRIPT ENGINE LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Escargot JS Engine                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Shell Layer

The shell layer provides the application entry point and UI integration:

| Shell | Platform | Description |
|-------|----------|-------------|
| EFL | Tizen, Linux | Primary shell using Enlightenment Foundation Libraries |
| GLFW | Desktop | Cross-platform desktop shell using GLFW |
| X11 | Linux | Direct X11 integration |
| Headless | Testing | No UI, for automated testing and CI |

### Public API Layer

The public API provides the stable interface for applications:

```cpp
// Main web view interface
class LWEWebView {
    void loadURL(const String& url);
    void loadHTML(const String& html);
    void reload();
    void stop();
    // ...
};

// Worker interface
class LWEWorker {
    void start();
    void terminate();
    // ...
};
```

### Platform Abstraction Layer

The platform layer abstracts OS-specific functionality:

#### Canvas Backend
- Cairo-based 2D graphics rendering
- OpenGL acceleration support
- Platform-specific surface management

#### Network Stack
- HTTP/HTTPS via libcurl
- WebSocket support (optional)
- Fetch API implementation

#### Multimedia
- Video/Audio playback
- WebRTC support (optional)
- Platform media players

#### Event Loop
- libtuv (libuv-like) event loop
- Timer management
- I/O multiplexing

### Core Engine Layer

#### DOM (Document Object Model)
- Full HTML5 DOM implementation
- ~417 IDL interfaces
- Node tree management
- Element creation and manipulation

#### Layout Engine
- CSS 2.1 box model
- Flexbox layout
- Grid layout (partial)
- Responsive layout support

#### Style System
- CSS parsing and cascading
- Style resolution
- Property inheritance
- CSS variables

#### Animation
- CSS Transitions
- CSS Animations
- Keyframe animation
- Timing functions

#### Event System
- DOM Events
- UI Events
- Mouse/Keyboard/Touch events
- Custom events

#### Fetch API
- XMLHttpRequest
- Fetch API
- Headers/Request/Response
- CORS handling

### Binding Layer

JavaScript bindings are generated from IDL files:

```
src/**/*.idl → binding_generator/ → C++ classes + JS bindings
```

Key IDL extended attributes:
- `[Exposed=(Window,Worker)]` - Availability context
- `[ConstructorCallWith=ExecutionContext]` - Context injection
- `[Unimplemented]` - Stub interfaces
- `[STARFISH_ENABLE_*]` - Build-conditional exposure

## Data Flow

### Page Load Sequence

```
1. URL Input
      ↓
2. Resource Loader (platform/network)
      ↓
3. HTML Parser (core/dom)
      ↓
4. DOM Tree Construction
      ↓
5. CSS Parsing (core/style)
      ↓
6. Style Resolution
      ↓
7. Layout (core/layout)
      ↓
8. Paint (platform/canvas)
      ↓
9. Display (shell)
```

### JavaScript Execution

```
1. Script Tag / eval()
      ↓
2. Escargot Parser
      ↓
3. Bytecode Compilation
      ↓
4. Execution
      ↓
5. DOM Binding Calls (via IDL)
      ↓
6. C++ Implementation
      ↓
7. DOM Updates
      ↓
8. Style/Layout Recalc
      ↓
9. Paint
```

## Threading Model

```
┌─────────────────────────────────────────────────────────┐
│                     Main Thread                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Event Loop (libtuv)                             │   │
│  │  - DOM manipulation                              │   │
│  │  - Style/Layout calculation                      │   │
│  │  - JavaScript execution (main context)            │   │
│  │  - Painting                                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Worker Threads (optional)             │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Dedicated Worker                                │   │
│  │  - Background computation                        │   │
│  │  - Independent JS context                        │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Service Worker                                  │   │
│  │  - Network interception                          │   │
│  │  - Caching                                       │   │
│  │  - Push notifications                            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Memory Management

- **Garbage Collection**: Escargot JS engine manages JavaScript object lifecycle
- **Reference Counting**: DOM nodes use reference counting
- **Arena Allocation**: Layout objects use arena allocators for efficiency
- **String Management**: `String` class with UTF-8/UTF-16 support

## Build Configuration

### Feature Flags

| Flag | Effect |
|------|--------|
| `STARFISH_ENABLE_CANVAS` | Canvas 2D API |
| `WEBGL` | WebGL API |
| `STARFISH_ENABLE_WEBAUDIO` | Web Audio API |
| `STARFISH_ENABLE_WEBSOCKET` | WebSocket API |
| `WEBRTC` | WebRTC + MediaStream |
| `WORKER` | Web Workers |
| `SERVICE_WORKER` | Service Workers + Cache API |
| `IDB` | IndexedDB |
| `STARFISH_ENABLE_TTS` | Text-to-Speech |
| `ENABLE_DEBUGGER` | JavaScript debugger |

### Platform Variants

| Platform | Host | Backend | Shell |
|----------|------|---------|-------|
| Linux Desktop | `linux` | `efl_cairo_gl` | `efl` |
| Tizen TV | `tizen` | `efl_cairo_gl` | `efl` |
| Tizen Mobile | `tizen` | `efl_cairo_gl` | `efl` |
| Tizen Wearable | `tizen` | `efl_cairo_gl` | `efl` |
| Windows | `windows` | - | WinForms |
| Android | `android` | - | Java shell |

## Extension Points

### Adding New Web APIs

1. Define IDL interface in `src/core/[module]/`
2. Implement C++ class inheriting `ScriptWrappable`
3. Register in build system
4. Add tests

### Adding New Platforms

1. Implement platform abstraction interfaces in `src/platform/`
2. Create shell in `src/shell/`
3. Add build configuration in `build/`
4. Add packaging in `packaging/`

### Adding New CSS Properties

1. Add to `FOR_EACH_STYLE_ATTRIBUTE_*` macro
2. Implement parsing
3. Implement application
4. Add tests

## Security Considerations

- **Content Security Policy (CSP)**: Implemented in `src/core/csp/`
- **CORS**: Cross-origin resource sharing in fetch implementation
- **TLS**: OpenSSL for HTTPS
- **Sandboxing**: Process isolation for workers

## Performance Considerations

- **Lazy Parsing**: CSS and HTML parsed on demand
- **Incremental Layout**: Layout recalculated incrementally
- **Paint Optimization**: Dirty region tracking
- **Memory Pools**: Arena allocation for short-lived objects
- **JIT Compilation**: Escargot JIT for JavaScript
