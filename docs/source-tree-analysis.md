# Source Tree Analysis

## Directory Structure Overview

```
starfish/
├── binding/              # JavaScript binding layer
├── browser/              # Browser-level features (history, etc.)
├── build/                # CMake build configuration
├── compat/               # Platform compatibility layer
├── core/                 # Core web platform implementation
├── docs/                 # Documentation
├── inc/                  # Public API headers
├── inspector/            # DevTools inspector support
├── launcher/             # Worker entry points
├── packaging/            # Distribution packaging
├── platform/             # Platform abstraction layer
├── public/               # Public API implementation
├── shell/                # Platform-specific shell implementations
├── src/                  # Main source files (entry points)
├── test/                 # Test suites and test infrastructure
├── third_party/          # Third-party dependencies
└── tool/                 # Development and testing tools
```

## Critical Directories

### `/src` - Main Source Files

Entry point and core initialization code.

| File | Purpose |
|------|---------|
| `Starfish.cpp` | Main engine initialization and lifecycle |
| `Starfish.h` | Main engine class definition |
| `StarfishBase.h` | Base types and macros |
| `StarfishConfig.h` | Configuration includes |
| `StarfishPlatform.h` | Platform-specific defines |
| `StaticStrings.cpp` | Static string atomization |
| `StoragePathProvider.cpp` | Storage path management |

### `/core` - Core Web Platform

The heart of the web engine implementation.

```
core/
├── animation/        # CSS Animations & Transitions
│   ├── Animation.cpp
│   ├── AnimationApplier.cpp
│   ├── AnimationExecutor.cpp
│   ├── CubicBezier.cpp
│   └── TimingFunction.cpp
├── csp/              # Content Security Policy
├── dom/              # DOM implementation
│   ├── Attr.cpp
│   ├── CharacterData.cpp
│   ├── Comment.cpp
│   ├── CSS.cpp
│   ├── CustomElementRegistry.cpp
│   ├── DOMImplementation.cpp
│   ├── DOMMatrix.cpp
│   ├── DOMParser.cpp
│   ├── Document.cpp (main document implementation)
│   └── ... (many more DOM classes)
├── event/            # Event system
├── extra/            # Additional features
├── fetch/            # Fetch API
├── fileapi/          # File API (Blob, File, FileReader)
├── inspector/        # Inspector integration
├── layout/           # Layout engine
├── modules/          # Feature modules
│   ├── canvas/       # Canvas 2D API
│   ├── threading/    # Threading support
│   ├── worker/       # Web Workers
│   └── ...
├── page/             # Page-level features
├── serialize/        # Serialization
├── storage/          # Web Storage
├── style/            # CSS style system
├── util/             # Utility classes
└── xml/              # XML support
```

### `/binding` - JavaScript Binding Layer

Connects C++ objects to JavaScript via Escargot engine.

| File | Purpose |
|------|---------|
| `ScriptBindingInstance.cpp` | Main binding instance |
| `ScriptWrappable.cpp` | Base class for JS-exposed objects |
| `Builtin.idl` | IDL definitions for built-ins |
| `*CustomBinding.cpp` | Custom binding implementations |
| `WindowProxy.cpp` | Window proxy for security |

### `/platform` - Platform Abstraction Layer

Hardware and OS abstraction for portability.

```
platform/
├── canvas/           # Canvas backend (Cairo)
├── event/            # Event loop abstraction
├── file/             # File system operations
├── loader/           # Resource loading
├── message_loop/     # Message loop implementation
├── multimedia/       # Media playback
├── network/          # Network stack (curl-based)
├── process/          # Process management
├── public/           # Public platform interfaces
└── tts/              # Text-to-Speech
```

### `/shell` - Platform Shells

Platform-specific application shells.

```
shell/
├── efl/              # EFL/Enlightenment shell (Tizen)
├── glfw/             # GLFW shell (desktop)
├── x11/              # X11 shell
├── headless/         # Headless mode
├── glib/             # GLib event loop
├── libuv/            # libuv event loop
├── ecore_wl2/        # Wayland support
├── ecore_x/          # X11 support
├── tcore_wl/         # Tizen core Wayland
├── test/             # Test shell
├── android/          # Android shell
└── windows/          # Windows shell
```

