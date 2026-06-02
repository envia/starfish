# Architecture Documentation

## Executive Summary

Starfish is a lightweight web browser engine built on a layered architecture designed for embedded systems. It implements the full web platform stack from HTML parsing through JavaScript execution to rendering, with careful attention to memory efficiency and portability.

## Architecture Pattern

**Layered Architecture with Platform Abstraction**

The engine follows a classic browser engine architecture with distinct layers:
1. **Public API Layer** - Embedder interface
2. **Shell Layer** - Platform-specific application hosting
3. **Core Engine Layer** - Web platform implementation
4. **Binding Layer** - JavaScript/C++ bridge
5. **Platform Abstraction Layer** - OS/hardware abstraction
6. **Third-Party Libraries** - External dependencies

## Technology Stack

### Core Technologies

| Category | Technology | Version/Notes |
|----------|-----------|---------------|
| **Language** | C++ | C++11 standard |
| **Build System** | CMake | 2.8.12+ |
| **Build Generator** | Ninja | Primary |
| **JavaScript Engine** | Escargot | Custom, ES6+ |
| **Graphics** | Cairo | 2D vector graphics |
| **Garbage Collection** | Boehm GC | Conservative GC |
| **Unicode** | ICU | Internationalization |
| **Network** | libcurl | HTTP/HTTPS |
| **SSL/TLS** | OpenSSL | Secure connections |

### Platform Backends

| Backend | Graphics | Event Loop | Window System |
|---------|----------|------------|---------------|
| `efl_cairo_gl` | Cairo + GL | GLib | EFL/Elementary |
| `uv_cairo_gl` | Cairo + GL | libuv | GLFW |
| `glib_cairo_gl` | Cairo + GL | GLib | X11 |
| `efl_headless` | Mock | GLib | None |
| `glib_headless` | Mock | GLib | None |

## Component Architecture

### 1. Public API Layer

The public API provides the interface for embedding applications.

```
┌─────────────────────────────────────────────────────────────┐
│                      Public API                              │
├─────────────────────────────────────────────────────────────┤
│  LWEWebView          │  LWEWorker         │  Delegates      │
│  - loadURL()         │  - createWorker()  │  - LoadDelegate │
│  - reload()          │  - postMessage()   │  - UIDelegate    │
│  - evaluateScript()  │  - terminate()     │  - PolicyDelegate│
│  - goBack/Forward()  │                    │                 │
└─────────────────────────────────────────────────────────────┘
```

**Key Classes:**
- `LWEWebView` - Main web view widget
- `LWEWorker` - Worker instance management
- `LWEDelegateLoader` - Delegate loading mechanism
- Bridge interfaces for platform integration

### 2. Shell Layer

Platform-specific application hosting and window management.

```
shell/
├── Shell.cpp/h           # Abstract shell interface
├── Window.h              # Window abstraction
├── ShellConfig.h         # Shell configuration
├── efl/                  # EFL shell (Tizen)
├── glfw/                 # GLFW shell (Desktop)
├── x11/                  # X11 shell
├── headless/             # Headless mode
├── glib/                 # GLib event loop
├── libuv/                # libuv event loop
└── windows/              # Windows shell
```

**Responsibilities:**
- Window creation and management
- Event loop integration
- Input event handling
- Native widget integration

### 3. Core Engine Layer

The heart of the web platform implementation.

#### DOM Implementation

```
core/dom/
├── Document.cpp          # Document node
├── Element.cpp           # Element interface
├── Node.cpp              # Node base class
├── Attr.cpp              # Attribute nodes
├── CharacterData.cpp     # Text/Comment base
├── DOMImplementation.cpp # DOM factory
├── DOMParser.cpp         # HTML/XML parsing
├── CustomElementRegistry.cpp # Custom elements
└── ... (many more DOM interfaces)
```

**Key Design Patterns:**
- **Node Hierarchy**: Node → Element/CharacterData/Document
- **Tree Ownership**: Parent-child references with GC management
- **Mutation Observers**: Change notification system

#### Style System

