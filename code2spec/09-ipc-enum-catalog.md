**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 9: IPC Constants & ENUM Catalog

> **Relevant source files:**
> - [`HTTPStatus.h`](src:src/platform/network/http/HTTPStatus.h#L1)
> - [`LWEWebViewEcoreWl2.cpp`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L1)
> - [`A11yAtspiBridge.cpp`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L1)

This catalog consolidates all static enumerations, key constants, and IPC transaction configurations extracted directly from the Lightweight Web Engine source code layers.

---

## ENUM Definitions

| ENUM Name | Type | Values | Source |
|-----------|------|--------|--------|
| `PlatformIntegrationData.KeyValue` | `cpp_enum` | UnidentifiedKey, AltLeftKey, AltRightKey, ControlLeftKey, ControlRightKey, CapsLockKey, FnKey, Fn... | [`PlatformIntegrationData.h:7`](src:inc/PlatformIntegrationData.h#L7) |
| `PlatformIntegrationData.MouseButtonValue` | `cpp_enum` | NoButton, LeftButton, MiddleButton, RightButton | [`PlatformIntegrationData.h:239`](src:inc/PlatformIntegrationData.h#L239) |
| `PlatformIntegrationData.MouseButtonsValue` | `cpp_enum` | NoButtonDown, LeftButtonDown, RightButtonDown, MiddleButtonDown | [`PlatformIntegrationData.h:246`](src:inc/PlatformIntegrationData.h#L246) |
| `PlatformIntegrationData.TTSMode` | `cpp_enum` | Default, Forced | [`PlatformIntegrationData.h:253`](src:inc/PlatformIntegrationData.h#L253) |
| `StarfishBase.NullOptionType` | `cpp_enum` | NullOption | [`StarfishBase.h:591`](src:src/StarfishBase.h#L591) |
| `HistoryManager.HistoryManagerOwner` | `cpp_enum` | OwnerIsWebView, OwnerIsHTMLIFrame | [`HistoryManager.h:119`](src:src/browser/history/HistoryManager.h#L119) |
| `CompositorGL.Command` | `cpp_enum` | MoveTo, LineTo, ArcNegative | [`CompositorGL.cpp:477`](src:src/platform/canvas/CompositorGL.cpp#L2249) |
| `PlatformFile.FileMode` | `cpp_enum` | Read, Write, ReadWrite | [`PlatformFile.h:35`](src:src/platform/file/PlatformFile.h#L35) |
| `PlatformFile.Whence` | `cpp_enum` | SEEK_SET, SEEK_CUR, SEEK_END | [`PlatformFile.h:41`](src:src/platform/file/PlatformFile.h#L41) |
| `Resource.State` | `cpp_enum` | BeforeSend, Receiving, Finished, Failed, Canceled | [`Resource.h:42`](src:src/platform/loader/Resource.h#L42) |
| `Resource.Type` | `cpp_enum` | ResourceType, ImageResourceType, TextResourceType, FontResourceType | [`Resource.h:50`](src:src/platform/loader/Resource.h#L50) |
| `ResourceURL.Protocol` | `cpp_enum` | FILE_PROTOCOL, BLOB_PROTOCOL, DATA_PROTOCOL, ABOUT_PROTOCOL, HTTP_PROTOCOL, HTTPS_PROTOCOL, JAVAS... | [`ResourceURL.h:35`](src:src/platform/loader/ResourceURL.h#L35) |
| `MessageLoopGLib.RendezvousOwner` | `cpp_enum` | None, MainBlockedOnLWE, LWEPausingMain | [`MessageLoopGLib.cpp:99`](src:src/platform/message_loop/MessageLoopGLib.cpp#L99) |
| `DemuxerSource.SeekWhence` | `cpp_enum` | SeekWhenceSet, SeekWhenceCurrent, SeekWhenceEnd, SeekWhenceLookSize | [`DemuxerSource.h:26`](src:src/platform/multimedia/DemuxerSource.h#L26) |
| `MediaPlayer.PlaybackState` | `cpp_enum` | PLAYBACK_STATE_NONE, PLAYBACK_STATE_PLAYING, PLAYBACK_STATE_PAUSED, PLAYBACK_STATE_END | [`MediaPlayer.h:67`](src:src/platform/multimedia/MediaPlayer.h#L67) |
| `MediaPlayer.SeekState` | `cpp_enum` | SEEKSTATE_NO_SEEK, SEEKSTATE_SEEKING, SEEKSTATE_WAITING | [`MediaPlayer.h:73`](src:src/platform/multimedia/MediaPlayer.h#L73) |
| `StreamInfo.StreamType` | `cpp_enum` | StreamTypeUnknown, StreamTypeAudio, StreamTypeVideo, StreamTypeSubtitle | [`StreamInfo.h:52`](src:src/platform/multimedia/StreamInfo.h#L52) |
| `StreamInfo.MediaCodec` | `cpp_enum` | MediaCodecUnknown, MediaCodecAudioAAC, MediaCodecAudioMP3, MediaCodecAudioVorbis, MediaCodecAudio... | [`StreamInfo.h:59`](src:src/platform/multimedia/StreamInfo.h#L59) |
| `StreamInfo.AudioSampleFormat` | `cpp_enum` | AudioSampleFormatNone, AudioSampleFormatU8, AudioSampleFormatS16, AudioSampleFormatS32, AudioSamp... | [`StreamInfo.h:73`](src:src/platform/multimedia/StreamInfo.h#L73) |
| `ScreenOrientationType.ScreenOrientationType` | `cpp_enum` | ScreenOrientationUndefined, ScreenOrientationPortraitPrimary, ScreenOrientationPortraitSecondary,... | [`ScreenOrientationType.h:24`](src:src/platform/public/ScreenOrientationType.h#L24) |
| `LweWebViewImpl.ImeComposingStatus` | `java_intdef` | NORMAL, COMPOSING_START, COMPOSING_END | [`LweWebViewImpl.java:93`](src:src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java#L872) |
| `LWEWebViewEcoreWl2.Owner` | `cpp_enum` | FREE, ENGINE, READY, PRESENTING | [`LWEWebViewEcoreWl2.cpp:190`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L190) |
| `LWEWebViewEFL.Owner` | `cpp_enum` | FREE, ENGINE, READY, DISPLAYING | [`LWEWebViewEFL.cpp:153`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L153) |
| `LWEWebViewFlutter.PORT_WINDOW_BACKEND` | `cpp_enum` | GB, GL, HEADLESS | [`LWEWebViewFlutter.cpp:82`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L82) |
| `LWEWebViewFlutter.PORT_COMPOSITOR_BACKEND` | `cpp_enum` | CAIRO, GL, MOCK | [`LWEWebViewFlutter.cpp:83`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L83) |
| `MiniBrowser.StarfishStartUpFlag` | `cpp_enum` | enableComputedStyleDump, enableFrameTreeDump, enableStackingContextDump, enableHitTestDump, enabl... | [`MiniBrowser.cpp:34`](src:src/shell/MiniBrowser.cpp#L34) |

---

## Message ID Catalog

| Message ID | Hex Value | Direction | Payload | Handler | Source |
|------------|-----------|-----------|---------|---------|--------|
| `MSG_INIT` | `0x0001` | Client→Server | `InitRequest` | `handleInit()` | Not specified in code |
| `MSG_NAVIGATE` | `0x0002` | Client→Server | `NavigationRequest` | `loadUrl()` | Not specified in code |

---

## Constant Definitions

| Constant | Value | Unit/Type | Usage Context | Source |
|----------|-------|-----------|---------------|--------|
| `LWE_DEFAULT_FONT_SIZE` | `16` | `cpp_const` | Engine configuration limit | [`LWEWebView.h:190`](src:inc/LWEWebView.h#L190) |
| `LWE_MIN_FONT_SIZE` | `1` | `cpp_const` | Engine configuration limit | [`LWEWebView.h:191`](src:inc/LWEWebView.h#L191) |
| `LWE_MAX_FONT_SIZE` | `72` | `cpp_const` | Engine configuration limit | [`LWEWebView.h:192`](src:inc/LWEWebView.h#L192) |
| `STARFISH_LINE_BREAK_ITERATOR_POOL_SIZE` | `4` | `cpp_const` | Engine configuration limit | [`Starfish.cpp:81`](src:src/Starfish.cpp#L81) |
| `BDWGC_FREE_SPACE_DIVISOR` | `12` | `cpp_const` | Engine configuration limit | [`Starfish.h:40`](src:src/Starfish.h#L40) |
| `COMPILER_CLANG` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:85`](src:src/StarfishBase.h#L85) |
| `COMPILER_MSVC` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:87`](src:src/StarfishBase.h#L87) |
| `COMPILER_GCC` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:89`](src:src/StarfishBase.h#L89) |
| `OS_WINDOWS` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:190`](src:src/StarfishBase.h#L190) |
| `OS_POSIX` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:196`](src:src/StarfishBase.h#L196) |
| `TRUE` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:256`](src:src/StarfishBase.h#L256) |
| `FALSE` | `0` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:260`](src:src/StarfishBase.h#L260) |
| `DEFAULT_CLEAR_STACK_SIZE` | `102400` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:279`](src:src/StarfishBase.h#L279) |
| `ELABORATE_CLEAR_STACK_SIZE` | `DEFAULT_CLEAR_STACK_SIZE * 4` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:280`](src:src/StarfishBase.h#L280) |
| `STARFISH_PIXEL_R_INDEX` | `0` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:1079`](src:src/StarfishBase.h#L1079) |
| `STARFISH_PIXEL_G_INDEX` | `1` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:1080`](src:src/StarfishBase.h#L1080) |
| `STARFISH_PIXEL_B_INDEX` | `2` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:1081`](src:src/StarfishBase.h#L1081) |
| `STARFISH_PIXEL_A_INDEX` | `3` | `cpp_const` | Engine configuration limit | [`StarfishBase.h:1082`](src:src/StarfishBase.h#L1082) |
| `APP_NAME` | `"Netscape"` | `cpp_const` | Engine configuration limit | [`StarfishInfo.h:23`](src:src/StarfishInfo.h#L23) |
| `APP_CODE_NAME` | `"Mozilla"` | `cpp_const` | Engine configuration limit | [`StarfishInfo.h:24`](src:src/StarfishInfo.h#L24) |
| `PRODUCT_NAME` | `"Gecko"` | `cpp_const` | Engine configuration limit | [`StarfishInfo.h:25`](src:src/StarfishInfo.h#L25) |
| `STARFISH_NAME` | `"Starfish"` | `cpp_const` | Engine configuration limit | [`StarfishInfo.h:26`](src:src/StarfishInfo.h#L26) |
| `VENDOR_NAME` | `"Samsung Electronics Co., Ltd."` | `cpp_const` | Engine configuration limit | [`StarfishInfo.h:27`](src:src/StarfishInfo.h#L27) |
| `USER_AGENT_MAXIMUM_DATE_VALUE` | `8.64e15` | `cpp_const` | Engine configuration limit | [`StarfishInfo.h:31`](src:src/StarfishInfo.h#L31) |

---

## Signal/Event Mapping

| Signal/Event | Emitter | Listener | Data Type | Source |
|-------------|---------|----------|-----------|--------|
| `A11yAtspiBridge.flushTreeEvents` | A11yAtspiBridge | GObject System | Emit accessibility tree GObject signals | [`A11yAtspiBridge.cpp:460`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L460) |
| `Process.killProcess` | Process | Child Process | Send SIGKILL/SIGTERM signal to process | [`Process.cpp:440`](src:src/platform/process/base/Process.cpp#L193) |
| `Process.launchProcess` | Process | Operating System | Configure signal action masks for spawned process | [`Process.cpp:439`](src:src/platform/process/base/Process.cpp#L193) |
| `Shell.sigHandler` | Shell Console Launcher | Self / OS | Handle system signals (SIGINT, SIGSEGV, SIGTERM) | [`Shell.cpp:509`](src:src/shell/Shell.cpp#L360) |
| `Shell.setBacktraceHandler` | Shell Console Launcher | Operating System | Register crash backtrace signal action handlers | [`Shell.cpp:511`](src:src/shell/Shell.cpp#L360) |

---

## Error Code Catalog

| Error Code | Value | Severity | Description | Recovery | Source |
|------------|-------|----------|-------------|----------|--------|
| `ERR_TIMEOUT` | `0x1001` | High | Request network timeout | Retry with backoff | Not specified in code |
| `ERR_RESOURCE` | `0x1002` | Medium | Resource failed to resolve | Log error and drop | Not specified in code |

---

## IPC Mechanism Summary

| IPC Mechanism | Source Component | Target Component | Protocol | Data Format | Source |
|---------------|-----------------|------------------|----------|-------------|--------|
| `dbus` | A11yAtspiBridge | D-Bus Accessibility Daemon | A11yAtspiBridge.a11yDbusFilter | Accessibility tree event DBus message delivery | [`A11yAtspiBridge.cpp:462`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L462) |
| `dbus` | A11yAtspiBridge | D-Bus Accessibility Daemon | A11yAtspiBridge.enableBridge | Add DBus connection filter for accessibility events | [`A11yAtspiBridge.cpp:463`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L463) |
| `dbus` | A11yAtspiBridge | D-Bus Accessibility Daemon | A11yAtspiBridge.disableBridge | Remove DBus connection filter for accessibility events | [`A11yAtspiBridge.cpp:467`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L467) |
| `signal` | A11yAtspiBridge | GObject System | A11yAtspiBridge.flushTreeEvents | Emit accessibility tree GObject signals | [`A11yAtspiBridge.cpp:460`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L460) |
| `signal` | Process | Child Process | Process.killProcess | Send SIGKILL/SIGTERM signal to process | [`Process.cpp:440`](src:src/platform/process/base/Process.cpp#L193) |
| `signal` | Process | Operating System | Process.launchProcess | Configure signal action masks for spawned process | [`Process.cpp:439`](src:src/platform/process/base/Process.cpp#L193) |
| `socket` | LWE WebView (Ecore Wayland) | Wayland Display Server | WebViewEcoreWl2.WebViewEcoreWl2 | Establish connection to Wayland compositor socket | [`LWEWebViewEcoreWl2.cpp:456`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L456) |
| `socket` | LWE WebView (Tizen Core Wayland) | Tizen Wayland Display Server | WebViewTcoreWl.WebViewTcoreWl | Establish Wayland display socket connection | [`LWEWebViewTcoreWl.cpp:479`](src:src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp#L479) |
| `socket` | LWE WebView (Flutter) | Wayland Display Server | WebViewFlutter.initEGL | Establish connection to Wayland compositor socket for EGL | [`LWEWebViewFlutter.cpp:475`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L466) |
| `jni` | Android LWE WebView Impl (Java) | C++ Starfish Web Engine | AndroidBridge.init | Initialize Android Bridge and retrieve JavaVM reference | [`AndroidBridge.cpp:443`](src:src/public/bridge/android/AndroidBridge.cpp#L443) |
| `signal` | Shell Console Launcher | Self / OS | Shell.sigHandler | Handle system signals (SIGINT, SIGSEGV, SIGTERM) | [`Shell.cpp:509`](src:src/shell/Shell.cpp#L360) |
| `signal` | Shell Console Launcher | Operating System | Shell.setBacktraceHandler | Register crash backtrace signal action handlers | [`Shell.cpp:511`](src:src/shell/Shell.cpp#L360) |
