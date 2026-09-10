#!/usr/bin/env python3
"""Centralized rule-based detection patterns for AST analysis.

All language-specific AST node type mappings, IPC patterns, test detection
patterns, and extension mappings are defined here as a single source of truth.
Other modules (parser.py, type_discovery.py, llm_client.py) import from here
instead of maintaining their own copies.
"""

from __future__ import annotations

import os
import re
from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Language extension mapping
# ---------------------------------------------------------------------------

EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cs": "csharp",
    ".rb": "ruby",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".swift": "swift",
    ".php": "php",
    ".sol": "solidity",
    ".vue": "vue",
    ".dart": "dart",
    ".scala": "scala",
    ".m": "objc",
    ".mm": "objc",
}


def get_language_from_extension(file_path: str) -> str:
    """Get language name from file extension."""
    if not file_path:
        return "unknown"
    _, ext = os.path.splitext(file_path)
    return EXTENSION_TO_LANGUAGE.get(ext, "unknown")


def get_extension_map() -> dict[str, str]:
    """Map language name to primary file extension (reverse lookup).

    Returns the most common extension for each language.
    """
    return {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "tsx": ".tsx",
        "go": ".go",
        "rust": ".rs",
        "java": ".java",
        "csharp": ".cs",
        "ruby": ".rb",
        "cpp": ".cpp",
        "c": ".c",
        "kotlin": ".kt",
        "swift": ".swift",
        "php": ".php",
        "solidity": ".sol",
        "vue": ".vue",
        "dart": ".dart",
        "scala": ".scala",
        "objc": ".m",
    }


# ---------------------------------------------------------------------------
# Tree-sitter node type mappings per language
# Maps (language) -> dict of semantic role -> list of TS node types
# ---------------------------------------------------------------------------

CLASS_TYPES: dict[str, list[str]] = {
    "python": ["class_definition"],
    "javascript": ["class_declaration", "class"],
    "typescript": ["class_declaration", "class"],
    "tsx": ["class_declaration", "class"],
    "go": ["type_declaration"],
    "rust": ["struct_item", "enum_item", "impl_item"],
    "java": ["class_declaration", "interface_declaration", "enum_declaration"],
    "c": ["struct_specifier", "type_definition"],
    "cpp": ["class_specifier", "struct_specifier"],
    "csharp": [
        "class_declaration", "interface_declaration",
        "enum_declaration", "struct_declaration",
    ],
    "ruby": ["class", "module"],
    "kotlin": ["class_declaration", "object_declaration"],
    "swift": ["class_declaration", "struct_declaration", "protocol_declaration"],
    "php": ["class_declaration", "interface_declaration"],
    "solidity": [
        "contract_declaration", "interface_declaration", "library_declaration",
        "struct_declaration", "enum_declaration", "error_declaration",
        "user_defined_type_definition",
    ],
}

FUNCTION_TYPES: dict[str, list[str]] = {
    "python": ["function_definition"],
    "javascript": ["function_declaration", "method_definition", "arrow_function"],
    "typescript": ["function_declaration", "method_definition", "arrow_function"],
    "tsx": ["function_declaration", "method_definition", "arrow_function"],
    "go": ["function_declaration", "method_declaration"],
    "rust": ["function_item"],
    "java": ["method_declaration", "constructor_declaration"],
    "c": ["function_definition"],
    "cpp": ["function_definition"],
    "csharp": ["method_declaration", "constructor_declaration"],
    "ruby": ["method", "singleton_method"],
    "kotlin": ["function_declaration"],
    "swift": ["function_declaration", "protocol_function_declaration"],
    "php": ["function_definition", "method_declaration"],
    # Solidity: events and modifiers use kind="Function" because the graph
    # schema has no dedicated kind for them.  State variables are also modeled
    # as Function nodes (public ones auto-generate getters) and distinguished
    # via extra["solidity_kind"].
    "solidity": [
        "function_definition", "constructor_definition", "modifier_definition",
        "event_definition", "fallback_receive_definition",
    ],
}

IMPORT_TYPES: dict[str, list[str]] = {
    "python": ["import_statement", "import_from_statement"],
    "javascript": ["import_statement"],
    "typescript": ["import_statement"],
    "tsx": ["import_statement"],
    "go": ["import_declaration"],
    "rust": ["use_declaration"],
    "java": ["import_declaration"],
    "c": ["preproc_include"],
    "cpp": ["preproc_include"],
    "csharp": ["using_directive"],
    "ruby": ["call"],  # require/require_relative
    "kotlin": ["import_header"],
    "swift": ["import_declaration"],
    "php": ["namespace_use_declaration"],
    "solidity": ["import_directive"],
}

