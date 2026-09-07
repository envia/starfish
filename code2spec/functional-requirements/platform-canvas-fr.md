# Functional Requirements — platform-canvas

> **Relevant source files**
> - [`CanvasCairo.cpp`](src:src/platform/canvas/CanvasCairo.cpp)
> - [`CompositorGL.cpp`](src:src/platform/canvas/CompositorGL.cpp)
> - [`PathCairo.h`](src:src/platform/canvas/PathCairo.h)
> - [`font/FontImplCairo.h`](src:src/platform/canvas/font/FontImplCairo.h)

## Given Factors

- Multiple rendering backends: Cairo (software), GL (GPU), Mock (testing)
- Font shaping via HarfBuzz + ICU
- BGRA pixel order for Cairo

## Overview

The canvas module provides 2D graphics rendering with pluggable backends (Cairo, OpenGL ES), path rendering, font management, and image data handling.

## Functional Requirements

### FR-CANVAS-001: Cairo Backend
The system shall provide canvas rendering via Cairo when `PORT_CANVAS_BACKEND_CAIRO` is defined.
- **Source:** [`CanvasCairo.cpp`](src:src/platform/canvas/CanvasCairo.cpp#L23)

### FR-CANVAS-002: GL Compositor
The system shall provide GPU-accelerated compositing via OpenGL ES.
- **Source:** [`CompositorGL.cpp`](src:src/platform/canvas/CompositorGL.cpp)

### FR-CANVAS-003: Path Rendering
The system shall provide path operations (moveTo, lineTo, arc) via backend-specific implementations.
- **Source:** [`PathCairo.h`](src:src/platform/canvas/PathCairo.h)

### FR-CANVAS-004: Font Shaping
The system shall shape text using HarfBuzz with ICU support.
- **Source:** [`HarfBuzzICU.h`](src:src/platform/canvas/font/hb-icu/HarfBuzzICU.h)

### FR-CANVAS-005: Image Data
The system shall handle image data types: Native, Compressed, AnimatedGIF, SVG.
- **Source:** [`NativeImageDataImpl.cpp`](src:src/platform/canvas/image/NativeImageDataImpl.cpp)

### FR-CANVAS-006: Mock Backend
The system shall provide a mock canvas backend for testing.
- **Source:** [`CanvasMock.cpp`](src:src/platform/canvas/CanvasMock.cpp)

## Dependencies

- Cairo, OpenGL ES, HarfBuzz, ICU, Skia, core-engine

## Code Factors

- C++, LGPL v2.1, compile-time backend selection

## Quality

- BGRA pixel order enforced for Cairo
- Mock backend for test isolation
