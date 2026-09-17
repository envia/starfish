# WebGL acceleration plan for the TensorFlow.js toxicity demo

Goal: make https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html
run on the TensorFlow.js `webgl` backend with both WebGL1
(`?tfjsflags=WEBGL_VERSION:1`) and WebGL2 (the page default), on top of
`master` 1.5.6 (`13c4ffd576`).

Scope: only what the TFJS WebGL backend touches. Complete WebGL extension or
WebGL2 conformance is out of scope, but every change must be spec-correct for
the part it implements and must not regress currently passing tests.

## Branches and roles

| Checkout | Branch | Who |
|---|---|---|
| `starfish_f_claude` | `origin/indigo/2025/webgl2/0375` | Claude Code |
| `starfish_f_codex` | `origin/indigo/2025/webgl2/0376` | Codex |
| `starfish_f` | `origin/indigo/2025/webgl2/0377` | Agreed result of 0375 and 0376 |
| `web_tc_new_` | `origin/indigo/2025/webgl2/0375` | Test assets (see Testing) |

Reference branches (all older than `master`; use them for content, not for
merging):

| Branch | What to take from it |
|---|---|
| `origin/indigo/2025/webgl2/0374` | Most complete 7-commit series, validated on NVIDIA RTX 3050 for WebGL1 and WebGL2. Primary source for commits 2 to 5. |
| `origin/indigo/2025/webgl2/0373` | Extension registry initialization fix; alternative texture upload and readPixels implementations. |
| `origin/indigo/2025/webgl2/0372` | Earlier 8-commit series; same fixes minus the registry initialization fix. |
| `origin/indigo/2025/webgl2/0171` | Older WebGL2 work (texStorage, buffer objects, IDL updates). Background only. |
| `origin/claude/2026/tfjs/0002` | Registry initialization fix with a `WebContainerTest` gtest that clears the current GL context before creating a WebGL context. |
| `github/envia/2026/devel/0730` | Codex single-commit version of the same fixes. Reuse `tests/webgl/toxicity-probe.js`, `tests/webgl/toxicity-reference.json` and `tests/webgl/run.py` for the end-to-end check. |
| `github/envia/2026/devel/0022`, `0750` | Codex patch series against the public repo; same content as 0372 plus a local toxicity demo bundle. |

The internal HTML tests that 0374 registered in `tool/reftest/cairo/internal.res`
were never committed to any test repository. They are rewritten here.

## Commit sequence

Each commit builds (`make` with the untracked repo-root `Makefile`:
`out/webgl2`, Debug, `uv_cairo_gl`, `x11`, `WEBGL=1`), passes
`./tool/lint/check_tidy.py`, and passes the tests listed for it under
`xvfb-run -s '-screen 0 1920x1080x24' -a`. IDL changes need a cmake re-run.

### 1. Initialize WebGL extension registry under a current GL context

`WebGLExtensionRegistry::initialize()` runs from the `WebGLRenderingContext`
constructor before any `GLContextScope` is entered. When the first WebGL
context of the process is created synchronously during page load, no GL
context is current, `glGetString(GL_EXTENSIONS)` returns null and the registry
freezes empty for the whole process (every `getExtension()` returns null,
BGRA detection flips off). This is the root cause of "no extensions on
llvmpipe / libuv".

- Move the initialization into `WebGLRenderingContext::initialize()` inside
  its `GLContextScope`.
- When `GL_EXTENSIONS` reads back null, log and stay uninitialized so a later
  context retries; accessors tolerate an uninitialized registry.
- Reference: 0373 first commit, `origin/claude/2026/tfjs/0002`.
- Test: the internal test of commit 2 creates its contexts synchronously in a
  page-load script and asserts an extension the driver advertises is visible.

### 2. Expose EXT_color_buffer_float to WebGL2 and filter extensions by version

- Add an internal `virtual int webGLVersion() const` (1 / 2) to the contexts.
- Register `EXT_color_buffer_float` (new IDL interface, no members) when the
  driver advertises `GL_EXT_color_buffer_float`. Expose it to WebGL2 only.