CALL_TYPES: dict[str, list[str]] = {
    "python": ["call"],
    "javascript": ["call_expression", "new_expression"],
    "typescript": ["call_expression", "new_expression"],
    "tsx": ["call_expression", "new_expression"],
    "go": ["call_expression"],
    "rust": ["call_expression", "macro_invocation"],
    "java": ["method_invocation", "object_creation_expression"],
    "c": ["call_expression"],
    "cpp": ["call_expression"],
    "csharp": ["invocation_expression", "object_creation_expression"],
    "ruby": ["call", "method_call"],
    "kotlin": ["call_expression"],
    "swift": ["call_expression"],
    "php": ["function_call_expression", "member_call_expression"],
    "solidity": ["call_expression"],
}

# ENUM node types per language — for extracting enum definitions with values
ENUM_TYPES: dict[str, list[str]] = {
    "python": ["enum_definition"],  # Python 3.11+ enum keyword or enum.Enum class
    "javascript": ["enum_declaration"],
    "typescript": ["enum_declaration"],
    "tsx": ["enum_declaration"],
    "java": ["enum_declaration"],
    "c": ["enum_specifier"],
    "cpp": ["enum_specifier"],
    "csharp": ["enum_declaration"],
    "go": ["type_spec"],  # With type_kind check for "enum"
    "rust": ["enum_item"],
    "kotlin": ["class_declaration"],  # With modifier check for "enum"
    "swift": ["enum_declaration"],
    "php": ["enum_declaration"],
    "ruby": ["class"],  # With inheritance from Enum
    "solidity": ["enum_declaration"],
}

# Constant definition node types per language
CONSTANT_TYPES: dict[str, list[str]] = {
    "python": ["assignment"],  # UPPER_SNAKE_CASE pattern matching
    "javascript": ["lexical_declaration", "variable_declaration"],
    "typescript": ["lexical_declaration", "variable_declaration"],
    "tsx": ["lexical_declaration", "variable_declaration"],
    "java": ["constant_declaration"],  # Only true constant_declaration (static final fields caught by LLM name/modifier filtering)
    "c": ["preproc_def"],
    "cpp": ["preproc_def", "declaration"],
    "csharp": ["constant_declaration"],  # Only true constant_declaration
    "go": ["const_spec"],
    "rust": ["constant_item"],
    "kotlin": ["property_declaration"],
    "swift": ["constant_declaration"],
    "php": ["constant_definition"],
    "ruby": ["assignment"],  # UPPER_CASE pattern
    "solidity": ["constant_variable_declaration"],
}

