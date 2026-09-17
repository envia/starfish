# WebGL acceleration plan for the TensorFlow.js toxicity demo

Written 2026-09-17. Shared between the Claude Code branch (`0375`) and the
Codex branch (`0376`); the agreed version of this document is the same on
both branches so that `0377` can take either.

Goal: make https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html
run on the TensorFlow.js `webgl` backend with both WebGL1
(`?tfjsflags=WEBGL_VERSION:1`) and WebGL2 (the page default), on top of
`master` 1.5.6 (`13c4ffd576`).

Scope: only what the TFJS WebGL backend touches. Complete WebGL extension or
WebGL2 conformance is out of scope, but every change must be spec-correct for
the part it implements and must not regress currently passing tests. A
successful validation is not a claim of full conformance or of the absence of
all regressions.

## Acceptance criteria

- The unmodified hosted page loads the model, renders the initial table and
  classifies an additional input, once with WebGL2 (default) and once with
  `WEBGL_VERSION:1`.
- Each run records the TFJS backend actually selected (`tf.getBackend()`), the
  WebGL version, `gl.RENDERER` and `WEBGL_RENDER_FLOAT32_ENABLED`. A CPU
  fallback is a failure, not a pass.
- Software GL (Mesa llvmpipe) and hardware GL (NVIDIA RTX 3050) are reported
  separately; a software renderer does not count as GPU validation.
- Predictions are compared with a CPU reference computed by the same TFJS
  build (1.2.2) and model on the same inputs. Fixed inputs: the demo's three
  initial sentences plus "Thank you for helping me." (7 labels × 4 inputs,
  28 decisions; the three initial sentences give the 21 decisions quoted
  below). All decisions must match; probability tolerance 1e-3.
- Test suites are diffed against a baseline captured from the same build
  configuration before the first code change. Pre-existing failures and new
  failures are reported separately; a new failure blocks completion until its
  cause is understood and fixed.

## Branches and roles

| Checkout | Branch | Who |
|---|---|---|
| `starfish_f_claude` | `origin/indigo/2025/webgl2/0375` | Claude Code |
| `starfish_f_codex` | `origin/indigo/2025/webgl2/0376` | Codex |
| `starfish_f` | `origin/indigo/2025/webgl2/0377` | Agreed result of 0375 and 0376 |
| `web_tc_new_` | `origin/indigo/2025/webgl2/0375` | Test assets (see Testing) |

Pushing this document does not make the code agreed; each commit is reviewed
between the two branches before it is taken into `0377`. The untracked
repo-root `Makefile` and the `web_tc_new_/` checkout are never committed.

Development environment: Linux x86_64, `SHELL=x11`, `BACKEND=uv_cairo_gl`,
`CMAKE_BUILD_TYPE=Debug`, `WEBGL=1` (`make` with the untracked `Makefile`
configures `out/webgl2`). The Codex sandbox has no GPU or `DISPLAY=:1`
access, so hardware runs are executed from the Claude Code environment or by
the user and their logs are shared.

## Reference branches

`github` remote: `git@github.com:envia/lightweight-web-engine.git`
(fetched locally from `/home/hwang/work/starfish_f_`).

| Branch | What to take from it |
|---|---|
| `origin/indigo/2025/webgl2/0374` | Most complete 7-commit series, validated on NVIDIA RTX 3050 for WebGL1 and WebGL2. Primary source for commits 2 to 5. |
| `origin/indigo/2025/webgl2/0373` | Extension registry initialization fix; alternative texture upload and readPixels implementations. |
| `origin/indigo/2025/webgl2/0372` | Earlier 8-commit series; same fixes minus the registry initialization fix. |
| `origin/indigo/2025/webgl2/0171` | Older WebGL2 work (texStorage, buffer objects, IDL updates). Background only. |
| `origin/claude/2026/tfjs/0002` | Registry initialization fix with a `WebContainerTest` gtest that clears the current GL context before creating a WebGL context. |
| `github/envia/2026/devel/0730` | Codex single-commit version of the same fixes. Its `tests/webgl/toxicity-probe.js`, `tests/webgl/toxicity-reference.json` (TFJS 1.2.2, CPU backend, four inputs) and `tests/webgl/run.py` are reused for the end-to-end check. |
| `github/envia/2026/devel/0022`, `0750` | Codex patch series against the public repo; same content as 0372 plus a local toxicity demo bundle. |

Branches are not merged; each change is compared against the current code and
the spec. Results recorded in those branches are not reused as validation of
this work. Every commit message names the reference commit hashes it drew
from, so later branch moves do not lose the trail.

