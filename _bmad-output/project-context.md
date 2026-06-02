---
project_name: Starfish
user_name: Joonhyung
date: 2026-06-02
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'code_quality', 'workflow_rules', 'critical_rules']
status: 'complete'
rule_count: 45
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

### Core Technologies

| Category | Technology | Version/Notes |
|----------|-----------|---------------|
| **Language** | C++ | C++11 standard |
| **Build System** | CMake | 2.8.12+ with Ninja generator |
| **JavaScript Engine** | Escargot | ES6+ support |
| **Graphics** | Cairo | 2D vector graphics |
| **Garbage Collection** | Boehm GC | Conservative GC |
| **Unicode** | ICU | Internationalization |
| **Network** | libcurl | HTTP/HTTPS |
| **SSL/TLS** | OpenSSL | Secure connections |

### Key Dependencies

- `tsl/robin_map`, `tsl/robin_set` - High-performance hash maps/sets
- `libjpeg-turbo`, `libpng`, `libwebp` - Image decoding
- `nanomsg` - IPC for workers
- `libwebsockets` - WebSocket protocol

### Platform Backends

| Backend | Graphics | Event Loop | Window System |
|---------|----------|------------|---------------|
| `efl_cairo_gl` | Cairo + GL | GLib | EFL/Elementary (Tizen) |
| `uv_cairo_gl` | Cairo + GL | libuv | GLFW |
| `glib_cairo_gl` | Cairo + GL | GLib | X11 |
| `efl_headless` | Mock | GLib | None |
| `glib_headless` | Mock | GLib | None |

### Build Options (CMake)

| Option | Default | Description |
|--------|---------|-------------|
| `WEBGL` | 0 | WebGL support |
| `WEBRTC` | 0 | WebRTC support |
| `WORKER` | 0 | Web Worker support |
| `SERVICE_WORKER` | 0 | Service Worker support |
| `IDB` | 0 | IndexedDB support |
| `ENABLE_DEBUGGER` | 0 | JS debugger support |
| `ENABLE_WASM` | 0 | WebAssembly support |

---

## Critical Implementation Rules

### Language-Specific Rules (C++)

#### Memory Management (Boehm GC)

- **All GC-managed objects must inherit from `gc` class**
- Use `GCVector<T>`, `GCUnorderedMap<K,V>`, `GCUnorderedSet<T>` for GC-aware containers
- Use `GC_MALLOC` family for GC allocations - never use raw `new char[N]` for arrays
- Call `STARFISH_ASSERT(ptr != nullptr)` before dereferencing non-nullable pointers

#### Coding Style

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 80 characters
- **Header guards**: `__StarfishFileName__` format
- **Braces**: Always use braces, even for single statements
- **Constructor initializers**: Separate lines, comma-aligned

```cpp
Dog::Dog(String name, Breed breed)
    : Animal()
    , m_name(name)
    , m_breed(breed)
{
}
```

#### Explicit Conditions (CRITICAL)

```cpp
// ✅ CORRECT - explicit expressions
if (ptr != nullptr) { ... }
if (isLoaded() == true) { ... }
if (strlen(str) > 0) { ... }
if (count != 0) { ... }

// ❌ WRONG - implicit conditions
if (ptr) { ... }
if (isLoaded()) { ... }
if (strlen(str)) { ... }
if (count) { ... }
```

**Exception**: Boolean-identifiable functions can omit right operand:
- Functions named `isXXX()`, `hasXXX()`, `didXXX()`, `shouldXXX()`, `inXXX()`, `flagXXX()`

#### Assertions

| Macro | Use Case |
|-------|----------|
| `STARFISH_ASSERT(cond)` | Debug builds only |
| `STARFISH_RELEASE_ASSERT(cond)` | Release builds (aborts on failure) |
| `STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE()` | Unreachable code paths |

#### NULLABLE Pattern

- Mark nullable pointers: `NULLABLE Object* func(NULLABLE Object* param);`
- Use `Nullable<T>` template **only for JavaScript binding interfaces**
- Never use `String*` as nullptr - use `String::emptyString` instead
- Always check nullable pointers before use: `if (ptr != nullptr) { ... }`

#### Forbidden Patterns

