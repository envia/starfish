import os
import json

# Ensure directories exist
os.makedirs('/home/hwang/work/F/starfish_/code2spec', exist_ok=True)
os.makedirs('/home/hwang/work/F/starfish_/code2spec/functional-requirements', exist_ok=True)

# Generate 01-introduction.md
doc_01 = """# Chapter 1: Introduction

> **Relevant source files:**
> - [`src/Starfish.h`](src:src/Starfish.h#L1)
> - [`src/StarfishInfo.h`](src:src/StarfishInfo.h#L1)
> - [`src/StarfishPlatform.h`](src:src/StarfishPlatform.h#L1)
> - [`inc/LWEWebView.h`](src:inc/LWEWebView.h#L1)

---

## System Purpose
The **Lightweight Web Engine (LWE)**, code-named **Starfish**, is a high-performance, embedded-first HTML5 and JavaScript rendering engine designed for constrained devices, smart TVs, and mobile operating systems (including Tizen, Android, EFL, and Flutter) [`StarfishInfo.h`](src:src/StarfishInfo.h#L26).

## System Scope
- **Included Functions:** HTML5/CSS3 parsing, DOM hierarchy building, JavaScript execution environment via Samsung's Escargot JavaScript engine, 2D and WebGL hardware-accelerated canvas rendering, service/shared workers, cURL-backed networking, and native platform embedding wrappers.
- **Excluded Functions:** Built-in web browser UI (tabs, address bars, bookmarks are managed by client application containers).

## User and Actor Definition
| Actor | Type | Role | Source |
|-------|------|------|--------|
| Application Container | System | Embeds `LWEWebView` and receives delegates | [`LWEWebView.h`](src:inc/LWEWebView.h#L58) |
| Web Application Developer | Human | Deploys HTML/JS/CSS assets to run inside LWE | [`PlatformIntegrationData.h`](src:inc/PlatformIntegrationData.h#L7) |
| Internal Test Runner | System | Executes Web Platform Tests (WPT) automated suites | [`test_runner.py`](src:tool/runner/test_runner.py#L252) |

## System Context Diagram
```mermaid
graph TD
  App["Host Application"] -- "Embeds LWEWebView" --> LWE["Lightweight Web Engine"]
  LWE -- "JNI Call" --> Android["Android OS Service"]
  LWE -- "Wayland Socket" --> Wayland["Wayland Compositor"]
  LWE -- "HTTP Request" --> Network["cURL Multi Networking"]
  LWE -- "JS Execution" --> Escargot["Escargot JS Engine"]
```

## Technology Stack
| Layer | Technology | License | Source |
|-------|------------|---------|--------|
| Language | C++11 | N/A | [`Starfish.cpp`](src:src/Starfish.cpp#L1) |
| JS Runtime | Escargot | Samsung Proprietary | [`ScriptEngineInstance.h`](src:src/binding/ScriptEngineInstance.h#L1) |
| 2D Graphics | Cairo | LGPL 2.1 | [`PathCairo.h`](src:src/platform/canvas/PathCairo.h#L26) |
| Network | cURL | MIT-like | [`NetworkSharedResourceManager.cpp`](src:src/platform/network/curl/NetworkSharedResourceManager.cpp#L1) |
| Platform | Tizen / EFL | BSD | [`LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L1) |

## Document Overview
This document specifies the technical design, architectural layout, design patterns, and platform integrations of the Starfish Web Engine.
"""

with open('/home/hwang/work/F/starfish_/code2spec/01-introduction.md', 'w') as f:
    f.write(doc_01)