```
core/style/
├── Style.h/cpp           # Computed style storage
├── StyleBuilder.cpp      # Style construction
├── StyleResolver.cpp     # Style resolution
├── Length.h/cpp          # CSS length values
├── Unit.h/cpp            # CSS units
└── StyleProperty.cpp     # Property handling
```

**CSS Processing Pipeline:**
1. Parse CSS text → StyleRule objects
2. Match selectors against DOM
3. Resolve computed styles
4. Apply to layout

#### Layout Engine

```
core/layout/
├── LayoutObject.cpp      # Base layout object
├── LayoutBlock.cpp       # Block layout
├── LayoutInline.cpp      # Inline layout
├── LayoutFlexibleBox.cpp # Flexbox layout
├── LayoutGrid.cpp        # Grid layout
├── LayoutView.cpp        # Viewport layout
└── LayoutUtil.cpp        # Layout utilities
```

**Layout Flow:**
1. Style resolution → LayoutObject creation
2. Min/max content sizing
3. Layout pass (width, then height)
4. Position assignment
5. Paint invalidation

#### Animation System

```
core/animation/
├── Animation.cpp         # Web Animations API
├── AnimationApplier.cpp  # Apply animations
├── AnimationExecutor.cpp # Run animations
├── AnimationTask.cpp     # Task scheduling
├── CubicBezier.cpp       # Timing functions
├── TimingFunction.cpp    # Easing functions
└── TransitionApplier.cpp # CSS Transitions
```

### 4. Binding Layer

JavaScript/C++ interconnection.

```
binding/
├── ScriptEngineInstance.cpp    # JS engine interface
├── ScriptBindingInstance.cpp   # Binding context
├── ScriptWrappable.cpp         # Base for JS-exposed objects
├── ScriptBindingSecurity.cpp   # Security checks
├── WindowProxy.cpp             # Window proxy
├── Builtin.idl                 # Built-in interfaces
└── *CustomBinding.cpp          # Custom implementations
```

**IDL Binding Flow:**
1. `.idl` file defines interface
2. Code generator creates C++ bindings
3. `ScriptWrappable` provides GC integration
4. Custom bindings handle special cases

**Key Concepts:**
- **ScriptWrappable**: Base class for all JS-exposed objects
- **ExecutionContext**: JavaScript execution context
- **WindowProxy**: Security boundary for window access

### 5. Platform Abstraction Layer

OS and hardware abstraction for portability.

```
platform/
├── canvas/               # Canvas backend
│   └── cairo/           # Cairo implementation
├── event/                # Event abstraction
├── file/                 # File system
├── loader/               # Resource loading
│   ├── ResourceLoader.cpp
│   └── ResourceFetcher.cpp
├── message_loop/         # Message loop
├── multimedia/           # Media playback
├── network/              # Network stack
│   ├── curl/             # libcurl implementation
│   └── http/             # HTTP handling
├── process/              # Process management
├── public/               # Platform interfaces
└── tts/                  # Text-to-Speech
```

**Platform Interface Pattern:**
```cpp
// Abstract interface
class CanvasContext {
public:
    virtual void drawRect(...) = 0;
    virtual void drawImage(...) = 0;
};

// Cairo implementation
class CairoCanvasContext : public CanvasContext {
    // Cairo-specific implementation
};
```

### 6. Worker Architecture

Multi-process worker implementation.

```
launcher/
├── ServiceWorkerEntry.cpp   # Service Worker entry
└── SharedWorkerEntry.cpp     # Shared Worker entry

core/modules/worker/
├── WorkerManager.cpp         # Worker coordination
├── WorkerThread.cpp          # Worker thread
└── WorkerGlobalScope.cpp     # Worker global object
```

**Worker Communication:**
- Main thread ↔ Worker via `postMessage()`
- IPC via nanomsg for process isolation
- Shared memory for large data

## Data Flow

### Page Load Sequence

```
1. URL Input
   └── LWEWebView::loadURL()
       └── ResourceFetcher::fetch()
           └── NetworkRequest (libcurl)
               └── Data received
                   └── HTMLDocumentParser
                       └── DOM Tree construction
                           ├── CSS parsing
                           │   └── StyleResolver
                           ├── DOM Content Loaded
                           │   └── Script execution
                           └── Document Complete
                               └── Layout
                                   └── Paint
                                       └── Composite
```

