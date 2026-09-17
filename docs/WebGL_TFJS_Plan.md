# WebGL acceleration plan for the TensorFlow.js toxicity demo

Written 2026-09-17. The Claude Code branch (`0375`) and the Codex branch
(`0376`) each keep their own plan document at this path; the two documents
differ in wording and language but share the agreed requirements recorded
here. Revision 10: the validation tool is committed as the first commit of each
working branch, and `0377` carries engine changes, tests and `docs/Spec.md`
only; the tool, this plan and the results document stay on `0375` / `0376`
(user decisions, 2026-09-17).

Goal: make https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html
run on the TensorFlow.js `webgl` backend with both WebGL1
(`?tfjsflags=WEBGL_VERSION:1`) and WebGL2 (the page default), on top of
`master` 1.5.6 (`13c4ffd576`).

Scope: only what the TFJS WebGL backend touches. Complete WebGL extension or
WebGL2 conformance is out of scope, but every change must be spec-correct for
the part it implements and must not regress currently passing tests. A known
limit of a partial implementation is recorded as such; it is never a reason
to introduce a new spec violation. A successful validation is not a claim of
full conformance or of the absence of all regressions.

## Acceptance criteria

- The unmodified hosted page loads the model, renders the initial table and
  classifies an additional input, once with WebGL2 (default) and once with
  `WEBGL_VERSION:1`.
- Each run records the TFJS backend actually selected (`tf.getBackend()`), the
  WebGL version, `gl.RENDERER`, `WEBGL_RENDER_FLOAT32_ENABLED` and, for
  WebGL2, `WEBGL_BUFFER_SUPPORTED`. A CPU fallback is a failure, not a pass.
- Software GL (Mesa llvmpipe) and hardware GL (NVIDIA RTX 3050) are reported
  separately; a software renderer does not count as GPU validation. Hardware
  runs record the renderer string reported by Starfish's own GL context and
  the `nvidia-smi` process entry.
