# Lightweight Web Engine (LWE) "Starfish" - Software Design Documentation (Spec)

Welcome to the Software Design Documentation (SDD) for **Starfish**, a high-performance, lightweight web engine designed for mobile and embedded platforms (such as Tizen, Android, EFL, and Flutter).

This documentation index provides complete architectural, logical, and interface specs generated directly from the source code using the **Code2Spec** framework. All technical descriptions and data points are evidence-backed with direct deep links into the source code.

---

## SDD Table of Contents

### 1. System Design Specification

| Chapter | Title | Content Overview |
|---------|-------|------------------|
| [Chapter 1](01-introduction.md) | **Introduction** | System purpose, scope, actor definition, technology stack, and context diagram |
| [Chapter 2](02-architecture.md) | **System Architecture** | Architectural patterns, layer structures, core components, and cross-module interfaces |
| [Chapter 3](03-design-patterns.md) | **Design Patterns** | Design principles, modularization approach, patterns (Factory, Observer, Wrapper), and dependency management |
| [Chapter 4](04-data-layer.md) | **Data Layer** | Data models, storage engines, cache policies, memory management (GC integration), and schema definitions |
| [Chapter 5](05-external-interfaces.md) | **External Interfaces** | User interfaces, public platform APIs, hardware interfaces, and native app containers |
| [Chapter 6](06-configuration-deployment.md) | **Configuration & Deployment** | Build configurations, startup flags, dependency configurations, and platform deployment |
| [Chapter 7](07-resources.md) | **Resources** | Thread model, process structure, memory allocation, and CPU/hardware acceleration policies |
| [Chapter 8](08-security-quality.md) | **Security & Quality** | Content security, sandbox bounds, verification coverage, unit tests, and performance benchmarks |
| [Chapter 9](09-ipc-enum-catalog.md) | **IPC & ENUM Catalog** | Complete list of enumerations, IPC mechanisms, message IDs, signals, and error codes |

---

### 2. Functional Requirements & Core Modules

- **Functional Requirements Index:** [functional-requirements/index.md](functional-requirements/index.md)
- **Module Design Specs:** (Generated on W2 under `modules/`)

---

## Source Citation & Deep Links

Every document in this specification references real-time code components using deep links of the form ``[`StarfishBase.h`](src:src/StarfishBase.h#L1)``. This ensures 100% adherence to our **Zero-Inference Policy**, representing the exact technical reality of the codebase.
