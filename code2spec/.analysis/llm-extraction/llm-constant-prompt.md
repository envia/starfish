
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
# Languages: c (118), cpp (150), java (11), javascript (8), python (43)

## Constant Definitions
- [c] LWE_EXPORT = __declspec(dllexport)
 | /home/hwang/starfish/compat/tizen_5.0/inc/LWEWebView.h:25
- [c] LWE_EXPORT = __attribute__((visibility("default")))
 | /home/hwang/starfish/compat/tizen_5.0/inc/LWEWebView.h:27
- [c] TIZEN_COMPAT_HEADER_5_0 = N/A | /home/hwang/starfish/compat/tizen_5.0/inc/LWEWebView.h:85
- [c] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/starfish/compat/tizen_5.0/inc/LWEWebView.h:180
- [c] LWE_MIN_FONT_SIZE = 1
 | /home/hwang/starfish/compat/tizen_5.0/inc/LWEWebView.h:181
- [c] LWE_MAX_FONT_SIZE = 72
 | /home/hwang/starfish/compat/tizen_5.0/inc/LWEWebView.h:182
- [python] SCRIPT_PATH = N/A | /home/hwang/starfish/docs/generator/run.py:7
- [c] LWE_EXPORT = __declspec(dllexport)
 | /home/hwang/starfish/inc/LWEWebView.h:30
- [c] LWE_EXPORT = __declspec(dllimport)
 | /home/hwang/starfish/inc/LWEWebView.h:32
- [c] LWE_EXPORT = __attribute__((visibility("default")))
 | /home/hwang/starfish/inc/LWEWebView.h:35
- [c] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/starfish/inc/LWEWebView.h:190
- [c] LWE_MIN_FONT_SIZE = 1
 | /home/hwang/starfish/inc/LWEWebView.h:191
- [c] LWE_MAX_FONT_SIZE = 72
 | /home/hwang/starfish/inc/LWEWebView.h:192
- [c] LWE_EXPORT = __declspec(dllexport)
 | /home/hwang/starfish/inc/LWEWorker.h:30
- [c] LWE_EXPORT = __declspec(dllimport)
 | /home/hwang/starfish/inc/LWEWorker.h:32
- [c] LWE_EXPORT = __attribute__((visibility("default")))
 | /home/hwang/starfish/inc/LWEWorker.h:35
- [cpp] STARFISH_LINE_BREAK_ITERATOR_POOL_SIZE = 4
 | /home/hwang/starfish/src/Starfish.cpp:81
- [c] BDWGC_FREE_SPACE_DIVISOR = 12
 | /home/hwang/starfish/src/Starfish.h:40
- [c] COMPILER_CLANG = 1
 | /home/hwang/starfish/src/StarfishBase.h:85
- [c] COMPILER_MSVC = 1
 | /home/hwang/starfish/src/StarfishBase.h:87
- [c] COMPILER_GCC = 1
 | /home/hwang/starfish/src/StarfishBase.h:89
- [c] COMPILER_SUPPORTS_CXX_OVERRIDE_CONTROL = 1
 | /home/hwang/starfish/src/StarfishBase.h:100
- [c] COMPILER_QUIRK_FINAL_IS_CALLED_SEALED = 1
 | /home/hwang/starfish/src/StarfishBase.h:101
- [c] ALWAYS_INLINE = inline __attribute__((__always_inline__))
 | /home/hwang/starfish/src/StarfishBase.h:108
- [c] ALWAYS_INLINE = __forceinline
 | /home/hwang/starfish/src/StarfishBase.h:110
- [c] ALWAYS_INLINE = inline
 | /home/hwang/starfish/src/StarfishBase.h:112
- [c] NEVER_INLINE = __attribute__((__noinline__))
 | /home/hwang/starfish/src/StarfishBase.h:119
- [c] NEVER_INLINE = N/A | /home/hwang/starfish/src/StarfishBase.h:121
- [c] NO_RETURN = __attribute((__noreturn__))
 | /home/hwang/starfish/src/StarfishBase.h:146
- [c] NO_RETURN = __declspec(noreturn)
 | /home/hwang/starfish/src/StarfishBase.h:148
- [c] NO_RETURN = N/A | /home/hwang/starfish/src/StarfishBase.h:150
- [c] EXPORT = __declspec(dllexport)
 | /home/hwang/starfish/src/StarfishBase.h:157
- [c] EXPORT = __attribute__((visibility("default")))
 | /home/hwang/starfish/src/StarfishBase.h:159
- [c] FALLTHROUGH = __attribute__((fallthrough))
 | /home/hwang/starfish/src/StarfishBase.h:166
- [c] FALLTHROUGH = /* fall through */
 | /home/hwang/starfish/src/StarfishBase.h:168
- [c] FALLTHROUGH = /* fall through */
 | /home/hwang/starfish/src/StarfishBase.h:171
- [c] FALLTHROUGH = N/A | /home/hwang/starfish/src/StarfishBase.h:173
- [c] NULLABLE = N/A | /home/hwang/starfish/src/StarfishBase.h:176
- [c] ENSURE_ENUM_UNSIGNED = : unsigned int
 | /home/hwang/starfish/src/StarfishBase.h:184
- [c] ENSURE_ENUM_UNSIGNED = N/A | /home/hwang/starfish/src/StarfishBase.h:186
- [c] OS_WINDOWS = 1
 | /home/hwang/starfish/src/StarfishBase.h:190
- [c] OS_WINDOWS = 1
 | /home/hwang/starfish/src/StarfishBase.h:192
- [c] OS_POSIX = 1
 | /home/hwang/starfish/src/StarfishBase.h:196
- [c] OS_POSIX = 1
 | /home/hwang/starfish/src/StarfishBase.h:198
- [c] OS_POSIX = 1
 | /home/hwang/starfish/src/StarfishBase.h:200
- [c] OS_POSIX = 1
 | /home/hwang/starfish/src/StarfishBase.h:205
- [c] OS_POSIX = 1
 | /home/hwang/starfish/src/StarfishBase.h:207
- [c] OS_POSIX = 1
 | /home/hwang/starfish/src/StarfishBase.h:209
- [c] NOMINMAX = N/A | /home/hwang/starfish/src/StarfishBase.h:215
- [c] SSIZE_T | /home/hwang/starfish/src/StarfishBase.h:218
- [c] WIN32_LEAN_AND_MEAN = N/A | /home/hwang/starfish/src/StarfishBase.h:224
- [c] ESCARGOT = // for use additional functions in GCutil
 | /home/hwang/starfish/src/StarfishBase.h:230
- [c] TRUE = 1
 | /home/hwang/starfish/src/StarfishBase.h:256
- [c] FALSE = 0
 | /home/hwang/starfish/src/StarfishBase.h:260
