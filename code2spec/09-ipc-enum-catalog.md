# 09 — IPC, ENUM, and Constant Catalog

> **Relevant source files**
> - [`inc/PlatformIntegrationData.h`](inc:PlatformIntegrationData.h)
> - [`src/platform/multimedia/StreamInfo.h`](src:src/platform/multimedia/StreamInfo.h)
> - [`src/platform/multimedia/MediaPlayer.h`](src:src/platform/multimedia/MediaPlayer.h)
> - [`src/platform/loader/Resource.h`](src:src/platform/loader/Resource.h)
> - [`src/platform/file/PlatformFile.h`](src/platform/file/PlatformFile.h)
> - [`src/shell/MiniBrowser.cpp`](src/shell/MiniBrowser.cpp)
> - [`src/streamline_annotate.h`](src/streamline_annotate.h)

## ENUM Definitions

| Name | Values | Source |
|---|---|---|
| KeyValue | UnidentifiedKey, AltLeftKey, AltRightKey, ... (229 total) | [`PlatformIntegrationData.h:7`](inc:PlatformIntegrationData.h#L7) |
| MouseButtonValue | NoButton, LeftButton, MiddleButton, RightButton | [`PlatformIntegrationData.h:239`](inc:PlatformIntegrationData.h#L239) |
| MouseButtonsValue | NoButtonDown, LeftButtonDown, RightButtonDown, MiddleButtonDown | [`PlatformIntegrationData.h:246`](inc:PlatformIntegrationData.h#L246) |
| TTSMode | Default, Forced | [`PlatformIntegrationData.h:253`](inc:PlatformIntegrationData.h#L253) |
| HistoryManagerOwner | OwnerIsWebView, OwnerIsHTMLIFrame | [`HistoryManager.h:119`](src:src/browser/history/HistoryManager.h#L119) |
| FileMode | Read, Write, ReadWrite | [`PlatformFile.h:35`](src/platform/file/PlatformFile.h#L35) |
| Whence | SEEK_SET, SEEK_CUR, SEEK_END | [`PlatformFile.h:41`](src/platform/file/PlatformFile.h#L41) |
| Resource.State | BeforeSend, Receiving, Finished, Failed, Canceled | [`Resource.h:42`](src/platform/loader/Resource.h#L42) |
| Resource.Type | ResourceType, ImageResourceType, TextResourceType, FontResourceType | [`Resource.h:50`](src/platform/loader/Resource.h#L50) |
| PlaybackState | PLAYBACK_STATE_NONE, PLAYBACK_STATE_PLAYING, PLAYBACK_STATE_PAUSED, PLAYBACK_STATE_END | [`MediaPlayer.h:67`](src/platform/multimedia/MediaPlayer.h#L67) |
| SeekState | SEEKSTATE_NO_SEEK, SEEKSTATE_SEEKING, SEEKSTATE_WAITING | [`MediaPlayer.h:73`](src/platform/multimedia/MediaPlayer.h#L73) |
| StreamInfo.StreamType | StreamTypeUnknown, StreamTypeAudio, StreamTypeVideo, StreamTypeSubtitle | [`StreamInfo.h:52`](src/platform/multimedia/StreamInfo.h#L52) |
| StreamInfo.MediaCodec | MediaCodecUnknown, MediaCodecAudioAAC, MediaCodecAudioMP3, MediaCodecAudioVorbis, MediaCodecAudioOpus, MediaCodecVideoH264, MediaCodecVideoHEVC, MediaCodecVideoVP9, MediaCodecVideoAV1 | [`StreamInfo.h:59`](src/platform/multimedia/StreamInfo.h#L59) |
| StreamInfo.AudioSampleFormat | AudioSampleFormatNone, U8, S16, S32, FLT, DBL, U8P, S16P, S32P, FLTP, DBLP | [`StreamInfo.h:73`](src/platform/multimedia/StreamInfo.h#L73) |
| ScreenOrientationType | Undefined, PortraitPrimary, PortraitSecondary, LandscapePrimary, LandscapeSecondary | [`ScreenOrientationType.h:24`](src/platform/public/ScreenOrientationType.h#L24) |
| LweWebViewImpl.ImeComposingStatus | NORMAL, COMPOSING_START, COMPOSING_END | [`LweWebViewImpl.java:93`](src:src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java#L872) |
| LWEWebViewEcoreWl2.Owner | FREE, ENGINE, READY, PRESENTING | [`LWEWebViewEcoreWl2.cpp:190`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L190) |
| LWEWebViewEFL.Owner | FREE, ENGINE, READY, DISPLAYING | [`LWEWebViewEFL.cpp:153`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L153) |
| LWEWebViewFlutter.PORT_WINDOW_BACKEND | GB, GL, HEADLESS | [`LWEWebViewFlutter.cpp:82`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L82) |
| LWEWebViewFlutter.PORT_COMPOSITOR_BACKEND | CAIRO, GL, MOCK | [`LWEWebViewFlutter.cpp:83`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L83) |

## Constant Definitions

### Font Size Constants

| Name | Value | Source |
|---|---|---|
| LWE_DEFAULT_FONT_SIZE | 16 | [`LWEWebView.h:180`](compat/tizen_5.0/inc/LWEWebView.h#L180) |
| LWE_MIN_FONT_SIZE | 1 | [`LWEWebView.h:181`](compat/tizen_5.0/inc/LWEWebView.h#L181) |
| LWE_MAX_FONT_SIZE | 72 | [`LWEWebView.h:182`](compat/tizen_5.0/inc/LWEWebView.h#L182) |

### GC Configuration

| Name | Value | Source |
|---|---|---|
| BDWGC_FREE_SPACE_DIVISOR | 12 | [`Starfish.h:40`](src:src/Starfish.h#L40) |
| STARFISH_LINE_BREAK_ITERATOR_POOL_SIZE | 4 | [`Starfish.cpp:81`](src:src/Starfish.cpp#L81) |

### Streamline Profiler Colors

| Name | Value | Source |
|---|---|---|
| ANNOTATE_RED | 0x0000ff1b | [`streamline_annotate.h:73`](src/streamline_annotate.h#L73) |
| ANNOTATE_BLUE | 0xff00001b | [`streamline_annotate.h:74`](src/streamline_annotate.h#L74) |
| ANNOTATE_GREEN | 0x00ff001b | [`streamline_annotate.h:75`](src/streamline_annotate.h#L75) |
| ANNOTATE_PURPLE | 0xff00ff1b | [`streamline_annotate.h:76`](src/streamline_annotate.h#L76) |
| ANNOTATE_YELLOW | 0x00ffff1b | [`streamline_annotate.h:77`](src/streamline_annotate.h#L77) |
| ANNOTATE_CYAN | 0xffff001b | [`streamline_annotate.h:78`](src/streamline_annotate.h#L78) |
| ANNOTATE_WHITE | 0xffffff1b | [`streamline_annotate.h:79`](src/streamline_annotate.h#L79) |
| ANNOTATE_BLACK | 0x0000001b | [`streamline_annotate.h:82`](src/streamline_annotate.h#L82) |

### Test Status Constants

| Name | Value | Type | Source |
|---|---|---|---|
| TEST_PASSED | 0 | python_const | [`constants.py:13`](tool/drivers/basics/constants.py#L13) |
| TEST_FAILED | 1 | error_code | [`constants.py:14`](tool/drivers/basics/constants.py#L14) |
| TEST_STOPPED | 2 | error_code | [`constants.py:15`](tool/drivers/basics/constants.py#L15) |

### Render Test Constants

| Name | Value | Source |
|---|---|---|
| TOLERANCE | 8 | [`check_render_bmp.py:30`](tool/ci/check_render_bmp.py#L30) |
| MIN_PAINT_FRACTION | 0.002 | [`check_render_bmp.py:38`](tool/ci/check_render_bmp.py#L38) |
| MIN_IMAGE_FRACTION | 0.0002 | [`check_render_bmp.py:39`](tool/ci/check_render_bmp.py#L39) |
| MIN_INK_FRACTION | 0.0001 | [`check_render_bmp.py:40`](tool/ci/check_render_bmp.py#L40) |

## IPC Mechanism Summary

Starfish is a single-process browser engine. IPC is limited to test/tooling HTTP sockets.

| Mechanism | Component | Target | Source |
|---|---|---|---|
| socket | wpt_audit.probe | WPT HTTP/HTTPS Server | [`wpt_audit.py`](tool/wpt/scripts/wpt_audit.py) |
| socket | wpt_server._port_open | WPT Server Port | [`wpt_server.py`](tool/wpt/scripts/wpt_server.py) |
| socket | wpt_server._http_ok | WPT HTTP Server | [`wpt_server.py`](tool/wpt/scripts/wpt_server.py) |
| socket | http_server.RequestHandler | HTTP Client | [`http_server.py`](tool/runner/http_server.py) |
| socket | perf_tools.server.H | HTTP Client (benchmark) | [`measure-bench/server.py`](tool/perf_tools/measure-bench/server.py) |
| socket | mse_smoke.server.H | HTTP Client (MSE test) | [`mse-smoke/server.py`](tool/perf_tools/mse-smoke/server.py) |
| socket | style_smoke.server.H | HTTP Client (style test) | [`style-smoke/server.py`](tool/perf_tools/style-smoke/server.py) |
| socket | wpt_runner.run_one | WPT Server | [`wpt_runner.py`](tool/wpt/scripts/wpt_runner.py) |

## Message ID Catalog

No protocol message IDs identified. The engine does not use custom IPC message protocols.

## Signal/Event Mapping

| Signal | Handler | Source |
|---|---|---|
| Process signals | `sigHandler` | [`Shell.cpp`](src/shell/Shell.cpp) |
| Backtrace | `setBacktraceHandler` | [`Shell.cpp`](src/shell/Shell.cpp) |

## Error Code Catalog

| Name | Value | Context | Source |
|---|---|---|---|
| TEST_FAILED | 1 | Test result: failed | [`constants.py:14`](tool/drivers/basics/constants.py#L14) |
| TEST_STOPPED | 2 | Test result: stopped | [`constants.py:15`](tool/drivers/basics/constants.py#L15) |

