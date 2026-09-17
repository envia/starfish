# Toxicity validation

Working-branch tooling; do not carry this directory into `0377`.
Adapted from `github/envia/2026/devel/0730` commits `02094e8638`,
`ca3fb940ee`, `7818039497`. Python uses only the standard library.

Build Starfish before running. The runner verifies backend/build type against
the selected CMake cache. It checks every pinned asset's SHA-256 before
opening the original hosted page, injects an observer through the shell
console, and compares both model output and the rendered initial table.
The observer may replay the initial inputs if they completed before injection;
it records this in the console log and still exercises the page's input handler.
It never changes the selected backend or suppresses engine errors.

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env \
  LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=4 \
  python3 tool/tfjs_toxicity/run.py --backend uv_cairo_gl \
  --build-type Debug --gl software --build-dir out/webgl2 \
  --case cpu --timeout 900 --output out/tfjs-baseline/cpu
```

Use `--case webgl1`, `webgl2`, or `default` for the forced versions and
unmodified page selection. Each run needs a new output directory. All four
backend/build combinations use the same arguments with their own build dir.

For NVIDIA, run outside the sandbox on the host's accessible display:

```sh
xvfb-run -s '-screen 0 1920x1080x24' -a env \
  DISPLAY=:1 __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json \
  python3 tool/tfjs_toxicity/run.py --backend uv_cairo_gl \
  --build-type Debug --gl gpu --build-dir out/webgl2 \
  --case webgl1 --timeout 600 --output out/tfjs-baseline/gpu-webgl1
```

Do not set `LIBGL_ALWAYS_SOFTWARE` for the GPU run. Hardware validation
requires Starfish's own renderer and its PID in `nvidia-smi`; process presence
does not measure individual tensor kernels. Draw counts additionally verify
that the observed classification exercised WebGL. Software mode rejects a
hardware renderer. CPU runs validate the numerical reference, not GL use.

TFJS 1.2.2, threshold 0.85, four fixed inputs and seven labels must match the
reference. The pinned demo calls `load()` without a threshold and its model
constructor defaults to 0.85 (the initial plan's 0.9 was incorrect).
All 28 decisions must match and maximum probability absolute error
must be at most 1e-3. Missing/duplicate labels, wrong shapes, nonfinite values,
wrong backend/version, CPU fallback, GL errors or timeouts fail closed.
WebGL2 also requires `WEBGL_BUFFER_SUPPORTED`. A reference mismatch must be
investigated; do not regenerate it merely to make validation pass.

Outputs: `metadata.json` (revision, cache/binary/tool hashes, pinned assets,
environment), `starfish.log` (full observations), `result.json` (predictions,
renderer, GPU evidence, comparison failures and time). Baseline GPU runs may
fail until the engine implementation is complete; their failure is evidence,
not an invitation to weaken the checker. Check `metadata.complete` as well as
the process exit status. A nonzero exit or missing result is not a pass.

Asset checking is a preflight against the hosted resources, not an intercept
of browser requests. If the host changes assets during a run, repeat with a
reviewed stable asset set. Frozen offline replay and small matrix checks will
be added alongside float support; they are not implemented by this first step.

The CPU run records recomputed probabilities in `result.json`; compare them
with the checked-in reference before changing engine code. Source attribution
and host model hashes are kept in `toxicity-reference.json`.
