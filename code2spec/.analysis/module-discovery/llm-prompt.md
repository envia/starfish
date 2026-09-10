# Task: Logical Hierarchy Module Discovery

## Context
You are reviewing a large repository where the full file list is too long for reliable semantic file-by-file review.
Your task is to derive human-reviewable logical modules from the directory hierarchy.

## Project Information
- **Total Files**: 1815
- **Prompt Mode**: logical-hierarchy
- **Prompt File Limit**: 1000
- **Files Listed In Prompt**: 0 full-list entries; representative samples are shown by directory
- **Full File List Entries Omitted**: 1815
- **Maximum Module Count**: 100
- **Hierarchy Overview Max Entries**: 80
- **Directory Summary Max Dirs**: 25
- **Representative Files Per Directory**: 3
- **AST Nodes**: 28929 (File: 1815, Constant: 1636, Enum: 444, Function: 24084, Class: 930, Test: 20)
- **AST Edges**: 152362 (CONTAINS: 27114, IMPORTS_FROM: 9306, CALLS: 114627, IPC: 1073, INHERITS: 191, TESTED_BY: 51)

## Hierarchy Policy
Use directory hierarchy as the primary module boundary. This is not a flat semantic review.
Prefer stable directory-level modules over inferred cross-cutting product workflows.

### Boundary Rules
1. Choose module boundaries at directory depth 2-3 by default.
2. Do not use overly broad roots such as `src`, `src/**`, `ui`, `ui/**`, `**/*`, or extension-wide globs.
3. Do not split every leaf directory into its own module; merge sibling leaf directories when they are one review surface.
4. Only merge across distant directories when names strongly match, such as `ConfluenceBuilder` with `useSkill.ts` and `model/skill.ts`.
5. Do not turn generated/vendor/bundle directories into business logical modules. If they must be covered, group them as support/generated artifacts with a non-business name such as `support-generated-artifacts`.
6. Do not infer names like `design-system-bundle` only from paths such as `ds-bundle`; directory names are structural evidence, not final domain names.
7. Keep shared UI foundation, app shell/config, backend runtime/config, backend data, backend realtime, and test/logging support separate when the hierarchy clearly shows those surfaces.
8. Use include/exclude patterns. Python will expand them against the full known file manifest and reject missing, duplicate, unknown, unmatched, empty, or overly broad modules.
9. Produce no more than the maximum module count. If preserving meaningful boundaries would require more modules, flag that conflict for human review instead of merging unrelated areas.

