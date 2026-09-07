**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 4: Data Layer

> **Relevant source files:**
> - [`HTTPCache.cpp`](src:src/platform/network/http/HTTPCache.cpp#L1)
> - [`PlatformFile.h`](src:src/platform/file/PlatformFile.h#L1)
> - [`StoragePathProvider.h`](src:src/StoragePathProvider.h#L1)

---

## Data Models and Storage
Starfish handles structured caching, cookies, and local database transactions internally using native abstractions.

## Cache Policies
The network layer leverages an integrated **HTTP Disk Cache** to persist asset chunks locally, respecting freshness and validation headers [`HTTPCache.cpp`](src:src/platform/network/http/HTTPCache.cpp#L441).
Memory cache and cookie records are managed within platform-specific storage paths configured via `StoragePathProvider` [`StoragePathProvider.h`](src:src/StoragePathProvider.h#L1).

## Memory Management & GC Integration
LWE implements a hybrid memory management layout. The main rendering classes integrate directly with Samsung's **Boehm Garbage Collector (BDWGC)** using custom heap allocation limits configured via `BDWGC_FREE_SPACE_DIVISOR` [`Starfish.h`](src:src/Starfish.h#L40).
This guarantees DOM nodes are reclaimed efficiently when JS context dereferences them.
