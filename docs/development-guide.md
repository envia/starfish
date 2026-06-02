# Starfish Development Guide

## Prerequisites

### Linux (Ubuntu 20.04+)

```bash
# Required packages
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev libgif-dev \
    cmake autoconf automake libtool ninja libwebp-dev libefl-all-dev

# Python for build tools
sudo apt-get install python-pip
pip install Jinja2

# Optional for ZeroMQ
sudo apt-get install asciidoc xmlto
```

### Tizen

- Install Tizen Studio
- Configure GBS (Git Build System)

### Windows

- Visual Studio 2019+
- CMake

### Android

- Android NDK r16b
- Android SDK

## Getting the Source

```bash
git clone <repository-url>
cd starfish
git submodule init
git submodule update
```

## Building

### Linux (EFL) - Release

```bash
cmake -Bout/efl/release \
    -DMODE=release \
    -DHOST=linux \
    -DARCH=x64 \
    -DBACKEND=efl_cairo_gl \
    -DSHELL=efl \
    -DTARGETNAME=Starfish \
    -G Ninja

ninja -C out/efl/release starfish.executable
```

### Linux (EFL) - Debug

```bash
cmake -Bout/efl/debug \
    -DMODE=debug \
    -DHOST=linux \
    -DARCH=x64 \
    -DBACKEND=efl_cairo_gl \
    -DSHELL=efl \
    -G Ninja

ninja -C out/efl/debug starfish.executable
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
| `HOST` | `linux`, `tizen`, `windows` | `linux` | Target platform |
| `MODE` | `debug`, `release` | `release` | Build mode |
| `BACKEND` | `efl_cairo_gl`, `uv_cairo_gl`, `glib_cairo_gl` | `efl_cairo_gl` | Graphics backend |
| `ARCH` | `x64`, `arm` | `x64` | Architecture |
| `LTO` | `0`, `1` | `0` | Link-time optimization |
| `COVERAGE` | `0`, `1` | `0` | Code coverage |
| `WEBGL` | `0`, `1` | `0` | WebGL support |
| `WEBRTC` | `0`, `1` | `0` | WebRTC support |
| `WORKER` | `0`, `1` | `0` | Web Workers |
| `SHARED_WORKER` | `0`, `1` | `0` | Shared Workers |
| `SERVICE_WORKER` | `0`, `1` | `0` | Service Workers |
| `IDB` | `0`, `1` | `0` | IndexedDB |
| `ENABLE_DEBUGGER` | `0`, `1` | `0` | JavaScript debugger |
| `ENABLE_TEST` | `0`, `1` | `0` | Build tests |
| `ENABLE_WASM` | `0`, `1` | `0` | WebAssembly |
| `SHELL` | `efl`, `efl_headless`, `glfw`, `x11` | `efl` | Shell type |
| `TARGETNAME` | string | `lightweight-web-engine` | Output name |

### Tizen Build (GBS)

```bash
# Configure GBS
git clone https://github.sec.samsung.net/TizenPM/gbs-conf.git
vi gbs-conf/gbs.conf  # Fill in credentials

# Build
gbs -c ../gbs-conf/gbs.conf build -A armv7l -P profile.50std \
    --incremental --include-all

# Profile-specific build
gbs build --define 'build_profile tv'    # TV profile
gbs build --define 'build_profile mobile' # Mobile profile
```

### Windows Build

```cmd
cmake -G "Visual Studio 16 2019" ^
    -DCMAKE_SYSTEM_NAME=Windows ^
    -DCMAKE_SYSTEM_VERSION="10.0" ^
    -DCMAKE_SYSTEM_PROCESSOR=x86 ^
    -DCMAKE_GENERATOR_PLATFORM=Win32 ^
    -DARCH=x86 ^
    -DMODE=release ^
    -Bout_windows ^
    -DHOST=windows

