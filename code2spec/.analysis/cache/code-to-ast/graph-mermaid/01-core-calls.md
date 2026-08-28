# Code Graph - All Function Calls


Total call relationships: 19290

## Diagrams by Module

### Module: compat

```mermaid
graph TD
    n0[["ExternalImageInfo"]]
    n1[["RenderResult"]]
    n2[["WebContainerArguments"]]
    n3[["RendererGLConfiguration"]]
    n4[["TransformationMatrix"]]
    n5["SetVersionPreference"]
    n6["IsInitialized"]
    n7["Finalize"]
    n8["GetGCFrequency"]
    n9["SetGCFrequency"]
    n10["GetVersion"]
    n11["IsUsingSeparateThread"]
    n12["HasCookies"]
    n13["ClearCookies"]
    n14["GetInstance"]
    n15["Destroy"]
    n16["UpdateSetting"]
    n17["GetCacheMode"]
    n18["Create"]
    n19["RegisterOnRenderedHandler"]
    n20["UpdateBuffer"]
    n21["CreateWithPlatformImage"]
    n22["CreateGL"]
    n23["CreateGLWithPlatformImage"]
    n24["CreateWebContainer"]
    n25["CreateHeadless"]
    n26["AddIdleCallback"]
    n27["AddTimeout"]
    n28["ClearTimeout"]
    n29["RegisterCanRenderingHandler"]
    n30["GetSettings"]
    n31["LoadURL"]
    n32["GetURL"]
    n33["LoadData"]
    n34["Reload"]
    n35["StopLoading"]
    n36["GoBack"]
    n37["GoForward"]
    n38["CanGoBack"]
    n39["CanGoForward"]
    n40["AddJavaScriptInterface"]
    n41["ClearHistory"]
    n15["Destroy"]
    n42["Pause"]
    n43["Resume"]
    n44["ResizeTo"]
    n45["Focus"]
    n46["Blur"]
    n47["SetSettings"]
    n48["RemoveJavascriptInterface"]
    n49["ClearCache"]
    n50["RegisterOnReceivedErrorHandler"]
    n51["RegisterOnPageParsedHandler"]
    n52["RegisterOnPageLoadedHandler"]
    n53["RegisterOnPageStartedHandler"]
    n54["RegisterOnLoadResourceHandler"]
    n55["RegisterShouldOverrideUrlLoadingHandler"]
    n56["RegisterOnProgressChangedHandler"]
    n57["RegisterOnDownloadStartHandler"]
    n58["RegisterShowDropdownMenuHandler"]
    n59["RegisterShowAlertHandler"]
    n60["RegisterCustomFileResourceRequestHandlers"]
    n61["RegisterDebuggerShouldInitHandler"]
    n62["RegisterDebuggerShouldContinueWaitingHandler"]
    n63["RegisterOnIdleHandler"]
    n64["CallHandler"]
    n65["SetUserAgentString"]
    n66["GetUserAgentString"]
    n67["SetCacheMode"]
    n17["GetCacheMode"]
    n68["SetDefaultFontSize"]
    n69["GetDefaultFontSize"]
    n70["DispatchMouseMoveEvent"]
    n71["DispatchMouseDownEvent"]
    n72["DispatchMouseUpEvent"]
    n73["DispatchMouseWheelEvent"]
    n74["DispatchTouchStartEvent"]
    n75["DispatchTouchMoveEvent"]
    n76["DispatchTouchEndEvent"]
    n77["DispatchKeyDownEvent"]
    n78["DispatchKeyPressEvent"]
    n79["DispatchKeyUpEvent"]
    n80["DispatchCompositionStartEvent"]
    n81["DispatchCompositionUpdateEvent"]
    n82["DispatchCompositionEndEvent"]
    n83["RegisterOnShowSoftwareKeyboardIfPossibleHandler"]
    n84["RegisterOnHideSoftwareKeyboardIfPossibleHandler"]
    n85["SetUserData"]
    n86["GetUserData"]
    n87["GetTitle"]
    n88["ScrollTo"]
    n89["ScrollBy"]
    n90["GetScrollX"]
    n91["GetScrollY"]
    n92["Width"]
    n93["Height"]
    n94["SetDevicePixelRatio"]
    n95["GetDevicePixelRatio"]
    n96["RegisterGetScreenMatrixHandler"]
    n18["Create"]
    n15["Destroy"]
    n30["GetSettings"]
    n31["LoadURL"]
    n32["GetURL"]
    n33["LoadData"]
    n34["Reload"]
    n35["StopLoading"]
    n36["GoBack"]
    n37["GoForward"]
    n38["CanGoBack"]
    n39["CanGoForward"]
    n42["Pause"]
    n43["Resume"]
    n40["AddJavaScriptInterface"]
    n41["ClearHistory"]
    n47["SetSettings"]
    n48["RemoveJavascriptInterface"]
    n49["ClearCache"]
    n50["RegisterOnReceivedErrorHandler"]
    n51["RegisterOnPageParsedHandler"]
    n52["RegisterOnPageLoadedHandler"]
    n53["RegisterOnPageStartedHandler"]
    n54["RegisterOnLoadResourceHandler"]
    n60["RegisterCustomFileResourceRequestHandlers"]
    n61["RegisterDebuggerShouldInitHandler"]
    n62["RegisterDebuggerShouldContinueWaitingHandler"]
    n85["SetUserData"]
    n86["GetUserData"]
    n87["GetTitle"]
    n88["ScrollTo"]
    n89["ScrollBy"]
    n90["GetScrollX"]
    n91["GetScrollY"]
    n97["Unwrap"]
    n45["Focus"]
    n46["Blur"]
    n94["SetDevicePixelRatio"]
    n95["GetDevicePixelRatio"]
    n98["FetchWebContainer"]
    n17 -->|calls| n99
```

### Module: inc