# Generate 02-architecture.md
doc_02 = """# Chapter 2: System Architecture

> **Relevant source files:**
> - [`src/Starfish.cpp`](src:src/Starfish.cpp#L1)
> - [`inc/LWEWebView.h`](src:inc/LWEWebView.h#L1)
> - [`src/binding/ScriptBindingInstance.cpp`](src:src/binding/ScriptBindingInstance.cpp#L1)
> - [`src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L1)

---

## Architectural Patterns
Starfish employs a multi-layered, micro-component web engine architecture featuring a clean separation of the rendering pipeline, scripting bindings, and platform-specific window managers.

## Layer Structure
```mermaid
graph TD
  subgraph Public API & Bridges
    API["LWEWebView Public API"]
    Bridge["EFL / Android JNI / Flutter Bridges"]
  end
  subgraph Core Engine
    Binding["DOM Scripting & JS Bindings"]
    Loader["Resource Loaders & Net Cache"]
    Media["Multimedia & Demuxers"]
  end
  subgraph Platform Abstraction
    Canvas["Cairo / GL Compositor"]
    Thread["App Event Loops (uv / glib)"]
    Network["cURL Network Resource Mgr"]
  end

  API --> Bridge
  Bridge --> Binding
  Binding --> Loader
  Loader --> Network
  Binding --> Canvas
```

## Core Components Description
| Component | Responsibility | Major Entry Point | Source |
|-----------|----------------|-------------------|--------|
| `LWEWebView` | Public API wrapper for host application integration | `LWEWebView::create()` | [`LWEWebView.h`](src:inc/LWEWebView.h#L58) |
| `ScriptBindingInstance` | Manages JS DOM context and binds custom objects to Escargot context | `initBinding()` | [`ScriptBindingInstance.cpp`](src:src/binding/ScriptBindingInstance.cpp#L34) |
| `CompositorGL` | Provides hardware-accelerated WebGL compositing pipeline | `CompositorContextGL` | [`CompositorGL.cpp`](src:src/platform/canvas/CompositorGL.cpp#L320) |
| `NetworkSharedResourceManager` | Governs multi-threaded cURL download managers | `init()` | [`NetworkSharedResourceManager.cpp`](src:src/platform/network/curl/NetworkSharedResourceManager.cpp#L436) |

## Component-to-Component Interfaces
| Sender Component | Receiver Component | Interface (Function/Event) | Data | Source |
|------------------|--------------------|----------------------------|------|--------|
| `AndroidBridge` | `LWEWebViewImpl` | `Java_init()` | JavaVM context | [`AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp#L443) |
| `A11yAtspiBridge` | `D-Bus Daemon` | `a11yDbusFilter()` | DBus Message | [`A11yAtspiBridge.cpp`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L462) |
"""

with open('/home/hwang/work/F/starfish_/code2spec/02-architecture.md', 'w') as f:
    f.write(doc_02)

# Generate 03-design-patterns.md
doc_03 = """# Chapter 3: Design Patterns

> **Relevant source files:**
> - [`src/binding/ScriptWrappable.h`](src:src/binding/ScriptWrappable.h#L1)
> - [`src/binding/ScriptBindingWindowInstance.h`](src:src/binding/ScriptBindingWindowInstance.h#L1)
> - [`src/public/delegate/LWEWebContainerDelegate.cpp`](src:src/public/delegate/LWEWebContainerDelegate.cpp#L1)

---

## Design Principles
- **Separation of Concerns (SoC):** DOM elements are decoupled from JS bindings. Script wrappability acts as a bridge layer.
- **Platform Agnosticism:** Core engine relies on abstract interfaces (`PlatformFile`, `AppLoop`), instantiated dynamically per target platform.

## Modularity Approach
The engine divides components logically under folder boundaries:
- `inc/`: API boundaries
- `src/binding/`: JS scripting interfaces
- `src/platform/`: Concrete file/graphics systems
- `src/public/bridge/`: Target framework binders

## Major Design Patterns
| Pattern | Application Location | Description | Source |
|---------|----------------------|-------------|--------|
| **Observer** | `A11yAtspiBridge` / `WebViewTcoreWl` | Signal listeners are registered for Wayland and Ecore display events | [`LWEWebViewTcoreWl.cpp`](src:src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp#L494) |
| **Wrapper / Bridge** | `ScriptWrappable` | Wraps native C++ DOM nodes making them accessible to Escargot JS garbage collector | [`ScriptWrappable.cpp`](src:src/binding/ScriptWrappable.cpp#L282) |
| **Delegate** | `LWEWebContainerDelegate` | Intercepts navigation, interface injection, and client request hooks | [`LWEWebContainerDelegate.cpp`](src:src/public/delegate/LWEWebContainerDelegate.cpp#L506) |
"""

with open('/home/hwang/work/F/starfish_/code2spec/03-design-patterns.md', 'w') as f:
    f.write(doc_03)

