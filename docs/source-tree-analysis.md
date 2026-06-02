# Starfish Source Tree Analysis

## Directory Structure Overview

```
starfish/
├── binding_generator/       # IDL-to-C++ binding generator
├── build/                   # CMake build configuration
│   ├── android/            # Android-specific build files
│   ├── tizen/              # Tizen-specific build files
│   ├── test/               # Test build configuration
│   └── windows/            # Windows-specific build files
├── compat/                  # Compatibility layer
├── docs/                    # Documentation
├── inc/                     # Public API headers
│   ├── LWEWebView.h        # Main WebView API
│   ├── LWEWorker.h         # Worker API
│   └── PlatformIntegrationData.h
├── inspector/               # DevTools inspector
├── packaging/               # Package definitions
├── src/                     # Source code
│   ├── binding/            # JavaScript bindings
│   ├── browser/            # Browser features (history)
│   ├── core/               # Core web engine
│   ├── launcher/           # Worker launchers
│   ├── platform/           # Platform abstraction
│   ├── public/             # Public API implementation
│   └── shell/              # Platform shells
├── test/                    # Test suites
├── third_party/             # Third-party dependencies
└── tool/                    # Development tools
```

## Critical Directories

### `src/core/` - Core Web Engine

The heart of Starfish's web rendering capabilities:

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `dom/` | DOM implementation | Document.cpp, Element.cpp, Node.cpp, HTMLElement.cpp |
| `layout/` | Layout engine | Block, Inline, Flexbox layout |
| `style/` | CSS processing | Style.cpp, Style.h |
| `animation/` | CSS Animations | Animation.cpp, AnimationExecutor.cpp |
| `events/` | Event system | Event.cpp, EventTarget.cpp |
| `fetch/` | Resource loading | XMLHttpRequest.cpp, Fetch API |
| `storage/` | Storage APIs | LocalStorage, SessionStorage |
| `fileapi/` | File API | Blob, File, FileReader |
| `xml/` | XML parsing | XMLDocument |
| `csp/` | Content Security Policy | ContentSecurityPolicy.cpp |
| `modules/` | Extended features | Canvas, WebAudio, etc. |
| `page/` | Page management | Window.cpp, Page.cpp |
| `serialize/` | Serialization | HTML serialization |
| `util/` | Utilities | String, AtomicString, QualifiedName |

### `src/binding/` - JavaScript Bindings

Interface between C++ and Escargot JavaScript engine:

| File | Purpose |
|------|---------|
| `ScriptEngineInstance.cpp` | Main JS engine interface |
| `ScriptBindingInstance.cpp` | Binding implementation |
| `ScriptWrappable.cpp` | Wrappable base for GC objects |
| `WindowProxy.cpp` | Window proxy for security |
| `*CustomBinding.cpp` | Custom bindings for performance |

### `src/platform/` - Platform Abstraction

Platform-specific implementations:

| Directory | Purpose |
|-----------|---------|
| `canvas/` | Native canvas rendering |
| `event/` | Platform event handling |
| `file/` | File I/O |
| `loader/` | Resource loading |
| `message_loop/` | Event loop |
| `multimedia/` | Audio/Video playback |
| `network/` | HTTP, WebSocket |
| `process/` | Process/thread management |
| `public/` | Public platform API |
| `tts/` | Text-to-Speech |

### `src/shell/` - Platform Shells

UI integration for each platform:

| Directory | Platform | Description |
|-----------|----------|-------------|
| `efl/` | Linux, Tizen | EFL-based shell (primary) |
| `glfw/` | Cross-platform | GLFW OpenGL window |
| `x11/` | Linux | X11 native |
| `headless/` | Any | No UI, for testing |
| `glib/` | Linux | GLib integration |
| `libuv/` | Cross-platform | libuv event loop |
| `tcore_wl/` | Tizen | Wayland integration |
| `ecore_wl2/` | Tizen | EFL Wayland |
| `ecore_x/` | Linux | EFL X11 |
| `test/` | Testing | Test shell |

### `src/public/` - Public API Implementation

Implementation of the public embedding API:

| File | Purpose |
|------|---------|
| `LWEWebView.cpp` | WebView implementation |
| `LWEWorker.cpp` | Worker implementation |
| `LWEDelegateLoader.cpp` | Delegate pattern support |
| `bridge/` | Platform bridges |
| `delegate/` | Delegate implementations |

### `third_party/` - External Dependencies

| Directory | Library | Purpose |
|-----------|---------|---------|
| `escargot/` | Escargot | JavaScript engine |
| `clipper/` | Clipper | Polygon clipping |
| `giflib/` | GIF | GIF image support |
| `httplib/` | cpp-httplib | HTTP server |
| `libjpeg-turbo/` | libjpeg-turbo | JPEG images |
| `libpng/` | libpng | PNG images |
| `libwebp/` | libwebp | WebP images |
| `nanomsg/` | nanomsg | IPC messaging |
| `openssl/` | OpenSSL | TLS/SSL |
| `webrtc/` | WebRTC | Real-time communication |
| `googletest/` | GoogleTest | Testing framework |

### `build/` - Build Configuration

| Directory/File | Purpose |
|----------------|---------|
| `starfish.cmake` | Main library build |
| `starfish_public_api.cmake` | Public API build |
| `starfish_shell.cmake` | Shell executable build |
| `third_party.cmake` | Third-party dependencies |
| `android/` | Android AAR/APK build |
| `tizen/` | Tizen TPK build |
| `windows/` | Windows build |
| `test/` | Test build |

### `test/` - Test Suites

| Type | Description |
|------|-------------|
| `reftest/` | Reference tests (pixel comparison) |
| `web-platform-tests/` | W3C Web Platform Tests |
| `internal/` | Internal unit tests |

### `tool/` - Development Tools

| Tool | Purpose |
|------|---------|
| `test_runner.py` | Test execution |
| `lwe_compat/` | Compatibility checking |

## Entry Points

### Main Entry Point
- **`src/Starfish.cpp`** - Engine initialization
- **Shell-specific main()** - Platform entry in `src/shell/*/`

### Public API Entry Points
- **`LWE::LWE::Initialize()`** - Engine initialization
- **`LWE::WebView::Create()`** - Create web view
- **`LWE::WebContainer::Create()`** - Create render container

## Key File Patterns

### IDL Files (`*.idl`)
Web IDL interface definitions in `src/core/dom/`, `src/core/modules/`:
- Define JavaScript-exposed interfaces
- Processed by `binding_generator/` to generate C++ bindings

### Generated Files
Located in build output directory:
- `binding/generated/` - Generated bindings from IDL

## Build Output Structure

```
out/
└── efl/
    └── release/
        ├── bin/
        │   └── lightweight-web-engine    # Executable
        └── lib/                          # Shared libraries
```

## File Counts by Category

| Category | Approximate Count |
|----------|-------------------|
| C++ Source (.cpp) | ~800+ |
| C++ Headers (.h) | ~700+ |
| IDL Files (.idl) | ~417 |
| CMake Files | ~30 |
| Test Files | ~500+ |
