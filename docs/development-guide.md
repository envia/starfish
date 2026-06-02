# Starfish Development Guide

## Prerequisites

### Ubuntu Linux (Primary Development Platform)

```bash
# Verified on Ubuntu 20.04
sudo apt-get install clang-format libcurl4-openssl-dev libicu-dev \
    libcairo2-dev libssl-dev libturbojpeg libturbojpeg0-dev libgif-dev \
    cmake autoconf automake libtool ninja libwebp-dev libefl-all-dev

# Python for build tools
sudo apt-get install python-pip
pip install Jinja2

# Optional: ZeroMQ dependencies
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

- Visual Studio 2019+
- CMake 3.15+
- Windows 10 SDK

### Android

- Android NDK r16b
- Android SDK
- Set `ANDROID_HOME` environment variable

## Getting the Source

```bash
git clone <repository-url>
cd starfish
git submodule init
git submodule update
```

## Building

### Linux (EFL + Cairo GL)

```bash
# Release build
cmake -Bout/efl/release -DMODE=release -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -DTARGETNAME=Starfish -G Ninja
ninja -C out/efl/release starfish.executable

# Debug build
cmake -Bout/efl/debug -DMODE=debug -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
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
| `HOST` | `linux`, `tizen` | `linux` | Target platform |
| `MODE` | `debug`, `release` | `release` | Build mode |
| `BACKEND` | `efl_cairo_gl`, `uv_cairo_gl`, `glib_cairo_gl` | `efl_cairo_gl` | Graphics backend |
| `ARCH` | `x64`, `arm` | `x64` | Target architecture |
| `LTO` | `0`, `1` | `0` | Link-time optimization |
| `ENABLE_DEBUGGER` | `0`, `1` | `0` | Enable JavaScript debugger |
| `TARGETNAME` | `Starfish`, `lightweight-web-engine` | `lightweight-web-engine` | Output name |
| `COVERAGE` | `0`, `1` | `0` | Enable gcov coverage |
| `SHELL` | `efl`, `efl_headless`, `glfw`, `x11` | `efl` | Shell type |
| `WEBGL` | `0`, `1` | `0` | Enable WebGL |
| `WEBRTC` | `0`, `1` | `0` | Enable WebRTC |
| `WORKER` | `0`, `1` | `0` | Enable Workers |
| `SERVICE_WORKER` | `0`, `1` | `0` | Enable Service Workers |
| `IDB` | `0`, `1` | `0` | Enable IndexedDB |

### Tizen Build (GBS)

```bash
gbs -c ../gbs-conf/gbs.conf build -A armv7l -P profile.50std \
    --incremental --include-all

# Build for specific profile
gbs build -A armv7l -P profile.50std --define 'build_profile tv'
```

### Windows Build

```cmd
cmake -G "Visual Studio 16 2019" -DCMAKE_SYSTEM_NAME=Windows ^
    -DCMAKE_SYSTEM_VERSION:STRING="10.0" ^
    -DCMAKE_SYSTEM_PROCESSOR=x86 ^
    -DCMAKE_GENERATOR_PLATFORM=Win32,version=10.0.18362.0 ^
    -DARCH=x86 -DMODE=release -Bout_windows/ -DHOST=windows

cmake --build out_windows --config Release -j
```

### Android Build

```bash
export ANDROID_HOME=$HOME/Android/Sdk
cd build/android/apk
gradle build
```

## Running

```bash
# Run with HTML file
./out/efl/release/bin/lightweight-web-engine 'path/to/file.html'

# Run with URL
./out/efl/release/bin/lightweight-web-engine 'https://example.com'
```

## Testing

### Prerequisites

```bash
# Install imgdiff tool for pixel tests
ninja install_pixel_test_dep
```

### Running Tests

