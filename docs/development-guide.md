# Starfish Development Guide

**Generated:** 2026-06-01

---

## Prerequisites

### Linux (Ubuntu 20.04+)

```bash
# Required packages
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev \
    libgif-dev cmake autoconf automake libtool ninja \
    libwebp-dev libefl-all-dev

# Python for build tools
sudo apt-get install python-pip
pip install Jinja2

# Optional: ZeroMQ dependencies
sudo apt-get install asciidoc xmlto
```

### Tizen

```bash
# Install GBS (Git Build System)
git clone https://github.sec.samsung.net/TizenPM/gbs-conf.git
vi gbs-conf/gbs.conf  # Configure credentials
```

### Windows

- Visual Studio 2019+
- CMake 3.15+

### Android

```bash
export ANDROID_HOME=$HOME/Android/Sdk
# Requires android-ndk-r16b
```

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

### Linux Build

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

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `HOST` | linux, tizen, windows | linux | Target platform |
| `MODE` | debug, release | release | Build mode |
| `BACKEND` | efl_cairo_gl, uv_cairo_gl, glib_cairo_gl | efl_cairo_gl | Graphics backend |
| `ARCH` | x64, arm | x64 | Architecture |
| `SHELL` | efl, efl_headless, glfw, x11 | efl | Shell type |
| `TARGETNAME` | string | lightweight-web-engine | Output name |
| `LTO` | 0, 1 | 0 | Link-time optimization |
| `COVERAGE` | 0, 1 | 0 | Code coverage |

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
| `ENABLE_TEST` | 0 | Build tests |
| `ENABLE_PROFILE` | 0 | Profiling support |
| `USE_FFMPEG_MEDIA_PLAYER` | 0 | FFmpeg media backend |

### Tizen Build (GBS)

```bash
cd starfish
gbs -c ../gbs-conf/gbs.conf build -A armv7l -P profile.50std --incremental --include-all

# Profile-specific builds
gbs build --define 'build_profile tv'      # TV profile
gbs build --define 'build_profile mobile'   # Mobile profile
gbs build --define 'build_profile wearable' # Wearable profile
```

### Windows Build

```cmd
cmake -G "Visual Studio 16 2019" ^
    -DCMAKE_SYSTEM_NAME=Windows ^
    -DCMAKE_SYSTEM_VERSION:STRING="10.0" ^
    -DCMAKE_SYSTEM_PROCESSOR=x86 ^
    -DCMAKE_GENERATOR_PLATFORM=Win32 ^
    -DARCH=x86 -DMODE=release ^
    -Bout_windows/ -DHOST=windows

cmake --build out_windows --config Release -j
```

### Android Build

```bash
cd build/android/apk
gradle build
```

---

## Running

```bash
# Basic run
./out/release/lightweight-web-engine 'path/to/file.html'

# With options
./out/release/lightweight-web-engine --width=800 --height=600 'path/to/file.html'
```

---

## Testing

### Test Runner

```bash
# Run all tests
./tool/test_runner.py

# Specific test suites
./tool/test_runner.py dom_conformance    # DOM tests
./tool/test_runner.py wpt_all            # Web Platform Tests
./tool/test_runner.py vendor_test        # Vendor tests
./tool/test_runner.py bidi_test          # Bidi tests
./tool/test_runner.py internal_test      # Internal tests

# WPT sub-categories
./tool/test_runner.py wpt_css_css21
./tool/test_runner.py wpt_css_backgrounds
./tool/test_runner.py wpt_css_flexbox
```

### Pixel Tests

```bash
# Install dependencies
ninja install_pixel_test_dep

# Capture screenshot
ELM_ENGINE="shot:file=capture.png" ./run.sh test.html --pixel-test --width=800 --height=600
```

### Compatibility Checking

```bash
# Static check (fast)
tool/lwe_compat/check_static.py path/to/page

# Runtime check
tool/lwe_compat/check_runtime.sh path/to/index.html --timeout=10
```

---

## Code Style

See [Coding Style Guide](./Coding_Style_Guide.md) for full details.

### Key Points

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Max 80 characters
- **Braces**: Always use braces, even for single statements
- **Naming**: camelCase for functions
- **Assertions**: Use `STARFISH_ASSERT(ptr != nullptr)`
- **No RTTI**: Do not use Run-Time Type Information
- **C++11**: Encouraged

### Example

```cpp
// Correct style
if (condition) {
    doSomething();
}

// Function declaration
returnType functionName(int arg1, int arg2)
{
    STARFISH_ASSERT(arg1 != nullptr);
    return result;
}
```

---

## Debugging

### Enable Debugger

```bash
cmake -Bout/debug -DENABLE_DEBUGGER=1 -DMODE=debug ...
```

### VSCode Extension

Use the [Escargot VSCode Extension](https://github.com/Samsung/escargot-vscode-extension) for JavaScript debugging.

### Debug Utilities

See [Debug Utilities Guide](./guide/debug_utilities.md).

---

## Project Structure Conventions

| Directory | Purpose |
|-----------|---------|
| `src/core/` | Core engine (DOM, layout, style) |
| `src/platform/` | Platform abstraction |
| `src/browser/` | Browser functionality |
| `src/shell/` | Application shells |
| `src/public/` | Public API |
| `inc/` | Public headers |
| `test/` | Test suites |
| `tool/` | Development tools |

---

## Adding New Features

### New HTML Element

1. Create IDL file in `src/core/dom/`
2. Implement element class
3. Register in `HTMLDocument.cpp`
4. Add tests

### New CSS Property

1. Add to `FOR_EACH_STYLE_ATTRIBUTE_*` macro in `src/core/style/Style.h`
2. Implement in `Style.cpp:applyProperty`
3. Add tests

### New Web API

1. Create IDL file with interface definition
2. Implement binding
3. Add build flag if optional
4. Document in `docs/Spec.md`

---

## Common Tasks

### Clean Build

```bash
rm -rf out/
# Re-run cmake and build
```

### Update Dependencies

```bash
git submodule update --init --recursive
```

### Check Code Style

```bash
clang-format --style=file -i src/**/*.cpp
```

---

## CI/CD

- CI Server: http://10.113.138.181/overview/444
- GitLab CI: `.gitlab-ci.yml`

---

## Troubleshooting

### Build Fails

1. Check all submodules are initialized
2. Verify all dependencies are installed
3. Check CMake cache for stale values

### Runtime Crashes

1. Enable debug build: `-DMODE=debug`
2. Enable assertions (default in debug)
3. Check for nullptr issues

### Test Failures

1. Update test baseline if expected
2. Check for platform-specific issues
3. Verify test environment setup

---

## Related Documentation

- [Project Overview](./project-overview.md)
- [Architecture](./architecture.md)
- [API Specification](./Spec.md)
- [Coding Style Guide](./Coding_Style_Guide.md)