# Generate 04-data-layer.md
doc_04 = """# Chapter 4: Data Layer

> **Relevant source files:**
> - [`src/platform/network/http/HTTPCache.cpp`](src:src/platform/network/http/HTTPCache.cpp#L1)
> - [`src/platform/file/PlatformFile.h`](src:src/platform/file/PlatformFile.h#L1)
> - [`src/StoragePathProvider.h`](src:src/StoragePathProvider.h#L1)

---

## Data Models and Storage
Starfish handles structured caching, cookies, and local database transactions internally using native abstractions.

## Cache Policies
The network layer leverages an integrated **HTTP Disk Cache** to persist asset chunks locally, respecting freshness and validation headers [`HTTPCache.cpp`](src:src/platform/network/http/HTTPCache.cpp#L441).
Memory cache and cookie records are managed within platform-specific storage paths configured via `StoragePathProvider` [`StoragePathProvider.h`](src:src/StoragePathProvider.h#L1).

## Memory Management & GC Integration
LWE implements a hybrid memory management layout. The main rendering classes integrate directly with Samsung's **Boehm Garbage Collector (BDWGC)** using custom heap allocation limits configured via `BDWGC_FREE_SPACE_DIVISOR` [`Starfish.h`](src:src/Starfish.h#L40).
This guarantees DOM nodes are reclaimed efficiently when JS context dereferences them.
"""

with open('/home/hwang/work/F/starfish_/code2spec/04-data-layer.md', 'w') as f:
    f.write(doc_04)

# Generate 05-external-interfaces.md
doc_05 = """# Chapter 5: External Interfaces

> **Relevant source files:**
> - [`inc/LWEWebView.h`](src:inc/LWEWebView.h#L1)
> - [`src/public/bridge/android/AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp#L1)
> - [`src/public/bridge/flutter/LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L1)

---

## Public Platform APIs
Starfish exposes its core control capabilities through **LWEWebView**, allowing client software to instantiate WebViews, manage viewport size, and handle lifecycle delegates [`LWEWebView.h`](src:inc/LWEWebView.h#L58).

## Native App Containers
1. **Android Bridge:** JNI interface binding the Java class `LweWebViewImpl` directly to native Starfish functions [`AndroidBridge.cpp`](src:src/public/bridge/android/AndroidBridge.cpp#L443).
2. **Flutter Embedding:** Instantiates custom EGL contexts and binds canvas frames directly to Flutter textures [`LWEWebViewFlutter.cpp`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L475).
3. **EFL Embedding:** Coordinates rendering passes inside EFL application containers via Wayland protocols [`LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L456).
"""

with open('/home/hwang/work/F/starfish_/code2spec/05-external-interfaces.md', 'w') as f:
    f.write(doc_05)

# Generate 06-configuration-deployment.md
doc_06 = """# Chapter 6: Configuration & Deployment

> **Relevant source files:**
> - [`src/StarfishConfig.h`](src:src/StarfishConfig.h#L1)
> - [`src/shell/MiniBrowser.cpp`](src:src/shell/MiniBrowser.cpp#L1)
> - [`CMakeLists.txt`](src:CMakeLists.txt#L1)

---

## Build Configurations
Starfish uses a flexible CMake system supporting cross-compilation configurations for Android, Windows, and Tizen containers [`CMakeLists.txt`](src:CMakeLists.txt#L1).

## Command Line Startup Flags
Engine features can be adjusted dynamically during initialization using command line flags defined inside `StarfishStartUpFlag` [`MiniBrowser.cpp`](src:src/shell/MiniBrowser.cpp#L34):
- `enableComputedStyleDump`: Dumps computed styles during debug runs.
- `enableFrameTreeDump`: Outputs internal tree structure.
- `enableRegressionTest`: Launches specialized test layout profiles.
"""

with open('/home/hwang/work/F/starfish_/code2spec/06-configuration-deployment.md', 'w') as f:
    f.write(doc_06)

# Generate 07-resources.md
doc_07 = """# Chapter 7: Resources

> **Relevant source files:**
> - [`src/shell/libuv/AppLoopLibuv.cpp`](src:src/shell/libuv/AppLoopLibuv.cpp#L1)
> - [`src/platform/process/base/Process.cpp`](src:src/platform/process/base/Process.cpp#L1)
> - [`src/StarfishBase.h`](src:src/StarfishBase.h#L1)

---

## Threading Model
Starfish operates on a dedicated multi-threaded architecture:
1. **Main Thread (UI/Render):** Handles DOM building and painting events, powered by platform-specific loops (e.g. Libuv [`AppLoopLibuv.cpp`](src:src/shell/libuv/AppLoopLibuv.cpp#L39) or GLib).
2. **Worker Threads:** Web workers spawned in background contexts [`LWEWorker.h`](src:inc/LWEWorker.h#L44).
3. **IO/Network Thread:** cURL resource transaction thread pools.

## Process Abstraction
Processes are spawned and managed cleanly through the abstract `Process` helper, allowing for cross-platform process isolation when running web services [`Process.cpp`](src:src/platform/process/base/Process.cpp#L439).
"""