- [c] DEFAULT_CLEAR_STACK_SIZE = 102400
 | /home/hwang/starfish/src/StarfishBase.h:279
- [c] ELABORATE_CLEAR_STACK_SIZE = DEFAULT_CLEAR_STACK_SIZE * 4
 | /home/hwang/starfish/src/StarfishBase.h:280
- [c] STARFISH_32 = N/A | /home/hwang/starfish/src/StarfishBase.h:308
- [c] STARFISH_64 = N/A | /home/hwang/starfish/src/StarfishBase.h:310
- [c] STARFISH_X86_64 = N/A | /home/hwang/starfish/src/StarfishBase.h:317
- [c] STARFISH_X86 = N/A | /home/hwang/starfish/src/StarfishBase.h:323
- [c] STARFISH_ARM = N/A | /home/hwang/starfish/src/StarfishBase.h:327
- [c] STARFISH_ARM_NEON = N/A | /home/hwang/starfish/src/StarfishBase.h:329
- [c] STARFISH_ARM64 = N/A | /home/hwang/starfish/src/StarfishBase.h:333
- [c] STARFISH_ARM_NEON = N/A | /home/hwang/starfish/src/StarfishBase.h:334
- [c] STARFISH_RISCV32 = N/A | /home/hwang/starfish/src/StarfishBase.h:337
- [c] STARFISH_RISCV64 = N/A | /home/hwang/starfish/src/StarfishBase.h:340
- [c] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/StarfishBase.h:358
- [c] STARFISH_ENABLE_PROFILE_LOADING = N/A | /home/hwang/starfish/src/StarfishBase.h:359
- [c] STARFISH_LOG_TAG = "[WORKER] "
 | /home/hwang/starfish/src/StarfishBase.h:363
- [c] STARFISH_LOG_TAG = ""
 | /home/hwang/starfish/src/StarfishBase.h:365
- [c] STARFISH_CRASH = STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE
 | /home/hwang/starfish/src/StarfishBase.h:476
- [c] WARN_UNUSED_RETURN = __attribute__((__warn_unused_result__))
 | /home/hwang/starfish/src/StarfishBase.h:578
- [c] WARN_UNUSED_RETURN = N/A | /home/hwang/starfish/src/StarfishBase.h:582
- [c] STARFISH_PIXEL_R_INDEX = 0
 | /home/hwang/starfish/src/StarfishBase.h:1079
- [c] STARFISH_PIXEL_G_INDEX = 1
 | /home/hwang/starfish/src/StarfishBase.h:1080
- [c] STARFISH_PIXEL_B_INDEX = 2
 | /home/hwang/starfish/src/StarfishBase.h:1081
- [c] STARFISH_PIXEL_A_INDEX = 3
 | /home/hwang/starfish/src/StarfishBase.h:1082
- [c] STARFISH_PIXEL_R_INDEX = 2
 | /home/hwang/starfish/src/StarfishBase.h:1084
- [c] STARFISH_PIXEL_G_INDEX = 1
 | /home/hwang/starfish/src/StarfishBase.h:1085
- [c] STARFISH_PIXEL_B_INDEX = 0
 | /home/hwang/starfish/src/StarfishBase.h:1086
- [c] STARFISH_PIXEL_A_INDEX = 3
 | /home/hwang/starfish/src/StarfishBase.h:1087
- [c] APP_NAME = "Netscape"
 | /home/hwang/starfish/src/StarfishInfo.h:23
- [c] APP_CODE_NAME = "Mozilla"
 | /home/hwang/starfish/src/StarfishInfo.h:24
- [c] PRODUCT_NAME = "Gecko"
 | /home/hwang/starfish/src/StarfishInfo.h:25
- [c] STARFISH_NAME = "Starfish"
 | /home/hwang/starfish/src/StarfishInfo.h:26
- [c] VENDOR_NAME = "Samsung Electronics Co., Ltd."
 | /home/hwang/starfish/src/StarfishInfo.h:27
- [c] VERSION = STARFISH_VERSION_STR
 | /home/hwang/starfish/src/StarfishInfo.h:28
- [c] USER_AGENT_MAXIMUM_DATE_VALUE = 8.64e15
 | /home/hwang/starfish/src/StarfishInfo.h:31
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/starfish/src/StarfishPlatform.h:24
- [c] PORT_EVENTLOOP_BACKEND_GLIB = N/A | /home/hwang/starfish/src/StarfishPlatform.h:25
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/starfish/src/StarfishPlatform.h:26
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:27
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/starfish/src/StarfishPlatform.h:29
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/starfish/src/StarfishPlatform.h:30
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/starfish/src/StarfishPlatform.h:31
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:32
- [c] PORT_GRAPHIC_BACKEND_MOCK = N/A | /home/hwang/starfish/src/StarfishPlatform.h:34
- [c] PORT_CANVAS_BACKEND_MOCK = N/A | /home/hwang/starfish/src/StarfishPlatform.h:35
- [c] PORT_EVENTLOOP_BACKEND_GLIB = N/A | /home/hwang/starfish/src/StarfishPlatform.h:36
- [c] PORT_IMAGEDECODER_BACKEND_MOCK = N/A | /home/hwang/starfish/src/StarfishPlatform.h:37
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:38
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/starfish/src/StarfishPlatform.h:40
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/starfish/src/StarfishPlatform.h:41
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/starfish/src/StarfishPlatform.h:42
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:43
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/starfish/src/StarfishPlatform.h:45
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/starfish/src/StarfishPlatform.h:46
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/starfish/src/StarfishPlatform.h:47
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:48
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/starfish/src/StarfishPlatform.h:50
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/starfish/src/StarfishPlatform.h:51
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/starfish/src/StarfishPlatform.h:52
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:53
- [c] PORT_CANVAS_BACKEND_CAIRO = N/A | /home/hwang/starfish/src/StarfishPlatform.h:55
- [c] PORT_EVENTLOOP_BACKEND_LIBUV = N/A | /home/hwang/starfish/src/StarfishPlatform.h:56
- [c] PORT_IMAGEDECODER_BACKEND_MISC = N/A | /home/hwang/starfish/src/StarfishPlatform.h:57
- [c] PORT_PIXEL_ORDER_BGRA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:58
- [c] PORT_WEBVIEW_BRIDGE_FLUTTER = N/A | /home/hwang/starfish/src/StarfishPlatform.h:59
- [c] PORT_BACKEND_GL_WITH_EXTERNAL_TBM = N/A | /home/hwang/starfish/src/StarfishPlatform.h:60
- [c] PORT_CANVAS_NEEDS_PREMULTIPLIED_ALPHA = N/A | /home/hwang/starfish/src/StarfishPlatform.h:64
- [c] STARFISH_WEBWORKER_NOT_HOST = N/A | /home/hwang/starfish/src/StarfishPlatform.h:68
- [cpp] STARFISH_LOCAL_STORAGE_FILE_NAME = "localStorage.txt"
 | /home/hwang/starfish/src/StoragePathProvider.cpp:27