## Hierarchy Overview
- src/ (1752 files)
- tool/ (51 files)
- third_party/ (5 files)
- docs/ (3 files)
- inc/ (3 files)
- compat/ (1 files)
- src/core/ (1485 files)
- src/platform/ (122 files)
- src/public/ (53 files)
- src/shell/ (39 files)
- src/binding/ (38 files)
- tool/drivers/ (14 files)
- tool/wpt/ (10 files)
- tool/runner/ (7 files)
- third_party/robin_map/ (5 files)
- tool/perf_tools/ (5 files)
- tool/pixel_test/ (4 files)
- tool/coverage/ (3 files)
- tool/lint/ (3 files)
- docs/generator/ (2 files)
- src/browser/ (2 files)
- src/launcher/ (2 files)
- tool/reftest/ (2 files)
- compat/tizen_5.0/ (1 files)
- docs/webpages/ (1 files)
- tool/ci/ (1 files)
- tool/imgdiff/ (1 files)
- src/core/dom/ (517 files)
- src/core/modules/ (464 files)
- src/core/style/ (147 files)
- src/core/layout/ (101 files)
- src/core/cdp/ (58 files)
- src/core/util/ (52 files)
- src/core/page/ (38 files)
- src/platform/multimedia/ (33 files)
- src/core/fetch/ (29 files)
- src/platform/canvas/ (25 files)
- src/core/animation/ (23 files)
- src/public/bridge/ (20 files)
- src/platform/loader/ (17 files)
- src/platform/network/ (17 files)
- src/core/extra/ (15 files)
- src/public/delegate/ (14 files)
- src/core/storage/ (13 files)
- src/platform/message_loop/ (12 files)
- src/core/fileapi/ (10 files)
- src/public/contract/ (9 files)
- tool/wpt/scripts/ (9 files)
- src/core/csp/ (7 files)
- tool/drivers/basics/ (7 files)
- src/shell/test/ (6 files)
- tool/drivers/tests/ (6 files)
- third_party/robin_map/include/ (5 files)
- src/core/serialize/ (4 files)
- src/core/xml/ (4 files)
- src/platform/file/ (4 files)
- src/platform/public/ (4 files)
- src/shell/efl/ (4 files)
- src/platform/process/ (3 files)
- src/platform/tts/ (3 files)
- src/shell/windows/ (3 files)
- src/browser/history/ (2 files)
- src/core/inspector/ (2 files)
- src/platform/feedback/ (2 files)
- src/shell/ecore/ (2 files)
- src/shell/glib/ (2 files)
- src/shell/libuv/ (2 files)
- src/shell/tcore_wl/ (2 files)
- tool/perf_tools/mse-smoke/ (2 files)
- tool/pixel_test/nw_capture/ (2 files)
- compat/tizen_5.0/inc/ (1 files)
- docs/webpages/webapi/ (1 files)
- src/core/event/ (1 files)
- src/platform/event/ (1 files)
- src/platform/windows/ (1 files)
- src/shell/dummy/ (1 files)
- src/shell/headless/ (1 files)
- src/shell/x11_webcontainer/ (1 files)
- tool/lint/contract_abi/ (1 files)
- tool/perf_tools/measure-bench/ (1 files)
... 2 more hierarchy entries omitted

## Directory Summary
This section is intentionally capped. Use it as representative evidence only; module include/exclude patterns will be validated against the full known manifest outside the LLM prompt.

### src/core/dom/ (286 files)
Extensions: .h 161, .cpp 124, .js 1
Likely keywords: element, event, list, table, text, node, track, document
Representative files:
- src/core/dom/AnimationEvent.h
- src/core/dom/Attr.cpp
- src/core/dom/Attr.h
... 283 more

### src/core/style/ (147 files)
Extensions: .h 87, .cpp 60
Likely keywords: style, data, value, list, media, length, query, border
Representative files:
- src/core/style/AdoptedStyleSheets.cpp
- src/core/style/AdoptedStyleSheets.h
- src/core/style/AncestorSelectorFilter.cpp
... 144 more

### src/core/dom/svg/ (125 files)
Extensions: .h 64, .cpp 61
Likely keywords: element, animated, list, transform, length, number, animate, path
Representative files:
- src/core/dom/svg/SVGAngle.cpp
- src/core/dom/svg/SVGAngle.h
- src/core/dom/svg/SVGAnimateElement.cpp
... 122 more

### src/core/modules/mediastream/ (77 files)
Extensions: .h 43, .cpp 34
Likely keywords: rtp, parameters, ice, media, event, peer, connection, track
Representative files:
- src/core/modules/mediastream/ConstrainBooleanParameters.h
- src/core/modules/mediastream/ConstrainDOMStringParameters.h
- src/core/modules/mediastream/ConstrainDoubleRange.h
... 74 more

### src/core/layout/ (69 files)
Extensions: .h 36, .cpp 33
Likely keywords: frame, box, table, replaced, block, layout, text, inline
Representative files:
- src/core/layout/ComputeOverflow.h
- src/core/layout/Frame.cpp
- src/core/layout/Frame.h
... 66 more

### src/core/util/ (48 files)
Extensions: .h 28, .cpp 19, .hpp 1
Likely keywords: string, text, name, options, pool, vector, archivable, archiver
Representative files:
- src/core/util/Archivable.cpp
- src/core/util/Archivable.h
- src/core/util/Archiver.cpp
... 45 more

