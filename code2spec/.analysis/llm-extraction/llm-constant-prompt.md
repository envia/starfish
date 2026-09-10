
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
# Languages: c (930), cpp (809), java (11), javascript (22), python (43)

## Constant Definitions
- [c] LWE_EXPORT = __declspec(dllexport)
 | /home/hwang/work/D/starfish_/compat/tizen_5.0/inc/LWEWebView.h:25
- [c] LWE_EXPORT = __attribute__((visibility("default")))
 | /home/hwang/work/D/starfish_/compat/tizen_5.0/inc/LWEWebView.h:27
- [c] TIZEN_COMPAT_HEADER_5_0 = N/A | /home/hwang/work/D/starfish_/compat/tizen_5.0/inc/LWEWebView.h:85
- [c] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/work/D/starfish_/compat/tizen_5.0/inc/LWEWebView.h:180
- [c] LWE_MIN_FONT_SIZE = 1
 | /home/hwang/work/D/starfish_/compat/tizen_5.0/inc/LWEWebView.h:181
- [c] LWE_MAX_FONT_SIZE = 72
 | /home/hwang/work/D/starfish_/compat/tizen_5.0/inc/LWEWebView.h:182
- [python] SCRIPT_PATH = N/A | /home/hwang/work/D/starfish_/docs/generator/run.py:7
- [c] LWE_EXPORT = __declspec(dllexport)
 | /home/hwang/work/D/starfish_/inc/LWEWebView.h:30
- [c] LWE_EXPORT = __declspec(dllimport)
 | /home/hwang/work/D/starfish_/inc/LWEWebView.h:32
- [c] LWE_EXPORT = __attribute__((visibility("default")))
 | /home/hwang/work/D/starfish_/inc/LWEWebView.h:35
- [c] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/work/D/starfish_/inc/LWEWebView.h:190
- [c] LWE_MIN_FONT_SIZE = 1
 | /home/hwang/work/D/starfish_/inc/LWEWebView.h:191
- [c] LWE_MAX_FONT_SIZE = 72
 | /home/hwang/work/D/starfish_/inc/LWEWebView.h:192
- [c] LWE_EXPORT = __declspec(dllexport)
 | /home/hwang/work/D/starfish_/inc/LWEWorker.h:30
- [c] LWE_EXPORT = __declspec(dllimport)
 | /home/hwang/work/D/starfish_/inc/LWEWorker.h:32
- [c] LWE_EXPORT = __attribute__((visibility("default")))
 | /home/hwang/work/D/starfish_/inc/LWEWorker.h:35
- [cpp] STARFISH_LINE_BREAK_ITERATOR_POOL_SIZE = 4
 | /home/hwang/work/D/starfish_/src/Starfish.cpp:81
- [c] BDWGC_FREE_SPACE_DIVISOR = 12
 | /home/hwang/work/D/starfish_/src/Starfish.h:40
- [c] COMPILER_CLANG = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:85
- [c] COMPILER_MSVC = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:87
- [c] COMPILER_GCC = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:89
- [c] COMPILER_SUPPORTS_CXX_OVERRIDE_CONTROL = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:100
- [c] COMPILER_QUIRK_FINAL_IS_CALLED_SEALED = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:101
- [c] ALWAYS_INLINE = inline __attribute__((__always_inline__))
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:108
- [c] ALWAYS_INLINE = __forceinline
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:110
- [c] ALWAYS_INLINE = inline
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:112
- [c] NEVER_INLINE = __attribute__((__noinline__))
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:119
- [c] NEVER_INLINE = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:121
- [c] NO_RETURN = __attribute((__noreturn__))
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:146
- [c] NO_RETURN = __declspec(noreturn)
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:148
- [c] NO_RETURN = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:150
- [c] EXPORT = __declspec(dllexport)
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:157
- [c] EXPORT = __attribute__((visibility("default")))
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:159
- [c] FALLTHROUGH = __attribute__((fallthrough))
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:166
- [c] FALLTHROUGH = /* fall through */
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:168
- [c] FALLTHROUGH = /* fall through */
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:171
- [c] FALLTHROUGH = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:173
- [c] NULLABLE = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:176
- [c] ENSURE_ENUM_UNSIGNED = : unsigned int
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:184
- [c] ENSURE_ENUM_UNSIGNED = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:186
- [c] OS_WINDOWS = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:190
- [c] OS_WINDOWS = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:192
- [c] OS_POSIX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:196
- [c] OS_POSIX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:198
- [c] OS_POSIX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:200
- [c] OS_POSIX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:205
- [c] OS_POSIX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:207
- [c] OS_POSIX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:209
- [c] NOMINMAX = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:215
- [c] SSIZE_T | /home/hwang/work/D/starfish_/src/StarfishBase.h:218
- [c] WIN32_LEAN_AND_MEAN = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:224
- [c] ESCARGOT = // for use additional functions in GCutil
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:230
- [c] TRUE = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:256
- [c] FALSE = 0
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:260
- [c] DEFAULT_CLEAR_STACK_SIZE = 102400
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:279
- [c] ELABORATE_CLEAR_STACK_SIZE = DEFAULT_CLEAR_STACK_SIZE * 4
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:280
- [c] STARFISH_32 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:308
- [c] STARFISH_64 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:310
- [c] STARFISH_X86_64 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:317
- [c] STARFISH_X86 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:323
- [c] STARFISH_ARM = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:327
- [c] STARFISH_ARM_NEON = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:329
- [c] STARFISH_ARM64 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:333
- [c] STARFISH_ARM_NEON = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:334
- [c] STARFISH_RISCV32 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:337
- [c] STARFISH_RISCV64 = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:340
- [c] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:358
- [c] STARFISH_ENABLE_PROFILE_LOADING = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:359
- [c] STARFISH_LOG_TAG = "[WORKER] "
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:363
- [c] STARFISH_LOG_TAG = ""
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:365
- [c] STARFISH_CRASH = STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:476
- [c] WARN_UNUSED_RETURN = __attribute__((__warn_unused_result__))
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:578
- [c] WARN_UNUSED_RETURN = N/A | /home/hwang/work/D/starfish_/src/StarfishBase.h:582
- [c] STARFISH_PIXEL_R_INDEX = 0
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1079
- [c] STARFISH_PIXEL_G_INDEX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1080
- [c] STARFISH_PIXEL_B_INDEX = 2
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1081
- [c] STARFISH_PIXEL_A_INDEX = 3
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1082
- [c] STARFISH_PIXEL_R_INDEX = 2
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1084
- [c] STARFISH_PIXEL_G_INDEX = 1
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1085
- [c] STARFISH_PIXEL_B_INDEX = 0
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1086
- [c] STARFISH_PIXEL_A_INDEX = 3
 | /home/hwang/work/D/starfish_/src/StarfishBase.h:1087
