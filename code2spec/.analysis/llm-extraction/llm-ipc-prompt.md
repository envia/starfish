
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
# Languages: c (930), cpp (809), java (11), javascript (22), python (43)

## IPC Patterns
- [javascript] Function - runWithMDNData | sig: (starfish_data) | /home/hwang/work/D/starfish_/docs/webpages/webapi/webapi_main.js:163
- [cpp] Function - eventtargetConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                                 size_t argc, ValueRef** argv,
                                 OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/EventTargetCustomBinding.cpp:30
- [cpp] Function - geopositionCallbackFunction | sig: (Document* document, Geoposition* pos,
                                        void* data) → void | /home/hwang/work/D/starfish_/src/binding/GeolocationCustomBinding.cpp:32
- [cpp] Function - geopositionErrorCallbackFunction | sig: (Document* document,
                                             PositionError* error, void* data) → void | /home/hwang/work/D/starfish_/src/binding/GeolocationCustomBinding.cpp:44
- [cpp] Function - htmlelementConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                                 size_t argc, ValueRef** argv,
                                 OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/HTMLElementCustomBinding.cpp:32
- [cpp] Function - imagedataConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                               size_t argc, ValueRef** argv,
                               OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/ImageDataCustomBinding.cpp:29
- [cpp] Function - mediastreamConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                                 size_t argc, ValueRef** argv,
                                 OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/MediaStreamCustomBinding.cpp:30
- [cpp] Function - initBinding | sig: () → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingInstance.cpp:288
- [cpp] Function - initJavaScriptBinding | sig: (ContextRef* context,
                                                  ExecutionStateRef* state) → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingInstance.cpp:525
- [c] Function - initBinding | sig: () → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingInstance.h:77
- [c] Function - initJavaScriptBinding | sig: (Escargot::ContextRef* context,
                                       Escargot::ExecutionStateRef* state) → virtual void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingInstance.h:205