cmake --build out_windows --config Release -j
```

### Android Build

```bash
export ANDROID_HOME=$HOME/Android/Sdk
cd build/android/apk
gradle build
```

## Running

### Basic Execution

```bash
./out/efl/release/bin/lightweight-web-engine 'file:///path/to/page.html'
```

### With URL

```bash
./out/efl/release/bin/lightweight-web-engine 'https://example.com'
```

## Testing

### Prerequisites

```bash
ninja install_pixel_test_dep
```

### Run All Tests

```bash
./tool/test_runner.py
```

### Specific Test Suites

```bash
# DOM Conformance Test
./tool/test_runner.py dom_conformance

# Web Platform Tests
./tool/test_runner.py wpt_all
./tool/test_runner.py wpt_css_css21
./tool/test_runner.py wpt_canvas
./tool/test_runner.py wpt_pwa

# Vendor Tests
./tool/test_runner.py vendor_test
./tool/test_runner.py vendor_test_blink
./tool/test_runner.py vendor_test_webkit

# Bidi Test
./tool/test_runner.py bidi_test

# Internal Tests
./tool/test_runner.py internal_test
```

### Pixel Tests with Screenshot

```bash
# Capture screenshot
ELM_ENGINE="shot:file=capture.png" ./run.sh test.html --pixel-test \
    --width=800 --height=600
```

## JavaScript Debugging

When built with `ENABLE_DEBUGGER=1`:

1. Install [Escargot VSCode Extension](https://github.com/Samsung/escargot-vscode-extension)
2. Start Starfish with debugger enabled
3. Connect VSCode to the debugger port

## Code Style

### Formatting

The project uses clang-format. Format before committing:

```bash
clang-format -i <file>
```

### Style Guidelines

See [Coding_Style_Guide.md](./Coding_Style_Guide.md) for detailed conventions.

## Project Structure Conventions

| Directory | Purpose |
|-----------|---------|
| `src/core/` | Core web engine code |
| `src/platform/` | Platform abstraction |
| `src/shell/` | Platform UI integration |
| `src/public/` | Public API implementation |
| `src/binding/` | JavaScript bindings |
| `inc/` | Public headers |
| `test/` | Test suites |
| `docs/` | Documentation |

## Adding New Features

### Adding a New HTML Element

1. Create IDL file in `src/core/dom/` (e.g., `HTMLNewElement.idl`)
2. Create implementation files (`HTMLNewElement.cpp`, `HTMLNewElement.h`)
3. Register in `HTMLDocument.cpp` using `DEFINE_KNOWN_ELEMENT`
4. Run binding generator

### Adding a New CSS Property

1. Add to `FOR_EACH_STYLE_ATTRIBUTE` macro in `Style.h`
2. Implement parsing in `Style.cpp`
3. Implement layout effect in layout engine

### Adding a New JavaScript API

1. Create IDL file defining the interface
2. Implement C++ class inheriting from `ScriptWrappable`
3. Add custom bindings if needed
4. Run binding generator

## Troubleshooting

### Build Issues

**Missing submodules:**
```bash
git submodule update --init --recursive
```

**Missing dependencies:**
```bash
# Re-run third-party build
./build_third_party.sh
```

### Runtime Issues

**Blank page:**
- Check URL encoding
- Verify file exists (for file:// URLs)
- Check console for JavaScript errors

**Performance issues:**
- Enable LTO for release builds
- Adjust GC frequency: `LWE::LWE::SetGCFrequency()`

## CI/CD

CI infrastructure runs automated tests on:
- Code submission
- Pull requests
- Scheduled builds

See CI dashboard at project infrastructure.

## Contributing

1. Follow the coding style guide
2. Write tests for new features
3. Ensure all tests pass
4. Submit pull request with description

## Governance

All decisions are made by consensus, respecting the principles and rules of the community. See [Samsung Inner Source Governance](https://github.sec.samsung.net/InnerSource/SamsungInnerSourceProgram/blob/master/GettingStarted/Governance.md).
