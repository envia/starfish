# Code Graph - Core Module Summary

Generated from: `/home/hwang/work/F/starfish_`
Core modules: 20

```mermaid
graph TD
    f0["compat/tizen_5.0/inc/LWEWebView.h"]
    f1["inc/LWEWebView.h"]
    f2["inc/PlatformIntegrationData.h"]
    style f2 fill:#f96,stroke:#333,color:#fff
    f3["src/Starfish.cpp"]
    style f3 fill:#f96,stroke:#333,color:#fff
    f4["src/StarfishBase.h"]
    style f4 fill:#f96,stroke:#333,color:#fff
    f5["src/StarfishConfig.h"]
    style f5 fill:#f96,stroke:#333,color:#fff
    f6["src/StaticStrings.cpp"]
    f7["src/StoragePathProvider.cpp"]
    f8["src/binding/CharacterDataCustomBinding.cpp"]
    f9["src/binding/DocumentCustomBinding.cpp"]
    f10["src/binding/DocumentHoldable.cpp"]
    f11["src/binding/EventTargetCustomBinding.cpp"]
    f12["src/binding/GeolocationCustomBinding.cpp"]
    f13["src/binding/HTMLElementCustomBinding.cpp"]
    f14["src/binding/HTMLInputElementCustomBinding.cpp"]
    f15["src/binding/ImageDataCustomBinding.cpp"]
    f16["src/binding/MediaStreamCustomBinding.cpp"]
    f17["src/binding/ObservableArray.cpp"]
    f18["src/binding/ScriptBindingInstance.cpp"]
    f19["src/binding/ScriptBindingSecurity.cpp"]
    f20["src/binding/ScriptBindingWindowInstance.cpp"]
    f21["src/binding/ScriptBindingWorkerInstance.cpp"]
    f22["src/binding/ScriptEngineInstance.cpp"]
    f23["src/binding/ScriptWrappable.cpp"]
    f24["src/binding/ScriptWrappable.h"]
    f25["src/binding/URLSearchParamsCustomBinding.cpp"]
    f26["src/binding/WebViewHoldable.cpp"]
    f27["src/binding/WindowCustomBinding.cpp"]
    f28["src/binding/WindowHoldable.cpp"]
    f29["src/binding/WindowProxy.cpp"]
    f30["src/binding/WorkerGlobalScopeCustomBinding.cpp"]
    f31["src/binding/XMLHttpRequestCustomBinding.cpp"]
    f32["src/browser/history/HistoryManager.cpp"]
    f33["src/platform/canvas/CanvasCairo.cpp"]
    f34["src/platform/canvas/CanvasCairoUtils.cpp"]
    f35["src/platform/canvas/CanvasMock.cpp"]
    f36["src/platform/canvas/CompositorCairo.cpp"]
    f37["src/platform/canvas/CompositorGL.cpp"]
    style f37 fill:#f96,stroke:#333,color:#fff
    f38["src/platform/canvas/CompositorMock.cpp"]
    f39["src/platform/canvas/PathCairo.cpp"]
    f40["src/platform/canvas/PathMock.cpp"]
    f41["src/platform/canvas/font/FontImplCairo.cpp"]
    f42["src/platform/canvas/font/FontImplMock.cpp"]
    f43["src/platform/canvas/font/hb-icu/HarfBuzzICU.cpp"]
    f44["src/platform/canvas/gl/EvasGL.cpp"]
    style f44 fill:#f96,stroke:#333,color:#fff
    f45["src/platform/canvas/gl/GenericGL.cpp"]
    style f45 fill:#f96,stroke:#333,color:#fff
    f46["src/platform/canvas/image/AnimatedGIFNativeImageDataImpl.cpp"]
    f47["src/platform/canvas/image/CompressedNativeImageDataImpl.cpp"]
    f48["src/platform/canvas/image/NativeImageDataImpl.cpp"]
    f49["src/platform/canvas/image/SVGNativeImageDataImpl.cpp"]
    f50["src/platform/feedback/TapSoundFeedback.cpp"]
    f51["src/platform/file/PlatformDirectory.cpp"]
    f52["src/platform/file/PlatformFile.cpp"]
    f53["src/platform/loader/ElementResourceClient.cpp"]
    f54["src/platform/loader/FontResource.cpp"]
    f55["src/platform/loader/HeaderResource.cpp"]
    f56["src/platform/loader/ImageResource.cpp"]
    f57["src/platform/loader/Resource.cpp"]
    f58["src/platform/loader/ResourceLoader.cpp"]
    f59["src/platform/loader/ResourceURL.cpp"]
    f60["src/platform/loader/TextResource.cpp"]
    f61["src/platform/message_loop/MessageLoopGLib.cpp"]
    f62["src/platform/message_loop/MessageLoopLibUV.cpp"]
    f63["src/platform/message_loop/RunLoopGLib.cpp"]
    f64["src/platform/message_loop/RunLoopLibUV.cpp"]
    f65["src/platform/message_loop/TimerGLib.cpp"]
    f66["src/platform/message_loop/TimerLibUV.cpp"]
    f67["src/platform/multimedia/Demuxer.cpp"]
    f68["src/platform/multimedia/DemuxerMP4.cpp"]
    f69["src/platform/multimedia/DemuxerWebM.cpp"]
    f70["src/platform/multimedia/MP4PacketGenerator.cpp"]
    f71["src/platform/multimedia/MediaPlayer.cpp"]
    f72["src/platform/multimedia/MediaPlayerAudio.cpp"]
    f73["src/platform/multimedia/MediaPlayerAudioLinux.cpp"]
    f74["src/platform/multimedia/MediaPlayerAudioTizen.cpp"]
    f75["src/platform/multimedia/MediaPlayerESPlusPlayer.cpp"]
    f76["src/platform/multimedia/MediaPlayerLinux.cpp"]
    f77["src/platform/multimedia/MediaPlayerTV.cpp"]
    f78["src/platform/multimedia/MediaPlayerTizen.cpp"]
    f79["src/platform/multimedia/MediaPlayerTizenBase.cpp"]
    f80["src/platform/multimedia/MediaPlayerWebRtc.cpp"]
    f81["src/platform/multimedia/MediaPlayerWebRtcLinux.cpp"]
    f82["src/platform/multimedia/MediaPlayerWebRtcTizen.cpp"]
    f83["src/platform/multimedia/MockMediaPlayer.cpp"]
    f84["src/platform/multimedia/StreamInfo.cpp"]
    f85["src/platform/network/curl/NetworkSharedResourceManager.cpp"]
    f86["src/platform/network/http/HTTPCache.cpp"]
    f87["src/platform/network/http/HTTPCacheEntry.cpp"]
    f88["src/platform/network/http/HTTPHeaderMap.cpp"]
    f89["src/platform/network/http/HTTPRequest.cpp"]
    f90["src/platform/network/http/HTTPResponse.cpp"]
    f91["src/platform/network/http/HTTPTransaction.cpp"]
    style f91 fill:#f96,stroke:#333,color:#fff
    f92["src/platform/network/http/HTTPUtil.cpp"]
    f93["src/platform/process/base/Process.cpp"]
    f94["src/platform/public/DeviceInfo.cpp"]
    f95["src/platform/tts/TTSBase.cpp"]
    f96["src/platform/tts/TTSTV.cpp"]
    f97["src/platform/tts/TTSTizen.cpp"]
    f98["src/platform/windows/LoggingWindows.cpp"]
    f99["src/public/LWEWebView.cpp"]
    style f99 fill:#f96,stroke:#333,color:#fff
    f100["src/public/bridge/android/AndroidBridge.cpp"]
    f101["src/public/bridge/android/java/com/samsung/android/lightweightwebengine/WebView.java"]
    style f101 fill:#f96,stroke:#333,color:#fff
    f102["src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java"]
    style f102 fill:#f96,stroke:#333,color:#fff
    f103["src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp"]
    style f103 fill:#f96,stroke:#333,color:#fff
    f104["src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp"]
    f105["src/public/bridge/efl/A11yAtspiBridge.cpp"]
    f106["src/public/bridge/efl/A11yAtspiBridge.h"]
    f107["src/public/bridge/efl/LWEWebViewEFL.cpp"]
    f108["src/public/bridge/flutter/LWEWebViewFlutter.cpp"]
    f109["src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp"]
    style f109 fill:#f96,stroke:#333,color:#fff
    f110["src/public/bridge/x11/LWEWebViewX11.cpp"]
    f111["src/public/contract/LWEWebContainerDelegate.h"]
    f112["src/public/contract/SettingsDelegate.h"]
    f113["src/public/delegate/CookieManagerDelegate.cpp"]
    f114["src/public/delegate/JavaScriptNativeHandler.cpp"]
    f115["src/public/delegate/LWEDelegate.cpp"]
    f116["src/public/delegate/LWEWebContainerDelegate.cpp"]
    style f116 fill:#f96,stroke:#333,color:#fff
    f117["src/public/delegate/LWEWebViewDelegate.cpp"]
    f118["src/public/delegate/LWEWebViewDelegateImpl.cpp"]
    f119["src/public/delegate/LWEWorkerDelegate.cpp"]
    f120["src/public/delegate/ThreadedCallHelper.cpp"]
    f121["src/shell/MiniBrowser.cpp"]
    f122["src/shell/Shell.h"]
    f123["src/shell/Window.h"]
    style f123 fill:#f96,stroke:#333,color:#fff
    f124["src/shell/dummy/WindowDummy.cpp"]
    f125["src/shell/efl/WindowEFL.cpp"]
    f126["src/shell/headless/WindowHeadless.cpp"]
    f127["src/shell/test/APIRecorderTest.cpp"]
    f128["src/shell/test/WebContainerTest.cpp"]
    f129["src/shell/test/WebViewTest.cpp"]
    f130["src/shell/x11_webcontainer/WindowX11Webcontainer.cpp"]
    f131["tool/lint/check_contract_abi.py"]
    f132["tool/repo_paths.py"]
    style f132 fill:#f96,stroke:#333,color:#fff
    f133["tool/runner/execution_test.py"]
    f134["tool/runner/execution_worker.py"]
    f135["tool/runner/test_runner.py"]
    f136["tool/runner/uwe_loader_test.py"]
    f137["tool/runner/uwe_worker_loader_test.py"]
    f138["tool/wpt/scripts/wpt_annotate.py"]
    f139["tool/wpt/scripts/wpt_audit.py"]
    f140["tool/wpt/scripts/wpt_manifest_lists.py"]
    f141["tool/wpt/scripts/wpt_reftest.py"]
    f142["tool/wpt/scripts/wpt_runner.py"]
    style f142 fill:#f96,stroke:#333,color:#fff
    f143["tool/wpt/scripts/wpt_server.py"]
    style f143 fill:#f96,stroke:#333,color:#fff
    f144["tool/wpt/scripts/wpt_status.py"]
    f0 -->|imports| f2
    f1 -->|imports| f2
    f3 -->|imports| f5
    f3 -->|imports| f1
    f4 -->|imports| f140
    f5 -->|imports| f4
    f6 -->|imports| f5
    f7 -->|imports| f5
    f8 -->|imports| f5
    f9 -->|imports| f5
    f10 -->|imports| f5
    f11 -->|imports| f5
    f12 -->|imports| f5
    f13 -->|imports| f5
    f14 -->|imports| f5
    f15 -->|imports| f5
    f16 -->|imports| f5
    f17 -->|imports| f5
    f18 -->|imports| f5
    f18 -->|imports| f24
    f19 -->|imports| f5
    f19 -->|imports| f2
    f20 -->|imports| f5
    f20 -->|imports| f24
    f21 -->|imports| f5
    f21 -->|imports| f24
    f22 -->|imports| f5
    f23 -->|imports| f5
    f23 -->|imports| f24
    f24 -->|imports| f4
    f25 -->|imports| f5
    f26 -->|imports| f5
    f27 -->|imports| f5
    f27 -->|imports| f2
    f28 -->|imports| f5
    f29 -->|imports| f5
    f30 -->|imports| f5
    f31 -->|imports| f5
    f32 -->|imports| f5
    f33 -->|imports| f5
    f34 -->|imports| f5
    f35 -->|imports| f5
    f36 -->|imports| f5
    f37 -->|imports| f5
    f38 -->|imports| f5
    f39 -->|imports| f5
    f40 -->|imports| f5
    f41 -->|imports| f5
    f42 -->|imports| f5
    f43 -->|imports| f4
    f44 -->|imports| f5
    f45 -->|imports| f5
    f46 -->|imports| f5
    f47 -->|imports| f5
    f48 -->|imports| f5
    f49 -->|imports| f5
    f50 -->|imports| f5
    f51 -->|imports| f5
    f52 -->|imports| f5
    f53 -->|imports| f5
    f54 -->|imports| f5
    f55 -->|imports| f5
    f56 -->|imports| f5
    f57 -->|imports| f5
    f58 -->|imports| f5
    f59 -->|imports| f5
    f60 -->|imports| f5
    f61 -->|imports| f5
    f62 -->|imports| f5
    f63 -->|imports| f5
    f64 -->|imports| f5
    f65 -->|imports| f5
    f66 -->|imports| f5
    f67 -->|imports| f5
    f68 -->|imports| f5
    f69 -->|imports| f5
    f70 -->|imports| f5
    f71 -->|imports| f5
    f72 -->|imports| f5
    f73 -->|imports| f5
    f74 -->|imports| f5
    f75 -->|imports| f5
    f76 -->|imports| f5
    f77 -->|imports| f5
    f78 -->|imports| f5
    f79 -->|imports| f5
    f80 -->|imports| f5
    f81 -->|imports| f5
    f82 -->|imports| f5
    f83 -->|imports| f5
    f84 -->|imports| f5
    f85 -->|imports| f5
    f85 -->|imports| f24
    f86 -->|imports| f5
    f86 -->|imports| f24
    f87 -->|imports| f5
    f88 -->|imports| f5
    f89 -->|imports| f5
    f90 -->|imports| f5
    f91 -->|imports| f5
    f92 -->|imports| f5
    f92 -->|imports| f24
    f93 -->|imports| f5
    f94 -->|imports| f5
    f95 -->|imports| f5
    f96 -->|imports| f5
    f97 -->|imports| f5
    f98 -->|imports| f5
    f99 -->|imports| f1
    f99 -->|imports| f112
    f99 -->|imports| f111
    f100 -->|imports| f5
    f100 -->|imports| f1
    f103 -->|imports| f5
    f103 -->|imports| f2
    f103 -->|imports| f111
    f103 -->|imports| f1
    f104 -->|imports| f5
    f104 -->|imports| f2
    f104 -->|imports| f111
    f104 -->|imports| f1
    f105 -->|imports| f5
    f105 -->|imports| f106
    f106 -->|imports| f5
    f107 -->|imports| f5
    f107 -->|imports| f2
    f107 -->|imports| f111
    f107 -->|imports| f106
    f108 -->|imports| f5
    f108 -->|imports| f1
    f108 -->|imports| f112
    f108 -->|imports| f2
    f108 -->|imports| f111
    f109 -->|imports| f5
    f109 -->|imports| f2
    f109 -->|imports| f111
    f109 -->|imports| f1
    f110 -->|imports| f5
    f110 -->|imports| f2
    f110 -->|imports| f111
    f110 -->|imports| f1
    f111 -->|imports| f2
    f112 -->|imports| f2
    f113 -->|imports| f5
    f114 -->|imports| f5
    f114 -->|imports| f24
    f115 -->|imports| f5
    f116 -->|imports| f5
    f116 -->|imports| f111
    f116 -->|imports| f112
    f116 -->|imports| f24
    f117 -->|imports| f5
    f118 -->|imports| f5
    f118 -->|imports| f112
    f118 -->|imports| f111
    f119 -->|imports| f5
    f120 -->|imports| f5
    f121 -->|imports| f123
    f122 -->|imports| f2
    f123 -->|imports| f2
    f124 -->|imports| f123
    f125 -->|imports| f123
    f126 -->|imports| f123
    f127 -->|imports| f1
    f127 -->|imports| f123
    f128 -->|imports| f1
    f128 -->|imports| f123
    f129 -->|imports| f1
    f129 -->|imports| f123
    f130 -->|imports| f123
    f131 -->|imports| f36
    f131 -->|imports| f16
    f131 -->|imports| f132
    f132 -->|imports| f36
    f133 -->|imports| f36
    f133 -->|imports| f67
    f133 -->|imports| f132
    f134 -->|imports| f36
    f134 -->|imports| f67
    f134 -->|imports| f132
    f135 -->|imports| f36
    f135 -->|imports| f33
    f135 -->|imports| f132
    f135 -->|imports| f134
    f135 -->|imports| f142
    f135 -->|imports| f143
    f135 -->|imports| f141
    f135 -->|imports| f144
    f136 -->|imports| f36
    f136 -->|imports| f132
    f137 -->|imports| f36
    f137 -->|imports| f67
    f137 -->|imports| f132
    f138 -->|imports| f36
    f138 -->|imports| f142
    f139 -->|imports| f36
    f139 -->|imports| f132
    f139 -->|imports| f143
    f140 -->|imports| f36
    f140 -->|imports| f143
    f140 -->|imports| f144
    f141 -->|imports| f36
    f141 -->|imports| f16
    f141 -->|imports| f132
    f141 -->|imports| f143
    f142 -->|imports| f36
    f142 -->|imports| f16
    f142 -->|imports| f132
    f142 -->|imports| f143
    f142 -->|imports| f141
    f143 -->|imports| f36
    f143 -->|imports| f67
    f143 -->|imports| f132
    f144 -->|imports| f36
    f144 -->|imports| f143
    f144 -->|imports| f142
    f144 -->|imports| f141
```

## Legend

- 🔴 **Red background** = Core module
- Default background = Related module
- **Total Files**: 145
- **Import Relationships**: 217
