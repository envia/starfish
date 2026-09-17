# TensorFlow.js toxicity validation tool

Working-branch tool for `docs/WebGL_TFJS_Plan.md`. It is kept on the
`indigo/2025/webgl2/0375` and `0376` branches and is not part of the
integration branch `0377`.

`run.py` launches Starfish on the unmodified public demo
(https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html),
injects `toxicity-probe.js` through the console (stdin), waits for the demo's
own three classifications plus one typed input, and compares the 28 decisions
and 56 probabilities with `toxicity-reference.json`. The reference was
computed with the TFJS 1.2.2 CPU backend of the same bundle; its `downloads`
list holds the URL, size and SHA-256 of every asset the demo loads, so a
changed bundle or model behind the same URL is detected with
`--verify-assets`.

One invocation covers one matrix row. The caller prepares the GL environment;
the tool checks `gl.RENDERER` against `--gl` and, for `--gl nvidia`, requires
the Starfish PID in `nvidia-smi` or advancing DRM engine counters.

## Cases

| `--case` | URL flag | Passes when |
|---|---|---|
| `webgl1` | `?tfjsflags=WEBGL_VERSION:1` | backend `webgl`, `WEBGL_VERSION` 1 |
| `webgl2` | `?tfjsflags=WEBGL_VERSION:2` | backend `webgl`, `WEBGL_VERSION` 2, `WEBGL_BUFFER_SUPPORTED` |
| `default` | none (page's own selection) | backend `webgl`, version recorded |
| `cpu` | `?tfjsflags=WEBGL_VERSION:0` | backend `cpu`, no WebGL context |

Every non-CPU case additionally requires `WEBGL_RENDER_FLOAT32_ENABLED` and
`WEBGL_DOWNLOAD_FLOAT_ENABLED`, at least one `drawElements` during
`classify`, no GL error, and a small float32 `matMul` with
`WEBGL_CPU_FORWARD=false`. A half-float `matMul` is attempted by clearing
`WEBGL_RENDER_FLOAT32_ENABLED`; if TFJS ignores the late flag change the
result is reported as not applicable, not as a pass.

## Usage

Software GL (Mesa llvmpipe) under Xvfb, Debug `uv_cairo_gl` build:

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=4 \
  ./tool/tfjs_toxicity/run.py --backend uv_cairo_gl --build debug --gl llvmpipe \
  --binary out/webgl2/bin/lightweight-web-engine --verify-assets \
  --output out/tfjs-toxicity/uv-debug-llvmpipe
```

Hardware GL on the real X server (reference machine: `DISPLAY=:1`, NVIDIA):

```sh
DISPLAY=:1 ./tool/tfjs_toxicity/run.py --backend uv_cairo_gl --build debug --gl nvidia \
  --binary out/webgl2/bin/lightweight-web-engine \
  --output out/tfjs-toxicity/uv-debug-nvidia
```

Without `--binary` the tool expects `out/<backend>-<build>/bin/lightweight-web-engine`.
Add `--case cpu` for the CPU reference re-derivation (about 210 s on a Debug
build; `--cpu-timeout` defaults to 900 s). Release builds need the default
`--inject-delay 3`; Debug builds accept smaller values.

## Output

`--output` must not exist. It receives:

- `metadata.json`: engine commit and dirty files, binary SHA-256, tool file
  SHA-256s, recorded environment variables, `nvidia-smi` name and driver,
  asset verification.
- `<label>-<case>.log`: Starfish stdout/stderr including the probe lines
  `TOXICITY_PROBE_READY`, `TOXICITY_PROGRESS`, `TOXICITY_RESULT`.
- `results.json`: per case `pass`, the list of failed checks in `reasons`,
  a `summary` (backend, version, renderer, decisions compared, maximum
  probability error, matmul), hardware evidence and the raw payload.

A WebGL case ends early when TFJS logs "Initialization of backend webgl
failed" or the probe reports the `cpu` backend, and the reason is recorded;
a Starfish assertion message is copied into `reasons` as well.

The exit status is 0 only when every case passed.

## Regenerating the reference

`reference.cjs` recomputes the CPU reference with Node.js 18+ by running the
demo bundle's model code outside a browser:

```sh
node tool/tfjs_toxicity/reference.cjs tool/tfjs_toxicity/toxicity-reference.json
```

It refuses to run when the bundle's SHA-256 changed; review the new TFJS and
model versions first. The plan's step 0 also re-derives the reference with
Starfish itself (`--case cpu`) and compares both.