```bash
# Run all tests
./tool/test_runner.py

# DOM Conformance Test
./tool/test_runner.py dom_conformance

# Web Platform Tests
./tool/test_runner.py wpt_all
./tool/test_runner.py wpt_css_css21
./tool/test_runner.py wpt_css_backgrounds
./tool/test_runner.py wpt_canvas

# Vendor Tests
./tool/test_runner.py vendor_test
./tool/test_runner.py vendor_test_blink
./tool/test_runner.py vendor_test_webkit

# Bidi Tests (on device)
./tool/test_runner.py bidi_test
```

### Pixel Tests with Screenshot Capture

```bash
# Starfish
ELM_ENGINE="shot:file=capture.png" ./run.sh test.html --pixel-test \
    --width=800 --height=600
```

## Debugging

### JavaScript Debugging

If debugger is enabled (`ENABLE_DEBUGGER=1`), use the Escargot VSCode extension:

- [escargot-vscode-extension](https://github.com/Samsung/escargot-vscode-extension)

### Trace Logging

Starfish provides trace macros for debugging (see `src/core/util/debug/Trace.h`):

```cpp
// Basic trace
TRACE(ID1, "message");

// Printf-style formatting
TRACE(ID2, "value: %d", value);

// Scope tracing (function call graph)
TRACE_SCOPE(ID3);
```

Enable traces via environment variable:

```bash
# Enable specific traces
export TRACE=ID1,ID2

# Enable all traces
export TRACE=*

# Enable all except specific
export TRACE=*,-ID1
```

### Debug Build

```bash
cmake -Bout/efl/debug -DMODE=debug -DHOST=linux -DARCH=x64 \
    -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja
ninja -C out/efl/debug starfish.executable
```

## Code Style

Follow the [Coding Style Guide](./Coding_Style_Guide.md). Key points:

- Use 4 spaces for indentation (no tabs)
- Max line length: 80 characters
- Follow Google C++ Style Guide as base
- Use `STARFISH_ASSERT` for assertions
- Use `NULLABLE` macro for nullable pointers

### Formatting

```bash
# Format code with clang-format
clang-format -i src/path/to/file.cpp
```

## Project Structure Conventions

### Header Guards

```cpp
#ifndef __StarfishClassName__
#define __StarfishClassName__
// ...
#endif
```

### Include Order

1. Related header
2. C system headers
3. C++ standard headers
4. Third-party library headers
5. Project headers

### Class Declaration

```cpp
class ClassName {
public:
    // Public members

protected:
    // Protected members

private:
    // Private members
};
```

## Common Development Tasks

### Adding a New Web API

1. Create IDL file in `src/core/dom/` or appropriate location
2. Implement the C++ class inheriting from `ScriptWrappable`
3. Add build configuration in CMakeLists.txt
4. Add tests in `test/` directory

### Adding a New CSS Property

1. Add property to `FOR_EACH_STYLE_ATTRIBUTE_*` macro in `Style.h`
2. Implement parsing in CSS parser
3. Implement application in `Style.cpp:applyProperty`
4. Add tests

### Adding a New HTML Element

1. Add element definition in `HTMLDocument.cpp` using `DEFINE_KNOWN_ELEMENT`
2. Create element class if needed
3. Add IDL file for JavaScript binding
4. Add tests

## CI/CD

- GitLab CI: `.gitlab-ci.yml`
- GBS for Tizen packaging

## Troubleshooting

### Build Issues

- **Missing submodules**: Run `git submodule update --init --recursive`
- **CMake version**: Ensure CMake 2.8.12 or later
- **EFL not found**: Install `libefl-all-dev` package

### Runtime Issues

- **Blank screen**: Check graphics backend compatibility
- **JavaScript errors**: Check Escargot engine compatibility
- **Missing features**: Verify build flags are enabled

## Additional Resources

- [Web Platform Tests](https://github.com/w3c/web-platform-tests)
- [Escargot JavaScript Engine](https://github.com/Samsung/escargot)
- [EFL Documentation](https://www.enlightenment.org/)
