# Source Tree Analysis

**Generated:** June 1, 2026

---

## Project Root Structure

```
starfish/
├── .clang-format          # Code formatting configuration
├── .gitignore             # Git ignore rules
├── .gitlab-ci.yml         # GitLab CI/CD configuration
├── .gitmodules            # Git submodules configuration
├── CHANGES                # Change log
├── CMakeLists.txt         # Main CMake configuration ⭐ ENTRY POINT
├── COPYRIGHT              # Copyright notice
├── LICENSE.*              # Multiple license files
├── makefile               # Legacy makefile
├── project_config_clang   # Clang configuration
├── README.md              # Project documentation
├── Starfish               # Binary symlink
│
├── _bmad/                 # BMad methodology configuration
├── _bmad-output/          # BMad output artifacts
├── binding_generator/      # JavaScript binding generator
├── build/                 # Build configuration files
├── compat/                # Compatibility layer
├── docs/                  # Documentation ⭐
├── inc/                   # Public API headers ⭐
├── inspector/             # Inspector tools
├── out/                   # Build output directory
├── packaging/             # Packaging configuration
├── src/                   # Main source code ⭐
├── test/                  # Test suites
├── third_party/           # Third-party libraries
└── tool/                  # Development tools
```

---

## Source Directory (`src/`)

The main source code is organized into logical layers:

```
src/
├── Starfish.cpp           # Main entry point ⭐
├── Starfish.h             # Main header
├── StarfishBase.h         # Base definitions
├── StarfishConfig.h       # Configuration
├── StarfishInfo.h         # Version info
├── StarfishPlatform.h     # Platform definitions
├── StaticStrings.cpp/h    # Static string pool
├── StoragePathProvider.*  # Storage path management
├── streamline_annotate.h  # Profiling annotations
│
├── binding/               # JavaScript bindings (IDL-generated)
├── browser/               # Browser-level functionality
├── core/                  # Core engine components ⭐
├── launcher/              # Application launcher
├── platform/              # Platform abstraction layer ⭐
├── public/                # Public API implementations
└── shell/                 # UI shell implementations
```

---

## Core Engine (`src/core/`)

The heart of the web engine:

```
src/core/
├── animation/             # CSS animations and transitions
├── csp/                   # Content Security Policy
├── dom/                   # DOM implementation ⭐
│   ├── HTMLDocument.cpp   # HTML document handling
│   ├── Element.cpp        # Element base class
│   └── ...                # Many DOM classes
├── event/                 # Event handling
├── extra/                 # Additional features
├── fetch/                 # Fetch API
├── fileapi/               # File API (Blob, File, FileReader)
├── inspector/             # Inspector integration
├── layout/                 # Layout engine ⭐
├── modules/               # ES6 modules
├── page/                  # Page management
├── serialize/             # Serialization
├── storage/               # Web Storage (localStorage, sessionStorage)
├── style/                 # CSS style engine ⭐
│   ├── Style.h            # Style definitions
│   └── Style.cpp          # Style application
├── util/                  # Utility functions
└── xml/                   # XML parser
```

---

## Platform Layer (`src/platform/`)

Platform abstraction for cross-platform support:

```
src/platform/
├── canvas/                # Canvas rendering
├── event/                 # Platform events
├── file/                  # File system operations
├── loader/                # Resource loading
├── message_loop/          # Event loop
├── multimedia/            # Media playback
├── network/               # Network operations
├── process/               # Process management
├── public/                # Public platform API
└── tts/                   # Text-to-speech
```

---

## Public API (`inc/`)

Public headers for external consumers:

```
inc/
├── LWEWebView.h           # WebView public API ⭐
├── LWEWorker.h            # Worker public API
└── PlatformIntegrationData.h  # Platform integration
```

---

## Build Configuration (`build/`)

CMake build files for different platforms:

```
build/
├── android.cmake          # Android build config
├── config.cmake           # General configuration
├── starfish.cmake         # Main build config
├── starfish_public_api.cmake  # Public API build
├── starfish_shell.cmake   # Shell build
├── starfish_shell_tpk.cmake  # Tizen package
├── starfish_uwe_service.cmake  # UWE service
├── starfish_uwe_tpk.cmake # UWE Tizen package
├── third_party.cmake      # Third-party deps
├── version.cmake          # Version management
├── windows.cmake          # Windows build config
├── worker.cmake           # Worker build
├── worker_launcher.cmake  # Worker launcher
├── worker_public_api.cmake # Worker public API
│
├── android/               # Android-specific build
├── test/                  # Test build config
├── tizen/                 # Tizen-specific build
└── windows/               # Windows-specific build
```

---

## Third-Party Libraries (`third_party/`)

Bundled dependencies:

```
third_party/
├── clipper/               # Polygon clipping
├── deviceapi/             # Device API
├── earcut.hpp/            # Polygon triangulation
├── escargot/              # JavaScript engine ⭐
├── giflib/                # GIF support
├── googletest/            # Testing framework
├── httplib/               # HTTP library
├── libjpeg-turbo/         # JPEG support
├── libpng/                # PNG support
├── libtuv/                # libuv port
├── libwebp/               # WebP support
├── libwebsockets/         # WebSocket
├── MP4Parse/              # MP4 parser
├── nanomsg/               # Messaging
├── nanomsgcpp/            # C++ nanomsg wrapper
├── openssl/               # TLS/SSL
├── rapidxml/              # XML parser
├── robin_map/             # Hash map
├── skia_matrix/           # Skia matrix
├── webm/                  # WebM support
├── webrtc/                # WebRTC
└── windows/               # Windows-specific libs
```

---

## Test Suite (`test/`)

Comprehensive testing infrastructure:

```
test/
├── README.md              # Test documentation
├── android/               # Android tests
├── cairo/                 # Cairo tests
└── tools/                 # Test tools
```

---

## Tools (`tool/`)

Development and testing tools:

```
tool/
├── test_runner.py         # Main test runner ⭐
├── lwe_compat/            # LWE compatibility checker
│   ├── check_static.py    # Static analysis
│   ├── check_runtime.sh   # Runtime checker
│   └── whitelist.json     # Feature whitelist
└── ...                    # Other tools
```

---

## Documentation (`docs/`)

Project documentation:

```
docs/
├── Spec.md                # Complete feature specification ⭐
├── Coding_Style_Guide.md  # C++ style guide
├── PWA.md                 # PWA design
├── RPi3_Guide.md          # Raspberry Pi guide
├── project-overview.md    # Project overview (generated)
├── source-tree-analysis.md # This file (generated)
├── development-guide.md   # Development guide (generated)
│
├── generator/             # Doc generator
├── guide/                 # Guides
│   └── debug_utilities.md
├── resources/             # Images and diagrams
└── webpages/              # Generated web docs
```

---

## Critical Files for Understanding

| File | Purpose |
|------|---------|
| `CMakeLists.txt` | Build configuration entry point |
| `src/Starfish.cpp` | Main entry point |
| `src/core/dom/HTMLDocument.cpp` | HTML element registration |
| `src/core/style/Style.h` | CSS property definitions |
| `src/**/*.idl` | JavaScript interface definitions |
| `inc/LWEWebView.h` | Public API |
| `docs/Spec.md` | Feature specification |

---

## Build Output (`out/`)

Generated build artifacts:

```
out/
├── efl/
│   └── release/
│       ├── bin/
│       │   └── lightweight-web-engine  # Main binary
│       └── lib/                        # Shared libraries
└── ...
```

---

## Key Patterns

### IDL Files
- Location: `src/**/*.idl`
- Purpose: Define JavaScript interfaces
- Extended attributes: `[Unimplemented]`, `[NoInterfaceObject]`, `[STARFISH_ENABLE_*]`

### Build Flags
- Defined in: `CMakeLists.txt`
- Pattern: `STARFISH_ENABLE_*` macros
- Control: Feature availability at compile time

### Platform Abstraction
- Pattern: Interface in `src/platform/public/`
- Implementation: Platform-specific in `src/platform/*/`
- Enables: Cross-platform support (Linux, Tizen, Windows, Android)