- Fixed comparison setup: TFJS 1.2.2 and the toxicity model as served by the
  demo, threshold 0.9 (the demo's value), inputs = the demo's three initial
  sentences plus "Thank you for helping me." (7 labels × 4 inputs, 28
  decisions; the three initial sentences give the 21 decisions quoted below).
  The CPU reference is recomputed with the current build before the first
  code change and compared with the 0730 JSON; a mismatch stops the work
  until explained.
- Pass rule: every decision matches the CPU reference and the maximum
  absolute probability error is at most 1e-3. NaN, Infinity, a missing result
  or a shape mismatch fails regardless of tolerance.
- Small matrix multiplications (float32 and half-float) are checked with
  `WEBGL_CPU_FORWARD=false` so the GL path itself is exercised.
- Test suites are diffed against a baseline captured from the same build
  configuration before the first code change. Pre-existing failures and new
  failures are reported separately; a new failure blocks completion until its
  cause is understood and fixed.
- Timings are recorded but are not a pass criterion.

## Branches and roles

| Checkout | Branch | Who |
|---|---|---|
| `/home/hwang/work/starfish_f_claude` | `origin/indigo/2025/webgl2/0375` | Claude Code |
| `/home/hwang/work/starfish_f_codex` | `origin/indigo/2025/webgl2/0376` | Codex |
| `/home/hwang/work/starfish_f` | `origin/indigo/2025/webgl2/0377` | Agreed result of 0375 and 0376 |
| `<checkout>/web_tc_new_` | `origin/indigo/2025/webgl2/0375` (Claude), `0376` (Codex) | Test assets (see Testing) |

Pushing this document does not make the code agreed; each commit is reviewed
between the two branches before it is taken into `0377`. `0377` receives the
engine changes, the test activations and the `docs/Spec.md` updates.
`tool/tfjs_toxicity/`, `docs/WebGL_TFJS_Plan.md` and
`docs/WebGL_TFJS_Validation.md` are working assets of `0375` / `0376` and
are not carried into `0377`. The untracked repo-root `Makefile` and the
`web_tc_new_/` checkout are never committed to this repository.

Development environment: Linux x86_64, `SHELL=x11`, `BACKEND=uv_cairo_gl`,
`CMAKE_BUILD_TYPE=Debug`, `WEBGL=1` (`make` with the untracked `Makefile`
configures `out/webgl2`). GPU: NVIDIA GeForce RTX 3050 OEM, driver 595.91.07,
`DISPLAY=:1`, `/dev/dri/renderD128`. The Codex sandbox needs its
outside-sandbox execution permission for GPU runs; every hardware run records
Starfish's own renderer string, not only host-level `glxinfo`.

## Reference branches

`github` remote: `git@github.com:envia/lightweight-web-engine.git`
(fetched locally from `/home/hwang/work/starfish_f_`).

| Branch | What to take from it |
|---|---|
| `origin/indigo/2025/webgl2/0374` | Most complete 7-commit series, validated on NVIDIA RTX 3050 for WebGL1 and WebGL2. Primary source for commits 3 to 6. |
| `origin/indigo/2025/webgl2/0373` | Extension registry initialization fix; alternative texture upload and readPixels implementations. |
| `origin/indigo/2025/webgl2/0372` | Earlier 8-commit series; same fixes minus the registry initialization fix. |
| `origin/indigo/2025/webgl2/0171` | Older WebGL2 work (texStorage, buffer objects, IDL updates). Background only. |
| `origin/claude/2026/tfjs/0002` | Registry initialization fix with a `WebContainerTest` gtest that clears the current GL context before creating a WebGL context. |
| `github/envia/2026/devel/0730` | Codex single-commit version of the same fixes. Its `tests/webgl/toxicity-probe.js`, `tests/webgl/toxicity-reference.json` (TFJS 1.2.2, CPU backend, four inputs) and `tests/webgl/run.py` are reused for the end-to-end check after re-deriving the reference. |
| `github/envia/2026/devel/0022`, `0750` | Codex patch series against the public repo; same content as 0372 plus a local toxicity demo bundle. |

Branches are not merged; each change is compared against the current code and
the spec. Results recorded in those branches are not reused as validation of
this work. Every commit message names the reference commit hashes it drew
from, so later branch moves do not lose the trail.

The internal HTML tests that 0374 registered in `tool/reftest/cairo/internal.res`
(`webgl-float-texture-upload.html`, `webgl1-float-render-target.html`,
`webgl-extension-version.html`, `webgl2-pixel-readback.html`) were searched
for in the `test/` submodule's fetched refs, in `web_tc_new` and
`web_tc_new_`, and in the 0374 tree itself; none contain them. They are
rewritten here. Anyone who finds an existing copy reuses it instead.

## Step 0: baseline

After commit 1 and before the first engine change, on that build:

- Run `internal_test`, `vendor_test_khronos`, `vendor_test_khronos2`,
  `vendor_test_khronossdk` and `wpt_serve_testharness_canvas` under
  `xvfb-run` and keep the result lists.
- Run the toxicity probe with `WEBGL_VERSION:1` and `:2` on llvmpipe and on
  NVIDIA, recording backend, version, renderer and the failure mode (CPU
  fallback, hang, exception).
- Recompute the CPU reference with the current build and compare it with the
  0730 JSON (inputs, model, TFJS version, probabilities).

## Commit sequence

Each commit builds, passes `./tool/lint/check_tidy.py`, and passes the tests
listed for it under `xvfb-run -s '-screen 0 1920x1080x24' -a`. The tests that
cover a commit are part of that commit's change set (test asset commit hash in
the message), never deferred to a later commit. IDL changes need a cmake
re-run.

The order keeps every intermediate commit no worse for TFJS than `master`:
WebGL2 `EXT_color_buffer_float` is exposed last, because exposing it before
`readPixels` into a pack buffer exists turns the current CPU fallback into a
hang in the TFJS download path (recorded in 0373 `614c9a3c15`).

### 1. Add the TFJS toxicity validation tool

- New `tool/tfjs_toxicity/` with `run.py` (launches Starfish on the hosted
  demo or the CPU reference page, injects the probe over stdin in 350-byte
  chunks with a `console.log` acknowledgement per chunk, records backend,
  WebGL version, renderer, decisions and probability error, and diffs against
  the reference), `toxicity-probe.js` (observes the unmodified demo through
  its Parcel module exports) and `toxicity-reference.json` (TFJS 1.2.2, CPU
  backend, four inputs, tolerance 1e-3; extended with the input strings and,
  for every asset the demo loads (page scripts, model manifest, weight
  shards, vocabulary), the URL and SHA-256 of the content, so a changed
  hosted demo is detected even when the URLs stay the same and a drifted
  page is never compared against the fixed reference), plus a short
  `README.md`. Source:
  0730 `02094e8638`, `ca3fb940ee`, `7818039497` (`tests/webgl/`), adapted to
  the `tool/` layout and to the matrix rows of this plan (backend, build
  type, GL environment as arguments instead of the fixed four targets).
