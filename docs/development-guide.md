# Development Guide

**Generated:** June 1, 2026

---

## Prerequisites

### Ubuntu Linux (Primary Platform)

```bash
# Core build tools
sudo apt-get install cmake autoconf automake libtool ninja

# Compilers and tools
sudo apt-get install clang-format

# Required libraries
sudo apt-get install \
    libcurl4-openssl-dev \
    libicu-dev \
    libcairo2-dev \
    libssl-dev \
    libturbojpeg \
    libturbojpeg0-dev \
    libgif-dev \
    libwebp-dev \
    libefl-all-dev

# Python for tools
sudo apt-get install python-pip
pip install Jinja2

# Optional: for zeromq
sudo apt-get install asciidoc xmlto
```

### Tizen

1. Install GBS (Git Build System)
2. Get gbs-conf:
   ```bash
   git clone https://github.sec.samsung.net/TizenPM/gbs-conf.git
   vi gbs-conf/gbs.conf
   # Fill out 'user' and 'passwd'
   ```

### Windows

- Visual Studio 2019
- CMake
- Windows 10 SDK (10.0.18362.0)

### Android

- Android NDK r16b
- Set `ANDROID_HOME` environment variable

---

## Getting the Source

```bash
git clone git@github.sec.samsung.net:lws/starfish.git
cd starfish
git submodule init
git submodule update
```

---

## Building

### Linux (EFL Shell)

```bash
# Configure
cmake -Bout/efl/release \
    -DMODE=release \
    -DHOST=linux \
    -DARCH=x64 \
    -DBACKEND=efl_cairo_gl \
    -DSHELL=efl \
    -DTARGETNAME=Starfish \
    -G Ninja

# Build
ninja -C out/efl/release starfish.executable
```

### Build Targets

| Target | Description |
|--------|-------------|
| `starfish.executable` | Build as executable |
| `starfish.shared_library` | Build as shared library (liblightweight-web-engine.so) |
| `starfish.static_library` | Build as static library (liblightweight-web-engine.a) |

### Build Options

| Option | Default | Values | Description |
|--------|---------|--------|-------------|
| `HOST` | linux | linux, tizen, windows | Target platform |
| `MODE` | release | debug, release | Build mode |
| `ARCH` | x64 | x64, arm | Target architecture |
| `BACKEND` | efl_cairo_gl | efl_cairo_gl, uv_cairo_gl, glib_cairo_gl | Graphics backend |
| `LTO` | 0 | 0, 1 | Link-time optimization |
| `ENABLE_DEBUGGER` | 0 | 0, 1 | Enable JavaScript debugger |
| `TARGETNAME` | lightweight-web-engine | any | Output name |
| `COVERAGE` | 0 | 0, 1 | Enable gcov coverage |
| `SHELL` | efl | efl, efl_headless, glfw, x11 | UI shell |
| `WEBGL` | 0 | 0, 1 | Enable WebGL |
| `WEBRTC` | 0 | 0, 1 | Enable WebRTC |
| `WORKER` | 0 | 0, 1 | Enable Web Workers |
| `SHARED_WORKER` | 0 | 0, 1 | Enable Shared Workers |
| `SERVICE_WORKER` | 0 | 0, 1 | Enable Service Workers |
| `IDB` | 0 | 0, 1 | Enable IndexedDB |
| `ENABLE_WASM` | 0 | 0, 1 | Enable WebAssembly |
| `ENABLE_CODECACHE` | 0 | 0, 1 | Enable code cache |
| `USE_FFMPEG_MEDIA_PLAYER` | 0 | 0, 1 | Use ffmpeg for media |

### Tizen Build

```bash
gbs -c ../gbs-conf/gbs.conf build -A armv7l -P profile.50std \
    --incremental --include-all \
    --define 'build_profile tv'
```

Build profiles: `tv`, `mobile`, `headless`, `wearable`, `all`

### Windows Build

```bash
# Configure
cmake -G "Visual Studio 16 2019" \
    -DCMAKE_SYSTEM_NAME=Windows \
    -DCMAKE_SYSTEM_VERSION:STRING="10.0" \
    -DCMAKE_SYSTEM_PROCESSOR=x86 \
    -DCMAKE_GENERATOR_PLATFORM=Win32,version=10.0.18362.0 \
    -DARCH=x86 \
    -DMODE=release \
    -Bout_windows/ \
    -DHOST=windows

# Build
cmake --build out_windows --config Release -j

# Build shell
msbuild build/windows/winform_shell/StarfishWinformShell/StarfishWinformShell.sln \
    /p:Platform="Any CPU"
```

### Android Build

```bash
cd build/android/apk
gradle build
```

---

## Running

### Basic Execution