```mermaid
graph TD
    n0[["RenderInfo"]]
    n1[["ExternalImageInfo"]]
    n2[["RenderResult"]]
    n3[["WebContainerArguments"]]
    n4[["RendererGLConfiguration"]]
    n5[["TransformationMatrix"]]
    n6["SetVersionPreference"]
    n7["IsInitialized"]
    n8["Finalize"]
    n9["GetGCFrequency"]
    n10["SetGCFrequency"]
    n11["GetVersion"]
    n12["IsUsingSeparateThread"]
    n13["HasCookies"]
    n14["ClearCookies"]
    n15["GetInstance"]
    n16["Destroy"]
    n17["UpdateSetting"]
    n18["GetCacheMode"]
    n19["Create"]
    n20["RegisterPreRenderingHandler"]
    n21["RegisterOnRenderedHandler"]
    n22["CreateWithPlatformImage"]
    n23["CreateGL"]
    n24["CreateGLWithPlatformImage"]
    n25["CreateWebContainer"]
    n26["CreateHeadless"]
    n27["AddIdleCallback"]
    n28["AddTimeout"]
    n29["ClearTimeout"]
    n30["RegisterCanRenderingHandler"]
    n31["GetSettings"]
    n32["LoadURL"]
    n33["GetURL"]
    n34["LoadData"]
    n35["Reload"]
    n36["StopLoading"]
    n37["GoBack"]
    n38["GoForward"]
    n39["CanGoBack"]
    n40["CanGoForward"]
    n41["AddJavaScriptInterface"]
    n42["ClearHistory"]
    n16["Destroy"]
    n43["Pause"]
    n44["Resume"]
    n45["ResizeTo"]
    n46["Focus"]
    n47["Blur"]
    n48["SetSettings"]
    n49["RemoveJavascriptInterface"]
    n50["ClearCache"]
    n51["RegisterOnReceivedErrorHandler"]
    n52["RegisterOnPageParsedHandler"]
    n53["RegisterOnPageLoadedHandler"]
    n54["RegisterOnPageStartedHandler"]
    n55["RegisterOnLoadResourceHandler"]
    n56["RegisterShouldOverrideUrlLoadingHandler"]
    n57["RegisterOnProgressChangedHandler"]
    n58["RegisterOnDownloadStartHandler"]
    n59["RegisterShowDropdownMenuHandler"]
    n60["RegisterShowAlertHandler"]
    n61["RegisterCustomFileResourceRequestHandlers"]
    n62["RegisterDebuggerShouldInitHandler"]
    n63["RegisterDebuggerShouldContinueWaitingHandler"]
    n64["RegisterOnIdleHandler"]
    n65["CallHandler"]
    n66["SetUserAgentString"]
    n67["GetUserAgentString"]
    n68["SetCacheMode"]
    n18["GetCacheMode"]
    n69["SetDefaultFontSize"]
    n70["GetDefaultFontSize"]
    n71["DispatchMouseMoveEvent"]
    n72["DispatchMouseDownEvent"]
    n73["DispatchMouseUpEvent"]
    n74["DispatchMouseWheelEvent"]
    n75["DispatchTouchStartEvent"]
    n76["DispatchTouchMoveEvent"]
    n77["DispatchTouchEndEvent"]
    n78["DispatchKeyDownEvent"]
    n79["DispatchKeyPressEvent"]
    n80["DispatchKeyUpEvent"]
    n81["DispatchCompositionStartEvent"]
    n82["DispatchCompositionUpdateEvent"]
    n83["DispatchCompositionEndEvent"]
    n84["RegisterOnShowSoftwareKeyboardIfPossibleHandler"]
    n85["RegisterOnHideSoftwareKeyboardIfPossibleHandler"]
    n86["SetUserData"]
    n87["GetUserData"]
    n88["GetTitle"]
    n89["ScrollTo"]
    n90["ScrollBy"]
    n91["GetScrollX"]
    n92["GetScrollY"]
    n93["Width"]
    n94["Height"]
    n95["SetDevicePixelRatio"]
    n96["GetDevicePixelRatio"]
    n97["RegisterGetScreenMatrixHandler"]
    n19["Create"]
    n16["Destroy"]
    n31["GetSettings"]
    n32["LoadURL"]
    n33["GetURL"]
    n34["LoadData"]
    n35["Reload"]
    n36["StopLoading"]
    n37["GoBack"]
    n38["GoForward"]
    n39["CanGoBack"]
    n40["CanGoForward"]
    n43["Pause"]
    n44["Resume"]
    n41["AddJavaScriptInterface"]
    n42["ClearHistory"]
    n48["SetSettings"]
    n49["RemoveJavascriptInterface"]
    n50["ClearCache"]
    n51["RegisterOnReceivedErrorHandler"]
    n52["RegisterOnPageParsedHandler"]
    n53["RegisterOnPageLoadedHandler"]
    n54["RegisterOnPageStartedHandler"]
    n55["RegisterOnLoadResourceHandler"]
    n61["RegisterCustomFileResourceRequestHandlers"]
    n62["RegisterDebuggerShouldInitHandler"]
    n63["RegisterDebuggerShouldContinueWaitingHandler"]
    n86["SetUserData"]
    n87["GetUserData"]
    n88["GetTitle"]
    n89["ScrollTo"]
    n90["ScrollBy"]
    n91["GetScrollX"]
    n92["GetScrollY"]
    n98["Unwrap"]
    n46["Focus"]
    n47["Blur"]
    n95["SetDevicePixelRatio"]
    n96["GetDevicePixelRatio"]
    n99["FetchWebContainer"]
    n18 -->|calls| n100
```

### Module: src

