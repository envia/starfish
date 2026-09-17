#!/usr/bin/env python3
"""Observe the public TensorFlow.js toxicity demo in Starfish and compare it
with a fixed CPU reference.

One invocation validates one row of the matrix in docs/WebGL_TFJS_Plan.md
(backend x build type x GL environment) for the requested cases. The caller
provides the display: wrap software runs in
`xvfb-run -s '-screen 0 1920x1080x24' -a` with LIBGL_ALWAYS_SOFTWARE=1, and
hardware runs in the real X display (DISPLAY=:1 on the reference machine).

A run passes only when TensorFlow.js reports the `webgl` backend with the
requested WebGL version (or `cpu` for the CPU case), every decision matches
the reference, the maximum absolute probability error stays within the
reference tolerance, the renderer matches the requested GL environment and,
for hardware rows, the Starfish process shows up in `nvidia-smi` or its DRM
engine counters advance. Skipped checks are reported as such, never as passes.
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCE_PATH = HERE / "toxicity-reference.json"
PROBE_PATH = HERE / "toxicity-probe.js"
DEMO = "https://storage.googleapis.com/tfjs-models/demos/toxicity/index.html"
BACKENDS = ("uv_cairo_gl", "glib_cairo_gl")
BUILDS = ("debug", "release")
GL_ENVIRONMENTS = ("llvmpipe", "nvidia")
CASES = ("webgl1", "webgl2", "default", "cpu")
SOFTWARE_RENDERERS = ("llvmpipe", "softpipe", "swrast", "swiftshader",
                      "software", "lavapipe")
RECORDED_ENVIRONMENT = ("DISPLAY", "XAUTHORITY", "LIBGL_ALWAYS_SOFTWARE",
                        "LIBGL_ALWAYS_INDIRECT", "GALLIUM_DRIVER",
                        "MESA_LOADER_DRIVER_OVERRIDE", "LP_NUM_THREADS",
                        "__EGL_VENDOR_LIBRARY_FILENAMES", "EGL_PLATFORM",
                        "DRI_PRIME", "__NV_PRIME_RENDER_OFFLOAD",
                        "__GLX_VENDOR_LIBRARY_NAME")


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_reference():
    return json.loads(REFERENCE_PATH.read_text())


class DRMUsage:
    """Account each DRM client of the Starfish process once.

    Counter semantics: https://docs.kernel.org/gpu/drm-usage-stats.html
    These are whole-process counters, including presentation, not per-op
    timings. NVIDIA's proprietary driver does not export them, which is why
    `nvidia-smi` sampling exists alongside this.
    """

    def __init__(self):
        self.clients = {}
        self.samples = 0

    def sample(self, pid):
        self.samples += 1
        directory = Path(f"/proc/{pid}/fdinfo")
        try:
            files = list(directory.iterdir())
        except OSError:
            return
        for path in files:
            try:
                raw = path.read_text()
            except OSError:
                continue
            fields = {}
            for line in raw.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    fields[key] = value.strip()
            if "drm-client-id" not in fields:
                continue
            key = fields["drm-client-id"]
            counters = {name: int(value.split()[0]) for name, value in fields.items()
                        if name.startswith("drm-engine-") and value.endswith(" ns")}
            client = self.clients.setdefault(key, {
                "driver": fields.get("drm-driver"), "pdev": fields.get("drm-pdev"),
                "first_ns": counters.copy(), "max_ns": counters.copy()})
            for name, value in counters.items():
                # amdgpu omits engines whose accumulated usage is zero.
                client["first_ns"].setdefault(
                    name, 0 if client["driver"] == "amdgpu" else value)
                client["max_ns"][name] = max(value, client["max_ns"].get(name, value))

    def result(self):
        for client in self.clients.values():
            client["delta_ns"] = {name: value - client["first_ns"][name]
                                  for name, value in client["max_ns"].items()}
        return {"samples": self.samples, "clients": self.clients}

    def advanced(self):
        return any(any(delta > 0 for delta in client["delta_ns"].values())
                   for client in self.result()["clients"].values())


class NvidiaSmi:
    """Record the Starfish PID in `nvidia-smi` process listings."""

    def __init__(self):
        self.samples = 0
        self.entries = []
        self.available = None

    def sample(self, pid):
        self.samples += 1
        try:
            output = subprocess.run(["nvidia-smi"], capture_output=True, text=True,
                                    timeout=10).stdout
        except (OSError, subprocess.TimeoutExpired):
            self.available = False
            return
        self.available = True
        for line in output.splitlines():
            columns = line.split()
            if str(pid) in columns and line not in self.entries:
                self.entries.append(line)

    def result(self):
        return {"available": self.available, "samples": self.samples,
                "entries": self.entries}


def probe_commands(probe):
    # Native console commands have a 1023-byte limit. libuv coalesces pending
    # console callbacks while model inference blocks the loop, so run() waits
    # for each command's acknowledgement before sending the next one.
    commands = ["void(window.__toxicityProbeSource = '');"]
    for index in range(0, len(probe), 350):
        chunk = json.dumps(probe[index:index + 350])
        commands.append(f"void(window.__toxicityProbeSource += {chunk});")
    commands.append("eval(window.__toxicityProbeSource);")
    return commands


def run_starfish(binary, url, log_path, timeout, probe, inject_delay,
                 gpu_evidence, stop_on_backend=None):
    """Run one case. `stop_on_backend` names the TFJS backend whose
    appearance in TOXICITY_PROBE_READY ends the run early (a CPU fallback
    of a WebGL case is a definite failure and needs no 200 s inference)."""
    storage = log_path.with_suffix(".storage")
    started = time.monotonic()
    command = [str(binary), url, "--width=1280", "--height=900",
               f"--storage-dir={storage}", f"--timeout={timeout + 5}"]
    commands = probe_commands(probe)
    payload = None
    progress = []
    probe_ready = None
    assertion = None
    stopped_early = None
    fallback_warning = None
    drm = DRMUsage() if gpu_evidence else None
    smi = NvidiaSmi() if gpu_evidence == "nvidia" else None
    with log_path.open("w") as log:
        process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                                   stdout=log, stderr=subprocess.STDOUT,
                                   text=True, start_new_session=True)
        sent = 0
        acknowledged = -1
        position = 0
        pending = ""
        last_sample = 0.0
        try:
            while time.monotonic() - started < timeout:
                now = time.monotonic()
                if drm and now - last_sample >= 1.0:
                    drm.sample(process.pid)
                    if smi:
                        smi.sample(process.pid)
                    last_sample = now
                if (sent < len(commands) and acknowledged == sent - 1 and
                        now - started >= inject_delay and process.poll() is None):
                    script = commands[sent] + f"console.log('TOXICITY_INJECT_ACK {sent}');\n"
                    assert len(script.encode()) < 1024
                    process.stdin.write(script)
                    process.stdin.flush()
                    sent += 1
                with log_path.open(errors="replace") as reader:
                    reader.seek(position)
                    pending += reader.read()
                    position = reader.tell()
                    lines = pending.split("\n")
                    pending = lines.pop()
                    for line in lines:
                        if "console.log: TOXICITY_INJECT_ACK " in line:
                            acknowledged = int(line.rsplit(" ", 1)[1])
                        elif "console.log: TOXICITY_PROGRESS " in line:
                            progress.append(json.loads(line.split("TOXICITY_PROGRESS ", 1)[1]))
                        elif "console.log: TOXICITY_RESULT " in line:
                            payload = json.loads(line.split("TOXICITY_RESULT ", 1)[1])
                        elif "console.log: TOXICITY_PROBE_READY " in line:
                            probe_ready = json.loads(line.split("TOXICITY_PROBE_READY ", 1)[1])
                        elif "Assertion" in line and assertion is None:
                            assertion = line.strip()
                        elif ("Initialization of backend webgl failed" in line and
                              fallback_warning is None):
                            # TFJS logs this before it falls back to the CPU
                            # backend and starts a 200 s CPU inference.
                            fallback_warning = line.split("console.warn: ", 1)[-1].strip()
                if stop_on_backend == "cpu" and fallback_warning:
                    stopped_early = "TFJS reported: " + fallback_warning
                    break
                if (stop_on_backend and probe_ready and
                        probe_ready.get("backend") == stop_on_backend):
                    stopped_early = f"TFJS selected the {stop_on_backend} backend"
                    break
                if payload is not None or process.poll() is not None:
                    break
                time.sleep(0.1)
        finally:
            if drm:
                drm.sample(process.pid)
            if smi:
                smi.sample(process.pid)
            exit_before_cleanup = process.poll()
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            process.stdin.close()
    return {
        "payload": payload, "progress": progress, "probe_ready": probe_ready,
        "assertion": assertion, "stopped_early": stopped_early,
        "fallback_warning": fallback_warning,
        "seconds": round(time.monotonic() - started, 3), "command": command,
        "exit_code_before_cleanup": exit_before_cleanup,
        "exit_code": process.returncode,
        "probe_commands_sent": sent, "probe_commands_total": len(commands),
        "timed_out": (payload is None and exit_before_cleanup is None and
                      stopped_early is None),
        "drm": drm.result() if drm else None,
        "drm_advanced": drm.advanced() if drm else None,
        "nvidia_smi": smi.result() if smi else None,
    }


def is_software_renderer(renderer):
    return bool(renderer) and any(name in renderer.lower() for name in SOFTWARE_RENDERERS)


def evaluate(case, payload, reference, gl_environment, hardware):
    """Return (pass, reasons, summary). Every failed check adds a reason."""
    reasons = []
    summary = {"decisions": 0, "max_probability_error": None,
               "renderer": None, "backend": None, "webgl_version": None}
    if not payload:
        return False, ["no TOXICITY_RESULT payload"], summary

    if payload.get("error"):
        reasons.append("probe error: " + str(payload["error"]))
    if payload.get("rows") != 5:
        reasons.append(f"table rows {payload.get('rows')} != 5")
    records = payload.get("classifications", [])
    if len(records) != 2:
        reasons.append(f"{len(records)} classifications != 2")
    expected_version = {"webgl1": 1, "webgl2": 2, "cpu": 0}.get(case)
    for record in records:
        summary["renderer"] = record.get("renderer")
        summary["backend"] = record.get("backend")
        summary["webgl_version"] = record.get("webglVersion")
        if case == "cpu":
            if record.get("backend") != "cpu":
                reasons.append(f"backend {record.get('backend')} != cpu")
            if record.get("hasWebGLContext"):
                reasons.append("CPU case created a WebGL context")
        else:
            if record.get("backend") != "webgl":
                reasons.append(f"backend {record.get('backend')} != webgl (CPU fallback)")
            if expected_version is not None and record.get("webglVersion") != expected_version:
                reasons.append(f"WEBGL_VERSION {record.get('webglVersion')} != {expected_version}")
            if not record.get("drawCount"):
                reasons.append("no drawElements observed during classify")
            if record.get("glError") not in (0, None):
                reasons.append(f"GL error 0x{record.get('glError'):04x} after classify")
            if not record.get("floatRendering"):
                reasons.append("WEBGL_RENDER_FLOAT32_ENABLED is false")
            if not record.get("floatDownload"):
                reasons.append("WEBGL_DOWNLOAD_FLOAT_ENABLED is false")
            if record.get("webglVersion") == 2 and not record.get("bufferSupported"):
                reasons.append("WEBGL_BUFFER_SUPPORTED is false on WebGL2")
            renderer = record.get("renderer")
            if gl_environment == "llvmpipe" and not is_software_renderer(renderer):
                reasons.append(f"renderer {renderer!r} is not a software renderer")
            if gl_environment == "nvidia" and (
                    is_software_renderer(renderer) or not renderer or
                    "nvidia" not in renderer.lower()):
                reasons.append(f"renderer {renderer!r} is not the NVIDIA GPU")
        if len(record.get("predictions", [])) != 7:
            reasons.append(f"{len(record.get('predictions', []))} label heads != 7")
    differences = []
    for record in records:
        for head in record.get("predictions", []):
            expected_head = next((h for h in reference["predictions"]
                                  if h["label"] == head["label"]), None)
            if expected_head is None:
                reasons.append(f"unknown label {head['label']}")
                continue
            for text, item in zip(record["inputs"], head["results"]):
                if text not in reference["inputs"]:
                    reasons.append(f"input not in reference: {text!r}")
                    continue
                expected = expected_head["results"][reference["inputs"].index(text)]
                probabilities = item.get("probabilities", [])
                if (len(probabilities) != 2 or
                        not all(isinstance(v, (int, float)) and v == v and
                                abs(v) != float("inf") for v in probabilities)):
                    reasons.append(f"{head['label']}: malformed probabilities {probabilities}")
                    continue
                if abs(sum(probabilities) - 1) > 2 * reference["tolerance"]:
                    reasons.append(f"{head['label']}: probabilities do not sum to 1")
                summary["decisions"] += 1
                if item.get("match") != expected["match"]:
                    reasons.append(f"{head['label']} / {text[:30]!r}: match "
                                   f"{item.get('match')} != {expected['match']}")
                differences.extend(abs(a - b) for a, b in
                                   zip(probabilities, expected["probabilities"]))
    if differences:
        summary["max_probability_error"] = max(differences)
        if max(differences) > reference["tolerance"]:
            reasons.append(f"max probability error {max(differences)} > "
                           f"{reference['tolerance']}")
    if records:
        expected_table = [[str(head["results"][row]["match"]).lower()
                           if head["results"][row]["match"] is not None else "null"
                           for head in records[0]["predictions"]] for row in range(3)]
        if payload.get("initialTable") != expected_table:
            reasons.append("rendered initial table differs from classification results")
    matmul = payload.get("matmul") or {}
    summary["matmul"] = matmul
    if case != "cpu":
        if matmul.get("skipped") or matmul.get("error"):
            reasons.append("matmul check did not run: " +
                           str(matmul.get("skipped") or matmul.get("error")))
        else:
            if not matmul.get("cpuForwardDisabled"):
                reasons.append("WEBGL_CPU_FORWARD could not be disabled")
            if not (matmul.get("float32") or {}).get("pass"):
                reasons.append("float32 matmul on the GL path failed")
            half = matmul.get("halfFloat") or {}
            if half.get("renderFloat32") is not False:
                summary["half_float_matmul"] = "not applicable: flag change did not take effect"
            elif not half.get("pass"):
                reasons.append("half-float matmul on the GL path failed")
    if hardware and case != "cpu":
        if not hardware.get("evidence"):
            reasons.append("no hardware evidence (nvidia-smi entry or DRM counters)")
    return not reasons, reasons, summary


def verify_assets(reference):
    results = []
    for item in reference.get("downloads", []):
        entry = {"url": item["url"], "expected_sha256": item["sha256"]}
        try:
            with urllib.request.urlopen(item["url"], timeout=60) as response:
                data = response.read()
            entry["sha256"] = hashlib.sha256(data).hexdigest()
            entry["bytes"] = len(data)
            entry["match"] = entry["sha256"] == item["sha256"]
        except OSError as error:
            entry["error"] = str(error)
            entry["match"] = False
        results.append(entry)
    return results


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--backend", choices=BACKENDS, required=True)
    parser.add_argument("--build", choices=BUILDS, required=True)
    parser.add_argument("--gl", choices=GL_ENVIRONMENTS, required=True,
                        help="GL environment the caller prepared; checked against gl.RENDERER")
    parser.add_argument("--binary", type=Path,
                        help="Starfish binary (default out/<backend>-<build>/bin/lightweight-web-engine)")
    parser.add_argument("--case", nargs="+", choices=CASES,
                        default=["webgl1", "webgl2", "default"])
    parser.add_argument("--timeout", type=int, default=300,
                        help="seconds per case (CPU case uses --cpu-timeout)")
    parser.add_argument("--cpu-timeout", type=int, default=900)
    parser.add_argument("--inject-delay", type=float, default=3.0,
                        help="seconds before the first console command; Release needs about 3")
    parser.add_argument("--verify-assets", action="store_true",
                        help="download every referenced asset and compare its SHA-256")
    parser.add_argument("--output", type=Path, required=True,
                        help="new directory for logs and results")
    args = parser.parse_args()

    if not os.environ.get("DISPLAY"):
        parser.error("DISPLAY is required; use xvfb-run or a real display")
    binary = args.binary or ROOT / "out" / f"{args.backend}-{args.build}" / "bin" / "lightweight-web-engine"
    binary = binary.resolve()
    if not binary.is_file():
        parser.error(f"binary not found: {binary}")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)

    reference = load_reference()
    probe = PROBE_PATH.read_text()
    label = f"{args.backend}-{args.build}-{args.gl}"
    metadata = {
        "label": label, "backend": args.backend, "build": args.build, "gl": args.gl,
        "started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "engine_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "engine_dirty_files": subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=ROOT, text=True).splitlines(),
        "binary": str(binary), "binary_sha256": sha256_file(binary),
        "tool_sha256": {p.name: sha256_file(p) for p in HERE.iterdir() if p.is_file()},
        "reference": {"tfjs": reference.get("tfjs"), "tolerance": reference.get("tolerance"),
                      "inputs": reference.get("inputs"),
                      "bundle_sha256": reference.get("bundle_sha256")},
        "host": {"platform": platform.platform(), "architecture": platform.machine(),
                 "logical_cpus": os.cpu_count()},
        "environment": {name: os.environ.get(name) for name in RECORDED_ENVIRONMENT},
        "complete": False,
    }
    if args.gl == "nvidia":
        try:
            metadata["nvidia_smi"] = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.TimeoutExpired) as error:
            metadata["nvidia_smi"] = f"unavailable: {error}"
    if args.verify_assets:
        metadata["assets"] = verify_assets(reference)
        metadata["assets_match"] = all(item["match"] for item in metadata["assets"])
        print(f"assets: {'MATCH' if metadata['assets_match'] else 'MISMATCH'} "
              f"({len(metadata['assets'])} files)", flush=True)
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    results = []
    for case in args.case:
        version = {"cpu": 0, "webgl1": 1, "webgl2": 2}.get(case)
        url = DEMO if case == "default" else DEMO + f"?tfjsflags=WEBGL_VERSION:{version}"
        timeout = args.cpu_timeout if case == "cpu" else args.timeout
        log_path = args.output / f"{label}-{case}.log"
        gpu_evidence = None if case == "cpu" else args.gl
        run = run_starfish(binary, url, log_path, timeout, probe, args.inject_delay,
                           gpu_evidence,
                           stop_on_backend="cpu" if case != "cpu" else None)
        hardware = None
        if args.gl == "nvidia" and case != "cpu":
            hardware = {"nvidia_smi_entries": run["nvidia_smi"]["entries"],
                        "drm_advanced": run["drm_advanced"]}
            hardware["evidence"] = bool(hardware["nvidia_smi_entries"]) or bool(run["drm_advanced"])
        passed, reasons, summary = evaluate(case, run["payload"], reference, args.gl, hardware)
        if run["exit_code_before_cleanup"] not in (None, 0):
            reasons.append(f"Starfish exited with {run['exit_code_before_cleanup']}")
            passed = False
        if run["timed_out"]:
            reasons.append("timed out before TOXICITY_RESULT")
            passed = False
        if run["stopped_early"]:
            reasons.append(run["stopped_early"] + " (stopped early)")
            passed = False
        if run["assertion"]:
            reasons.append(run["assertion"])
            passed = False
        if run["probe_ready"] and not summary.get("backend"):
            summary["backend"] = run["probe_ready"].get("backend")
            summary["backend_source"] = "TOXICITY_PROBE_READY"
        if args.verify_assets and not metadata["assets_match"]:
            reasons.append("reference assets changed upstream; reference is not comparable")
            passed = False
        result = {"case": case, "url": url, "pass": passed, "reasons": reasons,
                  "summary": summary, "hardware": hardware, "log": log_path.name}
        result.update({key: run[key] for key in (
            "seconds", "command", "exit_code", "exit_code_before_cleanup",
            "probe_commands_sent", "probe_commands_total", "timed_out",
            "stopped_early", "assertion", "probe_ready", "fallback_warning",
            "drm", "nvidia_smi", "payload", "progress")})
        results.append(result)
        (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        error = summary.get("max_probability_error")
        print(f"{label} {case}: {'PASS' if passed else 'FAIL'} "
              f"backend={summary.get('backend')} version={summary.get('webgl_version')} "
              f"renderer={summary.get('renderer')!r} decisions={summary.get('decisions')} "
              f"max_error={error if error is None else f'{error:.3g}'} "
              f"({run['seconds']}s)", flush=True)
        for reason in reasons:
            print(f"  - {reason}", flush=True)
    metadata["complete"] = True
    metadata["finished"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return 0 if all(result["pass"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
