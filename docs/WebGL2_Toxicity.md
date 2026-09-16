# TensorFlow.js toxicity on WebGL2

Build with `-DWEBGL=1`. The original demo selects WebGL2 without URL flags:

```sh
./Starfish 'https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html'
```

This completes the WebGL2 path used by this demo, not the entire WebGL2 API.
The engine now exposes `EXT_color_buffer_float` to WebGL2 on drivers with
native `GL_EXT_color_buffer_float`, and implements `readPixels` with PBO
byte offsets and TypedArray element offsets. Readback validates pack state,
alignment, destination types and buffer bounds before calling the driver.
Empty destination range checks in `getBufferSubData` avoid unsigned
underflow and division by zero. WebGL1 extension filtering is preserved.

## Validation (2026-09-16)

Debug uv_cairo_gl/x11 build; NVIDIA GeForce RTX 3050 OEM/PCIe/SSE2,
driver 595.91.07. The original hosted page reported TFJS backend `webgl`,
`WEBGL_VERSION=2`, and `WEBGL_BUFFER_SUPPORTED=true`. Its initial three
inputs rendered the expected results, and clicking classify for
`Thank you for your help.` appended seven false classifications.

- Full model: all 21 decisions match the previously rerun CPU baseline.
- Across 42 probabilities, maximum absolute error: `1.1920928955078125e-7`.
- Model loading plus inference: 19076 ms; this is not a controlled benchmark.
- Matrix multiplication with CPU forwarding disabled: `[7, 10, 15, 22]`.
- Existing Canvas regressions: 18/18 passed on NVIDIA.
- New pixel readback regression: passed on NVIDIA and Mesa llvmpipe.
- Khronos `get-buffer-sub-data`, `read-pixels-into-pixel-pack-buffer`, and
  `read-pixels-pack-parameters`: passed on both drivers. The latter two are
  now active in `tool/reftest/cairo/khronos_webgl2.res`.
- WebGL C++ tidy: 37 files, zero errors.

The readback regression checks subviews, element offsets, float values
outside [0, 1], fence completion, pack skips, padding sentinels, empty
arrays, invalid types, misaligned offsets and undersized/huge ranges.
NVIDIA required an explicit equivalent row length for PBO reads whose last
row has no trailing alignment padding; this is covered by odd-width cases.

Regression assets are mirrored in `test/` and `web_tc_new_/`:

- `cairo/internal-test/canvas/webgl-extension-version.html`
- `cairo/internal-test/canvas/webgl2-pixel-readback.html`

Both are registered in `tool/reftest/cairo/internal.res`. WPT's pinned
WebGL corpus has no equivalent PBO readback coverage; the internal and
Khronos tests cover this behavior instead. The test submodule gitlink is
intentionally not updated; select its final commit manually when integrating.

## Remaining conformance limits

The broader Khronos `ext-color-buffer-float.html` still fails on both
drivers: extension-enable gating for float renderbuffers, RGB16F rejection,
and the unimplemented `getInternalformatParameter` API remain incomplete.
Its known-failure list entry stays commented. `clearBufferfv` is also still
unimplemented. These APIs are not used by the tested toxicity path; this
validation must not be read as complete extension or WebGL2 conformance.

## Repeating the hardware checks

The wrapper uses the current login's NVIDIA display because Xvfb's own
display cannot initialize NVIDIA EGL on this machine:

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env \
  DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority \
  __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json \
  ./Starfish 'https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html' \
  --hide-window --timeout=600
```

For numerical reproduction, use the preserved local diagnostic
`webgl-toxicity-2026-09-15/webgl1/model.html?tfjsflags=WEBGL_VERSION:2`
as an absolute `file://` URL, despite its historical `webgl1` directory name.
Compare its `MODEL_RESULT` against `out/gpu-validation-20260916/cpu.log`.
Logs from this change are under `out/webgl2-validation/`: model and matrix
NVIDIA logs, Canvas results, both drivers' final readback and Khronos logs,
and `tidy.log`. Diagnostic bundles and build outputs are local, not shipped.
