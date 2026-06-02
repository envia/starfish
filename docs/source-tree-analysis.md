# Starfish Source Tree Analysis

**Generated:** 2026-06-01

---

## Root Directory Structure

```
starfish/                           # Project root
├── src/                            # Main source code ⭐
├── inc/                            # Public headers
├── build/                          # Build configuration
├── third_party/                    # External dependencies
├── test/                           # Test suites
├── docs/                           # Documentation
├── tool/                          # Development tools
├── binding_generator/             # IDL binding generator
├── inspector/                     # DevTools inspector
├── packaging/                     # Package definitions
├── compat/                        # Compatibility layer
├── CMakeLists.txt                 # Main build file
└── README.md                      # Project readme
```

---

## Source Directory (`src/`)

### Core Engine (`src/core/`)

```
src/core/
├── animation/          # CSS Animations & Transitions
│   └── CSSAnimation, KeyframeEffect, AnimationTimeline
├── dom/               # DOM Implementation ⭐
│   ├── Document, Element, Node
│   ├── HTML*Element classes
│   ├── Attr, CharacterData, Text
│   └── HTMLDocument.cpp (element factory)
├── event/             # Event System
│   ├── Event, MouseEvent, KeyboardEvent
│   ├── CustomEvent, EventTarget
│   └── EventDispatcher
├── layout/            # Layout Engine ⭐
│   ├── Block, Inline, Flexbox layout
│   ├── LineBox, BoxModel
│   └── LayoutTree
├── style/             # CSS Style System ⭐
│   ├── Style.h (property definitions)
│   ├── CSSStyleSheet, CSSRule
│   └── ComputedStyle
├── page/              # Page Management
│   ├── Page, Frame
│   └── NavigationController
├── storage/           # Storage APIs
│   ├── localStorage, sessionStorage
│   └── StorageEvent
├── fetch/             # Fetch API
│   ├── Request, Response, Headers
│   └── FetchController
├── csp/               # Content Security Policy
├── xml/               # XML Parser
├── serialize/         # HTML Serialization
├── util/              # Utilities
├── extra/             # Extended features
├── inspector/         # DevTools Protocol
├── modules/           # ES6 Modules
└── fileapi/           # File API
```

### Platform Layer (`src/platform/`)

```
src/platform/
├── canvas/            # Canvas 2D Rendering ⭐
│   ├── CanvasRenderingContext2D
│   └── PlatformCanvas implementation
├── event/             # Platform Events
│   └── MouseEvent, KeyEvent translation
├── file/              # File System
│   └── FileLoader, FileSystem
├── loader/            # Resource Loading
│   └── ImageLoader, ResourceLoader
├── message_loop/      # Event Loop
│   └── MessageLoop, TaskRunner
├── multimedia/        # Audio/Video
│   ├── MediaPlayer
│   └── AudioOutput
├── network/           # Networking ⭐
│   ├── HTTPClient
│   ├── WebSocket
│   └── CORS handling
├── process/           # Process Management
├── tts/               # Text-to-Speech
│   └── SpeechSynthesis
└── public/            # Platform Public API
```

### Browser Layer (`src/browser/`)

```
src/browser/
├── Browser.h          # Browser main class
├── BrowserPage.h      # Page management
├── BrowserSettings.h  # Configuration
└── Navigation.h       # Navigation controller
```

### Shell Layer (`src/shell/`)

```
src/shell/
├── efl/               # EFL Shell (Linux/Tizen) ⭐
├── glfw/              # GLFW Shell
├── x11/               # X11 Shell
└── headless/          # Headless (testing)
```

### Public API (`src/public/`)

```
src/public/
└── StarfishPublic.h   # Public API definitions
```

### Launcher (`src/launcher/`)

```
src/launcher/
└── Launcher.cpp       # Application launcher
```

### Binding (`src/binding/`)

```
src/binding/
└── (Generated from IDL)  # JavaScript bindings
```

---

## Include Directory (`inc/`)

```
inc/
├── LWEWebView.h       # WebView public API
├── LWEWorker.h        # Worker public API
└── PlatformIntegrationData.h
```

---

## Build Configuration (`build/`)

```
build/
├── config.cmake       # Main configuration
├── starfish.cmake     # Engine build rules
├── third_party.cmake  # Dependencies
├── version.cmake      # Version info
├── android.cmake      # Android build
├── windows.cmake       # Windows build
├── starfish_shell.cmake
├── worker.cmake        # Worker build
├── android/           # Android-specific
├── tizen/             # Tizen-specific
├── test/              # Test build
└── windows/           # Windows-specific
```

---

## Third-Party Dependencies (`third_party/`)

```
third_party/
├── escargot/          # JavaScript Engine ⭐
├── clipper/           # Polygon clipping
├── deviceapi/         # Device APIs
├── giflib/            # GIF decoding
├── googletest/        # Testing framework
├── httplib/           # HTTP library
├── libjpeg-turbo/     # JPEG decoding
├── libpng/            # PNG decoding
├── libtuv/            # libuv port
├── libwebp/           # WebP decoding
├── libwebsockets/     # WebSocket
├── MP4Parse/          # MP4 parsing
├── nanomsg/           # Messaging
├── openssl/           # TLS/SSL
├── rapidxml/          # XML parsing
├── robin_map/         # Hash map
├── skia_matrix/       # Matrix math
├── webm/              # WebM support
├── webrtc/            # WebRTC
└── windows/          # Windows deps
```

---

## Test Directory (`test/`)

```
test/
├── reftest/           # Reference tests ⭐
│   └── web-platform-tests/  # W3C WPT
├── unit/              # Unit tests
├── internal/          # Internal tests
└── (test resources)
```

---

## Tools Directory (`tool/`)

```
tool/
├── test_runner.py     # Test runner script ⭐
├── lwe_compat/        # Compatibility checker
│   ├── check_static.py
│   ├── check_runtime.sh
│   └── whitelist.json
└── (other utilities)
```

---

## Documentation Directory (`docs/`)

```
docs/
├── Spec.md            # API Specification ⭐
├── Coding_Style_Guide.md
├── PWA.md
├── RPi3_Guide.md
├── generator/         # Doc generator
├── guide/             # Guides
├── resources/         # Images
└── webpages/         # Web API docs
```

---

## Critical Files

| File | Purpose |
|------|---------|
| `CMakeLists.txt` | Main build configuration |
| `src/Starfish.cpp` | Engine initialization |
| `src/Starfish.h` | Main header |
| `src/StarfishConfig.h` | Build configuration |
| `src/core/dom/HTMLDocument.cpp` | Element factory |
| `src/core/style/Style.h` | CSS property definitions |
| `src/**/*.idl` | Web API definitions |

---

## Entry Points

| Entry Point | Location | Description |
|-------------|----------|-------------|
| `main()` | `src/shell/*/main.cpp` | Shell entry |
| `Starfish::create()` | `src/Starfish.cpp` | Engine creation |
| `LWEWebView` | `inc/LWEWebView.h` | WebView API |

---

## Generated Files

| Pattern | Source | Output |
|----------|--------|--------|
| `*Binding.cpp` | `.idl` files | `src/binding/` |
| `*Binding.h` | `.idl` files | `src/binding/` |

---

## Build Output

```
out/
└── release/
    ├── bin/lightweight-web-engine    # Executable
    └── lib/                          # Shared libraries
```

---

## Related Documentation

- [Project Overview](./project-overview.md)
- [Architecture](./architecture.md)
- [Development Guide](./development-guide.md)