- [c] APP_NAME = "Netscape"
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:23
- [c] APP_CODE_NAME = "Mozilla"
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:24
- [c] PRODUCT_NAME = "Gecko"
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:25
- [c] STARFISH_NAME = "Starfish"
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:26
- [c] VENDOR_NAME = "Samsung Electronics Co., Ltd."
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:27
- [c] VERSION = STARFISH_VERSION_STR
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:28
- [c] USER_AGENT_MAXIMUM_DATE_VALUE = 8.64e15
 | /home/hwang/work/D/starfish_/src/StarfishInfo.h:31
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:24
- [c] PORT_EVENTLOOP_BACKEND_GLIB = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:25
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:26
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:27
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:29
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:30
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:31
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:32
- [c] PORT_GRAPHIC_BACKEND_MOCK = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:34
- [c] PORT_CANVAS_BACKEND_MOCK = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:35
- [c] PORT_EVENTLOOP_BACKEND_GLIB = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:36
- [c] PORT_IMAGEDECODER_BACKEND_MOCK = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:37
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:38
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:40
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:41
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:42
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:43
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:45
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:46
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:47
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:48
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:50
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:51
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:52
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:53
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:55
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:56
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:57
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:58
- [c] PORT_WEBVIEW_BRIDGE_FLUTTER = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:59
- [c] PORT_BACKEND_GL_WITH_EXTERNAL_TBM = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:60
- [c] PORT_CANVAS_NEEDS_PREMULTIPLIED_ALPHA = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:64
- [c] STARFISH_WEBWORKER_NOT_HOST = N/A | /home/hwang/work/D/starfish_/src/StarfishPlatform.h:68
- [cpp] STARFISH_LOCAL_STORAGE_FILE_NAME = "localStorage.txt"
 | /home/hwang/work/D/starfish_/src/StoragePathProvider.cpp:27
- [cpp] STARFISH_COOKIES_FILE_NAME = "cookies.txt"
 | /home/hwang/work/D/starfish_/src/StoragePathProvider.cpp:28
- [cpp] STARFISH_CACHE_DIR_NAME = "cache"
 | /home/hwang/work/D/starfish_/src/StoragePathProvider.cpp:29
- [cpp] STARFISH_SHARED_WORKER_DIR_NAME = "shared_worker"
 | /home/hwang/work/D/starfish_/src/StoragePathProvider.cpp:30
- [cpp] STARFISH_SERVICE_WORKER_DIR_NAME = "service_worker"
 | /home/hwang/work/D/starfish_/src/StoragePathProvider.cpp:31
