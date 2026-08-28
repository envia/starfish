# Task: IPC Pattern Discovery for CPP

## Context
You are a static analysis expert. The code2spec parser has identified the following call expressions
from 5 cpp source files that do NOT match any known IPC patterns.

Your task is to identify which of these calls represent IPC (Inter-Process Communication) mechanisms
and categorize them appropriately.

## Known IPC Mechanisms
The parser already knows these IPC mechanisms:
- socket, grpc, message_queue, pipe, shared_memory, signal
- binder, dbus, broadcast_receiver (Android)
- named_pipe, wcf (Windows)
- rmi (Java), xpc (macOS)
- http_client, subprocess
- app_control, message_port (Tizen)

## Unmatched Call Expressions
(66 calls that don't match static patterns)

  - GC_BITMAP_SIZE
  - GC_FREE
  - GC_MALLOC_EXPLICITLY_TYPED
  - GC_USR_PTR_FROM_BASE
  - GC_WORD_LEN
  - GC_WORD_OFFSET
  - GC_disable
  - GC_enable
  - GC_enumerate_reachable_objects_inner
  - GC_gcollect
  - GC_gcollect_and_unmap
  - GC_get_kind_and_size
  - GC_make_descriptor
  - GC_print_backtrace
  - GC_register_mark_stack_func
  - GC_set_abort_func
  - GC_set_bit
  - GC_set_force_unmap_on_gcollect
  - GC_set_free_space_divisor
  - GC_set_warn_proc
  - QualifiedName
  - STARFISH_ASSERT
  - STARFISH_ENUM_HTML_TAG_NAMES
  - STARFISH_ENUM_MATHML_TAG_NAMES
  - STARFISH_ENUM_PSEUDO_SELECTORS
  - STARFISH_ENUM_SVG_TAG_NAMES
  - STARFISH_LOG_ERROR
  - STARFISH_LOG_INFO
  - STARFISH_RELEASE_ASSERT
  - addHistoryEntry
  - c
  - checkHistoryEntry
  - ctx
  - cur
  - currentEntry
  - document
  - entry
  - firstChild
  - g_profiler
  - go
  - hasBlockFlow
  - height
  - httpCacheDataDirectoryPath
  - initNetworkSharedResourceManager
  - isMainThread
  - iter
  - layoutLineBoxesVerticallyCenter
  - m_atomicStringMap
  - m_historyEntries
  - m_httpCache
  - m_iframe
  - m_rootMap
  - m_storageDirectoryPath
  - m_storagePathProvider
  - m_webView
  - m_workerManager
  - markHashTable
  - maybeRelativURL
  - nullable
  - paddingBottom
  - paddingTop
  - pathStdString
  - pushReplaceStateInternal
  - resolveURL
  - scriptNull
  - url

## Your Task
For each call that represents IPC communication:
1. Identify the IPC mechanism type (use existing types or propose new ones)
2. Provide a brief rationale for your classification
3. Suggest the direction (incoming/outgoing/bidirectional)

## Output Format
You MUST output in the following YAML format:

```yaml
language: "cpp"
ipc_patterns:
  - call_name: "SomeClass.SomeMethod"
    ipc_mechanism: "binder"  # or propose new like "content_provider"
    direction: "outgoing"  # incoming/outgoing/bidirectional
    rationale: "This is an Android Binder call for cross-process communication"
```

## Rules
1. Only identify calls that are truly IPC (cross-process communication)
2. Regular function calls within the same process should NOT be marked as IPC
3. If you identify a new IPC mechanism not in the known list, explain why it's needed
4. Be conservative - when in doubt, don't classify as IPC