- `getSupportedExtensions()` and `getExtension()` filter by context version.
- Track the native `GL_EXT_color_buffer_float` capability separately for
  commit 4; it must not expose the WebGL2 extension to WebGL1.
- Optional, decide during review: hide the WebGL1 extensions that WebGL2
  promoted to core (`OES_texture_float`, `OES_texture_half_float`,
  `OES_standard_derivatives`, `OES_vertex_array_object`, `WEBGL_depth_texture`,
  `EXT_blend_minmax`) from WebGL2, as the Khronos registry specifies. 0730 hides
  them, 0374 does not. Default: keep exposing them unless
  `vendor_test_khronos2` needs the change.
- Update `docs/Spec.md` WebGL section (extension list, "NOT implemented" list).
- Reference: 0374 commits 1 and 5, 0730.
- Tests: new `test/cairo/internal-test/canvas/webgl-extension-version.html`
  (WebGL1 never lists `EXT_color_buffer_float`; WebGL2 lists it iff
  `getExtension()` returns an object; results consistent between the two
  queries; contexts created synchronously at load).

### 3. Fix float texture uploads and null texture initialization

Shared `handleTexImageWithArrayBufferView` path for WebGL1 and WebGL2:

- `getBytesPerPixelWebGL1`: FLOAT is 4 bytes per component, add
  `HALF_FLOAT_OES` at 2; return 0 for undefined combinations instead of
  asserting, callers report `INVALID_ENUM`.
- Validate FLOAT / HALF_FLOAT_OES against the enabled extension (WebGL1 only)
  and the typed array kind (`Float32Array` / `Uint16Array`).
- Validate `border`, dimensions and `level` against `MAX_TEXTURE_SIZE` /
  `MAX_CUBE_MAP_TEXTURE_SIZE` before allocating the null backing buffer.
- `texImage2D(..., null)` zero-fills every component (WebGL 1.0 §5.14.8; the
  current fill sets alpha to 255) with `UNPACK_*` state pinned to the tightly
  packed buffer and restored afterwards.
- `texSubImage2D(..., null)` generates `INVALID_VALUE`.
- Keep the `PORT_PIXEL_ORDER_BGRA` promotion to `RGBA` + `UNSIGNED_BYTE` null
  uploads only.
- WebGL2: reject the ArrayBufferView overload while a `PIXEL_UNPACK_BUFFER` is
  bound.
- Reference: 0374 commit 2, 0373 commit 2.
- Tests: new `test/cairo/internal-test/canvas/webgl-float-texture-upload.html`
  (float and half-float uploads with correct sizes, undersized view rejected,
  wrong typed array rejected, null fill reads back zero alpha, null
  `texSubImage2D` error, oversized level rejected); activate Khronos
  `conformance/textures/texture-size.html`; activate
  `conformance/extensions/oes-texture-float.html` and
  `oes-texture-half-float.html` if they pass on llvmpipe.

### 4. Support WebGL1 float render targets on ES3

TFJS decides `WEBGL_RENDER_FLOAT32_CAPABLE` by attaching a `RGBA` / `FLOAT`
texture to a framebuffer and checking completeness. On an ES3 driver only the
sized formats are color-renderable through `EXT_color_buffer_float`.

- When the driver advertises `GL_EXT_color_buffer_float` and the context is
  WebGL1, store `RGBA` / `RGB` + `FLOAT` as `RGBA32F` / `RGB32F`, and
  `HALF_FLOAT_OES` as `RGBA16F` / `RGB16F` with the core `GL_HALF_FLOAT` upload
  type. WebGL1 input validation and the GLES2 fallback stay unchanged.
- Reference: 0374 commit 3.
- Tests: new `test/cairo/internal-test/canvas/webgl1-float-render-target.html`
  (float and half-float texture attached to an FBO is `FRAMEBUFFER_COMPLETE`,
  a draw into it followed by a sampling pass reproduces values outside
  [0, 1]).

### 5. Implement WebGL2 readPixels into pixel pack buffers

