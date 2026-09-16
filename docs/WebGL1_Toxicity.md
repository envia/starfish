# TensorFlow.js toxicity on WebGL1

Build with `-DWEBGL=1` (the optional feature remains disabled by default).
The demo normally tries WebGL2 first. Select WebGL1 using TensorFlow.js's
existing URL flag:

```sh
./Starfish 'https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html?tfjsflags=WEBGL_VERSION:1'
```

This change fixes ArrayBufferView and null texture uploads: float component
sizes, HALF_FLOAT_OES support and input types, zero initialization, and
preservation of float formats in the BGRA path. On drivers advertising native
`GL_EXT_color_buffer_float`, WebGL1 RGB/RGBA float textures use ES3 sized
storage and half-float uploads use the native ES3 type. The native capability
does not expose the WebGL2-only `EXT_color_buffer_float` extension to WebGL1.

## Validation (2026-09-16)

Current Debug build, uv_cairo_gl/x11, Xvfb, Mesa llvmpipe, two rasterizer
threads. CPU inference was checked before changing engine source.

| Check | Result |
| --- | --- |
| CPU, original demo's three inputs | 7 labels / 21 decisions, passed |
| WebGL1, same inputs | All 21 decisions match CPU |
| Maximum absolute difference, 42 probabilities | 1.7881393432617188e-7 |
| Model load + inference elapsed | CPU 350885 ms; WebGL1 18871 ms |
| Original hosted demo with WebGL1 flag | Initial table and additional input passed |
| TFJS matrix multiplication, CPU forwarding disabled | Float32 and half-float passed (tolerance 1e-5) |
| Existing Canvas regressions | 18 / 18 passed |
| New float/half-float upload and render-target regression | Passed |
| WebGL C++ tidy check | 37 files, zero errors |

The timings include model loading, differing cache state and concurrent
diagnostics; they are not a controlled benchmark. `gl.RENDERER` reported
`llvmpipe (LLVM 20.1.2, 256 bits)`. Thus these results verify the WebGL1 shader
backend, **not physical GPU acceleration**. The host NVIDIA driver/library
version mismatch prevented physical GPU validation. Driver repair was not
part of this source change. GLES2-only model accuracy and general WebGL
conformance are not established by these checks.

Regression coverage is registered in `tool/reftest/cairo/internal.res`:

- `test/cairo/internal-test/canvas/webgl-float-texture-upload.html`
- `test/cairo/internal-test/canvas/webgl1-float-render-target.html`

The `test` directory is a separate Git submodule; include its test files when
carrying this change to another checkout. The first regression file already
existed as an untracked diagnostic in this checkout and was left unchanged.

The preserved local diagnostic bundle in `webgl-toxicity-2026-09-15/` was
used without modifications. To repeat the numerical comparison from this
checkout, run its `webgl1/model.html#cpu` and then
`webgl1/model.html?tfjsflags=WEBGL_VERSION:1` as absolute `file://` URLs:

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env LP_NUM_THREADS=2 \
  ./Starfish 'file:///ABSOLUTE/CHECKOUT/webgl-toxicity-2026-09-15/webgl1/model.html#cpu' \
  --hide-window --disable-console --timeout=900
```

Compare the `MODEL_RESULT` JSON arrays by label, match and probability.
Do not treat a successful process exit alone as evidence of correct output.

Raw logs for this session are `/tmp/starfish-codex-toxicity-cpu.log`,
`/tmp/starfish-codex-toxicity-webgl1.log`,
`/tmp/starfish-codex-live-demo.log`, `/tmp/starfish-codex-canvas.log`,
`/tmp/starfish-codex-float-target.log` and `/tmp/starfish-codex-tidy.log`.

## Physical GPU revalidation after reboot (2026-09-16)

The driver/library mismatch was resolved by rebooting. With the same engine
build, the hosted demo reported `NVIDIA GeForce RTX 3050 OEM/PCIe/SSE2`,
vendor `NVIDIA Corporation`, TFJS backend `webgl`, `WEBGL_VERSION=1` and
`WEBGL_RENDER_FLOAT32_ENABLED=true`. NVIDIA driver version is `595.91.07`.
`nvidia-smi` also showed the Starfish graphics process with 154 MiB of GPU
memory. No additional engine changes were needed.

The hosted demo's initial three inputs and an additional input passed.
Float32 and half-float matrix tests passed with CPU forwarding disabled;
float/half-float render-target regression and all 18 Canvas regressions passed.
The full three-input model run took 22235 ms including model loading (1391 ms).
These diagnostic timings are not a controlled benchmark.

Xvfb's X11 platform could not initialize NVIDIA EGL. For the hardware checks,
the test wrapper used the existing NVIDIA X11 display with hidden windows:

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env \
  DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority \
  __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json \
  ./Starfish 'https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html?tfjsflags=WEBGL_VERSION:1' \
  --hide-window --timeout=600
```

The display and authority paths above are specific to this login session.
Logs are preserved in `out/gpu-validation-20260916/`: `live-nvidia.log`,
`model-nvidia.log`, `matrix-nvidia.log`, `matrix-half-nvidia.log`,
`render-target-nvidia.log`, `canvas-nvidia.log`, `nvidia-smi.txt` and `cpu.log`.
The earlier `/tmp/` logs were lost on reboot, so CPU inference was rerun.
All 21 classification decisions match the NVIDIA WebGL1 results. Across all
42 probabilities, the maximum absolute error is `5.960464477539063e-8`.
The CPU run completed in 211868 ms including model loading; both model runs
passed finite-value and probability-normalization checks.