- ❌ **No RTTI** (Run-Time Type Information)
- ❌ **No `try-catch`** except for throwing `DOMException`
- ❌ **No constructor delegation** (for embedded compatibility)
- ❌ **No `new char[N]`** - use GC allocation

### Framework-Specific Rules

#### Layered Architecture

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Public API** | `public/`, `inc/` | Embedder interface (`LWEWebView`, `LWEWorker`) |
| **Shell** | `shell/` | Platform-specific hosting (EFL, GLFW, X11) |
| **Core Engine** | `core/` | Web platform (DOM, Style, Layout, Animation) |
| **Binding** | `binding/` | JavaScript/C++ bridge |
| **Platform** | `platform/` | OS/hardware abstraction |

#### JavaScript Bindings (IDL)

- All JS-exposed classes **must inherit from `ScriptWrappable`**
- Define interfaces in `.idl` files → binding generator creates C++ bindings
- Custom bindings go in `*CustomBinding.cpp` files
- Use `ScriptBindingInstance` for JS execution context

**IDL Example:**
```idl
[Exposed=(Window,Worker)] interface MyInterface {
    void myMethod();
    attribute DOMString myAttribute;
};
```

#### DOM Implementation Patterns

- **Node hierarchy**: `Node` → `Element`/`CharacterData`/`Document`
- Parent-child references with GC management
- Use macro: `DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(ClassName)`

#### Platform Abstraction Pattern

```cpp
// Abstract interface in platform/public/
class CanvasContext {
public:
    virtual void drawRect(...) = 0;
};

// Implementation in platform/canvas/
class CairoCanvasContext : public CanvasContext { ... };
```

#### Adding New Features

**New DOM Interface:**
1. Create `.idl` file with interface definition
2. Implement C++ class inheriting from `ScriptWrappable`
3. Add custom bindings in `*CustomBinding.cpp` if needed
4. Register in binding generator

**New CSS Property:**
1. Add to `FOR_EACH_STYLE_ATTRIBUTE` macro in `Style.h`
2. Implement parsing in `Style.cpp`
3. Implement layout handling in appropriate layout class

**New Platform Backend:**
1. Define platform macros in `StarfishPlatform.h`
2. Implement platform interfaces in `platform/`
3. Add CMake configuration in `build/`
4. Create shell implementation in `shell/`

### Testing Rules

#### Test Runner

```bash
# Run all tests
./tool/test_runner.py

# Specific test suites
./tool/test_runner.py dom_conformance
./tool/test_runner.py wpt_all
./tool/test_runner.py wpt_css_css21
./tool/test_runner.py wpt_pwa
./tool/test_runner.py vendor_test
./tool/test_runner.py vendor_test_blink
```

#### Test Suites

| Suite | Description |
|-------|-------------|
| `dom_conformance` | DOM API conformance tests |
| `wpt_all` | All Web Platform Tests |
| `wpt_css_css21` | CSS 2.1 tests |
| `wpt_pwa` | PWA (Service Worker) tests |
| `vendor_test` | Vendor-specific tests |
| `bidi_test` | Bi-directional text tests (on device) |

#### Pixel Tests

```bash
# Install dependencies
ninja install_pixel_test_dep

# Run pixel test
ELM_ENGINE="shot:file=output.png" ./run.sh test.html --pixel-test
```

#### Build with Tests

Enable tests in CMake configuration:
```bash
cmake -Bout/debug -DMODE=debug -DENABLE_TEST=1 ...
```

#### Format Check

```bash
./tool/check_tidy.py
```

### Code Quality & Style Rules

#### Style Guide

Follows [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html) with project-specific conventions.

#### Formatting

| Rule | Requirement |
|------|-------------|
| **Indentation** | 4 spaces (no tabs) |
| **Line length** | Max 80 characters |
| **Header guards** | `__StarfishFileName__` format |
| **Braces** | Always use, even for single statements |
| **Empty lines** | 1 between functions in `.cpp`, 0 in `.h` for grouped functions |

#### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | camelCase | `myFunction()` |
| Member variables | `m_` prefix | `m_name` |
| Macros | UPPER_CASE with `STARFISH_` prefix | `STARFISH_ASSERT` |

