# 03 — Design Patterns

> **Relevant source files**
> - [`src/StarfishBase.h`](src:src/StarfishBase.h)
> - [`src/public/contract/LWEDelegate.h`](src:src/public/contract/LWEDelegate.h)
> - [`src/binding/ScriptWrappable.h`](src:src/binding/ScriptWrappable.h)
> - [`src/binding/WindowProxy.h`](src:src/binding/WindowProxy.h)

## Identified Patterns

### 1. Delegate Pattern (Contract-Delegate)

The public API uses a contract-delegate pattern to cross the `.so` boundary. Pure-virtual interfaces in `src/public/contract/` define the API surface; concrete implementations in `src/public/delegate/` provide the behavior.

- Contract: [`src/public/contract/LWEWebViewDelegate.h`](src:src/public/contract/LWEWebViewDelegate.h)
- Implementation: [`src/public/delegate/LWEWebViewDelegateImpl.cpp`](src:src/public/delegate/LWEWebViewDelegateImpl.cpp)

This pattern allows embedders to provide custom implementations without linking against the engine internals.

### 2. GC-Managed Object Graph

All engine objects inherit from `gc` (Boehm-Demers-Weiser GC). The `Starfish` class itself inherits `gc` [`Starfish.h`](src:src/Starfish.h#L58). Containers use `GCVector`/`GCTightVector` instead of `std::vector` to keep elements on the GC heap.

### 3. Optional<T> Nullability

Values that can be absent use `Optional<T>` [`src/StarfishBase.h`](src:src/StarfishBase.h) rather than raw pointers overloaded with `nullptr`. Truthiness check: `if (node)` / `if (!node)`.

### 4. Platform Abstraction (Backend Strategy)

Multiple platform backends implement the same interface:
- **Canvas**: Cairo (`CanvasCairo`), GL (`CompositorGL`), Mock (`CanvasMock`)
- **Message Loop**: GLib (`MessageLoopGLib`), libUV (`MessageLoopLibUV`)
- **Multimedia**: Linux, Tizen, TV, WebRTC variants
- **Window**: EFL, Ecore, GLib, libUV, headless, Windows, X11

### 5. ScriptWrappable / Holdable

DOM objects that need JS representation inherit `ScriptWrappable` [`src/binding/ScriptWrappable.h`](src:src/binding/ScriptWrappable.h). The `Holdable` pattern (`DocumentHoldable`, `WebViewHoldable`, `WindowHoldable`) manages JS object lifetime.

### 6. WindowProxy

`WindowProxy` [`src/binding/WindowProxy.h`](src:src/binding/WindowProxy.h) implements the security boundary for cross-origin window access per the HTML spec.

### 7. Custom Binding Generation

JS bindings for spec-defined interfaces are generated from `.idl` files at cmake configure time [`README.md`](README.md#L55). This follows the Web IDL specification pattern.

### 8. APIRecorder/Replayer

`APIRecorder` [`src/public/APIRecorder.cpp`](src:src/public/APIRecorder.cpp) records API calls for later replay by `APIReplayer` [`src/shell/APIReplayer.cpp`](src/shell/APIReplayer.cpp) — a testing/debugging pattern for reproducing engine state.