The internal HTML tests that 0374 registered in `tool/reftest/cairo/internal.res`
were never committed to any test repository. They are rewritten here.

## Step 0: baseline (no commit)

Before the first code change, on the `master` build:

- Run `internal_test`, `vendor_test_khronos`, `vendor_test_khronos2` under
  `xvfb-run` and keep the result lists.
- Run the toxicity probe with `WEBGL_VERSION:1` and `:2` on llvmpipe and on
  NVIDIA, recording backend, version, renderer and the failure mode (CPU
  fallback, hang, exception).
- Keep the CPU reference JSON from 0730 and re-derive it once with the
  current build to confirm the inputs and model are unchanged.

## Commit sequence

Each commit builds, passes `./tool/lint/check_tidy.py`, and passes the tests
listed for it under `xvfb-run -s '-screen 0 1920x1080x24' -a`. IDL changes
need a cmake re-run. The order keeps every intermediate commit no worse for
TFJS than `master`: WebGL2 `EXT_color_buffer_float` is exposed last, because
exposing it before `readPixels` into a pack buffer exists turns the current
CPU fallback into a hang in the TFJS download path.

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
- Reference: 0373 `7cf38c70e7`, claude/tfjs/0002 `15f91a2917` and
  `77e1a61164`.
- Tests: new `test/cairo/internal-test/canvas/webgl-extension-registry.html`
  creates a WebGL1 and a WebGL2 context synchronously in a page-load script,
  asserts `getSupportedExtensions()` is non-empty when the driver advertises
  any registry extension, and that `getExtension()` agrees with the list.
  Both backends (`uv_cairo_gl`, `glib_cairo_gl`) must pass if both are built.

### 2. Fix float texture uploads and null texture initialization

Shared `handleTexImageWithArrayBufferView` path for WebGL1 and WebGL2:

- Add an internal `virtual int webGLVersion() const` (1 / 2) to the contexts;
  no JavaScript-visible change.
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
- Reference: 0374 `cd0cc4d619`, `5da583748d`; 0373 `94e01891bc`.
- Tests: new `test/cairo/internal-test/canvas/webgl-float-texture-upload.html`
  (float and half-float uploads with correct sizes and preserved data,
  undersized view rejected, wrong typed array rejected, null fill reads back
  zero alpha, existing byte textures unchanged, null `texSubImage2D` error,
  oversized level rejected); activate Khronos
  `conformance/textures/texture-size.html`; activate
  `conformance/extensions/oes-texture-float.html` and
  `oes-texture-half-float.html` if they pass on llvmpipe.

### 3. Support WebGL1 float render targets on ES3

TFJS decides `WEBGL_RENDER_FLOAT32_CAPABLE` by attaching a `RGBA` / `FLOAT`
texture to a framebuffer and checking completeness. On an ES3 driver only the
sized formats are color-renderable through `EXT_color_buffer_float`.

- Track the native `GL_EXT_color_buffer_float` capability in the registry
  without exposing any new WebGL extension.
- When that capability is present and the context is WebGL1, store `RGBA` /
  `RGB` + `FLOAT` as `RGBA32F` / `RGB32F`, and `HALF_FLOAT_OES` as `RGBA16F` /
  `RGB16F` with the core `GL_HALF_FLOAT` upload type. WebGL1 input validation
  and the GLES2 fallback stay unchanged.
- Reference: 0374 `ec8ae45660`.
- Tests: new `test/cairo/internal-test/canvas/webgl1-float-render-target.html`
  (float and half-float texture attached to an FBO is `FRAMEBUFFER_COMPLETE`,
  a draw into it followed by a sampling pass reproduces values outside
  [0, 1]). After this commit the demo with `WEBGL_VERSION:1` must pass the
  acceptance criteria.

### 4. Implement WebGL2 readPixels into pixel pack buffers

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
  update `docs/Spec.md` (readPixels overloads).
- Reference: 0374 `423b832f10`; 0373 `614c9a3c15`; 0730 `02094e8638`.
- Tests: new `test/cairo/internal-test/canvas/webgl2-pixel-readback.html`
  (PBO read plus fence plus `getBufferSubData`, odd widths, element offsets,
  float values outside [0, 1], empty ranges, undersized buffer, huge sizes,
  misaligned offset and invalid type errors, view overload while a PBO is
  bound); activate Khronos
  `conformance2/reading/read-pixels-into-pixel-pack-buffer.html` and
  `read-pixels-pack-parameters.html`.

### 5. Expose EXT_color_buffer_float to WebGL2 and filter extensions by version

