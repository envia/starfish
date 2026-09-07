"""Interface/Protocol candidate scanner — evidence pipeline implementation.

The scanner is deliberately staged:

1. collect source evidence/endpoints/constants
2. apply framework-specific annotations as endpoint records
3. pair endpoints globally by normalized channel/topic/action
4. build final ``InterfaceCandidate`` objects

Framework-specific logic should not be the source of truth by itself; it annotates
raw source evidence so the builder can produce confidence-aware candidates.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .evidence import ConstantRecord, EndpointRecord
from .schema import (
    CandidateCollection,
    Confidence,
    Evidence,
    EvidenceStrength,
    EvidenceType,
    Family,
    InterfaceCandidate,
    MessageKind,
    Origin,
    Participant,
    ParticipantRole,
    Promotion,
    Verification,
    compute_candidate_id,
    sort_candidates,
)

# ── Known framework patterns ──────────────────────────────────────────────────

KNOWN_IMPORTS: dict[str, dict[str, Any]] = {
    "electron": {
        "framework": "electron",
        "platform": "node",
        "apis": {
            "ipcRenderer.invoke": "ipcRenderer.invoke/ipcMain.handle",
            "ipcRenderer.send": "ipcRenderer.send/ipcMain.on",
            "ipcRenderer.sendSync": "ipcRenderer.sendSync/ipcMain.on",
            "ipcMain.handle": "ipcRenderer.invoke/ipcMain.handle",
            "ipcMain.on": "ipcRenderer.send/ipcMain.on",
        },
        "direction_map": {
            "ipcRenderer.invoke": "renderer_to_main",
            "ipcRenderer.send": "renderer_to_main",
            "ipcRenderer.sendSync": "renderer_to_main",
            "ipcMain.handle": "main_receives",
            "ipcMain.on": "main_receives",
        },
    },
    "worker_threads": {
        "framework": "node_worker_threads",
        "platform": "node",
        "apis": {
            "parentPort.postMessage": "parentPort.postMessage",
            "worker.postMessage": "worker.postMessage",
            "self.onmessage": "self.onmessage",
        },
        "direction_map": {
            "parentPort.postMessage": "worker_to_main",
            "worker.postMessage": "main_to_worker",
            "self.onmessage": "worker_receives",
        },
    },
    "child_process": {
        "framework": "node_child_process",
        "platform": "node",
        "apis": {"child.send": "child.send", "process.send": "process.send", "process.on": "process.on('message')"},
        "direction_map": {"child.send": "main_to_child", "process.send": "child_to_main", "process.on": "child_receives"},
    },
    "socket.io": {
        "framework": "socket_io",
        "platform": "node",
        "apis": {"socket.emit": "socket.emit", "socket.on": "socket.on", "io.emit": "io.emit"},
        "direction_map": {"socket.emit": "publishes", "socket.on": "subscribes", "io.emit": "publishes"},
    },
    "ws": {
        "framework": "websocket",
        "platform": "node",
        "apis": {"ws.send": "ws.send", "socket.send": "socket.send", "ws.on": "ws.on('message')"},
        "direction_map": {"ws.send": "sends", "socket.send": "sends", "ws.on": "receives"},
    },
}

ANDROID_MANIFEST_TAGS = {
    "receiver": MessageKind.BROADCAST_ACTION,
    "service": MessageKind.INTENT_ACTION,
    "provider": MessageKind.CONTENT_PROVIDER_URI,
}

AIDL_EXT = ".aidl"

SOURCE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".java", ".kt", ".kts", ".py",
}

ANDROID_MANIFEST_NAMES = {"AndroidManifest.xml", "androidmanifest.xml"}

IGNORED_ANY_SEGMENTS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".code2spec-venv", ".code2spec-tools", ".ruff_cache", ".pytest_cache"}
IGNORED_TOP_LEVEL_DIRS = {"code2spec"}  # generated output directory only when it is a relative top-level segment


# ── Helpers ──────────────────────────────────────────────────────────────────


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_file_lines(path: Path) -> list[str] | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


def _should_skip_path(path: Path, repo_path: Path) -> bool:
    """Skip generated/dependency paths using relative path segments only."""
    try:
        rel = path.relative_to(repo_path)
    except ValueError:
        rel = path
    parts = rel.parts
    if not parts:
        return True
    if any(part in IGNORED_ANY_SEGMENTS for part in parts):
        return True
    if parts[0] in IGNORED_TOP_LEVEL_DIRS:
        return True
    return False


def _find_imports(lines: list[str], file_path: str) -> list[dict[str, Any]]:
    imports: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for import_key, import_info in KNOWN_IMPORTS.items():
            matched = False
            if f'require("{import_key}")' in stripped or f"require('{import_key}')" in stripped:
                matched = True
            if f'from "{import_key}"' in stripped or f"from '{import_key}'" in stripped:
                matched = True
            if stripped.startswith("import ") and (f'"{import_key}"' in stripped or f"'{import_key}'" in stripped):
                matched = True
            if matched:
                key = (import_key, i, stripped)
                if key not in seen:
                    seen.add(key)
                    imports.append({
                        "import_name": import_key,
                        "framework": import_info["framework"],
                        "platform": import_info["platform"],
                        "line": i,
                        "expression": stripped,
                    })
    return imports


def _extract_channel_name(expression: str) -> str | None:
    # Channel/event as first string argument.
    m = re.search(r'(?:invoke|send|emit|on|handle|postMessage)\s*\(\s*["\']([^"\']+)["\']', expression)
    if m:
        return m.group(1)
    # Constant/member reference as first argument.
    m = re.search(r'(?:invoke|send|emit|on|handle)\s*\(\s*([A-Za-z_][\w.]*)', expression)
    if m:
        return m.group(1)
    # Structured postMessage payload type.
    m = re.search(r'type\s*:\s*["\']([^"\']+)["\']', expression)
    if m:
        return m.group(1)
    return None


def _is_dynamic_channel(expression: str) -> bool:
    if re.search(r'`[^`]*\$\{', expression):
        return True
    if re.search(r'["\'][^"\']*["\']\s*\+', expression):
        return True
    return False


def _make_evidence(
    type_: EvidenceType,
    label: str,
    file: str,
    line: int,
    expression: str,
    source: str = "source_scan",
    strength: EvidenceStrength = EvidenceStrength.HIGH,
) -> Evidence:
    return Evidence(
        type=type_,
        label=label,
        file=file,
        line_start=line,
        line_end=line,
        expression=expression,
        source=source,
        strength=strength,
    )


def _import_evidence(imports: list[dict[str, Any]], import_name: str, file_path: str) -> list[Evidence]:
    return [
        _make_evidence(EvidenceType.KNOWN_IMPORT, f"{import_name} import", file_path, imp["line"], imp["expression"])
        for imp in imports
        if imp["import_name"] == import_name
    ]


def _endpoint(
    *,
    role: ParticipantRole,
    kind: str,
    platform: str,
    framework: str,
    mechanism: str,
    name: str,
    normalized_name: str,
    direction: str,
    file: str,
    line: int,
    symbol: str,
    expression: str,
    evidence: list[Evidence],
    verification_hint: Verification,
    promotion_hint: Promotion,
    confidence: Confidence,
    unresolved: list[str] | None = None,
) -> EndpointRecord:
    return EndpointRecord(
        role=role,
        family=Family.MESSAGE.value,
        kind=kind,
        platform=platform,
        framework=framework,
        mechanism=mechanism,
        name=name,
        normalized_name=normalized_name,
        direction=direction,
        file=file,
        line=line,
        symbol=symbol,
        expression=expression,
        evidence=evidence,
        verification_hint=verification_hint,
        promotion_hint=promotion_hint,
        confidence=confidence,
        unresolved=unresolved or [],
    )


# ── Endpoint annotators ──────────────────────────────────────────────────────


def _collect_electron_endpoints(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[EndpointRecord]:
    electron_imports = [imp for imp in imports if imp["import_name"] == "electron"]
    if not electron_imports:
        return []
    endpoints: list[EndpointRecord] = []
    import_ev = _import_evidence(imports, "electron", file_path)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for api in ("ipcRenderer.invoke", "ipcRenderer.send", "ipcRenderer.sendSync", "ipcMain.handle", "ipcMain.on"):
            if api not in stripped:
                continue
            channel = _extract_channel_name(stripped)
            dynamic = _is_dynamic_channel(stripped)
            role = ParticipantRole.SENDER if api.startswith("ipcRenderer") else ParticipantRole.RECEIVER
            mechanism = KNOWN_IMPORTS["electron"]["apis"].get(api, api)
            direction = KNOWN_IMPORTS["electron"]["direction_map"].get(api, "unknown")
            evidence = [*import_ev, _make_evidence(EvidenceType.KNOWN_API, api, file_path, i, stripped)]
            unresolved: list[str] = []
            if channel and not dynamic:
                evidence.append(_make_evidence(EvidenceType.CHANNEL_LITERAL, f"channel: {channel}", file_path, i, stripped))
                verification_hint = Verification.LIKELY
                promotion_hint = Promotion.MODULE_ALLOWED
                conf = Confidence(label="medium", score=0.72, reasons=["known_import", "known_api", "channel_literal"])
            else:
                channel = channel or stripped[:60]
                unresolved.append("dynamic_channel_name" if dynamic else "channel_name_not_found")
                verification_hint = Verification.CANDIDATE
                promotion_hint = Promotion.ANALYSIS_ONLY
                conf = Confidence(label="low", score=0.4, reasons=["known_import", "known_api"])
            endpoints.append(_endpoint(
                role=role,
                kind=MessageKind.IPC_CHANNEL.value,
                platform="node",
                framework="electron",
                mechanism=mechanism,
                name=channel,
                normalized_name=channel if not dynamic else "",
                direction=direction,
                file=file_path,
                line=i,
                symbol=api,
                expression=stripped,
                evidence=evidence,
                verification_hint=verification_hint,
                promotion_hint=promotion_hint,
                confidence=conf,
                unresolved=unresolved,
            ))
    return endpoints


def _collect_node_worker_endpoints(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[EndpointRecord]:
    endpoints: list[EndpointRecord] = []
    for imp in imports:
        import_name = imp["import_name"]
        if import_name not in ("worker_threads", "child_process"):
            continue
        framework = KNOWN_IMPORTS[import_name]["framework"]
        import_ev = _import_evidence(imports, import_name, file_path)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            endpoint_specs: list[tuple[str, ParticipantRole, str, str]] = []
            if "parentPort.postMessage" in stripped:
                endpoint_specs.append(("parentPort.postMessage", ParticipantRole.SENDER, MessageKind.WORKER_MESSAGE.value, "worker_to_main"))
            if "postMessage(" in stripped and "parentPort" not in stripped and "window" not in stripped:
                endpoint_specs.append(("worker.postMessage", ParticipantRole.SENDER, MessageKind.WORKER_MESSAGE.value, "main_to_worker"))
            if re.match(r'self\.onmessage\s*=', stripped):
                endpoint_specs.append(("self.onmessage", ParticipantRole.RECEIVER, MessageKind.WORKER_MESSAGE.value, "worker_receives"))
            if "child.send" in stripped:
                endpoint_specs.append(("child.send", ParticipantRole.SENDER, MessageKind.WORKER_MESSAGE.value, "main_to_child"))
            if "process.send" in stripped:
                endpoint_specs.append(("process.send", ParticipantRole.SENDER, MessageKind.WORKER_MESSAGE.value, "child_to_main"))
            if re.search(r'(?:process|child)\.on\s*\(\s*["\']message["\']', stripped):
                endpoint_specs.append(("child.on(\'message\')", ParticipantRole.RECEIVER, MessageKind.WORKER_MESSAGE.value, "main_receives"))
            for symbol, role, kind, direction in endpoint_specs:
                msg_type = _extract_channel_name(stripped) or "message"
                evidence = [*import_ev, _make_evidence(EvidenceType.KNOWN_API, symbol, file_path, i, stripped)]
                if msg_type != "message":
                    evidence.append(_make_evidence(EvidenceType.CHANNEL_LITERAL, f"message type: {msg_type}", file_path, i, stripped, strength=EvidenceStrength.MEDIUM))
                endpoints.append(_endpoint(
                    role=role,
                    kind=kind,
                    platform="node",
                    framework=framework,
                    mechanism=symbol,
                    name=msg_type,
                    normalized_name=msg_type,
                    direction=direction,
                    file=file_path,
                    line=i,
                    symbol=symbol,
                    expression=stripped,
                    evidence=evidence,
                    verification_hint=Verification.LIKELY,
                    promotion_hint=Promotion.MODULE_ALLOWED,
                    confidence=Confidence(label="medium", score=0.68, reasons=["known_import", "known_api"]),
                ))
    return endpoints


def _collect_browser_endpoints(lines: list[str], file_path: str) -> list[EndpointRecord]:
    endpoints: list[EndpointRecord] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "window.postMessage" in stripped or ("postMessage(" in stripped and "parentPort" not in stripped):
            is_window = "window.postMessage" in stripped
            msg_type = _extract_channel_name(stripped) or "postMessage"
            kind = MessageKind.POST_MESSAGE.value if is_window else MessageKind.WORKER_MESSAGE.value
            framework = "browser" if is_window else "web_worker"
            platform = "browser" if is_window else "node"
            symbol = "window.postMessage" if is_window else "postMessage"
            evidence = [_make_evidence(EvidenceType.KNOWN_API, symbol, file_path, i, stripped)] if is_window else [
                _make_evidence(EvidenceType.GENERIC_API, symbol, file_path, i, stripped, strength=EvidenceStrength.LOW)
            ]
            if msg_type != "postMessage":
                evidence.append(_make_evidence(EvidenceType.CHANNEL_LITERAL, f"message type: {msg_type}", file_path, i, stripped, strength=EvidenceStrength.MEDIUM))
            endpoints.append(_endpoint(
                role=ParticipantRole.SENDER,
                kind=kind,
                platform=platform,
                framework=framework,
                mechanism=symbol,
                name=msg_type,
                normalized_name=msg_type,
                direction="sends",
                file=file_path,
                line=i,
                symbol=symbol,
                expression=stripped,
                evidence=evidence,
                verification_hint=Verification.LIKELY if is_window else Verification.CANDIDATE,
                promotion_hint=Promotion.MODULE_ALLOWED if is_window else Promotion.ANALYSIS_ONLY,
                confidence=Confidence(label="medium" if is_window else "low", score=0.65 if is_window else 0.35, reasons=["known_api"] if is_window else ["generic_api"]),
                unresolved=[] if is_window else ["worker_boundary_not_resolved"],
            ))
        if re.search(r'addEventListener\s*\(\s*["\']message["\']', stripped):
            msg_type = _extract_channel_name(stripped) or "message_event"
            endpoints.append(_endpoint(
                role=ParticipantRole.RECEIVER,
                kind=MessageKind.POST_MESSAGE.value,
                platform="browser",
                framework="browser",
                mechanism="window.addEventListener('message')",
                name=msg_type,
                normalized_name=msg_type,
                direction="receives",
                file=file_path,
                line=i,
                symbol="addEventListener",
                expression=stripped,
                evidence=[_make_evidence(EvidenceType.KNOWN_API, "window.addEventListener('message')", file_path, i, stripped)],
                verification_hint=Verification.LIKELY,
                promotion_hint=Promotion.MODULE_ALLOWED,
                confidence=Confidence(label="medium", score=0.6, reasons=["known_api"]),
            ))
    return endpoints


def _collect_socket_endpoints(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[EndpointRecord]:
    socket_imports = [imp for imp in imports if imp["import_name"] in ("socket.io", "ws")]
    if not socket_imports:
        return []
    endpoints: list[EndpointRecord] = []
    for imp in socket_imports:
        import_name = imp["import_name"]
        framework = KNOWN_IMPORTS[import_name]["framework"]
        import_ev = _import_evidence(imports, import_name, file_path)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            specs: list[tuple[str, ParticipantRole, str]] = []
            if re.search(r'(?:socket|io)\.emit\s*\(', stripped):
                specs.append(("socket.emit", ParticipantRole.SENDER, "publishes"))
            if re.search(r'(?:socket)\.on\s*\(', stripped):
                specs.append(("socket.on", ParticipantRole.RECEIVER, "subscribes"))
            if re.search(r'(?:ws|socket)\.send\s*\(', stripped):
                specs.append(("ws.send", ParticipantRole.SENDER, "sends"))
            if re.search(r'(?:ws|socket)\.on\s*\(\s*["\']message["\']', stripped):
                specs.append(("ws.on(\'message\')", ParticipantRole.RECEIVER, "receives"))
            for symbol, role, direction in specs:
                event_name = _extract_channel_name(stripped) or "message"
                evidence = [*import_ev, _make_evidence(EvidenceType.KNOWN_API, symbol, file_path, i, stripped)]
                if event_name != "message":
                    evidence.append(_make_evidence(EvidenceType.CHANNEL_LITERAL, f"event: {event_name}", file_path, i, stripped))
                endpoints.append(_endpoint(
                    role=role,
                    kind=MessageKind.SOCKET_EVENT.value,
                    platform="node",
                    framework=framework,
                    mechanism=symbol,
                    name=event_name,
                    normalized_name=event_name,
                    direction=direction,
                    file=file_path,
                    line=i,
                    symbol=symbol,
                    expression=stripped,
                    evidence=evidence,
                    verification_hint=Verification.LIKELY,
                    promotion_hint=Promotion.MODULE_ALLOWED,
                    confidence=Confidence(label="medium", score=0.7, reasons=["known_import", "known_api"]),
                ))
    return endpoints


def _collect_generic_event_endpoints(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[EndpointRecord]:
    known_frameworks = {imp["import_name"] for imp in imports}
    if known_frameworks & {"electron", "socket.io", "ws", "worker_threads", "child_process"}:
        return []
    endpoints: list[EndpointRecord] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m = re.search(r'\.emit\s*\(\s*["\']([^"\']+)["\']', stripped)
        if not m:
            continue
        event_name = m.group(1)
        endpoints.append(_endpoint(
            role=ParticipantRole.SENDER,
            kind=MessageKind.EVENT_NAME.value,
            platform="unknown",
            framework="unknown",
            mechanism="generic_emit",
            name=event_name,
            normalized_name=event_name,
            direction="unknown",
            file=file_path,
            line=i,
            symbol="emit",
            expression=stripped,
            evidence=[_make_evidence(EvidenceType.GENERIC_API, "emit", file_path, i, stripped, strength=EvidenceStrength.LOW)],
            verification_hint=Verification.LOW,
            promotion_hint=Promotion.ANALYSIS_ONLY,
            confidence=Confidence(label="low", score=0.2, reasons=["generic_api"]),
            unresolved=["no_known_framework_import"],
        ))
    return endpoints


def _collect_android_source_endpoints(lines: list[str], file_path: str) -> list[EndpointRecord]:
    endpoints: list[EndpointRecord] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m = re.search(r'sendBroadcast\s*\(\s*(?:new\s+)?Intent\s*\(\s*["\']([^"\']+)["\']', stripped)
        if m:
            action = m.group(1)
            endpoints.append(_endpoint(
                role=ParticipantRole.SENDER,
                kind=MessageKind.BROADCAST_ACTION.value,
                platform="android",
                framework="android",
                mechanism="sendBroadcast",
                name=action,
                normalized_name=action,
                direction="sends",
                file=file_path,
                line=i,
                symbol="sendBroadcast",
                expression=stripped,
                evidence=[_make_evidence(EvidenceType.KNOWN_API, "sendBroadcast", file_path, i, stripped)],
                verification_hint=Verification.LIKELY,
                promotion_hint=Promotion.MODULE_ALLOWED,
                confidence=Confidence(label="medium", score=0.7, reasons=["known_api"]),
            ))

        intent_action_assign = re.search(r'\baction\s*=\s*((?:[A-Za-z_]\w*\.)+[A-Za-z_]\w*)', stripped)
        if intent_action_assign:
            action_ref = intent_action_assign.group(1)
            endpoints.append(_android_intent_endpoint(
                role=ParticipantRole.SENDER,
                name=action_ref,
                direction="sends",
                file_path=file_path,
                line=i,
                symbol="Intent.action",
                expression=stripped,
                mechanism="Intent.action assignment",
                reasons=["intent_action_assignment"],
            ))

        # Pattern 1: when (intent.action) { ... } with constant cases
        when_action = re.search(r'((?:[A-Za-z_]\w*\.)+[A-Za-z_]\w*)\s*->', stripped)
        if when_action and ("IntentActions." in when_action.group(1) or "Intent." in when_action.group(1)):
            action_ref = when_action.group(1)
            endpoints.append(_android_intent_endpoint(
                role=ParticipantRole.RECEIVER,
                name=action_ref,
                direction="receives",
                file_path=file_path,
                line=i,
                symbol="intent.action when",
                expression=stripped,
                mechanism="intent.action when branch",
                reasons=["intent_action_receiver"],
            ))

        # Pattern 2: case IntentActions.HABIT_NOTIFICATION.action -> (Kotlin when with property access)
        intent_prop_case = re.search(r'((?:[A-Za-z_]\w*\.)+[A-Za-z_]\w+)\.action\s*->', stripped)
        if intent_prop_case:
            action_ref = intent_prop_case.group(1)
            endpoints.append(_android_intent_endpoint(
                role=ParticipantRole.RECEIVER,
                name=action_ref,
                direction="receives",
                file_path=file_path,
                line=i,
                symbol="intent.action property when",
                expression=stripped,
                mechanism="intent.action property when branch",
                reasons=["intent_action_property_receiver"],
            ))

        action_compare = re.search(r'intent\??\.action\s*==\s*((?:[A-Za-z_]\w*\.)+[A-Za-z_]\w*)', stripped)
        if action_compare:
            action_ref = action_compare.group(1)
            endpoints.append(_android_intent_endpoint(
                role=ParticipantRole.RECEIVER,
                name=action_ref,
                direction="receives",
                file_path=file_path,
                line=i,
                symbol="intent.action compare",
                expression=stripped,
                mechanism="intent.action comparison",
                reasons=["intent_action_receiver"],
            ))
    return endpoints


def _android_intent_endpoint(
    *,
    role: ParticipantRole,
    name: str,
    direction: str,
    file_path: str,
    line: int,
    symbol: str,
    expression: str,
    mechanism: str,
    reasons: list[str],
) -> EndpointRecord:
    return _endpoint(
        role=role,
        kind=MessageKind.INTENT_ACTION.value,
        platform="android",
        framework="android",
        mechanism=mechanism,
        name=name,
        normalized_name=name,
        direction=direction,
        file=file_path,
        line=line,
        symbol=symbol,
        expression=expression,
        evidence=[
            _make_evidence(
                EvidenceType.KNOWN_API,
                mechanism,
                file_path,
                line,
                expression,
                strength=EvidenceStrength.MEDIUM,
            )
        ],
        verification_hint=Verification.LIKELY,
        promotion_hint=Promotion.MODULE_ALLOWED,
        confidence=Confidence(label="medium", score=0.72, reasons=reasons),
    )


def _collect_android_manifest_endpoints(manifest_path: Path) -> list[EndpointRecord]:
    lines = _read_file_lines(manifest_path)
    if not lines:
        return []
    file_path = str(manifest_path)
    endpoints: list[EndpointRecord] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for tag, kind in ANDROID_MANIFEST_TAGS.items():
            if f"<{tag}" not in stripped:
                continue
            action_name = None
            for j in range(i, min(i + 10, len(lines) + 1)):
                action_line = lines[j - 1].strip()
                action_m = re.search(r'<action\s+android:name="([^"]+)"', action_line)
                if action_m:
                    action_name = action_m.group(1)
                    break
                if f"</{tag}>" in action_line:
                    break
            name = action_name or f"android_{tag}"
            endpoints.append(_endpoint(
                role=ParticipantRole.RECEIVER if tag == "receiver" else ParticipantRole.PROVIDER,
                kind=kind.value,
                platform="android",
                framework="android",
                mechanism=f"android_{tag}",
                name=name,
                normalized_name=name,
                direction="receives" if tag == "receiver" else "provides",
                file=file_path,
                line=i,
                symbol=f"AndroidManifest <{tag}>",
                expression=stripped,
                evidence=[_make_evidence(EvidenceType.MANIFEST_DECLARATION, f"AndroidManifest <{tag}>", file_path, i, stripped, source="manifest_scan")],
                verification_hint=Verification.LIKELY,
                promotion_hint=Promotion.MODULE_ALLOWED,
                confidence=Confidence(label="medium", score=0.7, reasons=["manifest_declaration"]),
                unresolved=[] if action_name else ["action_name_not_found"],
            ))
        if "<provider" in stripped:
            authority_m = re.search(r'android:authorities="([^"]+)"', stripped)
            if authority_m:
                authority = authority_m.group(1)
                endpoints.append(_endpoint(
                    role=ParticipantRole.PROVIDER,
                    kind=MessageKind.CONTENT_PROVIDER_URI.value,
                    platform="android",
                    framework="android",
                    mechanism="content_provider",
                    name=authority,
                    normalized_name=authority,
                    direction="provides",
                    file=file_path,
                    line=i,
                    symbol="AndroidManifest <provider>",
                    expression=stripped,
                    evidence=[_make_evidence(EvidenceType.MANIFEST_DECLARATION, f"AndroidManifest <provider> authority={authority}", file_path, i, stripped, source="manifest_scan")],
                    verification_hint=Verification.LIKELY,
                    promotion_hint=Promotion.MODULE_ALLOWED,
                    confidence=Confidence(label="medium", score=0.7, reasons=["manifest_declaration"]),
                ))
    return endpoints


# ── Constant collectors ──────────────────────────────────────────────────────


def _collect_message_constants(lines: list[str], file_path: str) -> list[ConstantRecord]:
    constants: list[ConstantRecord] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m = re.match(r'enum\s+(\w*(?:Ipc|Message|Event|Channel|Action|Command)\w*)\s*\{', stripped)
        if m:
            enum_name = m.group(1)
            for j in range(i, min(i + 30, len(lines) + 1)):
                member_line = lines[j - 1].strip()
                member_m = re.match(r'(\w+)\s*=\s*["\']([^"\']+)["\']', member_line)
                if member_m:
                    member_name, member_value = member_m.group(1), member_m.group(2)
                    constants.append(ConstantRecord(
                        family=Family.MESSAGE.value,
                        kind=MessageKind.MESSAGE_CONSTANT.value,
                        platform="unknown",
                        framework="unknown",
                        mechanism="enum_constant",
                        name=f"{enum_name}.{member_name}",
                        normalized_name=member_value,
                        file=file_path,
                        line=j,
                        symbol=f"{enum_name}.{member_name}",
                        expression=member_line,
                        evidence=[_make_evidence(EvidenceType.CONSTANT_DEFINITION, f"enum {enum_name}.{member_name}", file_path, j, member_line, strength=EvidenceStrength.MEDIUM)],
                    ))
                if member_line.startswith("}"):
                    break

        intent_enum = re.match(r'enum\s+class\s+(Intent\w*)\s*\([^)]*\)\s*\{', stripped)
        if intent_enum:
            enum_name = intent_enum.group(1)
            for j in range(i + 1, min(i + 80, len(lines) + 1)):
                member_line = lines[j - 1].strip()
                member_m = re.match(r'(\w+)\s*\(\s*["\']([^"\']+)["\']\s*\)\s*,?', member_line)
                if member_m:
                    member_name, member_value = member_m.group(1), member_m.group(2)
                    symbol = f"{enum_name}.{member_name}.action"
                    constants.append(ConstantRecord(
                        family=Family.MESSAGE.value,
                        kind=MessageKind.INTENT_ACTION.value,
                        platform="android",
                        framework="android",
                        mechanism="enum_intent_action",
                        name=symbol,
                        normalized_name=symbol,
                        file=file_path,
                        line=j,
                        symbol=symbol,
                        expression=member_line,
                        evidence=[
                            _make_evidence(
                                EvidenceType.CONSTANT_DEFINITION,
                                f"intent action value: {member_value}",
                                file_path,
                                j,
                                member_line,
                                strength=EvidenceStrength.MEDIUM,
                            )
                        ],
                    ))
                if member_line.startswith("}"):
                    break

        m = re.match(r'(?:export\s+)?const\s+(\w*(?:Ipc|Message|Event|Channel|Action|Command)\w*)\s*=', stripped)
        if m and "as const" in stripped:
            const_name = m.group(1)
            constants.append(ConstantRecord(
                family=Family.MESSAGE.value,
                kind=MessageKind.MESSAGE_CONSTANT.value,
                platform="unknown",
                framework="unknown",
                mechanism="const_object",
                name=const_name,
                normalized_name=const_name,
                file=file_path,
                line=i,
                symbol=const_name,
                expression=stripped,
                evidence=[_make_evidence(EvidenceType.CONSTANT_DEFINITION, f"const {const_name}", file_path, i, stripped, strength=EvidenceStrength.MEDIUM)],
            ))
    return constants


def _collect_aidl_constants(repo_path: Path) -> list[ConstantRecord]:
    constants: list[ConstantRecord] = []
    for aidl_path in repo_path.rglob(f"*{AIDL_EXT}"):
        if _should_skip_path(aidl_path, repo_path):
            continue
        file_path = str(aidl_path)
        lines = _read_file_lines(aidl_path)
        if not lines:
            continue
        interface_name = aidl_path.stem
        for line in lines:
            m = re.match(r'\s*interface\s+(\w+)', line)
            if m:
                interface_name = m.group(1)
                break
        constants.append(ConstantRecord(
            family=Family.MESSAGE.value,
            kind=MessageKind.AIDL_INTERFACE.value,
            platform="android",
            framework="android",
            mechanism="aidl",
            name=interface_name,
            normalized_name=interface_name,
            file=file_path,
            line=1,
            symbol=interface_name,
            expression=f"AIDL: {interface_name}",
            evidence=[_make_evidence(EvidenceType.KNOWN_API, f"AIDL interface: {interface_name}", file_path, 1, f"AIDL: {interface_name}", source="file_scan")],
        ))
    return constants


# ── Candidate builder / pairing ──────────────────────────────────────────────


def _participant_from_endpoint(ep: EndpointRecord) -> Participant:
    return Participant(role=ep.role, file=ep.file, line=ep.line, symbol=ep.symbol, expression=ep.expression)


def _candidate_from_endpoint(ep: EndpointRecord, extra_unresolved: list[str] | None = None) -> InterfaceCandidate:
    unresolved = [*ep.unresolved, *(extra_unresolved or [])]
    cid = compute_candidate_id(ep.family, ep.kind, ep.platform, ep.framework, ep.normalized_name or ep.name, ep.file, ep.line, ep.expression)
    return InterfaceCandidate(
        id=cid,
        family=Family(ep.family),
        kind=ep.kind,
        platform=ep.platform,
        framework=ep.framework,
        mechanism=ep.mechanism,
        name=ep.name,
        normalized_name=ep.normalized_name,
        direction=ep.direction,
        origin=Origin.SCANNER,
        verification=ep.verification_hint,
        confidence=ep.confidence,
        promotion=ep.promotion_hint,
        needs_human_review=ep.verification_hint in (Verification.CANDIDATE, Verification.LOW, Verification.LLM_SUGGESTED),
        participants={ep.role.value: [_participant_from_endpoint(ep)]},
        evidence=ep.evidence,
        unresolved=unresolved,
    )


def _candidate_from_constant(record: ConstantRecord) -> InterfaceCandidate:
    cid = compute_candidate_id(record.family, record.kind, record.platform, record.framework, record.normalized_name or record.name, record.file, record.line, record.expression)
    return InterfaceCandidate(
        id=cid,
        family=Family(record.family),
        kind=record.kind,
        platform=record.platform,
        framework=record.framework,
        mechanism=record.mechanism,
        name=record.name,
        normalized_name=record.normalized_name,
        direction="unknown",
        origin=Origin.SCANNER,
        verification=Verification.CANDIDATE,
        confidence=Confidence(label="low", score=0.35, reasons=["constant_definition"]),
        promotion=Promotion.ANALYSIS_ONLY,
        needs_human_review=True,
        participants={ParticipantRole.CONSTANT.value: [Participant(role=ParticipantRole.CONSTANT, file=record.file, line=record.line, symbol=record.symbol, expression=record.expression)]},
        evidence=record.evidence,
        unresolved=record.unresolved,
    )


def _build_candidates(endpoints: list[EndpointRecord], constants: list[ConstantRecord]) -> list[InterfaceCandidate]:
    candidates: list[InterfaceCandidate] = []
    grouped: dict[tuple[str, str, str, str, str], list[EndpointRecord]] = {}
    unpairable: list[EndpointRecord] = []

    for ep in endpoints:
        if ep.normalized_name:
            grouped.setdefault(ep.pair_key, []).append(ep)
        else:
            unpairable.append(ep)

    for group in grouped.values():
        senders = [ep for ep in group if ep.role in (ParticipantRole.SENDER, ParticipantRole.PUBLISHER, ParticipantRole.CONSUMER)]
        receivers = [ep for ep in group if ep.role in (ParticipantRole.RECEIVER, ParticipantRole.SUBSCRIBER, ParticipantRole.PROVIDER)]
        first = group[0]
        if senders and receivers:
            primary = senders[0]
            evidence: list[Evidence] = []
            seen_ev: set[tuple[str, str, int, str]] = set()
            for ep in group:
                for ev in ep.evidence:
                    key = (ev.type.value, ev.file, ev.line_start, ev.expression)
                    if key not in seen_ev:
                        seen_ev.add(key)
                        evidence.append(ev)
            participants: dict[str, list[Participant]] = {}
            for ep in group:
                participants.setdefault(ep.role.value, []).append(_participant_from_endpoint(ep))
            mechanism = first.mechanism
            if first.framework == "electron":
                has_invoke = any("ipcRenderer.invoke" in ep.symbol for ep in group)
                has_handle = any("ipcMain.handle" in ep.symbol for ep in group)
                has_send = any("ipcRenderer.send" in ep.symbol or "ipcRenderer.sendSync" in ep.symbol for ep in group)
                has_on = any("ipcMain.on" in ep.symbol for ep in group)
                if has_invoke and has_handle:
                    mechanism = "ipcRenderer.invoke/ipcMain.handle"
                elif has_send and has_on:
                    mechanism = "ipcRenderer.send/ipcMain.on"
            cid = compute_candidate_id(first.family, first.kind, first.platform, first.framework, first.normalized_name, primary.file, primary.line, primary.expression)
            candidates.append(InterfaceCandidate(
                id=cid,
                family=Family(first.family),
                kind=first.kind,
                platform=first.platform,
                framework=first.framework,
                mechanism=mechanism,
                name=first.normalized_name,
                normalized_name=first.normalized_name,
                direction="paired",
                origin=Origin.SCANNER,
                verification=Verification.CONFIRMED,
                confidence=Confidence(label="high", score=0.9, reasons=["known_api", "channel_literal", "sender_receiver_pair"]),
                promotion=Promotion.MODULE_ALLOWED,
                needs_human_review=False,
                participants=participants,
                evidence=evidence,
                unresolved=[],
            ))
        else:
            missing = "no_matching_receiver" if senders else "no_matching_sender"
            for ep in group:
                candidates.append(_candidate_from_endpoint(ep, [missing]))

    for ep in unpairable:
        candidates.append(_candidate_from_endpoint(ep))

    candidates.extend(_candidate_from_constant(c) for c in constants)
    return sort_candidates(candidates)


# ── Backward-compatible scanner helpers used by tests ────────────────────────


def _scan_electron_ipc(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_electron_endpoints(lines, file_path, imports), [])


def _scan_node_workers(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_node_worker_endpoints(lines, file_path, imports), [])


def _scan_browser_messaging(lines: list[str], file_path: str) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_browser_endpoints(lines, file_path), [])


def _scan_socket_io(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_socket_endpoints(lines, file_path, imports), [])


def _scan_generic_events(lines: list[str], file_path: str, imports: list[dict[str, Any]]) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_generic_event_endpoints(lines, file_path, imports), [])


def _scan_message_constants(lines: list[str], file_path: str) -> list[InterfaceCandidate]:
    return [_candidate_from_constant(c) for c in _collect_message_constants(lines, file_path)]


def _scan_android_manifest(manifest_path: Path) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_android_manifest_endpoints(manifest_path), [])


def _scan_android_source(lines: list[str], file_path: str) -> list[InterfaceCandidate]:
    return _build_candidates(_collect_android_source_endpoints(lines, file_path), [])


def _scan_aidl_files(repo_path: Path) -> list[InterfaceCandidate]:
    return [_candidate_from_constant(c) for c in _collect_aidl_constants(repo_path)]


# ── Main scan function ───────────────────────────────────────────────────────


def run_scan(
    repo_path: Path,
    ast_dir: Path | None = None,
    families: list[str] | None = None,
    targets: list[str] | None = None,
    output_dir: Path | None = None,
) -> CandidateCollection:
    """Run the interface/protocol candidate scan.

    ``ast_dir`` is accepted for workflow compatibility. The current v1 scanner
    uses source/manifest evidence directly; future versions may use AST records
    to enrich call/constant provenance.
    """
    del ast_dir  # explicit compatibility knob; not used in v1
    if families is None:
        families = ["message"]
    if targets is None:
        targets = ["android", "node", "react"]

    endpoints: list[EndpointRecord] = []
    constants: list[ConstantRecord] = []

    # 1. Scan source files into intermediate endpoint/constant records.
    for source_path in repo_path.rglob("*"):
        if not source_path.is_file():
            continue
        if _should_skip_path(source_path, repo_path):
            continue
        ext = source_path.suffix.lower()
        if ext not in SOURCE_EXTENSIONS:
            continue
        lines = _read_file_lines(source_path)
        if not lines:
            continue
        file_path = str(source_path.relative_to(repo_path))
        imports = _find_imports(lines, file_path)

        if "message" in families:
            if "node" in targets or "react" in targets:
                endpoints.extend(_collect_electron_endpoints(lines, file_path, imports))
            if "node" in targets:
                endpoints.extend(_collect_node_worker_endpoints(lines, file_path, imports))
                endpoints.extend(_collect_socket_endpoints(lines, file_path, imports))
            if "react" in targets or "node" in targets:
                endpoints.extend(_collect_browser_endpoints(lines, file_path))
            endpoints.extend(_collect_generic_event_endpoints(lines, file_path, imports))
            constants.extend(_collect_message_constants(lines, file_path))
            if "android" in targets and ext in (".java", ".kt", ".kts"):
                endpoints.extend(_collect_android_source_endpoints(lines, file_path))

    # 2. Scan Android manifests and AIDL files.
    if "android" in targets and "message" in families:
        for manifest_name in ANDROID_MANIFEST_NAMES:
            for manifest_path in repo_path.rglob(manifest_name):
                if not _should_skip_path(manifest_path, repo_path):
                    endpoints.extend(_collect_android_manifest_endpoints(manifest_path))
        constants.extend(_collect_aidl_constants(repo_path))

    # 3. Pair endpoints and build final candidates.
    candidates = _build_candidates(endpoints, constants)
    metrics = _compute_metrics(candidates)

    return CandidateCollection(
        schema_version=1,
        generated_at=_utc_now(),
        analysis_target=str(repo_path),
        output_dir=str(output_dir or ""),
        families=families,
        candidates=candidates,
        metrics=metrics,
    )


def _compute_metrics(candidates: list[InterfaceCandidate]) -> dict[str, Any]:
    total = len(candidates)
    by_verification: dict[str, int] = {}
    by_family: dict[str, int] = {}
    msg_total = msg_confirmed = msg_likely = msg_candidate = 0
    for c in candidates:
        by_verification[c.verification.value] = by_verification.get(c.verification.value, 0) + 1
        by_family[c.family.value] = by_family.get(c.family.value, 0) + 1
        if c.family == Family.MESSAGE:
            msg_total += 1
            if c.verification == Verification.CONFIRMED:
                msg_confirmed += 1
            elif c.verification == Verification.LIKELY:
                msg_likely += 1
            elif c.verification == Verification.CANDIDATE:
                msg_candidate += 1
    return {
        "total": total,
        "by_verification": by_verification,
        "by_family": by_family,
        "message": {"total": msg_total, "confirmed": msg_confirmed, "likely": msg_likely, "candidate": msg_candidate},
    }
