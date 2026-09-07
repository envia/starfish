```yaml
language: "cpp"
ipc_patterns: []
```

## Rationale

After analyzing all 90 unmatched call expressions, none represent IPC (Inter-Process Communication) mechanisms:

- **GC_* calls** (GC_malloc, GC_free, GC_gcollect, etc.): These are Boehm-Demers-Weiser garbage collector functions for in-process memory management, not IPC.
- **png_* calls** (png_create_read_struct, png_read_image, etc.): These are libpng library functions for PNG image decoding, entirely in-process.
- **Standard C library** (fopen, fclose, fread, fprintf, memcpy, abort, exit, malloc, printf, puts, setbuf, setjmp, abs): Standard libc functions, no IPC involved.
- **STARFISH_* macros** (STARFISH_ASSERT, STARFISH_LOG_ERROR, STARFISH_ENUM_*): Internal assertion/logging/enum macros, same-process.
- **Other calls** (cookieManager, webView, webContainer, httpCacheDataDirectoryPath, etc.): Internal Starfish method/field accesses within the same process.

No new IPC mechanisms need to be registered.
