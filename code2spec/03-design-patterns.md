**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 3: Design Patterns

> **Relevant source files:**
> - [`ScriptWrappable.h`](src:src/binding/ScriptWrappable.h#L1)
> - [`ScriptBindingWindowInstance.h`](src:src/binding/ScriptBindingWindowInstance.h#L1)
> - [`LWEWebContainerDelegate.cpp`](src:src/public/delegate/LWEWebContainerDelegate.cpp#L1)

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