- [c] STARFISH_ASSERT : Attribute(QualifiedName name , String* value)
        : m_name(name)
    { | /home/hwang/work/D/starfish_/src/core/dom/Attribute.h:46
- [c] STARFISH_NATIVEGRADIENT_CACHE_SIZE = 1920 * 1080 * 4 * 2
 | /home/hwang/work/D/starfish_/src/core/dom/Document.h:33
- [c] HTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
 | /home/hwang/work/D/starfish_/src/core/dom/Document.h:92
- [c] SVG_NAMESPACE = "http://www.w3.org/2000/svg"
 | /home/hwang/work/D/starfish_/src/core/dom/Document.h:94
- [c] XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
 | /home/hwang/work/D/starfish_/src/core/dom/Document.h:95
- [c] XMLNS_NAMESPACE = "http://www.w3.org/2000/xmlns/"
 | /home/hwang/work/D/starfish_/src/core/dom/Document.h:96
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/dom/Document.h:709
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/dom/Document.h:710
- [c] VIRTUAL = virtual
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLBodyElement.h:40
- [c] OVERRIDE = override
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLBodyElement.h:41
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/dom/HTMLBodyElement.h:51
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/dom/HTMLBodyElement.h:52
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.h:97
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.h:98
- [c] VIRTUAL = virtual
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.h:173
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/dom/HTMLElement.h:174
- [c] STARFISH_DEFAULT_IFRAME_WIDTH = 300
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLIFrameElement.h:27
- [c] STARFISH_DEFAULT_IFRAME_HEIGHT = 150
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLIFrameElement.h:28
- [c] STARFISH_OBJECT_ELEMENT_DEFAULT_WIDTH = 300
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLObjectElement.h:25
- [c] STARFISH_OBJECT_ELEMENT_DEFAULT_HEIGHT = 150
 | /home/hwang/work/D/starfish_/src/core/dom/HTMLObjectElement.h:26
- [cpp] STARFISH_SCROLL_START_THRESHOLD = 10
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:40
- [cpp] STARFISH_SCROLL_START_FLING_THRESHOLD = 100
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:41
- [cpp] STARFISH_SCROLL_FLING_LENGTH_MULTIPLY_BASE = 500
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:42
- [cpp] STARFISH_SCROLL_FLING_LENGTH_MULTIPLY_RATIO = 1500
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:43
- [cpp] STARFISH_SCROLL_FLING_BASE_TIME_IN_MS = 1000
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:44
- [cpp] STARFISH_SCROLL_FLING_SPEED_RATIO = 1
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:45
- [cpp] STARFISH_SCROLL_ACTIVE_TIME_IN_MS = 500
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:46
- [cpp] STARFISH_SCROLLBAR_THICKNESS = 4
 | /home/hwang/work/D/starfish_/src/core/dom/Scrolling.cpp:579
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/dom/ShadowRoot.h:166
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/dom/ShadowRoot.h:167
- [c] TEXTTRACK_INVALID_TIMEVALUE = -1
 | /home/hwang/work/D/starfish_/src/core/dom/TextTrack.h:32
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/dom/TextTrackCue.h:103
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/dom/TextTrackCue.h:104
- [cpp] CRASH = STARFISH_CRASH
 | /home/hwang/work/D/starfish_/src/core/dom/canvas/CanvasRenderingContext2DMixIn.cpp:62
- [cpp] NEEDS_UNPREMULTIPLIED = N/A | /home/hwang/work/D/starfish_/src/core/dom/canvas/CanvasRenderingContext2DMixIn.cpp:67
- [c] STARFISH_CANVAS_DEFAULT_WIDTH = 300
 | /home/hwang/work/D/starfish_/src/core/dom/canvas/HTMLCanvasElement.h:29
- [c] STARFISH_CANVAS_DEFAULT_HEIGHT = 150
 | /home/hwang/work/D/starfish_/src/core/dom/canvas/HTMLCanvasElement.h:30
- [cpp] CRASH = STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE
 | /home/hwang/work/D/starfish_/src/core/dom/canvas/ImageData.cpp:31
- [c] DEFINE_GETTER_SETTER : const override ; | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLFramebuffer.h:40
- [c] FILL_GC_POINTER : BEGIN_IMPLEMENT_NEW_WITH_GC_DESC(WebGLRenderingContext,
                                     WebGLRenderingContextBaseMixIn) ; | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:303
- [c] FILL_GC_POINTER : FILL_GC_POINTER(WebGLRenderingContext, m_unpackColorSpace) ; | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:306
- [c] END_IMPLEMENT_NEW_WITH_GC_DESC : FILL_GC_COLLECTION(WebGLRenderingContext, m_enabledExtensions) ; | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLRenderingContext.h:308
- [c] DEFINE_GETTER : DEFINE_GETTER(GLint, rangeMin) ; | /home/hwang/work/D/starfish_/src/core/dom/canvas/webgl/WebGLShaderPrecisionFormat.h:50
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:238
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:258
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:267
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:282
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:291
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:304
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:317
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:327
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:353
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:378
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:399
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:412
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:430
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:468
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:481
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:499
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:537
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:554
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:572
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:610
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:621
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:632
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:649
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:666
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:686
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:711
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:729
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:767
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:790
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:808
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:826
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:847
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:859
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:882
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:912
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:943
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:975
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1009
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1028
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1047
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1072
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1106
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1124
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1139
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1146
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1159
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1200
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1217
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1235
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1249
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1264
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1288
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1310
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1326
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1350
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1370
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1412
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1440
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1466
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1485
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1504
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1530
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1554
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1582
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1609
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1628
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1647
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1664
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1675
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1688
- [cpp] HTML_BEGIN_STATE | /home/hwang/work/D/starfish_/src/core/dom/parser/HTMLTokenizer.cpp:1698
- [c] UNIT | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGMarkerElement.h:37
- [c] ORIENT | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGMarkerElement.h:43
- [c] STARFISH_SVG_ANIMATED_LENGTH_GETTER : virtual void styleForPresentationAttribute(
        CSSStyleValuePairVectorHolder& cssValues,
        MatchedStyleRules<>& matchedRules,
        Optional<const MutablePropertyValueList*> cssCustomValues) override;

    virtual void didNodeInserted(Node* parent, Node* newChild) override;
    virtual void didNodeRemoved(Node* parent, Node* oldChild) override;

    virtual bool needsGeometryAttributes() override
    {
        return true;
    }

    virtual bool needsSizingAttributes() override
    {
        return true;
    }

    virtual bool isRenderableElement() override
    {
        return true;
    }

    virtual bool isPaintServerLikeElement() override
    {
        return true;
    } | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGMaskElement.h:45
- [c] STARFISH_ASSERT : const override { | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGSymbolElement.h:62
- [c] STARFISH_SVG_ANIMATED_LENGTH_GETTER : virtual NativeImageData::PreserveAspectRatioAlign preserveAspectRatioAlign()
        override;
    virtual NativeImageData::PreserveAspectRatioMeetOrSlice
    preserveAspectRatioMeetOrSlice() override; | /home/hwang/work/D/starfish_/src/core/dom/svg/SVGSymbolElement.h:68
- [c] READABLE_STREAM_BUFFER_CHUNK_SIZE = 65536
 | /home/hwang/work/D/starfish_/src/core/fetch/stream/ReadableStreamBuffer.h:32
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/fileapi/FileReader.h:65
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/fileapi/FileReader.h:66
- [cpp] STARFISH_NATIVEGRADIENT_MAX_SIZE = 512
 | /home/hwang/work/D/starfish_/src/core/layout/FrameBox.cpp:1850
- [c] FRAMEBOX_RAREDATA_TAG = 0x3
 | /home/hwang/work/D/starfish_/src/core/layout/FrameBox.h:65
- [c] STARFISH_ASSERT : LayoutUnit operator/(const LayoutUnit& a , const LayoutUnit& b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:675
- [c] STARFISH_ASSERT : double operator/(const LayoutUnit& a , double b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:691
- [c] STARFISH_ASSERT : LayoutUnit operator/(const LayoutUnit& a , unsigned short b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:703
- [c] STARFISH_ASSERT : LayoutUnit operator/(const LayoutUnit& a , unsigned long b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:715
- [c] STARFISH_ASSERT : float operator /(const float a , const LayoutUnit& b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:727
- [c] STARFISH_ASSERT : LayoutUnit operator /(const int a , const LayoutUnit& b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:739
- [c] STARFISH_ASSERT : LayoutUnit operator /(unsigned a , const LayoutUnit& b)
{ | /home/hwang/work/D/starfish_/src/core/layout/LayoutUtil.h:751
- [cpp] STARFISH_GRAPHICS_BUFFER_ADDITIONAL_FACTOR_MAX_SCALE = 6
 | /home/hwang/work/D/starfish_/src/core/layout/StackingContext.cpp:1424
- [cpp] STARFISH_CANVAS_SURFACE_TILE_SIZE = 128
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/Canvas.cpp:79
- [cpp] NEEDS_UNPREMULTIPLIED = N/A | /home/hwang/work/D/starfish_/src/core/modules/canvas/Canvas.cpp:847
- [c] STARFISH_CANVAS_LENGTH_MAX = 65535
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/Canvas.h:23
- [c] SPACE_SIZE_DENOMINATOR = 60
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/font/Font.h:187
- [cpp] ESCARGOT = // for GCutil
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/BufferedNativeImageData.cpp:21
- [cpp] NEEDS_PREMULTIPLIED_ALPHA = N/A | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/ImageDecoder.cpp:25
- [cpp] PNG_SKIP_SETJMP_CHECK = N/A | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/ImageDecoder.cpp:28
- [cpp] STARFISH_ENABLE_WEBP = N/A | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/ImageDecoder.cpp:52
- [cpp] GIF_DISPOSE_SHIFT = 2
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/ImageDecoder.cpp:55
- [cpp] GIF_TRANSPARENT_MASK = 0x01
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/ImageDecoder.cpp:56
- [cpp] GIF_DISPOSE_MASK = 0x07
 | /home/hwang/work/D/starfish_/src/core/modules/canvas/image/ImageDecoder.cpp:57
- [cpp] CV_STATUS_TIMEOUT_MS = 1
 | /home/hwang/work/D/starfish_/src/core/modules/cast/BaseRunnable.cpp:27
- [cpp] CAST_APP_INFOR_BUFFER_SIZE = 1024
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastApplication.cpp:31
- [cpp] DEVICE_VENDOR_NAME = VENDOR_NAME
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:27
- [cpp] DEVICE_MODEL_NAME = STARFISH_NAME
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:28
- [cpp] DEVICE_PRODUCT_NAME = STARFISH_NAME
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:29
- [cpp] DEVICE_PRODUCT_VERSION = VERSION
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:30
- [cpp] DEVICE_TYPE = "urn:dial-multiscreen-org:service:dial:1"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:31
- [cpp] DEVICE_UUID = "9ad8fd1a-e0f5-44e9-8322-61dd08533c04"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:32
- [cpp] DEVICE_FRIENDLY_NAME = "LWE:StarFish"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:33
- [cpp] DEVICE_PRODUCT_NAME_AND_VERSION = \
    DEVICE_PRODUCT_NAME "/" DEVICE_PRODUCT_VERSION
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:34
- [cpp] SERVICE_ID = "upnp::id::lwe"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:36
- [cpp] DIAL_VERSION = "2.1"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:37
- [cpp] CAST_APP_SERVICE_TYPE = "urn:dial-multiscreen-org:schemas:dial"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.cpp:38
- [c] SSDP_GROUP = "239.255.255.250"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:27
- [c] SSDP_PORT = 1900
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:28
- [c] SSDP_ST = "urn:dial-multiscreen-org:service:dial:1"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:29
- [c] LOCATION_PORT = 5696
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:31
- [c] LOCATION_DESC = "/deviceDescription.xml"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:32
- [c] CAST_APP_URL = "/apps"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:33
- [c] LOG_ID = "DEBUG_CAST"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:49
- [c] COLOR_RESET = "\033[0m"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:56
- [c] COLOR_YELLOW = "\033[0;33m"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:57
- [c] COLOR_RED = "\033[31m"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:58
- [c] COLOR_GREEN = "\033[32m"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:59
- [c] COLOR_MAGENTA = "\033[35m"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:60
- [c] COLOR_CYAN = "\033[36m"
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastConfig.h:61
- [cpp] CAST_SERVER_THREAD_POOL_SIZE = 5
 | /home/hwang/work/D/starfish_/src/core/modules/cast/CastServer.cpp:34
- [cpp] CAST_DIAL_BUFFER_SIZE = 256
 | /home/hwang/work/D/starfish_/src/core/modules/cast/DIALRunnable.cpp:31
- [cpp] MAX_BUFFER_SIZE = 5000
 | /home/hwang/work/D/starfish_/src/core/modules/cast/SSDPRunnable.cpp:29
- [cpp] RECV_SLEEP_MS = 300
 | /home/hwang/work/D/starfish_/src/core/modules/cast/SSDPRunnable.cpp:30
- [c] IDB_LOCAL_STORAGE_DIR_PATH = "/indexedDB"
 | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBConfig.h:27
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(IDBCursor) | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBCursor.h:33
- [c] DEFINE_GETTER : DEFINE_GETTER(IDBConnection*, connection) ; | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBDatabase.h:82
- [c] DEFINE_GETTER : DEFINE_GETTER(unsigned long long, version) ; | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBDatabase.h:84
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(IDBIndex) | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBIndex.h:36
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(IDBKeyRange) | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBKeyRange.h:40
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBOpenDBRequest.h:61
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBOpenDBRequest.h:62
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBRequest.h:85
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/indexeddb/IDBRequest.h:86
- [c] STARFISH_MAX_MEDIASOURCE_BUFFERSPACE = 8 * 1024 * 1024
 | /home/hwang/work/D/starfish_/src/core/modules/mediasource/MediaSource.h:26
- [c] STARFISH_MAX_MEDIASOURCE_BUFFERSPACE_1080P = 16 * 1024 * 1024
 | /home/hwang/work/D/starfish_/src/core/modules/mediasource/MediaSource.h:30
- [c] STARFISH_MAX_MEDIASOURCE_BUFFERSPACE_4K = 60 * 1024 * 1024
 | /home/hwang/work/D/starfish_/src/core/modules/mediasource/MediaSource.h:34
- [cpp] STARFISH_FRAME_EVICTION_BACKWARD_DUR = 500
 | /home/hwang/work/D/starfish_/src/core/modules/mediasource/SourceBuffer.cpp:44
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCDataChannel.h:87
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCDataChannel.h:88
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(RTCDataChannelEvent) | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCDataChannelEvent.h:46
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCDtlsTransport.h:57
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCDtlsTransport.h:58
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(RTCIceCandidate) | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCIceCandidate.h:75
- [c] STARFISH_WEBRTC_DEBUG = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCPeerConnection.h:45
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCPeerConnection.h:376
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCPeerConnection.h:377
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(RTCPeerConnectionIceErrorEvent) | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCPeerConnectionIceErrorEvent.h:48
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(RTCPeerConnectionIceEvent) | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCPeerConnectionIceEvent.h:49
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCSctpTransport.h:54
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCSctpTransport.h:55
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(RTCTrackEvent) | /home/hwang/work/D/starfish_/src/core/modules/mediastream/RTCTrackEvent.h:86
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/networking/WebSocket.h:93
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/networking/WebSocket.h:94
- [cpp] DELTA_EPOCH_IN_MICROSECS = 11644473600000000Ui64
 | /home/hwang/work/D/starfish_/src/core/modules/profiling/Profiling.cpp:53
- [cpp] DELTA_EPOCH_IN_MICROSECS = 11644473600000000ULL
 | /home/hwang/work/D/starfish_/src/core/modules/profiling/Profiling.cpp:55
- [c] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/core/modules/profiling/Profiling.h:104
- [cpp] MOUSE_MOVE_EVENT_THRESHOLD = 100
 | /home/hwang/work/D/starfish_/src/core/modules/renderer/Renderer.cpp:44
- [cpp] MOUSE_MOVE_DRAG_EVENT_THRESHOLD = 16
 | /home/hwang/work/D/starfish_/src/core/modules/renderer/Renderer.cpp:48
- [cpp] STARFISH_CURL_HANDLE_CACHE_CLEAR_TIMEOUT_IN_MS = 5000
 | /home/hwang/work/D/starfish_/src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp:54
- [c] DECLARE_EVENT_LISTENER : VIRTUAL #define OVERRIDE | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/ServiceWorker.h:47
- [c] DEFINE_GETTER_SETTER : VIRTUAL #undef OVERRIDE | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/ServiceWorker.h:50
- [c] DEFINE_GETTER_SETTER : DEFINE_GETTER_SETTER(ServiceWorkerRegistrationData*, data, Data) ; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/ServiceWorkerRegistration.h:65
- [c] DECLARE_EVENT_LISTENER : VIRTUAL #define OVERRIDE | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/ServiceWorkerRegistration.h:68
- [c] DEFINE_GETTER_SETTER : void archive(Archiver& ar) override; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/ServiceWorkerRequest.h:39
- [c] STARFISH_ASSERT : Task(HandlerType handler , std::initializer_list<void*> params)
        : m_handler(handler)
    { | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/Task.h:38
- [javascript] HTML | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:2691
- [javascript] TAP | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:4081
- [cpp] SERVICE_WORKER_THREAD_POOL_SIZE = 1
 | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp:77
- [c] DEFINE_GETTER_SETTER : DEFINE_SETTER(Promise*, preloadResponse, PreloadResponse) ; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/host/FetchEvent.h:77
- [c] DEFINE_GETTER_SETTER : DEFINE_GETTER_SETTER(String*, resultingClientId, ResultingClientId) ; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/host/FetchEvent.h:79
- [c] DEFINE_GETTER_SETTER : DEFINE_GETTER_SETTER(Promise*, handled, Handled) ; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/host/FetchEvent.h:81
- [c] DEFINE_GETTER_SETTER : DEFINE_GETTER_SETTER(bool, waitToRespond, WaitToRespond) ; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/host/FetchEvent.h:84
- [c] DEFINE_GETTER_SETTER : DEFINE_GETTER_SETTER(bool, respondWithError, RespondWithError) ; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/host/FetchEvent.h:86
- [c] DEFINE_GETTER : bool isTerminating() override; | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/host/ServiceWorkerServer.h:62
- [c] DEFINE_GETTER_SETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(PushSubscription) | /home/hwang/work/D/starfish_/src/core/modules/serviceworker/push/PushSubscription.h:34
- [c] DEFINE_GETTER_SETTER : void registerDispatchMessageTask(
        SerializeWithTransferResult* serializedMessage) override; | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/IPCMessagePort.h:37
- [c] DEFINE_GETTER : void deserialize(IPCMessageDeserializer* deserializer) override; | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/SharedWorkerMessage.h:47
- [c] DEFINE_GETTER : void deserialize(IPCMessageDeserializer* deserializer) override; | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/SharedWorkerMessage.h:74
- [c] DEFINE_GETTER : void deserialize(IPCMessageDeserializer* deserializer) override; | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/SharedWorkerMessage.h:96
- [c] DEFINE_GETTER : DEFINE_GETTER(WorkerIPCAddress*, ipcAddress) ; | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/host/SharedWorkerAgent.h:83
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/host/SharedWorkerGlobalScope.h:67
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/sharedworker/host/SharedWorkerGlobalScope.h:68
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/tts/SpeechSynthesis.h:187
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/tts/SpeechSynthesis.h:188
- [c] DECLARE_EVENT_LISTENER : VIRTUAL #define OVERRIDE | /home/hwang/work/D/starfish_/src/core/modules/tts/SpeechSynthesis.h:243
- [c] DEFINE_GETTER : DECLARE_SCRIPT_BINDING_REQUIRED_FUNCTIONS(AudioBufferSourceNode) | /home/hwang/work/D/starfish_/src/core/modules/webaudio/AudioBufferSourceNode.h:47
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/webaudio/AudioScheduledSourceNode.h:40
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/webaudio/AudioScheduledSourceNode.h:41
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/webaudio/BaseAudioContext.h:129
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/webaudio/BaseAudioContext.h:130
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/AbstractWorker.h:43
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/AbstractWorker.h:44
- [c] DEFINE_GETTER : override ; | /home/hwang/work/D/starfish_/src/core/modules/worker/DedicatedWorkerGlobalScope.h:60
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/DedicatedWorkerGlobalScope.h:64
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/DedicatedWorkerGlobalScope.h:65
- [cpp] IO_EVENT_POLLING_TIMEOUT_MS = 300
 | /home/hwang/work/D/starfish_/src/core/modules/worker/PerProcess.cpp:40
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/Worker.h:58
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/Worker.h:59
- [c] WORKER_IPC_PROCESS_NAME = "ipc"
 | /home/hwang/work/D/starfish_/src/core/modules/worker/WorkerConfig.h:27
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/WorkerGlobalScope.h:152
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/modules/worker/WorkerGlobalScope.h:153
- [cpp] RECV_TIMEOUT = 1000
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/Connection.cpp:39
- [cpp] COLOR_SEND = "\033[0;36m"
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/Connection.cpp:40
- [cpp] COLOR_RECV = "\033[0;32m"
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/Connection.cpp:41
- [cpp] COLOR_RESET = "\033[0m"
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/Connection.cpp:42
- [cpp] MAX_LISTEN_SOCKET = 50
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/IORunnable.cpp:35
- [c] SCK_WAIT = 0
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/SocketNN.h:27
- [c] SCK_DONTWAIT = 1
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/SocketNN.h:28
- [c] SOCKETNN_INVALID_END_POINT = -1
 | /home/hwang/work/D/starfish_/src/core/modules/worker/util/network/SocketNN.h:29
- [cpp] STARFISH_TOUCH_SLOP_PX = 20.0
 | /home/hwang/work/D/starfish_/src/core/page/BrowsingContext.cpp:88
- [c] DECLARE_EVENT_LISTENER : VIRTUAL #define OVERRIDE | /home/hwang/work/D/starfish_/src/core/page/EventSource.h:116
- [cpp] STARFISH_THREAD_POOL_SIZE = 6
 | /home/hwang/work/D/starfish_/src/core/page/WebBase.cpp:62
- [cpp] ANNOTATE_SETUP = N/A | /home/hwang/work/D/starfish_/src/core/page/WebView.cpp:95
- [cpp] ANNOTATE_BLUE = 0xff00001b
 | /home/hwang/work/D/starfish_/src/core/page/WebView.cpp:98
- [cpp] STARFISH_FILLING_GRAPHICS_BUFFER_TIME_LIMIT = 100
 | /home/hwang/work/D/starfish_/src/core/page/WebView.cpp:236
- [cpp] STARFISH_FILLING_GRAPHICS_BUFFER_TIME_LIMIT = 10
 | /home/hwang/work/D/starfish_/src/core/page/WebView.cpp:238
- [cpp] STARFISH_IMAGE_DECODE_THREAD_THREAD_POOL_SIZE = 4
 | /home/hwang/work/D/starfish_/src/core/page/WebView.cpp:377
- [c] VIRTUAL = N/A | /home/hwang/work/D/starfish_/src/core/page/Window.h:315
- [c] OVERRIDE = N/A | /home/hwang/work/D/starfish_/src/core/page/Window.h:316
- [c] STARFISH_MAKE_STACK_ALLOCATED : enum Type {
        Auto,
        Fixed,

        InheritableNumber,
        Calc,
    } ; | /home/hwang/work/D/starfish_/src/core/style/Angle.h:38
- [c] STARFISH_ASSERT : Angle(Type type = Auto , float data = 0.f)
        : m_data(data) , m_type(type)
    { | /home/hwang/work/D/starfish_/src/core/style/Angle.h:48
- [c] STARFISH_MAKE_STACK_ALLOCATED : enum ParserOption ENSURE_ENUM_UNSIGNED { AllowNegative = 1 << 0 , AllowPercent = 1 << 1 , AllowAuto = 1 << 2 , AllowWithoutUnit = 1 << 3 , AllowNone = 1 << 4 , AllowDot = 1 << 5 , AllowUnderline = 1 << 6 , AllowPlus = 1 << 7 , AllowSharp = 1 << 8 , }; | /home/hwang/work/D/starfish_/src/core/style/CSSParser.h:62
- [c] CSSTOKENSTRING_BUILTIN_BUFFER_SIZE = 24
 | /home/hwang/work/D/starfish_/src/core/style/CSSParser.h:1256
- [c] CSSTOKEN_POOL_INITIAL_SIZE = 24
 | /home/hwang/work/D/starfish_/src/core/style/CSSParser.h:1708
- [cpp] STARFISH_MAKE_STACK_ALLOCATED | /home/hwang/work/D/starfish_/src/core/style/CSSVariableSyntaxTreeBuilder.cpp:55
- [cpp] MUL = true
 | /home/hwang/work/D/starfish_/src/core/style/CalcData.cpp:102
- [cpp] DIV = false
 | /home/hwang/work/D/starfish_/src/core/style/CalcData.cpp:103
- [c] STARFISH_MAKE_STACK_ALLOCATED : enum class ValueKind : uint8_t { kNone , kInvalid , // Only for type checking kNumber , kLength , kAngle , kTime , kPercentage , kCalcData , }; | /home/hwang/work/D/starfish_/src/core/style/CalcData.h:32
- [cpp] ENABLE_PARALLEL_BLUR = 0
 | /home/hwang/work/D/starfish_/src/core/style/FilterFunctions.cpp:29
- [c] CACHEABLE_GRADIENT_ITEM_EXTENT = (25.0f * 25.0f)
 | /home/hwang/work/D/starfish_/src/core/style/GradientData.h:27
- [c] CACHEABLE_GRADIENT_ITEM_EXTENT = (256.0f * 256.0f)
 | /home/hwang/work/D/starfish_/src/core/style/GradientData.h:31
- [c] STARFISH_MAKE_STACK_ALLOCATED : enum Type {
        Auto,
        Percent,
        Fixed,

        // After finishing resolveStyle, ex~Vmax values should be changed to
        // Fixed
        Ex,
        Em,
        Rem,
        Ch,
        Vw,
        Vh,
        Vmin,
        Vmax,

        // This is for line-height
        // (font-related value but does not change to Fixed since inheritance
        // issue)
        InheritableNumber,
        Calc,
        FitContent,
        MinContent,
        MaxContent
    } ; | /home/hwang/work/D/starfish_/src/core/style/Length.h:38
- [c] STARFISH_ASSERT : Length(Type type = Auto , float data = 0.f)
        : m_data(data) , m_type(type)
    { | /home/hwang/work/D/starfish_/src/core/style/Length.h:66
- [c] DECLARE_EVENT_LISTENER : VIRTUAL #define OVERRIDE | /home/hwang/work/D/starfish_/src/core/style/MediaQueryList.h:49
- [c] FOR_EACH_STYLE_ATTRIBUTE_TOTAL : enum KeyKind ENSURE_ENUM_UNSIGNED { Unknown , #define ADD_CSS_KEYKIND(Name, ...) Name, | /home/hwang/work/D/starfish_/src/core/style/Style.h:1041
- [c] MAX_TYPE_NAME = 30
 | /home/hwang/work/D/starfish_/src/core/util/Archivable.h:48
- [cpp] DOCUMENT = reinterpret_cast<rapidjson::Document*>(mDocument)
 | /home/hwang/work/D/starfish_/src/core/util/Archiver.cpp:75
- [cpp] STACK = (reinterpret_cast<JsonReaderStack*>(mStack))
 | /home/hwang/work/D/starfish_/src/core/util/Archiver.cpp:76
- [cpp] TOP = (STACK->top())
 | /home/hwang/work/D/starfish_/src/core/util/Archiver.cpp:77
- [cpp] CURRENT = (*TOP.value)
 | /home/hwang/work/D/starfish_/src/core/util/Archiver.cpp:78
- [cpp] WRITER = \
    reinterpret_cast<rapidjson::PrettyWriter<rapidjson::StringBuffer>*>(mWriter)
 | /home/hwang/work/D/starfish_/src/core/util/Archiver.cpp:358
- [cpp] STREAM = reinterpret_cast<rapidjson::StringBuffer*>(mStream)
 | /home/hwang/work/D/starfish_/src/core/util/Archiver.cpp:360
- [c] NUM_SUPPORTED_CRYPTO_ALGORITHM_TYPE = 3
 | /home/hwang/work/D/starfish_/src/core/util/Cryptographic.h:32
- [c] ID_INITIAL_VALUE = 0
 | /home/hwang/work/D/starfish_/src/core/util/Id.h:29
- [c] CALLED_CONSTRUCTOR_WITHOUT_NEW = "Constructor '%s' requires 'new'"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:25
- [c] FAILED_TO_CONSTRUCT = "Failed to construct '%s': %s"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:26
- [c] FAILED_TO_EXECUTE = "Failed to execute '%s' on '%s': %s"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:27
- [c] FAILED_TO_SET_PROPERTY = "Failed to set the '%s' property on '%s': %s"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:28
- [c] ILLEGAL_INVOKE = "Illegal invocation"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:29
- [c] ARGS_NOT_ENOUGH = "needs %s parameter, but only %s present."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:32
- [c] ARG_TYPE_IS_NONFINITE = "The provided double value is non-finite"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:33
- [c] ARG_TYPE_MISMATCH = "parameter %s ('%s') is not a(n) %s."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:34
- [c] ARG_TYPE_MISMATCH_2 = \
    "parameter %s ('%s') must be either a '%s' or '%s' element."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:35
- [c] ARG_TYPE_MISMATCH_WITH_INDEXABLE_TYPE = \
    "The parameter %s ('%s') is neither an array, nor does it have indexed " \
    "properties."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:37
- [c] ARG_TYPE_MISMATCH_WITH_ENUM = \
    "The provided value is not a valid enum value of type %s."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:40
- [c] SIGNATURE_NOT_FOUND = \
    "No function was found that matched the signature provided."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:42
- [c] QUERY_SELECTOR_IS_EMPTY = "The provided selector is empty."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:44
- [c] INVALID_SIZE = "The value provided %s, which is an invalid size."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:45
- [c] INVALID_TARGET_ORIGIN = "Invalid target origin '%s' in a call to '%s'"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:46
- [c] INVALID_DATA_CLONE = "'%s' could not be cloned."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:47
- [c] ORIGINS_ARE_NOT_MATCHED = \
    "The target origin provided('%s') does not match the recipient window's " \
    "origin('%s')"
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:48
- [c] NOT_POSITIVE = "The value provided (%s) is not positive or 0."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:51
- [c] EXCEED_MIN_BOUNDARY = \
    "The value provided (%s) is less than the minimum boundary (%s)."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:52
- [c] EXCEED_MAX_BOUNDARY = \
    "The value provided (%s) is greater than the maximum boundary (%s)."
 | /home/hwang/work/D/starfish_/src/core/util/Messages.h:54
- [c] CHECK_REF_COUNTED_LIFECYCLE = 0
 | /home/hwang/work/D/starfish_/src/core/util/RefCounted.h:31
- [c] CHECK_REF_COUNTED_LIFECYCLE = 1
 | /home/hwang/work/D/starfish_/src/core/util/RefCounted.h:33
- [c] STRING_BUILDER_INLINE_STORAGE_MAX = 64
 | /home/hwang/work/D/starfish_/src/core/util/String.h:1604
- [cpp] URL | /home/hwang/work/D/starfish_/src/core/util/URL.cpp:33
- [cpp] URL | /home/hwang/work/D/starfish_/src/core/util/URL.cpp:40
- [cpp] TYPE_LENGTH_LIMIT = 5
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:33
- [cpp] TRACE_ID_LENGTH_LIMIT = 10
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:34
- [cpp] CLR_RESET = "\033[0m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:35
- [cpp] CLR_DIM = "\033[0;2m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:36
- [cpp] CLR_RED = "\033[0;31m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:39
- [cpp] CLR_GREEN = "\033[0;32m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:40
- [cpp] CLR_GREY = "\033[0;37m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:41
- [cpp] CLR_BLACK = "\033[0;30m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:42
- [cpp] CLR_YELLOW = "\033[0;33m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:43
- [cpp] CLR_BLUE = "\033[0;34m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:44
- [cpp] CLR_MAGENTA = "\033[0;35m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:45
- [cpp] CLR_CYAN = "\033[0;36m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:46
- [cpp] CLR_DARKGREY = "\033[01;30m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:47
- [cpp] CLR_BRED = "\033[01;31m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:48
- [cpp] CLR_BYELLOW = "\033[01;33m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:49
- [cpp] CLR_BBLUE = "\033[01;34m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:50
- [cpp] CLR_BMAGENTA = "\033[01;35m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:51
- [cpp] CLR_BCYAN = "\033[01;36m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:52
- [cpp] CLR_BGREEN = "\033[01;32m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:53
- [cpp] CLR_WHITE = "\033[01;37m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:54
- [cpp] CLR_REDBG = "\033[0;41m"
 | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.cpp:55
- [c] ENABLE_TRACE = N/A | /home/hwang/work/D/starfish_/src/core/util/debug/Trace.h:33
- [c] DECLARE_EVENT_LISTENER : VIRTUAL #define OVERRIDE | /home/hwang/work/D/starfish_/src/core/xml/XMLHttpRequest.h:129
- [cpp] CAIRO_FORMAT = CAIRO_FORMAT_ARGB32
 | /home/hwang/work/D/starfish_/src/platform/canvas/CanvasCairo.cpp:68
- [cpp] CAIRO_FORMAT = CAIRO_FORMAT_ARGB32
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorCairo.cpp:38
- [cpp] EVAS_GL_IMAGE_PRESERVED = 0x30D2
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:161
- [cpp] EVAS_GL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:162
- [cpp] EGL_TRUE = 1
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:166
- [cpp] EGL_NONE = 0x3038
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:167
- [cpp] EGL_IMAGE_PRESERVED_KHR = 0x30D2
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:168
- [cpp] EGL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:169
- [cpp] EGL_DMA_BUF_PLANE3_FD_EXT = 0x3440
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:180
- [cpp] EGL_DMA_BUF_PLANE3_OFFSET_EXT = 0x3441
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:183
- [cpp] EGL_DMA_BUF_PLANE3_PITCH_EXT = 0x3442
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:186
- [cpp] EGL_ATTRIBUTE_MAX = 50
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:188
- [cpp] EGL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:190
- [cpp] MIN_MAX_TEXTURE_SIZE = 2048
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:295
- [cpp] RRCLIP_EGL_SAMPLER_PREAMBLE = \
    "#extension GL_OES_EGL_image_external : require\n" \
    "uniform samplerExternalOES uTexture;\n"
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:2053
- [cpp] GAUSSIAN_KERNEL_HALF_WIDTH = 11
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:2250
- [cpp] GAUSSIAN_KERNEL_STEP = 0.2
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:2251
- [cpp] GL_DEBUG_OUTPUT = 0x92E0
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:2662
- [cpp] GL_DEBUG_OUTPUT_SYNCHRONOUS = 0x8242
 | /home/hwang/work/D/starfish_/src/platform/canvas/CompositorGL.cpp:2665
- [cpp] UBLOCK_SUPPLEMENTAL_SYMBOLS_AND_PICTOGRAPHS = 298
 | /home/hwang/work/D/starfish_/src/platform/canvas/font/FontImplCairo.cpp:608
- [c] STARFISH_FONT_CAIRO_MIN_ENABLE_KERNING_SIZE = 48
 | /home/hwang/work/D/starfish_/src/platform/canvas/font/FontImplCairo.h:42
- [c] CHECK_ERROR = \
    if (error) {                                      \
        STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE(); \
    }
 | /home/hwang/work/D/starfish_/src/platform/canvas/font/FontImplCairo.h:47
- [cpp] HB_UNUSED = N/A | /home/hwang/work/D/starfish_/src/platform/canvas/font/hb-icu/HarfBuzzICU.cpp:53
- [cpp] ARRAY_LENGTH : unsigned int | /home/hwang/work/D/starfish_/src/platform/canvas/font/hb-icu/HarfBuzzICU.cpp:57
- [c] HB_ICU_H = N/A | /home/hwang/work/D/starfish_/src/platform/canvas/font/hb-icu/HarfBuzzICU.h:30
- [c] GL_NONE = 0
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/GLTypes.h:55
- [cpp] EGL_NO_CONTEXT = ((EGLContext)0)
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/GenericGL.cpp:30
- [cpp] GLAPIENTRY = N/A | /home/hwang/work/D/starfish_/src/platform/canvas/gl/GenericGL.cpp:48
- [c] GL_GLEXT_PROTOTYPES = N/A | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:27
- [c] EGL_EGLEXT_PROTOTYPES = N/A | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:42
- [c] GL_GLEXT_PROTOTYPES = N/A | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:43
- [c] GL_TEXTURE_EXTERNAL_OES = 0x8D65
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:57
- [c] GL_BGRA_EXT = 0x80E1
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:61
- [c] GL_MAJOR_VERSION = 0x821B
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:65
- [c] GL_MINOR_VERSION = 0x821C
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:69
- [c] GL_UNPACK_ROW_LENGTH = 0x0CF2
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:73
- [c] GL_UNPACK_SKIP_ROWS = 0x0CF3
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:77
- [c] GL_UNPACK_SKIP_PIXELS = 0x0CF4
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:81
- [c] GL_DEPTH_STENCIL = 0x84F9
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:85
- [c] GL_UNSIGNED_INT_24_8 = 0x84FA
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:89
- [c] GL_TEXTURE_SWIZZLE_R = 0x8E42
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:93
- [c] GL_TEXTURE_SWIZZLE_G = 0x8E43
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:96
- [c] GL_TEXTURE_SWIZZLE_B = 0x8E44
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:99
- [c] GL_TEXTURE_SWIZZLE_A = 0x8E45
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:102
- [c] TEXTURE_SWIZZLE_RGBA = 0x8E46
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:105
- [c] GL_RED = 0x1903
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:109
- [c] GL_GREEN = 0x1904
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:112
- [c] GL_BLUE = 0x1905
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:115
- [c] GL_ALPHA = 0x1906
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:118
- [c] GL_R8 = 0x8229
 | /home/hwang/work/D/starfish_/src/platform/canvas/gl/IncludeGL.h:121
- [cpp] DIR | /home/hwang/work/D/starfish_/src/platform/file/PlatformDirectory.cpp:44
- [cpp] DIR | /home/hwang/work/D/starfish_/src/platform/file/PlatformDirectory.cpp:57
- [cpp] STARFISH_RESOURCE_CACHE_SIZE = 1024 * 1024 * 4
 | /home/hwang/work/D/starfish_/src/platform/loader/ResourceLoader.cpp:45
- [cpp] MAX_PORT_DIGITS = 5
 | /home/hwang/work/D/starfish_/src/platform/loader/ResourceURL.cpp:25
- [cpp] MAX_PORT_NUMBER = 65535
 | /home/hwang/work/D/starfish_/src/platform/loader/ResourceURL.cpp:26
- [c] STARFISH_ASSERT : ResourceURL(const char* url , size_t len)
        : ResourceURL(String::fromUTF8(url, len))
    { | /home/hwang/work/D/starfish_/src/platform/loader/ResourceURL.h:53
- [cpp] MINUMUM_ANIMATOR_WAIT_TIME = 3000 // us
 | /home/hwang/work/D/starfish_/src/platform/message_loop/TimerLibUV.cpp:137
- [c] STARFISH_VIDEO_WIDTH_WHEN_VIDEO_NOT_EXISTS = 300
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayer.h:24
- [c] STARFISH_VIDEO_HEIGHT_WHEN_VIDEO_NOT_EXISTS = 150
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayer.h:25
- [cpp] STARFISH_ESPP_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:57
- [cpp] STARFISH_ESPP_MAX_AV_DIFF_IN_MS = 1500
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:60
- [cpp] STARFISH_ESPP_FEED_WAIT_US = (1000 * 25)
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:62
- [cpp] STARFISH_ESPP_TOTAL_BUFFER_SIZE = (64 * 1024 * 1024)
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:65
- [cpp] STARFISH_ESPP_AUDIO_BUFFER_SIZE = (768 * 1024)
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:66
- [cpp] STARFISH_ESPP_MIN_BYTE_THRESHOLD = 10
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:77
- [cpp] STARFISH_ESPP_SEEK_IDR_MAX_LOOKBACK_MS = 20000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:85
- [cpp] STARFISH_ESPP_SEEK_IDR_MAX_LOOKAHEAD_MS = 20000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:97
- [cpp] STARFISH_ESPP_MAX_SKIP_AHEAD_MS = 30000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:105
- [cpp] STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_PREROLL_MS = 50
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:112
- [cpp] STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_STEADY_MS = 500
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:113
- [cpp] STARFISH_ESPP_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:116
- [cpp] STARFISH_ESPP_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:117
- [c] STARFISH_ESPP_SEEK_WATCHDOG_MS = 12000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerESPlusPlayer.h:51
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:134
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:135
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:136
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:137
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:138
- [cpp] STARFISH_MSE_MIN_MARGIN_IN_MS = 3000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:139
- [cpp] SEEK_LAND_TOLERANCE_MS = 5000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:144
- [cpp] STARFISH_DECODE_LOOKAHEAD_MS_DEFAULT = 400
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:152
- [cpp] STARFISH_RUN_MSE_THREAD_WAIT_TIME = 1000 * 25 // 25ms
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.cpp:1799
- [c] MAX_WAITING_SECONDS_FOR_SEEK_OPERATION = 30000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.h:26
- [c] STARFISH_RUN_MSE_THREAD = N/A | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerLinux.h:29
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTV.cpp:45
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTV.cpp:46
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTV.cpp:47
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTV.cpp:48
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTV.cpp:49
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:50
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:51
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:52
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:53
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:54
- [cpp] STARFISH_MSE_MIN_MARGIN_IN_MS = 3000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:55
- [cpp] STARFISH_RUN_MSE_THREAD_WAIT_TIME = 1000 * 25 // 25ms
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.cpp:1228
- [c] EFL_BETA_API_SUPPORT = N/A | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.h:36
- [c] MAX_WAITING_SECONDS_FOR_SEEK_OPERATION = 30000
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.h:48
- [c] STARFISH_RUN_MSE_THREAD = N/A | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizen.h:51
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizenBase.cpp:47
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizenBase.cpp:48
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizenBase.cpp:49
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizenBase.cpp:50
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MediaPlayerTizenBase.cpp:51
- [cpp] STARFISH_FRAME_EVICTION_BACKWARD_DUR = 500
 | /home/hwang/work/D/starfish_/src/platform/multimedia/MockMediaPlayer.cpp:43
- [cpp] CURLHANDLE_CACHE_PRUNE_MINIMUM_SIZE = 12
 | /home/hwang/work/D/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp:42
- [cpp] CURLHANDLE_CACHE_PRUNE_MINIMUM_INTERVAL_S = 0.5
 | /home/hwang/work/D/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp:43
- [cpp] CURLHANDLE_CACHE_IDLE_TIME_LIMIT_S = 60
 | /home/hwang/work/D/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp:50
- [cpp] CURLPIPE_MULTIPLEX = 0
 | /home/hwang/work/D/starfish_/src/platform/network/curl/NetworkSharedResourceManager.cpp:795
- [cpp] INDEX_FILE_NAME = "/index.txt"
 | /home/hwang/work/D/starfish_/src/platform/network/http/HTTPCache.cpp:43
- [cpp] DEFAULT_HTTP_CACHE_SIZE = 1024 * 1024 * 50
 | /home/hwang/work/D/starfish_/src/platform/network/http/HTTPCache.cpp:44
- [cpp] MAX_ENTRY_FILE_SIZE = (DEFAULT_HTTP_CACHE_SIZE * 0.04)
 | /home/hwang/work/D/starfish_/src/platform/network/http/HTTPCache.cpp:45
- [cpp] NUM_OF_COL = 18
 | /home/hwang/work/D/starfish_/src/platform/network/http/HTTPCache.cpp:46
- [cpp] CURLPIPE_MULTIPLEX = 0
 | /home/hwang/work/D/starfish_/src/platform/network/http/HTTPTransaction.cpp:161
- [cpp] TTS_MODE_INTERRUPT = 3
 | /home/hwang/work/D/starfish_/src/platform/tts/TTSTV.cpp:43
- [cpp] TTS_REMOVED_INSTANCE_SIZE = 5
 | /home/hwang/work/D/starfish_/src/platform/tts/TTSTV.cpp:44
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS = "db/setting/accessibility/tts"
 | /home/hwang/work/D/starfish_/src/platform/tts/TTSTizen.cpp:63
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY = \
    "db/setting/accessibility/tts/temporary"
 | /home/hwang/work/D/starfish_/src/platform/tts/TTSTizen.cpp:68
- [cpp] TTS_REMOVED_INSTANCE_SIZE = 5
 | /home/hwang/work/D/starfish_/src/platform/tts/TTSTizen.cpp:71
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp:22
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp:22
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS = "db/setting/accessibility/tts"
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:54
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY = \
    "db/setting/accessibility/tts/temporary"
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:59
- [cpp] STARFISH_ATK_PLUG_TYPE = (starfish_atk_plug_get_type())
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:188
- [cpp] STARFISH_ATK_NODE_TYPE = (starfish_atk_node_get_type())
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/A11yAtspiBridge.cpp:407
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:32
- [cpp] EVAS_GL_NO_GL_H_CHECK = N/A | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:53
- [cpp] EGL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:64
- [cpp] EGL_IMAGE_PRESERVED_KHR = 0x30D2
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:67
- [cpp] EFL_BETA_API_SUPPORT = N/A | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:75
- [cpp] ANNOTATE_SETUP = N/A | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:103
- [cpp] ANNOTATE_GREEN = 0x00ff001b
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:106
- [cpp] EINA_LIST_FREE | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:645
- [cpp] EVAS_GL_OPTIONS_DIRECT_MEMORY_OPTIMIZE = (1 << 12)
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:981
- [cpp] EVAS_GL_OPTIONS_DIRECT_OVERRIDE = (1 << 13)
 | /home/hwang/work/D/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:982
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:40
- [cpp] EFL_BETA_API_SUPPORT = N/A | /home/hwang/work/D/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:42
- [cpp] ANNOTATE_SETUP = N/A | /home/hwang/work/D/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:56
- [cpp] ANNOTATE_GREEN = 0x00ff001b
 | /home/hwang/work/D/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:59
- [cpp] PORT_WINDOW_BACKEND | /home/hwang/work/D/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:82
- [cpp] PORT_COMPOSITOR_BACKEND | /home/hwang/work/D/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:83
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp:22
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/work/D/starfish_/src/public/bridge/x11/LWEWebViewX11.cpp:22
- [cpp] GC_CPP_H = N/A | /home/hwang/work/D/starfish_/src/public/bridge/x11/LWEWebViewX11.cpp:25
- [c] EXPORT_UNMANAGED_API = __declspec(dllexport)
 | /home/hwang/work/D/starfish_/src/public/contract/LWEDelegateConfig.h:24
- [c] EXPORT_UNMANAGED_API = __attribute__((visibility("default")))
 | /home/hwang/work/D/starfish_/src/public/contract/LWEDelegateConfig.h:26
- [cpp] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/work/D/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp:59
- [cpp] LWE_MIN_FONT_SIZE = 1
 | /home/hwang/work/D/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp:60
- [cpp] LWE_MAX_FONT_SIZE = 72
 | /home/hwang/work/D/starfish_/src/public/delegate/LWEWebContainerDelegate.cpp:61
- [cpp] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/work/D/starfish_/src/public/delegate/SettingsDelegate.cpp:29
- [cpp] THREAD_MINIMUM_STACK_SIZE = \
    4 * 1024 * 1024 // we need at least 4MB for stack
 | /home/hwang/work/D/starfish_/src/public/delegate/ThreadedCallHelper.cpp:27
- [c] LWE | /home/hwang/work/D/starfish_/src/shell/MiniBrowser.h:42
- [c] LWE | /home/hwang/work/D/starfish_/src/shell/MiniBrowser.h:46
- [c] SHELL_ENABLE_ELEMENTARY_GL = N/A | /home/hwang/work/D/starfish_/src/shell/ShellConfig.h:25
- [c] SHELL_X86_64 = N/A | /home/hwang/work/D/starfish_/src/shell/ShellConfig.h:30
- [c] SHELL_ENABLE_BACKTRACE = N/A | /home/hwang/work/D/starfish_/src/shell/ShellConfig.h:35
- [c] SHELL_ENABLE_TEST = N/A | /home/hwang/work/D/starfish_/src/shell/ShellConfig.h:39

<!-- Truncated: showing 1068 of 1435 relevant nodes -->
