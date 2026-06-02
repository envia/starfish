# Development Guide

## Prerequisites

### Ubuntu (20.04+)

```bash
# Required packages
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
  libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev libgif-dev \
  cmake autoconf automake libtool ninja libwebp-dev

# EFL backend (optional, for Tizen targets)
sudo apt-get install libefl-all-dev

# Python dependencies
pip install Jinja2
```

### Windows

1. Install Visual Studio 2019+ with C++ workload
2. Install CMake
3. Open "x86 Native Tools Command Prompt" for x86 builds

### Android

1. Install Android SDK and NDK r16b
2. Set `ANDROID_HOME` environment variable

## Building

### Quick Build (Linux)

```bash
# Clone and initialize submodules
git clone <repository-url>
cd starfish
git submodule update --init --recursive

# Configure and build
cmake -Bout/release -DMODE=release -DHOST=linux -DARCH=x64 \
  -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
ninja -C out/release starfish.executable
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
| `ARCH` | `x64`, `arm`, `x86` | `x64` | Target architecture |
| `SHELL` | `efl`, `efl_headless`, `glfw`, `x11` | - | Shell type |
| `TARGETNAME` | `Starfish`, `lightweight-web-engine` | `lightweight-web-engine` | Output name |
| `LTO` | `0`, `1` | `0` | Link-time optimization |
| `COVERAGE` | `0`, `1` | `0` | Code coverage |
| `WEBGL` | `0`, `1` | `0` | WebGL support |
| `WEBRTC` | `0`, `1` | `0` | WebRTC support |
| `WORKER` | `0`, `1` | `0` | Web Worker support |
| `SHARED_WORKER` | `0`, `1` | `0` | Shared Worker support |
| `SERVICE_WORKER` | `0`, `1` | `0` | Service Worker support |
| `IDB` | `0`, `1` | `0` | IndexedDB support |
| `ENABLE_DEBUGGER` | `0`, `1` | `0` | JavaScript debugger |
| `ENABLE_WASM` | `0`, `1` | `0` | WebAssembly support |
| `ENABLE_TEST` | `0`, `1` | `0` | Build tests |
| `ENABLE_PROFILE` | `0`, `1` | `0` | Profiling support |

### Platform-Specific Builds

#### Tizen (GBS)

```bash
# Install GBS
git clone https://github.sec.samsung.net/TizenPM/gbs-conf.git
# Configure gbs.conf with credentials

# Build
gbs -c ../gbs-conf/gbs.conf build -A armv7l -P profile.50std \
  --incremental --include-all \
  --define 'build_profile tv'
```

#### Windows

```cmd
cmake -G "Visual Studio 16 2019" -DCMAKE_SYSTEM_NAME=Windows ^
  -DCMAKE_SYSTEM_VERSION:STRING="10.0" ^
  -DCMAKE_SYSTEM_PROCESSOR=x86 ^
  -DCMAKE_GENERATOR_PLATFORM=Win32 ^
  -DARCH=x86 -DMODE=release -Bout_windows -DHOST=windows

cmake --build out_windows --config Release -j
```

#### Android

```bash
export ANDROID_HOME=$HOME/Android/Sdk
cd build/android/apk
gradle build
```

## Running

### Basic Execution

```bash
./out/release/bin/lightweight-web-engine 'path/to/file.html'
```

### With Options

```bash
# Pixel test mode
ELM_ENGINE="shot:file=capture.png" ./out/release/bin/lightweight-web-engine \
  'test.html' --pixel-test --width=800 --height=600
```

## Testing

### Run All Tests

```bash
./tool/test_runner.py
```

### Specific Test Suites

```bash
# DOM Conformance
./tool/test_runner.py dom_conformance

# Web Platform Tests
./tool/test_runner.py wpt_all
./tool/test_runner.py wpt_css_css21
./tool/test_runner.py wpt_pwa

# Vendor Tests
./tool/test_runner.py vendor_test
./tool/test_runner.py vendor_test_blink

# Bidi Tests (on device)
./tool/test_runner.py bidi_test
```

### Pixel Tests

```bash
# Install dependencies
ninja install_pixel_test_dep

# Run pixel test
ELM_ENGINE="shot:file=output.png" ./run.sh test.html --pixel-test
```

## Code Style

### Style Guide

Follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) with project-specific conventions documented in [Coding_Style_Guide.md](./Coding_Style_Guide.md).

### Key Conventions

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: Max 80 characters
- **Header Guards**: `__StarfishFileName__`
- **Braces**: Always use braces, even for single statements
- **Assertions**: Use `STARFISH_ASSERT()` for pointer validation

### Format Check

```bash
./tool/check_tidy.py
```

## Debugging

### JavaScript Debugging

1. Build with debugger enabled:
   ```bash
   cmake -Bout/debug -DMODE=debug -DENABLE_DEBUGGER=1 ...
   ```

2. Install [Escargot VSCode Extension](https://github.com/Samsung/escargot-vscode-extension)

3. Attach debugger from VSCode

### Memory Debugging

```bash
# Enable ASAN
cmake -Bout/debug -DMODE=debug -DASAN=1 ...

# Run with ASAN
./out/debug/bin/lightweight-web-engine test.html
```

### GC Debugging

The engine uses Boehm GC. For GC-related issues:

```cpp
// Force full GC
starfish->doFullGCWithoutSeeingStack();

// Print all reachable objects
starfish->printEveryReachableGCObjects();
```

## Project Structure Conventions

### Adding New Files

1. Create `.cpp` in appropriate `src/` subdirectory
2. Create `.h` header with proper guard
3. Update `CMakeLists.txt` if needed
4. Add IDL file for JavaScript-exposed interfaces

### IDL Files

Web IDL files define JavaScript interfaces:

```idl
[
  Exposed=(Window,Worker)
] interface MyInterface {
  void myMethod();
  attribute DOMString myAttribute;
};
```

IDL files are processed by the binding generator to create C++ bindings.

## Common Tasks

### Adding a New CSS Property

1. Add property to `src/core/style/Style.h` (FOR_EACH_STYLE_ATTRIBUTE macro)
2. Implement parsing in `src/core/style/Style.cpp`
3. Implement layout in appropriate layout class

### Adding a New DOM Interface

1. Create IDL file in `src/core/dom/` or appropriate location
2. Implement C++ class inheriting from `ScriptWrappable`
3. Add custom bindings if needed
4. Register in binding generator

### Adding a New Platform Backend

1. Create platform defines in `StarfishPlatform.h`
2. Implement platform interfaces in `platform/`
3. Add CMake configuration in `build/`
4. Create shell implementation in `shell/`

## CI/CD

The project uses GitLab CI (`.gitlab-ci.yml`) for continuous integration.

- CI Dashboard: http://10.113.138.181/overview/444

## Troubleshooting

### Build Issues

| Problem | Solution |
|---------|----------|
| Missing submodules | `git submodule update --init --recursive` |
| CMake version error | Update CMake to 2.8.12+ |
| Missing dependencies | Install required packages |

### Runtime Issues

| Problem | Solution |
|---------|----------|
| Blank page | Check HTML encoding (must be UTF-8) |
| JS errors | Enable debugger to trace |
| Missing features | Check build flags (WEBGL, WORKER, etc.) |