# IPC pattern detection — maps language -> ipc_mechanism -> call name patterns
IPC_PATTERNS: dict[str, dict[str, list[str]]] = {
    "python": {
        "socket": ["socket.socket", "connect", "bind", "accept", "recv", "send"],
        "http_client": ["requests.get", "requests.post", "urllib.request.urlopen", "http.client.HTTPConnection"],
        "grpc": ["grpc.insecure_channel", "grpc.secure_channel", "Stub"],
        "message_queue": ["kafka.KafkaProducer", "kafka.KafkaConsumer", "pika.BlockingConnection"],
        "subprocess": ["subprocess.Popen", "subprocess.run", "subprocess.call", "os.system"],
        "pipe": ["os.pipe", "os.mkfifo", "multiprocessing.Pipe"],
        "shared_memory": ["multiprocessing.shared_memory.SharedMemory", "mmap.mmap"],
        "signal": ["signal.signal", "os.kill", "signal.pause"],
    },
    "java": {
        "socket": ["ServerSocket", "Socket", "DatagramSocket", "SocketChannel"],
        "http_client": ["HttpURLConnection", "HttpClient", "RestTemplate", "WebClient"],
        "grpc": ["ManagedChannelBuilder", "newBlockingStub", "newStub"],
        "binder": ["IBinder", "Messenger", "AIDL", "Binder"],
        "broadcast_receiver": ["sendBroadcast", "registerReceiver", "LocalBroadcastManager"],
        "content_provider": ["ContentResolver", "IContentProvider", "ContentProviderClient", "provider.call"],
        "jni": ["native", "System.loadLibrary", "JNI_OnLoad", "nativeMethods", "RegisterNatives"],
        "message_queue": ["KafkaConsumer", "KafkaProducer", "ConnectionFactory"],
        "rmi": ["UnicastRemoteObject", "Naming.lookup", "Registry"],
    },
    "c": {
        "socket": ["socket", "bind", "listen", "accept", "connect", "send", "recv"],
        "pipe": ["pipe", "mkfifo", "popen"],
        "shared_memory": ["shmget", "shmat", "mmap", "munmap"],
        "signal": ["signal", "kill", "sigaction"],
        "dbus": ["dbus_connection_open", "dbus_message_new"],
        "app_control": ["app_control_create", "app_control_send_launch_request", "app_control_cb"],
        "message_port": ["message_port_register_local_port", "message_port_check_remote_port", "message_port_send_message"],
        "broadcast_receiver": ["event_publish", "event_add_watch", "event_cb"],
        "jni": ["JNI_OnLoad", "JNI_OnUnload", "RegisterNatives", "GetJavaVM", "JNIEnv"],
    },
    "cpp": {
        "socket": ["socket", "bind", "listen", "accept", "connect", "asio::ip::tcp"],
        "grpc": ["grpc::Channel", "grpc::ClientContext", "NewStub"],
        "pipe": ["pipe", "popen", "boost::pipe"],
        "shared_memory": ["boost::interprocess::shared_memory_object", "mmap"],
        "signal": ["signal", "kill", "sigaction"],
        "jni": ["JNI_OnLoad", "JNI_OnUnload", "RegisterNatives", "GetJavaVM", "JNIEnv"],
        "app_control": ["app_control_create", "app_control_send_launch_request", "app_control_cb"],
        "message_port": ["message_port_register_local_port", "message_port_check_remote_port", "message_port_send_message"],
        "broadcast_receiver": ["event_publish", "event_add_watch", "event_cb"],
    },
    "csharp": {
        "socket": ["TcpListener", "TcpClient", "UdpClient", "Socket"],
        "http_client": ["HttpClient", "WebRequest", "RestClient"],
        "grpc": ["GrpcChannel", "CallInvoker", "ClientBase"],
        "named_pipe": ["NamedPipeServerStream", "NamedPipeClientStream"],
        "shared_memory": ["MemoryMappedFile", "MemoryMappedViewAccessor"],
        "wcf": ["ServiceHost", "ChannelFactory", "DuplexClient"],
        "app_control": ["AppControl", "SendLaunchRequest", "SendTerminateRequest"],
        "message_port": ["LocalMessagePort", "RemoteMessagePort", "TrustedMessagePort", "Listen", "Send"],
        "broadcast_receiver": ["EventControl", "BroadcastEvent", "EventReceiver", "Received"],
        "message_queue": ["ConnectionMultiplexer", "IBus", "BusCreator"],
    },
    "go": {
        "socket": ["net.Dial", "net.Listen", "net.Pipe"],
        "http_client": ["http.Get", "http.Post", "http.Client"],
        "grpc": ["grpc.Dial", "grpc.NewClient", "ClientConn"],
        "pipe": ["io.Pipe", "os.Pipe"],
        "signal": ["signal.Notify", "syscall.Kill"],
    },
    "rust": {
        "socket": ["TcpStream", "TcpListener", "UdpSocket"],
        "grpc": ["tonic::transport::Channel"],
        "pipe": ["std::process::Command", "os_pipe"],
        "shared_memory": ["shared_memory"],
        "signal": ["signal_hook"],
    },
    "kotlin": {
        "socket": ["ServerSocket", "Socket", "DatagramSocket"],
        "http_client": ["HttpClient", "OkHttpClient", "Retrofit"],
        "grpc": ["ManagedChannelBuilder", "newBlockingStub"],
        "binder": ["IBinder", "Messenger", "Binder"],
        "broadcast_receiver": ["sendBroadcast", "registerReceiver", "LocalBroadcastManager"],
        "content_provider": ["ContentResolver", "IContentProvider", "ContentProviderClient", "provider.call"],
        "jni": ["native", "System.loadLibrary", "external fun", "JNI_OnLoad"],
    },
    "swift": {
        "socket": ["Socket", "NWConnection", "NWListener"],
        "http_client": ["URLSession", "URLRequest"],
        "xpc": ["xpc_connection_create", "xpc_session_create"],
        "pipe": ["Pipe", "FileHandle"],
    },
    "javascript": {
        "http_client": ["fetch", "axios", "XMLHttpRequest"],
        "socket": ["WebSocket", "net.Socket", "net.Server"],
        "subprocess": ["child_process.exec", "child_process.spawn", "child_process.fork"],
        "message_queue": ["amqp", "kafka", "redis"],
        # Tizen IPC patterns
        "app_control": ["launchAppControl", "launchDefaultAppControl"],
        "message_port": ["requestLocalMessagePort", "requestRemoteMessagePort", "requestTrustedLocalMessagePort", "requestTrustedRemoteMessagePort", "sendMessage"],
        "broadcast_receiver": ["broadcastEvent", "broadcastTrustedEvent", "addEventListener", "removeEventListener"],
    },
    "typescript": {
        "http_client": ["fetch", "axios", "XMLHttpRequest", "node-fetch"],
        "socket": ["WebSocket", "net.Socket", "net.Server", "socket.io"],
        "grpc": ["grpc.Client", "grpc.Server", "@grpc/grpc-js"],
        "subprocess": ["child_process.exec", "child_process.spawn", "child_process.fork"],
        # TypeScript-specific IPC patterns
        "event_emitter": ["EventEmitter", "vscode.Event", "EventEmitter.on", "EventEmitter.emit", "EventEmitter.once"],
        "rxjs": ["Subject", "BehaviorSubject", "ReplaySubject", "AsyncSubject", "Observable"],
        "post_message": ["window.postMessage", "addEventListener('message')", "onmessage"],
        "worker": ["new Worker", "worker_threads", "parentPort", "worker.postMessage"],
        "channel": ["MessageChannel", "MessagePort", "BroadcastChannel"],
        # Tizen IPC patterns
        "app_control": ["launchAppControl", "launchDefaultAppControl"],
        "message_port": ["requestLocalMessagePort", "requestRemoteMessagePort", "requestTrustedLocalMessagePort", "requestTrustedRemoteMessagePort", "sendMessage"],
        "broadcast_receiver": ["broadcastEvent", "broadcastTrustedEvent", "addEventListener", "removeEventListener"],
    },
    "tsx": {
        "http_client": ["fetch", "axios", "XMLHttpRequest"],
        "socket": ["WebSocket"],
        # Tizen IPC patterns
        "app_control": ["launchAppControl", "launchDefaultAppControl"],
        "message_port": ["requestLocalMessagePort", "requestRemoteMessagePort", "requestTrustedLocalMessagePort", "requestTrustedRemoteMessagePort", "sendMessage"],
        "broadcast_receiver": ["broadcastEvent", "broadcastTrustedEvent", "addEventListener", "removeEventListener"],
    },
    "ruby": {
        "socket": ["TCPSocket", "TCPServer", "UDPSocket"],
        "http_client": ["Net::HTTP", "HTTParty", "Faraday"],
        "pipe": ["IO.pipe", "Open3"],
        "subprocess": ["system", "exec", "Open3"],
    },
    "php": {
        "socket": ["socket_create", "socket_bind", "socket_connect"],
        "http_client": ["curl_init", "file_get_contents", "Guzzle"],
        "pipe": ["popen", "proc_open"],
        "shared_memory": ["shmop_open", "shmop_read"],
    },
}


