```yaml
language: "cpp"
ipc_patterns: []
```

None of the 66 unmatched calls represent true IPC (cross-process communication) mechanisms. They are all in-process function calls, macro invocations, or field accesses:
- GC_* functions: Boehm garbage collector API calls (same process)
- STARFISH_* macros: Assertions, logging, enum registration (same process)
- m_* fields: Regular member field accesses (e.g., m_webView, m_httpCache, m_workerManager)
- Utility functions: resolveURL, isMainThread, addHistoryEntry, etc. (same process)