- The tool's own `README.md` documents the invocation. The repository
  `README.md` is not changed because the tool does not go to `0377`.
- No engine change. The reference JSON is regenerated with the current build
  in step 0 and replaced if it differs.

### 2. Initialize WebGL extension registry under a current GL context

`WebGLExtensionRegistry::initialize()` runs from the `WebGLRenderingContext`
constructor before any `GLContextScope` is entered. When the first WebGL
context of the process is created synchronously during page load, no GL
context is current, `glGetString(GL_EXTENSIONS)` returns null and the registry
freezes empty for the whole process (every `getExtension()` returns null,
BGRA detection flips off). This is the root cause of "no extensions on
llvmpipe / libuv".

- Move the initialization into `WebGLRenderingContext::initialize()` inside
  its `GLContextScope`. This is the fix.
- As a guard only, not a substitute: when `GL_EXTENSIONS` still reads back
  null, log and stay uninitialized so a later context retries, and accessors
  tolerate an uninitialized registry.
- Reference: 0373 `7cf38c70e7`, claude/tfjs/0002 `15f91a2917` and
  `77e1a61164`.
- Tests: new `test/cairo/internal-test/canvas/webgl-extension-registry.html`
  creates a WebGL1 and a WebGL2 context synchronously in a page-load script,
  asserts `getSupportedExtensions()` is non-empty when the driver advertises
  any registry extension, and that `getExtension()` agrees with the list. The
  `uv_cairo_gl` runner reproduces the no-current-context start condition; if
  a run shows it does not, the `WebContainerTest` gtest from claude/tfjs/0002
  (clears the current context, then creates a context) is added in the same
  commit.

### 3. Fix float texture uploads and null texture initialization

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
  oversized level rejected, WebGL2 unpack-buffer conflict); activate Khronos
  `conformance/textures/texture-size.html`; activate
  `conformance/extensions/oes-texture-float.html` and
  `oes-texture-half-float.html` if they pass on llvmpipe.

### 4. Support WebGL1 float render targets on ES3

TFJS decides `WEBGL_RENDER_FLOAT32_CAPABLE` by attaching a `RGBA` / `FLOAT`
texture to a framebuffer and checking completeness. On an ES3 driver only the
sized formats are color-renderable through `EXT_color_buffer_float`.

- Track the native `GL_EXT_color_buffer_float` capability in the registry
  without exposing any new WebGL extension. Three things stay distinct: the
  native capability, the WebGL extension being exposed (commit 6, WebGL2
  only), and the extension being enabled by the page.
- When that capability is present and the context is WebGL1, store `RGBA` /
  `RGB` + `FLOAT` as `RGBA32F` / `RGB32F`, and `HALF_FLOAT_OES` as `RGBA16F` /
  `RGB16F` with the core `GL_HALF_FLOAT` upload type. WebGL1 input validation
  and the GLES2 fallback stay unchanged.
- Renderability is a driver property, not something this commit asserts:
  `RGBA32F` and `RGBA16F` are color-renderable under
  `EXT_color_buffer_float`; `RGB32F` and `RGB16F` are not. The storage
  conversion for RGB is for upload and sampling only.
- Reference: 0374 `ec8ae45660`.
- Tests: new `test/cairo/internal-test/canvas/webgl1-float-render-target.html`
  (RGBA float and RGBA half-float textures attached to an FBO are
  `FRAMEBUFFER_COMPLETE`; a draw into them followed by a sampling pass
  reproduces values outside [0, 1]; RGB float textures upload and sample
  correctly and their framebuffer status is only recorded, not asserted).
  After this commit the demo with `WEBGL_VERSION:1` must pass the acceptance
  criteria.

### 5. Implement WebGL2 readPixels into pixel pack buffers

TFJS downloads WebGL2 results through a `PIXEL_PACK_BUFFER`, a fence and
`getBufferSubData`. Both WebGL2 `readPixels` overloads are `[Unimplemented]`
and throw "Illegal invocation".

- Implement `readPixels(..., GLintptr offset)` against the bound pack buffer
  (byte offset) and `readPixels(..., ArrayBufferView dstData, dstOffset)`
  (element offset of the view).
- Validate format/type enums, element alignment of the offset, and the bytes
  the read touches from `PACK_ALIGNMENT`, `PACK_ROW_LENGTH`, `PACK_SKIP_ROWS`,
  `PACK_SKIP_PIXELS` (OpenGL ES 3.0 §4.3.2) so an undersized buffer never
  becomes an out-of-bounds driver write.
