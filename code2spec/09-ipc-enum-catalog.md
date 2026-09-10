# IPC Constants and ENUM Catalog

> **Relevant source files**
>
> - [inc/LWEWebView.h](src:inc/LWEWebView.h)
> - [inc/LWEWorker.h](src:inc/LWEWorker.h)
> - [inc/PlatformIntegrationData.h](src:inc/PlatformIntegrationData.h)
> - [src/core/dom/parser/HTMLConstructionSite.h](src:src/core/dom/parser/HTMLConstructionSite.h)
> - [src/core/dom/parser/HTMLEntityParser.cpp](src:src/core/dom/parser/HTMLEntityParser.cpp)
> - [src/core/dom/parser/HTMLEntitySearch.h](src:src/core/dom/parser/HTMLEntitySearch.h)
> - [src/core/dom/parser/HTMLFormattingElementList.h](src:src/core/dom/parser/HTMLFormattingElementList.h)
> - [src/core/dom/parser/HTMLParserIdioms.h](src:src/core/dom/parser/HTMLParserIdioms.h)
> - [src/core/dom/parser/HTMLToken.h](src:src/core/dom/parser/HTMLToken.h)
> - [src/core/dom/parser/HTMLTokenizer.h](src:src/core/dom/parser/HTMLTokenizer.h)

> **Generated**: 2026-08-27  
> **Project**: Starfish  
> **Source Files**: 1,815 files analyzed (AST export); extraction entries: 169 enums, 480 constants, 34 IPC records

This catalog is generated from the W1 LLM-extraction results (`.analysis/llm-extraction/llm-{enum,constant,ipc}-results.json`), which were produced from the tree-sitter AST export and verified against source. Entries without code evidence are omitted.

---

## ENUM Definitions

169 enum definitions were extracted.

