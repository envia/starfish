# Starfish Source Tree Analysis

## Directory Structure Overview

```
starfish/
├── binding_generator/       # JavaScript binding code generator
├── build/                   # Build configuration and CMake modules
├── compat/                   # Compatibility layer for different platforms
├── docs/                     # Documentation (existing and generated)
├── inc/                      # Public API headers
│   ├── LWEWebView.h         # Main web view API
│   ├── LWEWorker.h          # Worker API
│   └── PlatformIntegrationData.h
├── inspector/                # Web inspector integration
├── packaging/                # Packaging configuration (RPM, TPK, etc.)
├── src/                      # Main source code
│   ├── Starfish.cpp         # Engine entry point
│   ├── Starfish.h
│   ├── StarfishBase.h       # Base types and macros
│   ├── StarfishConfig.h     # Configuration defines
│   ├── StarfishInfo.h       # Version and build info
│   ├── StarfishPlatform.h   # Platform abstractions
│   ├── binding/             # JavaScript binding implementation
│   ├── browser/             # Browser shell implementation
│   ├── core/                # Core web engine components
│   ├── launcher/            # Application launcher
│   ├── platform/            # Platform-specific implementations
│   ├── public/              # Public API implementation
│   └── shell/               # Shell implementations (EFL, GLFW, etc.)
├── test/                     # Test suites and Web Platform Tests
├── third_party/              # Third-party dependencies
├── tool/                     # Development tools and scripts
└── CMakeLists.txt           # Main build configuration
```

## Critical Directories

### `src/core/` - Core Engine Components

The heart of the web engine, implementing web standards:

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `dom/` | Document Object Model implementation | Element, Node, Document classes |
| `layout/` | Layout engine | Box model, flexbox, grid |
| `style/` | CSS style resolution | Style.h, CSS properties |
| `animation/` | CSS animations and transitions | Animation controllers |
| `event/` | DOM Events | Event dispatch, event listeners |
| `fetch/` | Fetch API implementation | Network requests |
| `fileapi/` | File API | Blob, File, FileReader |
| `storage/` | Web Storage | localStorage, sessionStorage |
| `xml/` | XML parser | DOMParser, XML document |
| `csp/` | Content Security Policy | CSP evaluation |
| `page/` | Page management | Page lifecycle |
| `serialize/` | Serialization | HTML serialization |
| `modules/` | Web API modules | Geolocation, Media, etc. |
| `inspector/` | DevTools protocol | Inspector integration |
| `util/` | Utilities | Debug tools, tracing |
| `extra/` | Extensions | Additional features |

### `src/platform/` - Platform Abstraction Layer

Hardware and OS abstraction:

| Directory | Purpose |
|-----------|---------|
| `canvas/` | Canvas 2D rendering backend |
| `event/` | Platform event handling |
| `file/` | File system operations |
| `loader/` | Resource loading |
| `message_loop/` | Event loop implementation |
| `multimedia/` | Audio/Video playback |
| `network/` | Network stack |
| `process/` | Process management |
| `tts/` | Text-to-Speech |
| `public/` | Platform public interfaces |

### `src/shell/` - Shell Implementations

Different shell variants for various use cases:

| Shell | Description | Use Case |
|-------|-------------|----------|
| `efl/` | EFL (Enlightenment) shell | Tizen, Linux |
| `efl_headless/` | Headless EFL | Testing, CI |
| `glfw/` | GLFW shell | Desktop development |
| `x11/` | X11 shell | Linux desktop |

### `third_party/` - Third-Party Libraries

| Library | Version/Notes | Purpose |
|---------|---------------|---------|
| `escargot/` | Custom | JavaScript engine |
| `openssl/` | - | TLS/SSL cryptography |
| `libcurl/` | (external) | HTTP client |
| `libpng/` | - | PNG image decoding |
| `libjpeg-turbo/` | - | JPEG decoding |
| `libwebp/` | - | WebP image decoding |
| `giflib/` | - | GIF image decoding |
| `cairo/` | (external) | 2D graphics |
| `libtuv/` | - | Event loop (libuv-like) |
| `nanomsg/` | - | Messaging library |
| `nanomsgcpp/` | - | C++ wrapper for nanomsg |
| `httplib/` | - | HTTP server library |
| `googletest/` | - | Testing framework |
| `rapidxml/` | - | XML parser |
| `robin_map/` | - | Hash map implementation |
| `skia_matrix/` | - | Skia matrix operations |
| `clipper/` | - | Polygon clipping |
| `earcut.hpp/` | - | Polygon triangulation |
| `MP4Parse/` | - | MP4 parser |
| `webm/` | - | WebM container |
| `webrtc/` | - | WebRTC implementation |
| `deviceapi/` | - | Device APIs |
| `windows/` | - | Windows-specific code |

### `build/` - Build Configuration

| File | Purpose |
|------|---------|
| `config.cmake` | Build configuration |
| `version.cmake` | Version generation |
| `third_party.cmake` | Third-party build rules |
| `starfish.cmake` | Main build targets |
| `starfish_shell.cmake` | Shell build rules |
| `test/` | Test configuration |
| `android/` | Android build configuration |
| `windows/` | Windows build configuration |

### `tool/` - Development Tools

| Tool | Purpose |
|------|---------|
| `test_runner.py` | Test execution script |
| `lwe_compat/` | Compatibility checking tools |
| `gyp/` | Legacy GYP build (deprecated) |

## Entry Points

### Main Entry Point
- **File**: `src/Starfish.cpp`
- **Function**: Main engine initialization and lifecycle

### Shell Entry Points
- **EFL Shell**: `src/shell/efl/`
- **GLFW Shell**: `src/shell/glfw/`
- **Headless**: `src/shell/efl_headless/`

### Public API Entry Points
- **LWEWebView**: `inc/LWEWebView.h` - Main web view interface
- **LWEWorker**: `inc/LWEWorker.h` - Worker interface

## Build Outputs

```
out/
├── efl/
│   ├── release/
│   │   ├── bin/
│   │   │   └── lightweight-web-engine    # Main executable
│   │   └── lib/                          # Shared libraries
│   └── debug/
├── windows/
└── android/
```

## Key File Patterns

### IDL Files (JavaScript Bindings)
- Location: `src/**/*.idl`
- Purpose: Define JavaScript interfaces
- Count: ~417 IDL files

### Style Properties
- Location: `src/core/style/Style.h`
- Macro: `FOR_EACH_STYLE_ATTRIBUTE_*`

### HTML Elements
- Location: `src/core/dom/HTMLDocument.cpp`
- Macro: `DEFINE_KNOWN_ELEMENT`

## Test Structure

```
test/
├── reftest/              # Reftest suite
│   └── web-platform-tests/  # WPT tests
├── internal/             # Internal unit tests
└── vendor/               # Vendor-specific tests
```

## Configuration Files

| File | Purpose |
|------|---------|
| `CMakeLists.txt` | Main CMake configuration |
| `.clang-format` | Code formatting rules |
| `.gitlab-ci.yml` | GitLab CI pipeline |
| `.gitmodules` | Git submodules |
| `lightweight-web-engine.pc.in` | pkg-config template |
| `lightweight-web-engine.conf` | Engine configuration |
| `lightweight-web-engine.manifest` | Manifest file |