# ---------------------------------------------------------------------------
# IPC Mechanism Enum — strict values to prevent hallucination
# ---------------------------------------------------------------------------


# Module-level storage for dynamically discovered IPC mechanisms.
# Kept outside the enum class to avoid Python's Enum treating it as a member.
_ipc_discovered_mechanisms: dict[str, str] = {}


class IpcMechanism(str, Enum):
    """Strict enum of IPC mechanisms detectable from code.

    Only these values are allowed in EdgeInfo.extra["ipc_mechanism"].
    This prevents LLM hallucination of non-existent IPC types.

    Note: New IPC mechanisms can be dynamically discovered via LLM
    and added via IpcMechanism.add_discovered_mechanism().
    """

    SOCKET = "socket"                          # TCP/UDP/Unix socket
    GRPC = "grpc"                              # gRPC (all languages)
    MESSAGE_QUEUE = "message_queue"            # Kafka, RabbitMQ, ActiveMQ
    PIPE = "pipe"                              # Anonymous pipe
    SHARED_MEMORY = "shared_memory"            # mmap, shmget, MemoryMappedFile
    SIGNAL = "signal"                          # POSIX signals
    BROADCAST_RECEIVER = "broadcast_receiver"  # Android BroadcastReceiver
    BINDER = "binder"                          # Android Binder/AIDL
    DBUS = "dbus"                              # D-Bus (Linux)
    NAMED_PIPE = "named_pipe"                  # Windows Named Pipe
    WCF = "wcf"                                # Windows Communication Foundation
    RMI = "rmi"                                # Java RMI
    XPC = "xpc"                                # macOS XPC
    HTTP_CLIENT = "http_client"                # HTTP REST client (cross-process)
    SUBPROCESS = "subprocess"                  # subprocess.Popen, exec, system()
    CONTENT_PROVIDER = "content_provider"      # Android ContentProvider
    JNI = "jni"                                # Java Native Interface / FFI
    EVENT_EMITTER = "event_emitter"            # Node.js / VS Code EventEmitter
    RXJS = "rxjs"                              # RxJS Subject/Observable
    POST_MESSAGE = "post_message"              # window.postMessage (browser)
    WORKER = "worker"                          # Web Worker / Worker Thread
    CHANNEL = "channel"                        # MessageChannel / MessagePort
    # Tizen IPC mechanisms
    APP_CONTROL = "app_control"                # Tizen App Control (app launch + data)
    MESSAGE_PORT = "message_port"              # Tizen Message Port (async messaging)

    @classmethod
    def add_discovered_mechanism(cls, name: str, value: str) -> None:
        """Add a dynamically discovered IPC mechanism.

        Args:
            name: The mechanism name (e.g., "content_provider")
            value: The mechanism value (same as name, lowercase)
        """
        _ipc_discovered_mechanisms[name.lower()] = value.lower()

    @classmethod
    def get_all_mechanisms(cls) -> set[str]:
        """Get all known IPC mechanisms (static + discovered)."""
        mechanisms = {m.value for m in cls}
        mechanisms.update(_ipc_discovered_mechanisms.values())
        return mechanisms

    @classmethod
    def is_valid_mechanism(cls, value: str) -> bool:
        """Check if a value is a valid IPC mechanism."""
        return value.lower() in cls.get_all_mechanisms()

    @classmethod
    def reset_discovered_mechanisms(cls) -> None:
        """Clear all dynamically discovered IPC mechanisms.

        This is important for test isolation — without it, mechanisms
        discovered in one test persist and pollute subsequent test runs.
        """
        _ipc_discovered_mechanisms.clear()