```mermaid
graph TD
    n0[["SSIZE_T"]]
    n1[["uint"]]
    n2[["typename"]]
    n3["clearStack"]
    n3["clearStack"]
    n3["clearStack"]
    n4["forwardPrintingLogInfo"]
    n5["forwardPrintingLogError"]
    n6["forwardPrintingLogWarn"]
    n7["getWindowsTempDir"]
    n8["m_value"]
    n9["value"]
    n10["valueOr"]
    n11["getValue"]
    n12["reset"]
    n8["m_value"]
    n9["value"]
    n13["valueOrNull"]
    n10["valueOr"]
    n11["getValue"]
    n12["reset"]
    n14["markHashTable"]
    n15["hash_combine"]
    n16["narrow_cast"]
    n17["downcast"]
    n18["castTo"]
    n19["isInfOrNan"]
    n19["isInfOrNan"]
    n20["OnScopeLeave"]
    n21[["ObservableArrayBackend"]]
    n22["ObservableArrayBackend"]
    n23["backendOf"]
    n24["isLengthKey"]
    n25["seedTarget"]
    n26["setTrap"]
    n27["definePropertyTrap"]
    n28["deletePropertyTrap"]
    n29["defineTrap"]
    n30["create"]
    n31["syncFromHost"]
    n32[["GlobalBindingNameAccessorPropertyData"]]
    n33["compilePotentialWASMResponse"]
    n34["compileStreamingWASMFunction"]
    n35["instantiateStreamingWASMFunction"]
    n36["ScriptBindingInstance"]
    n37["GlobalBindingNameAccessorPropertyData"]
    n38["operator new"]
    n39["accessorGetter"]
    n40["accessorSetter"]
    n41["initBinding"]
    n42["defineGlobalBindingNameAccessor"]
    n43["destroy"]
    n44["toBrowserStringForConsole"]
    n45["printToDebuggerInConsole"]
    n46["_createConcatenatedStringForConsole"]
    n47["_timeConsoleFunction"]
    n48["_timeLogConsoleFunction"]
    n49["_timeEndConsoleFunction"]
    n50["_groupConsoleFunction"]
    n51["_groupCollapsedConsoleFunction"]
    n52["_groupEndConsoleFunction"]
    n53["_assertConsoleFunction"]
    n54["_logConsoleFunction"]
    n55["_infoConsoleFunction"]
    n56["_errorConsoleFunction"]
    n57["_warnConsoleFunction"]
    n58["_debugConsoleFunction"]
    n59["initJavaScriptBinding"]
    n60[["EscargotStarfishPlatform"]]
    n61[["EscargotStringView"]]
    n62[["DebuggerCallbackParam"]]
    n63[["Holder"]]
    n64["EscargotStarfishPlatform"]
    n65["customInfoLogger"]
    n66["customErrorLogger"]
    n67["markJSJobEnqueued"]
    n68["makeModuleLoadErrorString"]
    n69["loadModule"]
    n70["onLoadModule"]
    n71["didLoadModule"]
    n72["hostImportModuleDynamically"]
    n73["markJSJobFromAnotherThreadExists"]
    n74["staticallyInitScriptEngine"]
    n75["staticallyDestroyScriptEngine"]
    n76["scriptNull"]
    n77["scriptUndefined"]
    n78["scriptStringToScriptValue"]
    n79["isCallableScriptValue"]
    n80["isConstructibleScriptValue"]
    n81["isObjectScriptValue"]
    n82["isNumberScriptValue"]
    n83["isBooleanScriptValue"]
    n84["isNullOrUndefinedScriptValue"]
    n85["isStringScriptValue"]
    n86["scriptValueAsBoolean"]
    n87["scriptValueAsNumber"]
    n88["scriptValueAsObject"]
    n89["scriptValueToBoolean"]
    n90["scriptError"]
    n91["scriptEvalError"]
    n92["scriptRangeError"]
    n93["scriptReferenceError"]
    n94["scriptTypeError"]
    n95["scriptURIError"]
    n96["scriptReadIterableValue"]
    n97["defineNativeAccessorPropertyButNeedToGenerateJSFunction"]
    n98["loggingJSErrorInfo"]
    n99["fetchExecutionContext"]
    n100["fetchWebBase"]
    n101["fetchScriptBindingInstance"]
    n102["fetchWebView"]
    n103["fetchWindow"]
    n104["fetchDocument"]
    n105["fetchResponsibleDocument"]
    n106["fetchStaticStrings"]
    n107["EscargotStringView"]
    n108["length"]
    n109["charAt"]
    n110["bufferAccessData"]
    n111["isStringView"]
    n112["operator new"]
    n113["operator new[]"]
    n114["toBrowserString"]
    n114["toBrowserString"]
    n114["toBrowserString"]
    n114["toBrowserString"]
    n115["toJSString"]
    n116["toCalleeObject"]
    n117["errorOnConstructorFunction"]
    n118["ScriptWrappable"]
    n119["generateScriptObject"]
    n120["scriptValue"]
    n121["toScriptWrappable"]
    n121["toScriptWrappable"]
    n122["createScriptString"]
    n122["createScriptString"]
    n123["createScriptASCIIString"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n124["createScriptValue"]
    n125["dispatchErrorEventToWindow"]
    n126["createScriptFunction"]
    n126["createScriptFunction"]
    n127["createAttributeStringEventFunction"]
    n128["callScriptFunction"]
    n129["callConstructor"]
    n130["constructCustomElementConstructor"]
    n131["setScriptObjectProperty"]
    n131["setScriptObjectProperty"]
    n132["setScriptObjectPropertyThrowsException"]
    n132["setScriptObjectPropertyThrowsException"]
    n133["getScriptObjectProperty"]
    n133["getScriptObjectProperty"]
    n134["getScriptObjectPropertyThrowsException"]
    n134["getScriptObjectPropertyThrowsException"]
    n133["getScriptObjectProperty"]
    n135["getScriptObjectOwnProperty"]
    n136["callScriptFunctionWithError"]
    n137["callHandleEventFunction"]
    n138["callHandleNodeFilterFunction"]
    n139["jsGlobalObjectDefinePropertyIfNotExists"]
    n140["createCompressibleScriptString"]
    n141["initDebuggerIfNeeds"]
    n142["initializeScript"]
    n143["evaluateString"]
    n144["initModule"]
    n145["moduleRequests"]
    n146["executeModule"]
    n147["isExecutableModule"]
    n148["notifyDynamicLoadedModuleResult"]
    n148["notifyDynamicLoadedModuleResult"]
    n149["notifyDynamicLoadedModuleError"]
    n150["createScriptArrayBuffer"]
    n150["createScriptArrayBuffer"]
    n151["createScriptArrayBufferAdoptingVector"]
    n152["createEmptyInt8Array"]
    n153["createScriptUint8Array"]
    n154["createEmptyUint8Array"]
    n155["createEmptyInt16Array"]
    n156["createEmptyUint16Array"]
    n157["createEmptyInt32Array"]
    n158["createEmptyUint32Array"]
    n159["createEmptyFloat32Array"]
    n160["createEmptyFloat64Array"]
    n161["createEmptyUint8ClampedArray"]
    n162["createEmptyScriptObject"]
    n163["createScriptObject"]
    n163["createScriptObject"]
    n164["registerJavaScriptNativeInterface"]
    n165["unregisterJavaScriptNativeInterface"]
    n165["unregisterJavaScriptNativeInterface"]
    n166["parseJSON"]
    n167["parseJSONStringToScriptValueOrNull"]
    n168["parseDate"]
    n169["timeToUTCString"]
    n170["invokeTestStartFunction"]
    n171["throwScriptTypeError"]
    n172["throwScriptException"]
    n173["arrayBufferRawData"]
    n174["arrayBufferByteSize"]
    n175["arrayBufferViewRawData"]
    n176["arrayBufferViewByteSize"]
    n177["arrayBufferViewSize"]
    n178["createTypedArray"]
    n179["createArray"]
    n180["detachArrayBuffer"]
    n181["enqueueMicrotask"]
    n182["Holder"]
    n183["Promise"]
    n183["Promise"]
    n184["fulfill"]
    n185["reject"]
    n186["then"]
    n186["then"]
    n187["promiseResult"]
    n188["freezeArray"]
    n189["toPromise"]
    n190["AttributeEventFunction"]
    n191[["ValueRef"]]
    n192[["DOMTimeStamp"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n193[["Escargot"]]
    n194["staticallyInitScriptEngine"]
    n195["staticallyDestroyScriptEngine"]
    n196["scriptNull"]
    n197["scriptUndefined"]
    n198["scriptStringToScriptValue"]
    n199["isCallableScriptValue"]
    n200["isConstructibleScriptValue"]
    n201["isObjectScriptValue"]
    n202["isNumberScriptValue"]
    n203["isBooleanScriptValue"]
    n204["isNullOrUndefinedScriptValue"]
    n205["isStringScriptValue"]
    n206["scriptValueAsBoolean"]
    n207["scriptValueAsNumber"]
    n208["scriptValueAsObject"]
    n209["scriptError"]
    n210["scriptEvalError"]
    n211["scriptRangeError"]
    n212["scriptReferenceError"]
    n213["scriptTypeError"]
    n214["scriptURIError"]
    n215["scriptStringPrototype"]
    n216["scriptStringConstructor"]
    n217["scriptStringLength"]
    n218["scriptString__proto__"]
    n219["scriptReadIterableValueThrowsException"]
    n220["toJSString"]
    n221["toCalleeObject"]
    n222["errorOnConstructorFunction"]
    n223["createScriptString"]
    n223["createScriptString"]
    n224["createScriptASCIIString"]
    n224["createScriptASCIIString"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n225["createScriptValue"]
    n226["createScriptFunction"]
    n227["createAttributeStringEventFunction"]
    n228["callScriptFunction"]
    n229["callScriptFunctionWithError"]
    n230["callConstructor"]
    n231["constructCustomElementConstructor"]
    n232["callHandleEventFunction"]
    n233["callHandleNodeFilterFunction"]
    n234["executeModule"]
    n235["isExecutableModule"]
    n236["notifyDynamicLoadedModuleResult"]
    n237["notifyDynamicLoadedModuleError"]
    n238["setScriptObjectPropertyThrowsException"]
    n238["setScriptObjectPropertyThrowsException"]
    n239["getScriptObjectPropertyThrowsException"]
    n239["getScriptObjectPropertyThrowsException"]
    n240["jsGlobalObjectDefinePropertyIfNotExists"]
    n241["createScriptArrayBuffer"]
    n241["createScriptArrayBuffer"]
    n242["createScriptArrayBufferAdoptingVector"]
    n243["createScriptUint8Array"]
    n244["createEmptyInt8Array"]
    n245["createEmptyUint8Array"]
    n246["createEmptyInt16Array"]
    n247["createEmptyUint16Array"]
    n248["createEmptyUint8ClampedArray"]
    n249["createEmptyUint32Array"]
    n250["createEmptyInt32Array"]
    n251["createEmptyFloat32Array"]
    n252["createEmptyFloat64Array"]
    n253["createEmptyScriptObject"]
    n254["createScriptObject"]
    n254["createScriptObject"]
    n255["registerJavaScriptNativeInterface"]
    n256["unregisterJavaScriptNativeInterface"]
    n256["unregisterJavaScriptNativeInterface"]
    n257["parseJSON"]
    n258["parseJSONStringToScriptValueOrNull"]
    n259["parseDate"]
    n260["timeToUTCString"]
    n261["throwScriptTypeError"]
    n262["throwScriptException"]
    n263["arrayBufferRawData"]
    n264["arrayBufferViewRawData"]
    n265["arrayBufferByteSize"]
    n266["arrayBufferViewSize"]
    n267["arrayBufferViewByteSize"]
    n268["detachArrayBuffer"]
    n269["enqueueMicrotask"]
    n270["invokeTestStartFunction"]
    n271["ScriptWrappable"]
    n272["scriptObject"]
    n273["giveUpScriptValue"]
    n274["isGivenUpScriptValue"]
    n275["generateScriptObject"]
    n276["scriptValue"]
    n277["postInit"]
    n278["toSerializable"]
    n279["toTransferable"]
    n280["toScriptWrappable"]
    n280["toScriptWrappable"]
    n281["init"]
    n282["scriptBindingInstance"]
    n283["target"]
    n284["fulfill"]
    n285["reject"]
    n286["then"]
    n286["then"]
    n287["promiseResult"]
    n276["scriptValue"]
    n288["onSettled"]
    n289["setOnSettled"]
    n290["isSettled"]
    n291["toPromise"]
    n292["freezeArray"]
    n293[["TimeOutData"]]
    n294[["ScreenShotTimeOutData"]]
    n295["starfishRecordTestFailure"]
    n296["customExit"]
    n297["TimeOutData"]
    n298["timeoutHandler"]
    n299["setTimeoutWindowFunction"]
    n300["setIntervalWindowFunction"]
    n301["requestAnimationFrameHandler"]
    n302["postMessageWindowFunction"]
    n303["requestAnimationFrameWindowFunction"]
    n304["debugPauseFunction"]
    n305["debugResumeFunction"]
    n306["networkEnableFunction"]
    n307["networkDisableFunction"]
    n308["webSecurityEnableFunction"]
    n309["webSecurityDisableFunction"]
    n310["isPixelTestFunction"]
    n311["renderingCountFunction"]
    n312["screenShotTimeoutHandler"]
    n313["screenShotFunction"]
    n314["screenShotRelativePathFunction"]
    n315["forceDisableOnloadCaptureFunction"]
    n316["getXYWHFunction"]
    n317["simulateClickFunction"]
    n318["simulateMouseDownFunction"]
    n319["simulateMouseUpFunction"]
    n320["simulateMouseMoveFunction"]
    n321["simulateTouchStartFunction"]
    n322["simulateTouchMoveFunction"]
    n323["simulateTouchEndFunction"]
    n324["simulateTouchCancelFunction"]
    n325["simulateVisibilitychangeFunction"]
    n326["getLastTTSTextFunction"]
    n327["setTTSAccessibilityModeFunction"]
    n328["getA11yFocusedElementIdFunction"]
    n329["testAssertFunction"]
    n330["testEndFunction"]
    n331["wptTestEndFunction"]
    n332["testImgDiffFunction"]
    n333["readPNGPixelData"]
    n334["getPixelColorFunction"]
    n335["checkPixelColorFunction"]
    n336["checkPixelColorsFunction"]
    n337["getImageSizeFunction"]
    n338["postInit"]
    n339[["TimeOutData"]]
    n340["TimeOutData"]
    n341["timeoutHandler"]
    n342["setTimeoutWorkerGlobalScopeFunction"]
    n343["setIntervalWorkerGlobalScopeFunction"]
    n344[["FontFaceReferenceHolder"]]
    n345[["NativeGradientCairo"]]
    n346[["NativePatternCairo"]]
    n347[["CanvasCairo"]]
    n348[["CanvasAttachableNativeImageCairo"]]
    n349["FontFaceReferenceHolder"]
    n350["addToCairoFontFace"]
    n351["removeFontFaceReference"]
    n352["NativeGradientCairo"]
    n352["NativeGradientCairo"]
    n352["NativeGradientCairo"]
    n353["~NativeGradientCairo"]
    n354["addColorStop"]
    n355["isZeroSize"]
    n356["pattern"]
    n357["initialize"]
    n358["applyGradientMatrixInternal"]
    n359["initializePatternToLinearGradient"]
    n360["initializePatternToRadialGradient"]
    n361["create"]
    n361["create"]
    n361["create"]
    n362["NativePatternCairo"]
    n363["~NativePatternCairo"]
    n364["pattern"]
    n365["applyTransform"]
    n366["initialize"]
    n361["create"]
    n367["initFromBuffer"]
    n368["initFromNativeImageData"]
    n369["init"]
    n370["applyCanvasFillStrokeSourceIfNeeds"]
    n371["CanvasCairo"]
    n371["CanvasCairo"]
    n371["CanvasCairo"]
    n372["~CanvasCairo"]
    n373["checkError"]
    n374["clearColor"]
    n375["flush"]
    n376["save"]
    n377["restore"]
    n378["scale"]
    n378["scale"]
    n379["rotate"]
    n379["rotate"]
    n380["translate"]
    n380["translate"]
    n381["beginLayer"]
    n382["endLayer"]
    n383["clip"]
    n384["clipPath"]
    n385["pixelSnappedClip"]
    n386["unsetDevicePixelRatio"]
    n387["applyDevicePixelRatio"]
    n388["setFillColor"]
    n389["setFillSource"]
    n390["fillSource"]
    n391["setStrokeColor"]
    n392["setStrokeSource"]
    n393["strokeSource"]
    n394["setGlobalAlpha"]
    n395["globalAlpha"]
    n396["setCompositeOperator"]
    n397["compositeOperator"]
    n398["blendMode"]
    n399["setVisible"]
    n400["setNonInvertableCTM"]
    n401["hasNonInvertableCTM"]
    n402["setPathTransformMatrix"]
    n403["pathTransformMatrix"]
    n404["setOriginalFontStr"]
    n405["setCanvasWebFontState"]
    n406 -->|calls| n407
    n406 -->|calls| n408
    n406 -->|calls| n409
    n406 -->|calls| n410
    n406 -->|calls| n411
    n406 -->|calls| n412
    n406 -->|calls| n413
    n406 -->|calls| n414
    n406 -->|calls| n415
    n406 -->|calls| n416
    n406 -->|calls| n417
    n406 -->|calls| n418
    n406 -->|calls| n419
    n420 -->|calls| n421
    n420 -->|calls| n422
    n420 -->|calls| n423
    n420 -->|calls| n424
    n420 -->|calls| n425
    n420 -->|calls| n426
    n420 -->|calls| n427
    n428 -->|calls| n429
    n428 -->|calls| n430
    n428 -->|calls| n428
    n428 -->|calls| n431
    n428 -->|calls| n432
    n413 -->|calls| n433
    n413 -->|calls| n434
    n413 -->|calls| n435
    n436 -->|calls| n437
    n436 -->|calls| n438
    n436 -->|calls| n412
    n436 -->|calls| n439
    n440 -->|calls| n437
    n440 -->|calls| n438
    n440 -->|calls| n441
    n440 -->|calls| n439
    n442 -->|calls| n437
    n442 -->|calls| n438
    n443 -->|calls| n444
    n443 -->|calls| n445
    n443 -->|calls| n446
    n447 -->|calls| n408
    n447 -->|calls| n445
    n447 -->|calls| n448
    n447 -->|calls| n449
    n447 -->|calls| n450
    n447 -->|calls| n451
    n447 -->|calls| n452
    n447 -->|calls| n453
    n447 -->|calls| n454
    n455 -->|calls| n456
    n455 -->|calls| n415
    n455 -->|calls| n416
    n457 -->|calls| n458
    n3 -->|calls| n459
    n9 -->|calls| n451
    n9 -->|calls| n417
    n13 -->|calls| n417
    n10 -->|calls| n417
    n11 -->|calls| n451
    n11 -->|calls| n417
    n14 -->|calls| n422
    n15 -->|calls| n460
    n16 -->|calls| n461
    n17 -->|calls| n451
    n18 -->|calls| n451
    n19 -->|calls| n462
    n19 -->|calls| n463
    n20 -->|calls| n464
    n20 -->|calls| n465
    n466 -->|calls| n467
    n466 -->|calls| n468
    n466 -->|calls| n469
    n466 -->|calls| n470
    n466 -->|calls| n471
```