- [cpp] STARFISH_COOKIES_FILE_NAME = "cookies.txt"
 | /home/hwang/starfish/src/StoragePathProvider.cpp:28
- [cpp] STARFISH_CACHE_DIR_NAME = "cache"
 | /home/hwang/starfish/src/StoragePathProvider.cpp:29
- [cpp] STARFISH_SHARED_WORKER_DIR_NAME = "shared_worker"
 | /home/hwang/starfish/src/StoragePathProvider.cpp:30
- [cpp] STARFISH_SERVICE_WORKER_DIR_NAME = "service_worker"
 | /home/hwang/starfish/src/StoragePathProvider.cpp:31
- [cpp] CAIRO_FORMAT = CAIRO_FORMAT_ARGB32
 | /home/hwang/starfish/src/platform/canvas/CanvasCairo.cpp:68
- [cpp] CAIRO_FORMAT = CAIRO_FORMAT_ARGB32
 | /home/hwang/starfish/src/platform/canvas/CompositorCairo.cpp:38
- [cpp] EVAS_GL_IMAGE_PRESERVED = 0x30D2
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:161
- [cpp] EVAS_GL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:162
- [cpp] EGL_TRUE = 1
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:166
- [cpp] EGL_NONE = 0x3038
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:167
- [cpp] EGL_IMAGE_PRESERVED_KHR = 0x30D2
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:168
- [cpp] EGL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:169
- [cpp] EGL_DMA_BUF_PLANE3_FD_EXT = 0x3440
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:180
- [cpp] EGL_DMA_BUF_PLANE3_OFFSET_EXT = 0x3441
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:183
- [cpp] EGL_DMA_BUF_PLANE3_PITCH_EXT = 0x3442
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:186
- [cpp] EGL_ATTRIBUTE_MAX = 50
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:188
- [cpp] EGL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:190
- [cpp] MIN_MAX_TEXTURE_SIZE = 2048
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:295
- [cpp] RRCLIP_EGL_SAMPLER_PREAMBLE = \
    "#extension GL_OES_EGL_image_external : require\n" \
    "uniform samplerExternalOES uTexture;\n"
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:2053
- [cpp] GAUSSIAN_KERNEL_HALF_WIDTH = 11
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:2250
- [cpp] GAUSSIAN_KERNEL_STEP = 0.2
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:2251
- [cpp] GL_DEBUG_OUTPUT = 0x92E0
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:2662
- [cpp] GL_DEBUG_OUTPUT_SYNCHRONOUS = 0x8242
 | /home/hwang/starfish/src/platform/canvas/CompositorGL.cpp:2665
- [cpp] UBLOCK_SUPPLEMENTAL_SYMBOLS_AND_PICTOGRAPHS = 298
 | /home/hwang/starfish/src/platform/canvas/font/FontImplCairo.cpp:608
- [c] STARFISH_FONT_CAIRO_MIN_ENABLE_KERNING_SIZE = 48
 | /home/hwang/starfish/src/platform/canvas/font/FontImplCairo.h:42
- [c] CHECK_ERROR = \
    if (error) {                                      \
        STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE(); \
    }
 | /home/hwang/starfish/src/platform/canvas/font/FontImplCairo.h:47
- [cpp] HB_UNUSED = N/A | /home/hwang/starfish/src/platform/canvas/font/hb-icu/HarfBuzzICU.cpp:53
- [cpp] ARRAY_LENGTH : unsigned int | /home/hwang/starfish/src/platform/canvas/font/hb-icu/HarfBuzzICU.cpp:57
- [c] HB_ICU_H = N/A | /home/hwang/starfish/src/platform/canvas/font/hb-icu/HarfBuzzICU.h:30
- [c] GL_NONE = 0
 | /home/hwang/starfish/src/platform/canvas/gl/GLTypes.h:55
- [cpp] EGL_NO_CONTEXT = ((EGLContext)0)
 | /home/hwang/starfish/src/platform/canvas/gl/GenericGL.cpp:30
- [cpp] GLAPIENTRY = N/A | /home/hwang/starfish/src/platform/canvas/gl/GenericGL.cpp:48
- [c] GL_GLEXT_PROTOTYPES = N/A | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:27
- [c] EGL_EGLEXT_PROTOTYPES = N/A | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:42
- [c] GL_GLEXT_PROTOTYPES = N/A | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:43
- [c] GL_TEXTURE_EXTERNAL_OES = 0x8D65
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:57
- [c] GL_BGRA_EXT = 0x80E1
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:61
- [c] GL_MAJOR_VERSION = 0x821B
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:65
- [c] GL_MINOR_VERSION = 0x821C
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:69
- [c] GL_UNPACK_ROW_LENGTH = 0x0CF2
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:73
- [c] GL_UNPACK_SKIP_ROWS = 0x0CF3
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:77
- [c] GL_UNPACK_SKIP_PIXELS = 0x0CF4
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:81
- [c] GL_DEPTH_STENCIL = 0x84F9
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:85
- [c] GL_UNSIGNED_INT_24_8 = 0x84FA
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:89
- [c] GL_TEXTURE_SWIZZLE_R = 0x8E42
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:93
- [c] GL_TEXTURE_SWIZZLE_G = 0x8E43
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:96
- [c] GL_TEXTURE_SWIZZLE_B = 0x8E44
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:99
- [c] GL_TEXTURE_SWIZZLE_A = 0x8E45
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:102
- [c] TEXTURE_SWIZZLE_RGBA = 0x8E46
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:105
- [c] GL_RED = 0x1903
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:109
- [c] GL_GREEN = 0x1904
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:112
- [c] GL_BLUE = 0x1905
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:115
- [c] GL_ALPHA = 0x1906
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:118
- [c] GL_R8 = 0x8229
 | /home/hwang/starfish/src/platform/canvas/gl/IncludeGL.h:121
- [cpp] DIR | /home/hwang/starfish/src/platform/file/PlatformDirectory.cpp:44
- [cpp] DIR | /home/hwang/starfish/src/platform/file/PlatformDirectory.cpp:57
- [cpp] STARFISH_RESOURCE_CACHE_SIZE = 1024 * 1024 * 4
 | /home/hwang/starfish/src/platform/loader/ResourceLoader.cpp:45
- [cpp] MAX_PORT_DIGITS = 5
 | /home/hwang/starfish/src/platform/loader/ResourceURL.cpp:25
- [cpp] MAX_PORT_NUMBER = 65535
 | /home/hwang/starfish/src/platform/loader/ResourceURL.cpp:26
