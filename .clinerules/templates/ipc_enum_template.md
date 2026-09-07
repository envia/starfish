# IPC Constants & ENUM Catalog

> **Generated**: YYYY-MM-DD
> **Project**: <ProjectName>
> **Source Files**: <N> files analyzed

<!-- This template is for IPC constants, ENUM values, message IDs, signal mappings, and error codes -->
<!-- Cite sources as backticked deep links: [`file or symbol`](src:repo-relative-path#L<line>).
     Take the line from the file:line of the extraction JSON (llm-extraction/*.json). Omit the host prefix — repo.json.deepLink.base is prepended at render time.
     Same deep-link discipline as every other chapter. Without evidence, write "Not specified in code". -->

---

## ENUM Definitions

<!-- Extract all ENUM/enum definitions with their values from source code -->
<!-- Supported languages: C/C++ enum_specifier, Java enum_declaration, Python enum, TypeScript enum_declaration, etc. -->

| ENUM Name | Type | Values | Source |
|-----------|------|--------|--------|
| `MessageType` | int32 | INIT=0x01, DATA=0x02, ACK=0x03, ERR=0xFF | [`protocol.h`](src:protocol.h#L12) |

---

## Message ID Catalog

<!-- Extract IPC message IDs, opcodes, and protocol constants -->
<!-- Message IDs are typically #define constants or enum values used for IPC message identification -->

| Message ID | Hex Value | Direction | Payload | Handler | Source |
|------------|-----------|-----------|---------|---------|--------|
| MSG_INIT | 0x0001 | Client→Server | InitRequest | handleInit() | [`msg.h`](src:msg.h#L23) |

---

## Constant Definitions

<!-- Extract #define constants, const declarations, and static final values -->
<!-- Focus on constants related to IPC, protocol, configuration, and system limits -->

| Constant | Value | Unit/Type | Usage Context | Source |
|----------|-------|-----------|---------------|--------|
| MAX_RETRY | 3 | count | Connection retry logic | [`config.h`](src:config.h#L5) |

---

## Signal/Event Mapping

<!-- Extract signal-slot connections, event handlers, and observer patterns -->
<!-- For event-driven architectures: Qt signals, Android BroadcastReceiver, Node.js EventEmitter, etc. -->

| Signal/Event | Emitter | Listener | Data Type | Source |
|-------------|---------|----------|-----------|--------|
| onConnect | ConnectionMgr | SessionHandler | ConnInfo | [`events.h`](src:events.h#L34) |

---

## Error Code Catalog

<!-- Extract error codes, return status values, and failure enums -->
<!-- Include severity classification and recovery strategies where identifiable from code -->

| Error Code | Value | Severity | Description | Recovery | Source |
|------------|-------|----------|-------------|----------|--------|
| ERR_TIMEOUT | 0x1001 | High | Request timeout | Retry with backoff | [`errors.h`](src:errors.h#L8) |

---

## IPC Mechanism Summary

<!-- Summary of all IPC mechanisms detected in the codebase -->
<!-- IPC mechanism values must be from the IpcMechanism enum: socket, grpc, message_queue, pipe, shared_memory, signal, broadcast_receiver, binder, dbus, named_pipe, wcf, rmi, xpc, http_client, subprocess -->

| IPC Mechanism | Source Component | Target Component | Protocol | Data Format | Source |
|---------------|-----------------|------------------|----------|-------------|--------|
| socket | PaymentClient | PaymentServer | TCP:8080 | JSON | [`client.cpp`](src:client.cpp#L45) |
