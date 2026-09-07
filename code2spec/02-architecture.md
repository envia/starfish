**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 2: System Architecture

> **Relevant source files:**
> - [`Starfish.cpp`](src:src/Starfish.cpp#L1)
> - [`LWEWebView.h`](src:inc/LWEWebView.h#L1)
> - [`ScriptBindingInstance.cpp`](src:src/binding/ScriptBindingInstance.cpp#L1)
> - [`LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L1)

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

  API --> Bridge:::external
  class API,Bridge external
  Bridge --> Binding:::external
  class Binding external
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

## Module Dependencies

<!-- code2spec:module-dependency:start -->
```mermaid
%% code2spec:diagram-type=module-dependency
graph LR
  bindings["bindings"]
  browser["browser"]
  compat_tizen["compat-tizen"]
  docs_generator["docs-generator"]
  engine_core["engine-core"]
  inc_headers["inc-headers"]
  launcher["launcher"]
  platform_canvas["platform-canvas"]
  platform_core["platform-core"]
  platform_file["platform-file"]
  platform_loader["platform-loader"]
  platform_multimedia["platform-multimedia"]
  platform_network["platform-network"]
  public_bridge["public-bridge"]
  shell["shell"]
  third_party["third-party"]
  tooling["tooling"]
```
<!-- code2spec:module-dependency:end -->