# ---------------------------------------------------------------------------
# Test detection patterns
# ---------------------------------------------------------------------------

TEST_PATTERNS = [
    re.compile(r"^test_"),
    re.compile(r"^Test"),
    re.compile(r"_test$"),
    re.compile(r"\.test\."),
    re.compile(r"\.spec\."),
    re.compile(r"_spec$"),
]

TEST_FILE_PATTERNS = [
    re.compile(r"test_.*\.py$"),
    re.compile(r".*_test\.py$"),
    re.compile(r".*\.test\.[jt]sx?$"),
    re.compile(r".*\.spec\.[jt]sx?$"),
    re.compile(r".*_test\.go$"),
    re.compile(r"tests?/"),
]


def is_test_file(path: str) -> bool:
    """Check if a file path matches test file patterns."""
    return any(p.search(path) for p in TEST_FILE_PATTERNS)


def is_test_function(name: str, file_path: str) -> bool:
    """A function is a test if its name matches test patterns or it lives
    in a test file and has a test-runner name (describe, it, test, etc.).
    """
    if any(p.search(name) for p in TEST_PATTERNS):
        return True
    # In test files, treat common JS/TS test-runner wrappers as tests
    if is_test_file(file_path) and name in (
        "describe", "it", "test", "beforeEach", "afterEach",
        "beforeAll", "afterAll",
    ):
        return True
    return False


# ---------------------------------------------------------------------------
# Node kind filtering per extraction type (for LLM client)
# ---------------------------------------------------------------------------

ENUM_KINDS = {"Enum", "enum_declaration", "enum_class", "enum_specifier",
              "enum_item", "annotation_declaration", "annotation_type_definition",
              "sealed_class", "object_declaration", "interface_declaration"}