- [c] STARFISH_ASSERT : ResourceURL(const char* url , size_t len)
        : ResourceURL(String::fromUTF8(url, len))
    { | /home/hwang/starfish/src/platform/loader/ResourceURL.h:53
- [cpp] MINUMUM_ANIMATOR_WAIT_TIME = 3000 // us
 | /home/hwang/starfish/src/platform/message_loop/TimerLibUV.cpp:137
- [c] STARFISH_VIDEO_WIDTH_WHEN_VIDEO_NOT_EXISTS = 300
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayer.h:24
- [c] STARFISH_VIDEO_HEIGHT_WHEN_VIDEO_NOT_EXISTS = 150
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayer.h:25
- [cpp] STARFISH_ESPP_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:57
- [cpp] STARFISH_ESPP_MAX_AV_DIFF_IN_MS = 1500
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:60
- [cpp] STARFISH_ESPP_FEED_WAIT_US = (1000 * 25)
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:62
- [cpp] STARFISH_ESPP_TOTAL_BUFFER_SIZE = (64 * 1024 * 1024)
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:65
- [cpp] STARFISH_ESPP_AUDIO_BUFFER_SIZE = (768 * 1024)
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:66
- [cpp] STARFISH_ESPP_MIN_BYTE_THRESHOLD = 10
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:77
- [cpp] STARFISH_ESPP_SEEK_IDR_MAX_LOOKBACK_MS = 20000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:85
- [cpp] STARFISH_ESPP_SEEK_IDR_MAX_LOOKAHEAD_MS = 20000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:97
- [cpp] STARFISH_ESPP_MAX_SKIP_AHEAD_MS = 30000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:105
- [cpp] STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_PREROLL_MS = 50
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:112
- [cpp] STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_STEADY_MS = 500
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:113
- [cpp] STARFISH_ESPP_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:116
- [cpp] STARFISH_ESPP_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.cpp:117
- [c] STARFISH_ESPP_SEEK_WATCHDOG_MS = 12000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerESPlusPlayer.h:51
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:134
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:135
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:136
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:137
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:138
- [cpp] STARFISH_MSE_MIN_MARGIN_IN_MS = 3000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:139
- [cpp] SEEK_LAND_TOLERANCE_MS = 5000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:144
- [cpp] STARFISH_DECODE_LOOKAHEAD_MS_DEFAULT = 400
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:152
- [cpp] STARFISH_RUN_MSE_THREAD_WAIT_TIME = 1000 * 25 // 25ms
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.cpp:1799
- [c] MAX_WAITING_SECONDS_FOR_SEEK_OPERATION = 30000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.h:26
- [c] STARFISH_RUN_MSE_THREAD = N/A | /home/hwang/starfish/src/platform/multimedia/MediaPlayerLinux.h:29
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTV.cpp:45
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTV.cpp:46
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTV.cpp:47
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTV.cpp:48
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTV.cpp:49
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:50
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:51
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:52
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:53
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:54
- [cpp] STARFISH_MSE_MIN_MARGIN_IN_MS = 3000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:55
- [cpp] STARFISH_RUN_MSE_THREAD_WAIT_TIME = 1000 * 25 // 25ms
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.cpp:1228
- [c] EFL_BETA_API_SUPPORT = N/A | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.h:36
- [c] MAX_WAITING_SECONDS_FOR_SEEK_OPERATION = 30000
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.h:48
- [c] STARFISH_RUN_MSE_THREAD = N/A | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizen.h:51
- [cpp] STARFISH_VIDEO_MAX_WIDTH = 1920
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizenBase.cpp:47
- [cpp] STARFISH_VIDEO_MAX_HEIGHT = 1080
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizenBase.cpp:48
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM = 2997
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizenBase.cpp:49
- [cpp] STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN = 100
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizenBase.cpp:50
- [cpp] STARFISH_MSE_SUBMIT_BYTES_RATE = 0.3
 | /home/hwang/starfish/src/platform/multimedia/MediaPlayerTizenBase.cpp:51
- [cpp] STARFISH_FRAME_EVICTION_BACKWARD_DUR = 500
 | /home/hwang/starfish/src/platform/multimedia/MockMediaPlayer.cpp:43
- [cpp] CURLHANDLE_CACHE_PRUNE_MINIMUM_SIZE = 12
 | /home/hwang/starfish/src/platform/network/curl/NetworkSharedResourceManager.cpp:42
- [cpp] CURLHANDLE_CACHE_PRUNE_MINIMUM_INTERVAL_S = 0.5
 | /home/hwang/starfish/src/platform/network/curl/NetworkSharedResourceManager.cpp:43
- [cpp] CURLHANDLE_CACHE_IDLE_TIME_LIMIT_S = 60
 | /home/hwang/starfish/src/platform/network/curl/NetworkSharedResourceManager.cpp:50
- [cpp] CURLPIPE_MULTIPLEX = 0
 | /home/hwang/starfish/src/platform/network/curl/NetworkSharedResourceManager.cpp:795
- [cpp] INDEX_FILE_NAME = "/index.txt"
 | /home/hwang/starfish/src/platform/network/http/HTTPCache.cpp:43
- [cpp] DEFAULT_HTTP_CACHE_SIZE = 1024 * 1024 * 50
 | /home/hwang/starfish/src/platform/network/http/HTTPCache.cpp:44
- [cpp] MAX_ENTRY_FILE_SIZE = (DEFAULT_HTTP_CACHE_SIZE * 0.04)
 | /home/hwang/starfish/src/platform/network/http/HTTPCache.cpp:45
- [cpp] NUM_OF_COL = 18
 | /home/hwang/starfish/src/platform/network/http/HTTPCache.cpp:46
- [cpp] CURLPIPE_MULTIPLEX = 0
 | /home/hwang/starfish/src/platform/network/http/HTTPTransaction.cpp:161
- [cpp] TTS_MODE_INTERRUPT = 3
 | /home/hwang/starfish/src/platform/tts/TTSTV.cpp:43
- [cpp] TTS_REMOVED_INSTANCE_SIZE = 5
 | /home/hwang/starfish/src/platform/tts/TTSTV.cpp:44
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS = "db/setting/accessibility/tts"
 | /home/hwang/starfish/src/platform/tts/TTSTizen.cpp:63
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY = \
    "db/setting/accessibility/tts/temporary"
 | /home/hwang/starfish/src/platform/tts/TTSTizen.cpp:68
- [cpp] TTS_REMOVED_INSTANCE_SIZE = 5
 | /home/hwang/starfish/src/platform/tts/TTSTizen.cpp:71
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp:22
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp:22
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS = "db/setting/accessibility/tts"
 | /home/hwang/starfish/src/public/bridge/efl/A11yAtspiBridge.cpp:54
- [cpp] VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY = \
    "db/setting/accessibility/tts/temporary"
 | /home/hwang/starfish/src/public/bridge/efl/A11yAtspiBridge.cpp:59
- [cpp] STARFISH_ATK_PLUG_TYPE = (starfish_atk_plug_get_type())
 | /home/hwang/starfish/src/public/bridge/efl/A11yAtspiBridge.cpp:188
- [cpp] STARFISH_ATK_NODE_TYPE = (starfish_atk_node_get_type())
 | /home/hwang/starfish/src/public/bridge/efl/A11yAtspiBridge.cpp:407
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:32
- [cpp] EVAS_GL_NO_GL_H_CHECK = N/A | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:53
- [cpp] EGL_NATIVE_SURFACE_TIZEN = 0x32A1
 | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:64
- [cpp] EGL_IMAGE_PRESERVED_KHR = 0x30D2
 | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:67
- [cpp] EFL_BETA_API_SUPPORT = N/A | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:75
- [cpp] ANNOTATE_SETUP = N/A | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:103
- [cpp] ANNOTATE_GREEN = 0x00ff001b
 | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:106
- [cpp] EINA_LIST_FREE | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:645
- [cpp] EVAS_GL_OPTIONS_DIRECT_MEMORY_OPTIMIZE = (1 << 12)
 | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:981
- [cpp] EVAS_GL_OPTIONS_DIRECT_OVERRIDE = (1 << 13)
 | /home/hwang/starfish/src/public/bridge/efl/LWEWebViewEFL.cpp:982
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/public/bridge/flutter/LWEWebViewFlutter.cpp:40
- [cpp] EFL_BETA_API_SUPPORT = N/A | /home/hwang/starfish/src/public/bridge/flutter/LWEWebViewFlutter.cpp:42
- [cpp] ANNOTATE_SETUP = N/A | /home/hwang/starfish/src/public/bridge/flutter/LWEWebViewFlutter.cpp:56
- [cpp] ANNOTATE_GREEN = 0x00ff001b
 | /home/hwang/starfish/src/public/bridge/flutter/LWEWebViewFlutter.cpp:59
- [cpp] PORT_WINDOW_BACKEND | /home/hwang/starfish/src/public/bridge/flutter/LWEWebViewFlutter.cpp:82
- [cpp] PORT_COMPOSITOR_BACKEND | /home/hwang/starfish/src/public/bridge/flutter/LWEWebViewFlutter.cpp:83
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp:22
- [cpp] STARFISH_ENABLE_PROFILE_TIMER = N/A | /home/hwang/starfish/src/public/bridge/x11/LWEWebViewX11.cpp:22
- [cpp] GC_CPP_H = N/A | /home/hwang/starfish/src/public/bridge/x11/LWEWebViewX11.cpp:25
- [c] EXPORT_UNMANAGED_API = __declspec(dllexport)
 | /home/hwang/starfish/src/public/contract/LWEDelegateConfig.h:24
- [c] EXPORT_UNMANAGED_API = __attribute__((visibility("default")))
 | /home/hwang/starfish/src/public/contract/LWEDelegateConfig.h:26
- [cpp] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/starfish/src/public/delegate/LWEWebContainerDelegate.cpp:59
- [cpp] LWE_MIN_FONT_SIZE = 1
 | /home/hwang/starfish/src/public/delegate/LWEWebContainerDelegate.cpp:60
- [cpp] LWE_MAX_FONT_SIZE = 72
 | /home/hwang/starfish/src/public/delegate/LWEWebContainerDelegate.cpp:61
- [cpp] LWE_DEFAULT_FONT_SIZE = 16
 | /home/hwang/starfish/src/public/delegate/SettingsDelegate.cpp:29
- [cpp] THREAD_MINIMUM_STACK_SIZE = \
    4 * 1024 * 1024 // we need at least 4MB for stack
 | /home/hwang/starfish/src/public/delegate/ThreadedCallHelper.cpp:27
- [c] LWE | /home/hwang/starfish/src/shell/MiniBrowser.h:42
- [c] LWE | /home/hwang/starfish/src/shell/MiniBrowser.h:46
- [c] SHELL_ENABLE_ELEMENTARY_GL = N/A | /home/hwang/starfish/src/shell/ShellConfig.h:25
- [c] SHELL_X86_64 = N/A | /home/hwang/starfish/src/shell/ShellConfig.h:30
- [c] SHELL_ENABLE_BACKTRACE = N/A | /home/hwang/starfish/src/shell/ShellConfig.h:35
- [c] SHELL_ENABLE_TEST = N/A | /home/hwang/starfish/src/shell/ShellConfig.h:39
- [c] SHELL_TIZEN = N/A | /home/hwang/starfish/src/shell/ShellConfig.h:43
- [c] SHELL_ENABLE_TRANSPARENT_WINDOW = N/A | /home/hwang/starfish/src/shell/ShellConfig.h:47
- [c] HINT_VISIBLE = 0x0001
 | /home/hwang/starfish/src/shell/Window.h:34
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:200
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:206
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:215
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:227
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:241
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:255
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:269
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:292
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:333
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:341
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:401
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:407
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:413
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:422
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:430
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:440
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:454
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:463
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:473
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:483
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:492
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:504
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:515
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:524
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:533
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:542
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:556
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:565
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/APIRecorderTest.cpp:573
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:43
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:50
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:57
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:70
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:76
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:106
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:111
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/CookieManagerTest.cpp:116
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:38
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:56
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:79
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:84
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:89
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:97
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:108
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:122
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:127
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:133
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/LWETest.cpp:139
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:46
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:52
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:64
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:76
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:89
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:99
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:109
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:119
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:130
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:141
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:153
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:165
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:175
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:185
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:195
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:205
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:215
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:225
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:233
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/SettingsTest.cpp:265
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:135
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:176
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:228
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:244
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:260
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:277
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:295
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:310
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:325
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:342
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:353
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebContainerTest.cpp:369
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebViewTest.cpp:63
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebViewTest.cpp:101
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebViewTest.cpp:145
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebViewTest.cpp:158
- [cpp] TEST_F | /home/hwang/starfish/src/shell/test/WebViewTest.cpp:171
- [cpp] UINT_PTR = N/A | /home/hwang/starfish/src/shell/windows/StarfishShell.cpp:245
- [cpp] UINT_PTR = N/A | /home/hwang/starfish/src/shell/windows/StarfishShell.cpp:247
- [cpp] UINT = N/A | /home/hwang/starfish/src/shell/windows/StarfishShell.cpp:248
- [cpp] UINT = N/A | /home/hwang/starfish/src/shell/windows/StarfishShell.cpp:253
- [c] STREAMLINE_ANNOTATE_H = N/A | /home/hwang/starfish/src/streamline_annotate.h:34
- [c] ANNOTATE_RED = 0x0000ff1b
 | /home/hwang/starfish/src/streamline_annotate.h:73
- [c] ANNOTATE_BLUE = 0xff00001b
 | /home/hwang/starfish/src/streamline_annotate.h:74
- [c] ANNOTATE_GREEN = 0x00ff001b
 | /home/hwang/starfish/src/streamline_annotate.h:75
- [c] ANNOTATE_PURPLE = 0xff00ff1b
 | /home/hwang/starfish/src/streamline_annotate.h:76
- [c] ANNOTATE_YELLOW = 0x00ffff1b
 | /home/hwang/starfish/src/streamline_annotate.h:77
- [c] ANNOTATE_CYAN = 0xffff001b
 | /home/hwang/starfish/src/streamline_annotate.h:78
- [c] ANNOTATE_WHITE = 0xffffff1b
 | /home/hwang/starfish/src/streamline_annotate.h:79
- [c] ANNOTATE_LTGRAY = 0xbbbbbb1b
 | /home/hwang/starfish/src/streamline_annotate.h:80
- [c] ANNOTATE_DKGRAY = 0x5555551b
 | /home/hwang/starfish/src/streamline_annotate.h:81
- [c] ANNOTATE_BLACK = 0x0000001b
 | /home/hwang/starfish/src/streamline_annotate.h:82
- [c] ANNOTATE_MUTEX_DEFINE = \
    pthread_mutex_t gator_mutex = PTHREAD_MUTEX_INITIALIZER;
 | /home/hwang/starfish/src/streamline_annotate.h:200
- [c] ANNOTATE_LOCK = pthread_mutex_lock(&gator_mutex)
 | /home/hwang/starfish/src/streamline_annotate.h:202
- [c] ANNOTATE_UNLOCK = pthread_mutex_unlock(&gator_mutex)
 | /home/hwang/starfish/src/streamline_annotate.h:203
- [c] ANNOTATE_MUTEX_DEFINE = N/A | /home/hwang/starfish/src/streamline_annotate.h:206
- [c] ANNOTATE_LOCK = ((void)0)
 | /home/hwang/starfish/src/streamline_annotate.h:207
- [c] ANNOTATE_UNLOCK = ((void)0)
 | /home/hwang/starfish/src/streamline_annotate.h:208
- [c] ANNOTATE_DEFINE = \
    ANNOTATE_MUTEX_DEFINE \
    FILE *gator_annotate = 0
 | /home/hwang/starfish/src/streamline_annotate.h:213
- [c] ANNOTATE_SETUP = \
    do {                                                         \
        if (!gator_annotate) {                                   \
            gator_annotate = fopen("/dev/gator/annotate", "wb"); \
        }                                                        \
    } while (0)
 | /home/hwang/starfish/src/streamline_annotate.h:217
- [c] TSL_ROBIN_GROWTH_POLICY_H = N/A | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_growth_policy.h:25
- [c] TSL_RH_NO_EXCEPTIONS = N/A | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_growth_policy.h:51
- [c] TSL_RH_NB_PRIMES = 51
 | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_growth_policy.h:241
- [c] TSL_RH_NB_PRIMES = 40
 | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_growth_policy.h:243
- [c] TSL_RH_NB_PRIMES = 23
 | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_growth_policy.h:245
- [c] TSL_ROBIN_HASH_H = N/A | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_hash.h:25
- [c] USE_STORED_HASH_ON_REHASH : bool | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_hash.h:432
- [c] TSL_ROBIN_MAP_H = N/A | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_map.h:25
- [c] TSL_ROBIN_SET_H = N/A | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_set.h:25
- [c] TSL_ROBIN_VECTOR_H = N/A | /home/hwang/starfish/third_party/robin_map/include/tsl/robin_vector.h:26
- [python] TOLERANCE = 8 | /home/hwang/starfish/tool/ci/check_render_bmp.py:30
- [python] PAINT_COLOR = N/A | /home/hwang/starfish/tool/ci/check_render_bmp.py:32
- [python] IMAGE_COLOR = N/A | /home/hwang/starfish/tool/ci/check_render_bmp.py:33
- [python] MIN_PAINT_FRACTION = 0.002 | /home/hwang/starfish/tool/ci/check_render_bmp.py:38
- [python] MIN_IMAGE_FRACTION = 0.0002 | /home/hwang/starfish/tool/ci/check_render_bmp.py:39
- [python] MIN_INK_FRACTION = 0.0001 | /home/hwang/starfish/tool/ci/check_render_bmp.py:40
- [python] ENVOPTS | /home/hwang/starfish/tool/drivers/basics/constants.py:6
- [python] TEST_RESULT_FILE = "TC_TEST_RESULT_FILE" | /home/hwang/starfish/tool/drivers/basics/constants.py:7
- [python] FORCE_ENABLE = "TC_FORCE_ENABLE" | /home/hwang/starfish/tool/drivers/basics/constants.py:8
- [python] TIMEOUT = "TC_TIMEOUT" | /home/hwang/starfish/tool/drivers/basics/constants.py:9
- [python] REPLACE_STR = "TC_REPLACE_STR" | /home/hwang/starfish/tool/drivers/basics/constants.py:10
- [python] ERRORCODE | /home/hwang/starfish/tool/drivers/basics/constants.py:12
- [python] TEST_PASSED = 0 | /home/hwang/starfish/tool/drivers/basics/constants.py:13
- [python] TEST_FAILED = 1 | /home/hwang/starfish/tool/drivers/basics/constants.py:14
- [python] TEST_STOPPED = 2 | /home/hwang/starfish/tool/drivers/basics/constants.py:15
- [python] FNULL = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:17
- [python] WIDTH_OPT_PREFIX = "--width=" | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:19
- [python] HEIGHT_OPT_PREFIX = "--height=" | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:20
- [python] REGRESSION_OPT = "--regression-test" | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:21
- [python] NON_REGRESSION_OPT = "" | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:22
- [python] DEFAULT_WIDTH_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:23
- [python] DEFAULT_HEIGHT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:24
- [python] DEFAULT_REGRESSION_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:25
- [python] TEST_RESULT_PASS_FILE = None | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:26
- [python] TIMEOUT_OPT_PREFIX = "--timeout=" | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:27
- [python] DEFAULT_NATIVE_TIMEOUT_SEC = 180 | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:38
- [python] RE_PASS = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:40
- [python] RE_FAIL = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:41
- [python] DEFAULT_WIDTH_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:45
- [python] DEFAULT_HEIGHT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:46
- [python] DEFAULT_REGRESSION_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:47
- [python] TEST_RESULT_PASS_FILE = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:174
- [python] TEST_RESULT_FAIL_FILE = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_basic_test.py:175
- [python] FNULL = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:14
- [python] ERRSTR = " diff: 100.0% failed" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:17
- [python] WIDTH_OPT_PREFIX = "--width=" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:18
- [python] HEIGHT_OPT_PREFIX = "--height=" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:19
- [python] SCREENSHOT_OPT_PREFIX = "--screen-shot=" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:20
- [python] AHEM_OPT = "--pixel-test" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:21
- [python] NON_AHEM_OPT = "--regression-test" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:22
- [python] HIDE_WINDOW_OPT = "--hide-window" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:23
- [python] DEFAULT_WIDTH_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:24
- [python] DEFAULT_HEIGHT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:25
- [python] DEFAULT_FONT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:26
- [python] DEFAULT_BACKEND = "efl" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:27
- [python] REMOTE_EXP_DIR = "remote-test" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:28
- [python] OUT_DIR = "out" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:29
- [python] DEFAULT_WIDTH_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:34
- [python] DEFAULT_HEIGHT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:35
- [python] DEFAULT_FONT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:36
- [python] DEFAULT_BACKEND = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_test.py:39
- [python] FNULL = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:13
- [python] ERRSTR = " diff: 100.0% failed" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:16
- [python] WIDTH_OPT_PREFIX = "--width=" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:17
- [python] HEIGHT_OPT_PREFIX = "--height=" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:18
- [python] SCREENSHOT_OPT_PREFIX = "--screen-shot=" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:19
- [python] AHEM_OPT = "--pixel-test" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:20
- [python] NON_AHEM_OPT = "--regression-test" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:21
- [python] HIDE_WINDOW_OPT = "--hide-window" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:22
- [python] DEFAULT_WIDTH_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:23
- [python] DEFAULT_HEIGHT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:24
- [python] DEFAULT_FONT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:25
- [python] DEFAULT_BACKEND = "efl" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:26
- [python] REMOTE_EXP_DIR = "remote-test" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:27
- [python] OUT_DIR = "out" | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:28
- [python] DEFAULT_WIDTH_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:32
- [python] DEFAULT_HEIGHT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:33
- [python] DEFAULT_FONT_OPT = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:34
- [python] DEFAULT_BACKEND = N/A | /home/hwang/starfish/tool/drivers/basics/starfish_pixel_with_remote_test.py:37
- [python] ENDC = '\033[0m' | /home/hwang/starfish/tool/drivers/basics/utils.py:5
- [python] BLUE = '\033[94m' | /home/hwang/starfish/tool/drivers/basics/utils.py:6
- [python] GREEN = '\033[32m' | /home/hwang/starfish/tool/drivers/basics/utils.py:7
- [python] YELLOW = '\033[93m' | /home/hwang/starfish/tool/drivers/basics/utils.py:8
- [python] RED = '\033[91m' | /home/hwang/starfish/tool/drivers/basics/utils.py:9
- [python] PASS_SIGN = N/A | /home/hwang/starfish/tool/drivers/basics/utils.py:40
- [python] FAIL_SIGN = N/A | /home/hwang/starfish/tool/drivers/basics/utils.py:41
- [python] CHECK_SIGN = N/A | /home/hwang/starfish/tool/drivers/basics/utils.py:42
- [python] RE_KEYWORDS = N/A | /home/hwang/starfish/tool/drivers/tests/dom_conformance_test.py:9
- [python] RE_KEYWORDS = N/A | /home/hwang/starfish/tool/drivers/tests/vendor_test.py:9
- [python] FNULL = N/A | /home/hwang/starfish/tool/drivers/tests/wpt_test.py:17
- [python] RE_KEYWORDS = N/A | /home/hwang/starfish/tool/drivers/tests/wpt_test.py:19
- [python] RE_RTERROR = N/A | /home/hwang/starfish/tool/drivers/tests/wpt_test.py:20
- [python] RE_RTPASS = N/A | /home/hwang/starfish/tool/drivers/tests/wpt_test.py:21
- [python] RE_RTCAPTURED = N/A | /home/hwang/starfish/tool/drivers/tests/wpt_test.py:22
- [python] TIMEOUT_SEC = 5 | /home/hwang/starfish/tool/drivers/tests/wpt_test.py:23
- [cpp] PNG_DEBUG = 3
 | /home/hwang/starfish/tool/imgdiff/imgdiff.cpp:33
- [python] CONTRACT_DIR = "src/public/contract" | /home/hwang/starfish/tool/lint/check_contract_abi.py:104
- [python] EXTRA_HEADERS = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:107
- [python] SHIM_REL_PATH = "tool/lint/contract_abi/contract_shim.cpp" | /home/hwang/starfish/tool/lint/check_contract_abi.py:108
- [python] WAIVER_REL_PATH = "tool/lint/contract_abi/breaking_changes.md" | /home/hwang/starfish/tool/lint/check_contract_abi.py:109
- [python] ABI_EPOCH_REL_PATH = "src/public/contract/LWEDelegateContract.h" | /home/hwang/starfish/tool/lint/check_contract_abi.py:110
- [python] LOADER_REL_PATHS = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:111
- [python] WITNESS_STRUCT = "ContractAbiWitness" | /home/hwang/starfish/tool/lint/check_contract_abi.py:115
- [python] ABIDW_FLAGS = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:117
- [python] COMPILE_FLAGS = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:128
- [python] CLASS_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:133
- [python] NAMED_STRUCT_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:134
- [python] PROCTABLE_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:135
- [python] ENUM_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:136
- [python] VIRTUAL_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:137
- [python] WRAPPER_NAME_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:138
- [python] DLSYM_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:139
- [python] WRAPPER_CHECK_MACRO_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:140
- [python] ABI_EPOCH_RE = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:141
- [python] FIXTURES = N/A | /home/hwang/starfish/tool/lint/check_contract_abi.py:1043
- [python] TERM_RED = '\033[1;31m' | /home/hwang/starfish/tool/lint/check_tidy.py:26
- [python] TERM_GREEN = '\033[1;32m' | /home/hwang/starfish/tool/lint/check_tidy.py:27
- [python] TERM_YELLOW = '\033[1;33m' | /home/hwang/starfish/tool/lint/check_tidy.py:28
- [python] TERM_PURPLE = '\033[35m' | /home/hwang/starfish/tool/lint/check_tidy.py:29
- [python] TERM_EMPTY = '\033[0m' | /home/hwang/starfish/tool/lint/check_tidy.py:30
- [python] BASE = N/A | /home/hwang/starfish/tool/perf_tools/measure-bench/server.py:4
- [python] BASE = N/A | /home/hwang/starfish/tool/perf_tools/style-smoke/server.py:4
- [python] REPO_ROOT = N/A | /home/hwang/starfish/tool/repo_paths.py:29
- [python] REPO_ROOT = N/A | /home/hwang/starfish/tool/runner/execution_worker.py:27
- [python] PADDING = 30 | /home/hwang/starfish/tool/runner/test_runner.py:52
- [python] ROOT = "test/cairo/internal-test/served-resources" | /home/hwang/starfish/tool/runner/test_runner.py:85
- [python] KHRONOS_WEBGL_JOBS = 4 | /home/hwang/starfish/tool/runner/test_runner.py:138
- [python] KHRONOS_WEBGL_TIMEOUT_SEC = 480 | /home/hwang/starfish/tool/runner/test_runner.py:148
- [python] ROOT = N/A | /home/hwang/starfish/tool/runner/test_runner.py:153
- [python] DIR = N/A | /home/hwang/starfish/tool/runner/test_runner.py:154
- [python] ADDRESS = "localhost" | /home/hwang/starfish/tool/runner/test_runner.py:155
- [python] PORT = 11010 | /home/hwang/starfish/tool/runner/test_runner.py:156
- [python] UPDATE_DIR = N/A | /home/hwang/starfish/tool/runner/uwe_loader_test.py:53
- [python] DEFAULT_VERSION_PATH = N/A | /home/hwang/starfish/tool/runner/uwe_loader_test.py:54
- [python] SCENARIOS = N/A | /home/hwang/starfish/tool/runner/uwe_loader_test.py:168
- [python] UPDATE_DIR = N/A | /home/hwang/starfish/tool/runner/uwe_worker_loader_test.py:42
- [python] DEFAULT_VERSION_PATH = N/A | /home/hwang/starfish/tool/runner/uwe_worker_loader_test.py:43
- [python] WORKERS = N/A | /home/hwang/starfish/tool/runner/uwe_worker_loader_test.py:45
- [python] SCENARIOS = N/A | /home/hwang/starfish/tool/runner/uwe_worker_loader_test.py:137
- [python] MARK_FMT = "# [auto-fail:%s] " | /home/hwang/starfish/tool/wpt/scripts/wpt_annotate.py:41
- [python] DEFAULT_RES_DIR = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_audit.py:47
- [python] STARFISH = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_reftest.py:66
- [python] IMGDIFF = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_reftest.py:67
- [python] SERVER = "http://web-platform.test:8000" | /home/hwang/starfish/tool/wpt/scripts/wpt_reftest.py:84
- [python] STARFISH_CMD_PREFIX = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_reftest.py:90
- [python] STARFISH = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:59
- [python] TMP_DIR = "/tmp" | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:60
- [python] STARFISH_CMD_PREFIX = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:70
- [python] RE_PASS = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:127
- [python] RE_FAIL = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:128
- [python] RE_DONE = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:129
- [python] RE_CRASHOK = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:130
- [python] CRASHTEST_QUERY = "__starfish_crashtest=1" | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:137
- [python] RE_CONNECT_REFUSED = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:205
- [python] CONNECT_REFUSED_RETRIES = 5 | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:212
- [python] CRASH_REASONS = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_runner.py:351
- [python] HOST = "web-platform.test" | /home/hwang/starfish/tool/wpt/scripts/wpt_server.py:42
- [python] HTTP_PORT = 8000 | /home/hwang/starfish/tool/wpt/scripts/wpt_server.py:43
- [python] REQUIRED_PORTS = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_server.py:45
- [python] DEFAULT_INJECT = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_server.py:51
- [python] DEFAULT_WPT_ROOT = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_server.py:53
- [python] TEST_TYPES = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_status.py:72
- [python] DEFAULT_TARGETS = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_status.py:74
- [python] SERVER = "http://web-platform.test:8000" | /home/hwang/starfish/tool/wpt/scripts/wpt_status.py:75
- [python] HARNESS_STATUS = N/A | /home/hwang/starfish/tool/wpt/scripts/wpt_status.py:79
- [python] HTML_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Starfish WPT status</title>
<style>
 body{font:14px/1.5 system-ui,sans-serif;margin:0;padding:1.5rem;color:#1a1a1a}
 h1{font-size:1.4rem;margin:0 0 .25rem}
 .meta{color:#666;margin-bottom:1rem}
 .bar{height:14px;border-radius:7px;background:#e33;overflow:hidden;margin:.5rem 0}
 .bar>span{display:block;height:100%;background:#2a2}
 details{border:1px solid #ddd;border-radius:6px;margin:.4rem 0}
 details details{margin:.4rem .4rem .4rem 1rem;border-left:3px solid #eee}
 summary{cursor:pointer;padding:.5rem .75rem;font-weight:600;
         display:flex;justify-content:space-between;gap:1rem}
 summary .n{font-weight:400;color:#666}
 table{width:100%;border-collapse:collapse;font-size:13px}
 td{padding:.3rem .75rem;border-top:1px solid #eee;vertical-align:top}
 td.s{width:3.2rem;font-weight:700}
 tr.pass td.s{color:#2a2} tr.fail td.s{color:#e33}
 .u{font-family:ui-monospace,monospace;word-break:break-all}
 .sub{color:#888;white-space:nowrap}
 .toggle{margin-bottom:1rem}
 body.failonly tr.pass{display:none}
 body.failonly details.allpass{display:none}
</style>
<script>
 function failOnly(cb){document.body.classList.toggle('failonly',cb.checked)}
 // Reorder directory <details> and test <tr> siblings at every tree level by
 // the chosen key/direction. Preserves the tree (dirs first, table last) and
 // each <details> open state, since we only re-append existing nodes.
 function sortAll(){
   var key=document.getElementById('sortKey').value;
   var sign=document.getElementById('sortDir').value==='asc'?1:-1;
   function val(el){return key==='name'?(el.getAttribute('data-name')||''):
     parseFloat(el.getAttribute('data-rate'))||0}
   function cmp(a,b){var x=val(a),y=val(b);
     if(key==='name')return sign*String(x).localeCompare(String(y));
     return sign*(x-y)}
   function sortIn(container){
     var kids=Array.prototype.slice.call(container.children);
     var dets=kids.filter(function(e){return e.tagName==='DETAILS'&&
       e.classList.contains('dir')});
     var tables=kids.filter(function(e){return e.tagName==='TABLE'});
     dets.sort(cmp);
     dets.forEach(function(d){container.appendChild(d)});
     tables.forEach(function(tb){
       container.appendChild(tb);
       // Browsers wrap bare <tr> in an implicit <tbody>, so match both and
       // re-append to each row's actual parent.
       var rows=Array.prototype.slice.call(
         tb.querySelectorAll(':scope>tr, :scope>tbody>tr'));
       rows.sort(cmp);
       rows.forEach(function(r){r.parentNode.appendChild(r)})});
     dets.forEach(sortIn);
   }
   sortIn(document.body);
 }
</script>
</head><body>
""" | /home/hwang/starfish/tool/wpt/scripts/wpt_status.py:290

<!-- Total: 7004 nodes, 560 relevant -->