- The ArrayBufferView overload generates `INVALID_OPERATION` while a pack
  buffer is bound; the offset overload does so when none is bound.
- `getBufferSubData`: reject `dstOffset` / `length` beyond the destination
  view before computing the copy.
- NVIDIA workaround (0374 reports the driver wants padding after the final
  row of a PBO read): reproduce on the current driver first; adopt the
  temporary `PACK_ROW_LENGTH = width` only if reproduced, restore the
  previous value afterwards, and verify llvmpipe behaves identically.
- Remove the two `[Unimplemented]` markers in `WebGL2RenderingContext.idl`;
  update `docs/Spec.md` (readPixels overloads).
- While working on this commit, expose `EXT_color_buffer_float` on the
  pre-commit tree once, in a separate worktree or a clearly separated patch
  that never enters the feature commit, run the demo with a time limit, and
  record in the results document whether the TFJS WebGL2 download hang from
  0373 `614c9a3c15` reproduces on the current code. If it does not, record
  that observation as is; the reference branch's record is not treated as a
  current result.
- Float readback needs a float color attachment, which WebGL2 pages may only
  render to once `EXT_color_buffer_float` is enabled, and that extension is
  exposed in commit 6. The commit 5 test therefore covers the byte paths and
  every error path as mandatory; its float cases are gated on
  `getExtension('EXT_color_buffer_float')` and report "not run" when it is
  absent. Commit 6 must re-run the test with the float cases mandatory; a
  skipped float case is never counted as a pass.
- Reference: 0374 `423b832f10`; 0373 `614c9a3c15`; 0730 `02094e8638`.
- Tests: new `test/cairo/internal-test/canvas/webgl2-pixel-readback.html`
  (PBO read plus fence plus `getBufferSubData`, odd widths, element offsets,
  subviews, float values outside [0, 1], empty ranges, undersized buffer,
  huge sizes, misaligned offset and invalid type errors, view overload while
  a PBO is bound); activate Khronos
  `conformance2/reading/read-pixels-into-pixel-pack-buffer.html` and
  `read-pixels-pack-parameters.html`; confirm
  `conformance2/buffers/get-buffer-sub-data.html` stays passing.

### 6. Expose EXT_color_buffer_float to WebGL2 and filter extensions by version

- Register `EXT_color_buffer_float` (new IDL interface, no members) when the
  driver advertises `GL_EXT_color_buffer_float`. Expose it to WebGL2 only.
- `getSupportedExtensions()` and `getExtension()` filter by context version
  following the Khronos WebGL extension registry, and stay consistent with
  each other:
  - WebGL1 never lists `EXT_color_buffer_float`.
  - WebGL2 does not list the WebGL1 extensions it promoted to core. Of the
    registry's current set that means `OES_texture_float`,
    `OES_texture_half_float`, `OES_standard_derivatives`,
    `OES_vertex_array_object`, `WEBGL_depth_texture` and `EXT_blend_minmax`;
    `OES_texture_float_linear` and `EXT_texture_filter_anisotropic` remain
    available in both versions. This fixes an existing over-exposure and is
    the default, not conditional on a failing test.
- Update `docs/Spec.md` WebGL section (extension list, "NOT implemented"
  list, version notes).
- Reference: 0374 `12bc919205`; 0730 `02094e8638`.
- Tests: new `test/cairo/internal-test/canvas/webgl-extension-version.html`
  (the rules above, both queries consistent); activate Khronos
  `conformance2/extensions/promoted-extensions.html`; re-run
  `webgl2-pixel-readback.html` with its float cases now mandatory (PBO and
  view overloads reading `RGBA` / `FLOAT` from an `RGBA32F` attachment,
  values outside [0, 1]). After this commit the demo with default WebGL2
  must pass the acceptance criteria.

### 7. Document the validation results

- New `docs/WebGL_TFJS_Validation.md`: per matrix row, the source revision,
  build options, driver and renderer string, TFJS backend and version
  selected, per-input decisions against the CPU reference, maximum
  probability error, suite diffs against the baseline (pre-existing versus
  new failures), timings for orientation, and every limit or unverified item.
  The step 0 baseline observations are recorded in the same document.
- When `0377` is validated, the same document records the `0377` revision
  that was run and the `0375` / `0376` commit hash of the tool used, since the
  tool itself is not on `0377` (Codex proposal, `8c5ad90cfb`).
- `docs/WebGL_TFJS_Plan.md` is updated to its final agreed state in the same
  commit.