### src/core/modules/worker/ (45 files)
Extensions: .h 25, .cpp 20
Likely keywords: worker, host, proxy, dedicated, global, scope, thread, manager
Representative files:
- src/core/modules/worker/AbstractWorker.cpp
- src/core/modules/worker/AbstractWorker.h
- src/core/modules/worker/DedicatedWorkerGlobalScope.cpp
... 42 more

### src/core/cdp/domains/ (40 files)
Extensions: .cpp 20, .h 20
Likely keywords: domain, storage, accessibility, animation, debugger, snapshot, emulation, fetch
Representative files:
- src/core/cdp/domains/AccessibilityDomain.cpp
- src/core/cdp/domains/AccessibilityDomain.h
- src/core/cdp/domains/AnimationDomain.cpp
... 37 more

### src/binding/ (38 files)
Extensions: .cpp 23, .h 15
Likely keywords: binding, custom, script, instance, holdable, window, document, worker
Representative files:
- src/binding/CharacterDataCustomBinding.cpp
- src/binding/DocumentCustomBinding.cpp
- src/binding/DocumentHoldable.cpp
... 35 more

### src/core/page/ (38 files)
Extensions: .h 20, .cpp 17, .js 1
Likely keywords: event, source, a11y, navigator, web, window, global, scope
Representative files:
- src/core/page/A11yAtspiTreeSource.cpp
- src/core/page/A11yAtspiTreeSource.h
- src/core/page/A11yTouchExploration.cpp
... 35 more

### src/core/modules/indexeddb/ (36 files)
Extensions: .h 19, .cpp 17
Likely keywords: key, store, database, request, backing, connection, cursor, identifier
Representative files:
- src/core/modules/indexeddb/IDBBackingStore.h
- src/core/modules/indexeddb/IDBConfig.h
- src/core/modules/indexeddb/IDBConnection.cpp
... 33 more

### src/core/modules/serviceworker/ (36 files)
Extensions: .h 20, .cpp 16
Likely keywords: service, worker, data, registration, job, fetch, message, cache
Representative files:
- src/core/modules/serviceworker/ConnectionInterface.h
- src/core/modules/serviceworker/ExceptionData.cpp
- src/core/modules/serviceworker/ExceptionData.h
... 33 more

### src/core/dom/canvas/ (33 files)
Extensions: .h 20, .cpp 13
Likely keywords: canvas, image, rendering, context, context2, text, path, mix
Representative files:
- src/core/dom/canvas/CanvasDirection.h
- src/core/dom/canvas/CanvasFillRule.h
- src/core/dom/canvas/CanvasGradient.cpp
... 30 more

### src/platform/multimedia/ (33 files)
Extensions: .cpp 18, .h 15
Likely keywords: player, media, web, tizen, audio, linux, rtc, demuxer
Representative files:
- src/platform/multimedia/Demuxer.cpp
- src/platform/multimedia/Demuxer.h
- src/platform/multimedia/DemuxerMP4.cpp
... 30 more

### src/core/layout/svg/ (32 files)
Extensions: .cpp 16, .h 16
Likely keywords: frame, box, path, circle, clip, ellipse, invisible, line
Representative files:
- src/core/layout/svg/FrameSVGBox.cpp
- src/core/layout/svg/FrameSVGBox.h
- src/core/layout/svg/FrameSVGCircleBox.cpp
... 29 more

### src/core/dom/canvas/webgl/ (31 files)
Extensions: .h 18, .cpp 13
Likely keywords: web, context, rendering, object, shader, buffer, attributes, extensions
Representative files:
- src/core/dom/canvas/webgl/WebGL2RenderingContext.cpp
- src/core/dom/canvas/webgl/WebGL2RenderingContext.h
- src/core/dom/canvas/webgl/WebGLActiveInfo.h
... 28 more

### src/core/dom/parser/ (31 files)
Extensions: .h 18, .cpp 13
Likely keywords: element, entity, parser, stack, tokenizer, token, construction, site
Representative files:
- src/core/dom/parser/AtomicHTMLToken.h
- src/core/dom/parser/HTMLConstructionSite.cpp
- src/core/dom/parser/HTMLConstructionSite.h
... 28 more