CONSTANT_KINDS = {"Constant", "constant_declaration", "field_declaration",
                  "preproc_def", "const_spec", "constant_item", "property_declaration",
                  "lexical_declaration", "variable_declaration"}

# IPC_KINDS: Only nodes with explicit IPC-specific extra fields are candidates.
# Matching on kind alone (e.g. "Function", "Class") would flag every function/class
# as an IPC candidate, producing excessive noise in the Gap 8 coverage report.
# Use IPC_NAME_PATTERNS and extra.get("ipc_mechanism") for actual IPC detection.
IPC_KINDS = set()  # Intentionally empty — IPC is detected via edges and extra fields



# ---------------------------------------------------------------------------
# Name patterns for additional filtering (for LLM client)
# ---------------------------------------------------------------------------

ENUM_NAME_PATTERNS = re.compile(
    r'(enum|Enum|ENUM|IntDef|intdef|StringDef|stringdef|@interface|annotation_type|'
    r'sealed_class|sealed_interface|companion_object|object_declaration|'
    r'flag|Flag|FLAG)',
    re.IGNORECASE
)

# Constant name patterns - strict matching to avoid false positives on function names.
# Pattern 1: Pure UPPER_SNAKE_CASE (3+ chars) - most reliable indicator
# Pattern 2: Specific error/status code prefixes (EXIT_, ERROR_, ERR_, etc.)
# Pattern 3: Specific constant-like suffixes (_ID, _NAME, _PATH, etc.)
# IMPORTANT: All patterns require the string to START with the pattern to avoid
# matching function names like "read_json_from_path" (contains PATH but isn't a constant).
CONSTANT_NAME_PATTERNS = re.compile(
    r'^(?:'
    # Pattern 1: UPPER_SNAKE_CASE (minimum 3 chars, must start with uppercase)
    r'[A-Z][A-Z0-9_]{2,}'
    r'|'
    # Pattern 2: Specific prefixes that indicate constants
    r'(?:EXIT_|ERROR_|ERR_|STATUS_|CODE_|MAX_|MIN_|DEFAULT_|'
    r'NOTIFICATION_|CHANNEL_|PREF_|KEY_|SETTINGS_|CONFIG_|'
    r'FLAG_|MASK_|PERMISSION_|AUTHORITY_|'
    r'DESCRIPTOR_|ACTION_|INTENT_|BINDER_|SERVICE_|SERVER_|'
    r'APPLICATION_ID|PACKAGE_NAME|VERSION_|BUILD_|'
    r'TIMEOUT_|SIZE_|COUNT_|PORT_|HOST_|URI_|'
    r'ENABLED|DISABLED|SUPPORTED|REQUIRED)'
    r')$'
)

IPC_NAME_PATTERNS = re.compile(
    r'(Binder|AIDL|ServiceConnection|BroadcastReceiver|ContentProvider|'
    r'Intent|Messenger|Socket|Channel|Pipe|SharedMemory|gRPC|'
    r'IInterface|Stub|Proxy|Aidl|IPC|RemoteException|'
    r'sendBroadcast|registerReceiver|bindService|connect|transact|'
    # Tizen IPC patterns
    r'app_control|message_port|AppControl|MessagePort|'
    r'launchAppControl|requestLocalMessagePort|sendMessage|'
    r'broadcastEvent|EventControl|BroadcastEvent|EventReceiver|'
    r'event_publish|event_add_watch|event_cb)',
    re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def parse_json_from_markdown(response: str) -> Any:
    """Extract and parse JSON from an LLM response string.

    Handles three cases:
    1. Raw JSON string
    2. JSON inside a ```json ... ``` markdown code block
    3. Bare JSON array/object embedded in text

    Args:
        response: Raw LLM response text

    Returns:
        Parsed Python object (list, dict, or None if parsing fails)
    """
    import json as _json

    if not response:
        return None

    # Try direct JSON parse
    try:
        return _json.loads(response)
    except _json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ``` code block
    json_block_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    if json_block_match:
        try:
            return _json.loads(json_block_match.group(1))
        except _json.JSONDecodeError:
            pass

    # Try finding any JSON-like structure
    json_match = re.search(r'\[\s*\{.*\}\s*\]|\{\s*".*".*\}', response, re.DOTALL)
    if json_match:
        try:
            return _json.loads(json_match.group())
        except _json.JSONDecodeError:
            pass

    return None