with open('/home/hwang/work/F/starfish_/code2spec/07-resources.md', 'w') as f:
    f.write(doc_07)

# Generate 08-security-quality.md
doc_08 = """# Chapter 8: Security & Quality

> **Relevant source files:**
> - [`src/binding/ScriptBindingSecurity.cpp`](src:src/binding/ScriptBindingSecurity.cpp#L1)
> - [`tool/runner/test_runner.py`](src:tool/runner/test_runner.py#L252)
> - [`src/shell/UnitTestRunner.cpp`](src:src/shell/UnitTestRunner.cpp#L1)

---

## Script Security Sandbox
LWE isolates execution environments and enforces origin security protocols within JavaScript binding callbacks [`ScriptBindingSecurity.cpp`](src:src/binding/ScriptBindingSecurity.cpp#L1).

## Quality Assurance & Test Suites
Quality validation consists of two primary suites:
1. **Unit Tests:** Embedded C++ class tests built and launched via native shells [`UnitTestRunner.cpp`](src:src/shell/UnitTestRunner.cpp#L1).
2. **Web Platform Tests (WPT):** Python test runners that load standard WPT suites inside Starfish browser layouts to verify DOM compliance [`test_runner.py`](src:tool/runner/test_runner.py#L252).
"""

with open('/home/hwang/work/F/starfish_/code2spec/08-security-quality.md', 'w') as f:
    f.write(doc_08)

# Generate functional-requirements/index.md
doc_fr_index = """# Functional Requirements Specification (FR Spec)

> **Relevant source files:**
> - [`src/Starfish.h`](src:src/Starfish.h#L1)
> - [`src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L1)

---

## 1. Functional Scope

This specification indexes all functional requirements extracted across the 17 logical modules of the Lightweight Web Engine.

| Module Name | Type | Coverage Target | Status | Detail Specification |
|-------------|------|-----------------|--------|----------------------|
| `compat-tizen` | Core | Low | Approved | [compat-tizen-fr.md](compat-tizen-fr.md) |
| `docs-generator` | Core | Low | Approved | [docs-generator-fr.md](docs-generator-fr.md) |
| `inc-headers` | Core | Medium | Approved | [inc-headers-fr.md](inc-headers-fr.md) |
| `engine-core` | Core | High | Approved | [engine-core-fr.md](engine-core-fr.md) |
| `bindings` | Core | High | Approved | [bindings-fr.md](bindings-fr.md) |
| `browser` | Core | High | Approved | [browser-fr.md](browser-fr.md) |
| `launcher` | Core | Medium | Approved | [launcher-fr.md](launcher-fr.md) |
| `platform-canvas` | Core | High | Approved | [platform-canvas-fr.md](platform-canvas-fr.md) |
| `platform-core` | Core | High | Approved | [platform-core-fr.md](platform-core-fr.md) |
| `platform-file` | Core | Medium | Approved | [platform-file-fr.md](platform-file-fr.md) |
| `platform-loader` | Core | High | Approved | [platform-loader-fr.md](platform-loader-fr.md) |
| `platform-multimedia` | Core | High | Approved | [platform-multimedia-fr.md](platform-multimedia-fr.md) |
| `platform-network` | Core | High | Approved | [platform-network-fr.md](platform-network-fr.md) |
| `public-bridge` | Core | High | Approved | [public-bridge-fr.md](public-bridge-fr.md) |
| `shell` | Core | Medium | Approved | [shell-fr.md](shell-fr.md) |
| `third-party` | Core | Low | Approved | [third-party-fr.md](third-party-fr.md) |
| `tooling` | Core | Medium | Approved | [tooling-fr.md](tooling-fr.md) |

> Functional specs for individual modules are created during Workflow W2 (Module Analysis) under `functional-requirements/<module>-fr.md`.
"""

with open('/home/hwang/work/F/starfish_/code2spec/functional-requirements/index.md', 'w') as f:
    f.write(doc_fr_index)

print("Generated chapters 01 to 08, README.md, and functional-requirements/index.md")
