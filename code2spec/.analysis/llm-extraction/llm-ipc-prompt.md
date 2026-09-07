
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
# Languages: c (118), cpp (150), java (11), javascript (8), python (43)

## IPC Patterns
- [javascript] Function - runWithMDNData | sig: (starfish_data) | /home/hwang/work/E/starfish_/docs/webpages/webapi/webapi_main.js:163
- [cpp] Function - eventtargetConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                                 size_t argc, ValueRef** argv,
                                 OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/EventTargetCustomBinding.cpp:30
- [cpp] Function - geopositionCallbackFunction | sig: (Document* document, Geoposition* pos,
                                        void* data) → void | /home/hwang/work/E/starfish_/src/binding/GeolocationCustomBinding.cpp:32
- [cpp] Function - geopositionErrorCallbackFunction | sig: (Document* document,
                                             PositionError* error, void* data) → void | /home/hwang/work/E/starfish_/src/binding/GeolocationCustomBinding.cpp:44
- [cpp] Function - htmlelementConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                                 size_t argc, ValueRef** argv,
                                 OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/HTMLElementCustomBinding.cpp:32
- [cpp] Function - imagedataConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                               size_t argc, ValueRef** argv,
                               OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/ImageDataCustomBinding.cpp:29
- [cpp] Function - mediastreamConstructor | sig: (ExecutionStateRef* state, ValueRef* thisValue,
                                 size_t argc, ValueRef** argv,
                                 OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/MediaStreamCustomBinding.cpp:30
- [cpp] Function - initBinding | sig: () → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingInstance.cpp:288
- [cpp] Function - initJavaScriptBinding | sig: (ContextRef* context,
                                                  ExecutionStateRef* state) → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingInstance.cpp:525
- [c] Function - initJavaScriptBinding | sig: (Escargot::ContextRef* context,
                                       Escargot::ExecutionStateRef* state) → virtual void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingInstance.h:205
- [cpp] Function - _setListenerAvplayFunction | sig: (ExecutionStateRef* state,
                                            ValueRef* thisValue, size_t argc,
                                            ValueRef** argv,
                                            bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/ScriptBindingWindowInstance.cpp:219
- [cpp] Function - initJavaScriptBinding | sig: (
    ContextRef* context, ExecutionStateRef* state) → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingWindowInstance.cpp:245
- [cpp] Function - initJavaScriptGlobalBinding | sig: (
    ScriptExecutionState state, ScriptBindingInstance* scriptBindingInstance) → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:98
- [cpp] Function - initJavaScriptGlobalBinding | sig: (
    ScriptExecutionState state, ScriptBindingInstance* scriptBindingInstance) → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:110
- [cpp] Function - initJavaScriptGlobalBinding | sig: (
    ScriptExecutionState state, ScriptBindingInstance* scriptBindingInstance) → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:121
- [cpp] Function - initJavaScriptBinding | sig: (
    Escargot::ContextRef* context, Escargot::ExecutionStateRef* state) → void | /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp:144
- [cpp] Function - fetchScriptBindingInstance | sig: (ContextRef* ctx) → ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp:548
- [cpp] Function - generateScriptObject | sig: () → ScriptObject | /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp:744
- [cpp] Function - createAttributeStringEventFunction | sig: (EventTarget* target,
                                               String* functionBody,
                                               bool& result) → ScriptValue | /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp:977
- [cpp] Function - initDebuggerIfNeeds | sig: (ScriptBindingInstance* instance) → void | /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp:1431
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.h:526
- [cpp] Function - urlsearchparamsConstructor | sig: (ExecutionStateRef* state,
                                     ValueRef* thisValue, size_t argc,
                                     ValueRef** argv,
                                     OptionalRef<ObjectRef> newTarget) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/URLSearchParamsCustomBinding.cpp:28
- [cpp] Function - timeoutHandler | sig: (void* data) → void | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:100
- [cpp] Function - setTimeoutWindowFunction | sig: (ExecutionStateRef* state,
                                   ValueRef* thisValue, size_t argc,
                                   ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:111
- [cpp] Function - setIntervalWindowFunction | sig: (ExecutionStateRef* state,
                                    ValueRef* thisValue, size_t argc,
                                    ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:159
- [cpp] Function - requestAnimationFrameHandler | sig: (void* data) → void | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:208
- [cpp] Function - requestAnimationFrameWindowFunction | sig: (ExecutionStateRef* state,
                                              ValueRef* thisValue, size_t argc,
                                              ValueRef** argv,
                                              bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:294
- [cpp] Function - screenShotTimeoutHandler | sig: (void* data) → void | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:431
- [cpp] Function - testAssertFunction | sig: (ExecutionStateRef* state,
                                    ValueRef* thisValue, size_t argc,
                                    ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:723
- [cpp] Function - wptTestEndFunction | sig: (ExecutionStateRef* state,
                                    ValueRef* thisValue, size_t argc,
                                    ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:772
- [cpp] Function - testImgDiffFunction | sig: (ExecutionStateRef* state,
                                     ValueRef* thisValue, size_t argc,
                                     ValueRef** argv, bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp:795
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/binding/WindowHoldable.cpp:38
- [c] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/binding/WindowHoldable.h:43
- [cpp] File - /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp | /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp:1
- [cpp] Function - WindowProxy | sig: (Window* window) | /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp:37
- [cpp] Function - updateSource | sig: (Window* window) → void | /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp:43
- [cpp] Function - scriptBindingInstance | sig: () → ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp:129
- [c] File - /home/hwang/work/E/starfish_/src/binding/WindowProxy.h | /home/hwang/work/E/starfish_/src/binding/WindowProxy.h:1
- [c] Constant - __StarfishWindowProxy__ | /home/hwang/work/E/starfish_/src/binding/WindowProxy.h:21
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/binding/WindowProxy.h:35
- [cpp] Function - timeoutHandler | sig: (void* data) → void | /home/hwang/work/E/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp:45
- [cpp] Function - setTimeoutWorkerGlobalScopeFunction | sig: (ExecutionStateRef* state,
                                              ValueRef* thisValue, size_t argc,
                                              NULLABLE ValueRef** argv,
                                              bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp:62
- [cpp] Function - setIntervalWorkerGlobalScopeFunction | sig: (ExecutionStateRef* state,
                                               ValueRef* thisValue, size_t argc,
                                               NULLABLE ValueRef** argv,
                                               bool isNewExpression) → ValueRef * | /home/hwang/work/E/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp:113
- [cpp] Function - main | sig: (int argc, char* argv[]) → int | /home/hwang/work/E/starfish_/src/launcher/ServiceWorkerEntry.cpp:55
- [cpp] Class - sigaction | /home/hwang/work/E/starfish_/src/launcher/ServiceWorkerEntry.cpp:86
- [cpp] Function - main | sig: (int argc, char* argv[]) → int | /home/hwang/work/E/starfish_/src/launcher/SharedWorkerEntry.cpp:55
- [cpp] Class - sigaction | /home/hwang/work/E/starfish_/src/launcher/SharedWorkerEntry.cpp:81
- [cpp] Function - dumpTextureToPNG | sig: (GL* gl, GLuint textureId, int width, int height,
                      const char* path, GLenum textureTarget = GL_TEXTURE_2D) → void | /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp:100
- [cpp] Function - bindTexIdx | sig: (GLint texIdx, bool attach) → void | /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp:1521
- [cpp] Function - bindTexPos | sig: (GLint texPos, bool flipY = false) → void | /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp:1533
- [cpp] Function - dumpTextureToPNG | sig: (GL* gl, GLuint textureId, int width, int height,
                      const char* path, GLenum textureTarget) → void | /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp:5902
- [cpp] Function - bindBuffer | sig: (GLenum target, GLuint buffer) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp:56
- [cpp] Function - bindFramebuffer | sig: (GLenum target, GLuint framebuffer) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp:61
- [cpp] Function - bindRenderbuffer | sig: (GLenum target, GLuint renderbuffer) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp:66
- [cpp] Function - bindTexture | sig: (GLenum target, GLuint texture) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp:71
- [cpp] Function - bindBuffer | sig: (GLenum target, GLuint buffer) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp:73
- [cpp] Function - bindFramebuffer | sig: (GLenum target, GLuint framebuffer) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp:78
- [cpp] Function - bindRenderbuffer | sig: (GLenum target, GLuint renderbuffer) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp:83
- [cpp] Function - bindTexture | sig: (GLenum target, GLuint texture) → virtual void | /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp:88
- [cpp] Class - pa_channel_map | /home/hwang/work/E/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:68
- [c] Function - audioChannels | sig: () → uint16_t | /home/hwang/work/E/starfish_/src/platform/multimedia/StreamInfo.h:182
- [c] Function - setAudioChannels | sig: (uint16_t channels) → void | /home/hwang/work/E/starfish_/src/platform/multimedia/StreamInfo.h:187
- [cpp] Function - transformetoNetscapeCookieFormat | sig: (
    ExecutionContext* executionContext, ResourceURL* url, String* value) → String * | /home/hwang/work/E/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp:208
- [cpp] Constant - CURLPIPE_MULTIPLEX | /home/hwang/work/E/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp:795
- [cpp] Function - extractHTTPCacheEntryProperty | sig: (NetworkURLWorkerData* nwd,
                                              CacheControl& cc,
                                              HTTPContentInfo& cinfo,
                                              HTTPFreshnessInfo& finfo) → void | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPCache.cpp:441
- [cpp] File - /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.cpp | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.cpp:1
- [cpp] Function - HTTPTransaction | sig: (CurlMultiRequestData* curlMultiRequestData) | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.cpp:49
- [cpp] Function - ~HTTPTransaction | sig: () | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.cpp:84
- [cpp] Constant - CURLPIPE_MULTIPLEX | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.cpp:161
- [cpp] Function - updateTransactionStatus | sig: () → void | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.cpp:346
- [c] File - /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.h | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.h:1
- [c] Constant - __StarfishHTTPTransaction__ | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.h:21
- [c] Function - updateTransactionStatus | sig: () → void | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.h:80
- [c] Function - setProxyURL | sig: (const std::string& url) → void | /home/hwang/work/E/starfish_/src/platform/network/http/HTTPTransaction.h:90
- [cpp] Function - launchProcess | sig: (const std::vector<std::string>& argv,
                                PID* processID) → bool | /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp:43
- [cpp] Class - sigaction | /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp:60
- [cpp] Function - killProcess | sig: (PID pid, bool isWait) → bool | /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp:156
- [cpp] Function - getLocalIPAddress | sig: (std::string queriedInfName,
                                   std::string& ipAddressQueried) → bool | /home/hwang/work/E/starfish_/src/platform/public/DeviceInfo.cpp:31
- [cpp] Function - GetProxyURL | sig: () → std::string | /home/hwang/work/E/starfish_/src/public/LWEWebView.cpp:275
- [cpp] Function - SetProxyURL | sig: (const std::string& proxyURL) → void | /home/hwang/work/E/starfish_/src/public/LWEWebView.cpp:369
- [cpp] Function - Java_com_samsung_android_lightweightwebengine_internal_LweWebViewImpl_init | sig: (
    JNIEnv* env, jobject thiz) → JNIEXPORT void JNICALL | /home/hwang/work/E/starfish_/src/public/bridge/android/AndroidBridge.cpp:122
- [java] Function - InputConnection | sig: (EditorInfo outAttrs) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/WebView.java:64
- [java] Function - InputConnection | sig: (View view) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebView.java:41
- [java] Function - InputConnection | sig: (View view) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:288
- [java] Function - InputConnection | sig: (View view) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:292
- [java] Class - ImeInputConnection | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:307
- [java] Function - ImeInputConnection | sig: (View view) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:308
- [java] Function - commitText | sig: (CharSequence text, int newCursorPosition) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:313
- [java] Function - setComposingText | sig: (CharSequence text, int newCursorPosition) | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:327
- [java] Function - finishComposingText | sig: () | /home/hwang/work/E/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:343
- [cpp] Function - initEGLDisplay | sig: (EGLDisplay eglDisplay, EGLConfig& config) → bool | /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp:49
- [cpp] Function - createEGLDisplay | sig: (EGLDisplay& display, EGLConfig& config) → bool | /home/hwang/work/E/starfish_/src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp:47
- [cpp] Function - flushTreeEvents | sig: (gpointer) → gboolean | /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:1056
- [cpp] Function - a11yDbusFilter | sig: (DBusConnection* connection,
                                        DBusMessage* message, void*) → DBusHandlerResult | /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:1309
- [cpp] Function - enableBridge | sig: () → void | /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:1363
- [cpp] Function - disableBridge | sig: () → void | /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:1491
- [cpp] Function - bindRenderFBO | sig: () → void | /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:431
- [cpp] Function - createEGLDisplay | sig: (EGLDisplay& display, EGLConfig& config,
                      struct wl_display* wlDisplay) → bool | /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp:48
- [cpp] Function - createEGLDisplay | sig: (EGLDisplay& display, EGLConfig& config) → bool | /home/hwang/work/E/starfish_/src/public/bridge/x11/LWEWebViewX11.cpp:67
- [c] Function - scriptBindingInstance | sig: () → virtual ScriptBindingInstance * | /home/hwang/work/E/starfish_/src/public/delegate/JavaScriptNativeHandler.h:39
- [cpp] Function - AddJavaScriptInterface | sig: (
    const std::string& exposedObjectName, const std::string& jsFunctionName,
    std::function<std::string(const std::string&)> cb) → void | /home/hwang/work/E/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp:969
- [cpp] Function - RemoveJavascriptInterface | sig: (
    const std::string& exposedObjectName, const std::string& jsFunctionName) → void | /home/hwang/work/E/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp:1216
- [cpp] Function - GetProxyURL | sig: () → std::string | /home/hwang/work/E/starfish_/src/public/delegate/SettingsDelegate.cpp:163
- [cpp] Function - SetProxyURL | sig: (const std::string& proxyURL) → void | /home/hwang/work/E/starfish_/src/public/delegate/SettingsDelegate.cpp:336
- [cpp] Function - sigHandler | sig: (int sig, struct sigcontext ctx) → void | /home/hwang/work/E/starfish_/src/shell/Shell.cpp:216
- [cpp] Function - setBacktraceHandler | sig: () → void | /home/hwang/work/E/starfish_/src/shell/Shell.cpp:253
- [cpp] Class - sigaction | /home/hwang/work/E/starfish_/src/shell/Shell.cpp:262
- [cpp] Function - init | sig: () → void | /home/hwang/work/E/starfish_/src/shell/glib/AppLoopGlib.cpp:67
- [cpp] Function - start | sig: (double timeoutInSec) → int | /home/hwang/work/E/starfish_/src/shell/libuv/AppLoopLibuv.cpp:85
- [cpp] Class - sigaction | /home/hwang/work/E/starfish_/src/shell/libuv/AppLoopLibuv.cpp:96
- [cpp] Function - createEGLDisplay | sig: (EGLDisplay& display, EGLConfig& config) → bool | /home/hwang/work/E/starfish_/src/shell/x11_webcontainer/WindowX11Webcontainer.cpp:63
- [cpp] Function - registerX11Fd | sig: () → void | /home/hwang/work/E/starfish_/src/shell/x11_webcontainer/WindowX11Webcontainer.cpp:389
- [c] Function - gator_annotate_channel | sig: (int channel, const char *str) → void | /home/hwang/work/E/starfish_/src/streamline_annotate.h:89
- [c] Function - gator_annotate_channel_color | sig: (int channel, int color, const char *str) → void | /home/hwang/work/E/starfish_/src/streamline_annotate.h:91
- [c] Function - gator_annotate_channel_end | sig: (int channel) → void | /home/hwang/work/E/starfish_/src/streamline_annotate.h:93
- [c] Function - gator_annotate_name_channel | sig: (int channel, int group, const char *str) → void | /home/hwang/work/E/starfish_/src/streamline_annotate.h:94
- [python] Function - wpt_serve_testharness_websocket | sig: () | /home/hwang/work/E/starfish_/tool/runner/test_runner.py:365
- [python] Function - probe | sig: (url, timeout=10) | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_audit.py:72
- [python] Constant - RE_CONNECT_REFUSED | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_runner.py:205
- [python] Constant - CONNECT_REFUSED_RETRIES | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_runner.py:212
- [python] Function - _is_connect_refused_on_navigation | sig: (log, url) | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_runner.py:215
- [python] Function - run_one | sig: (url, timeout, storage_dir=None, _retries=CONNECT_REFUSED_RETRIES) | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_runner.py:227
- [python] Function - _port_open | sig: (port, host="127.0.0.1", timeout=0.5) | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_server.py:57
- [python] Function - _http_ok | sig: (path="/", timeout=2.0) | /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_server.py:63

### IPC Edges
- /home/hwang/work/E/starfish_/docs/webpages/webapi/webapi_main.js::runWithMDNData → addEventListener [broadcast_receiver]
- /home/hwang/work/E/starfish_/docs/webpages/webapi/webapi_main.js::runWithMDNData → addEventListener [broadcast_receiver]
- /home/hwang/work/E/starfish_/src/binding/EventTargetCustomBinding.cpp::eventtargetConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/GeolocationCustomBinding.cpp::geopositionCallbackFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/GeolocationCustomBinding.cpp::geopositionErrorCallbackFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/HTMLElementCustomBinding.cpp::htmlelementConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/HTMLElementCustomBinding.cpp::htmlelementConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ImageDataCustomBinding.cpp::imagedataConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ImageDataCustomBinding.cpp::imagedataConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/MediaStreamCustomBinding.cpp::mediastreamConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/MediaStreamCustomBinding.cpp::mediastreamConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/MediaStreamCustomBinding.cpp::mediastreamConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingInstance.cpp::initBinding → initJavaScriptBinding [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingInstance.cpp::initJavaScriptBinding → STARFISH_ENUM_BINDING_UNIMPL_NAMES [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingWindowInstance.cpp::_setListenerAvplayFunction → setListener [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingWindowInstance.cpp::initJavaScriptBinding → STARFISH_ENUM_GLOBAL_BINDING_WINDOW_NAMES [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp::initJavaScriptGlobalBinding → STARFISH_ENUM_GLOBAL_BINDING_DEDICATEDWORKER_NAMES [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp::initJavaScriptGlobalBinding → STARFISH_ENUM_GLOBAL_BINDING_SHAREDWORKER_NAMES [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp::initJavaScriptGlobalBinding → STARFISH_ENUM_GLOBAL_BINDING_SERVICEWORKER_NAMES [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptBindingWorkerInstance.cpp::initJavaScriptBinding → initJavaScriptGlobalBinding [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::EscargotStarfishPlatform.markJSJobEnqueued → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::EscargotStarfishPlatform.loadModule → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::EscargotStarfishPlatform.loadModule → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::EscargotStarfishPlatform.loadModule → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::EscargotStarfishPlatform.hostImportModuleDynamically → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::EscargotStarfishPlatform.hostImportModuleDynamically → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::fetchScriptBindingInstance → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::generateScriptObject → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::createAttributeStringEventFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::initDebuggerIfNeeds → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/ScriptWrappable.cpp::initDebuggerIfNeeds → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/URLSearchParamsCustomBinding.cpp::urlsearchparamsConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/URLSearchParamsCustomBinding.cpp::urlsearchparamsConstructor → fetchScriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::timeoutHandler → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::setTimeoutWindowFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::setIntervalWindowFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::requestAnimationFrameHandler → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::requestAnimationFrameWindowFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::screenShotTimeoutHandler → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::testAssertFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::wptTestEndFunction → closeConnection [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::testImgDiffFunction → popen [pipe]
- /home/hwang/work/E/starfish_/src/binding/WindowCustomBinding.cpp::testImgDiffFunction → popen [pipe]
- /home/hwang/work/E/starfish_/src/binding/WindowHoldable.cpp::scriptBindingInstance → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp::updateSource → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp::updateSource → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WindowProxy.cpp::scriptBindingInstance → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp::timeoutHandler → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp::setTimeoutWorkerGlobalScopeFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/binding/WorkerGlobalScopeCustomBinding.cpp::setIntervalWorkerGlobalScopeFunction → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/launcher/ServiceWorkerEntry.cpp::main → sigaction [signal]
- /home/hwang/work/E/starfish_/src/launcher/SharedWorkerEntry.cpp::main → sigaction [signal]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.prepareExternalSurface → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.prepareExternalSurface → bindRenderbuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.prepareExternalSurface → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.flushExternalSurface → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.flushExternalSurface → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.rectProgram → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.rectProgram → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.bindTexIdx → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.bindTexIdx → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.bindTexPos → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.bindTexPos → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.streamArrayBuffer → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternal → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternal → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternal → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternal → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternal → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternal → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternalWithMask → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternalWithMask → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternalWithMask → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternalWithMask → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternalWithMask → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramEGLImageExternalWithMask → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgram → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgram → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgram → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgram → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgram → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgram → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClip → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClip → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClip → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClip → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClip → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClip → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClipEGLImageExternal → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClipEGLImageExternal → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClipEGLImageExternal → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClipEGLImageExternal → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClipEGLImageExternal → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramRoundedClipEGLImageExternal → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramWithMask → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramWithMask → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramWithMask → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramWithMask → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramWithMask → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texShaderProgramWithMask → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramW → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramW → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramW → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramW → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramW → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramW → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramEGLImageExternalW → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramEGLImageExternalW → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramEGLImageExternalW → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramEGLImageExternalW → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramEGLImageExternalW → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramEGLImageExternalW → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramH → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramH → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramH → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramH → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramH → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramH → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramHWithMask → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramHWithMask → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramHWithMask → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramHWithMask → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramHWithMask → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorContextGL.texBlurShaderProgramHWithMask → bindTexIdx [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CanvasSurfaceGL.ensureGenerateTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CanvasSurfaceGL.ensureGenerateTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CanvasSurfaceGL.ensureGenerateTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CanvasSurfaceGL.ensureGenerateTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CanvasSurfaceGL.unmapBufferAndNotifyUpdatedRegion → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CanvasSurfaceGL.unmapBufferAndNotifyUpdatedRegion → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.~CompositorImplGL → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.~CompositorImplGL → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTessellatedPolygon → bindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawFilteredTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawFilteredTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawFilteredTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawFilteredTexture → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawFilteredTexture → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawTexture → bindTexPos [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawSurface → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.drawSurface → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.pushFBOContext → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.pushFBOContext → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.pushFBOContext → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.pushFBOContext → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.popFBOContext → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.popFBOContext → bindRenderbuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::CompositorImplGL.popFBOContext → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::dumpTextureToPNG → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::dumpTextureToPNG → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::dumpTextureToPNG → bindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/CompositorGL.cpp::dumpTextureToPNG → bindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindAttribLocation → glBindAttribLocation [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindBuffer → glBindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindFramebuffer → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindRenderbuffer → glBindRenderbuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindTexture → glBindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindVertexArray → glBindVertexArray [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindBufferRange → glBindBufferRange [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/EvasGL.cpp::EvasGL.bindBufferBase → glBindBufferBase [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindAttribLocation → glBindAttribLocation [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindBuffer → glBindBuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindFramebuffer → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindRenderbuffer → glBindRenderbuffer [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindTexture → glBindTexture [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindVertexArray → glBindVertexArray [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindBufferRange → glBindBufferRange [socket]
- /home/hwang/work/E/starfish_/src/platform/canvas/gl/GenericGL.cpp::GenericGL.bindBufferBase → glBindBufferBase [socket]
- /home/hwang/work/E/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp::transformetoNetscapeCookieFormat → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/platform/network/http/HTTPCache.cpp::extractHTTPCacheEntryProperty → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp::launchProcess → strsignal [signal]
- /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp::launchProcess → sigaction [signal]
- /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp::killProcess → kill [signal]
- /home/hwang/work/E/starfish_/src/platform/process/base/Process.cpp::killProcess → kill [signal]
- /home/hwang/work/E/starfish_/src/platform/public/DeviceInfo.cpp::getLocalIPAddress → socket [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/android/AndroidBridge.cpp::Java_com_samsung_android_lightweightwebengine_internal_LweWebViewImpl_init → GetJavaVM [jni]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::initEGLDisplay → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.~FboPresenter → pthread_cond_signal [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.onMakeCurrent → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.onSwapBuffers → pthread_cond_signal [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.onSwapBuffers → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.allocBuffer → glBindTexture [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.allocBuffer → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.buildBlitShader → glBindAttribLocation [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.buildBlitShader → glBindBuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.blitFrame → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.blitFrame → glBindTexture [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::FboPresenter.blitFrame → glBindBuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::WebViewEcoreWl2.WebViewEcoreWl2 → ecore_wl2_display_connect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::WebViewEcoreWl2.WebViewEcoreWl2 → ecore_wl2_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp::WebViewEcoreWl2.~WebViewEcoreWl2 → ecore_wl2_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp::createEGLDisplay → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::flushTreeEvents → g_signal_emit_by_name [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::flushTreeEvents → g_signal_emit_by_name [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::a11yDbusFilter → dbus_connection_send [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::enableBridge → dbus_connection_add_filter [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::enableBridge → g_signal_emit_by_name [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::enableBridge → g_signal_emit_by_name [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::enableBridge → g_signal_emit_by_name [signal]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp::disableBridge → dbus_connection_remove_filter [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.onMakeCurrent → bindRenderFBO [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.onSwapBuffers → bindRenderFBO [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.ensureContext → ecore_wl2_connected_display_get [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.ensureContext → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.bindRenderFBO → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.allocBuffer → glBindTexture [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp::ThreadedTbmPresenter.allocBuffer → glBindFramebuffer [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp::WebViewFlutter.initEGL → ecore_wl2_display_connect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp::WebViewFlutter.initEGL → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp::WebViewFlutter.Destroy → ecore_wl2_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::createEGLDisplay → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.WebViewTcoreWl → tizen_core_wl_display_connect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.WebViewTcoreWl → tizen_core_wl_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.WebViewTcoreWl → tizen_core_wl_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.WebViewTcoreWl → tizen_core_wl_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_event_remove_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.~WebViewTcoreWl → tizen_core_wl_display_disconnect [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp::WebViewTcoreWl.setupEventHandlers → tizen_core_wl_event_add_listener [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/x11/LWEWebViewX11.cpp::createEGLDisplay → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/public/bridge/x11/LWEWebViewX11.cpp::WebViewX11.registerX11Fd → ConnectionNumber [socket]
- /home/hwang/work/E/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp::AddJavaScriptInterface → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp::RemoveJavascriptInterface → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp::RemoveJavascriptInterface → scriptBindingInstance [socket]
- /home/hwang/work/E/starfish_/src/shell/Shell.cpp::sigHandler → signal [signal]
- /home/hwang/work/E/starfish_/src/shell/Shell.cpp::sigHandler → kill [signal]
- /home/hwang/work/E/starfish_/src/shell/Shell.cpp::setBacktraceHandler → sigaction [signal]
- /home/hwang/work/E/starfish_/src/shell/Shell.cpp::setBacktraceHandler → sigaction [signal]
- /home/hwang/work/E/starfish_/src/shell/dummy/WindowDummy.cpp::RendererDelegateOffscreen.initialize → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/shell/glib/AppLoopGlib.cpp::init → g_unix_signal_add [signal]
- /home/hwang/work/E/starfish_/src/shell/glib/AppLoopGlib.cpp::init → g_unix_signal_add [signal]
- /home/hwang/work/E/starfish_/src/shell/libuv/AppLoopLibuv.cpp::start → sigaction [signal]
- /home/hwang/work/E/starfish_/src/shell/windows/StarfishShell.cpp::Shell.handleMessage → KillTimer [signal]
- /home/hwang/work/E/starfish_/src/shell/windows/StarfishShell.cpp::Shell.handleMessage → KillTimer [signal]
- /home/hwang/work/E/starfish_/src/shell/x11_webcontainer/WindowX11Webcontainer.cpp::createEGLDisplay → eglBindAPI [socket]
- /home/hwang/work/E/starfish_/src/shell/x11_webcontainer/WindowX11Webcontainer.cpp::registerX11Fd → ConnectionNumber [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/measure-bench/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/measure-bench/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/measure-bench/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/measure-bench/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/measure-bench/server.py::H.do_POST → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/measure-bench/server.py::H.do_POST → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_POST → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/mse-smoke/server.py::H.do_POST → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/style-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/style-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/style-smoke/server.py::H.do_GET → send_header [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/style-smoke/server.py::H.do_GET → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/style-smoke/server.py::H.do_POST → send_response [socket]
- /home/hwang/work/E/starfish_/tool/perf_tools/style-smoke/server.py::H.do_POST → send_header [socket]
- /home/hwang/work/E/starfish_/tool/runner/http_server.py::RequestHandler.end_headers → send_header [socket]
- /home/hwang/work/E/starfish_/tool/runner/http_server.py::RequestHandler.end_headers → send_header [socket]
- /home/hwang/work/E/starfish_/tool/runner/http_server.py::RequestHandler.end_headers → send_header [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_audit.py::probe → HTTPSConnection [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_audit.py::probe → HTTPConnection [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_runner.py::run_one → _is_connect_refused_on_navigation [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_server.py::_port_open → connect_ex [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_server.py::_http_ok → create_connection [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_server.py::_http_ok → sendall [socket]
- /home/hwang/work/E/starfish_/tool/wpt/scripts/wpt_server.py::_http_ok → recv [socket]

<!-- Total: 7004 nodes, 124 relevant -->