#### Comments

- Use `//` style (preferred over `/* */`)
- Write comments in `.cpp` files, not headers
- Comments are optional - prefer clear function names
- Document: unusual behaviors, pre/post conditions, non-obvious logic

#### Include Rules

- Include headers only in `.cpp` files when possible
- Use forward declarations in headers
- Allowed includes in headers: class inheritance, member as instance
- Named parameters in function declarations

```cpp
// ✅ CORRECT
returnType functionName(int arg1, int arg2);

// ❌ WRONG
returnType functionName(int, int);
```

### Development Workflow Rules

#### Build Workflow

```bash
# Clone and initialize
git clone <repository-url>
cd starfish
git submodule update --init --recursive

# Configure (Linux example)
cmake -Bout/release -DMODE=release -DHOST=linux -DARCH=x64 \
  -DBACKEND=efl_cairo_gl -DSHELL=efl -G Ninja

# Build
ninja -C out/release starfish.executable
```

#### Build Targets

| Target | Description |
|--------|-------------|
| `starfish.executable` | Build as executable |
| `starfish.shared_library` | Build as shared library (liblightweight-web-engine.so) |
| `starfish.static_library` | Build as static library (liblightweight-web-engine.a) |

#### Platform-Specific Builds

**Tizen (GBS):**
```bash
gbs -c ../gbs-conf/gbs.conf build -A armv7l -P profile.50std \
  --incremental --include-all --define 'build_profile tv'
```

**Windows:**
```cmd
cmake -G "Visual Studio 16 2019" -DARCH=x86 -DMODE=release -DHOST=windows -Bout_windows
cmake --build out_windows --config Release -j
```

**Android:**
```bash
export ANDROID_HOME=$HOME/Android/Sdk
cd build/android/apk && gradle build
```

#### Debugging

| Mode | CMake Flag | Description |
|------|------------|-------------|
| JS Debugger | `-DENABLE_DEBUGGER=1` | Use Escargot VSCode Extension |
| ASAN | `-DASAN=1` | AddressSanitizer for memory debugging |
| GC Debug | In code | `starfish->doFullGCWithoutSeeingStack()` |

#### Running

```bash
# Basic execution
./out/release/bin/lightweight-web-engine 'path/to/file.html'

# With options
ELM_ENGINE="shot:file=capture.png" ./out/release/bin/lightweight-web-engine \
  'test.html' --pixel-test --width=800 --height=600
```

### Critical Don't-Miss Rules

#### Anti-Patterns to Avoid

```cpp
// ❌ WRONG - Implicit conditions
if (ptr) { ... }
if (!ptr) { ... }
if (strlen(str)) { ... }

// ❌ WRONG - Raw array allocation
char* buffer = new char[1024];  // Use GC_MALLOC instead

// ❌ WRONG - String as nullptr
String* str = nullptr;  // Use String::emptyString

// ❌ WRONG - Constructor delegation
Dog::Dog(String name) : Dog() { }  // Not allowed for embedded compatibility

// ❌ WRONG - RTTI
if (dynamic_cast<Derived*>(base)) { }  // No RTTI allowed

// ❌ WRONG - try-catch (except DOMException)
try { ... } catch (...) { }  // Only DOMException allowed
```

#### Edge Cases to Handle

- Always check `NULLABLE` pointers before use
- Use `STARFISH_ASSERT(ptr != nullptr)` for non-nullable pointers
- Memory allocation failure terminates the app (no null checks needed for GC_MALLOC)
- Use `Nullable<T>` only for JavaScript binding interfaces

#### Security Rules

- Use `ScriptBindingSecurity` for cross-origin checks
- Use `WindowProxy` for cross-origin window access protection
- Follow Same-Origin Policy for DOM access

#### Performance Gotchas

- Don't use `std::vector` for GC-managed objects - use `GCVector`
- Don't forget to call `giveUpScriptValue()` when releasing JS references
- Use `ALWAYS_INLINE` for hot paths in release builds

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Update this file if new patterns emerge

**For Humans:**

- Keep this file lean and focused on agent needs
- Update when technology stack changes
- Review quarterly for outdated rules
- Remove rules that become obvious over time

**Last Updated:** 2026-06-02