### JavaScript Execution Flow

```
1. Script element parsed
   └── HTMLScriptElement
       └── ScriptRunner
           └── ScriptEngineInstance::evaluate()
               └── Escargot::Script::evaluate()
                   └── Bytecode execution
                       └── C++ callbacks (via bindings)
                           └── DOM manipulation
                               └── Style/Layout invalidation
```

### Event Dispatch Flow

```
1. Platform event (mouse, keyboard)
   └── Shell event handler
       └── PlatformEvent
           └── EventDispatcher
               └── Hit testing
                   └── Target element
                       └── Event path computation
                           └── Dispatch (capture → target → bubble)
                               └── JavaScript handlers
```

## Memory Management

### Garbage Collection

The engine uses **Boehm Conservative GC** for automatic memory management.

**GC-Managed Objects:**
- DOM nodes
- JavaScript objects
- Strings
- Layout objects

**GC Integration:**
```cpp
// GC-aware allocation
void* operator new(size_t size) {
    return GC_MALLOC(size);
}

// Typed allocation for precise marking
void* operator new(size_t size) {
    return GC_MALLOC_EXPLICITLY_TYPED(size, descriptor);
}
```

### Root Set Management

```cpp
// Root registration
void Starfish::addPointerInRootSet(void* ptr);
void Starfish::removePointerFromRootSet(void* ptr);
```

## Threading Model

### Main Thread
- DOM manipulation
- Style resolution
- Layout
- JavaScript execution (main context)

### Worker Threads
- JavaScript execution (worker context)
- Background computation
- File I/O

### Platform Threads
- Network I/O
- Image decoding
- Media playback

## Security Model

### Same-Origin Policy
- Origin comparison for cross-origin access
- CORS support for controlled cross-origin requests

### Content Security Policy
- CSP header parsing
- Directive enforcement
- Violation reporting

### Script Security
- Script binding security checks
- WindowProxy for cross-origin window access protection

## Build Configuration

### Feature Flags

| Flag | Effect |
|------|--------|
| `STARFISH_ENABLE_CANVAS` | Canvas 2D API |
| `STARFISH_ENABLE_WEBGL` | WebGL support |
| `STARFISH_ENABLE_WEBAUDIO` | Web Audio API |
| `STARFISH_ENABLE_WEBSOCKET` | WebSocket API |
| `STARFISH_ENABLE_TTS` | Speech Synthesis |
| `STARFISH_ENABLE_MULTIMEDIA` | `<video>`/`<audio>` |
| `STARFISH_ENABLE_WEBRTC` | WebRTC |
| `STARFISH_ENABLE_HTTPCACHE` | HTTP Cache |
| `STARFISH_ENABLE_THREADING` | Multi-threading |

### Platform Defines

```cpp
// Graphics backend
#define PORT_CANVAS_BACKEND_CAIRO
#define PORT_GRAPHIC_BACKEND_MOCK

// Event loop
#define PORT_EVENTLOOP_BACKEND_GLIB
#define PORT_EVENTLOOP_BACKEND_LIBUV

// Window system
#define PORT_WEBVIEW_BRIDGE_EFL
#define PORT_WEBVIEW_BRIDGE_FLUTTER
```

## Extension Points

### Adding New DOM Interfaces
1. Create IDL file
2. Implement C++ class
3. Add to binding generator
4. Register in CMake

### Adding New CSS Properties
1. Add to `FOR_EACH_STYLE_ATTRIBUTE` macro
2. Implement parsing
3. Implement layout handling

### Adding New Platform Backends
1. Define platform macros
2. Implement platform interfaces
3. Create shell implementation
4. Add CMake configuration

## Performance Considerations

### Memory Optimization
- Conservative GC with configurable frequency
- String atomization
- Style sharing
- Layout object pooling

### Rendering Optimization
- Incremental layout
- Paint invalidation tracking
- Layer-based compositing (where supported)

### JavaScript Performance
- Escargot JIT compilation
- Inline caching
- Hidden class optimization
