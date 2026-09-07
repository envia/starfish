"""
LLM Prompt Templates for AST Extraction.

Token-efficient prompts designed for Semantic Markdown input (not raw JSON).

The pipeline is: tree-sitter CST → parser.py (NodeInfo/EdgeInfo) → graph-raw.json
→ filter relevant nodes → compact Semantic Markdown → single LLM call.

Each prompt:
- Expects pre-filtered Semantic Markdown (not raw AST JSON)
- Is language-agnostic (LLM reads the Languages header)
- Requires [Source: file:line] citations
- Requests JSON array output
"""

# =============================================================================
# ENUM EXTRACTION PROMPT
# =============================================================================

ENUM_EXTRACTION_PROMPT = """
You are an expert code analyzer. Extract ENUM definitions from the Semantic Markdown below.

## Input Format
The input is pre-filtered Semantic Markdown — only enum-relevant nodes are included.
Languages are auto-detected from file extensions and shown in the header.
Each line format: `[language] EnumName | VALUE1, VALUE2, ... | file:line`

## Output Format
Return a JSON array where each enum entry has:
{
    "name": "EnumName",
    "values": ["VALUE1", "VALUE2"],
    "type": "<language>_enum",
    "language": "java|kotlin|cpp|typescript|python|swift|csharp|go|rust|other",
    "source": "[Source: file/path.ext:line_number]"
}

The `type` field uses the language prefix (e.g., "kotlin_enum", "java_intdef", "cpp_enum").
The `language` field identifies the programming language.

## CRITICAL: Qualified ENUM Names
Every ENUM name MUST use the format `EnclosingClass.EnumName` or `FileName.EnumName`:
- If enum is nested inside a class/struct, qualify with parent: `PeerInfo.Type`, `AdbPairingClient.State`
- If enum is top-level but language uses file-scoped naming, qualify with file stem: `ShizukuSettings.LaunchMethod`
- If enum is inside a namespace/module, qualify with namespace: `Network.ConnectionState`
- NEVER return a bare generic name like `Type`, `State`, `Mode`, `Kind`, `Status` — always qualify it with its parent class or file name

## Non-Standard ENUM Patterns to Detect (ALL languages)
In addition to standard enum declarations, extract these patterns:
1. **Annotation-style enums** (Java/Android @IntDef, @StringDef): Groups of integer/string constants annotated with @IntDef/@StringDef — extract as ENUM with type "java_intdef"
2. **Sealed class/interface hierarchies** (Kotlin, Scala, Swift): `sealed class` with object/enum subclasses — extract as ENUM with type "kotlin_sealed_class" / "swift_sealed_enum"
3. **Companion object constant groups** (Kotlin): `companion object` where ALL members are `const val` of same type — extract as ENUM with type "kotlin_companion_enum"
4. **Static final constant groups** (Java/C#): `interface` or `class` where ALL fields are `static final` constants forming a logical group — extract as ENUM with type "java_constant_enum" / "csharp_constant_enum"
5. **C/C++ #define groups**: Consecutive `#define` macros with same prefix forming a logical enumeration — extract as ENUM with type "cpp_define_enum"
6. **Python module-level constant groups**: Module-level UPPER_CASE = integer groups forming a logical enumeration — extract as ENUM with type "python_constant_enum"
7. **Go iota constant groups**: `const` blocks using `iota` — extract as ENUM with type "go_iota_enum"
8. **Rust enum-like patterns**: `struct` with a `kind`/`type` field + constant implementations — extract as ENUM with type "rust_adt_enum"

## Instructions
1. Read the Languages header to identify which languages are present
2. For EACH language found, extract all enum-like patterns from the markdown lines
3. Use the correct language prefix in `type`
4. Include the `language` field in every entry
5. Return ONLY the JSON array, no additional text
6. Every entry MUST include source citation: [Source: file:line]
7. ALWAYS qualify enum names with their enclosing class or file name

## Semantic Markdown to Analyze
{ast_json}
"""

# =============================================================================
# CONSTANT EXTRACTION PROMPT
# =============================================================================

