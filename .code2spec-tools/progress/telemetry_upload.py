#!/usr/bin/env python3
"""Best-effort upload of Code2Spec run telemetry to the skills endpoint.

Fired at the end of finalize (W3) and delta (W-DELTA) stages. Never raises —
a network failure or opt-out must not break history finalization.
"""

from __future__ import annotations

import base64
import json
import os
import platform
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

try:
    from ..analysis_paths import get_canonical_paths
    from .common import _load_runtime_stats
    from .telemetry import resolve_git_context
except ImportError:  # script/installed-tools flat execution
    from analysis_paths import get_canonical_paths
    from progress.common import _load_runtime_stats
    from progress.telemetry import resolve_git_context

# 엔드포인트 URL·타임아웃은 환경변수로 오버라이드 가능(테스트/스테이징 대응).
TELEMETRY_ENDPOINT = os.environ.get(
    "CODE2SPEC_TELEMETRY_ENDPOINT", "https://skills.sec.samsung.net/api/v1/telemetry"
)
# 엔드포인트 event는 고정 enum(install|remove|check|update|find|experimental_sync|usage).
# code2spec 식별자는 skill 필드에 담는다 (참조 예: "CODE-skills/testkit/cli").
EVENT_NAME = "usage"
SKILL_NAME = "code2spec/code2spec-telemetry"
OPT_OUT_ENV = "CODE2SPEC_TELEMETRY_UPLOAD"  # set to 0/false/no to disable
UPLOAD_MARKER_FILE = ".telemetry-uploaded.json"  # 세션별 중복 전송 방지 마커
try:
    DEFAULT_TIMEOUT = float(os.environ.get("CODE2SPEC_TELEMETRY_TIMEOUT", "3.0"))
except ValueError:
    DEFAULT_TIMEOUT = 3.0
_UNKNOWN = "unknown"
# 템플릿 placeholder(예: {{CODE2SPEC_CODING_AGENT}}) 감지용 — 부분 문자열 매칭 대신 패턴 매칭
_PLACEHOLDER_RE = re.compile(r"\{\{.*?\}\}")
# 엔드포인트 하드 제한: JSON body ≤ 8192 bytes. 파일 전체 대신 FTE 산출에
# 필요한 필드만 추려 base64로 담으므로 항상 이 한도 안에 든다.
MAX_BODY_BYTES = 8192


def _upload_enabled() -> bool:
    """Upload is on by default; opt out via CODE2SPEC_TELEMETRY_UPLOAD=0."""
    raw = os.environ.get(OPT_OUT_ENV)
    if raw is None:
        return True
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _mask_home(path: str | None) -> str | None:
    """홈 디렉토리 접두를 ~ 로 치환 (사용자명 노출 방지, 디렉토리 구조는 유지)."""
    if not path:
        return path
    try:
        home = str(Path.home())
    except (RuntimeError, OSError):
        return path
    if path == home:
        return "~"
    if path.startswith(home + os.sep):
        return "~" + path[len(home):]
    return path


def resolve_agent(stats: dict[str, Any]) -> str:
    """Return the coding agent, or 'unknown' when missing/blank/unsubstituted."""
    agent = stats.get("coding_agent")
    if not isinstance(agent, str):
        return _UNKNOWN
    agent = agent.strip()
    if not agent or _PLACEHOLDER_RE.search(agent):  # empty or unsubstituted placeholder
        return _UNKNOWN
    return agent


def _load_telemetry_events(output_dir: Path) -> list[dict[str, Any]]:
    """Parse telemetry-events.jsonl into event dicts (empty list if absent)."""
    path = get_canonical_paths(output_dir).telemetry_events
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                events.append(item)
    except OSError:
        return []
    return events