### Module: tool

```mermaid
graph TD
    n0[["SetupError"]]
    n1["require_tool"]
    n2["check_abidw_version"]
    n3["git"]
    n4["resolve_ref"]
    n5["tracked_paths_at_ref"]
    n6["export_ref_tree"]
    n7["export_working_tree"]
    n8["strip_comments"]
    n9["find_matching_brace"]
    n10["parse_contract_surface"]
    n11["extract_wrapper_names"]
    n12["compile_shim"]
    n13["assert_no_include_leak"]
    n14["dump_abi"]
    n15["find_decl"]
    n16["extract_class_fp"]
    n17["extract_struct_fp"]
    n18["extract_enum_fp"]
    n19["build_fingerprint"]
    n20["assert_coverage_sane"]
    n21["_appendable_struct"]
    n22["classify_fingerprints"]
    n23["i2_wrapper_delta"]
    n24["check_i1_current_repo"]
    n25["check_shim_covers_all_headers"]
    n26["check_wrapper_assert_count_matches"]
    n27["run_abidiff"]
    n28["compare_trees"]
    n29["added_waiver_lines"]
    n30["unwaived_breaking_items"]
    n31["read_abi_epoch"]
    n32["abi_epoch_policy_errors"]
    n33["print_coverage"]
    n34["print_verdict"]
    n35["base_predates_checker"]
    n36("bootstrap_smoke_test")
    n37["compare"]
    n38["resolve_base"]
    n39["_mutate"]
    n40["_append"]
    n41["fixture"]
    n42["decorator"]
    n43["_fixture_unchanged"]
    n44["_fixture_reorder"]
    n45["_fixture_removed"]
    n46["_fixture_appended"]
    n47["_fixture_return_type"]
    n48["_fixture_const"]
    n49["_fixture_struct_insert"]
    n50["_fixture_enum_renumber"]
    n51["_fixture_ttsmode"]
    n52["_fixture_wrapper_rename_header"]
    n53["_fixture_proctable_mismatch"]
    n54["_fixture_new_interface"]
    n55["run_verify_checker"]
    n56["main"]
    n57[["WorkerRunner"]]
    n58["__init__"]
    n59["run"]
    n60["terminate"]
    n61[["WptServerError"]]
    n62["_port_open"]
    n63["_http_ok"]
    n64["_wait_ports_free"]
    n65["_port_owner_pid"]
    n66["_reclaim_ports"]
    n67["wpt_serve"]
    n68["_terminate"]
    n69["_main"]
    n70["run"]
    n71["check_error"]
    n72["print_output"]
    n73["file_len"]
    n74["print_table"]
    n75("run_test")
    n76("internal_test")
    n77("dom_conformance_test")
    n78["vendor_test_blink"]
    n79["vendor_test_gecko"]
    n80["vendor_test_webkit"]
    n81["run_vendor_test_khronos"]
    n82["vendor_test_khronos"]
    n83["vendor_test_khronos2"]
    n84["vendor_test_khronossdk"]
    n85("vendor_test")
    n86["wpt_css_css21"]
    n87["wpt_css_backgrounds"]
    n88["wpt_css_color"]
    n89["wpt_css_flexbox"]
    n90["wpt_css_transforms"]
    n91["wpt_css_variables"]
    n92["wpt_mediaqueries"]
    n93["wpt_selectors"]
    n94["wpt_css_all"]
    n95["wpt_all"]
    n96["_wpt_serve_run"]
    n97["wpt_serve_testharness_css"]
    n98["wpt_serve_testharness_dom"]
    n99["wpt_serve_testharness_canvas"]
    n100["wpt_serve_testharness_html"]
    n101["wpt_serve_testharness_xhr"]
    n102["wpt_serve_testharness_fetch"]
    n103["wpt_serve_testharness_worker"]
    n104["wpt_serve_testharness_serviceworker"]
    n105["wpt_serve_testharness_idb"]
    n106["wpt_serve_testharness_websocket"]
    n107["wpt_serve_testharness_webrtc"]
    n108["wpt_serve_testharness_intersection_observer"]
    n109["wpt_serve_testharness_svg"]
    n110["wpt_serve_testharness_custom_elements"]
    n111["wpt_serve_testharness_fullscreen"]
    n112["wpt_serve_testharness_others"]
    n113["wpt_serve_testharness"]
    n114["_wpt_manifest_run"]
    n115["wpt_serve_reftest"]
    n116["wpt_serve_crashtest"]
    n117("bidi_test")
    n118["reftest_all"]
    n119("test_all")
    n120["print_columns"]
    n121["find_impl_so"]
    n122["write_version"]
    n123["reset_mount_state"]
    n124["ensure_clean_start"]
    n125["setup_updated_impl_selected"]
    n126["setup_lower_version_ignored"]
    n127["setup_unloadable_file_falls_back"]
    n128["build_fake_updated_impl"]
    n129["setup_incompatible_abi_epoch_falls_back"]
    n130["setup_missing_abi_epoch_falls_back"]
    n131["setup_missing_symbol_falls_back"]
    n132["run_starfish"]
    n133["run_scenario"]
    n134["main"]
    n135["write_version"]
    n136["reset_mount_state"]
    n137["ensure_clean_start"]
    n138["find_worker_impl"]
    n139["setup_updated_impl_selected"]
    n140["build_fake_updated_impl"]
    n141["setup_incompatible_abi_epoch"]
    n142["setup_missing_abi_epoch"]
    n143["setup_missing_worker_symbol"]
    n144["run_worker"]
    n145["run_scenario"]
    n146["main"]
    n147["load_verdicts"]
    n148["annotate_file"]
    n149["main"]
    n150["parse_res"]
    n151["probe"]
    n152["audit"]
    n153["classify"]
    n154["build_basename_index"]
    n155["_score"]
    n156["_in"]
    n157["_candidate_paths"]
    n158["remap_candidate"]
    n159["main"]
    n160["do"]
    n161["recover"]
    n162["report"]
    n163["list_name"]
    n164["write_list"]
    n165["main"]
    n166["_isolated_storage_dir"]
    n167["_manifest_path"]
    n168["ensure_manifest"]
    n169["load_manifest"]
    n170["ensure_imgdiff"]
    n171["_find_node"]
    n172["resolve_references"]
    n173["_ref_to_url"]
    n174["url_to_test_path"]
    n175["_screenshot"]
    n176["_images_differ"]
    n177["run_reftest"]
    n178["isolated_storage_dir"]
    n179["_storage_dir_scope"]
    n180["reason_category"]
    n181["read_res"]
    n182["collect"]
    n183["_is_connect_refused_on_navigation"]
    n184["run_one"]
    n185["run_one_reftest"]
    n186["_with_crashtest_marker"]
    n187["run_one_crashtest"]
    n188["_is_crash_reason"]
    n189["_tail_lines"]
    n190["load_done"]
    n191["run_all"]
    n192["task"]
    n193["main"]
    n194["go"]
    n195["wpt_revision"]
    n196["git"]
    n197["read_targets"]
    n198["_collect_urls"]
    n199["enumerate_tests"]
    n200("run_test")
    n201["verdict"]
    n202["score"]
    n203["run_all"]
    n204["build_tree"]
    n205["_accumulate"]
    n206["render_node"]
    n207["render_html"]
    n208["_summarize"]
    n209["extract_metrics"]
    n210["main"]
    n211["go"]
    n1 -->|calls| n212
    n1 -->|calls| n0
    n2 -->|calls| n213
    n2 -->|calls| n214
    n2 -->|calls| n1
    n2 -->|calls| n215
    n2 -->|calls| n216
    n2 -->|calls| n217
    n2 -->|calls| n0
    n2 -->|calls| n218
    n3 -->|calls| n214
    n3 -->|calls| n219
    n3 -->|calls| n0
    n3 -->|calls| n220
    n3 -->|calls| n218
    n3 -->|calls| n213
    n4 -->|calls| n218
    n4 -->|calls| n3
    n5 -->|calls| n3
    n5 -->|calls| n221
    n6 -->|calls| n219
    n6 -->|calls| n5
    n6 -->|calls| n222
    n6 -->|calls| n0
    n6 -->|calls| n3
    n6 -->|calls| n220
    n6 -->|calls| n223
    n6 -->|calls| n224
    n6 -->|calls| n225
    n6 -->|calls| n226
    n7 -->|calls| n227
    n7 -->|calls| n228
    n7 -->|calls| n220
    n7 -->|calls| n229
    n7 -->|calls| n222
    n7 -->|calls| n230
    n7 -->|calls| n0
    n7 -->|calls| n223
    n7 -->|calls| n224
    n7 -->|calls| n231
    n8 -->|calls| n232
    n9 -->|calls| n233
    n9 -->|calls| n234
    n9 -->|calls| n0
    n10 -->|calls| n235
    n10 -->|calls| n220
    n10 -->|calls| n227
    n10 -->|calls| n228
    n10 -->|calls| n229
    n10 -->|calls| n8
    n10 -->|calls| n236
    n10 -->|calls| n225
    n10 -->|calls| n237
    n10 -->|calls| n9
    n10 -->|calls| n238
    n10 -->|calls| n234
    n10 -->|calls| n239
    n10 -->|calls| n217
    n10 -->|calls| n240
    n10 -->|calls| n241
    n11 -->|calls| n235
    n11 -->|calls| n220
    n11 -->|calls| n228
    n11 -->|calls| n229
    n11 -->|calls| n236
    n11 -->|calls| n225
    n11 -->|calls| n241
    n11 -->|calls| n239
    n12 -->|calls| n220
    n12 -->|calls| n214
    n12 -->|calls| n0
    n12 -->|calls| n213
    n12 -->|calls| n13
    n13 -->|calls| n230
    n13 -->|calls| n242
    n13 -->|calls| n236
    n13 -->|calls| n225
    n13 -->|calls| n243
    n13 -->|calls| n244
    n13 -->|calls| n245
    n13 -->|calls| n220
    n13 -->|calls| n246
    n13 -->|calls| n0
    n14 -->|calls| n214
    n14 -->|calls| n0
    n14 -->|calls| n213
    n15 -->|calls| n247
    n15 -->|calls| n248
    n15 -->|calls| n234
    n15 -->|calls| n0
    n16 -->|calls| n247
    n16 -->|calls| n249
    n16 -->|calls| n248
    n16 -->|calls| n250
    n16 -->|calls| n239
    n16 -->|calls| n216
    n16 -->|calls| n234
    n17 -->|calls| n239
    n17 -->|calls| n249
    n17 -->|calls| n248
    n18 -->|calls| n248
    n18 -->|calls| n239
    n18 -->|calls| n249
    n19 -->|calls| n251
    n19 -->|calls| n252
    n19 -->|calls| n15
    n19 -->|calls| n222
    n19 -->|calls| n16
    n19 -->|calls| n17
    n19 -->|calls| n18
    n20 -->|calls| n222
    n20 -->|calls| n253
    n20 -->|calls| n248
    n20 -->|calls| n0
    n20 -->|calls| n220
    n21 -->|calls| n229
    n22 -->|calls| n222
    n22 -->|calls| n253
    n22 -->|calls| n248
    n22 -->|calls| n254
    n22 -->|calls| n21
    n22 -->|calls| n255
    n23 -->|calls| n11
    n23 -->|calls| n227
    n23 -->|calls| n222
    n24 -->|calls| n11
    n24 -->|calls| n235
    n24 -->|calls| n236
    n24 -->|calls| n225
    n24 -->|calls| n220
    n24 -->|calls| n241
    n24 -->|calls| n239
    n24 -->|calls| n227
    n24 -->|calls| n0
    n25 -->|calls| n220
    n25 -->|calls| n236
    n25 -->|calls| n225
    n25 -->|calls| n228
    n25 -->|calls| n229
    n25 -->|calls| n0
    n26 -->|calls| n11
    n26 -->|calls| n236
    n26 -->|calls| n225
    n26 -->|calls| n220
    n26 -->|calls| n221
    n26 -->|calls| n246
    n26 -->|calls| n256
    n26 -->|calls| n234
    n26 -->|calls| n239
    n26 -->|calls| n0
    n27 -->|calls| n214
    n27 -->|calls| n213
    n27 -->|calls| n0
    n27 -->|calls| n257
    n28 -->|calls| n25
    n28 -->|calls| n26
    n28 -->|calls| n10
    n28 -->|calls| n12
    n28 -->|calls| n220
    n28 -->|calls| n14
    n28 -->|calls| n19
    n28 -->|calls| n20
    n28 -->|calls| n22
    n28 -->|calls| n27
    n28 -->|calls| n0
    n28 -->|calls| n23
    n28 -->|calls| n258
    n29 -->|calls| n3
    n29 -->|calls| n220
    n29 -->|calls| n221
    n29 -->|calls| n246
    n30 -->|calls| n29
    n31 -->|calls| n220
    n31 -->|calls| n230
    n31 -->|calls| n239
    n31 -->|calls| n236
    n31 -->|calls| n225
    n31 -->|calls| n234
    n31 -->|calls| n0
    n31 -->|calls| n216
    n32 -->|calls| n31
    n33 -->|calls| n259
    n33 -->|calls| n227
    n33 -->|calls| n253
    n33 -->|calls| n229
    n33 -->|calls| n234
    n33 -->|calls| n220
    n34 -->|calls| n259
    n35 -->|calls| n5
    n36 -->|calls| n259
    n36 -->|calls| n260
    n36 -->|calls| n220
    n36 -->|calls| n223
    n36 -->|calls| n7
    n36 -->|calls| n25
    n36 -->|calls| n26
    n36 -->|calls| n10
    n36 -->|calls| n12
    n36 -->|calls| n14
    n36 -->|calls| n19
    n36 -->|calls| n20
    n36 -->|calls| n33
    n37 -->|calls| n2
    n37 -->|calls| n1
    n37 -->|calls| n35
    n37 -->|calls| n36
    n37 -->|calls| n24
    n37 -->|calls| n260
    n37 -->|calls| n220
    n37 -->|calls| n223
    n37 -->|calls| n6
    n37 -->|calls| n7
    n37 -->|calls| n28
    n37 -->|calls| n32
    n37 -->|calls| n33
    n37 -->|calls| n34
    n37 -->|calls| n259
    n37 -->|calls| n30
    n37 -->|calls| n234
    n38 -->|calls| n4
    n38 -->|calls| n0
    n39 -->|calls| n236
    n39 -->|calls| n225
    n39 -->|calls| n0
    n39 -->|calls| n226
    n39 -->|calls| n242
    n40 -->|calls| n225
    n40 -->|calls| n226
    n42 -->|calls| n222
    n44 -->|calls| n220
    n44 -->|calls| n39
    n45 -->|calls| n220
    n45 -->|calls| n39
    n46 -->|calls| n220
    n46 -->|calls| n39
    n47 -->|calls| n220
    n47 -->|calls| n39
    n48 -->|calls| n220
    n48 -->|calls| n39
    n49 -->|calls| n220
    n49 -->|calls| n39
    n50 -->|calls| n220
    n50 -->|calls| n39
    n51 -->|calls| n220
    n51 -->|calls| n39
    n52 -->|calls| n220
    n52 -->|calls| n39
    n53 -->|calls| n220
    n53 -->|calls| n39
    n54 -->|calls| n220
    n54 -->|calls| n39
    n54 -->|calls| n40
    n55 -->|calls| n1
    n55 -->|calls| n2
    n55 -->|calls| n260
    n55 -->|calls| n220
    n55 -->|calls| n223
    n55 -->|calls| n7
    n55 -->|calls| n261
    n55 -->|calls| n28
    n55 -->|calls| n222
    n55 -->|calls| n259
    n55 -->|calls| n262
    n55 -->|calls| n225
    n55 -->|calls| n226
    n55 -->|calls| n257
    n55 -->|calls| n32
    n55 -->|calls| n214
    n55 -->|calls| n14
    n55 -->|calls| n10
    n55 -->|calls| n19
    n55 -->|calls| n20
    n55 -->|calls| n234
    n56 -->|calls| n263
    n56 -->|calls| n264
    n56 -->|calls| n265
    n56 -->|calls| n55
    n56 -->|calls| n38
    n56 -->|calls| n37
    n56 -->|calls| n259
    n70 -->|calls| n266
    n71 -->|calls| n267
    n71 -->|calls| n259
    n71 -->|calls| n72
    n71 -->|calls| n268
    n72 -->|calls| n236
    n72 -->|calls| n259
    n72 -->|calls| n213
    n59 -->|calls| n259
    n59 -->|calls| n222
    n59 -->|calls| n266
    n59 -->|calls| n269
    n60 -->|calls| n259
    n60 -->|calls| n270
    n60 -->|calls| n271
    n60 -->|calls| n272
    n60 -->|calls| n267
    n73 -->|calls| n225
    n73 -->|calls| n273
    n73 -->|calls| n246
    n74 -->|calls| n259
    n74 -->|calls| n274
    n75 -->|calls| n74
    n75 -->|calls| n275
    n75 -->|calls| n73
    n75 -->|calls| n276
    n75 -->|calls| n259
    n75 -->|calls| n268
    n76 -->|calls| n75
    n76 -->|calls| n277
    n77 -->|calls| n75
    n78 -->|calls| n75
```