CONSTANT_EXTRACTION_PROMPT = """
You are an expert code analyzer. Extract constant definitions from the Semantic Markdown below.

## Input Format
The input is pre-filtered Semantic Markdown — only constant-relevant nodes are included.
Languages are auto-detected from file extensions and shown in the header.
Each line format: `[language] CONST_NAME = value (modifiers) : type | file:line`

## Output Format
Return a JSON array where each constant entry has:
{
    "name": "CONSTANT_NAME",
    "value": "constant_value",
    "type": "<language>_const|<language>_define|error_code",
    "language": "java|kotlin|cpp|typescript|python|swift|csharp|go|rust|other",
    "usage_context": "Brief description of where/how this constant is used",
    "source": "[Source: file/path.ext:line_number]"
}

The `type` field uses the language prefix (e.g., "java_const", "kotlin_const", "cpp_define").
Error codes (EXIT_*, ERROR_*, ERR_*) should use type "error_code" regardless of language.

## Constant Categories to Extract (ALL of these, not just protocol constants)
1. **Notification/UI constants**: NOTIFICATION_CHANNEL_*, NOTIFICATION_ID_*, UI labels
2. **Preference/Settings constants**: PREF_*, KEY_*, SETTINGS_*, CONFIG_*
3. **Service/Component identifiers**: SERVICE_NAME, SERVER_NAME, APPLICATION_ID, PACKAGE_NAME, AUTHORITY, BINDER_DESCRIPTOR
4. **Permission/Authorization constants**: PERMISSION, FLAG_*, MASK_*, ALLOWED, DENIED, REQUIRED
5. **Action/Intent string constants**: DESCRIPTOR, ACTION_*, INTENT_*, BINDER_*
6. **Error code constants**: EXIT_*, ERROR_*, ERR_* (type must be "error_code")
7. **Protocol/Transport constants**: CMD_*, AUTH_TYPE_*, MAX_PAYLOAD, etc.
8. **Configuration limits**: TIMEOUT, MAX_*, MIN_*, DEFAULT_*, LIMIT_*, SIZE_*
9. **Network/Connection constants**: PORT_*, HOST_*, URL_*, URI_*, ENDPOINT_*
10. **Version/Build constants**: VERSION_*, BUILD_*, API_LEVEL

Do NOT duplicate constants already extracted as ENUM values or Message IDs.
If a constant serves as a message identifier in a protocol (e.g., CMD_CNXN = "CNXN"), list it ONLY in the Message ID Catalog, NOT in Constant Definitions.

## Instructions
1. Read the Languages header to identify which languages are present
2. For EACH language found, extract all constant patterns
3. Include error code patterns (EXIT_*, ERROR_*, ERR_*) with type "error_code"
4. Use the correct language prefix in `type`
5. Include the `language` field in every entry
6. Return ONLY the JSON array, no additional text
7. Every entry MUST include source citation: [Source: file:line]

## Semantic Markdown to Analyze
{ast_json}
"""

# =============================================================================
# IPC EXTRACTION PROMPT
# =============================================================================

