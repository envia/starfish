
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
# Languages: c (118), cpp (150), java (11), javascript (8), python (43)

## Enum Definitions
- [c] class | ? | /home/hwang/work/F/starfish_/compat/tizen_5.0/inc/LWEWebView.h:50
- [c] class | ? | /home/hwang/work/F/starfish_/compat/tizen_5.0/inc/LWEWebView.h:184
- [javascript] generateFlagTag | ? | /home/hwang/work/F/starfish_/docs/webpages/webapi/webapi_main.js:53
- [c] class | ? | /home/hwang/work/F/starfish_/inc/LWEWebView.h:58
- [c] class | ? | /home/hwang/work/F/starfish_/inc/LWEWebView.h:194
- [c] class | ? | /home/hwang/work/F/starfish_/inc/LWEWorker.h:44
- [c] KeyValue | UnidentifiedKey=auto, AltLeftKey=auto, AltRightKey=auto, ControlLeftKey=auto, ControlRightKey=auto, CapsLockKey=auto, FnKey=auto, FnLockKey=auto, HyperKey=auto, MetaKey=auto, NumLockKey=auto, ScrollLockKey=auto, ShiftLeftKey=auto, ShiftRightKey=auto, SuperKey=auto, SymbolKey=auto, SymbolLockKey=auto, EnterKey=auto, TabKey=auto, ArrowDownKey=auto | /home/hwang/work/F/starfish_/inc/PlatformIntegrationData.h:7
- [c] MouseButtonValue | NoButton=0, LeftButton=0, MiddleButton=1, RightButton=2 | /home/hwang/work/F/starfish_/inc/PlatformIntegrationData.h:239
- [c] MouseButtonsValue | NoButtonDown=0, LeftButtonDown=1, RightButtonDown=auto, MiddleButtonDown=auto | /home/hwang/work/F/starfish_/inc/PlatformIntegrationData.h:246
- [c] TTSMode | Default=0, Forced=1 | /home/hwang/work/F/starfish_/inc/PlatformIntegrationData.h:253
- [c] class | ? | /home/hwang/work/F/starfish_/inc/PlatformIntegrationData.h:258
- [c] class | ? | /home/hwang/work/F/starfish_/inc/PlatformIntegrationData.h:260
- [c] class | ? | /home/hwang/work/F/starfish_/src/Starfish.h:43
- [c] ENSURE_ENUM_UNSIGNED | ? | /home/hwang/work/F/starfish_/src/StarfishBase.h:184
- [c] ENSURE_ENUM_UNSIGNED | ? | /home/hwang/work/F/starfish_/src/StarfishBase.h:186
- [c] NullOptionType | NullOption=auto | /home/hwang/work/F/starfish_/src/StarfishBase.h:591
- [c] class | ? | /home/hwang/work/F/starfish_/src/browser/history/HistoryManager.h:33
- [c] HistoryManagerOwner | OwnerIsWebView=auto, OwnerIsHTMLIFrame=auto | /home/hwang/work/F/starfish_/src/browser/history/HistoryManager.h:119
- [cpp] setDoneFlag | ? | /home/hwang/work/F/starfish_/src/launcher/ServiceWorkerEntry.cpp:32
- [cpp] setDoneFlag | ? | /home/hwang/work/F/starfish_/src/launcher/SharedWorkerEntry.cpp:32
- [cpp] Command | MoveTo=auto, LineTo=auto, ArcNegative=auto | /home/hwang/work/F/starfish_/src/platform/canvas/CompositorGL.cpp:477
- [c] class | ? | /home/hwang/work/F/starfish_/src/platform/canvas/PathCairo.h:26
- [c] class | ? | /home/hwang/work/F/starfish_/src/platform/canvas/PathMock.h:25
- [c] GLenum | ? | /home/hwang/work/F/starfish_/src/platform/canvas/gl/GLTypes.h:27
- [c] FileMode | Read=1, Write=auto, ReadWrite=auto | /home/hwang/work/F/starfish_/src/platform/file/PlatformFile.h:35
- [c] Whence | SEEK_SET=auto, SEEK_CUR=auto, SEEK_END=auto | /home/hwang/work/F/starfish_/src/platform/file/PlatformFile.h:41
- [c] State | BeforeSend=auto, Receiving=auto, Finished=auto, Failed=auto, Canceled=auto | /home/hwang/work/F/starfish_/src/platform/loader/Resource.h:42
- [c] Type | ResourceType=auto, ImageResourceType=auto, TextResourceType=auto, FontResourceType=auto | /home/hwang/work/F/starfish_/src/platform/loader/Resource.h:50
- [c] Protocol | FILE_PROTOCOL=auto, BLOB_PROTOCOL=auto, DATA_PROTOCOL=auto, ABOUT_PROTOCOL=auto, HTTP_PROTOCOL=auto, HTTPS_PROTOCOL=auto, JAVASCRIPT_PROTOCOL=auto, WS_PROTOCOL=auto, WSS_PROTOCOL=auto, UNKNOWN=auto | /home/hwang/work/F/starfish_/src/platform/loader/ResourceURL.h:35
- [c] Protocol | ? | /home/hwang/work/F/starfish_/src/platform/loader/ResourceURL.h:253
- [c] class | ? | /home/hwang/work/F/starfish_/src/platform/loader/ResourceURL.h:282
- [cpp] RendezvousOwner | None=auto, MainBlockedOnLWE=auto, LWEPausingMain=auto | /home/hwang/work/F/starfish_/src/platform/message_loop/MessageLoopGLib.cpp:99
- [c] SeekWhence | SeekWhenceSet=auto, SeekWhenceCurrent=auto, SeekWhenceEnd=auto, SeekWhenceLookSize=auto | /home/hwang/work/F/starfish_/src/platform/multimedia/DemuxerSource.h:26
- [c] PlaybackState | PLAYBACK_STATE_NONE=auto, PLAYBACK_STATE_PLAYING=auto, PLAYBACK_STATE_PAUSED=auto, PLAYBACK_STATE_END=auto | /home/hwang/work/F/starfish_/src/platform/multimedia/MediaPlayer.h:67
- [c] SeekState | SEEKSTATE_NO_SEEK=auto, SEEKSTATE_SEEKING=auto, SEEKSTATE_WAITING=auto | /home/hwang/work/F/starfish_/src/platform/multimedia/MediaPlayer.h:73
- [c] class | ? | /home/hwang/work/F/starfish_/src/platform/multimedia/MediaPlayerLinux.h:163
- [c] StreamType | StreamTypeUnknown=1, StreamTypeAudio=auto, StreamTypeVideo=auto, StreamTypeSubtitle=auto | /home/hwang/work/F/starfish_/src/platform/multimedia/StreamInfo.h:52
- [c] MediaCodec | MediaCodecUnknown=auto, MediaCodecAudioAAC=auto, MediaCodecAudioMP3=auto, MediaCodecAudioVorbis=auto, MediaCodecAudioOpus=auto, MediaCodecVideoH264=auto, MediaCodecVideoHEVC=auto, MediaCodecVideoVP9=auto, MediaCodecVideoAV1=auto | /home/hwang/work/F/starfish_/src/platform/multimedia/StreamInfo.h:59
- [c] AudioSampleFormat | AudioSampleFormatNone=-1, AudioSampleFormatU8=auto, AudioSampleFormatS16=auto, AudioSampleFormatS32=auto, AudioSampleFormatFLT=auto, AudioSampleFormatDBL=auto, AudioSampleFormatU8P=auto, AudioSampleFormatS16P=auto, AudioSampleFormatS32P=auto, AudioSampleFormatFLTP=auto, AudioSampleFormatDBLP=auto | /home/hwang/work/F/starfish_/src/platform/multimedia/StreamInfo.h:73
- [c] HTTPStatusCode | ? | /home/hwang/work/F/starfish_/src/platform/network/http/HTTPStatus.h:94
- [c] ScreenOrientationType | ScreenOrientationUndefined=0, ScreenOrientationPortraitPrimary=auto, ScreenOrientationPortraitSecondary=auto, ScreenOrientationLandscapePrimary=auto, ScreenOrientationLandscapeSecondary=auto | /home/hwang/work/F/starfish_/src/platform/public/ScreenOrientationType.h:24
- [c] class | ? | /home/hwang/work/F/starfish_/src/public/LWEDelegateLoader.h:34
- [c] class | ? | /home/hwang/work/F/starfish_/src/public/LWELoaderUtils.h:29
- [c] class | ? | /home/hwang/work/F/starfish_/src/public/LWEWorkerDelegateLoader.h:31
- [java] ImeComposingStatus | NORMAL=auto, COMPOSING_START=auto, COMPOSING_END=auto | type: int | /home/hwang/work/F/starfish_/src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java:93
- [cpp] Owner | FREE=auto, ENGINE=auto, READY=auto, PRESENTING=auto | /home/hwang/work/F/starfish_/src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp:190
- [cpp] Owner | FREE=auto, ENGINE=auto, READY=auto, DISPLAYING=auto | /home/hwang/work/F/starfish_/src/public/bridge/efl/LWEWebViewEFL.cpp:153
- [cpp] PORT_WINDOW_BACKEND | GB=auto, GL=auto, HEADLESS=auto | /home/hwang/work/F/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:82
- [cpp] PORT_COMPOSITOR_BACKEND | CAIRO=auto, GL=auto, MOCK=auto | /home/hwang/work/F/starfish_/src/public/bridge/flutter/LWEWebViewFlutter.cpp:83
- [c] class | ? | /home/hwang/work/F/starfish_/src/public/contract/LWEWorkerDelegate.h:28
- [cpp] StarfishStartUpFlag | enableComputedStyleDump=auto, enableFrameTreeDump=auto, enableStackingContextDump=auto, enableHitTestDump=auto, enableDebugGraphicsLayer=auto, enableDebugRepaintRegion=auto, enableRegressionTest=auto | /home/hwang/work/F/starfish_/src/shell/MiniBrowser.cpp:34
- [c] class | ? | /home/hwang/work/F/starfish_/src/shell/WindowKeyType.h:25
- [c] class | ? | /home/hwang/work/F/starfish_/src/shell/WindowKeyType.h:44
- [c] class | ? | /home/hwang/work/F/starfish_/src/shell/WindowKeyType.h:49
- [cpp] setDoneFlag | ? | /home/hwang/work/F/starfish_/src/shell/libuv/AppLoopLibuv.cpp:39
- [cpp] GLenum | ? | /home/hwang/work/F/starfish_/src/shell/windows/RendererWGL.cpp:36
- [python] ABIDW_FLAGS | ? | /home/hwang/work/F/starfish_/tool/lint/check_contract_abi.py:117
- [python] COMPILE_FLAGS | ? | /home/hwang/work/F/starfish_/tool/lint/check_contract_abi.py:128
- [python] ENUM_RE | ? | /home/hwang/work/F/starfish_/tool/lint/check_contract_abi.py:136
- [python] extract_enum_fp | ? | /home/hwang/work/F/starfish_/tool/lint/check_contract_abi.py:438
- [python] _fixture_enum_renumber | ? | /home/hwang/work/F/starfish_/tool/lint/check_contract_abi.py:1112
- [python] enumerate_tests | ? | /home/hwang/work/F/starfish_/tool/wpt/scripts/wpt_status.py:136

<!-- Total: 7004 nodes, 62 relevant -->