- Register `EXT_color_buffer_float` (new IDL interface, no members) when the
  driver advertises `GL_EXT_color_buffer_float`. Expose it to WebGL2 only.
- `getSupportedExtensions()` and `getExtension()` filter by context version.
- Open decision: hide from WebGL2 the WebGL1 extensions it promoted to core
  (`OES_texture_float`, `OES_texture_half_float`, `OES_standard_derivatives`,
  `OES_vertex_array_object`, `WEBGL_depth_texture`, `EXT_blend_minmax`), as
  the Khronos registry specifies. 0730 hides them, 0374 does not. Default:
  keep exposing them unless `vendor_test_khronos2` needs the change.
- Update `docs/Spec.md` WebGL section (extension list, "NOT implemented"
  list).
- Reference: 0374 `12bc919205`; 0730 `02094e8638`.
- Tests: new `test/cairo/internal-test/canvas/webgl-extension-version.html`
  (WebGL1 never lists `EXT_color_buffer_float`; WebGL2 lists it iff
  `getExtension()` returns an object; results consistent between the two
  queries). After this commit the demo with default WebGL2 must pass the
  acceptance criteria.

## Testing

Internal tests use `console.assert` and `testEnd()` and must also run in a
plain browser. They live in the `test/` submodule
(`test/cairo/internal-test/canvas/`) and are registered in
`tool/reftest/cairo/internal.res`. Commits in `test/` are made in the
`starfish_f_claude` checkout, fetched into `/home/hwang/work/web_tc_new_` as
the same commit objects and pushed there as `indigo/2025/webgl2/0375`. The
submodule gitlink in this repository is not bumped; pick the final test commit
when integrating `0377`. Codex test assets follow the same rule on
`indigo/2025/webgl2/0376` in `web_tc_new_`.

Khronos activations follow the `.res` rule: uncomment only tests that pass
in this build, never delete or comment a line to make a run green, never relax
an expectation to fit the implementation.

Validation matrix. Rows marked required gate completion; the others are run
when time allows and reported as such.

| Backend | Build | GL | Suites | Toxicity WebGL1 / WebGL2 | Required |
|---|---|---|---|---|---|
| `uv_cairo_gl` | Debug | llvmpipe (`xvfb-run`, `LIBGL_ALWAYS_SOFTWARE=1`) | yes, diffed against baseline | yes | yes |
| `uv_cairo_gl` | Debug | NVIDIA (`DISPLAY=:1`) | targeted only | yes | yes |
| `uv_cairo_gl` | Release | NVIDIA | no | yes (timing smoke test) | yes |
| `glib_cairo_gl` | Debug | llvmpipe | internal_test | yes | optional |
| `glib_cairo_gl` | Release | NVIDIA | no | yes | optional |

Final verification, run sequentially (llvmpipe is CPU bound):

1. `./tool/lint/check_tidy.py`.
2. `internal_test`, `vendor_test_khronos`, `vendor_test_khronos2` under
   `xvfb-run` with `LP_NUM_THREADS=4`, diffed against the step 0 baseline.
   No new failures.
3. Toxicity demo per the acceptance criteria on every required matrix row.
   The probe is injected through stdin (`src/shell/Console.cpp`, 1023-byte
   lines) in chunks with a `console.log` acknowledgement per chunk; Release
   builds have no `testEnd` binding, so the probe output is the result.
4. Push `indigo/2025/webgl2/0375` to `origin` and the test commits to
   `web_tc_new_`.

Every log records the source revision, build options, driver and renderer,
TFJS and model version, per-input decisions, maximum probability error and
any failures or limits.

Expected magnitudes from 2026-09-16 (Debug, 3-sentence classify; expectations,
not results): CPU about 210 s, WebGL1 about 19 s on both llvmpipe and RTX
3050, maximum probability difference against CPU about 1e-7. Release: WebGL1
about 1.2 s, WebGL2 about 1.1 s.

## Open items for review between 0375 and 0376

- Whether to commit the toxicity probe and runner into the repository (0730
  put them under `tests/webgl/`, which is not a repository convention) or keep
  them as untracked tooling described by this document. Default: untracked.
- The promoted-extension decision in commit 5.
- Whether `glib_cairo_gl` rows become required.

## Known remaining gaps (not in this plan)

Khronos `ext-color-buffer-float.html` still fails: float renderbuffer
enable-gating, `RGB16F` rejection and `getInternalformatParameter` are not
implemented. `clearBufferfv` is unimplemented. None of these are on the TFJS
toxicity path.