```bash
./out/efl/release/bin/lightweight-web-engine 'path/to/file.html'
```

### With Options

```bash
# With specific dimensions
./out/efl/release/bin/lightweight-web-engine 'file.html' \
    --width=800 --height=600

# Pixel test mode
ELM_ENGINE="shot:file=capture.png" ./run.sh file.html \
    --pixel-test --width=800 --height=600
```

---

## Testing

### Test Runner

The main test runner is `tool/test_runner.py`:

```bash
# Run all tests
./tool/test_runner.py

# Specific test categories
./tool/test_runner.py dom_conformance
./tool/test_runner.py wpt_all
./tool/test_runner.py wpt_css_css21
./tool/test_runner.py wpt_css_backgrounds
./tool/test_runner.py vendor_test
./tool/test_runner.py bidi_test
./tool/test_runner.py internal_test
```

### Test Categories

| Category | Description |
|----------|-------------|
| `dom_conformance` | DOM conformance tests |
| `wpt_all` | All Web Platform Tests |
| `wpt_css_*` | CSS-specific WPT tests |
| `vendor_test` | Vendor-specific tests (Blink, WebKit, Gecko) |
| `bidi_test` | Bidirectional text tests |
| `internal_test` | Internal engine tests |

### Pixel Tests

```bash
# Install dependencies
ninja install_pixel_test_dep

# Run pixel test
ELM_ENGINE="shot:file=capture.png" ./run.sh file.html \
    --pixel-test --width=800 --height=600
```

### LWE Compatibility Checker

```bash
# Static check
tool/lwe_compat/check_static.py path/to/page-or-dir

# Runtime check
tool/lwe_compat/check_runtime.sh path/to/index.html --timeout=10
```

---

## Debugging

### JavaScript Debugging

If built with `ENABLE_DEBUGGER=1`, use the Escargot VSCode extension:

- [escargot-vscode-extension](https://github.com/Samsung/escargot-vscode-extension)

### Debug Build

```bash
cmake -Bout/efl/debug \
    -DMODE=debug \
    -DHOST=linux \
    -DARCH=x64 \
    -G Ninja
ninja -C out/efl/debug starfish.executable
```

### Address Sanitizer

```bash
cmake -Bout/efl/asan \
    -DMODE=debug \
    -DASAN=1 \
    -G Ninja
ninja -C out/efl/asan starfish.executable
```

---

## Code Style

### Guidelines

Follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) with project-specific conventions documented in `docs/Coding_Style_Guide.md`.

### Key Conventions

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: 80 characters max
- **Braces**: Always use braces, even for single statements
- **Naming**: camelCase for functions
- **Assertions**: Use `STARFISH_ASSERT()` for pointer validation

### Format Check

```bash
clang-format -i src/file.cpp
```

---

## Project Structure

See [Source Tree Analysis](./source-tree-analysis.md) for detailed directory structure.

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/core/` | Core engine (DOM, layout, style) |
| `src/platform/` | Platform abstraction |
| `src/binding/` | JavaScript bindings |
| `inc/` | Public API headers |
| `docs/` | Documentation |
| `test/` | Test suites |
| `tool/` | Development tools |

---

## Common Tasks

### Adding a New HTML Element

1. Create IDL file in `src/core/dom/`
2. Implement element class
3. Register in `HTMLDocument.cpp` using `DEFINE_KNOWN_ELEMENT`
4. Update `docs/Spec.md`

### Adding a New CSS Property

1. Add to `FOR_EACH_STYLE_ATTRIBUTE_*` macro in `src/core/style/Style.h`
2. Implement in `Style.cpp:applyProperty`
3. Update `docs/Spec.md`

### Adding a New JavaScript API

1. Create IDL file with interface definition
2. Implement C++ class inheriting `ScriptWrappable`
3. Use `DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS` macro
4. Update `docs/Spec.md`

---

## Troubleshooting

### Build Fails

1. Ensure all submodules are updated: `git submodule update --init --recursive`
2. Check all dependencies are installed
3. Clean build: `rm -rf out/ && cmake -Bout/...`

### Runtime Crashes

1. Use debug build for better stack traces
2. Check assertions with `STARFISH_ASSERT`
3. Use Address Sanitizer: `-DASAN=1`

### Test Failures

1. Check test output in console
2. Run specific test category in isolation
3. Verify pixel test reference images

---

## CI/CD

- **GitLab CI**: `.gitlab-ci.yml`
- **CI Dashboard**: http://10.113.138.181/overview/444

---

## Additional Resources

- [Project Overview](./project-overview.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Feature Specification](./Spec.md)
- [Coding Style Guide](./Coding_Style_Guide.md)
- [PWA Design](./PWA.md)