def collect_fte_metrics(output_dir: Path, stats: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract only the fields FTE 산출 uses, from telemetry events + runtime-stats.

    FTE model needs: code lines/files (코드 탐색·파일 파악), md lines (문서 작성),
    module count (delta F^Δ), run_type (옵션1/2 구분), session_id·timestamp
    (delta 월별 집계), agent·version (식별).

    stats를 넘기면 runtime-stats.json 재로드를 생략한다(중복 I/O 방지).
    """
    if stats is None:
        stats = _load_runtime_stats(output_dir)
    events = _load_telemetry_events(output_dir)

    # code_size는 finalized(W3에서 AST 보강된 확정값)를 우선한다. 순서에 의존하지
    # 않도록 finalized와 measured/session 초기값을 분리 수집한 뒤 finalized를 채택.
    code_lines = code_files = md_lines = module_count = None
    early_lines = early_files = None  # code_size_measured / session_started (초기 추정)
    modules_regenerated = 0
    finalized_ts = None
    for event in events:
        etype = event.get("event_type")
        if etype == "code_size_finalized":
            if event.get("code_size_total_lines") is not None:
                code_lines = event["code_size_total_lines"]
            if event.get("code_size_total_files") is not None:
                code_files = event["code_size_total_files"]
        elif etype in ("code_size_measured", "session_started"):
            if event.get("code_size_total_lines") is not None:
                early_lines = event["code_size_total_lines"]
            if event.get("code_size_total_files") is not None:
                early_files = event["code_size_total_files"]
        elif etype == "history_finalized":
            md_lines = event.get("md_lines")
            module_count = event.get("module_count")
            finalized_ts = event.get("timestamp")
        elif etype == "module_regenerated":
            modules_regenerated += 1

    # 우선순위: finalized → 초기(measured/session) → runtime-stats code_size
    code_size = stats.get("code_size") or {}
    if code_lines is None:
        code_lines = early_lines if early_lines is not None else code_size.get("total_lines")
    if code_files is None:
        code_files = early_files if early_files is not None else code_size.get("total_files")

    # 프로젝트 식별: git 정보(resolve_git_context가 runtime-stats에 없으면 repo에서 직접 추출)
    # 와 analysis_target(실제 분석 경로)을 함께 싣는다.
    git = resolve_git_context(output_dir, stats) or {}
    raw_target = stats.get("analysis_target") or stats.get("target_path")
    project = git.get("repo")
    if not project and raw_target:
        project = os.path.basename(str(raw_target).rstrip("/")) or None
    # 사용자명 노출을 막기 위해 홈 경로만 ~ 로 마스킹 (디렉토리 구조는 유지)
    analysis_target = _mask_home(str(raw_target) if raw_target else None)

    metrics = {
        "session_id": stats.get("session_id"),
        "timestamp": finalized_ts,
        "run_type": stats.get("run_type"),
        "agent": resolve_agent(stats),
        "version": stats.get("code2spec_version"),
        "analysis_target": analysis_target,
        "project": project,
        "branch": git.get("branch"),
        "commit": git.get("commit"),
        "code_lines": code_lines,
        "code_files": code_files,
        "md_lines": md_lines,
        "module_count": module_count,
        "modules_regenerated": modules_regenerated,
    }
    return {k: v for k, v in metrics.items() if v is not None}


def build_fte_jsonl(
    output_dir: Path, *, include_modules: bool = True, stats: dict[str, Any] | None = None
) -> str:
    """FTE 산출에 필요한 최소 이벤트만 담은 jsonl 문자열.

    기존 fte_calculator `--telemetry` 파서가 그대로 읽을 수 있는 스키마
    (event_type별 이벤트)로, 원본의 bulky 필드는 모두 제거해 최소화한다.
    - code_size_finalized: 코드 라인/파일 수 (옵션1 C·F)
    - history_finalized:   md_lines·module_count·timestamp (문서 작성·월별)
    - module_regenerated:  delta의 F^Δ 카운트용 (delta 실행에서만)

    include_modules=False면 가변 길이인 module_regenerated 줄을 생략한다
    (8KB 초과 시 build_payload가 이 경로로 축소).

    module_regenerated는 N줄로 방출한다 — 수신 측 fte_calculator 파서가 이벤트
    "개수"로 F^Δ를 집계하기 때문(count 필드 미지원). 줄 수 폭증은 build_payload의
    8KB 가드가 흡수한다.
    """
    m = collect_fte_metrics(output_dir, stats)
    sid = m.get("session_id")
    run_type = m.get("run_type")
    # 어느 프로젝트/버전에서 나온 telemetry인지 식별 (git + analysis_target)
    ident = {
        k: m.get(k)
        for k in ("project", "branch", "commit", "analysis_target")
        if m.get(k) is not None
    }
    lines = [
        json.dumps(
            {
                "event_type": "code_size_finalized",
                "session_id": sid,
                "run_type": run_type,
                **ident,
                "code_size_total_lines": m.get("code_lines"),
                "code_size_total_files": m.get("code_files"),
            },
            ensure_ascii=False,
        ),
        json.dumps(
            {
                "event_type": "history_finalized",
                "session_id": sid,
                "run_type": run_type,
                **ident,
                "md_lines": m.get("md_lines"),
                "module_count": m.get("module_count"),
                "timestamp": m.get("timestamp"),
            },
            ensure_ascii=False,
        ),
    ]
    # 재생성 모듈 수(F^Δ)는 delta에서만 의미 → delta일 때만 카운트 라인 추가
    if include_modules and (run_type or "").lower() == "delta":
        for _ in range(int(m.get("modules_regenerated") or 0)):
            lines.append(
                json.dumps(
                    {"event_type": "module_regenerated", "session_id": sid, "run_type": run_type},
                    ensure_ascii=False,
                )
            )
    return "\n".join(lines) + "\n"


def _envelope(stats: dict[str, Any], data_b64: str) -> dict[str, Any]:
    return {
        "event": EVENT_NAME,
        "skill": SKILL_NAME,
        "agent": resolve_agent(stats),
        "os": platform.system() or _UNKNOWN,
        "data": data_b64,
    }


def _body_bytes(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def build_payload(output_dir: Path, stats: dict[str, Any] | None = None) -> dict[str, Any]:
    """Envelope(event/skill/agent/os) + `data`에 base64(FTE 최소 jsonl).

    전송된 `data`를 base64 디코드하면 그대로 fte_calculator `--telemetry`로
    FTE를 산출할 수 있다(수신 측에서 루프가 닫힌다).

    8KB(MAX_BODY_BYTES) 초과 시(delta에서 재생성 모듈이 매우 많을 때) 가변 길이인
    module_regenerated 줄을 생략해 한도 안으로 축소한다(핵심 2줄은 고정 크기).

    stats를 넘기면 runtime-stats.json 재로드를 생략한다(중복 I/O 방지).
    """
    if stats is None:
        stats = _load_runtime_stats(output_dir)

    def _encode(include_modules: bool) -> dict[str, Any]:
        jsonl = build_fte_jsonl(output_dir, include_modules=include_modules, stats=stats)
        return _envelope(stats, base64.b64encode(jsonl.encode("utf-8")).decode("ascii"))

    payload = _encode(include_modules=True)
    if _body_bytes(payload) > MAX_BODY_BYTES:
        payload = _encode(include_modules=False)
    return payload


def _marker_path(output_dir: Path) -> Path:
    """세션별 전송 여부를 기록하는 마커 파일 (telemetry 이벤트 파일 옆)."""
    return get_canonical_paths(output_dir).telemetry_events.parent / UPLOAD_MARKER_FILE


def _uploaded_sessions(output_dir: Path) -> list[str]:
    path = _marker_path(output_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    sessions = data.get("sessions") if isinstance(data, dict) else None
    return sessions if isinstance(sessions, list) else []


def _mark_uploaded(output_dir: Path, session_id: str) -> None:
    sessions = _uploaded_sessions(output_dir)
    if session_id in sessions:
        return
    sessions.append(session_id)
    try:
        path = _marker_path(output_dir)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"sessions": sessions}), encoding="utf-8")
    except OSError:
        pass


def upload_telemetry(output_dir: Path, *, timeout: float = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """POST the run telemetry payload. Best-effort — returns a status dict, never raises.

    같은 session_id는 한 번만 전송한다(finalize 재실행 시 중복 방지). 마커는
    전송이 성공(2xx)했을 때만 기록하므로, 실패한 실행은 다음 finalize에서 재시도된다.
    session_id가 없으면 중복 방지가 불가능하므로 전송 자체를 skip한다.
    """
    if not _upload_enabled():
        return {"status": "skipped", "reason": "opt_out"}

    # runtime-stats는 여기서 한 번만 읽어 build_payload까지 재사용 (중복 I/O 방지)
    stats = _load_runtime_stats(output_dir)
    session_id = stats.get("session_id")
    if not session_id:
        # session_id가 없으면 dedupe/마킹이 불가 → 무한 재전송을 막기 위해 skip
        return {"status": "skipped", "reason": "no_session_id"}
    if session_id in _uploaded_sessions(output_dir):
        return {"status": "skipped", "reason": "already_sent", "session_id": session_id}

    try:
        payload = build_payload(output_dir, stats=stats)
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            TELEMETRY_ENDPOINT,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            _mark_uploaded(output_dir, session_id)
            return {"status": "sent", "http_status": response.status, "payload": payload}
    except urllib.error.HTTPError as exc:
        return {"status": "error", "reason": f"http_{exc.code}"}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"status": "error", "reason": type(exc).__name__}
    except Exception as exc:  # never break finalize, but surface unexpected bugs
        # 네트워크 오류가 아닌 프로그래밍 결함(payload 구성 등)이 조용히 묻히지
        # 않도록 stderr로 경고. finalize는 계속 진행한다.
        print(
            f"[telemetry] unexpected upload error (ignored): {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return {"status": "error", "reason": f"unexpected:{type(exc).__name__}"}