- `docs/Spec.md` changes land with the commits that change the surface (5
  and 6). This commit and the plan document stay on `0375` / `0376`.

## Testing

Internal tests use `console.assert` and `testEnd()` and must also run in a
plain browser. They live in the `test/` submodule
(`test/cairo/internal-test/canvas/`) and are registered in
`tool/reftest/cairo/internal.res`.

Test asset flow, identical for both branches:

1. Commit in `<checkout>/test` (submodule worktree, remote
   `lws-test/web_tc_new`).
2. Fetch the same commit objects into `<checkout>/web_tc_new_` (clone of the
   fork `jh1984-hwang/web_tc_new`, currently at `254715162`) and push them
   there as `indigo/2025/webgl2/0375` (Claude) or `0376` (Codex). The clone
   inside each Starfish checkout is the one used; `/home/hwang/work/web_tc_new_`
   is a separate clone of the same fork and is left alone.
3. Each engine commit message records the test commit hash it depends on and
   the `.res` lines it activates.
4. The submodule gitlink in this repository is not bumped on `0375` or
   `0376` (user decision). `0377` bumps it to the final agreed test commit
   once that commit is on a ref the submodule URL can reach, so a fresh
   checkout reproduces the tests; until then the test hash in the commit
   messages is the pointer.

Khronos activations follow the `.res` rule: uncomment only tests that pass
in this build, never delete or comment a line to make a run green, never relax
an expectation to fit the implementation.

Validation matrix. All eight rows are required (user decision, 2026-09-17).
Each row runs WebGL1 and WebGL2 forced, plus the page's own automatic
selection. Builds use separate output directories (`out/<backend>-<type>`).

| Backend | Build | GL | Suites | Toxicity WebGL1 / WebGL2 |
|---|---|---|---|---|
| `uv_cairo_gl` | Debug | llvmpipe (`xvfb-run`, `LIBGL_ALWAYS_SOFTWARE=1`) | all five, diffed against baseline | yes |
| `uv_cairo_gl` | Debug | NVIDIA (`DISPLAY=:1`) | activated tests | yes |
| `uv_cairo_gl` | Release | llvmpipe | none (no `testEnd` binding) | yes |
| `uv_cairo_gl` | Release | NVIDIA | none | yes |
| `glib_cairo_gl` | Debug | llvmpipe | `internal_test`, `vendor_test_khronos`, `vendor_test_khronos2` | yes |
| `glib_cairo_gl` | Debug | NVIDIA | activated tests | yes |
| `glib_cairo_gl` | Release | llvmpipe | none | yes |
| `glib_cairo_gl` | Release | NVIDIA | none | yes |

Final verification, run sequentially (llvmpipe is CPU bound):

1. `./tool/lint/check_tidy.py`.
2. Suites per the matrix under `xvfb-run` with `LP_NUM_THREADS=4`, diffed
   against the step 0 baseline. No new failures.
3. Toxicity demo per the acceptance criteria on every required matrix row,
   both the forced versions and the page's own automatic selection. The probe
   is injected through stdin (`src/shell/Console.cpp`, 1023-byte lines) in
   chunks with a `console.log` acknowledgement per chunk; Release builds have
   no `testEnd` binding, so the probe output is the result.
4. Record the results (commit 7) and push `indigo/2025/webgl2/0375` to
   `origin` and the test commits to `web_tc_new_`.

Every log records the source revision, build options, driver and renderer,
TFJS and model version, per-input decisions, maximum probability error and
any failures or limits.

Magnitudes observed on 2026-09-16 (Debug, 3-sentence classify), for
orientation only and not a pass criterion: CPU about 210 s, WebGL1 about 19 s
on both llvmpipe and RTX 3050, maximum probability difference against CPU
about 1e-7. Release: WebGL1 about 1.2 s, WebGL2 about 1.1 s.

## Settled between 0375 and 0376

- 2026-09-17: all eight matrix rows are required; results are documented in
  `docs/WebGL_TFJS_Validation.md` (commit 7).
- 2026-09-17: the validation tool is committed under `tool/tfjs_toxicity/`
  (commit 1) on `0375` / `0376` only.
- 2026-09-17: `0377` updates `docs/Spec.md` only; the tool, the plan and the
  results document are not carried over, so each branch may keep its own
  language.

## Known remaining gaps (not in this plan)

Khronos `ext-color-buffer-float.html` still fails: float renderbuffer
enable-gating, `RGB16F` rejection and `getInternalformatParameter` are not
implemented. `clearBufferfv` is unimplemented. None of these are on the TFJS
toxicity path.
