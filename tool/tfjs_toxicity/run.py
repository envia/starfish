#!/usr/bin/env python3
"""Observe the hosted toxicity demo without changing its backend selection.

Derived from github/envia/2026/devel/0730: 02094e8638, ca3fb940ee,
7818039497. Run under xvfb-run; hardware runs also select the real display.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOFTWARE = ("llvmpipe", "softpipe", "software", "swiftshader", "swrast")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def check_assets(reference):
    """Fail closed on changed assets; never silently bless new model data."""
    records = []
    for asset in reference["downloads"]:
        digest = hashlib.sha256()
        size = 0
        with urllib.request.urlopen(asset["url"], timeout=60) as response:
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                size += len(chunk)
                digest.update(chunk)
        actual = {"url": asset["url"], "bytes": size,
                  "sha256": digest.hexdigest()}
        if actual != asset:
            raise ValueError("Asset drift: " + asset["url"])
        records.append(actual)
    return records


def commands(probe):
    # Console.cpp reads 1023 bytes; await each acknowledgement because libuv
    # coalesces console callbacks while inference blocks the event loop.
    result = ["void(window.__toxicityProbeSource = '');"]
    for start in range(0, len(probe), 350):
        result.append("void(window.__toxicityProbeSource += " +
                      json.dumps(probe[start:start + 350]) + ");")
    result.append("eval(window.__toxicityProbeSource);")
    return result


def run(binary, url, output, timeout, gpu):
    started = time.monotonic()
    command = [str(binary), url, "--width=1280", "--height=900",
               "--storage-dir=" + str(output.with_suffix(".storage")),
               "--timeout=" + str(timeout + 10)]
    injection = commands((HERE / "toxicity-probe.js").read_text())
    result = {"command": command, "payload": None, "gpu_process_samples": []}
    sent, ack, position = 0, -1, 0
    pending = ""
    next_gpu_sample = 0
    with output.open("w") as log:
        process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE,
                                   stdout=log, stderr=subprocess.STDOUT,
                                   text=True, start_new_session=True)
        result["pid"] = process.pid
        try:
            while time.monotonic() - started < timeout:
                if gpu and time.monotonic() >= next_gpu_sample:
                    sample = subprocess.run(["nvidia-smi"], capture_output=True,
                                            text=True, timeout=10)
                    matching = [line for line in sample.stdout.splitlines()
                                if re.search(r"\b" + str(process.pid) + r"\s+[CG]+\s", line)]
                    if matching and not result["gpu_process_samples"]:
                        result["gpu_process_samples"].append(sample.stdout)
                    next_gpu_sample = time.monotonic() + 2
                if (sent < len(injection) and ack == sent - 1 and
                        time.monotonic() - started >= 1 and process.poll() is None):
                    script = injection[sent] + f"console.log('TOXICITY_INJECT_ACK {sent}');\n"
                    if len(script.encode()) >= 1024:
                        raise ValueError("Console chunk exceeds native buffer")
                    process.stdin.write(script)
                    process.stdin.flush()
                    sent += 1
                with output.open(errors="replace") as reader:
                    reader.seek(position)
                    pending += reader.read()
                    position = reader.tell()
                lines = pending.split("\n")
                pending = lines.pop()
                for line in lines:
                    if "console.log: TOXICITY_INJECT_ACK " in line:
                        ack = int(line.rsplit(" ", 1)[1])
                    if "console.log: TOXICITY_RESULT " in line:
                        result["payload"] = json.loads(line.split("TOXICITY_RESULT ", 1)[1])
                if result["payload"] is not None or process.poll() is not None:
                    break
                time.sleep(0.1)
        finally:
            result["exit_before_cleanup"] = process.poll()
            result["timed_out"] = result["payload"] is None and process.poll() is None
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            process.stdin.close()
    result.update(seconds=round(time.monotonic() - started, 3),
                  probe_commands_sent=sent, probe_commands_total=len(injection))
    return result


def validate(payload, reference, case, gl_environment, gpu_samples):
    """Return explicit failures, including missing, duplicate and nonfinite data."""
    failures, differences = [], []
    if not payload or payload.get("error"):
        return ["No successful completion: " + str(payload)], None
    records = payload.get("classifications", [])
    if len(records) != 2 or payload.get("rows") != 5:
        return ["Expected initial and submitted classifications, and five table rows"], None
    version = {"cpu": 0, "webgl1": 1, "webgl2": 2, "default": 2}[case]
    labels = [head["label"] for head in reference["predictions"]]
    for record, inputs in zip(records, (reference["inputs"][:3], reference["inputs"][3:])):
        if record.get("inputs") != inputs:
            failures.append("Input mismatch")
            continue
        if record.get("tfjs") != reference["tfjs"] or record.get("threshold") != reference["threshold"]:
            failures.append("TFJS version or threshold mismatch")
        if record.get("backend") != ("cpu" if case == "cpu" else "webgl"):
            failures.append("Backend mismatch / CPU fallback")
        if record.get("webglVersion") != version:
            failures.append("WebGL version mismatch")
        if case != "cpu":
            if not record.get("hasWebGLContext") or not record.get("drawCount", 0):
                failures.append("No WebGL draws")
            if record.get("glError") != 0 or not record.get("floatRendering"):
                failures.append("GL error or float rendering disabled")
            if version == 2 and not record.get("bufferSupported"):
                failures.append("WebGL2 buffer download disabled")
            renderer = record.get("renderer") or ""
            software = any(name in renderer.lower() for name in SOFTWARE)
            if not renderer or software != (gl_environment == "software"):
                failures.append("Renderer does not match requested GL environment")
            if gl_environment == "gpu" and not gpu_samples:
                failures.append("No nvidia-smi entry for the Starfish PID")
        heads = record.get("predictions", [])
        if [head.get("label") for head in heads] != labels:
            failures.append("Label count/order mismatch")
            continue
        for head, expected_head in zip(heads, reference["predictions"]):
            results = head.get("results", [])
            if len(results) != len(inputs):
                failures.append("Result shape mismatch")
                continue
            for text, item in zip(inputs, results):
                expected = expected_head["results"][reference["inputs"].index(text)]
                if item.get("match") is not expected["match"]:
                    failures.append("Decision mismatch")
                values = item.get("probabilities", [])
                if (len(values) != 2 or any(type(v) not in (int, float) or
                        not math.isfinite(v) or not 0 <= v <= 1 for v in values)):
                    failures.append("Invalid probability values/shape")
                    continue
                differences.extend(abs(a - b) for a, b in zip(values, expected["probabilities"]))
    expected_table = [[str(head["results"][row]["match"]).lower()
                       for head in reference["predictions"]] for row in range(3)]
    if payload.get("initialTable") != expected_table:
        failures.append("Rendered initial table mismatch")
    error = max(differences) if differences else None
    if error is None or error > reference["tolerance"]:
        failures.append("Probability error exceeds tolerance or no probabilities")
    return sorted(set(failures)), error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("uv_cairo_gl", "glib_cairo_gl"), required=True)
    parser.add_argument("--build-type", choices=("Debug", "Release"), required=True)
    parser.add_argument("--gl", choices=("software", "gpu"), required=True)
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--case", choices=("cpu", "webgl1", "webgl2", "default"), required=True)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    binary = build / "bin/lightweight-web-engine"
    cache = (build / "CMakeCache.txt").read_text()
    source_match = re.search(r"^CMAKE_HOME_DIRECTORY:INTERNAL=(.+)$", cache, re.M)
    if not source_match:
        parser.error("Missing CMake source directory")
    engine_root = Path(source_match.group(1))
    for key, value in (("BACKEND", args.backend), ("CMAKE_BUILD_TYPE", args.build_type)):
        if not re.search(r"^" + key + r":[^=]+=" + re.escape(value) + r"$", cache, re.M):
            parser.error("Build configuration mismatch: " + key)
    if not os.environ.get("DISPLAY") or args.timeout <= 0:
        parser.error("DISPLAY and a positive timeout are required")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    reference = json.loads((HERE / "toxicity-reference.json").read_text())
    metadata = {"started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "engine_revision": git("rev-parse", "HEAD", cwd=engine_root),
                "engine_source": str(engine_root),
                "tool_revision": git("log", "-1", "--format=%H", "--", str(HERE)),
                "tracked_status": git("status", "--short", "--untracked-files=no", cwd=engine_root),
                "arguments": {k: str(v) for k, v in vars(args).items()},
                "binary_sha256": sha256(binary), "cmake_cache_sha256": sha256(build / "CMakeCache.txt"),
                "shared_library_sha256": {p.name: sha256(p) for p in (build / "lib").glob("*.so*")
                                          if p.is_file() and not p.is_symlink()},
                "tool_sha256": {p.name: sha256(p) for p in HERE.iterdir() if p.is_file()},
                "environment": {k: os.environ.get(k) for k in (
                    "DISPLAY", "LIBGL_ALWAYS_SOFTWARE", "__EGL_VENDOR_LIBRARY_FILENAMES")},
                "complete": False}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    try:
        metadata["assets"] = check_assets(reference)
        version = {"cpu": 0, "webgl1": 1, "webgl2": 2}.get(args.case)
        url = reference["demo_url"] + ("" if version is None else f"?tfjsflags=WEBGL_VERSION:{version}")
        result = run(binary, url, output / "starfish.log", args.timeout, args.gl == "gpu")
        failures, error = validate(result["payload"], reference, args.case,
                                   args.gl, result["gpu_process_samples"])
        if result["exit_before_cleanup"] not in (None, 0):
            failures.append("Starfish exited abnormally")
        result.update(failures=failures, max_probability_error=error, passed=not failures)
        (output / "result.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        metadata["complete"] = True
        print(json.dumps({"case": args.case, "passed": not failures,
                          "seconds": result["seconds"], "failures": failures,
                          "max_probability_error": error}), flush=True)
        return 1 if failures else 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        metadata["error"] = str(error)
        print(str(error), flush=True)
        return 1
    finally:
        (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
