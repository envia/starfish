# IPC Pattern Discovery Response (consolidated — verified against source)

Round 1 (repo-root sample, 5 files): no IPC — unmatched calls were bdwgc GC
APIs, logging/assert macros, libpng, and stdio (in-process only).

Round 2 (src/core/modules, 40 files) plus direct verification of the worker,
serviceworker, and networking modules identified these cross-process /
network communication call sites:

- nanomsg (`nn_*`): scalability-protocols message sockets used by the worker
  transport layer. [Source: src/core/modules/worker/util/network/SocketNN.cpp:52,134,146]
- Process launching: `ProcessUtil::launchProcess` / `launchProcessOnDoubleFork`
  spawn worker host processes. [Source: src/platform/process/base/Process.cpp:43,104]
  Used by ServiceWorkerProcessManager. [Source: src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp:234]
- libwebsockets (`lws_*`): WebSocket client transport. [Source: src/core/modules/networking/SocketLWS.cpp:87,436]

New mechanisms proposed: `nanomsg` (distinct message-socket library, not plain
BSD socket), `websocket` (framed full-duplex network messaging, distinct from
plain http_client).

```yaml
language: "cpp"
ipc_patterns:
  - call_name: "nn_socket"
    ipc_mechanism: "nanomsg"
    direction: "bidirectional"
    rationale: "Creates a nanomsg scalability-protocols socket for the worker transport (SocketNN.cpp:52)"
  - call_name: "nn_send"
    ipc_mechanism: "nanomsg"
    direction: "outgoing"
    rationale: "Sends a message over a nanomsg socket (SocketNN.cpp:134)"
  - call_name: "nn_recv"
    ipc_mechanism: "nanomsg"
    direction: "incoming"
    rationale: "Receives a message from a nanomsg socket (SocketNN.cpp:146)"
  - call_name: "nn_close"
    ipc_mechanism: "nanomsg"
    direction: "bidirectional"
    rationale: "Closes a nanomsg IPC endpoint (SocketNN.cpp)"
  - call_name: "launchProcess"
    ipc_mechanism: "subprocess"
    direction: "outgoing"
    rationale: "ProcessUtil::launchProcess spawns a worker host process (Process.cpp:43; used by ServiceWorkerProcessManager.cpp:234)"
  - call_name: "launchProcessOnDoubleFork"
    ipc_mechanism: "subprocess"
    direction: "outgoing"
    rationale: "Double-fork variant of worker host process spawning (Process.cpp:104)"
  - call_name: "lws_write"
    ipc_mechanism: "websocket"
    direction: "outgoing"
    rationale: "libwebsockets frame write in the WebSocket client transport (SocketLWS.cpp:87)"
  - call_name: "lws_service"
    ipc_mechanism: "websocket"
    direction: "bidirectional"
    rationale: "libwebsockets event-loop service pump for WebSocket I/O (SocketLWS.cpp:436)"
```
