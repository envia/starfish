# 04 — Data Layer

> **Relevant source files**
> - [`src/platform/network/http/HTTPCache.h`](src:src/platform/network/http/HTTPCache.h)
> - [`src/platform/network/http/HTTPCacheEntry.h`](src:src/platform/network/http/HTTPCacheEntry.h)
> - [`src/platform/network/http/HTTPHeaderMap.h`](src:src/platform/network/http/HTTPHeaderMap.h)
> - [`src/browser/history/HistoryManager.h`](src:src/browser/history/HistoryManager.h)
> - [`src/StoragePathProvider.h`](src:src/StoragePathProvider.h)

## Data Storage

### HTTP Cache

The HTTP cache (`HTTPCache`) provides persistent caching of HTTP responses. Gated by `STARFISH_ENABLE_HTTPCACHE` compile flag [`Starfish.h`](src:src/Starfish.h#L35).

- `HTTPCache` — cache manager [`src/platform/network/http/HTTPCache.h`](src:src/platform/network/http/HTTPCache.h)
- `HTTPCacheEntry` — individual cache entry [`src/platform/network/http/HTTPCacheEntry.h`](src:src/platform/network/http/HTTPCacheEntry.h)
- `HTTPHeaderMap` — HTTP header storage [`src/platform/network/http/HTTPHeaderMap.h`](src:src/platform/network/http/HTTPHeaderMap.h)

### Browser History

`HistoryManager` [`src/browser/history/HistoryManager.h`](src:src/browser/history/HistoryManager.h) manages navigation history.

### Storage Path Provider

`StoragePathProvider` [`src/StoragePathProvider.h`](src:src/StoragePathProvider.h) provides file system path management for persistent storage. Configured via `StarfishConfiguration.storageDirectoryPath` [`Starfish.h`](src:src/Starfish.h#L50).

### File System Access

Platform file access:
- `PlatformFile` [`src/platform/file/PlatformFile.h`](src/platform/file/PlatformFile.h) — file operations
- `PlatformDirectory` [`src/platform/file/PlatformDirectory.h`](src/platform/file/PlatformDirectory.h) — directory operations

## Data Structures

### GC-Managed Containers

Per `AGENTS.md`, containers of GC-managed pointers use `GCVector`/`GCTightVector` instead of `std::vector` to prevent collection of elements while in use.

### robin_map (Third-Party)

The `tsl::robin_map` header-only hash map [`third_party/robin_map/`](third_party/robin_map/) is used as a high-performance hash map implementation.

## Data Flow

1. **Network → Cache**: HTTP responses flow through `HTTPTransaction` → `HTTPCache` for persistence
2. **Loader → Resource**: `ResourceLoader` fetches resources via network, creates typed `Resource` objects (Font, Image, Text, Header)
3. **History → Storage**: `HistoryManager` persists navigation history to the storage path