### `/public` - Public API

Public API for embedding applications.

| File | Purpose |
|------|---------|
| `LWEWebView.cpp` | WebView public API |
| `LWEWorker.cpp` | Worker public API |
| `LWEDelegateLoader.cpp` | Delegate loading |
| `bridge/` | Bridge interfaces |
| `delegate/` | Delegate interfaces |

### `/inc` - Public Headers

| File | Purpose |
|------|---------|
| `LWEWebView.h` | WebView public header |
| `LWEWorker.h` | Worker public header |
| `PlatformIntegrationData.h` | Platform data structures |

### `/third_party` - Third-Party Dependencies

| Directory | Library | Purpose |
|-----------|---------|---------|
| `escargot/` | Escargot | JavaScript engine |
| `openssl/` | OpenSSL | TLS/SSL encryption |
| `libjpeg-turbo/` | libjpeg-turbo | JPEG decoding |
| `libpng/` | libpng | PNG decoding |
| `libwebp/` | libwebp | WebP decoding |
| `giflib/` | giflib | GIF decoding |
| `nanomsg/` | nanomsg | IPC for workers |
| `libwebsockets/` | libwebsockets | WebSocket protocol |
| `libtuv/` | libtuv | libuv portability |
| `webrtc/` | WebRTC | Real-time communication |
| `skia_matrix/` | Skia matrix | Matrix math |
| `clipper/` | Clipper | Polygon clipping |
| `MP4Parse/` | MP4Parse | MP4 parsing |
| `webm/` | libwebm | WebM parsing |
| `rapidxml/` | RapidXML | XML parsing |
| `robin_map/` | robin_map | Hash map |
| `googletest/` | GoogleTest | Testing framework |
| `httplib/` | cpp-httplib | HTTP client/server |

### `/build` - Build Configuration

CMake configuration files for different platforms and features.

| File | Purpose |
|------|---------|
| `starfish.cmake` | Main build configuration |
| `third_party.cmake` | Third-party library builds |
| `config.cmake` | Platform configuration |
| `starfish_public_api.cmake` | Public API build |
| `worker.cmake` | Worker build configuration |
| `android.cmake` | Android-specific config |
| `windows.cmake` | Windows-specific config |
| `version.cmake` | Version management |

### `/tool` - Development Tools

| File/Dir | Purpose |
|----------|---------|
| `test_runner.py` | Test execution script |
| `check_tidy.py` | Code style checker |
| `http_server.py` | Local test server |
| `imgdiff/` | Image comparison for pixel tests |
| `reftest/` | Reftest infrastructure |
| `gyp/` | Legacy GYP build support |
| `fonts/` | Test fonts |
| `coverage/` | Code coverage tools |

### `/test` - Test Suite

Web platform tests and internal tests.

```
test/
├── android/          # Android-specific tests
├── cairo/            # Cairo backend tests
├── tools/            # Test utilities
└── (web-platform-tests via submodule)
```

## Entry Points

### Main Entry Point
- **`src/Starfish.cpp`** - `Starfish::Starfish()` constructor initializes the engine

### Shell Entry Points
- **`shell/Shell.cpp`** - Shell abstraction
- **`shell/efl/`** - EFL application entry
- **`shell/glfw/`** - GLFW application entry

### Worker Entry Points
- **`launcher/ServiceWorkerEntry.cpp`** - Service Worker process entry
- **`launcher/SharedWorkerEntry.cpp`** - Shared Worker process entry

## Build Output Structure

```
out/
└── {backend}/
    └── {mode}/
        ├── bin/
        │   └── lightweight-web-engine    # Main executable
        └── lib/                          # Shared libraries
            ├── liblightweight-web-engine.so
            ├── libescargot.so
            ├── libcairo.so
            └── ...
```

## Key File Patterns

| Pattern | Description |
|---------|-------------|
| `*.idl` | Web IDL interface definitions |
| `*.cpp` / `*.h` | C++ source and headers |
| `*.cmake` | CMake build scripts |
| `*.py` | Python tooling scripts |
| `*.sh` | Shell scripts |
| `*.pc.in` | pkg-config template files |