### src/core/modules/canvas/filter/ (24 files)
Extensions: .cpp 12, .h 12
Likely keywords: filter, color, matrix, transfer, composite, displacement, map, flood
Representative files:
- src/core/modules/canvas/filter/Filter.cpp
- src/core/modules/canvas/filter/Filter.h
- src/core/modules/canvas/filter/FilterColorMatrix.cpp
... 21 more

### src/core/animation/ (21 files)
Extensions: .h 11, .cpp 10
Likely keywords: animation, applier, timing, animated, value, executor, task, cubic
Representative files:
- src/core/animation/AnimatedValue.cpp
- src/core/animation/AnimatedValue.h
- src/core/animation/Animation.cpp
... 18 more

### src/core/modules/serviceworker/host/ (21 files)
Extensions: .h 11, .cpp 10
Likely keywords: service, worker, event, fetch, job, host, server, extendable
Representative files:
- src/core/modules/serviceworker/host/ExtendableEvent.cpp
- src/core/modules/serviceworker/host/ExtendableEvent.h
- src/core/modules/serviceworker/host/FetchEvent.cpp
... 18 more

### src/core/modules/sharedworker/ (20 files)
Extensions: .cpp 10, .h 10
Likely keywords: shared, worker, message, connection, port, handler, serializer, client
Representative files:
- src/core/modules/sharedworker/IPCConnection.cpp
- src/core/modules/sharedworker/IPCConnection.h
- src/core/modules/sharedworker/IPCMessageHandler.cpp
... 17 more

### src/core/fetch/ (19 files)
Extensions: .h 10, .cpp 9
Likely keywords: data, request, fetch, headers, response, body, init
Representative files:
- src/core/fetch/Body.cpp
- src/core/fetch/Body.h
- src/core/fetch/Fetch.cpp
... 16 more

### src/core/cdp/ (18 files)
Extensions: .h 10, .cpp 8
Likely keywords: base64, command, connection, dispatcher, server, node, registry, remote
Representative files:
- src/core/cdp/Base64.cpp
- src/core/cdp/Base64.h
- src/core/cdp/CDPCommand.cpp
... 15 more

### src/core/modules/canvas/ (17 files)
Extensions: .h 11, .cpp 6
Likely keywords: canvas, shadow, data, compositor, blend, mode, fill, stroke
Representative files:
- src/core/modules/canvas/BlendMode.cpp
- src/core/modules/canvas/BlendMode.h
- src/core/modules/canvas/Canvas.cpp
... 14 more

### src/platform/loader/ (17 files)
Extensions: .h 9, .cpp 8
Likely keywords: resource, client, element, font, header, image, loader, text
Representative files:
- src/platform/loader/ElementResourceClient.cpp
- src/platform/loader/ElementResourceClient.h
- src/platform/loader/FontResource.cpp
... 14 more

... 109 more directories omitted from summary

## Output Format
You MUST output ONLY YAML in this shape:

```yaml
modules:
  - name: "ui-chat-experience"
    include:
      - "ui/components/Chat"
      - "ui/components/ChatWindow"
      - "ui/components/MessageInputActions"
      - "ui/hooks/useSearchState.ts"
    exclude:
      - "ui/components/ChatWindow/*.test.tsx"
    rationale: "Chat/search UI directories and strongly named supporting hooks"
    confidence: 0.86
```

### Review Checklist
- Produce no more than 100 modules. If preserving meaningful boundaries would require more modules, flag that conflict for human review instead of merging unrelated areas.
- Every known file must be covered exactly once after pattern expansion.
- Prefer directory paths over long file lists.
- Use file paths only for root files and boundary exceptions.
- Explain whether tests, styles, constants, generated files, and config files stay with their directory module or move to support/generated modules.
- Generated/vendor/bundle paths should be labeled as support artifacts, not product/domain modules.