| ENUM Name | Type | Values | Source |
|-----------|------|--------|--------|
| `Archiver.State` | cpp_enum | BeforeStart, Started, Closed | [`State`](src:src/core/util/Archiver.cpp#L58) |
| `AttributeName.MatchType` | cpp_enum | MatchName, MatchNS, MatchAll | [`MatchType`](src:src/core/util/AttributeName.h#L28) |
| `BorderData.InitiallyZero` | cpp_enum | InitiallyZeroValue | [`InitiallyZero`](src:src/core/style/BorderData.h#L36) |
| `CSSAngle.Kind` | cpp_enum | UNSPECIFIED, DEG, GRAD, RAD, TURN | [`Kind`](src:src/core/style/CSSAngle.h#L32) |
| `CSSGradientValue.SideOrConer` | cpp_enum | toLeft, toRight, toTop, toBottom | [`SideOrConer`](src:src/core/style/CSSGradientValue.h#L32) |
| `CSSLength.Kind` | cpp_enum | PX, EM, EX, INCH, CM, MM, PT, PC, VW, VH, VMIN, VMAX … (3 more) | [`Kind`](src:src/core/style/CSSLength.h#L33) |
| `CSSNumericValue.CSSNumericBaseType` | cpp_enum | Length, Angle, Time, Frequency, Resolution, Flex, Percent, Null | [`CSSNumericBaseType`](src:src/core/style/CSSNumericValue.h#L33) |
| `CSSParser.AllowedRulesType` | cpp_enum | AllowCharsetRules, AllowImportRules, AllowNamespaceRules, RegularRules, KeyframeRules, ApplyRules, NoRules | [`AllowedRulesType`](src:src/core/style/CSSParser.h#L1769) |
| `CSSParser.CompoundSelectorFlags` | cpp_enum | HasPseudoElementForRightmostCompound, HasContentPseudoElement | [`CompoundSelectorFlags`](src:src/core/style/CSSParser.cpp#L1680) |
| `CSSParser.LogicOp` | cpp_enum | And, Or, Not | [`LogicOp`](src:src/core/style/CSSParser.h#L1757) |
| `CSSParser.MediaFeature` | cpp_enum | MediaFeatureNone, MediaFeatureAspectRatio, MediaFeatureMinWidth, MediaFeatureDeviceAspectRatio, MediaFeatureMinDeviceWidth | [`MediaFeature`](src:src/core/style/CSSParser.h#L1648) |
| `CSSParser.MediaQueryParserType` | cpp_enum | MediaQuerySetParser, MediaConditionParser | [`MediaQueryParserType`](src:src/core/style/CSSParser.h#L1929) |
| `CSSParser.NumericSign` | cpp_enum | NoSign, PlusSign, MinusSign | [`NumericSign`](src:src/core/style/CSSParser.h#L1751) |
| `CSSParser.ParseResult` | cpp_enum | Consumed, ErrorFounded, Failed | [`ParseResult`](src:src/core/style/CSSParser.h#L1786) |
| `CSSParser.RuleListType` | cpp_enum | TopLevelRuleList, RegularRuleList, KeyframesRuleList | [`RuleListType`](src:src/core/style/CSSParser.h#L1784) |
| `CSSParser.TruthOp` | cpp_enum | False, True, Paren | [`TruthOp`](src:src/core/style/CSSParser.h#L1763) |
| `CSSRule.Type` | cpp_enum | STYLE_RULE, CHARSET_RULE, IMPORT_RULE, MEDIA_RULE, FONT_FACE_RULE, PAGE_RULE, KEYFRAMES_RULE, KEYFRAME_RULE, MARGIN_RULE, NAMESPACE_RULE, COUNTER_STYLE_RULE, SUPPORTS_RULE … (4 more) | [`Type`](src:src/core/style/CSSRule.h#L36) |
| `CSSStyleValuePair.ValueKind` | cpp_enum | Initial, Inherit, Unset, Length, Percentage, Auto, None, Number, Int32, Angle, Time, Normal … (29 more) | [`ValueKind`](src:src/core/style/Style.h#L1052) |
| `CSSTime.Kind` | cpp_enum | S, MS | [`Kind`](src:src/core/style/CSSTime.h#L30) |
| `CSSTransformFunction.Kind` | cpp_enum | None, Matrix, Matrix3D, Translate, Translate3D, TranslateX, TranslateY, TranslateZ, Scale, Scale3D, ScaleX, ScaleY … (7 more) | [`Kind`](src:src/core/style/Style.h#L915) |
| `CSSVariableSyntaxTreeBuilder.TokenType` | cpp_enum | VARIABLE, VARIABLEBLOCKOPEN, VARIABLEBLOCKCLOSE, COMMA, RAWVALUE, EMPTY, END | [`TokenType`](src:src/core/style/CSSVariableSyntaxTreeBuilder.cpp#L56) |
| `Canvas.CanvasSurfaceFlag` | cpp_enum | PlainElement, PreferEGLImage, PreferUnitedTexture, PreferRetainCPUBufferWhenUnmap | [`CanvasSurfaceFlag`](src:src/core/modules/canvas/Canvas.h#L161) |
| `CompositorGL.Command` | cpp_enum | MoveTo, LineTo, ArcNegative | [`Command`](src:src/platform/canvas/CompositorGL.cpp#L477) |
| `ComputedStyle.ComputedStyleDamage` | cpp_enum | ComputedStyleDamageNone, ComputedStyleDamageInherited, ComputedStyleDamageRebuildFrame, ComputedStyleDamageLayout, ComputedStyleDamageEstablishesStackingContext, ComputedStyleDamageComputeStackingContextProperties, ComputedStyleDamagePainting, ComputedStyleDamageComposite, ComputedStyleDamageAnimation, ComputedStyleDamageSVGViewportContent | [`ComputedStyleDamage`](src:src/core/style/ComputedStyle.h#L56) |
| `ComputedStyle.KeyKind` | cpp_enum | Order, ZIndex, FlexGrow, FlexShrink, Opacity, Border, BorderBlockStart, BorderBlockEnd, BorderInlineStart, BorderInlineEnd, BoxDecorationBreak, BoxShadow … (8 more) | [`KeyKind`](src:src/core/style/ComputedStyle.h#L91) |
| `ContentData.ContentType` | cpp_enum | None, Text, Image, Counter, Quote | [`ContentType`](src:src/core/style/ContentData.h#L132) |
| `CounterStyle.System` | cpp_enum | NoneSystem, CyclicSystem, FixedSystem, SymbolicSystem, AlphabeticSystem, NumericSystem, AdditiveSystem, ExtendsSystem | [`System`](src:src/core/style/CounterStyle.h#L29) |
| `DOMException.Code` | cpp_enum | DOM_EXCEPTION, INDEX_SIZE_ERR, HIERARCHY_REQUEST_ERR, WRONG_DOCUMENT_ERR, INVALID_CHARACTER_ERR, NO_MODIFICATION_ALLOWED_ERR, NOT_FOUND_ERR, NOT_SUPPORTED_ERR, INUSE_ATTRIBUTE_ERR, INVALID_STATE_ERR, SYNTAX_ERR, INVALID_MODIFICATION_ERR … (8 more) | [`Code`](src:src/core/dom/DOMException.h#L29) |
| `DemuxerSource.SeekWhence` | cpp_enum | SeekWhenceSet, SeekWhenceCurrent, SeekWhenceEnd, SeekWhenceLookSize | [`SeekWhence`](src:src/platform/multimedia/DemuxerSource.h#L26) |
| `Document.CompatibilityMode` | cpp_enum | QuirksMode, LimitedQuirksMode, NoQuirksMode, NoQuirksModeForce | [`CompatibilityMode`](src:src/core/dom/Document.h#L122) |
| `Document.DocumentReadyState` | cpp_enum | DocumentReadyStateLoading, DocumentReadyStateInteractive, DocumentReadyStateComplete | [`DocumentReadyState`](src:src/core/dom/Document.h#L85) |
| `Document.VisibilityState` | cpp_enum | VisibilityStateHidden, VisibilityStateVisible, VisibilityStatePrerender, VisibilityStateUnloaded | [`VisibilityState`](src:src/core/dom/Document.h#L78) |
| `EventSource.ReadyState` | cpp_enum | CONNECTING, OPEN, CLOSED | [`ReadyState`](src:src/core/page/EventSource.h#L80) |
| `EventTarget.DefaultArgumentSequence` | cpp_enum | DEFAULT_ARG_EVENT, DEFAULT_ARG_SIZE | [`DefaultArgumentSequence`](src:src/core/dom/EventTarget.cpp#L62) |
| `EventTarget.ErrorArgumentSequence` | cpp_enum | ERROR_ARG_MESSAGE, ERROR_ARG_SRC, ERROR_ARG_LINENO, ERROR_ARG_COLNO, ERROR_ARG_ERROR, ERROR_ARG_SIZE | [`ErrorArgumentSequence`](src:src/core/dom/EventTarget.cpp#L53) |
| `EventTarget.GlobalPointingEventKind` | cpp_enum | GlobalPointingEventKindDown, GlobalPointingEventKindUp, GlobalPointingEventKindMove | [`GlobalPointingEventKind`](src:src/core/dom/EventTarget.h#L239) |
| `Filter.FixedSourcePlace` | cpp_enum | SourceGraphic | [`FixedSourcePlace`](src:src/core/modules/canvas/filter/Filter.h#L96) |
| `FlexBasisData.Type` | cpp_enum | Auto, Content, Width | [`Type`](src:src/core/style/FlexBasisData.h#L28) |
| `Font.FontKerningValue` | cpp_enum | FontKerningAutoValue, FontKerningNormalValue, FontKerningNoneValue | [`FontKerningValue`](src:src/core/modules/canvas/font/Font.h#L43) |
| `Font.FontStyle` | cpp_enum | FontStyleNormal, FontStyleItalic, FontStyleOblique | [`FontStyle`](src:src/core/modules/canvas/font/Font.h#L31) |
| `Font.FontWeight` | cpp_enum | FontWeightStart, FontWeightNormal, FontWeightEnd | [`FontWeight`](src:src/core/modules/canvas/font/Font.h#L37) |
| `FontFaceSrcData.Format` | cpp_enum | Unknown, NotSpecified, SVG, WOFF2, EmbeddedOpenType, OpenType, TrueType, WOFF | [`Format`](src:src/core/style/FontFaceSrcData.h#L36) |
| `FontFaceSrcData.LoadFrom` | cpp_enum | Local, URL | [`LoadFrom`](src:src/core/style/FontFaceSrcData.h#L33) |
| `Frame.ComputePurpose` | cpp_enum | Scrolling, GraphicsBufferBySelf, GraphicsBufferByOtherLayer | [`ComputePurpose`](src:src/core/layout/Frame.h#L1930) |
| `Frame.HasFloat` | cpp_enum | HasNone, HasLeft, HasRight | [`HasFloat`](src:src/core/layout/Frame.h#L886) |
| `Frame.HitTestStage` | cpp_enum | HitTestPositionedElements, HitTestNormalFlowInline, HitTestNonPositionedFloats, HitTestNormalFlowBlock, HitTestStageEnd | [`HitTestStage`](src:src/core/layout/Frame.h#L82) |
| `Frame.LayoutWantToResolve` | cpp_enum | ResolveWidth, ResolveHeight, ResolveAll | [`LayoutWantToResolve`](src:src/core/layout/Frame.h#L1842) |
| `Frame.PaintingKind` | cpp_enum | NormalFlowBlockChild, NonPositionedFloats, NormalFlowInline, ReplacedBlock | [`PaintingKind`](src:src/core/layout/Frame.h#L1859) |
| `Frame.PaintingStage` | cpp_enum | PaintingNormalFlowBlock, PaintingNonPositionedFloats, PaintingReplacedBlock, PaintingNormalFlowInline, PaintingStageEnd | [`PaintingStage`](src:src/core/layout/Frame.h#L71) |
| `Frame.WordType` | cpp_enum | CollapsibleWhiteSpace, NonCollapsibleWhiteSpace, ForcedNewline, General | [`WordType`](src:src/core/layout/Frame.h#L892) |
| `FrameBlockBox.Direction` | cpp_enum | None, LtrDirection, RtlDirection | [`Direction`](src:src/core/layout/FrameBlockBox.h#L1164) |
| `FrameBlockBox.InlineNonReplacedBoxMBPStatus` | cpp_enum | MBPStatusNone, ProcessedStaringMBP, ProcessedEndingMBP, SetLeftMBP, SetRightMBP | [`InlineNonReplacedBoxMBPStatus`](src:src/core/layout/FrameBlockBox.h#L487) |
| `FrameBox.BoxSide` | cpp_enum | TopSide, RightSide, BottomSide, LeftSide | [`BoxSide`](src:src/core/layout/FrameBox.h#L453) |
| `FrameBox.ComputeMatrixFor` | cpp_enum | Screen, GraphicsLayer, Window, GraphicsLayerOnGraphicsLayer | [`ComputeMatrixFor`](src:src/core/layout/FrameBox.cpp#L4533) |
| `FrameBox.CopyFlag` | cpp_enum | PositionCopy, WidthAndHeightCopy, MarginCopy, BorderCopy, PaddingCopy, BorderBoxCopy | [`CopyFlag`](src:src/core/layout/FrameBox.h#L444) |
| `FrameBox.PaintingInlineStage` | cpp_enum | PaintingInlineBox, PaintingAtomicInlineBoxButInlineReplaced, PaintingInlineReplaced, PaintingInlineStageEnd | [`PaintingInlineStage`](src:src/core/layout/FrameBox.h#L279) |
| `FrameFlexibleBox.Violations` | cpp_enum | None, Min, Max | [`Violations`](src:src/core/layout/FrameFlexibleBox.cpp#L549) |
| `FrameSVGBox.Mode` | cpp_enum | WaitCoordsX, WaitCoordsY | [`Mode`](src:src/core/layout/svg/FrameSVGBox.cpp#L814) |
| `HTMLCanvasElement.CanvasContextMode` | cpp_enum | CanvasContextModeNone, CanvasContextModePlaceHolder, CanvasContextMode2D, CanvasContextModeBitmapRenderer, CanvasContextModeWebGL, CanvasContextModeWebGL2 | [`CanvasContextMode`](src:src/core/dom/canvas/HTMLCanvasElement.h#L43) |
| `HTMLConstructionSite.Operation` | cpp_enum | Insert, InsertText, InsertAlreadyParsedChild, Reparent, TakeAllChildren | [`Operation`](src:src/core/dom/parser/HTMLConstructionSite.h#L56) |
| `HTMLConstructionSite.WhitespaceMode` | cpp_enum | WhitespaceUnknown, NotAllWhitespace, AllWhitespace | [`WhitespaceMode`](src:src/core/dom/parser/HTMLConstructionSite.h#L90) |
| `HTMLEntityParser.EntityState` | cpp_enum | Initial, Number, MaybeHexLowerCaseX, MaybeHexUpperCaseX, Hex, Decimal, Named | [`EntityState`](src:src/core/dom/parser/HTMLEntityParser.cpp#L197) |
| `HTMLEntitySearch.CompareResult` | cpp_enum | Before, Prefix, After | [`CompareResult`](src:src/core/dom/parser/HTMLEntitySearch.h#L74) |
| `HTMLFormattingElementList.MarkerEntryType` | cpp_enum | MarkerEntry | [`MarkerEntryType`](src:src/core/dom/parser/HTMLFormattingElementList.h#L69) |
| `HTMLMediaElement.NetworkState` | cpp_enum | NETWORK_EMPTY, NETWORK_IDLE, NETWORK_LOADING, NETWORK_NO_SOURCE | [`NetworkState`](src:src/core/dom/HTMLMediaElement.h#L241) |
| `HTMLMediaElement.PreloadState` | cpp_enum | PRELOAD_NONE, PRELOAD_METADATA, PRELOAD_AUTOMATIC | [`PreloadState`](src:src/core/dom/HTMLMediaElement.h#L256) |
| `HTMLMediaElement.ReadyState` | cpp_enum | HAVE_NOTHING, HAVE_METADATA, HAVE_CURRENT_DATA, HAVE_FUTURE_DATA, HAVE_ENOUGH_DATA | [`ReadyState`](src:src/core/dom/HTMLMediaElement.h#L248) |
| `HTMLParserIdioms.CharacterWidth` | cpp_enum | Likely8Bit, Force8Bit, Force16Bit | [`CharacterWidth`](src:src/core/dom/parser/HTMLParserIdioms.h#L351) |
| `HTMLParserIdioms.Sign` | cpp_enum | Positive, Negative | [`Sign`](src:src/core/dom/parser/HTMLParserIdioms.h#L61) |
| `HTMLTableElement.CellBorders` | cpp_enum | NoBorders, InsetBorders, SolidBordersRowsOnly, SolidBordersColsOnly, SolidBorders | [`CellBorders`](src:src/core/dom/HTMLTableElement.h#L41) |
| `HTMLTableElement.Rules` | cpp_enum | UnsetRules, NoneRules, GroupsRules, RowsRules, ColsRules, AllRules | [`Rules`](src:src/core/dom/HTMLTableElement.h#L32) |
| `HTMLTextEditable.EditStatus` | cpp_enum | None, PreeditStart, PreeditEnd, Commit | [`EditStatus`](src:src/core/dom/HTMLTextEditable.h#L27) |
| `HTMLToken.Type` | cpp_enum | Uninitialized, DOCTYPE, StartTag, EndTag, Comment, Character, EndOfFile | [`Type`](src:src/core/dom/parser/HTMLToken.h#L77) |
| `HTMLTokenizer.State` | cpp_enum | DataState, CharacterReferenceInDataState, RCDATAState, CharacterReferenceInRCDATAState, RAWTEXTState, ScriptDataState, PLAINTEXTState, TagOpenState, EndTagOpenState, TagNameState, RCDATALessThanSignState, RCDATAEndTagOpenState … (8 more) | [`State`](src:src/core/dom/parser/HTMLTokenizer.h#L60) |
| `HTMLTreeBuilder.InsertionMode` | cpp_enum | InitialMode, BeforeHTMLMode, BeforeHeadMode, InHeadMode, InHeadNoscriptMode, AfterHeadMode, TemplateContentsMode, InBodyMode, TextMode, InTableMode, InTableTextMode, InCaptionMode … (8 more) | [`InsertionMode`](src:src/core/dom/parser/HTMLTreeBuilder.h#L164) |
| `HTTPStatus.HTTPStatusCode` | cpp_enum | HTTP_STATUS_CONTINUE, HTTP_STATUS_SWITCHING_PROTOCOLS, HTTP_STATUS_PROCESSING, HTTP_STATUS_OK, HTTP_STATUS_CREATED, HTTP_STATUS_ACCEPTED, HTTP_STATUS_NON_AUTHORITATIVE_INFORMATION, HTTP_STATUS_NO_CONTENT, HTTP_STATUS_RESET_CONTENT, HTTP_STATUS_PARTIAL_CONTENT, HTTP_STATUS_MULTI_STATUS, HTTP_STATUS_ALREADY_REPORTED … (29 more) | [`HTTPStatusCode`](src:src/platform/network/http/HTTPStatus.h#L94) |
| `HistoryManager.HistoryManagerOwner` | cpp_enum | OwnerIsWebView, OwnerIsHTMLIFrame | [`HistoryManagerOwner`](src:src/browser/history/HistoryManager.h#L119) |
| `LWEWebView.InitializeOption` | cpp_enum | None, PreferSeparateThread, PreferIncrementalGC | [`InitializeOption`](src:compat/tizen_5.0/inc/LWEWebView.h#L50) |
| `LWEWebView.InitializeOption` | cpp_enum | None, PreferSeparateThread, PreferIncrementalGC | [`InitializeOption`](src:inc/LWEWebView.h#L58) |
| `LWEWebViewEFL.Owner` | cpp_enum | FREE, ENGINE, READY, DISPLAYING | [`Owner`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L153) |
| `LWEWebViewEcoreWl2.Owner` | cpp_enum | FREE, ENGINE, READY, PRESENTING | [`Owner`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L190) |
| `LWEWebViewFlutter.PORT_COMPOSITOR_BACKEND` | cpp_enum | CAIRO, GL, MOCK | [`PORT_COMPOSITOR_BACKEND`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L83) |
| `LWEWebViewFlutter.PORT_WINDOW_BACKEND` | cpp_enum | GB, GL, HEADLESS | [`PORT_WINDOW_BACKEND`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L82) |
| `LWEWorker.WorkerProcessState` | cpp_enum | None, Terminated | [`WorkerProcessState`](src:inc/LWEWorker.h#L44) |
| `LayoutUtil.AspectRatioFit` | cpp_enum | ShrinkAspectRatioFit, GrowAspectRatioFit | [`AspectRatioFit`](src:src/core/layout/LayoutUtil.h#L140) |
| `LineBreakerIteratorPool.LineBreakIteratorMode` | cpp_enum | LineBreakIteratorModeUAX14, LineBreakIteratorModeUAX14Loose, LineBreakIteratorModeUAX14Normal, LineBreakIteratorModeUAX14Strict | [`LineBreakIteratorMode`](src:src/core/util/LineBreakerIteratorPool.h#L28) |
| `LweWebViewImpl.ImeComposingStatus` | java_enum | NORMAL, COMPOSING_START, COMPOSING_END | [`ImeComposingStatus`](src:src/public/bridge/android/java/com/samsung/android/lightweightwebengine/internal/LweWebViewImpl.java#L93) |
| `MediaPlayer.PlaybackState` | cpp_enum | PLAYBACK_STATE_NONE, PLAYBACK_STATE_PLAYING, PLAYBACK_STATE_PAUSED, PLAYBACK_STATE_END | [`PlaybackState`](src:src/platform/multimedia/MediaPlayer.h#L67) |
| `MediaPlayer.SeekState` | cpp_enum | SEEKSTATE_NO_SEEK, SEEKSTATE_SEEKING, SEEKSTATE_WAITING | [`SeekState`](src:src/platform/multimedia/MediaPlayer.h#L73) |
| `MediaQuery.RestrictorType` | cpp_enum | Only, Not, None | [`RestrictorType`](src:src/core/style/MediaQuery.h#L55) |
| `MediaQueryEvaluator.MediaFeaturePrefix` | cpp_enum | NoPrefix, MinPrefix, MaxPrefix | [`MediaFeaturePrefix`](src:src/core/style/MediaQueryEvaluator.cpp#L58) |
| `MediaSource.EndOfStreamError` | cpp_enum | None, Network, Decode | [`EndOfStreamError`](src:src/core/modules/mediasource/MediaSource.h#L58) |
| `MediaSource.ReadyState` | cpp_enum | Closed, Open, Ended | [`ReadyState`](src:src/core/modules/mediasource/MediaSource.h#L48) |
| `MemorySerializer.ScriptValueSerializerTag` | cpp_enum | Undefined, Null, TruePrimitive, FalsePrimitive, Int32Primitive, Uint32Primitive, DoublePrimitive, OneByteStringPrimitive, TwoByteStringPrimitive, BeginObject, EndObject, BeginArrayObject … (8 more) | [`ScriptValueSerializerTag`](src:src/core/serialize/MemorySerializer.cpp#L123) |
| `MessageLoopGLib.RendezvousOwner` | cpp_enum | None, MainBlockedOnLWE, LWEPausingMain | [`RendezvousOwner`](src:src/platform/message_loop/MessageLoopGLib.cpp#L99) |
| `MiniBrowser.StarfishStartUpFlag` | cpp_enum | enableComputedStyleDump, enableFrameTreeDump, enableStackingContextDump, enableHitTestDump, enableDebugGraphicsLayer, enableDebugRepaintRegion, enableRegressionTest | [`StarfishStartUpFlag`](src:src/shell/MiniBrowser.cpp#L34) |
| `NamedColors.NamedColorValue` | cpp_enum | currentColor | [`NamedColorValue`](src:src/core/style/NamedColors.h#L179) |
| `NativeImageData.PreserveAspectRatioAlign` | cpp_enum | None, xMinYMin, xMidYMin, xMaxYMin, xMinYMid, xMidYMid, xMaxYMid, xMinYMax, xMidYMax, xMaxYMax | [`PreserveAspectRatioAlign`](src:src/core/modules/canvas/image/NativeImageData.h#L38) |
| `NativeImageData.PreserveAspectRatioMeetOrSlice` | cpp_enum | Meet, Slice | [`PreserveAspectRatioMeetOrSlice`](src:src/core/modules/canvas/image/NativeImageData.h#L51) |
| `Node.DocumentPosition` | cpp_enum | DOCUMENT_POSITION_DISCONNECTED, DOCUMENT_POSITION_PRECEDING, DOCUMENT_POSITION_FOLLOWING, DOCUMENT_POSITION_CONTAINS, DOCUMENT_POSITION_CONTAINED_BY, DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC | [`DocumentPosition`](src:src/core/dom/Node.h#L196) |
| `Node.NodeState` | cpp_enum | NodeStateNormal, NodeStateActive, NodeStateFocused, NodeStateHovered, NodeStateTarget, NodeStateLink | [`NodeState`](src:src/core/dom/Node.h#L451) |
| `Node.NodeType` | cpp_enum | ELEMENT_NODE, ATTRIBUTE_NODE, TEXT_NODE, CDATA_SECTION_NODE, ENTITY_REFERENCE_NODE, ENTITY_NODE, PROCESSING_INSTRUCTION_NODE, COMMENT_NODE, DOCUMENT_NODE, DOCUMENT_TYPE_NODE, DOCUMENT_FRAGMENT_NODE, NOTATION_NODE | [`NodeType`](src:src/core/dom/Node.h#L181) |
| `PassRef.AdoptTag` | cpp_enum | Adopt | [`AdoptTag`](src:src/core/util/RefPtr.h#L77) |
| `PassRefPtr.AdoptTag` | cpp_enum | Adopt | [`AdoptTag`](src:src/core/util/RefPtr.h#L279) |
| `PlatformFile.FileMode` | cpp_enum | Read, Write, ReadWrite | [`FileMode`](src:src/platform/file/PlatformFile.h#L35) |
| `PlatformFile.Whence` | cpp_enum | SEEK_SET, SEEK_CUR, SEEK_END | [`Whence`](src:src/platform/file/PlatformFile.h#L41) |
| `PlatformIntegrationData.IdleModeJob` | cpp_enum | ClearDrawnBuffers, ForceGC, DropDecodedImageBuffer, ClearFontCache, IdleModeFull, IdleModeMiddle, IdleModeNone | [`IdleModeJob`](src:inc/PlatformIntegrationData.h#L260) |
| `PlatformIntegrationData.KeyValue` | cpp_enum | UnidentifiedKey, AltLeftKey, AltRightKey, ControlLeftKey, ControlRightKey, CapsLockKey, FnKey, FnLockKey, HyperKey, MetaKey, NumLockKey, ScrollLockKey … (8 more) | [`KeyValue`](src:inc/PlatformIntegrationData.h#L7) |
| `PlatformIntegrationData.MouseButtonValue` | cpp_enum | NoButton, LeftButton, MiddleButton, RightButton | [`MouseButtonValue`](src:inc/PlatformIntegrationData.h#L239) |
| `PlatformIntegrationData.MouseButtonsValue` | cpp_enum | NoButtonDown, LeftButtonDown, RightButtonDown, MiddleButtonDown | [`MouseButtonsValue`](src:inc/PlatformIntegrationData.h#L246) |
| `PlatformIntegrationData.TTSMode` | cpp_enum | Default, Forced | [`TTSMode`](src:inc/PlatformIntegrationData.h#L253) |
| `PlatformIntegrationData.WebSecurityMode` | cpp_enum | Enable, Disable | [`WebSecurityMode`](src:inc/PlatformIntegrationData.h#L258) |
| `PreloadScanner.Mode` | cpp_enum | ModeAttr, ModeValueWaitFirstQuotationMark, ModeValueWaitValue | [`Mode`](src:src/core/dom/parser/PreloadScanner.cpp#L72) |
| `RTCIceTransport.RTCIceTransportState` | cpp_enum | New, Checking, Connected, Completed, Disconnected, Failed, Closed | [`RTCIceTransportState`](src:src/core/modules/mediastream/RTCIceTransport.h#L34) |
| `RTCRtpTransceiverInit.RTCRtpTransceiverDirection` | cpp_enum | Sendrecv, Sendonly, Recvonly, Inactive, Stopped | [`RTCRtpTransceiverDirection`](src:src/core/modules/mediastream/RTCRtpTransceiverInit.h#L33) |
| `Range.ProcessingType` | cpp_enum | Extract, Clone, Delete | [`ProcessingType`](src:src/core/dom/Range.h#L129) |
| `Renderer.WindowHandlerKind` | cpp_enum | WindowHandlerShowDropdownMenu, WindowHandlerShowAlert, WindowHandlerOnDropdownMenuItemSelected | [`WindowHandlerKind`](src:src/core/modules/renderer/Renderer.h#L30) |
| `Resource.State` | cpp_enum | BeforeSend, Receiving, Finished, Failed, Canceled | [`State`](src:src/platform/loader/Resource.h#L42) |
| `Resource.Type` | cpp_enum | ResourceType, ImageResourceType, TextResourceType, FontResourceType | [`Type`](src:src/platform/loader/Resource.h#L50) |
| `ResourceURL.Protocol` | cpp_enum | FILE_PROTOCOL, BLOB_PROTOCOL, DATA_PROTOCOL, ABOUT_PROTOCOL, HTTP_PROTOCOL, HTTPS_PROTOCOL, JAVASCRIPT_PROTOCOL, WS_PROTOCOL, WSS_PROTOCOL, UNKNOWN | [`Protocol`](src:src/platform/loader/ResourceURL.h#L35) |
| `SVGComponentTransferFunctionElement.ComponentTransferType` | cpp_enum | SVG_FECOMPONENTTRANSFER_TYPE_UNKNOWN, SVG_FECOMPONENTTRANSFER_TYPE_IDENTITY, SVG_FECOMPONENTTRANSFER_TYPE_TABLE, SVG_FECOMPONENTTRANSFER_TYPE_DISCRETE, SVG_FECOMPONENTTRANSFER_TYPE_LINEAR, SVG_FECOMPONENTTRANSFER_TYPE_GAMMA | [`ComponentTransferType`](src:src/core/dom/svg/SVGComponentTransferFunctionElement.h#L29) |
| `SVGFETurbulenceElement.StitchType` | cpp_enum | SVG_STITCHTYPE_UNKNOWN, SVG_STITCHTYPE_STITCH, SVG_STITCHTYPE_NOSTITCH | [`StitchType`](src:src/core/dom/svg/SVGFETurbulenceElement.h#L52) |
| `SVGFETurbulenceElement.TurbulenceType` | cpp_enum | SVG_TURBULENCE_TYPE_UNKNOWN, SVG_TURBULENCE_TYPE_FRACTALNOISE, SVG_TURBULENCE_TYPE_TURBULENCE | [`TurbulenceType`](src:src/core/dom/svg/SVGFETurbulenceElement.h#L42) |
| `SVGLength.UnitType` | cpp_enum | SVG_LENGTHTYPE_UNKNOWN, SVG_LENGTHTYPE_NUMBER, SVG_LENGTHTYPE_PERCENTAGE, SVG_LENGTHTYPE_EMS, SVG_LENGTHTYPE_EXS, SVG_LENGTHTYPE_PX, SVG_LENGTHTYPE_CM, SVG_LENGTHTYPE_MM, SVG_LENGTHTYPE_IN, SVG_LENGTHTYPE_PT, SVG_LENGTHTYPE_PC | [`UnitType`](src:src/core/dom/svg/SVGLength.h#L32) |
| `SVGMarkerElement.ORIENT` | cpp_enum | SVG_MARKER_ORIENT_UNKNOWN, SVG_MARKER_ORIENT_AUTO, SVG_MARKER_ORIENT_ANGLE | [`ORIENT`](src:src/core/dom/svg/SVGMarkerElement.h#L43) |
| `SVGMarkerElement.UNIT` | cpp_enum | SVG_MARKERUNTIS_UNKNOWN, SVG_MARKERUNITS_USERSPACEONUSE, SVG_MARKERUNITS_STROKEWIDTH | [`UNIT`](src:src/core/dom/svg/SVGMarkerElement.h#L37) |
| `SVGPathElement.Mode` | cpp_enum | WaitCommand, WaitCoordsX, WaitCoordsY, WaitCoordsX2, WaitCoordsY2, WaitCoordsX3, WaitCoordsY3, WaitCoordsX4, WaitCoordsY4 | [`Mode`](src:src/core/dom/svg/SVGPathElement.cpp#L401) |
| `SVGTransform.Type` | cpp_enum | SVG_TRANSFORM_UNKOWN, SVG_TRANSFORM_MATRIX, SVG_TRANSFORM_TRANSLATE, SVG_TRANSFORM_SCALE, SVG_TRANSFORM_ROTATE, SVG_TRANSFORM_SKEWX, SVG_TRANSFORM_SKEWY | [`Type`](src:src/core/dom/svg/SVGTransform.h#L34) |
| `SVGUnitTypes.UnitTypes` | cpp_enum | SVG_UNIT_TYPE_UNKNOWN, SVG_UNIT_TYPE_USERSPACEONUSE, SVG_UNIT_TYPE_OBJECTBOUNDINGBOX | [`UnitTypes`](src:src/core/dom/svg/SVGUnitTypes.h#L27) |
| `SelectorQuery.ClassElementListBehavior` | cpp_enum | AllElements, OnlyRoots | [`ClassElementListBehavior`](src:src/core/dom/SelectorQuery.cpp#L43) |
| `SelectorQuery.MatchTraverseRootState` | cpp_enum | DoesNotMatchTraverseRoots, MatchesTraverseRoots | [`MatchTraverseRootState`](src:src/core/dom/SelectorQuery.h#L32) |
| `Serializer.Type` | cpp_enum | Undefined, Null, BooleanPrimitive, Int32Primitive, Uint32Primitive, NumberPrimitive, StringPrimitive, Boolean, Number, String, Date, RegExp … (8 more) | [`Type`](src:src/core/serialize/Serializer.h#L680) |
| `SocketLWS.LwsEvent` | cpp_enum | OPEN, ERROR, CLOSE, ONMESSAGE | [`LwsEvent`](src:src/core/modules/networking/SocketLWS.h#L65) |
| `SocketLWS.SocketLWSDataType` | cpp_enum | TEXT, BINARY | [`SocketLWSDataType`](src:src/core/modules/networking/SocketLWS.h#L37) |
| `SourceBuffer.AppendMode` | cpp_enum | Segments, Sequence | [`AppendMode`](src:src/core/modules/mediasource/SourceBuffer.h#L141) |
| `SourceBuffer.AppendState` | cpp_enum | WaitingForSegment, ParsingInitSegment, ParsingMediaSegment | [`AppendState`](src:src/core/modules/mediasource/SourceBuffer.h#L146) |
| `SourceBuffer.UpdateState` | cpp_enum | Success, Error, Abort | [`UpdateState`](src:src/core/modules/mediasource/SourceBuffer.h#L135) |
| `StackingContext.NeedsGraphicsLayerReason` | cpp_enum | NeedsGraphicsLayerReasonNone, NeedsGraphicsLayerReasonBySelf, NeedsGraphicsLayerReasonNotCoveredByParent, NeedsGraphicsLayerReasonCollapsedWithSiblingLayer, NeedsGraphicsLayerReasonSiblingLayerNeedsAnimation, NeedsGraphicsLayerReasonNeedsScroll | [`NeedsGraphicsLayerReason`](src:src/core/layout/StackingContext.h#L37) |
| `StackingContext.RepaintingWhenScrollingReason` | cpp_enum | RepaintingWhenScrollingReasonNone, RepaintingWhenScrollingReasonNoGraphicsBuffer, RepaintingWhenScrollingReasonBorder, RepaintingWhenScrollingReasonBoxShadow, RepaintingWhenScrollingReasonOutline, RepaintingWhenScrollingReasonBackgroundSize | [`RepaintingWhenScrollingReason`](src:src/core/layout/StackingContext.h#L49) |
| `Starfish.ScreenOrientationType` | cpp_enum | ScreenOrientationUndefined, ScreenOrientationPortraitPrimary, ScreenOrientationPortraitSecondary, ScreenOrientationLandscapePrimary, ScreenOrientationLandscapeSecondary | [`ScreenOrientationType`](src:src/platform/public/ScreenOrientationType.h#L24) |
| `Starfish.StarfishRendererType` | cpp_enum | kOpenGL, kSoftware, kHeadless | [`StarfishRendererType`](src:src/Starfish.h#L43) |
| `Starfish.StorageType` | cpp_enum | Session, Local | [`StorageType`](src:src/core/storage/StorageType.h#L25) |
| `Starfish.WorkerType` | cpp_enum | Classic, Module | [`WorkerType`](src:src/core/modules/worker/WorkerType.h#L30) |
| `StarfishBase.NullOptionType` | cpp_enum | NullOption | [`NullOptionType`](src:src/StarfishBase.h#L591) |
| `StreamInfo.AudioSampleFormat` | cpp_enum | AudioSampleFormatNone, AudioSampleFormatU8, AudioSampleFormatS16, AudioSampleFormatS32, AudioSampleFormatFLT, AudioSampleFormatDBL, AudioSampleFormatU8P, AudioSampleFormatS16P, AudioSampleFormatS32P, AudioSampleFormatFLTP, AudioSampleFormatDBLP | [`AudioSampleFormat`](src:src/platform/multimedia/StreamInfo.h#L73) |
| `StreamInfo.MediaCodec` | cpp_enum | MediaCodecUnknown, MediaCodecAudioAAC, MediaCodecAudioMP3, MediaCodecAudioVorbis, MediaCodecAudioOpus, MediaCodecVideoH264, MediaCodecVideoHEVC, MediaCodecVideoVP9, MediaCodecVideoAV1 | [`MediaCodec`](src:src/platform/multimedia/StreamInfo.h#L59) |
| `StreamInfo.StreamType` | cpp_enum | StreamTypeUnknown, StreamTypeAudio, StreamTypeVideo, StreamTypeSubtitle | [`StreamType`](src:src/platform/multimedia/StreamInfo.h#L52) |
| `String.BufferDataKind` | cpp_enum | ASCIIData, BMPData, UTF32Data | [`BufferDataKind`](src:src/core/util/String.h#L642) |
| `String.CharCategory` | cpp_enum | NoCategory, Other_NotAssigned, Letter_Uppercase, Letter_Lowercase, Letter_Titlecase, Letter_Modifier, Letter_Other, Mark_NonSpacing, Mark_Enclosing, Mark_SpacingCombining, Number_DecimalDigit, Number_Letter … (8 more) | [`CharCategory`](src:src/core/util/String.h#L597) |
| `String.CharDirection` | cpp_enum | Ltr, Rtl, Mixed, Neutral | [`CharDirection`](src:src/core/util/String.h#L590) |
| `String.FastPathFlags` | cpp_enum | NoFastPath, Use8BitAdvanceAndUpdateLineNumbers, Use8BitAdvance | [`FastPathFlags`](src:src/core/util/String.h#L2135) |
| `String.LookAheadResult` | cpp_enum | DidNotMatch, DidMatch, NotEnoughCharacters | [`LookAheadResult`](src:src/core/util/String.h#L1990) |
| `String.TakeBuffer` | cpp_enum | TakeBufferValue | [`TakeBuffer`](src:src/core/util/String.h#L1063) |
| `StringBuilderPiece.Type` | cpp_enum | StringPiece, ConstChar, Char | [`Type`](src:src/core/util/String.h#L1617) |
| `Style.CalcParserOption` | cpp_enum | LengthParser, AngleParser, TimeParser, LineheightParser | [`CalcParserOption`](src:src/core/style/Style.h#L2664) |
| `Style.DisplayValue` | cpp_enum | InlineDisplayValue, BlockDisplayValue, ListItemDisplayValue, InlineListItemDisplayValue, InlineBlockDisplayValue, TableDisplayValue, InlineTableDisplayValue, TableRowGroupDisplayValue, TableHeaderGroupDisplayValue, TableFooterGroupDisplayValue, TableRowDisplayValue, TableColumnGroupDisplayValue … (10 more) | [`DisplayValue`](src:src/core/style/Style.h#L120) |
| `Style.PositionValue` | cpp_enum | StaticPositionValue, RelativePositionValue, AbsolutePositionValue, FixedPositionValue | [`PositionValue`](src:src/core/style/Style.h#L145) |
| `StyleTransformData.OperationType` | cpp_enum | Matrix, Translate, Scale, Rotate, Skew, None | [`OperationType`](src:src/core/style/StyleTransformData.h#L37) |
| `TextAlternativeHelper.AriaByType` | cpp_enum | AriaLabelledBy, ArialDescribedBy | [`AriaByType`](src:src/core/modules/tts/TextAlternativeHelper.h#L34) |
| `TextOverflowData.TextOverflowValue` | cpp_enum | TextOverflowClipValue, TextOverflowEllipsisValue | [`TextOverflowValue`](src:src/core/style/TextOverflowData.h#L29) |
| `TextTrack.Kind` | cpp_enum | InvalidKind, Subtitles, Captions, Descriptions, Chapters, Metadata | [`Kind`](src:src/core/dom/TextTrack.h#L43) |
| `TextTrack.Mode` | cpp_enum | InvalidMode, Off, Hidden, Showing | [`Mode`](src:src/core/dom/TextTrack.h#L36) |
| `WebBase.StarfishPubicWebViewHandlerKind` | cpp_enum | OnPageStarted, OnPageLoaded, OnPageParsed, OnLoadResource, OnReceivedError, OnProgressChanged, OnDownloadStart, OnIdle, ShouldOverrideUrlLoading, DebuggerShouldInit, DebuggerShouldContinueWaiting | [`StarfishPubicWebViewHandlerKind`](src:src/core/page/WebBase.h#L43) |
| `WebSocket.CloseCode` | cpp_enum | NormalClosure, GoingAway, ProtocolError, Reserved_1004, UnsupportedData, NoStatusReceived, AbnormalClosure, InvalidFramePayloadData, PolicyViolation, MessageTooBig, MissingExtension, InternalError … (4 more) | [`CloseCode`](src:src/core/modules/networking/WebSocket.h#L37) |
| `WebSocket.ReadyState` | cpp_enum | CONNECTING, OPEN, CLOSING, CLOSED | [`ReadyState`](src:src/core/modules/networking/WebSocket.h#L35) |
| `WebView.StarfishDeviceKind` | cpp_enum | deviceKindUseMouse, deviceKindUseTouchScreen | [`StarfishDeviceKind`](src:src/core/page/WebView.h#L44) |
| `WebView.StarfishStartUpFlag` | cpp_enum | enableComputedStyleDump, enableFrameTreeDump, enableStackingContextDump, enableHitTestDump, enableDebugGraphicsLayer, enableDebugRepaintRegion, enableRegressionTest | [`StarfishStartUpFlag`](src:src/core/page/WebView.h#L34) |
| `WindowKeyType.INPUT` | cpp_enum | NONE, RELEASE, PRESS, ACTION_END, MOUSE_LBUTTON, TYPE_END, LEFT, UP, RIGHT, DOWN, CODE_END | [`INPUT`](src:src/shell/WindowKeyType.h#L25) |
| `WindowKeyType.MOD` | cpp_enum | SHIFT, CONTROL | [`MOD`](src:src/shell/WindowKeyType.h#L44) |

---

## Message ID Catalog

Message identifiers observed on IPC channels (text-based protocols; no numeric opcodes were found in the extraction results).

| Message ID | Hex Value | Direction | Payload | Handler | Source |
|------------|-----------|-----------|---------|---------|--------|
| `{'id': 'Runtime.consoleAPICalled', 'value': 'Runtime.consoleAPICalled', 'direction': 'Server→Client', 'payload': 'type/level, args ({type,value} list), executionContextId', 'handler': 'CDPDispatcher::emitConsoleForWebView'}` | Not specified in code | Not specified in code | Builds a Runtime.consoleAPICalled event (level, args array of {type,value}, exec | `CDPDispatcher::emitConsoleForWebView` | [`emitConsoleForWebView`](src:src/core/cdp/CDPDispatcher.cpp#L1594) |
| `{'id': 'Runtime.bindingCalled', 'value': 'Runtime.bindingCalled', 'direction': 'Server→Client', 'payload': 'name, payload string, executionContextId', 'handler': 'CDPDispatcher::emitBindingCalled'}` | Not specified in code | Not specified in code | Routes to the TargetContext/session owning the originating WebView and, when run | `CDPDispatcher::emitBindingCalled` | [`emitBindingCalled`](src:src/core/cdp/CDPDispatcher.cpp#L1701) |
| `{'id': 'ping', 'value': 'ping', 'direction': 'Client→Server', 'payload': 'JSON {"command":"ping"}', 'handler': 'Inspector::worker'}` | Not specified in code | Not specified in code | Creates nn::socket(AF_SP, NN_PAIR), binds to the configured address, then recv(N | `Inspector::worker` | [`worker`](src:src/core/inspector/Inspector.cpp#L197) |
| `{'id': 'pong', 'value': 'pong', 'direction': 'Server→Client', 'payload': 'JSON {"command":"pong"}', 'handler': 'Inspector::worker'}` | Not specified in code | Not specified in code | Creates nn::socket(AF_SP, NN_PAIR), binds to the configured address, then recv(N | `Inspector::worker` | [`worker`](src:src/core/inspector/Inspector.cpp#L197) |
| `{'id': 'eval', 'value': 'eval', 'direction': 'Client→Server', 'payload': 'JSON {"command":"eval","content":<JS source>}; result returned as console-info', 'handler': 'Inspector::commandEvaluator'}` | Not specified in code | Not specified in code | Creates nn::socket(AF_SP, NN_PAIR), binds to the configured address, then recv(N | `Inspector::worker` | [`worker`](src:src/core/inspector/Inspector.cpp#L197) |
| `{'id': 'console-info', 'value': 'console-info', 'direction': 'Server→Client', 'payload': 'console info text (content field)', 'handler': 'Inspector::sendInfoMessage'}` | Not specified in code | Not specified in code | Sends JSON {"command":"console-info","content":<message text>} over the nanomsg  | `Inspector::sendInfoMessage` | [`sendInfoMessage`](src:src/core/inspector/Inspector.cpp#L58) |
| `{'id': 'console-error', 'value': 'console-error', 'direction': 'Server→Client', 'payload': 'console error text (content field)', 'handler': 'Inspector::sendErrorMessage'}` | Not specified in code | Not specified in code | Sends JSON {"command":"console-error","content":<message text>} over the nanomsg | `Inspector::sendErrorMessage` | [`sendErrorMessage`](src:src/core/inspector/Inspector.cpp#L89) |
| `{'id': 'console-warn', 'value': 'console-warn', 'direction': 'Server→Client', 'payload': 'console warning text (content field)', 'handler': 'Inspector::sendWarnMessage'}` | Not specified in code | Not specified in code | Sends JSON {"command":"console-warn","content":<message text>} over the nanomsg  | `Inspector::sendWarnMessage` | [`sendWarnMessage`](src:src/core/inspector/Inspector.cpp#L120) |
| `{'id': 'console-debug', 'value': 'console-debug', 'direction': 'Server→Client', 'payload': 'console debug text (content field)', 'handler': 'Inspector::sendDebugMessage'}` | Not specified in code | Not specified in code | Sends JSON {"command":"console-debug","content":<message text>} over the nanomsg | `Inspector::sendDebugMessage` | [`sendDebugMessage`](src:src/core/inspector/Inspector.cpp#L151) |

---

## Constant Definitions

479 constants (excluding error codes).

| Constant | Value | Unit/Type | Usage Context | Source |
|----------|-------|-----------|---------------|--------|
| `LWE_DEFAULT_FONT_SIZE` | 16 | cpp_define | LWE WebView public API header (Tizen 5.0 compat) (LWEWebView.h) | [`LWE_DEFAULT_FONT_SIZE`](src:compat/tizen_5.0/inc/LWEWebView.h#L180) |
| `LWE_EXPORT` | __declspec(dllexport) | cpp_define | LWE WebView public API header (Tizen 5.0 compat) (LWEWebView.h) | [`LWE_EXPORT`](src:compat/tizen_5.0/inc/LWEWebView.h#L25) |
| `LWE_EXPORT` | __attribute__((visibility("default"))) | cpp_define | LWE WebView public API header (Tizen 5.0 compat) (LWEWebView.h) | [`LWE_EXPORT`](src:compat/tizen_5.0/inc/LWEWebView.h#L27) |
| `LWE_MAX_FONT_SIZE` | 72 | cpp_define | LWE WebView public API header (Tizen 5.0 compat) (LWEWebView.h) | [`LWE_MAX_FONT_SIZE`](src:compat/tizen_5.0/inc/LWEWebView.h#L182) |
| `LWE_MIN_FONT_SIZE` | 1 | cpp_define | LWE WebView public API header (Tizen 5.0 compat) (LWEWebView.h) | [`LWE_MIN_FONT_SIZE`](src:compat/tizen_5.0/inc/LWEWebView.h#L181) |
| `TIZEN_COMPAT_HEADER_5_0` | N/A | cpp_define | LWE WebView public API header (Tizen 5.0 compat) (LWEWebView.h) | [`TIZEN_COMPAT_HEADER_5_0`](src:compat/tizen_5.0/inc/LWEWebView.h#L85) |
| `SCRIPT_PATH` | N/A | python_const | Docs generator script (run.py) | [`SCRIPT_PATH`](src:docs/generator/run.py#L7) |
| `LWE_DEFAULT_FONT_SIZE` | 16 | cpp_define | LWE WebView public API header (LWEWebView.h) | [`LWE_DEFAULT_FONT_SIZE`](src:inc/LWEWebView.h#L190) |
| `LWE_EXPORT` | __declspec(dllexport) | cpp_define | LWE WebView public API header (LWEWebView.h) | [`LWE_EXPORT`](src:inc/LWEWebView.h#L30) |
| `LWE_EXPORT` | __declspec(dllimport) | cpp_define | LWE WebView public API header (LWEWebView.h) | [`LWE_EXPORT`](src:inc/LWEWebView.h#L32) |
| `LWE_EXPORT` | __attribute__((visibility("default"))) | cpp_define | LWE WebView public API header (LWEWebView.h) | [`LWE_EXPORT`](src:inc/LWEWebView.h#L35) |
| `LWE_MAX_FONT_SIZE` | 72 | cpp_define | LWE WebView public API header (LWEWebView.h) | [`LWE_MAX_FONT_SIZE`](src:inc/LWEWebView.h#L192) |
| `LWE_MIN_FONT_SIZE` | 1 | cpp_define | LWE WebView public API header (LWEWebView.h) | [`LWE_MIN_FONT_SIZE`](src:inc/LWEWebView.h#L191) |
| `LWE_EXPORT` | __declspec(dllexport) | cpp_define | LWE Worker public API header (LWEWorker.h) | [`LWE_EXPORT`](src:inc/LWEWorker.h#L30) |
| `LWE_EXPORT` | __declspec(dllimport) | cpp_define | LWE Worker public API header (LWEWorker.h) | [`LWE_EXPORT`](src:inc/LWEWorker.h#L32) |
| `LWE_EXPORT` | __attribute__((visibility("default"))) | cpp_define | LWE Worker public API header (LWEWorker.h) | [`LWE_EXPORT`](src:inc/LWEWorker.h#L35) |
| `STARFISH_LINE_BREAK_ITERATOR_POOL_SIZE` | 4 | cpp_define | Engine initialization (Starfish.cpp) | [`STARFISH_LINE_BREAK_ITERATOR_POOL_SIZE`](src:src/Starfish.cpp#L81) |
| `BDWGC_FREE_SPACE_DIVISOR` | 12 | cpp_define | Engine configuration (Starfish.h) | [`BDWGC_FREE_SPACE_DIVISOR`](src:src/Starfish.h#L40) |
| `ALWAYS_INLINE` | inline __attribute__((__always_inline__)) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ALWAYS_INLINE`](src:src/StarfishBase.h#L108) |
| `ALWAYS_INLINE` | __forceinline | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ALWAYS_INLINE`](src:src/StarfishBase.h#L110) |
| `ALWAYS_INLINE` | inline | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ALWAYS_INLINE`](src:src/StarfishBase.h#L112) |
| `COMPILER_CLANG` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`COMPILER_CLANG`](src:src/StarfishBase.h#L85) |
| `COMPILER_GCC` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`COMPILER_GCC`](src:src/StarfishBase.h#L89) |
| `COMPILER_MSVC` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`COMPILER_MSVC`](src:src/StarfishBase.h#L87) |
| `COMPILER_QUIRK_FINAL_IS_CALLED_SEALED` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`COMPILER_QUIRK_FINAL_IS_CALLED_SEALED`](src:src/StarfishBase.h#L101) |
| `COMPILER_SUPPORTS_CXX_OVERRIDE_CONTROL` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`COMPILER_SUPPORTS_CXX_OVERRIDE_CONTROL`](src:src/StarfishBase.h#L100) |
| `DEFAULT_CLEAR_STACK_SIZE` | 102400 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`DEFAULT_CLEAR_STACK_SIZE`](src:src/StarfishBase.h#L279) |
| `ELABORATE_CLEAR_STACK_SIZE` | DEFAULT_CLEAR_STACK_SIZE * 4 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ELABORATE_CLEAR_STACK_SIZE`](src:src/StarfishBase.h#L280) |
| `ENSURE_ENUM_UNSIGNED` | : unsigned int | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ENSURE_ENUM_UNSIGNED`](src:src/StarfishBase.h#L184) |
| `ENSURE_ENUM_UNSIGNED` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ENSURE_ENUM_UNSIGNED`](src:src/StarfishBase.h#L186) |
| `ESCARGOT` | // for use additional functions in GCutil | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`ESCARGOT`](src:src/StarfishBase.h#L230) |
| `EXPORT` | __declspec(dllexport) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`EXPORT`](src:src/StarfishBase.h#L157) |
| `EXPORT` | __attribute__((visibility("default"))) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`EXPORT`](src:src/StarfishBase.h#L159) |
| `FALLTHROUGH` | __attribute__((fallthrough)) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`FALLTHROUGH`](src:src/StarfishBase.h#L166) |
| `FALLTHROUGH` | /* fall through */ | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`FALLTHROUGH`](src:src/StarfishBase.h#L168) |
| `FALLTHROUGH` | /* fall through */ | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`FALLTHROUGH`](src:src/StarfishBase.h#L171) |
| `FALLTHROUGH` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`FALLTHROUGH`](src:src/StarfishBase.h#L173) |
| `FALSE` | 0 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`FALSE`](src:src/StarfishBase.h#L260) |
| `NEVER_INLINE` | __attribute__((__noinline__)) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NEVER_INLINE`](src:src/StarfishBase.h#L119) |
| `NEVER_INLINE` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NEVER_INLINE`](src:src/StarfishBase.h#L121) |
| `NOMINMAX` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NOMINMAX`](src:src/StarfishBase.h#L215) |
| `NO_RETURN` | __attribute((__noreturn__)) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NO_RETURN`](src:src/StarfishBase.h#L146) |
| `NO_RETURN` | __declspec(noreturn) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NO_RETURN`](src:src/StarfishBase.h#L148) |
| `NO_RETURN` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NO_RETURN`](src:src/StarfishBase.h#L150) |
| `NULLABLE` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`NULLABLE`](src:src/StarfishBase.h#L176) |
| `OS_POSIX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_POSIX`](src:src/StarfishBase.h#L196) |
| `OS_POSIX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_POSIX`](src:src/StarfishBase.h#L198) |
| `OS_POSIX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_POSIX`](src:src/StarfishBase.h#L200) |
| `OS_POSIX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_POSIX`](src:src/StarfishBase.h#L205) |
| `OS_POSIX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_POSIX`](src:src/StarfishBase.h#L207) |
| `OS_POSIX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_POSIX`](src:src/StarfishBase.h#L209) |
| `OS_WINDOWS` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_WINDOWS`](src:src/StarfishBase.h#L190) |
| `OS_WINDOWS` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`OS_WINDOWS`](src:src/StarfishBase.h#L192) |
| `STARFISH_32` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_32`](src:src/StarfishBase.h#L308) |
| `STARFISH_64` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_64`](src:src/StarfishBase.h#L310) |
| `STARFISH_ARM` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_ARM`](src:src/StarfishBase.h#L327) |
| `STARFISH_ARM64` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_ARM64`](src:src/StarfishBase.h#L333) |
| `STARFISH_ARM_NEON` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_ARM_NEON`](src:src/StarfishBase.h#L329) |
| `STARFISH_ARM_NEON` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_ARM_NEON`](src:src/StarfishBase.h#L334) |
| `STARFISH_CRASH` | STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_CRASH`](src:src/StarfishBase.h#L476) |
| `STARFISH_ENABLE_PROFILE_LOADING` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_ENABLE_PROFILE_LOADING`](src:src/StarfishBase.h#L359) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/StarfishBase.h#L358) |
| `STARFISH_LOG_TAG` | "[WORKER] " | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_LOG_TAG`](src:src/StarfishBase.h#L363) |
| `STARFISH_LOG_TAG` | "" | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_LOG_TAG`](src:src/StarfishBase.h#L365) |
| `STARFISH_PIXEL_A_INDEX` | 3 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_A_INDEX`](src:src/StarfishBase.h#L1082) |
| `STARFISH_PIXEL_A_INDEX` | 3 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_A_INDEX`](src:src/StarfishBase.h#L1087) |
| `STARFISH_PIXEL_B_INDEX` | 2 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_B_INDEX`](src:src/StarfishBase.h#L1081) |
| `STARFISH_PIXEL_B_INDEX` | 0 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_B_INDEX`](src:src/StarfishBase.h#L1086) |
| `STARFISH_PIXEL_G_INDEX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_G_INDEX`](src:src/StarfishBase.h#L1080) |
| `STARFISH_PIXEL_G_INDEX` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_G_INDEX`](src:src/StarfishBase.h#L1085) |
| `STARFISH_PIXEL_R_INDEX` | 0 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_R_INDEX`](src:src/StarfishBase.h#L1079) |
| `STARFISH_PIXEL_R_INDEX` | 2 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_PIXEL_R_INDEX`](src:src/StarfishBase.h#L1084) |
| `STARFISH_RISCV32` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_RISCV32`](src:src/StarfishBase.h#L337) |
| `STARFISH_RISCV64` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_RISCV64`](src:src/StarfishBase.h#L340) |
| `STARFISH_X86` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_X86`](src:src/StarfishBase.h#L323) |
| `STARFISH_X86_64` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`STARFISH_X86_64`](src:src/StarfishBase.h#L317) |
| `TRUE` | 1 | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`TRUE`](src:src/StarfishBase.h#L256) |
| `WARN_UNUSED_RETURN` | __attribute__((__warn_unused_result__)) | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`WARN_UNUSED_RETURN`](src:src/StarfishBase.h#L578) |
| `WARN_UNUSED_RETURN` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`WARN_UNUSED_RETURN`](src:src/StarfishBase.h#L582) |
| `WIN32_LEAN_AND_MEAN` | N/A | cpp_define | Base compiler/platform configuration macro (StarfishBase.h) | [`WIN32_LEAN_AND_MEAN`](src:src/StarfishBase.h#L224) |
| `APP_CODE_NAME` | "Mozilla" | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`APP_CODE_NAME`](src:src/StarfishInfo.h#L24) |
| `APP_NAME` | "Netscape" | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`APP_NAME`](src:src/StarfishInfo.h#L23) |
| `PRODUCT_NAME` | "Gecko" | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`PRODUCT_NAME`](src:src/StarfishInfo.h#L25) |
| `STARFISH_NAME` | "Starfish" | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`STARFISH_NAME`](src:src/StarfishInfo.h#L26) |
| `USER_AGENT_MAXIMUM_DATE_VALUE` | 8.64e15 | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`USER_AGENT_MAXIMUM_DATE_VALUE`](src:src/StarfishInfo.h#L31) |
| `VENDOR_NAME` | "Samsung Electronics Co., Ltd." | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`VENDOR_NAME`](src:src/StarfishInfo.h#L27) |
| `VERSION` | STARFISH_VERSION_STR | cpp_define | Browser identification value (navigator/user-agent) (StarfishInfo.h) | [`VERSION`](src:src/StarfishInfo.h#L28) |
| `PORT_BACKEND_GL_WITH_EXTERNAL_TBM` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_BACKEND_GL_WITH_EXTERNAL_TBM`](src:src/StarfishPlatform.h#L60) |
| `PORT_CANVAS_BACKEND_CAIRO` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_CAIRO`](src:src/StarfishPlatform.h#L24) |
| `PORT_CANVAS_BACKEND_CAIRO` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_CAIRO`](src:src/StarfishPlatform.h#L29) |
| `PORT_CANVAS_BACKEND_CAIRO` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_CAIRO`](src:src/StarfishPlatform.h#L40) |
| `PORT_CANVAS_BACKEND_CAIRO` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_CAIRO`](src:src/StarfishPlatform.h#L45) |
| `PORT_CANVAS_BACKEND_CAIRO` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_CAIRO`](src:src/StarfishPlatform.h#L50) |
| `PORT_CANVAS_BACKEND_CAIRO` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_CAIRO`](src:src/StarfishPlatform.h#L55) |
| `PORT_CANVAS_BACKEND_MOCK` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_BACKEND_MOCK`](src:src/StarfishPlatform.h#L35) |
| `PORT_CANVAS_NEEDS_PREMULTIPLIED_ALPHA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_CANVAS_NEEDS_PREMULTIPLIED_ALPHA`](src:src/StarfishPlatform.h#L64) |
| `PORT_EVENTLOOP_BACKEND_GLIB` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_GLIB`](src:src/StarfishPlatform.h#L25) |
| `PORT_EVENTLOOP_BACKEND_GLIB` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_GLIB`](src:src/StarfishPlatform.h#L36) |
| `PORT_EVENTLOOP_BACKEND_LIBUV` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_LIBUV`](src:src/StarfishPlatform.h#L30) |
| `PORT_EVENTLOOP_BACKEND_LIBUV` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_LIBUV`](src:src/StarfishPlatform.h#L41) |
| `PORT_EVENTLOOP_BACKEND_LIBUV` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_LIBUV`](src:src/StarfishPlatform.h#L46) |
| `PORT_EVENTLOOP_BACKEND_LIBUV` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_LIBUV`](src:src/StarfishPlatform.h#L51) |
| `PORT_EVENTLOOP_BACKEND_LIBUV` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_EVENTLOOP_BACKEND_LIBUV`](src:src/StarfishPlatform.h#L56) |
| `PORT_GRAPHIC_BACKEND_MOCK` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_GRAPHIC_BACKEND_MOCK`](src:src/StarfishPlatform.h#L34) |
| `PORT_IMAGEDECODER_BACKEND_MISC` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MISC`](src:src/StarfishPlatform.h#L26) |
| `PORT_IMAGEDECODER_BACKEND_MISC` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MISC`](src:src/StarfishPlatform.h#L31) |
| `PORT_IMAGEDECODER_BACKEND_MISC` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MISC`](src:src/StarfishPlatform.h#L42) |
| `PORT_IMAGEDECODER_BACKEND_MISC` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MISC`](src:src/StarfishPlatform.h#L47) |
| `PORT_IMAGEDECODER_BACKEND_MISC` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MISC`](src:src/StarfishPlatform.h#L52) |
| `PORT_IMAGEDECODER_BACKEND_MISC` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MISC`](src:src/StarfishPlatform.h#L57) |
| `PORT_IMAGEDECODER_BACKEND_MOCK` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_IMAGEDECODER_BACKEND_MOCK`](src:src/StarfishPlatform.h#L37) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L27) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L32) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L38) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L43) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L48) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L53) |
| `PORT_PIXEL_ORDER_BGRA` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_PIXEL_ORDER_BGRA`](src:src/StarfishPlatform.h#L58) |
| `PORT_WEBVIEW_BRIDGE_FLUTTER` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`PORT_WEBVIEW_BRIDGE_FLUTTER`](src:src/StarfishPlatform.h#L59) |
| `STARFISH_WEBWORKER_NOT_HOST` | N/A | cpp_define | Port/backend selection flag (StarfishPlatform.h) | [`STARFISH_WEBWORKER_NOT_HOST`](src:src/StarfishPlatform.h#L68) |
| `STARFISH_CACHE_DIR_NAME` | "cache" | cpp_define | Storage file/directory name (StoragePathProvider.cpp) | [`STARFISH_CACHE_DIR_NAME`](src:src/StoragePathProvider.cpp#L29) |
| `STARFISH_COOKIES_FILE_NAME` | "cookies.txt" | cpp_define | Storage file/directory name (StoragePathProvider.cpp) | [`STARFISH_COOKIES_FILE_NAME`](src:src/StoragePathProvider.cpp#L28) |
| `STARFISH_LOCAL_STORAGE_FILE_NAME` | "localStorage.txt" | cpp_define | Storage file/directory name (StoragePathProvider.cpp) | [`STARFISH_LOCAL_STORAGE_FILE_NAME`](src:src/StoragePathProvider.cpp#L27) |
| `STARFISH_SERVICE_WORKER_DIR_NAME` | "service_worker" | cpp_define | Storage file/directory name (StoragePathProvider.cpp) | [`STARFISH_SERVICE_WORKER_DIR_NAME`](src:src/StoragePathProvider.cpp#L31) |
| `STARFISH_SHARED_WORKER_DIR_NAME` | "shared_worker" | cpp_define | Storage file/directory name (StoragePathProvider.cpp) | [`STARFISH_SHARED_WORKER_DIR_NAME`](src:src/StoragePathProvider.cpp#L30) |
| `HTML_NAMESPACE` | "http://www.w3.org/1999/xhtml" | cpp_define | DOM implementation (Document.h) | [`HTML_NAMESPACE`](src:src/core/dom/Document.h#L92) |
| `OVERRIDE` | N/A | cpp_define | DOM implementation (Document.h) | [`OVERRIDE`](src:src/core/dom/Document.h#L710) |
| `STARFISH_NATIVEGRADIENT_CACHE_SIZE` | 1920 * 1080 * 4 * 2 | cpp_define | DOM implementation (Document.h) | [`STARFISH_NATIVEGRADIENT_CACHE_SIZE`](src:src/core/dom/Document.h#L33) |
| `SVG_NAMESPACE` | "http://www.w3.org/2000/svg" | cpp_define | DOM implementation (Document.h) | [`SVG_NAMESPACE`](src:src/core/dom/Document.h#L94) |
| `VIRTUAL` | N/A | cpp_define | DOM implementation (Document.h) | [`VIRTUAL`](src:src/core/dom/Document.h#L709) |
| `XMLNS_NAMESPACE` | "http://www.w3.org/2000/xmlns/" | cpp_define | DOM implementation (Document.h) | [`XMLNS_NAMESPACE`](src:src/core/dom/Document.h#L96) |
| `XML_NAMESPACE` | "http://www.w3.org/XML/1998/namespace" | cpp_define | DOM implementation (Document.h) | [`XML_NAMESPACE`](src:src/core/dom/Document.h#L95) |
| `OVERRIDE` | override | cpp_define | DOM implementation (HTMLBodyElement.h) | [`OVERRIDE`](src:src/core/dom/HTMLBodyElement.h#L41) |
| `OVERRIDE` | N/A | cpp_define | DOM implementation (HTMLBodyElement.h) | [`OVERRIDE`](src:src/core/dom/HTMLBodyElement.h#L52) |
| `VIRTUAL` | virtual | cpp_define | DOM implementation (HTMLBodyElement.h) | [`VIRTUAL`](src:src/core/dom/HTMLBodyElement.h#L40) |
| `VIRTUAL` | N/A | cpp_define | DOM implementation (HTMLBodyElement.h) | [`VIRTUAL`](src:src/core/dom/HTMLBodyElement.h#L51) |
| `OVERRIDE` | N/A | cpp_define | DOM implementation (HTMLElement.h) | [`OVERRIDE`](src:src/core/dom/HTMLElement.h#L98) |
| `OVERRIDE` | N/A | cpp_define | DOM implementation (HTMLElement.h) | [`OVERRIDE`](src:src/core/dom/HTMLElement.h#L174) |
| `VIRTUAL` | N/A | cpp_define | DOM implementation (HTMLElement.h) | [`VIRTUAL`](src:src/core/dom/HTMLElement.h#L97) |
| `VIRTUAL` | virtual | cpp_define | DOM implementation (HTMLElement.h) | [`VIRTUAL`](src:src/core/dom/HTMLElement.h#L173) |
| `STARFISH_DEFAULT_IFRAME_HEIGHT` | 150 | cpp_define | DOM implementation (HTMLIFrameElement.h) | [`STARFISH_DEFAULT_IFRAME_HEIGHT`](src:src/core/dom/HTMLIFrameElement.h#L28) |
| `STARFISH_DEFAULT_IFRAME_WIDTH` | 300 | cpp_define | DOM implementation (HTMLIFrameElement.h) | [`STARFISH_DEFAULT_IFRAME_WIDTH`](src:src/core/dom/HTMLIFrameElement.h#L27) |
| `STARFISH_OBJECT_ELEMENT_DEFAULT_HEIGHT` | 150 | cpp_define | DOM implementation (HTMLObjectElement.h) | [`STARFISH_OBJECT_ELEMENT_DEFAULT_HEIGHT`](src:src/core/dom/HTMLObjectElement.h#L26) |
| `STARFISH_OBJECT_ELEMENT_DEFAULT_WIDTH` | 300 | cpp_define | DOM implementation (HTMLObjectElement.h) | [`STARFISH_OBJECT_ELEMENT_DEFAULT_WIDTH`](src:src/core/dom/HTMLObjectElement.h#L25) |
| `STARFISH_SCROLLBAR_THICKNESS` | 4 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLLBAR_THICKNESS`](src:src/core/dom/Scrolling.cpp#L579) |
| `STARFISH_SCROLL_ACTIVE_TIME_IN_MS` | 500 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_ACTIVE_TIME_IN_MS`](src:src/core/dom/Scrolling.cpp#L46) |
| `STARFISH_SCROLL_FLING_BASE_TIME_IN_MS` | 1000 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_FLING_BASE_TIME_IN_MS`](src:src/core/dom/Scrolling.cpp#L44) |
| `STARFISH_SCROLL_FLING_LENGTH_MULTIPLY_BASE` | 500 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_FLING_LENGTH_MULTIPLY_BASE`](src:src/core/dom/Scrolling.cpp#L42) |
| `STARFISH_SCROLL_FLING_LENGTH_MULTIPLY_RATIO` | 1500 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_FLING_LENGTH_MULTIPLY_RATIO`](src:src/core/dom/Scrolling.cpp#L43) |
| `STARFISH_SCROLL_FLING_SPEED_RATIO` | 1 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_FLING_SPEED_RATIO`](src:src/core/dom/Scrolling.cpp#L45) |
| `STARFISH_SCROLL_START_FLING_THRESHOLD` | 100 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_START_FLING_THRESHOLD`](src:src/core/dom/Scrolling.cpp#L41) |
| `STARFISH_SCROLL_START_THRESHOLD` | 10 | cpp_define | DOM implementation (Scrolling.cpp) | [`STARFISH_SCROLL_START_THRESHOLD`](src:src/core/dom/Scrolling.cpp#L40) |
| `OVERRIDE` | N/A | cpp_define | DOM implementation (ShadowRoot.h) | [`OVERRIDE`](src:src/core/dom/ShadowRoot.h#L167) |
| `VIRTUAL` | N/A | cpp_define | DOM implementation (ShadowRoot.h) | [`VIRTUAL`](src:src/core/dom/ShadowRoot.h#L166) |
| `TEXTTRACK_INVALID_TIMEVALUE` | -1 | cpp_define | DOM implementation (TextTrack.h) | [`TEXTTRACK_INVALID_TIMEVALUE`](src:src/core/dom/TextTrack.h#L32) |
| `OVERRIDE` | N/A | cpp_define | DOM implementation (TextTrackCue.h) | [`OVERRIDE`](src:src/core/dom/TextTrackCue.h#L104) |
| `VIRTUAL` | N/A | cpp_define | DOM implementation (TextTrackCue.h) | [`VIRTUAL`](src:src/core/dom/TextTrackCue.h#L103) |
| `CRASH` | STARFISH_CRASH | cpp_define | Canvas element binding (CanvasRenderingContext2DMixIn.cpp) | [`CRASH`](src:src/core/dom/canvas/CanvasRenderingContext2DMixIn.cpp#L62) |
| `NEEDS_UNPREMULTIPLIED` | N/A | cpp_define | Canvas element binding (CanvasRenderingContext2DMixIn.cpp) | [`NEEDS_UNPREMULTIPLIED`](src:src/core/dom/canvas/CanvasRenderingContext2DMixIn.cpp#L67) |
| `STARFISH_CANVAS_DEFAULT_HEIGHT` | 150 | cpp_define | Canvas element binding (HTMLCanvasElement.h) | [`STARFISH_CANVAS_DEFAULT_HEIGHT`](src:src/core/dom/canvas/HTMLCanvasElement.h#L30) |
| `STARFISH_CANVAS_DEFAULT_WIDTH` | 300 | cpp_define | Canvas element binding (HTMLCanvasElement.h) | [`STARFISH_CANVAS_DEFAULT_WIDTH`](src:src/core/dom/canvas/HTMLCanvasElement.h#L29) |
| `CRASH` | STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE | cpp_define | Canvas element binding (ImageData.cpp) | [`CRASH`](src:src/core/dom/canvas/ImageData.cpp#L31) |
| `READABLE_STREAM_BUFFER_CHUNK_SIZE` | 65536 | cpp_define | Fetch stream buffering (ReadableStreamBuffer.h) | [`READABLE_STREAM_BUFFER_CHUNK_SIZE`](src:src/core/fetch/stream/ReadableStreamBuffer.h#L32) |
| `OVERRIDE` | N/A | cpp_define | File API (FileReader.h) | [`OVERRIDE`](src:src/core/fileapi/FileReader.h#L66) |
| `VIRTUAL` | N/A | cpp_define | File API (FileReader.h) | [`VIRTUAL`](src:src/core/fileapi/FileReader.h#L65) |
| `STARFISH_NATIVEGRADIENT_MAX_SIZE` | 512 | cpp_define | Layout engine (FrameBox.cpp) | [`STARFISH_NATIVEGRADIENT_MAX_SIZE`](src:src/core/layout/FrameBox.cpp#L1850) |
| `FRAMEBOX_RAREDATA_TAG` | 0x3 | cpp_define | Layout engine (FrameBox.h) | [`FRAMEBOX_RAREDATA_TAG`](src:src/core/layout/FrameBox.h#L65) |
| `STARFISH_GRAPHICS_BUFFER_ADDITIONAL_FACTOR_MAX_SCALE` | 6 | cpp_define | Layout engine (StackingContext.cpp) | [`STARFISH_GRAPHICS_BUFFER_ADDITIONAL_FACTOR_MAX_SCALE`](src:src/core/layout/StackingContext.cpp#L1424) |
| `NEEDS_UNPREMULTIPLIED` | N/A | cpp_define | Canvas rendering module (Canvas.cpp) | [`NEEDS_UNPREMULTIPLIED`](src:src/core/modules/canvas/Canvas.cpp#L847) |
| `STARFISH_CANVAS_SURFACE_TILE_SIZE` | 128 | cpp_define | Canvas rendering module (Canvas.cpp) | [`STARFISH_CANVAS_SURFACE_TILE_SIZE`](src:src/core/modules/canvas/Canvas.cpp#L79) |
| `STARFISH_CANVAS_LENGTH_MAX` | 65535 | cpp_define | Canvas rendering module (Canvas.h) | [`STARFISH_CANVAS_LENGTH_MAX`](src:src/core/modules/canvas/Canvas.h#L23) |
| `SPACE_SIZE_DENOMINATOR` | 60 | cpp_define | Canvas rendering module (Font.h) | [`SPACE_SIZE_DENOMINATOR`](src:src/core/modules/canvas/font/Font.h#L187) |
| `ESCARGOT` | // for GCutil | cpp_define | Canvas rendering module (BufferedNativeImageData.cpp) | [`ESCARGOT`](src:src/core/modules/canvas/image/BufferedNativeImageData.cpp#L21) |
| `GIF_DISPOSE_MASK` | 0x07 | cpp_define | Canvas rendering module (ImageDecoder.cpp) | [`GIF_DISPOSE_MASK`](src:src/core/modules/canvas/image/ImageDecoder.cpp#L57) |
| `GIF_DISPOSE_SHIFT` | 2 | cpp_define | Canvas rendering module (ImageDecoder.cpp) | [`GIF_DISPOSE_SHIFT`](src:src/core/modules/canvas/image/ImageDecoder.cpp#L55) |
| `GIF_TRANSPARENT_MASK` | 0x01 | cpp_define | Canvas rendering module (ImageDecoder.cpp) | [`GIF_TRANSPARENT_MASK`](src:src/core/modules/canvas/image/ImageDecoder.cpp#L56) |
| `NEEDS_PREMULTIPLIED_ALPHA` | N/A | cpp_define | Canvas rendering module (ImageDecoder.cpp) | [`NEEDS_PREMULTIPLIED_ALPHA`](src:src/core/modules/canvas/image/ImageDecoder.cpp#L25) |
| `PNG_SKIP_SETJMP_CHECK` | N/A | cpp_define | Canvas rendering module (ImageDecoder.cpp) | [`PNG_SKIP_SETJMP_CHECK`](src:src/core/modules/canvas/image/ImageDecoder.cpp#L28) |
| `STARFISH_ENABLE_WEBP` | N/A | cpp_define | Canvas rendering module (ImageDecoder.cpp) | [`STARFISH_ENABLE_WEBP`](src:src/core/modules/canvas/image/ImageDecoder.cpp#L52) |
| `CV_STATUS_TIMEOUT_MS` | 1 | cpp_define | Cast/DIAL module (BaseRunnable.cpp) | [`CV_STATUS_TIMEOUT_MS`](src:src/core/modules/cast/BaseRunnable.cpp#L27) |
| `CAST_APP_INFOR_BUFFER_SIZE` | 1024 | cpp_define | Cast/DIAL module (CastApplication.cpp) | [`CAST_APP_INFOR_BUFFER_SIZE`](src:src/core/modules/cast/CastApplication.cpp#L31) |
| `CAST_APP_SERVICE_TYPE` | "urn:dial-multiscreen-org:schemas:dial" | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`CAST_APP_SERVICE_TYPE`](src:src/core/modules/cast/CastConfig.cpp#L38) |
| `DEVICE_FRIENDLY_NAME` | "LWE:StarFish" | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_FRIENDLY_NAME`](src:src/core/modules/cast/CastConfig.cpp#L33) |
| `DEVICE_MODEL_NAME` | STARFISH_NAME | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_MODEL_NAME`](src:src/core/modules/cast/CastConfig.cpp#L28) |
| `DEVICE_PRODUCT_NAME` | STARFISH_NAME | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_PRODUCT_NAME`](src:src/core/modules/cast/CastConfig.cpp#L29) |
| `DEVICE_PRODUCT_NAME_AND_VERSION` | DEVICE_PRODUCT_NAME "/" DEVICE_PRODUCT_VERSION | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_PRODUCT_NAME_AND_VERSION`](src:src/core/modules/cast/CastConfig.cpp#L34) |
| `DEVICE_PRODUCT_VERSION` | VERSION | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_PRODUCT_VERSION`](src:src/core/modules/cast/CastConfig.cpp#L30) |
| `DEVICE_TYPE` | "urn:dial-multiscreen-org:service:dial:1" | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_TYPE`](src:src/core/modules/cast/CastConfig.cpp#L31) |
| `DEVICE_UUID` | "9ad8fd1a-e0f5-44e9-8322-61dd08533c04" | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_UUID`](src:src/core/modules/cast/CastConfig.cpp#L32) |
| `DEVICE_VENDOR_NAME` | VENDOR_NAME | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DEVICE_VENDOR_NAME`](src:src/core/modules/cast/CastConfig.cpp#L27) |
| `DIAL_VERSION` | "2.1" | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`DIAL_VERSION`](src:src/core/modules/cast/CastConfig.cpp#L37) |
| `SERVICE_ID` | "upnp::id::lwe" | cpp_define | Cast/DIAL service configuration (CastConfig.cpp) | [`SERVICE_ID`](src:src/core/modules/cast/CastConfig.cpp#L36) |
| `CAST_APP_URL` | "/apps" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`CAST_APP_URL`](src:src/core/modules/cast/CastConfig.h#L33) |
| `COLOR_CYAN` | "\033[36m" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`COLOR_CYAN`](src:src/core/modules/cast/CastConfig.h#L61) |
| `COLOR_GREEN` | "\033[32m" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`COLOR_GREEN`](src:src/core/modules/cast/CastConfig.h#L59) |
| `COLOR_MAGENTA` | "\033[35m" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`COLOR_MAGENTA`](src:src/core/modules/cast/CastConfig.h#L60) |
| `COLOR_RED` | "\033[31m" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`COLOR_RED`](src:src/core/modules/cast/CastConfig.h#L58) |
| `COLOR_RESET` | "\033[0m" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`COLOR_RESET`](src:src/core/modules/cast/CastConfig.h#L56) |
| `COLOR_YELLOW` | "\033[0;33m" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`COLOR_YELLOW`](src:src/core/modules/cast/CastConfig.h#L57) |
| `LOCATION_DESC` | "/deviceDescription.xml" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`LOCATION_DESC`](src:src/core/modules/cast/CastConfig.h#L32) |
| `LOCATION_PORT` | 5696 | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`LOCATION_PORT`](src:src/core/modules/cast/CastConfig.h#L31) |
| `LOG_ID` | "DEBUG_CAST" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`LOG_ID`](src:src/core/modules/cast/CastConfig.h#L49) |
| `SSDP_GROUP` | "239.255.255.250" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`SSDP_GROUP`](src:src/core/modules/cast/CastConfig.h#L27) |
| `SSDP_PORT` | 1900 | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`SSDP_PORT`](src:src/core/modules/cast/CastConfig.h#L28) |
| `SSDP_ST` | "urn:dial-multiscreen-org:service:dial:1" | cpp_define | Cast/DIAL service configuration (CastConfig.h) | [`SSDP_ST`](src:src/core/modules/cast/CastConfig.h#L29) |
| `CAST_SERVER_THREAD_POOL_SIZE` | 5 | cpp_define | Cast/DIAL module (CastServer.cpp) | [`CAST_SERVER_THREAD_POOL_SIZE`](src:src/core/modules/cast/CastServer.cpp#L34) |
| `CAST_DIAL_BUFFER_SIZE` | 256 | cpp_define | Cast/DIAL module (DIALRunnable.cpp) | [`CAST_DIAL_BUFFER_SIZE`](src:src/core/modules/cast/DIALRunnable.cpp#L31) |
| `MAX_BUFFER_SIZE` | 5000 | cpp_define | Cast/DIAL module (SSDPRunnable.cpp) | [`MAX_BUFFER_SIZE`](src:src/core/modules/cast/SSDPRunnable.cpp#L29) |
| `RECV_SLEEP_MS` | 300 | cpp_define | Cast/DIAL module (SSDPRunnable.cpp) | [`RECV_SLEEP_MS`](src:src/core/modules/cast/SSDPRunnable.cpp#L30) |
| `IDB_LOCAL_STORAGE_DIR_PATH` | "/indexedDB" | cpp_define | IndexedDB module (IDBConfig.h) | [`IDB_LOCAL_STORAGE_DIR_PATH`](src:src/core/modules/indexeddb/IDBConfig.h#L27) |
| `OVERRIDE` | N/A | cpp_define | IndexedDB module (IDBOpenDBRequest.h) | [`OVERRIDE`](src:src/core/modules/indexeddb/IDBOpenDBRequest.h#L62) |
| `VIRTUAL` | N/A | cpp_define | IndexedDB module (IDBOpenDBRequest.h) | [`VIRTUAL`](src:src/core/modules/indexeddb/IDBOpenDBRequest.h#L61) |
| `OVERRIDE` | N/A | cpp_define | IndexedDB module (IDBRequest.h) | [`OVERRIDE`](src:src/core/modules/indexeddb/IDBRequest.h#L86) |
| `VIRTUAL` | N/A | cpp_define | IndexedDB module (IDBRequest.h) | [`VIRTUAL`](src:src/core/modules/indexeddb/IDBRequest.h#L85) |
| `STARFISH_MAX_MEDIASOURCE_BUFFERSPACE` | 8 * 1024 * 1024 | cpp_define | Media Source buffering (MediaSource.h) | [`STARFISH_MAX_MEDIASOURCE_BUFFERSPACE`](src:src/core/modules/mediasource/MediaSource.h#L26) |
| `STARFISH_MAX_MEDIASOURCE_BUFFERSPACE_1080P` | 16 * 1024 * 1024 | cpp_define | Media Source buffering (MediaSource.h) | [`STARFISH_MAX_MEDIASOURCE_BUFFERSPACE_1080P`](src:src/core/modules/mediasource/MediaSource.h#L30) |
| `STARFISH_MAX_MEDIASOURCE_BUFFERSPACE_4K` | 60 * 1024 * 1024 | cpp_define | Media Source buffering (MediaSource.h) | [`STARFISH_MAX_MEDIASOURCE_BUFFERSPACE_4K`](src:src/core/modules/mediasource/MediaSource.h#L34) |
| `STARFISH_FRAME_EVICTION_BACKWARD_DUR` | 500 | cpp_define | Media Source buffering (SourceBuffer.cpp) | [`STARFISH_FRAME_EVICTION_BACKWARD_DUR`](src:src/core/modules/mediasource/SourceBuffer.cpp#L44) |
| `OVERRIDE` | N/A | cpp_define | WebRTC module (RTCDataChannel.h) | [`OVERRIDE`](src:src/core/modules/mediastream/RTCDataChannel.h#L88) |
| `VIRTUAL` | N/A | cpp_define | WebRTC module (RTCDataChannel.h) | [`VIRTUAL`](src:src/core/modules/mediastream/RTCDataChannel.h#L87) |
| `OVERRIDE` | N/A | cpp_define | WebRTC module (RTCDtlsTransport.h) | [`OVERRIDE`](src:src/core/modules/mediastream/RTCDtlsTransport.h#L58) |
| `VIRTUAL` | N/A | cpp_define | WebRTC module (RTCDtlsTransport.h) | [`VIRTUAL`](src:src/core/modules/mediastream/RTCDtlsTransport.h#L57) |
| `OVERRIDE` | N/A | cpp_define | WebRTC module (RTCPeerConnection.h) | [`OVERRIDE`](src:src/core/modules/mediastream/RTCPeerConnection.h#L377) |
| `STARFISH_WEBRTC_DEBUG` | N/A | cpp_define | WebRTC module (RTCPeerConnection.h) | [`STARFISH_WEBRTC_DEBUG`](src:src/core/modules/mediastream/RTCPeerConnection.h#L45) |
| `VIRTUAL` | N/A | cpp_define | WebRTC module (RTCPeerConnection.h) | [`VIRTUAL`](src:src/core/modules/mediastream/RTCPeerConnection.h#L376) |
| `OVERRIDE` | N/A | cpp_define | WebRTC module (RTCSctpTransport.h) | [`OVERRIDE`](src:src/core/modules/mediastream/RTCSctpTransport.h#L55) |
| `VIRTUAL` | N/A | cpp_define | WebRTC module (RTCSctpTransport.h) | [`VIRTUAL`](src:src/core/modules/mediastream/RTCSctpTransport.h#L54) |
| `OVERRIDE` | N/A | cpp_define | WebSocket module (WebSocket.h) | [`OVERRIDE`](src:src/core/modules/networking/WebSocket.h#L94) |
| `VIRTUAL` | N/A | cpp_define | WebSocket module (WebSocket.h) | [`VIRTUAL`](src:src/core/modules/networking/WebSocket.h#L93) |
| `DELTA_EPOCH_IN_MICROSECS` | 11644473600000000Ui64 | cpp_define | Profiling module (Profiling.cpp) | [`DELTA_EPOCH_IN_MICROSECS`](src:src/core/modules/profiling/Profiling.cpp#L53) |
| `DELTA_EPOCH_IN_MICROSECS` | 11644473600000000ULL | cpp_define | Profiling module (Profiling.cpp) | [`DELTA_EPOCH_IN_MICROSECS`](src:src/core/modules/profiling/Profiling.cpp#L55) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Profiling module (Profiling.h) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/core/modules/profiling/Profiling.h#L104) |
| `MOUSE_MOVE_DRAG_EVENT_THRESHOLD` | 16 | cpp_define | Renderer event handling (Renderer.cpp) | [`MOUSE_MOVE_DRAG_EVENT_THRESHOLD`](src:src/core/modules/renderer/Renderer.cpp#L48) |
| `MOUSE_MOVE_EVENT_THRESHOLD` | 100 | cpp_define | Renderer event handling (Renderer.cpp) | [`MOUSE_MOVE_EVENT_THRESHOLD`](src:src/core/modules/renderer/Renderer.cpp#L44) |
| `STARFISH_CURL_HANDLE_CACHE_CLEAR_TIMEOUT_IN_MS` | 5000 | cpp_define | Resource request handling (NetworkURLResourceRequestJobDelegate.cpp) | [`STARFISH_CURL_HANDLE_CACHE_CLEAR_TIMEOUT_IN_MS`](src:src/core/modules/resource_request/NetworkURLResourceRequestJobDelegate.cpp#L54) |
| `SERVICE_WORKER_THREAD_POOL_SIZE` | 1 | cpp_define | Service Worker module (ServiceWorkerProcessManager.cpp) | [`SERVICE_WORKER_THREAD_POOL_SIZE`](src:src/core/modules/serviceworker/client/ServiceWorkerProcessManager.cpp#L77) |
| `OVERRIDE` | N/A | cpp_define | Shared Worker module (SharedWorkerGlobalScope.h) | [`OVERRIDE`](src:src/core/modules/sharedworker/host/SharedWorkerGlobalScope.h#L68) |
| `VIRTUAL` | N/A | cpp_define | Shared Worker module (SharedWorkerGlobalScope.h) | [`VIRTUAL`](src:src/core/modules/sharedworker/host/SharedWorkerGlobalScope.h#L67) |
| `OVERRIDE` | N/A | cpp_define | Speech synthesis module (SpeechSynthesis.h) | [`OVERRIDE`](src:src/core/modules/tts/SpeechSynthesis.h#L188) |
| `VIRTUAL` | N/A | cpp_define | Speech synthesis module (SpeechSynthesis.h) | [`VIRTUAL`](src:src/core/modules/tts/SpeechSynthesis.h#L187) |
| `OVERRIDE` | N/A | cpp_define | Web Audio module (AudioScheduledSourceNode.h) | [`OVERRIDE`](src:src/core/modules/webaudio/AudioScheduledSourceNode.h#L41) |
| `VIRTUAL` | N/A | cpp_define | Web Audio module (AudioScheduledSourceNode.h) | [`VIRTUAL`](src:src/core/modules/webaudio/AudioScheduledSourceNode.h#L40) |
| `OVERRIDE` | N/A | cpp_define | Web Audio module (BaseAudioContext.h) | [`OVERRIDE`](src:src/core/modules/webaudio/BaseAudioContext.h#L130) |
| `VIRTUAL` | N/A | cpp_define | Web Audio module (BaseAudioContext.h) | [`VIRTUAL`](src:src/core/modules/webaudio/BaseAudioContext.h#L129) |
| `OVERRIDE` | N/A | cpp_define | Web Worker module (AbstractWorker.h) | [`OVERRIDE`](src:src/core/modules/worker/AbstractWorker.h#L44) |
| `VIRTUAL` | N/A | cpp_define | Web Worker module (AbstractWorker.h) | [`VIRTUAL`](src:src/core/modules/worker/AbstractWorker.h#L43) |
| `OVERRIDE` | N/A | cpp_define | Web Worker module (DedicatedWorkerGlobalScope.h) | [`OVERRIDE`](src:src/core/modules/worker/DedicatedWorkerGlobalScope.h#L65) |
| `VIRTUAL` | N/A | cpp_define | Web Worker module (DedicatedWorkerGlobalScope.h) | [`VIRTUAL`](src:src/core/modules/worker/DedicatedWorkerGlobalScope.h#L64) |
| `IO_EVENT_POLLING_TIMEOUT_MS` | 300 | cpp_define | Web Worker module (PerProcess.cpp) | [`IO_EVENT_POLLING_TIMEOUT_MS`](src:src/core/modules/worker/PerProcess.cpp#L40) |
| `OVERRIDE` | N/A | cpp_define | Web Worker module (Worker.h) | [`OVERRIDE`](src:src/core/modules/worker/Worker.h#L59) |
| `VIRTUAL` | N/A | cpp_define | Web Worker module (Worker.h) | [`VIRTUAL`](src:src/core/modules/worker/Worker.h#L58) |
| `WORKER_IPC_PROCESS_NAME` | "ipc" | cpp_define | Web Worker module (WorkerConfig.h) | [`WORKER_IPC_PROCESS_NAME`](src:src/core/modules/worker/WorkerConfig.h#L27) |
| `OVERRIDE` | N/A | cpp_define | Web Worker module (WorkerGlobalScope.h) | [`OVERRIDE`](src:src/core/modules/worker/WorkerGlobalScope.h#L153) |
| `VIRTUAL` | N/A | cpp_define | Web Worker module (WorkerGlobalScope.h) | [`VIRTUAL`](src:src/core/modules/worker/WorkerGlobalScope.h#L152) |
| `COLOR_RECV` | "\033[0;32m" | cpp_define | Worker IPC socket networking (Connection.cpp) | [`COLOR_RECV`](src:src/core/modules/worker/util/network/Connection.cpp#L41) |
| `COLOR_RESET` | "\033[0m" | cpp_define | Worker IPC socket networking (Connection.cpp) | [`COLOR_RESET`](src:src/core/modules/worker/util/network/Connection.cpp#L42) |
| `COLOR_SEND` | "\033[0;36m" | cpp_define | Worker IPC socket networking (Connection.cpp) | [`COLOR_SEND`](src:src/core/modules/worker/util/network/Connection.cpp#L40) |
| `RECV_TIMEOUT` | 1000 | cpp_define | Worker IPC socket networking (Connection.cpp) | [`RECV_TIMEOUT`](src:src/core/modules/worker/util/network/Connection.cpp#L39) |
| `MAX_LISTEN_SOCKET` | 50 | cpp_define | Worker IPC socket networking (IORunnable.cpp) | [`MAX_LISTEN_SOCKET`](src:src/core/modules/worker/util/network/IORunnable.cpp#L35) |
| `SCK_DONTWAIT` | 1 | cpp_define | Worker IPC socket networking (SocketNN.h) | [`SCK_DONTWAIT`](src:src/core/modules/worker/util/network/SocketNN.h#L28) |
| `SCK_WAIT` | 0 | cpp_define | Worker IPC socket networking (SocketNN.h) | [`SCK_WAIT`](src:src/core/modules/worker/util/network/SocketNN.h#L27) |
| `SOCKETNN_INVALID_END_POINT` | -1 | cpp_define | Worker IPC socket networking (SocketNN.h) | [`SOCKETNN_INVALID_END_POINT`](src:src/core/modules/worker/util/network/SocketNN.h#L29) |
| `STARFISH_TOUCH_SLOP_PX` | 20.0 | cpp_define | Page/WebView core (BrowsingContext.cpp) | [`STARFISH_TOUCH_SLOP_PX`](src:src/core/page/BrowsingContext.cpp#L88) |
| `STARFISH_THREAD_POOL_SIZE` | 6 | cpp_define | Page/WebView core (WebBase.cpp) | [`STARFISH_THREAD_POOL_SIZE`](src:src/core/page/WebBase.cpp#L62) |
| `ANNOTATE_BLUE` | 0xff00001b | cpp_define | Page/WebView core (WebView.cpp) | [`ANNOTATE_BLUE`](src:src/core/page/WebView.cpp#L98) |
| `ANNOTATE_SETUP` | N/A | cpp_define | Page/WebView core (WebView.cpp) | [`ANNOTATE_SETUP`](src:src/core/page/WebView.cpp#L95) |
| `STARFISH_FILLING_GRAPHICS_BUFFER_TIME_LIMIT` | 100 | cpp_define | Page/WebView core (WebView.cpp) | [`STARFISH_FILLING_GRAPHICS_BUFFER_TIME_LIMIT`](src:src/core/page/WebView.cpp#L236) |
| `STARFISH_FILLING_GRAPHICS_BUFFER_TIME_LIMIT` | 10 | cpp_define | Page/WebView core (WebView.cpp) | [`STARFISH_FILLING_GRAPHICS_BUFFER_TIME_LIMIT`](src:src/core/page/WebView.cpp#L238) |
| `STARFISH_IMAGE_DECODE_THREAD_THREAD_POOL_SIZE` | 4 | cpp_define | Page/WebView core (WebView.cpp) | [`STARFISH_IMAGE_DECODE_THREAD_THREAD_POOL_SIZE`](src:src/core/page/WebView.cpp#L377) |
| `OVERRIDE` | N/A | cpp_define | Page/WebView core (Window.h) | [`OVERRIDE`](src:src/core/page/Window.h#L316) |
| `VIRTUAL` | N/A | cpp_define | Page/WebView core (Window.h) | [`VIRTUAL`](src:src/core/page/Window.h#L315) |
| `CSSTOKENSTRING_BUILTIN_BUFFER_SIZE` | 24 | cpp_define | CSS style engine (CSSParser.h) | [`CSSTOKENSTRING_BUILTIN_BUFFER_SIZE`](src:src/core/style/CSSParser.h#L1256) |
| `CSSTOKEN_POOL_INITIAL_SIZE` | 24 | cpp_define | CSS style engine (CSSParser.h) | [`CSSTOKEN_POOL_INITIAL_SIZE`](src:src/core/style/CSSParser.h#L1708) |
| `DIV` | false | cpp_define | CSS style engine (CalcData.cpp) | [`DIV`](src:src/core/style/CalcData.cpp#L103) |
| `MUL` | true | cpp_define | CSS style engine (CalcData.cpp) | [`MUL`](src:src/core/style/CalcData.cpp#L102) |
| `ENABLE_PARALLEL_BLUR` | 0 | cpp_define | CSS style engine (FilterFunctions.cpp) | [`ENABLE_PARALLEL_BLUR`](src:src/core/style/FilterFunctions.cpp#L29) |
| `CACHEABLE_GRADIENT_ITEM_EXTENT` | (25.0f * 25.0f) | cpp_define | CSS style engine (GradientData.h) | [`CACHEABLE_GRADIENT_ITEM_EXTENT`](src:src/core/style/GradientData.h#L27) |
| `CACHEABLE_GRADIENT_ITEM_EXTENT` | (256.0f * 256.0f) | cpp_define | CSS style engine (GradientData.h) | [`CACHEABLE_GRADIENT_ITEM_EXTENT`](src:src/core/style/GradientData.h#L31) |
| `MAX_TYPE_NAME` | 30 | cpp_define | Core utility (Archivable.h) | [`MAX_TYPE_NAME`](src:src/core/util/Archivable.h#L48) |
| `CURRENT` | (*TOP.value) | cpp_define | Core utility (Archiver.cpp) | [`CURRENT`](src:src/core/util/Archiver.cpp#L78) |
| `DOCUMENT` | reinterpret_cast<rapidjson::Document*>(mDocument) | cpp_define | Core utility (Archiver.cpp) | [`DOCUMENT`](src:src/core/util/Archiver.cpp#L75) |
| `STACK` | (reinterpret_cast<JsonReaderStack*>(mStack)) | cpp_define | Core utility (Archiver.cpp) | [`STACK`](src:src/core/util/Archiver.cpp#L76) |
| `STREAM` | reinterpret_cast<rapidjson::StringBuffer*>(mStream) | cpp_define | Core utility (Archiver.cpp) | [`STREAM`](src:src/core/util/Archiver.cpp#L360) |
| `TOP` | (STACK->top()) | cpp_define | Core utility (Archiver.cpp) | [`TOP`](src:src/core/util/Archiver.cpp#L77) |
| `WRITER` | reinterpret_cast<rapidjson::PrettyWriter<rapidjson::StringBuffer>*>(mWriter) | cpp_define | Core utility (Archiver.cpp) | [`WRITER`](src:src/core/util/Archiver.cpp#L358) |
| `NUM_SUPPORTED_CRYPTO_ALGORITHM_TYPE` | 3 | cpp_define | Core utility (Cryptographic.h) | [`NUM_SUPPORTED_CRYPTO_ALGORITHM_TYPE`](src:src/core/util/Cryptographic.h#L32) |
| `ID_INITIAL_VALUE` | 0 | cpp_define | Core utility (Id.h) | [`ID_INITIAL_VALUE`](src:src/core/util/Id.h#L29) |
| `ARGS_NOT_ENOUGH` | "needs %s parameter, but only %s present." | cpp_define | Script binding error message template (Messages.h) | [`ARGS_NOT_ENOUGH`](src:src/core/util/Messages.h#L32) |
| `ARG_TYPE_IS_NONFINITE` | "The provided double value is non-finite" | cpp_define | Script binding error message template (Messages.h) | [`ARG_TYPE_IS_NONFINITE`](src:src/core/util/Messages.h#L33) |
| `ARG_TYPE_MISMATCH` | "parameter %s ('%s') is not a(n) %s." | cpp_define | Script binding error message template (Messages.h) | [`ARG_TYPE_MISMATCH`](src:src/core/util/Messages.h#L34) |
| `ARG_TYPE_MISMATCH_2` | "parameter %s ('%s') must be either a '%s' or '%s' element." | cpp_define | Script binding error message template (Messages.h) | [`ARG_TYPE_MISMATCH_2`](src:src/core/util/Messages.h#L35) |
| `ARG_TYPE_MISMATCH_WITH_ENUM` | "The provided value is not a valid enum value of type %s." | cpp_define | Script binding error message template (Messages.h) | [`ARG_TYPE_MISMATCH_WITH_ENUM`](src:src/core/util/Messages.h#L40) |
| `ARG_TYPE_MISMATCH_WITH_INDEXABLE_TYPE` | "The parameter %s ('%s') is neither an array, nor does it have indexed " "properties." | cpp_define | Script binding error message template (Messages.h) | [`ARG_TYPE_MISMATCH_WITH_INDEXABLE_TYPE`](src:src/core/util/Messages.h#L37) |
| `CALLED_CONSTRUCTOR_WITHOUT_NEW` | "Constructor '%s' requires 'new'" | cpp_define | Script binding error message template (Messages.h) | [`CALLED_CONSTRUCTOR_WITHOUT_NEW`](src:src/core/util/Messages.h#L25) |
| `EXCEED_MAX_BOUNDARY` | "The value provided (%s) is greater than the maximum boundary (%s)." | cpp_define | Script binding error message template (Messages.h) | [`EXCEED_MAX_BOUNDARY`](src:src/core/util/Messages.h#L54) |
| `EXCEED_MIN_BOUNDARY` | "The value provided (%s) is less than the minimum boundary (%s)." | cpp_define | Script binding error message template (Messages.h) | [`EXCEED_MIN_BOUNDARY`](src:src/core/util/Messages.h#L52) |
| `FAILED_TO_CONSTRUCT` | "Failed to construct '%s': %s" | cpp_define | Script binding error message template (Messages.h) | [`FAILED_TO_CONSTRUCT`](src:src/core/util/Messages.h#L26) |
| `FAILED_TO_EXECUTE` | "Failed to execute '%s' on '%s': %s" | cpp_define | Script binding error message template (Messages.h) | [`FAILED_TO_EXECUTE`](src:src/core/util/Messages.h#L27) |
| `FAILED_TO_SET_PROPERTY` | "Failed to set the '%s' property on '%s': %s" | cpp_define | Script binding error message template (Messages.h) | [`FAILED_TO_SET_PROPERTY`](src:src/core/util/Messages.h#L28) |
| `ILLEGAL_INVOKE` | "Illegal invocation" | cpp_define | Script binding error message template (Messages.h) | [`ILLEGAL_INVOKE`](src:src/core/util/Messages.h#L29) |
| `INVALID_DATA_CLONE` | "'%s' could not be cloned." | cpp_define | Script binding error message template (Messages.h) | [`INVALID_DATA_CLONE`](src:src/core/util/Messages.h#L47) |
| `INVALID_SIZE` | "The value provided %s, which is an invalid size." | cpp_define | Script binding error message template (Messages.h) | [`INVALID_SIZE`](src:src/core/util/Messages.h#L45) |
| `INVALID_TARGET_ORIGIN` | "Invalid target origin '%s' in a call to '%s'" | cpp_define | Script binding error message template (Messages.h) | [`INVALID_TARGET_ORIGIN`](src:src/core/util/Messages.h#L46) |
| `NOT_POSITIVE` | "The value provided (%s) is not positive or 0." | cpp_define | Script binding error message template (Messages.h) | [`NOT_POSITIVE`](src:src/core/util/Messages.h#L51) |
| `ORIGINS_ARE_NOT_MATCHED` | "The target origin provided('%s') does not match the recipient window's " "origin('%s')" | cpp_define | Script binding error message template (Messages.h) | [`ORIGINS_ARE_NOT_MATCHED`](src:src/core/util/Messages.h#L48) |
| `QUERY_SELECTOR_IS_EMPTY` | "The provided selector is empty." | cpp_define | Script binding error message template (Messages.h) | [`QUERY_SELECTOR_IS_EMPTY`](src:src/core/util/Messages.h#L44) |
| `SIGNATURE_NOT_FOUND` | "No function was found that matched the signature provided." | cpp_define | Script binding error message template (Messages.h) | [`SIGNATURE_NOT_FOUND`](src:src/core/util/Messages.h#L42) |
| `CHECK_REF_COUNTED_LIFECYCLE` | 0 | cpp_define | Core utility (RefCounted.h) | [`CHECK_REF_COUNTED_LIFECYCLE`](src:src/core/util/RefCounted.h#L31) |
| `CHECK_REF_COUNTED_LIFECYCLE` | 1 | cpp_define | Core utility (RefCounted.h) | [`CHECK_REF_COUNTED_LIFECYCLE`](src:src/core/util/RefCounted.h#L33) |
| `STRING_BUILDER_INLINE_STORAGE_MAX` | 64 | cpp_define | Core utility (String.h) | [`STRING_BUILDER_INLINE_STORAGE_MAX`](src:src/core/util/String.h#L1604) |
| `CLR_BBLUE` | "\033[01;34m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BBLUE`](src:src/core/util/debug/Trace.cpp#L50) |
| `CLR_BCYAN` | "\033[01;36m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BCYAN`](src:src/core/util/debug/Trace.cpp#L52) |
| `CLR_BGREEN` | "\033[01;32m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BGREEN`](src:src/core/util/debug/Trace.cpp#L53) |
| `CLR_BLACK` | "\033[0;30m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BLACK`](src:src/core/util/debug/Trace.cpp#L42) |
| `CLR_BLUE` | "\033[0;34m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BLUE`](src:src/core/util/debug/Trace.cpp#L44) |
| `CLR_BMAGENTA` | "\033[01;35m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BMAGENTA`](src:src/core/util/debug/Trace.cpp#L51) |
| `CLR_BRED` | "\033[01;31m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BRED`](src:src/core/util/debug/Trace.cpp#L48) |
| `CLR_BYELLOW` | "\033[01;33m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_BYELLOW`](src:src/core/util/debug/Trace.cpp#L49) |
| `CLR_CYAN` | "\033[0;36m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_CYAN`](src:src/core/util/debug/Trace.cpp#L46) |
| `CLR_DARKGREY` | "\033[01;30m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_DARKGREY`](src:src/core/util/debug/Trace.cpp#L47) |
| `CLR_DIM` | "\033[0;2m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_DIM`](src:src/core/util/debug/Trace.cpp#L36) |
| `CLR_GREEN` | "\033[0;32m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_GREEN`](src:src/core/util/debug/Trace.cpp#L40) |
| `CLR_GREY` | "\033[0;37m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_GREY`](src:src/core/util/debug/Trace.cpp#L41) |
| `CLR_MAGENTA` | "\033[0;35m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_MAGENTA`](src:src/core/util/debug/Trace.cpp#L45) |
| `CLR_RED` | "\033[0;31m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_RED`](src:src/core/util/debug/Trace.cpp#L39) |
| `CLR_REDBG` | "\033[0;41m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_REDBG`](src:src/core/util/debug/Trace.cpp#L55) |
| `CLR_RESET` | "\033[0m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_RESET`](src:src/core/util/debug/Trace.cpp#L35) |
| `CLR_WHITE` | "\033[01;37m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_WHITE`](src:src/core/util/debug/Trace.cpp#L54) |
| `CLR_YELLOW` | "\033[0;33m" | cpp_define | Debug trace output (Trace.cpp) | [`CLR_YELLOW`](src:src/core/util/debug/Trace.cpp#L43) |
| `TRACE_ID_LENGTH_LIMIT` | 10 | cpp_define | Debug trace output (Trace.cpp) | [`TRACE_ID_LENGTH_LIMIT`](src:src/core/util/debug/Trace.cpp#L34) |
| `TYPE_LENGTH_LIMIT` | 5 | cpp_define | Debug trace output (Trace.cpp) | [`TYPE_LENGTH_LIMIT`](src:src/core/util/debug/Trace.cpp#L33) |
| `ENABLE_TRACE` | N/A | cpp_define | Debug trace output (Trace.h) | [`ENABLE_TRACE`](src:src/core/util/debug/Trace.h#L33) |
| `CAIRO_FORMAT` | CAIRO_FORMAT_ARGB32 | cpp_define | Compositor/canvas platform layer (CanvasCairo.cpp) | [`CAIRO_FORMAT`](src:src/platform/canvas/CanvasCairo.cpp#L68) |
| `CAIRO_FORMAT` | CAIRO_FORMAT_ARGB32 | cpp_define | Compositor/canvas platform layer (CompositorCairo.cpp) | [`CAIRO_FORMAT`](src:src/platform/canvas/CompositorCairo.cpp#L38) |
| `EGL_ATTRIBUTE_MAX` | 50 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_ATTRIBUTE_MAX`](src:src/platform/canvas/CompositorGL.cpp#L188) |
| `EGL_DMA_BUF_PLANE3_FD_EXT` | 0x3440 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_DMA_BUF_PLANE3_FD_EXT`](src:src/platform/canvas/CompositorGL.cpp#L180) |
| `EGL_DMA_BUF_PLANE3_OFFSET_EXT` | 0x3441 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_DMA_BUF_PLANE3_OFFSET_EXT`](src:src/platform/canvas/CompositorGL.cpp#L183) |
| `EGL_DMA_BUF_PLANE3_PITCH_EXT` | 0x3442 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_DMA_BUF_PLANE3_PITCH_EXT`](src:src/platform/canvas/CompositorGL.cpp#L186) |
| `EGL_IMAGE_PRESERVED_KHR` | 0x30D2 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_IMAGE_PRESERVED_KHR`](src:src/platform/canvas/CompositorGL.cpp#L168) |
| `EGL_NATIVE_SURFACE_TIZEN` | 0x32A1 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_NATIVE_SURFACE_TIZEN`](src:src/platform/canvas/CompositorGL.cpp#L169) |
| `EGL_NATIVE_SURFACE_TIZEN` | 0x32A1 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_NATIVE_SURFACE_TIZEN`](src:src/platform/canvas/CompositorGL.cpp#L190) |
| `EGL_NONE` | 0x3038 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_NONE`](src:src/platform/canvas/CompositorGL.cpp#L167) |
| `EGL_TRUE` | 1 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EGL_TRUE`](src:src/platform/canvas/CompositorGL.cpp#L166) |
| `EVAS_GL_IMAGE_PRESERVED` | 0x30D2 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EVAS_GL_IMAGE_PRESERVED`](src:src/platform/canvas/CompositorGL.cpp#L161) |
| `EVAS_GL_NATIVE_SURFACE_TIZEN` | 0x32A1 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`EVAS_GL_NATIVE_SURFACE_TIZEN`](src:src/platform/canvas/CompositorGL.cpp#L162) |
| `GAUSSIAN_KERNEL_HALF_WIDTH` | 11 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`GAUSSIAN_KERNEL_HALF_WIDTH`](src:src/platform/canvas/CompositorGL.cpp#L2250) |
| `GAUSSIAN_KERNEL_STEP` | 0.2 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`GAUSSIAN_KERNEL_STEP`](src:src/platform/canvas/CompositorGL.cpp#L2251) |
| `GL_DEBUG_OUTPUT` | 0x92E0 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`GL_DEBUG_OUTPUT`](src:src/platform/canvas/CompositorGL.cpp#L2662) |
| `GL_DEBUG_OUTPUT_SYNCHRONOUS` | 0x8242 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`GL_DEBUG_OUTPUT_SYNCHRONOUS`](src:src/platform/canvas/CompositorGL.cpp#L2665) |
| `MIN_MAX_TEXTURE_SIZE` | 2048 | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`MIN_MAX_TEXTURE_SIZE`](src:src/platform/canvas/CompositorGL.cpp#L295) |
| `RRCLIP_EGL_SAMPLER_PREAMBLE` | "#extension GL_OES_EGL_image_external : require\n" "uniform samplerExternalOES uTexture;\n" | cpp_define | Compositor/canvas platform layer (CompositorGL.cpp) | [`RRCLIP_EGL_SAMPLER_PREAMBLE`](src:src/platform/canvas/CompositorGL.cpp#L2053) |
| `UBLOCK_SUPPLEMENTAL_SYMBOLS_AND_PICTOGRAPHS` | 298 | cpp_define | Font rendering (FontImplCairo.cpp) | [`UBLOCK_SUPPLEMENTAL_SYMBOLS_AND_PICTOGRAPHS`](src:src/platform/canvas/font/FontImplCairo.cpp#L608) |
| `STARFISH_FONT_CAIRO_MIN_ENABLE_KERNING_SIZE` | 48 | cpp_define | Font rendering (FontImplCairo.h) | [`STARFISH_FONT_CAIRO_MIN_ENABLE_KERNING_SIZE`](src:src/platform/canvas/font/FontImplCairo.h#L42) |
| `HB_UNUSED` | N/A | cpp_define | Font rendering (HarfBuzzICU.cpp) | [`HB_UNUSED`](src:src/platform/canvas/font/hb-icu/HarfBuzzICU.cpp#L53) |
| `HB_ICU_H` | N/A | cpp_define | Font rendering (HarfBuzzICU.h) | [`HB_ICU_H`](src:src/platform/canvas/font/hb-icu/HarfBuzzICU.h#L30) |
| `GL_NONE` | 0 | cpp_define | GL/EGL constant (GLTypes.h) | [`GL_NONE`](src:src/platform/canvas/gl/GLTypes.h#L55) |
| `EGL_NO_CONTEXT` | ((EGLContext)0) | cpp_define | GL/EGL constant (GenericGL.cpp) | [`EGL_NO_CONTEXT`](src:src/platform/canvas/gl/GenericGL.cpp#L30) |
| `GLAPIENTRY` | N/A | cpp_define | GL/EGL constant (GenericGL.cpp) | [`GLAPIENTRY`](src:src/platform/canvas/gl/GenericGL.cpp#L48) |
| `EGL_EGLEXT_PROTOTYPES` | N/A | cpp_define | GL/EGL constant (IncludeGL.h) | [`EGL_EGLEXT_PROTOTYPES`](src:src/platform/canvas/gl/IncludeGL.h#L42) |
| `GL_ALPHA` | 0x1906 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_ALPHA`](src:src/platform/canvas/gl/IncludeGL.h#L118) |
| `GL_BGRA_EXT` | 0x80E1 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_BGRA_EXT`](src:src/platform/canvas/gl/IncludeGL.h#L61) |
| `GL_BLUE` | 0x1905 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_BLUE`](src:src/platform/canvas/gl/IncludeGL.h#L115) |
| `GL_DEPTH_STENCIL` | 0x84F9 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_DEPTH_STENCIL`](src:src/platform/canvas/gl/IncludeGL.h#L85) |
| `GL_GLEXT_PROTOTYPES` | N/A | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_GLEXT_PROTOTYPES`](src:src/platform/canvas/gl/IncludeGL.h#L27) |
| `GL_GLEXT_PROTOTYPES` | N/A | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_GLEXT_PROTOTYPES`](src:src/platform/canvas/gl/IncludeGL.h#L43) |
| `GL_GREEN` | 0x1904 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_GREEN`](src:src/platform/canvas/gl/IncludeGL.h#L112) |
| `GL_MAJOR_VERSION` | 0x821B | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_MAJOR_VERSION`](src:src/platform/canvas/gl/IncludeGL.h#L65) |
| `GL_MINOR_VERSION` | 0x821C | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_MINOR_VERSION`](src:src/platform/canvas/gl/IncludeGL.h#L69) |
| `GL_R8` | 0x8229 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_R8`](src:src/platform/canvas/gl/IncludeGL.h#L121) |
| `GL_RED` | 0x1903 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_RED`](src:src/platform/canvas/gl/IncludeGL.h#L109) |
| `GL_TEXTURE_EXTERNAL_OES` | 0x8D65 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_TEXTURE_EXTERNAL_OES`](src:src/platform/canvas/gl/IncludeGL.h#L57) |
| `GL_TEXTURE_SWIZZLE_A` | 0x8E45 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_TEXTURE_SWIZZLE_A`](src:src/platform/canvas/gl/IncludeGL.h#L102) |
| `GL_TEXTURE_SWIZZLE_B` | 0x8E44 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_TEXTURE_SWIZZLE_B`](src:src/platform/canvas/gl/IncludeGL.h#L99) |
| `GL_TEXTURE_SWIZZLE_G` | 0x8E43 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_TEXTURE_SWIZZLE_G`](src:src/platform/canvas/gl/IncludeGL.h#L96) |
| `GL_TEXTURE_SWIZZLE_R` | 0x8E42 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_TEXTURE_SWIZZLE_R`](src:src/platform/canvas/gl/IncludeGL.h#L93) |
| `GL_UNPACK_ROW_LENGTH` | 0x0CF2 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_UNPACK_ROW_LENGTH`](src:src/platform/canvas/gl/IncludeGL.h#L73) |
| `GL_UNPACK_SKIP_PIXELS` | 0x0CF4 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_UNPACK_SKIP_PIXELS`](src:src/platform/canvas/gl/IncludeGL.h#L81) |
| `GL_UNPACK_SKIP_ROWS` | 0x0CF3 | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_UNPACK_SKIP_ROWS`](src:src/platform/canvas/gl/IncludeGL.h#L77) |
| `GL_UNSIGNED_INT_24_8` | 0x84FA | cpp_define | GL/EGL constant (IncludeGL.h) | [`GL_UNSIGNED_INT_24_8`](src:src/platform/canvas/gl/IncludeGL.h#L89) |
| `TEXTURE_SWIZZLE_RGBA` | 0x8E46 | cpp_define | GL/EGL constant (IncludeGL.h) | [`TEXTURE_SWIZZLE_RGBA`](src:src/platform/canvas/gl/IncludeGL.h#L105) |
| `STARFISH_RESOURCE_CACHE_SIZE` | 1024 * 1024 * 4 | cpp_define | Resource loader (ResourceLoader.cpp) | [`STARFISH_RESOURCE_CACHE_SIZE`](src:src/platform/loader/ResourceLoader.cpp#L45) |
| `MAX_PORT_DIGITS` | 5 | cpp_define | Resource loader (ResourceURL.cpp) | [`MAX_PORT_DIGITS`](src:src/platform/loader/ResourceURL.cpp#L25) |
| `MAX_PORT_NUMBER` | 65535 | cpp_define | Resource loader (ResourceURL.cpp) | [`MAX_PORT_NUMBER`](src:src/platform/loader/ResourceURL.cpp#L26) |
| `MINUMUM_ANIMATOR_WAIT_TIME` | 3000 // us | cpp_define | Timer/message loop (TimerLibUV.cpp) | [`MINUMUM_ANIMATOR_WAIT_TIME`](src:src/platform/message_loop/TimerLibUV.cpp#L137) |
| `STARFISH_VIDEO_HEIGHT_WHEN_VIDEO_NOT_EXISTS` | 150 | cpp_define | Media player tuning (MediaPlayer.h) | [`STARFISH_VIDEO_HEIGHT_WHEN_VIDEO_NOT_EXISTS`](src:src/platform/multimedia/MediaPlayer.h#L25) |
| `STARFISH_VIDEO_WIDTH_WHEN_VIDEO_NOT_EXISTS` | 300 | cpp_define | Media player tuning (MediaPlayer.h) | [`STARFISH_VIDEO_WIDTH_WHEN_VIDEO_NOT_EXISTS`](src:src/platform/multimedia/MediaPlayer.h#L24) |
| `STARFISH_ESPP_AUDIO_BUFFER_SIZE` | (768 * 1024) | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_AUDIO_BUFFER_SIZE`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L66) |
| `STARFISH_ESPP_DEFAULT_FRAMERATE_DEN` | 100 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_DEFAULT_FRAMERATE_DEN`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L117) |
| `STARFISH_ESPP_DEFAULT_FRAMERATE_NUM` | 2997 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_DEFAULT_FRAMERATE_NUM`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L116) |
| `STARFISH_ESPP_FEED_WAIT_US` | (1000 * 25) | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_FEED_WAIT_US`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L62) |
| `STARFISH_ESPP_MAX_AV_DIFF_IN_MS` | 1500 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_MAX_AV_DIFF_IN_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L60) |
| `STARFISH_ESPP_MAX_SKIP_AHEAD_MS` | 30000 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_MAX_SKIP_AHEAD_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L105) |
| `STARFISH_ESPP_MIN_BYTE_THRESHOLD` | 10 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_MIN_BYTE_THRESHOLD`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L77) |
| `STARFISH_ESPP_SEEK_IDR_MAX_LOOKAHEAD_MS` | 20000 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_SEEK_IDR_MAX_LOOKAHEAD_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L97) |
| `STARFISH_ESPP_SEEK_IDR_MAX_LOOKBACK_MS` | 20000 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_SEEK_IDR_MAX_LOOKBACK_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L85) |
| `STARFISH_ESPP_SUBMIT_BYTES_RATE` | 0.3 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_SUBMIT_BYTES_RATE`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L57) |
| `STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_PREROLL_MS` | 50 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_PREROLL_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L112) |
| `STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_STEADY_MS` | 500 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_SUBMIT_RETRY_BACKOFF_STEADY_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L113) |
| `STARFISH_ESPP_TOTAL_BUFFER_SIZE` | (64 * 1024 * 1024) | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.cpp) | [`STARFISH_ESPP_TOTAL_BUFFER_SIZE`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.cpp#L65) |
| `STARFISH_ESPP_SEEK_WATCHDOG_MS` | 12000 | cpp_define | Media player tuning (MediaPlayerESPlusPlayer.h) | [`STARFISH_ESPP_SEEK_WATCHDOG_MS`](src:src/platform/multimedia/MediaPlayerESPlusPlayer.h#L51) |
| `SEEK_LAND_TOLERANCE_MS` | 5000 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`SEEK_LAND_TOLERANCE_MS`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L144) |
| `STARFISH_DECODE_LOOKAHEAD_MS_DEFAULT` | 400 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_DECODE_LOOKAHEAD_MS_DEFAULT`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L152) |
| `STARFISH_MSE_MIN_MARGIN_IN_MS` | 3000 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_MSE_MIN_MARGIN_IN_MS`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L139) |
| `STARFISH_MSE_SUBMIT_BYTES_RATE` | 0.3 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_MSE_SUBMIT_BYTES_RATE`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L138) |
| `STARFISH_RUN_MSE_THREAD_WAIT_TIME` | 1000 * 25 // 25ms | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_RUN_MSE_THREAD_WAIT_TIME`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L1799) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN` | 100 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L137) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM` | 2997 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L136) |
| `STARFISH_VIDEO_MAX_HEIGHT` | 1080 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_VIDEO_MAX_HEIGHT`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L135) |
| `STARFISH_VIDEO_MAX_WIDTH` | 1920 | cpp_define | Media player tuning (MediaPlayerLinux.cpp) | [`STARFISH_VIDEO_MAX_WIDTH`](src:src/platform/multimedia/MediaPlayerLinux.cpp#L134) |
| `MAX_WAITING_SECONDS_FOR_SEEK_OPERATION` | 30000 | cpp_define | Media player tuning (MediaPlayerLinux.h) | [`MAX_WAITING_SECONDS_FOR_SEEK_OPERATION`](src:src/platform/multimedia/MediaPlayerLinux.h#L26) |
| `STARFISH_RUN_MSE_THREAD` | N/A | cpp_define | Media player tuning (MediaPlayerLinux.h) | [`STARFISH_RUN_MSE_THREAD`](src:src/platform/multimedia/MediaPlayerLinux.h#L29) |
| `STARFISH_MSE_SUBMIT_BYTES_RATE` | 0.3 | cpp_define | Media player tuning (MediaPlayerTV.cpp) | [`STARFISH_MSE_SUBMIT_BYTES_RATE`](src:src/platform/multimedia/MediaPlayerTV.cpp#L49) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN` | 100 | cpp_define | Media player tuning (MediaPlayerTV.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN`](src:src/platform/multimedia/MediaPlayerTV.cpp#L48) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM` | 2997 | cpp_define | Media player tuning (MediaPlayerTV.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM`](src:src/platform/multimedia/MediaPlayerTV.cpp#L47) |
| `STARFISH_VIDEO_MAX_HEIGHT` | 1080 | cpp_define | Media player tuning (MediaPlayerTV.cpp) | [`STARFISH_VIDEO_MAX_HEIGHT`](src:src/platform/multimedia/MediaPlayerTV.cpp#L46) |
| `STARFISH_VIDEO_MAX_WIDTH` | 1920 | cpp_define | Media player tuning (MediaPlayerTV.cpp) | [`STARFISH_VIDEO_MAX_WIDTH`](src:src/platform/multimedia/MediaPlayerTV.cpp#L45) |
| `STARFISH_MSE_MIN_MARGIN_IN_MS` | 3000 | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_MSE_MIN_MARGIN_IN_MS`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L55) |
| `STARFISH_MSE_SUBMIT_BYTES_RATE` | 0.3 | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_MSE_SUBMIT_BYTES_RATE`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L54) |
| `STARFISH_RUN_MSE_THREAD_WAIT_TIME` | 1000 * 25 // 25ms | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_RUN_MSE_THREAD_WAIT_TIME`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L1228) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN` | 100 | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L53) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM` | 2997 | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L52) |
| `STARFISH_VIDEO_MAX_HEIGHT` | 1080 | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_VIDEO_MAX_HEIGHT`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L51) |
| `STARFISH_VIDEO_MAX_WIDTH` | 1920 | cpp_define | Media player tuning (MediaPlayerTizen.cpp) | [`STARFISH_VIDEO_MAX_WIDTH`](src:src/platform/multimedia/MediaPlayerTizen.cpp#L50) |
| `EFL_BETA_API_SUPPORT` | N/A | cpp_define | Media player tuning (MediaPlayerTizen.h) | [`EFL_BETA_API_SUPPORT`](src:src/platform/multimedia/MediaPlayerTizen.h#L36) |
| `MAX_WAITING_SECONDS_FOR_SEEK_OPERATION` | 30000 | cpp_define | Media player tuning (MediaPlayerTizen.h) | [`MAX_WAITING_SECONDS_FOR_SEEK_OPERATION`](src:src/platform/multimedia/MediaPlayerTizen.h#L48) |
| `STARFISH_RUN_MSE_THREAD` | N/A | cpp_define | Media player tuning (MediaPlayerTizen.h) | [`STARFISH_RUN_MSE_THREAD`](src:src/platform/multimedia/MediaPlayerTizen.h#L51) |
| `STARFISH_MSE_SUBMIT_BYTES_RATE` | 0.3 | cpp_define | Media player tuning (MediaPlayerTizenBase.cpp) | [`STARFISH_MSE_SUBMIT_BYTES_RATE`](src:src/platform/multimedia/MediaPlayerTizenBase.cpp#L51) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN` | 100 | cpp_define | Media player tuning (MediaPlayerTizenBase.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_DEN`](src:src/platform/multimedia/MediaPlayerTizenBase.cpp#L50) |
| `STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM` | 2997 | cpp_define | Media player tuning (MediaPlayerTizenBase.cpp) | [`STARFISH_VIDEO_DEFAULT_FRAMERATE_NUM`](src:src/platform/multimedia/MediaPlayerTizenBase.cpp#L49) |
| `STARFISH_VIDEO_MAX_HEIGHT` | 1080 | cpp_define | Media player tuning (MediaPlayerTizenBase.cpp) | [`STARFISH_VIDEO_MAX_HEIGHT`](src:src/platform/multimedia/MediaPlayerTizenBase.cpp#L48) |
| `STARFISH_VIDEO_MAX_WIDTH` | 1920 | cpp_define | Media player tuning (MediaPlayerTizenBase.cpp) | [`STARFISH_VIDEO_MAX_WIDTH`](src:src/platform/multimedia/MediaPlayerTizenBase.cpp#L47) |
| `STARFISH_FRAME_EVICTION_BACKWARD_DUR` | 500 | cpp_define | Media player tuning (MockMediaPlayer.cpp) | [`STARFISH_FRAME_EVICTION_BACKWARD_DUR`](src:src/platform/multimedia/MockMediaPlayer.cpp#L43) |
| `CURLHANDLE_CACHE_IDLE_TIME_LIMIT_S` | 60 | cpp_define | Network/HTTP layer (NetworkSharedResourceManager.cpp) | [`CURLHANDLE_CACHE_IDLE_TIME_LIMIT_S`](src:src/platform/network/curl/NetworkSharedResourceManager.cpp#L50) |
| `CURLHANDLE_CACHE_PRUNE_MINIMUM_INTERVAL_S` | 0.5 | cpp_define | Network/HTTP layer (NetworkSharedResourceManager.cpp) | [`CURLHANDLE_CACHE_PRUNE_MINIMUM_INTERVAL_S`](src:src/platform/network/curl/NetworkSharedResourceManager.cpp#L43) |
| `CURLHANDLE_CACHE_PRUNE_MINIMUM_SIZE` | 12 | cpp_define | Network/HTTP layer (NetworkSharedResourceManager.cpp) | [`CURLHANDLE_CACHE_PRUNE_MINIMUM_SIZE`](src:src/platform/network/curl/NetworkSharedResourceManager.cpp#L42) |
| `CURLPIPE_MULTIPLEX` | 0 | cpp_define | Network/HTTP layer (NetworkSharedResourceManager.cpp) | [`CURLPIPE_MULTIPLEX`](src:src/platform/network/curl/NetworkSharedResourceManager.cpp#L795) |
| `DEFAULT_HTTP_CACHE_SIZE` | 1024 * 1024 * 50 | cpp_define | Network/HTTP layer (HTTPCache.cpp) | [`DEFAULT_HTTP_CACHE_SIZE`](src:src/platform/network/http/HTTPCache.cpp#L44) |
| `INDEX_FILE_NAME` | "/index.txt" | cpp_define | Network/HTTP layer (HTTPCache.cpp) | [`INDEX_FILE_NAME`](src:src/platform/network/http/HTTPCache.cpp#L43) |
| `MAX_ENTRY_FILE_SIZE` | (DEFAULT_HTTP_CACHE_SIZE * 0.04) | cpp_define | Network/HTTP layer (HTTPCache.cpp) | [`MAX_ENTRY_FILE_SIZE`](src:src/platform/network/http/HTTPCache.cpp#L45) |
| `NUM_OF_COL` | 18 | cpp_define | Network/HTTP layer (HTTPCache.cpp) | [`NUM_OF_COL`](src:src/platform/network/http/HTTPCache.cpp#L46) |
| `CURLPIPE_MULTIPLEX` | 0 | cpp_define | Network/HTTP layer (HTTPTransaction.cpp) | [`CURLPIPE_MULTIPLEX`](src:src/platform/network/http/HTTPTransaction.cpp#L161) |
| `TTS_MODE_INTERRUPT` | 3 | cpp_define | TTS platform layer (TTSTV.cpp) | [`TTS_MODE_INTERRUPT`](src:src/platform/tts/TTSTV.cpp#L43) |
| `TTS_REMOVED_INSTANCE_SIZE` | 5 | cpp_define | TTS platform layer (TTSTV.cpp) | [`TTS_REMOVED_INSTANCE_SIZE`](src:src/platform/tts/TTSTV.cpp#L44) |
| `TTS_REMOVED_INSTANCE_SIZE` | 5 | cpp_define | TTS platform layer (TTSTizen.cpp) | [`TTS_REMOVED_INSTANCE_SIZE`](src:src/platform/tts/TTSTizen.cpp#L71) |
| `VCONFKEY_SETAPPL_ACCESSIBILITY_TTS` | "db/setting/accessibility/tts" | cpp_define | TTS platform layer (TTSTizen.cpp) | [`VCONFKEY_SETAPPL_ACCESSIBILITY_TTS`](src:src/platform/tts/TTSTizen.cpp#L63) |
| `VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY` | "db/setting/accessibility/tts/temporary" | cpp_define | TTS platform layer (TTSTizen.cpp) | [`VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY`](src:src/platform/tts/TTSTizen.cpp#L68) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Platform bridge (LWEWebViewEcoreWl2.cpp) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/public/bridge/ecore_wl2/LWEWebViewEcoreWl2.cpp#L22) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Platform bridge (LWEWebViewEcoreX.cpp) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/public/bridge/ecore_x/LWEWebViewEcoreX.cpp#L22) |
| `STARFISH_ATK_NODE_TYPE` | (starfish_atk_node_get_type()) | cpp_define | Platform bridge (A11yAtspiBridge.cpp) | [`STARFISH_ATK_NODE_TYPE`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L407) |
| `STARFISH_ATK_PLUG_TYPE` | (starfish_atk_plug_get_type()) | cpp_define | Platform bridge (A11yAtspiBridge.cpp) | [`STARFISH_ATK_PLUG_TYPE`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L188) |
| `VCONFKEY_SETAPPL_ACCESSIBILITY_TTS` | "db/setting/accessibility/tts" | cpp_define | Platform bridge (A11yAtspiBridge.cpp) | [`VCONFKEY_SETAPPL_ACCESSIBILITY_TTS`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L54) |
| `VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY` | "db/setting/accessibility/tts/temporary" | cpp_define | Platform bridge (A11yAtspiBridge.cpp) | [`VCONFKEY_SETAPPL_ACCESSIBILITY_TTS_TEMPORARY`](src:src/public/bridge/efl/A11yAtspiBridge.cpp#L59) |
| `ANNOTATE_GREEN` | 0x00ff001b | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`ANNOTATE_GREEN`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L106) |
| `ANNOTATE_SETUP` | N/A | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`ANNOTATE_SETUP`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L103) |
| `EFL_BETA_API_SUPPORT` | N/A | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`EFL_BETA_API_SUPPORT`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L75) |
| `EGL_IMAGE_PRESERVED_KHR` | 0x30D2 | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`EGL_IMAGE_PRESERVED_KHR`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L67) |
| `EGL_NATIVE_SURFACE_TIZEN` | 0x32A1 | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`EGL_NATIVE_SURFACE_TIZEN`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L64) |
| `EVAS_GL_NO_GL_H_CHECK` | N/A | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`EVAS_GL_NO_GL_H_CHECK`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L53) |
| `EVAS_GL_OPTIONS_DIRECT_MEMORY_OPTIMIZE` | (1 << 12) | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`EVAS_GL_OPTIONS_DIRECT_MEMORY_OPTIMIZE`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L981) |
| `EVAS_GL_OPTIONS_DIRECT_OVERRIDE` | (1 << 13) | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`EVAS_GL_OPTIONS_DIRECT_OVERRIDE`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L982) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Platform bridge (LWEWebViewEFL.cpp) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/public/bridge/efl/LWEWebViewEFL.cpp#L32) |
| `ANNOTATE_GREEN` | 0x00ff001b | cpp_define | Platform bridge (LWEWebViewFlutter.cpp) | [`ANNOTATE_GREEN`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L59) |
| `ANNOTATE_SETUP` | N/A | cpp_define | Platform bridge (LWEWebViewFlutter.cpp) | [`ANNOTATE_SETUP`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L56) |
| `EFL_BETA_API_SUPPORT` | N/A | cpp_define | Platform bridge (LWEWebViewFlutter.cpp) | [`EFL_BETA_API_SUPPORT`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L42) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Platform bridge (LWEWebViewFlutter.cpp) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/public/bridge/flutter/LWEWebViewFlutter.cpp#L40) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Platform bridge (LWEWebViewTcoreWl.cpp) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/public/bridge/tcore_wl/LWEWebViewTcoreWl.cpp#L22) |
| `GC_CPP_H` | N/A | cpp_define | Platform bridge (LWEWebViewX11.cpp) | [`GC_CPP_H`](src:src/public/bridge/x11/LWEWebViewX11.cpp#L25) |
| `STARFISH_ENABLE_PROFILE_TIMER` | N/A | cpp_define | Platform bridge (LWEWebViewX11.cpp) | [`STARFISH_ENABLE_PROFILE_TIMER`](src:src/public/bridge/x11/LWEWebViewX11.cpp#L22) |
| `EXPORT_UNMANAGED_API` | __declspec(dllexport) | cpp_define | Public delegate contract (LWEDelegateConfig.h) | [`EXPORT_UNMANAGED_API`](src:src/public/contract/LWEDelegateConfig.h#L24) |
| `EXPORT_UNMANAGED_API` | __attribute__((visibility("default"))) | cpp_define | Public delegate contract (LWEDelegateConfig.h) | [`EXPORT_UNMANAGED_API`](src:src/public/contract/LWEDelegateConfig.h#L26) |
| `LWE_DEFAULT_FONT_SIZE` | 16 | cpp_define | Public delegate implementation (LWEWebContainerDelegate.cpp) | [`LWE_DEFAULT_FONT_SIZE`](src:src/public/delegate/LWEWebContainerDelegate.cpp#L59) |
| `LWE_MAX_FONT_SIZE` | 72 | cpp_define | Public delegate implementation (LWEWebContainerDelegate.cpp) | [`LWE_MAX_FONT_SIZE`](src:src/public/delegate/LWEWebContainerDelegate.cpp#L61) |
| `LWE_MIN_FONT_SIZE` | 1 | cpp_define | Public delegate implementation (LWEWebContainerDelegate.cpp) | [`LWE_MIN_FONT_SIZE`](src:src/public/delegate/LWEWebContainerDelegate.cpp#L60) |
| `LWE_DEFAULT_FONT_SIZE` | 16 | cpp_define | Public delegate implementation (SettingsDelegate.cpp) | [`LWE_DEFAULT_FONT_SIZE`](src:src/public/delegate/SettingsDelegate.cpp#L29) |
| `THREAD_MINIMUM_STACK_SIZE` | 4 * 1024 * 1024 // we need at least 4MB for stack | cpp_define | Public delegate implementation (ThreadedCallHelper.cpp) | [`THREAD_MINIMUM_STACK_SIZE`](src:src/public/delegate/ThreadedCallHelper.cpp#L27) |
| `SHELL_ENABLE_BACKTRACE` | N/A | cpp_define | Shell configuration (ShellConfig.h) | [`SHELL_ENABLE_BACKTRACE`](src:src/shell/ShellConfig.h#L35) |
| `SHELL_ENABLE_ELEMENTARY_GL` | N/A | cpp_define | Shell configuration (ShellConfig.h) | [`SHELL_ENABLE_ELEMENTARY_GL`](src:src/shell/ShellConfig.h#L25) |
| `SHELL_ENABLE_TEST` | N/A | cpp_define | Shell configuration (ShellConfig.h) | [`SHELL_ENABLE_TEST`](src:src/shell/ShellConfig.h#L39) |
| `SHELL_X86_64` | N/A | cpp_define | Shell configuration (ShellConfig.h) | [`SHELL_X86_64`](src:src/shell/ShellConfig.h#L30) |

---

## Signal/Event Mapping

No OS-signal or broadcast-receiver style mappings were found in the extraction results (Starfish DOM events are in-process and are documented per module in W2). Not specified in code.

---

## Error Code Catalog

1 error/status constants.

| Error Code | Value | Severity | Description | Recovery | Source |
|------------|-------|----------|-------------|----------|--------|
| `CHECK_ERROR` | if (error) { STARFISH_RELEASE_ASSERT_SHOULD_NOT_BE_HERE(); } | Not specified in code | Font rendering (FontImplCairo.h) | Not specified in code | [`CHECK_ERROR`](src:src/platform/canvas/font/FontImplCairo.h#L47) |

---

## IPC Mechanism Summary

34 IPC records across mechanisms: `socket` (23), `nanomsg` (5), `message_port` (3), `websocket` (2), `http_client` (1).

| IPC Mechanism | Source Component | Target Component | Protocol | Data Format | Source |
|---------------|-----------------|------------------|----------|-------------|--------|
| http_client | Page JavaScript fetch() API (Fetch, Starfish) | Remote HTTP server (URL from Request; Not identifiable from code) | `Fetch::fetch` | fetch(ExecutionContext*, RequestInfo&) and the RequestInit overload (line 133) create a Re | [`fetch`](src:src/core/fetch/Fetch.cpp#L122) |
| message_port | JS context creating the channel (port1 holder) | JS context receiving the transferred port (port2 holder) | `MessageChannel::MessageChannel` | Creates two MessagePort objects (port1/port2) and entangles them via MessagePort::entangle | [`MessageChannel`](src:src/core/dom/MessageChannel.cpp#L27) |
| message_port | MessagePort endpoint | Entangled MessagePort peer (other JS context) | `MessagePort::MessagePort` | Message-port endpoint holding a PortMessageQueue and structured-clone serializer (Serializ | [`MessagePort`](src:src/core/dom/MessagePort.cpp#L33) |
| message_port | Entangled MessagePort peer (message sender) | This MessagePort's onmessage EventListener | `MessagePort::setOnmessage` | Registers the 'message' attribute event listener; per spec, the first assignment enables t | [`setOnmessage`](src:src/core/dom/MessagePort.cpp#L178) |
| nanomsg | Inspector (Starfish WebView) | Remote inspector client (nanomsg NN_PAIR peer) | `Inspector::sendDebugMessage` | Sends JSON {"command":"console-debug","content":<message text>} over the nanomsg NN_PAIR s | [`sendDebugMessage`](src:src/core/inspector/Inspector.cpp#L151) |
| nanomsg | Inspector (Starfish WebView) | Remote inspector client (nanomsg NN_PAIR peer) | `Inspector::sendErrorMessage` | Sends JSON {"command":"console-error","content":<message text>} over the nanomsg NN_PAIR s | [`sendErrorMessage`](src:src/core/inspector/Inspector.cpp#L89) |
| nanomsg | Inspector (Starfish WebView) | Remote inspector client (nanomsg NN_PAIR peer) | `Inspector::sendInfoMessage` | Sends JSON {"command":"console-info","content":<message text>} over the nanomsg NN_PAIR so | [`sendInfoMessage`](src:src/core/inspector/Inspector.cpp#L58) |
| nanomsg | Inspector (Starfish WebView) | Remote inspector client (nanomsg NN_PAIR peer) | `Inspector::sendWarnMessage` | Sends JSON {"command":"console-warn","content":<message text>} over the nanomsg NN_PAIR so | [`sendWarnMessage`](src:src/core/inspector/Inspector.cpp#L120) |
| nanomsg | Inspector (WebView remote inspection thread) | Remote inspector client (nanomsg NN_PAIR peer) | `Inspector::worker` | Creates nn::socket(AF_SP, NN_PAIR), binds to the configured address, then recv(NN_MSG, NN_ | [`worker`](src:src/core/inspector/Inspector.cpp#L197) |
| socket | CDPCommand/CDPDispatcher (Starfish CDP backend) | DevTools frontend (CDP client) | `CDPCommand::emit` | Serializes a rapidjson CDP response/event document (adding sessionId when present) and sen | [`emit`](src:src/core/cdp/CDPCommand.cpp#L42) |
| socket | CDPConnection (CDPServer per-client handler) | DevTools frontend (CDP client) | `CDPConnection::CDPConnection` | Per-connection handler over the accepted TCP fd; serves HTTP discovery endpoints (/json/ve | [`CDPConnection`](src:src/core/cdp/CDPConnection.cpp#L39) |
| socket | Page JavaScript binding call (WebView) | DevTools frontend (CDP client) | `CDPDispatcher::emitBindingCalled` | Routes to the TargetContext/session owning the originating WebView and, when runtimeEnable | [`emitBindingCalled`](src:src/core/cdp/CDPDispatcher.cpp#L1701) |
| socket | Starfish page console API (per WebView) | DevTools frontend (CDP client) | `CDPDispatcher::emitConsoleForWebView` | Builds a Runtime.consoleAPICalled event (level, args array of {type,value}, executionConte | [`emitConsoleForWebView`](src:src/core/cdp/CDPDispatcher.cpp#L1594) |
| socket | CDPServer accept loop (IO thread) | CDPDispatcher (main thread session state) | `CDPDispatcher::onConnectionClosed` | Invoked when the DevTools client's socket connection closes; resets connection-scoped CDP  | [`onConnectionClosed`](src:src/core/cdp/CDPDispatcher.cpp#L214) |
| socket | DevTools frontend (CDP client) | CDPDispatcher domain handlers (Starfish) | `CDPDispatcher::route` | Routes each incoming CDP command (domain.method with CDPCommand payload) to per-domain pro | [`route`](src:src/core/cdp/CDPDispatcher.cpp#L390) |
| socket | CDPServer (DevTools server IO thread) | DevTools frontend (CDP client, e.g. Chrome DevTools/puppeteer) | `CDPServer::acceptLoop` | Creates AF_INET SOCK_STREAM TCP listen socket, setsockopt(SO_REUSEADDR), bind()/listen() o | [`acceptLoop`](src:src/core/cdp/CDPServer.cpp#L97) |
| socket | DIALRunnable (Starfish cast module, httplib::Server) | DIAL client devices on local network (cast senders) | `DIALRunnable::doRun` | Runs an httplib HTTP server listening on the local address at LOCATION_PORT: GET LOCATION_ | [`doRun`](src:src/core/modules/cast/DIALRunnable.cpp#L43) |
| socket | DevTools frontend (CDP client) | DOMDebuggerDomain (Starfish) | `DOMDebuggerDomain::processMessage` | Handles incoming CDP DOMDebugger.* commands: processMessage(CDPCommand& cmd, const std::st | [`processMessage`](src:src/core/cdp/domains/DOMDebuggerDomain.cpp#L58) |
| socket | DevTools frontend (CDP client) | DOMDomain (Starfish) | `DOMDomain::processMessage` | Handles incoming CDP DOM.* commands: processMessage(CDPCommand& cmd, const std::string& me | [`processMessage`](src:src/core/cdp/domains/DOMDomain.cpp#L87) |
| socket | PageDomain (Starfish) | DevTools frontend (CDP client) | `PageDomain::finishNavigation` | On navigation completion for a CDP session: evaluates Page.addScriptToEvaluateOnNewDocumen | [`finishNavigation`](src:src/core/cdp/domains/PageDomain.cpp#L1120) |
| socket | DevTools frontend (CDP client) | Page JavaScript context (via RuntimeDomain) | `RuntimeDomain::callFunctionOn` | CDP Runtime callFunctionOn handler: callFunctionOn(WebView* wv, BrowsingContext* bc, CDPCo | [`callFunctionOn`](src:src/core/cdp/domains/RuntimeDomain.cpp#L458) |
| socket | DevTools frontend (CDP client) | Page JavaScript context (via RuntimeDomain) | `RuntimeDomain::compileScript` | CDP Runtime compileScript handler: compileScript(WebView* wv, BrowsingContext* bc, CDPComm | [`compileScript`](src:src/core/cdp/domains/RuntimeDomain.cpp#L623) |
| socket | DevTools frontend (CDP client) | Page JavaScript context (via RuntimeDomain) | `RuntimeDomain::evaluateSource` | CDP Runtime evaluate implementation: evaluateSource(WebView* wv, BrowsingContext* bc, cons | [`evaluateSource`](src:src/core/cdp/domains/RuntimeDomain.cpp#L892) |
| socket | DevTools frontend (CDP client) | Page JavaScript context (via RuntimeDomain) | `RuntimeDomain::getProperties` | CDP Runtime getProperties handler: getProperties(WebView* wv, BrowsingContext* bc, CDPComm | [`getProperties`](src:src/core/cdp/domains/RuntimeDomain.cpp#L753) |
| socket | DevTools frontend (CDP client) | Page JavaScript context (via RuntimeDomain) | `RuntimeDomain::globalLexicalScopeNames` | CDP Runtime globalLexicalScopeNames handler: globalLexicalScopeNames(WebView* wv, CDPComma | [`globalLexicalScopeNames`](src:src/core/cdp/domains/RuntimeDomain.cpp#L845) |
| socket | DevTools frontend (Runtime.addBinding command) | Page JavaScript global object | `RuntimeDomain::injectBinding` | Defines a native window[name] function (with BindingExtra name) in the page's script conte | [`injectBinding`](src:src/core/cdp/domains/RuntimeDomain.cpp#L320) |
| socket | DevTools frontend (CDP client) | RuntimeDomain (Starfish) | `RuntimeDomain::processMessage` | Handles incoming CDP Runtime.* commands: processMessage(CDPCommand& cmd, const std::string | [`processMessage`](src:src/core/cdp/domains/RuntimeDomain.cpp#L67) |
| socket | SSDPRunnable (Starfish cast module) | SSDP multicast group / cast sender devices on local network | `SSDPRunnable::initSocket` | Creates UDP socket (AF_INET, SOCK_DGRAM\|SOCK_NONBLOCK\|SOCK_CLOEXEC) with SO_REUSEADDR, b | [`initSocket`](src:src/core/modules/cast/SSDPRunnable.cpp#L118) |
| socket | SSDPRunnable (Starfish cast module thread) | SSDP multicast group on local network | `SSDPRunnable::preRun` | Thread pre-run hook: initializes the SSDP UDP multicast socket via initSocket() before the | [`preRun`](src:src/core/modules/cast/SSDPRunnable.cpp#L42) |
| socket | DevTools frontend (CDP client) | TracingDomain (Starfish) | `TracingDomain::processMessage` | Handles incoming CDP Tracing.* commands: processMessage(CDPCommand& cmd, const std::string | [`processMessage`](src:src/core/cdp/domains/TracingDomain.cpp#L71) |
| socket | Page JavaScript (window[name](payload) call) | DevTools frontend (CDP client) | `bindingNativeCallback (RuntimeDomain)` | Native callback installed by Runtime.addBinding: resolves the originating WebView from the | [`bindingNativeCallback`](src:src/core/cdp/domains/RuntimeDomain.cpp#L289) |
| socket | ScriptBindingInstance (Starfish window script context) | Remote script debugger client (Escargot debugger protocol) | `initDebuggerIfNeeds` | When STARFISH_ENABLE_DEBUGGER is defined: for window contexts with scripting enabled, asks | [`initDebuggerIfNeeds`](src:src/binding/ScriptWrappable.cpp#L1431) |
| websocket | ExecutionContext (page/worker context) | Remote WebSocket server (Not identifiable from code) | `ExecutionContext::addActiveWebSockets` | Registers an active WebSocket client connection with the execution context (guarded by STA | [`addActiveWebSockets`](src:src/core/dom/ExecutionContext.cpp#L182) |
| websocket | ExecutionContext (page/worker context) | Remote WebSocket server (Not identifiable from code) | `ExecutionContext::disposeActiveWebSockets` | On context teardown, disposes (closes) every remaining active WebSocket connection via web | [`disposeActiveWebSockets`](src:src/core/dom/ExecutionContext.cpp#L196) |

Discovered custom IPC patterns applied during W1 (see `.analysis/ipc-discovery/discovered-ipc-patterns.json`): `nanomsg` (nn_socket/nn_send/nn_recv/nn_close), `subprocess` (launchProcess, launchProcessOnDoubleFork), `websocket` (lws_write, lws_service).

Related: [External Interfaces](./05-external-interfaces.md) · [System Architecture](./02-architecture.md)