- [cpp] Function - _setListenerAvplayFunction | sig: (ExecutionStateRef* state,
                                            ValueRef* thisValue, size_t argc,
                                            ValueRef** argv,
                                            bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/ScriptBindingWindowInstance.cpp:219
- [cpp] Function - initJavaScriptBinding | sig: (
    ContextRef* context, ExecutionStateRef* state) → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingWindowInstance.cpp:245
- [cpp] Function - initJavaScriptGlobalBinding | sig: (
    ScriptExecutionState state, ScriptBindingInstance* scriptBindingInstance) → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:98
- [cpp] Function - initJavaScriptGlobalBinding | sig: (
    ScriptExecutionState state, ScriptBindingInstance* scriptBindingInstance) → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:110
- [cpp] Function - initJavaScriptGlobalBinding | sig: (
    ScriptExecutionState state, ScriptBindingInstance* scriptBindingInstance) → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:121
- [cpp] Function - initJavaScriptBinding | sig: (
    Escargot::ContextRef* context, Escargot::ExecutionStateRef* state) → void | /home/hwang/work/D/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:144
- [cpp] Function - fetchScriptBindingInstance | sig: (ContextRef* ctx) → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/binding/ScriptWrappable.cpp:548
- [cpp] Function - generateScriptObject | sig: () → ScriptObject | /home/hwang/work/D/starfish_/src/binding/ScriptWrappable.cpp:744
- [cpp] Function - createAttributeStringEventFunction | sig: (EventTarget* target,
                                               String* functionBody,
                                               bool& result) → ScriptValue | /home/hwang/work/D/starfish_/src/binding/ScriptWrappable.cpp:977
- [cpp] Function - initDebuggerIfNeeds | sig: (ScriptBindingInstance* instance) → void | /home/hwang/work/D/starfish_/src/binding/ScriptWrappable.cpp:1431
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/binding/ScriptWrappable.h:526
- [cpp] Function - urlsearchparamsConstructor | sig: (ExecutionStateRef* state,
                                     ValueRef* thisValue, size_t argc,
                                     ValueRef** argv,
                                     OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/URLSearchParamsCustomBinding.cpp:28
- [cpp] Function - timeoutHandler | sig: (void* data) → void | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:100
- [cpp] Function - setTimeoutWindowFunction | sig: (ExecutionStateRef* state,
                                   ValueRef* thisValue, size_t argc,
                                   ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:111
- [cpp] Function - setIntervalWindowFunction | sig: (ExecutionStateRef* state,
                                    ValueRef* thisValue, size_t argc,
                                    ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:159
- [cpp] Function - requestAnimationFrameHandler | sig: (void* data) → void | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:208
- [cpp] Function - requestAnimationFrameWindowFunction | sig: (ExecutionStateRef* state,
                                              ValueRef* thisValue, size_t argc,
                                              ValueRef** argv,
                                              bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:294
- [cpp] Function - screenShotTimeoutHandler | sig: (void* data) → void | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:431
- [cpp] Function - testAssertFunction | sig: (ExecutionStateRef* state,
                                    ValueRef* thisValue, size_t argc,
                                    ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:723
- [cpp] Function - wptTestEndFunction | sig: (ExecutionStateRef* state,
                                    ValueRef* thisValue, size_t argc,
                                    ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:772
- [cpp] Function - testImgDiffFunction | sig: (ExecutionStateRef* state,
                                     ValueRef* thisValue, size_t argc,
                                     ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WindowCustomBinding.cpp:795
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/binding/WindowHoldable.cpp:38
- [c] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/binding/WindowHoldable.h:43
- [cpp] File - /home/hwang/work/D/starfish_/src/binding/WindowProxy.cpp | /home/hwang/work/D/starfish_/src/binding/WindowProxy.cpp:1
- [cpp] Function - WindowProxy | sig: (Window* window) | /home/hwang/work/D/starfish_/src/binding/WindowProxy.cpp:37
- [cpp] Function - updateSource | sig: (Window* window) → void | /home/hwang/work/D/starfish_/src/binding/WindowProxy.cpp:43
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/binding/WindowProxy.cpp:129
- [c] File - /home/hwang/work/D/starfish_/src/binding/WindowProxy.h | /home/hwang/work/D/starfish_/src/binding/WindowProxy.h:1
- [c] Constant - __StarfishWindowProxy__ | /home/hwang/work/D/starfish_/src/binding/WindowProxy.h:21
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/binding/WindowProxy.h:35
- [cpp] Function - timeoutHandler | sig: (void* data) → void | /home/hwang/work/D/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp:45
- [cpp] Function - setTimeoutWorkerGlobalScopeFunction | sig: (ExecutionStateRef* state,
                                              ValueRef* thisValue, size_t argc,
                                              NULLABLE ValueRef** argv,
                                              bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp:62
- [cpp] Function - setIntervalWorkerGlobalScopeFunction | sig: (ExecutionStateRef* state,
                                               ValueRef* thisValue, size_t argc,
                                               NULLABLE ValueRef** argv,
                                               bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp:113
- [cpp] Function - emit | sig: (rapidjson::Document& doc) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPCommand.cpp:42
- [cpp] File - /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.cpp | /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.cpp:1
- [cpp] Function - CDPConnection | sig: (CDPServer* server, int fd) | /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.cpp:39
- [cpp] Function - ~CDPConnection | sig: () | /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.cpp:46
- [c] File - /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.h | /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.h:1
- [c] Constant - __StarfishCDPConnection__ | /home/hwang/work/D/starfish_/src/core/cdp/CDPConnection.h:21
- [cpp] Function - onConnectionClosed | sig: () → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.cpp:214
- [cpp] Function - onConnectionClosedOnMain | sig: (size_t, void* data) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.cpp:224
- [cpp] Function - resetConnectionState | sig: () → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.cpp:229
- [cpp] Function - route | sig: (CDPCommand& cmd, const std::string& domain,
                          const std::string& method) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.cpp:390
- [cpp] Function - emitConsoleForWebView | sig: (WebView* webView, const char* level,
                                          const std::string& text,
                                          Escargot::ValueRef** argv,
                                          size_t argc) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.cpp:1594
- [cpp] Function - emitBindingCalled | sig: (WebView* webView, const std::string& name,
                                      const std::string& payload) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.cpp:1701
- [c] Function - onConnectionClosed | sig: () → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.h:75
- [c] Function - emitBindingCalled | sig: (WebView* webView, const std::string& name,
                           const std::string& payload) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.h:97
- [c] Function - fetch | sig: () → FetchDomain * | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.h:144
- [c] Function - onConnectionClosedOnMain | sig: (size_t handle, void* data) → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.h:197
- [c] Function - resetConnectionState | sig: () → void | /home/hwang/work/D/starfish_/src/core/cdp/CDPDispatcher.h:198
- [cpp] Function - acceptLoop | sig: (void* data) → void * | /home/hwang/work/D/starfish_/src/core/cdp/CDPServer.cpp:97
- [cpp] Function - processMessage | sig: (CDPCommand& cmd,
                                       const std::string& method) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/DOMDebuggerDomain.cpp:58
- [cpp] Function - processMessage | sig: (CDPCommand& cmd, const std::string& method) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/DOMDomain.cpp:87
- [cpp] Function - finishNavigation | sig: (const std::string& sessionId) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/PageDomain.cpp:1120
- [cpp] Function - processMessage | sig: (CDPCommand& cmd, const std::string& method) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:67
- [cpp] Function - bindingNativeCallback | sig: (ExecutionStateRef* state,
                                       ValueRef* thisValue, size_t argc,
                                       ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:289
- [cpp] Function - injectBinding | sig: (WebView* wv, const std::string& name) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:320
- [cpp] Function - callFunctionOn | sig: (WebView* wv, BrowsingContext* bc,
                                   CDPCommand& cmd) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:458
- [cpp] Function - compileScript | sig: (WebView* wv, BrowsingContext* bc,
                                  CDPCommand& cmd) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:623
- [cpp] Function - getProperties | sig: (WebView* wv, BrowsingContext* bc,
                                  CDPCommand& cmd) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:753
- [cpp] Function - globalLexicalScopeNames | sig: (WebView* wv, CDPCommand& cmd) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:845
- [cpp] Function - evaluateSource | sig: (WebView* wv, BrowsingContext* bc,
                                   const std::string& exprStr,
                                   bool returnByValue, bool awaitPromise,
                                   CDPCommand& cmd) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.cpp:892
- [c] Function - injectBinding | sig: (WebView* wv, const std::string& name) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/RuntimeDomain.h:44
- [cpp] Function - processMessage | sig: (CDPCommand& cmd, const std::string& method) → void | /home/hwang/work/D/starfish_/src/core/cdp/domains/TracingDomain.cpp:71
- [cpp] Function - ContentSecurityPolicy | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/csp/ContentSecurityPolicy.cpp:39
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/CustomElementRegistry.cpp:91
- [cpp] Function - define | sig: (String* name,
                                   CustomElementConstructor* constructorInput,
                                   ElementDefinitionOptions options) → void | /home/hwang/work/D/starfish_/src/core/dom/CustomElementRegistry.cpp:222
- [cpp] Function - whenDefined | sig: (String* name) → Promise * | /home/hwang/work/D/starfish_/src/core/dom/CustomElementRegistry.cpp:596
- [cpp] Function - enqueueElementOnAppropriateElementQueue | sig: (
    HTMLCustomElement* element) → void | /home/hwang/work/D/starfish_/src/core/dom/CustomElementRegistry.cpp:677
- [cpp] Function - invokeCustomElementReaction | sig: (
    HTMLCustomElement* element, CustomElementCallbackType type,
    Optional<ScriptValue*> data) → void | /home/hwang/work/D/starfish_/src/core/dom/CustomElementRegistry.cpp:739
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/CustomElementRegistry.h:147
- [cpp] Function - DOMException | sig: (ExecutionContext* executionContext, Code code,
                           const char* message) | /home/hwang/work/D/starfish_/src/core/dom/DOMException.cpp:92
- [cpp] Function - DOMException | sig: (ExecutionContext* executionContext, String* message,
                           String* name) | /home/hwang/work/D/starfish_/src/core/dom/DOMException.cpp:143
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMException.cpp:165
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMImplementation.cpp:42
- [cpp] Function - createDocument | sig: (
    Optional<String*> namespaceParameter, String* qualifiedName,
    Optional<DocumentType*> doctype) → XMLDocument * | /home/hwang/work/D/starfish_/src/core/dom/DOMImplementation.cpp:64
- [cpp] Function - createHTMLDocument | sig: (Optional<String*> title) → Document * | /home/hwang/work/D/starfish_/src/core/dom/DOMImplementation.cpp:112
- [cpp] Function - fromFloat32Array | sig: (ExecutionContext* executionContext,
                                       ScriptFloat32Array array32) → DOMMatrix * | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrix.cpp:36
- [cpp] Function - fromFloat64Array | sig: (ExecutionContext* executionContext,
                                       ScriptFloat64Array array64) → DOMMatrix * | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrix.cpp:91
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrix.cpp:481
- [cpp] Function - fromFloat32Array | sig: (
    ExecutionContext* executionContext, ScriptFloat32Array array32) → DOMMatrixReadOnly * | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrixReadOnly.cpp:150
- [cpp] Function - fromFloat64Array | sig: (
    ExecutionContext* executionContext, ScriptFloat64Array array64) → DOMMatrixReadOnly * | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrixReadOnly.cpp:202
- [cpp] Function - toFloat32Array | sig: () → ScriptFloat32Array | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrixReadOnly.cpp:506
- [cpp] Function - toFloat64Array | sig: () → ScriptFloat64Array | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrixReadOnly.cpp:570
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMMatrixReadOnly.cpp:808
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMParser.cpp:46
- [cpp] Function - parseFromString | sig: (String* str, String* type) → Document * | /home/hwang/work/D/starfish_/src/core/dom/DOMParser.cpp:165
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMParser.h:35
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMPointReadOnly.cpp:37
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMQuad.cpp:79
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMRectList.cpp:45
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMRectReadOnly.cpp:56
- [cpp] Function - toJSON | sig: () → ScriptObject | /home/hwang/work/D/starfish_/src/core/dom/DOMRectReadOnly.cpp:72
- [cpp] Function - DOMStringList | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/dom/DOMStringList.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMStringMap.cpp:110
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMStringMap.h:36
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMTokenList.cpp:35
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/DOMTokenList.h:38
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:270
- [cpp] Function - resumeDocumentParsing | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:667
- [cpp] Function - executeModule | sig: (Document* document,
                          GCVector<Document::ScriptModuleData*>& moduleScripts,
                          size_t startSize, bool fromParser) → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:700
- [cpp] Function - notifyDomContentLoaded | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:758
- [cpp] Function - dispose | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:866
- [cpp] Function - focusRing | sig: () → const GCAtomicVector<Element*> & | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:1775
- [cpp] Function - loadBuiltinPolyfill | sig: (String* localPath) → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:2209
- [cpp] Function - signalSlotChange | sig: (HTMLSlotElement* slot) → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:2679
- [cpp] Function - ensureMutationAndSlotMicrotaskQueued | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:2692
- [cpp] Function - finalizeObservation | sig: (Node* node) → void | /home/hwang/work/D/starfish_/src/core/dom/Document.cpp:2914
- [c] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Document.h:318
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name, Optional<String*> old,
                                  String* value, bool attributeCreated,
                                  bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:596
- [cpp] Function - didNodeInserted | sig: (Node* parent, Node* newChild) → void | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:779
- [cpp] Function - didNodeRemoved | sig: (Node* parent, Node* oldChild) → void | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:788
- [cpp] Function - elementScrollPropertyChanged | sig: (Element* element) → void | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:1387
- [cpp] Function - supportsFocus | sig: () → bool | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:2461
- [cpp] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:2493
- [cpp] Function - tabIndexSetExplicitly | sig: () → bool | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:2509
- [cpp] Function - makeKeyframesFromObject | sig: (ScriptObject object,
                                      GCVector<StyleRuleBase*>& keyframeRules) → void | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:2537
- [cpp] Function - setPointerCapture | sig: (int32_t param) → void | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:2859
- [cpp] Function - requestFullscreen | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/dom/Element.cpp:2886
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Event.cpp:182
- [cpp] Function - call | sig: (Event* event) → ScriptValue | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:64
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:116
- [cpp] Function - getEventListeners | sig: (
    const String* eventType) → Optional<GCVector<EventListener*>*> | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:121
- [cpp] Function - addEventListener | sig: (const String* eventType,
                                   EventListener* listener, bool useCapture) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:135
- [cpp] Function - removeEventListener | sig: (const String* eventType,
                                      EventListener* listener, bool useCapture) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:176
- [cpp] Function - dispatchEvent | sig: (Event* event) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:286
- [cpp] Function - hasListenerForTypeOnPath | sig: (const String* eventType) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:293
- [cpp] Function - dispatchEvent | sig: (EventTarget* origin, Event* event) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:422
- [cpp] Function - dispatchEventForTarget | sig: (EventTarget* origin, Event* event) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:842
- [cpp] Function - setAttributeEventListener | sig: (const QualifiedName& eventTypeName,
                                            String* str, EventTarget* target) → void | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:869
- [cpp] Function - setAttributeEventListener | sig: (const String* eventType,
                                            EventListener* listener) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:883
- [cpp] Function - getAttributeEventListener | sig: (const String* eventType) → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:891
- [cpp] Function - clearAttributeEventListener | sig: (const String* eventType) → bool | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.cpp:915
- [c] Function - setAttributeEventListener | sig: (const QualifiedName& eventTypeName,
                                   EventListener* l) → void | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.h:194
- [c] Function - getAttributeEventListener | sig: (const QualifiedName& eventType) → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.h:204
- [c] Function - clearAttributeEventListener | sig: (const QualifiedName& name) → void | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.h:210
- [c] Function - attributeEventListener | sig: (const QualifiedName& name) → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.h:216
- [c] Function - clearEventListeners | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/EventTarget.h:222
- [cpp] Function - addActiveWebSockets | sig: (WebSocket* webSocket) → void | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.cpp:182
- [cpp] Function - removeActiveWebSockets | sig: (WebSocket* webSocket) → void | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.cpp:187
- [cpp] Function - disposeActiveWebSockets | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.cpp:196
- [c] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.h:66
- [c] Function - addActiveWebSockets | sig: (WebSocket* webSocket) → void | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.h:102
- [c] Function - removeActiveWebSockets | sig: (WebSocket* webSocket) → void | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.h:103
- [c] Function - disposeActiveWebSockets | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/ExecutionContext.h:104
- [cpp] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/HTMLAnchorElement.cpp:53
- [cpp] Function - handleDefaultEvent | sig: (Event* event) → bool | /home/hwang/work/D/starfish_/src/core/dom/HTMLAnchorElement.cpp:104
- [cpp] Function - handleDefaultEvent | sig: (Event* event) → bool | /home/hwang/work/D/starfish_/src/core/dom/HTMLAreaElement.cpp:129
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name,
                                          Optional<String*> old, String* value,
                                          bool attributeCreated,
                                          bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLBodyElement.cpp:59
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/HTMLCollection.cpp:36
- [cpp] Function - showModal | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLDialogElement.cpp:68
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name, Optional<String*> old,
                                      String* value, bool attributeCreated,
                                      bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.cpp:102
- [cpp] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.cpp:241
- [c] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.h:55
- [cpp] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/HTMLFormElement.cpp:970
- [cpp] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/HTMLIFrameElement.cpp:247
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name,
                                           Optional<String*> old, String* value,
                                           bool attributeCreated,
                                           bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLMediaElement.cpp:160
- [cpp] Function - hasEventListenerInDispatchPath | sig: (EventTarget* origin,
                                           String* eventType) → bool | /home/hwang/work/D/starfish_/src/core/dom/HTMLMediaElement.cpp:1264
- [cpp] Function - MediaOperationQueueDataRequestPlay | sig: (
    HTMLMediaElement* p, Promise* pm) | /home/hwang/work/D/starfish_/src/core/dom/HTMLMediaElement.cpp:1799
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/HTMLOptionsCollection.cpp:40
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/HTMLOptionsCollection.h:44
- [cpp] Function - processImportMap | sig: (Document* document, String* txt) → bool | /home/hwang/work/D/starfish_/src/core/dom/HTMLScriptElement.cpp:599
- [cpp] Function - executeScriptImpl | sig: (bool forceSync, bool inParser) → bool | /home/hwang/work/D/starfish_/src/core/dom/HTMLScriptElement.cpp:659
- [cpp] Function - showDropdownMenu | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLSelectElement.cpp:478
- [cpp] Function - signalSlotChangeForFallbackMutation | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLSlotElement.cpp:79
- [cpp] Function - didNodeInserted | sig: (Node* parent, Node* newChild) → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLSlotElement.cpp:92
- [cpp] Function - didNodeRemoved | sig: (Node* parent, Node* oldChild) → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLSlotElement.cpp:102
- [c] Function - signalSlotChangeForFallbackMutation | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLSlotElement.h:85
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name,
                                           Optional<String*> old, String* value,
                                           bool attributeCreated,
                                           bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/HTMLTrackElement.cpp:147
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/ImageBitmap.cpp:36
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserver.cpp:120
- [cpp] Function - disconnect | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserver.cpp:187
- [cpp] Function - notify | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserver.cpp:204
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserver.h:67
- [c] Function - disconnect | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserver.h:83
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserverEntry.cpp:33
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/IntersectionObserverEntry.h:72
- [cpp] Function - MediaError | sig: (ExecutionContext* executionContext, int32_t code,
                       String* message) | /home/hwang/work/D/starfish_/src/core/dom/MediaError.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MediaError.cpp:45
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MediaError.h:33
- [cpp] File - /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.cpp | /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.cpp:1
- [cpp] Function - MessageChannel | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.cpp:27
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.cpp:46
- [c] File - /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.h | /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.h:1
- [c] Constant - __StarfishMessageChannel__ | /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.h:21
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MessageChannel.h:34
- [c] Class - WindowOrMessagePortOrServiceWorker | /home/hwang/work/D/starfish_/src/core/dom/MessageEvent.h:28
- [cpp] File - /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp:1
- [cpp] Function - MessagePort | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp:33
- [cpp] Function - onmessage | sig: () → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp:172
- [cpp] Function - setOnmessage | sig: (EventListener* listener) → void | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp:178
- [cpp] Function - onmessageerror | sig: () → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp:192
- [cpp] Function - setOnmessageerror | sig: (EventListener* listener) → void | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.cpp:198
- [c] File - /home/hwang/work/D/starfish_/src/core/dom/MessagePort.h | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.h:1
- [c] Constant - __StarfishMessagePort__ | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.h:21
- [c] Function - isMessagePort | sig: () → virtual bool | /home/hwang/work/D/starfish_/src/core/dom/MessagePort.h:68
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MutationObserver.cpp:108
- [cpp] Function - disconnect | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/MutationObserver.cpp:204
- [cpp] Function - notify | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/MutationObserver.cpp:227
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MutationObserver.h:198
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MutationRecord.cpp:64
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/MutationRecord.h:41
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/NamedNodeMap.cpp:38
- [cpp] Function - compareDocumentPosition | sig: (Node* other) → unsigned short | /home/hwang/work/D/starfish_/src/core/dom/Node.cpp:1064
- [cpp] Function - notifyNodeInsertedToDocumentTree | sig: (Node* head, Node* node) → void | /home/hwang/work/D/starfish_/src/core/dom/Node.cpp:1545
- [cpp] Function - notifyNodeRemoveFromDocumentTree | sig: (Node* node) → void | /home/hwang/work/D/starfish_/src/core/dom/Node.cpp:1875
- [c] Function - setConnected | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Node.h:228
- [c] Function - clearConnected | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Node.h:233
- [cpp] Function - NodeIterator | sig: (Document* document, Node* root, unsigned whatToShow,
                           ScriptValue filter) | /home/hwang/work/D/starfish_/src/core/dom/NodeIterator.cpp:87
- [cpp] Function - nextNode | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/NodeIterator.cpp:189
- [cpp] Function - previousNode | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/NodeIterator.cpp:216
- [cpp] Function - acceptNode | sig: (Node* node, bool& error) → unsigned | /home/hwang/work/D/starfish_/src/core/dom/NodeIterator.cpp:251
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/NodeIterator.h:70
- [c] Function - acceptNode | sig: (Node*, bool&) → unsigned | /home/hwang/work/D/starfish_/src/core/dom/NodeIterator.h:93
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/NodeList.cpp:48
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Range.cpp:74
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Range.h:82
- [cpp] Function - handleDefaultEvent | sig: (Event* event, Window* window,
                                   FrameBlockBox* frame, OverflowValue ox,
                                   OverflowValue oy) → bool | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:65
- [cpp] Function - stopScrolling | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:399
- [cpp] Function - updateSlotElements | sig: (bool shouldConnectSlotWithSlottables) → void | /home/hwang/work/D/starfish_/src/core/dom/ShadowRoot.cpp:108
- [cpp] Function - assignSlot | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/ShadowRoot.cpp:135
- [cpp] Function - connectSlotWithSlottables | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/ShadowRoot.cpp:141
- [c] Function - connectSlotWithSlottables | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/ShadowRoot.h:174
- [cpp] Function - TextTrackCueList | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/dom/TextTrackCueList.cpp:27
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/TextTrackCueList.cpp:34
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Touch.cpp:47
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/Touch.h:190
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/TouchList.cpp:32
- [cpp] Function - TreeWalker | sig: (Document* document, Node* root, unsigned whatToShow,
                       ScriptValue filter) | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:30
- [cpp] Function - parentNode | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:51
- [cpp] Function - firstChild | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:76
- [cpp] Function - lastChild | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:115
- [cpp] Function - previousNode | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:156
- [cpp] Function - nextNode | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:216
- [cpp] Function - TraverseSiblings | sig: () → Node * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:257
- [cpp] Function - acceptNode | sig: (Node* node, bool& error) → unsigned | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.cpp:331
- [c] Function - acceptNode | sig: (Node*, bool&) → unsigned | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.h:71
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/TreeWalker.h:75
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/CanvasGradient.cpp:76
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/CanvasPattern.cpp:54
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/CanvasRenderingContext.cpp:30
- [cpp] Function - getImageData | sig: (int32_t sx, int32_t sy,
                                                       int32_t sw, int32_t sh) → ImageData * | /home/hwang/work/D/starfish_/src/core/dom/canvas/CanvasRenderingContext2DMixIn.cpp:1554
- [cpp] Function - initialize | sig: (int32_t rows, int32_t pixelsPerRow,
                           ScriptUint8ClampedArray source) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/ImageData.cpp:89
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/ImageData.cpp:129
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/Path2D.cpp:55
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/TextMetrics.cpp:57
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:93
- [cpp] Function - bindBuffer | sig: (GLenum target,
                                        Optional<WebGLBuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:126
- [cpp] Function - bindFramebuffer | sig: (
    GLenum target, Optional<WebGLFramebuffer*> maybeFramebuffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:179
- [cpp] Function - bindTexture | sig: (GLenum target,
                                         Optional<WebGLTexture*> maybeTexture) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:211
- [cpp] Function - getUniformImpl | sig: (
    WebGLProgram* program, WebGLUniformLocation* location, GLenum type) → Optional<ScriptValue> | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:407
- [cpp] Function - getVertexAttrib | sig: (GLuint index, GLenum pname) → ScriptValue | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:535
- [cpp] Function - fenceSync | sig: (GLenum condition,
                                                       GLbitfield flags) → Optional<WebGLSync*> | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:1120
- [cpp] Function - bindBufferBase | sig: (GLenum target, GLuint index,
                                            Optional<WebGLBuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:1221
- [cpp] Function - bindBufferRange | sig: (GLenum target, GLuint index,
                                             Optional<WebGLBuffer*> buffer,
                                             GLintptr offset, GLsizeiptr size) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:1271
- [cpp] Function - getActiveUniforms | sig: (
    WebGLProgram* program, GCAtomicVector<GLuint> uniformIndices, GLenum pname) → ScriptValue | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:1322
- [cpp] Function - createVertexArray | sig: () → WebGLVertexArrayObject * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:1382
- [cpp] Function - bindVertexArray | sig: (
    Optional<WebGLVertexArrayObject*> array) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp:1440
- [c] Function - bindBuffer | sig: (GLenum target, Optional<WebGLBuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.h:104
- [c] Function - bindFramebuffer | sig: (GLenum target, Optional<WebGLFramebuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.h:105
- [c] Function - bindTexture | sig: (GLenum target, Optional<WebGLTexture*> texture) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.h:106
- [c] Function - bindBufferBase | sig: (GLenum target, GLuint index,
                        Optional<WebGLBuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.h:204
- [c] Function - bindBufferRange | sig: (GLenum target, GLuint index,
                         Optional<WebGLBuffer*> buffer, GLintptr offset,
                         GLsizeiptr size) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.h:206
- [c] Function - bindVertexArray | sig: (Optional<WebGLVertexArrayObject*> array) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGL2RenderingContext.h:217
- [cpp] Function - createVertexArrayOES | sig: () → WebGLVertexArrayObjectOES * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLOES_VertexArrayObject.cpp:41
- [cpp] Function - bindVertexArrayOES | sig: (
    Optional<WebGLVertexArrayObjectOES*> arrayObject) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLOES_VertexArrayObject.cpp:105
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:116
- [cpp] Function - preInitialize | sig: (ScriptValue contextAttributes) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:121
- [cpp] Function - initialize | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:182
- [cpp] Function - flushDrawingCommands | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:201
- [cpp] Function - flushForReadback | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:210
- [cpp] Function - onResize | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:298
- [cpp] Function - getExtension | sig: (
    String* requestedName) → Optional<ScriptObject> | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:411
- [cpp] Function - bindAttribLocation | sig: (WebGLProgram* program,
                                               GLuint index, String* name) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:462
- [cpp] Function - bindBuffer | sig: (GLenum target,
                                       Optional<WebGLBuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:479
- [cpp] Function - bindFramebuffer | sig: (
    GLenum target, Optional<WebGLFramebuffer*> maybeFramebuffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:509
- [cpp] Function - bindRenderbuffer | sig: (
    GLenum target, Optional<WebGLRenderbuffer*> maybeRenderbuffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:540
- [cpp] Function - bindTexture | sig: (GLenum target,
                                        Optional<WebGLTexture*> maybeTexture) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:569
- [cpp] Function - createBuffer | sig: () → WebGLBuffer * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:746
- [cpp] Function - createFramebuffer | sig: () → WebGLFramebuffer * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:755
- [cpp] Function - createProgram | sig: () → WebGLProgram * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:764
- [cpp] Function - createRenderbuffer | sig: () → WebGLRenderbuffer * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:771
- [cpp] Function - createShader | sig: (unsigned long type) → WebGLShader * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:780
- [cpp] Function - createTexture | sig: () → WebGLTexture * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:792
- [cpp] Function - getParameter | sig: (GLenum pname) → ScriptValue | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1189
- [cpp] Function - getActiveAttrib | sig: (WebGLProgram* program,
                                                        GLuint index) → WebGLActiveInfo * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1369
- [cpp] Function - getActiveUniform | sig: (WebGLProgram* program,
                                                         GLuint index) → WebGLActiveInfo * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1407
- [cpp] Function - getShaderPrecisionFormat | sig: (
    GLenum shadertype, GLenum precisiontype) → WebGLShaderPrecisionFormat * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1683
- [cpp] Function - getUniformImpl | sig: (
    WebGLProgram* program, WebGLUniformLocation* location, GLenum type) → Optional<ScriptValue> | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1816
- [cpp] Function - getUniformLocation | sig: (
    WebGLProgram* program, String* name) → WebGLUniformLocation * | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1954
- [cpp] Function - getVertexAttrib | sig: (GLuint index, GLenum pname) → ScriptValue | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.cpp:1990
- [c] Function - bindAttribLocation | sig: (WebGLProgram* program, GLuint index, String* name) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:96
- [c] Function - bindBuffer | sig: (GLenum target, Optional<WebGLBuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:97
- [c] Function - bindFramebuffer | sig: (GLenum target, Optional<WebGLFramebuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:98
- [c] Function - bindRenderbuffer | sig: (GLenum target, Optional<WebGLRenderbuffer*> buffer) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:99
- [c] Function - bindTexture | sig: (GLenum target, Optional<WebGLTexture*> texture) → void | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:100
- [cpp] Function - createFrameBufferObject | sig: (GL* gl, const unsigned width,
                                    const unsigned height, GLuint& outFbo,
                                    GLuint& outTextureId, GLuint& outRboDepth,
                                    GLuint& outRboOrTextureIdForDepthStencil,
                                    const bool needAlphaBuffer,
                                    const bool needDepthBuffer,
                                    const bool needStencilBuffer) → bool | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/gl/FramebufferTexture.cpp:32
- [cpp] Function - destroy | sig: () → bool | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/gl/FramebufferTexture.cpp:152
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAngle.cpp:45
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAngle.h:45
- [cpp] Function - beginElementAt | sig: (float offset) → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimateMotionElement.cpp:69
- [cpp] Function - SVGAnimatedAngle | sig: (Document* document, SVGAngle* baseVal,
                                   SVGAngle* animVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedAngle.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedAngle.cpp:35
- [cpp] Function - SVGAnimatedBoolean | sig: (Document* document, bool baseVal,
                                       bool animVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedBoolean.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedBoolean.cpp:35
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedEnumeration.cpp:50
- [cpp] Function - SVGAnimatedInteger | sig: (SVGElement* targetElement,
                                       const QualifiedName& targetAttribute,
                                       long baseVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedInteger.cpp:27
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedInteger.cpp:43
- [cpp] Function - SVGAnimatedLength | sig: (Document* document, SVGLength* baseVal,
                                     SVGLength* animVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedLength.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedLength.cpp:35
- [cpp] Function - SVGAnimatedLengthList | sig: (Document* document,
                                             SVGLengthList* baseVal,
                                             SVGLengthList* animVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedLengthList.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedLengthList.cpp:36
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedNumber.cpp:52
- [cpp] Function - SVGAnimatedNumberList | sig: (Document* document,
                                             SVGNumberList* baseVal,
                                             SVGNumberList* animVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedNumberList.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedNumberList.cpp:36
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedString.cpp:45
- [cpp] Function - SVGAnimatedTransformList | sig: (Document* document,
                                                   SVGTransformList* baseVal,
                                                   SVGTransformList* animVal) | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedTransformList.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimatedTransformList.cpp:36
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name,
                                              Optional<String*> old,
                                              String* value,
                                              bool attributeCreated,
                                              bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:114
- [cpp] Function - onbegin | sig: () → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:713
- [cpp] Function - setOnbegin | sig: (EventListener* onbegin) → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:719
- [cpp] Function - onend | sig: () → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:729
- [cpp] Function - setOnend | sig: (EventListener* onend) → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:735
- [cpp] Function - onrepeat | sig: () → EventListener * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:745
- [cpp] Function - setOnrepeat | sig: (EventListener* onrepeat) → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGAnimationElement.cpp:751
- [cpp] Function - didAttributeChanged | sig: (QualifiedName name, Optional<String*> old,
                                     String* value, bool attributeCreated,
                                     bool attributeRemoved) → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGElement.cpp:197
- [cpp] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGElement.cpp:510
- [c] Function - tabIndex | sig: () → int | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGElement.h:206
- [cpp] Function - xChannelSelector | sig: () → SVGAnimatedEnumeration * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGFEDisplacementMapElement.cpp:182
- [cpp] Function - yChannelSelector | sig: () → SVGAnimatedEnumeration * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGFEDisplacementMapElement.cpp:193
- [c] Function - xChannelSelector | sig: () → SVGAnimatedEnumeration * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGFEDisplacementMapElement.h:61
- [c] Function - yChannelSelector | sig: () → SVGAnimatedEnumeration * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGFEDisplacementMapElement.h:62
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGLength.cpp:79
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGLength.h:54
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGLengthList.cpp:44
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGNumber.cpp:48
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGNumber.h:41
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGNumberList.cpp:45
- [cpp] Function - connectUseElements | sig: () → void | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGSVGElement.cpp:192
- [cpp] Function - executeScriptImpl | sig: (bool forceSync, bool inParser) → bool | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGScriptElement.cpp:247
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGTransform.cpp:46
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGTransform.h:55
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGTransformList.cpp:48
- [cpp] Function - setListener | sig: (ScriptValue listener) → void | /home/hwang/work/D/starfish_/src/core/extra/Avplay.cpp:381
- [cpp] Function - callJSCallback | sig: (AVPLAY_CALLBACK_TYPE type) → void | /home/hwang/work/D/starfish_/src/core/extra/Avplay.cpp:407
- [c] Function - setListener | sig: (ScriptValue listener) → void | /home/hwang/work/D/starfish_/src/core/extra/Avplay.h:86
- [cpp] Function - toJSON | sig: () → ScriptObject | /home/hwang/work/D/starfish_/src/core/extra/Performance.cpp:194
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/extra/PerformanceEntry.cpp:47
- [cpp] Function - toJSON | sig: () → ScriptObject | /home/hwang/work/D/starfish_/src/core/extra/PerformanceEntry.cpp:52
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/extra/PerformanceEntry.h:38
- [cpp] Function - PerformanceResourceTiming | sig: (
    ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/extra/PerformanceResourceTiming.cpp:26
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/extra/PerformanceResourceTiming.cpp:40
- [cpp] Function - TimeRanges | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/extra/TimeRanges.cpp:28
- [cpp] Function - TimeRanges | sig: (ExecutionContext* executionContext,
                       const GCAtomicVector<TimeRange>& other) | /home/hwang/work/D/starfish_/src/core/extra/TimeRanges.cpp:34
- [cpp] Function - TimeRanges | sig: (ExecutionContext* executionContext,
                       GCAtomicVector<TimeRange>&& other) | /home/hwang/work/D/starfish_/src/core/extra/TimeRanges.cpp:42
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/extra/TimeRanges.cpp:50
- [cpp] Function - Body | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/fetch/Body.cpp:81
- [cpp] Function - Body | sig: (ExecutionContext* executionContext, Optional<BodyInit>& body) | /home/hwang/work/D/starfish_/src/core/fetch/Body.cpp:91
- [cpp] Function - arrayBuffer | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Body.cpp:119
- [cpp] Function - blob | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Body.cpp:167
- [cpp] Function - json | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Body.cpp:206
- [cpp] Function - text | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Body.cpp:256
- [cpp] Function - fail | sig: () → void | /home/hwang/work/D/starfish_/src/core/fetch/Fetch.cpp:115
- [cpp] Function - fetch | sig: (ExecutionContext* executionContext, RequestInfo& info) → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Fetch.cpp:122
- [cpp] Function - fetch | sig: (ExecutionContext* executionContext, RequestInfo& info,
                      RequestInit& init) → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Fetch.cpp:133
- [c] Function - fetch | sig: (ExecutionContext* executionContext,
                          RequestInfo& input) → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Fetch.h:44
- [c] Function - fetch | sig: (ExecutionContext* executionContext,
                          RequestInfo& input, RequestInit& init) → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/Fetch.h:46
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fetch/Headers.cpp:93
- [cpp] Function - initHeadersFromArrayObject | sig: (ScriptObject object) → void | /home/hwang/work/D/starfish_/src/core/fetch/Headers.cpp:124
- [cpp] Function - initHeadersFromObject | sig: (ScriptObject object) → void | /home/hwang/work/D/starfish_/src/core/fetch/Headers.cpp:165
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fetch/Request.cpp:279
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fetch/Response.cpp:119
- [cpp] Function - ReadableStream | sig: (ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStream.cpp:33
- [cpp] Function - ReadableStream | sig: (ExecutionContext* executionContext,
                               ScriptObject underlyingSource) | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStream.cpp:43
- [cpp] Function - ReadableStream | sig: (ExecutionContext* executionContext,
                               ScriptObject underlyingSource,
                               ScriptValue options) | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStream.cpp:72
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStream.cpp:94
- [cpp] Function - resolveWithType | sig: (Promise* promise,
                                           ExecutionContext* executionContext,
                                           BodyType type) → void | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamBuffer.cpp:83
- [cpp] Function - ReadableStreamDefaultController | sig: (
    ExecutionContext* executionContext) | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultController.cpp:33
- [cpp] Function - ReadableStreamDefaultController | sig: (
    ExecutionContext* executionContext, ReadableStream* stream) | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultController.cpp:45
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultController.cpp:54
- [cpp] Function - pull | sig: (DefaultReadRequest* request) → void | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultController.cpp:84
- [cpp] Function - ReadableStreamDefaultReader | sig: (
    ExecutionContext* executionContext, ReadableStream* stream) | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:71
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:82
- [cpp] Function - read | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:87
- [cpp] Function - readDefaultReadRequest | sig: (
    DefaultReadRequest* request) → void | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:106
- [cpp] Function - fulfillReadRequest | sig: (ScriptValue chunk,
                                                     bool done) → void | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:134
- [cpp] Function - cancel | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:152
- [cpp] Function - runCloseStepsReadRequests | sig: () → void | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamDefaultReader.cpp:177
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fileapi/Blob.cpp:145
- [cpp] Function - text | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fileapi/Blob.cpp:208
- [cpp] Function - arrayBuffer | sig: () → Promise * | /home/hwang/work/D/starfish_/src/core/fileapi/Blob.cpp:216
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fileapi/File.cpp:43
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/fileapi/FileReader.cpp:55
- [cpp] Function - readArrayBuffer | sig: (Blob* blob) → void | /home/hwang/work/D/starfish_/src/core/fileapi/FileReader.cpp:179
- [cpp] Function - sendInfoMessage | sig: (String* m) → void | /home/hwang/work/D/starfish_/src/core/inspector/Inspector.cpp:58
- [cpp] Function - sendErrorMessage | sig: (String* m) → void | /home/hwang/work/D/starfish_/src/core/inspector/Inspector.cpp:89
- [cpp] Function - sendWarnMessage | sig: (String* m) → void | /home/hwang/work/D/starfish_/src/core/inspector/Inspector.cpp:120
- [cpp] Function - sendDebugMessage | sig: (String* m) → void | /home/hwang/work/D/starfish_/src/core/inspector/Inspector.cpp:151
- [cpp] Function - worker | sig: (void* data) → void * | /home/hwang/work/D/starfish_/src/core/inspector/Inspector.cpp:197
- [cpp] Function - doRun | sig: () → bool | /home/hwang/work/D/starfish_/src/core/modules/cast/DIALRunnable.cpp:43
- [cpp] Function - preRun | sig: () → bool | /home/hwang/work/D/starfish_/src/core/modules/cast/SSDPRunnable.cpp:42
- [cpp] Function - initSocket | sig: () → bool | /home/hwang/work/D/starfish_/src/core/modules/cast/SSDPRunnable.cpp:118
- [c] Function - initSocket | sig: () → bool | /home/hwang/work/D/starfish_/src/core/modules/cast/SSDPRunnable.h:37
- [c] Function - isCrypto | sig: () → virtual bool | /home/hwang/work/D/starfish_/src/core/modules/crypto/Crypto.h:32
- [cpp] File - /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.cpp | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.cpp:1
- [cpp] Function - IDBConnectionData | sig: () | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.cpp:33
- [cpp] Function - openDatabase | sig: (IDBConnectionData* connectionData,
                                 OpenDBRequestData* data) → void | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.cpp:50
- [cpp] Function - IDBConnection | sig: (const std::string& dbName,
                             IDBDatabaseIdentifier identifier) | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.cpp:98
- [c] File - /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.h | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.h:1
- [c] Constant - __StarfishIDBConnection__ | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConnection.h:23
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBCursor.cpp:34
- [cpp] Function - transaction | sig: (
    DOMStringOrSequenceOfDOMString storeNames, String* mode,
    const IDBTransactionOptions& options) → IDBTransaction * | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBDatabase.cpp:58
- [cpp] Function - createObjectStore | sig: (String* name) → IDBObjectStore * | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBDatabase.cpp:75
- [cpp] Function - createObjectStore | sig: (String* name,
                                               IDBObjectStoreParameters options) → IDBObjectStore * | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBDatabase.cpp:80

<!-- Truncated: showing 597 of 2470 relevant nodes -->