IPC_EXTRACTION_PROMPT = """
You are an expert code analyzer. Extract IPC (Inter-Process Communication) patterns from the Semantic Markdown below.

## Input Format
The input is pre-filtered Semantic Markdown — only IPC-relevant nodes and edges are included.
Languages are auto-detected from file extensions and shown in the header.
Node lines: `[language] mechanism - Name extends BaseClass | sig: params → return | file:line`
Edge lines: `source → target [mechanism] | data`

## Output Format
Return a JSON array where each IPC entry has:
{
    "mechanism": "binder|socket|broadcast_receiver|content_provider|intent|messenger|shared_memory|pipe|grpc|channel|jni|content_provider|app_control|message_port|other",
    "source_component": "Component initiating/receiving IPC",
    "target_component": "Target component (if identifiable)",
    "data": "Description of data exchanged or method signatures",
    "language": "java|kotlin|cpp|typescript|python|swift|csharp|go|rust|other",
    "source": "[Source: file/path.ext:line_number]",
    "message_ids": [{"id": "identifier", "value": "0xNN", "direction": "Client→Server|Server→Client|Bidirectional", "payload": "description", "handler": "method"}],
    "signal_events": [{"event": "name", "emitter": "component", "listener": "component", "data_type": "type", "registration": "mechanism"}]
}

The `message_ids` and `signal_events` arrays are optional — include them only when relevant.

## IPC Patterns to Detect (ALL languages, ALL patterns)
1. **Binder/AIDL** (Java/Kotlin): IBinder, Binder, onTransact, transact, bindService, ServiceConnection, AIDL
2. **Broadcast Receiver** (Java/Kotlin): BroadcastReceiver, sendBroadcast, registerReceiver, LocalBroadcastManager
3. **Content Provider** (Java/Kotlin): ContentResolver, IContentProvider, ContentProviderClient
4. **JNI/FFI** (Java/Kotlin/C/C++): native methods, System.loadLibrary, external fun, JNI_OnLoad, dlopen, dlsym
5. **Signal** (C/C++/POSIX): kill(), raise(), signal(), sigaction()
6. **Pipe/Subprocess** (all): popen(), exec(), ProcessBuilder, Runtime.exec(), os.system(), subprocess.Popen
7. **Socket** (all): ServerSocket, Socket, net.Dial, TcpListener, socket.socket()
8. **gRPC** (all): grpc.Dial, ManagedChannelBuilder, tonic::transport::Channel
9. **Shared Memory** (all): mmap, MemoryMappedFile, shared_memory, shmget
10. **Message Queue** (all): KafkaProducer, RabbitMQ, redis, zmq
11. **Intent/Event actions** (Android): Any ACTION_* constant used in Intent construction
12. **Tizen App Control** (JavaScript/TypeScript/C/C++/C#): launchAppControl, launchDefaultAppControl, app_control_create, app_control_send_launch_request, AppControl, SendLaunchRequest
13. **Tizen Message Port** (JavaScript/TypeScript/C/C++/C#): requestLocalMessagePort, requestRemoteMessagePort, sendMessage, message_port_register_local_port, message_port_send_message, LocalMessagePort, RemoteMessagePort
14. **Tizen Broadcast Receiver** (JavaScript/TypeScript/C/C++/C#): broadcastEvent, broadcastTrustedEvent, addEventListener, event_publish, event_add_watch, EventControl, BroadcastEvent, EventReceiver

For Android projects: If AndroidManifest.xml is present, parse it for <receiver>, <service>, <provider>, and <intent-filter> declarations.
For Tizen projects: If tizen-manifest.xml is present, parse it for <service>, <app-control>, and <feature> declarations.
For any project: Check config files (XML, YAML, TOML, JSON) for declared IPC endpoints.

## Message ID / Protocol Constant Extraction
In addition to IPC mechanisms, extract ALL message identifiers used in inter-process communication:
1. **Protocol message types**: A_CNXN, A_AUTH, CMD_OPEN, etc.
2. **Binder/IPC transaction codes**: TRANSACTION_*, BINDER_TRANSACTION_*, or integer constants used in onTransact()/transact()
3. **Intent/Event action strings**: ACTION_* prefix, or string constants used in Intent(), BroadcastReceiver, IntentFilter
4. **Request/Response type codes**: Constants or enums identifying request types in client-server patterns
5. **Function codes/opcodes**: Any integer or string constant used as a command identifier in a protocol

For each Message ID, include: identifier, value (hex where applicable), direction (Client→Server / Server→Client / Bidirectional), payload description, and handler function.

## Signal/Event Mapping Extraction
In addition to IPC mechanisms, extract ALL signal and event mappings:
1. **System lifecycle events**: Boot, shutdown, pause, resume — from manifest declarations or lifecycle handler registrations
2. **Callback/Listener patterns**: onXxxReceived(), onXxxChanged(), onXxxComplete() called by a different component
3. **Observer patterns**: Observer, Subscriber, Listener, or onXxxChanged() — map observable → observer
4. **Broadcast events**: BroadcastReceiver, LocalBroadcastManager, EventBus — map sender and receiver
5. **Custom event dispatchers**: dispatchXxx(), notifyXxx(), emitXxx(), publishXxx() — trace trigger and handler
6. **Async message patterns**: Future, Promise, callback, coroutine continuation — map producer → consumer

For each Signal/Event: specify emitter component, listener component, data type carried, and registration mechanism.

## Instructions
1. Read the Languages header to identify which languages and frameworks are present
2. For EACH language found, identify all IPC patterns from the markdown
3. Also discover NEW IPC patterns not in the predefined mechanism list
4. Include the `language` field in every entry
5. Return ONLY the JSON array, no additional text
6. Every entry MUST include source citation: [Source: file:line]

## Semantic Markdown to Analyze
{ast_json}
"""