TFJS downloads WebGL2 results through a `PIXEL_PACK_BUFFER`, a fence and
`getBufferSubData`. Both WebGL2 `readPixels` overloads are `[Unimplemented]`
and throw "Illegal invocation".

- Implement `readPixels(..., GLintptr offset)` against the bound pack buffer
  and `readPixels(..., ArrayBufferView dstData, dstOffset)`.
- Validate format/type enums, element alignment of the offset, and the bytes
  the read touches from `PACK_ALIGNMENT`, `PACK_ROW_LENGTH`, `PACK_SKIP_ROWS`,
  `PACK_SKIP_PIXELS` (OpenGL ES 3.0 §4.3.2) so an undersized buffer never
  becomes an out-of-bounds driver write.
- The ArrayBufferView overload generates `INVALID_OPERATION` while a pack
  buffer is bound; the offset overload does so when none is bound.
- `getBufferSubData`: reject `dstOffset` / `length` beyond the destination
  view before computing the copy.
- NVIDIA requires an explicit `PACK_ROW_LENGTH` equal to `width` for PBO reads
  whose last row has no trailing padding; set it temporarily when it is 0.
- Remove the two `[Unimplemented]` markers in `WebGL2RenderingContext.idl`;
  update `docs/Spec.md`.
- Reference: 0374 commit 6, 0373 commit 3, 0730.
- Tests: new `test/cairo/internal-test/canvas/webgl2-pixel-readback.html`
  (PBO read plus fence plus `getBufferSubData`, odd widths, element offsets,
  float values outside [0, 1], undersized buffer and misaligned offset
  errors, view overload while a PBO is bound); activate Khronos
  `conformance2/reading/read-pixels-into-pixel-pack-buffer.html` and
  `read-pixels-pack-parameters.html`.

## Testing

Internal tests use `console.assert` and `testEnd()` and must also run in a
plain browser. They live in the `test/` submodule
(`test/cairo/internal-test/canvas/`) and are registered in
`tool/reftest/cairo/internal.res`. Commits in `test/` are made in this
checkout, fetched into `/home/hwang/work/web_tc_new_` as the same commit
objects and pushed there as `indigo/2025/webgl2/0375`. The submodule gitlink
in this repository is not bumped; pick the final test commit when integrating
0377.

Khronos activations follow the `.res` rule: uncomment only tests that pass
in this build, never delete a commented line.

Final verification, run sequentially (llvmpipe is CPU bound):

1. `./tool/lint/check_tidy.py`.
2. `internal_test`, `vendor_test_khronos`, `vendor_test_khronos2` under
   `xvfb-run` with `LP_NUM_THREADS=4`, diffed against a `master` baseline
   from the same build configuration. No new failures.
3. Toxicity demo, 3 sentences, 21 decisions compared with the CPU reference
   (`tests/webgl/toxicity-reference.json` from
   `github/envia/2026/devel/0730`, tolerance 1e-3):
   - WebGL1 and WebGL2 on NVIDIA (`DISPLAY=:1`, real X server).
   - WebGL1 and WebGL2 on Mesa llvmpipe (`xvfb-run`, `LIBGL_ALWAYS_SOFTWARE=1`).
   The probe is injected through stdin (`src/shell/Console.cpp`, 1023-byte
   lines) in chunks with a `console.log` acknowledgement per chunk.
4. Push `indigo/2025/webgl2/0375` to `origin` and the test commit to
   `web_tc_new_`.

Expected reference numbers from 2026-09-16 (Debug, 3-sentence classify):
CPU about 210 s, WebGL1 about 19 s on both llvmpipe and RTX 3050, maximum
probability difference against CPU about 1e-7. Release build: WebGL1 about
1.2 s, WebGL2 about 1.1 s.

## Known remaining gaps (not in this plan)

Khronos `ext-color-buffer-float.html` still fails: float renderbuffer
enable-gating, `RGB16F` rejection and `getInternalformatParameter` are not
implemented. `clearBufferfv` is unimplemented. None of these are on the TFJS
toxicity path.
