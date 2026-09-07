# Functional Requirements — binding

> **Relevant source files**
> - [`ScriptEngineInstance.h`](src:src/binding/ScriptEngineInstance.h)
> - [`ScriptBindingInstance.h`](src:src/binding/ScriptBindingInstance.h)
> - [`ScriptBindingSecurity.h`](src:src/binding/ScriptBindingSecurity.h)
> - [`WindowProxy.h`](src:src/binding/WindowProxy.h)

## Given Factors

- Escargot JS engine integration
- GC-managed object graph (BDWGC)
- IDL-generated bindings

## Overview

The binding module integrates the Escargot JavaScript engine with the Starfish DOM, providing script execution, security enforcement, and custom DOM interface bindings.

## Functional Requirements

### FR-BINDING-001: Script Engine Lifecycle
The system shall manage the Escargot JS engine instance, including locale, timezone, disposal, and idle mode.
- **Source:** [`ScriptEngineInstance.h`](src:src/binding/ScriptEngineInstance.h#L35)

### FR-BINDING-002: Microtask Queue
The system shall drain the microtask queue and track macro task counter.
- **Source:** [`ScriptEngineInstance.h`](src:src/binding/ScriptEngineInstance.h#L43)

### FR-BINDING-003: DOM-JS Bridge
The system shall provide custom bindings for DOM interfaces (Document, Window, HTMLElement, EventTarget, XMLHttpRequest, etc.).
- **Source:** [`ScriptBindingInstance.h`](src:src/binding/ScriptBindingInstance.h#L54)

### FR-BINDING-004: Same-Origin Security
The system shall enforce same-origin policy via `ScriptBindingSecurity` and `WindowProxy`.
- **Source:** [`ScriptBindingSecurity.h`](src:src/binding/ScriptBindingSecurity.h), [`WindowProxy.h`](src:src/binding/WindowProxy.h)

### FR-BINDING-005: IDL-Generated Bindings
The system shall generate JS bindings from `.idl` files at cmake configure time.
- **Source:** [`ScriptBindingInstance.h`](src:src/binding/ScriptBindingInstance.h#L36)

### FR-BINDING-006: Holdable Pattern
The system shall manage JS object lifetime via Holdable wrappers (Document, WebView, Window, Starfish).
- **Source:** [`DocumentHoldable.h`](src:src/binding/DocumentHoldable.h), [`WebViewHoldable.h`](src:src/binding/WebViewHoldable.h)

## Dependencies

- Escargot JS engine, core-engine (DOM)

## Code Factors

- C++, LGPL v2.1, GC-managed

## Quality

- Security enforced at binding layer
- Generated bindings reduce manual code
