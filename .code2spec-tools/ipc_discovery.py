#!/usr/bin/env python3
"""IPC Pattern Discovery — LLM-based IPC mechanism detection.

Uses the same 3-step pattern as other LLM extraction modules:
  1. collect_unmatched_calls() → gathers calls not matching static patterns
  2. build_ipc_discovery_prompt() → saves llm-prompt.md
  3. Cline LLM processes the prompt
  4. parse_ipc_discovery_response() → returns discovered IPC patterns
  5. apply_ipc_patterns() → updates patterns module at runtime

The discovered IPC patterns are merged with static patterns in patterns.py,
with LLM-discovered patterns taking precedence for the target codebase.
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

try:
    import tree_sitter_language_pack as tslp
except ImportError:
    tslp = None

try:
    from .patterns import (
        CALL_TYPES as _CALL_TYPES,
    )
    from .patterns import (
        IPC_PATTERNS as _STATIC_IPC_PATTERNS,
    )
    from .patterns import (
        get_extension_map as _get_extension_map,
    )
except ImportError:  # script/installed-tools flat execution
    from patterns import (
        CALL_TYPES as _CALL_TYPES,
    )
    from patterns import (
        IPC_PATTERNS as _STATIC_IPC_PATTERNS,
    )
    from patterns import (
        get_extension_map as _get_extension_map,
    )

logger = logging.getLogger(__name__)

# Maximum recursion depth for AST tree traversal — prevents stack overflow
# on deeply nested or malformed trees.
_MAX_AST_DEPTH = 200

# Directories never worth scanning for the target project's IPC calls.
# `.code2spec-tools`/`.code2spec-venv` are the installer's own payload: left in,
# they fill the (max_files-capped) sample with code2spec's internals and crowd
# out the project's real sources.
_SKIP_DIRS = frozenset({
    ".code2spec-tools", ".code2spec-venv", ".code-to-ast", ".git", ".hg", ".svn",
    "__pycache__", ".venv", "venv", "node_modules", "dist", "build", "target",
    ".next", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".tox",
})


def _ts_parse(parser, source_bytes: bytes):
    """Parse source bytes, tolerating both bytes-only and str-only bindings.

    tree-sitter >= 0.26 requires bytes or a callable; some language-pack builds
    still expose a str-only binding. Node offsets are byte offsets either way,
    so callers keep the original bytes around for text extraction.
    """
    try:
        return parser.parse(source_bytes)
    except TypeError as exc:
        if "bytes" not in str(exc) or "str" not in str(exc):
            raise
        return parser.parse(source_bytes.decode("utf-8", errors="replace"))


def _child_count(node) -> int:
    """Read ``child_count`` across the method (>=0.25) and property APIs."""
    attr = getattr(node, "child_count", 0)
    return attr() if callable(attr) else attr


# ---------------------------------------------------------------------------
# IPC Pattern Discovery
# ---------------------------------------------------------------------------

# _CALL_TYPES and _STATIC_IPC_PATTERNS are imported from .patterns — see that module for details.


def collect_unmatched_calls(
    source_dir: str,
    language: str,
    max_files: int = 20,
) -> tuple[list[str], int]:
    """Collect call expressions that don't match static IPC patterns.

    These unmatched calls may represent new IPC mechanisms not in the static patterns.

    Returns:
        (unmatched_call_names, files_scanned)
    """
    ext_map = _get_extension_map()
    ext = ext_map.get(language)
    if not ext:
        raise ValueError(f"Unknown language: {language}")

    if tslp is None:
        raise ImportError("tree_sitter_language_pack is required")

    parser = tslp.get_parser(language)
    call_types = set(_CALL_TYPES.get(language, []))
    static_patterns = _STATIC_IPC_PATTERNS.get(language, {})
    all_static_patterns = set()
    for patterns in static_patterns.values():
        all_static_patterns.update(p.lower() for p in patterns)

    unmatched_calls: set[str] = set()
    files_scanned = 0
    files_matched = 0
    files_failed = 0

    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for fname in files:
            if not fname.endswith(ext):
                continue
            files_matched += 1
            if files_scanned >= max_files:
                break
            fpath = os.path.join(root, fname)
            try:
                source = Path(fpath).read_bytes()
            except (OSError, PermissionError) as e:
                logger.warning("[ipc-discovery] Failed to read %s: %s", fpath, e)
                files_failed += 1
                continue

            try:
                tree = _ts_parse(parser, source)
            except Exception as e:
                # Warn, not debug: a systematic parse failure (wrong argument
                # type, ABI mismatch) otherwise looks like "no IPC found".
                logger.warning("[ipc-discovery] Failed to parse %s: %s", fpath, e)
                files_failed += 1
                continue

            # tree-sitter >= 0.25: root_node is a method
            ast_root = tree.root_node() if callable(tree.root_node) else tree.root_node
            _collect_unmatched_calls_recursive(
                ast_root, source, call_types, all_static_patterns, unmatched_calls,
            )
            files_scanned += 1

        if files_scanned >= max_files:
            break

    if files_matched == 0:
        logger.warning(
            "[ipc-discovery] No %s files (*%s) found under %s", language, ext, source_dir,
        )
    elif files_scanned == 0:
        logger.warning(
            "[ipc-discovery] Found %d %s file(s) under %s but all %d failed to read/parse "
            "— check tree-sitter compatibility",
            files_matched, language, source_dir, files_failed,
        )
    else:
        logger.info(
            "[ipc-discovery] Scanned %d/%d %s files (%d read/parse failures)",
            files_scanned, files_matched, language, files_failed,
        )

    return sorted(unmatched_calls), files_scanned


def _collect_unmatched_calls_recursive(
    node,
    source_bytes: bytes,
    call_types: set[str],
    static_patterns: set[str],
    unmatched: set[str],
    depth: int = 0,
) -> None:
    """Recursively walk AST and collect unmatched call names."""
    if depth > _MAX_AST_DEPTH:
        return

    # tree-sitter API: use kind() method to get node type
    try:
        node_type = node.kind()
    except (AttributeError, TypeError):
        node_type = getattr(node, 'type', None)

    if node_type in call_types:
        # Extract call name from the node
        call_name = _extract_call_name_from_node(node, source_bytes)
        if call_name:
            call_lower = call_name.lower()
            # Check if this call matches any static IPC pattern
            matches_static = any(pattern in call_lower for pattern in static_patterns)
            if not matches_static:
                unmatched.add(call_name)

    # Recurse into children
    for i in range(_child_count(node)):
        child = node.child(i)
        if child is not None:
            _collect_unmatched_calls_recursive(
                child, source_bytes, call_types, static_patterns, unmatched, depth + 1,
            )


def _extract_call_name_from_node(node, source_bytes: bytes) -> str | None:
    """Extract the call name from a call expression node.

    Offsets reported by tree-sitter are byte offsets, so the slice is taken
    from the raw bytes and decoded — slicing a decoded str would misalign on
    any non-ASCII source.
    """
    # language-pack Rust 바인딩 Node에는 children 속성이 없음 → child_count()/child(i) 사용
    if not _child_count(node):
        return None

    first = node.child(0)
    if first is None:
        return None
    # tree-sitter >= 0.25: node.kind() is the method; node.type doesn't exist.
    # Use callable(getattr(...)) pattern for consistent dual-API support.
    if callable(getattr(first, 'kind', None)):
        first_type = first.kind()
    else:
        first_type = getattr(first, 'type', None)

    if first_type == "identifier":
        start = first.start_byte() if callable(first.start_byte) else first.start_byte
        end = first.end_byte() if callable(first.end_byte) else first.end_byte
        return source_bytes[start:end].decode("utf-8", errors="replace")

    # Method call: obj.method()
    member_types = ("attribute", "member_expression", "field_expression")
    if first_type in member_types:
        # Get the rightmost identifier
        for i in range(_child_count(first) - 1, -1, -1):
            child = first.child(i)
            if callable(getattr(child, 'kind', None)):
                child_type = child.kind()
            else:
                child_type = getattr(child, 'type', None)
            if child_type in ("identifier", "property_identifier"):
                start = child.start_byte() if callable(child.start_byte) else child.start_byte
                end = child.end_byte() if callable(child.end_byte) else child.end_byte
                return source_bytes[start:end].decode("utf-8", errors="replace")

    return None


def build_ipc_discovery_prompt(
    language: str,
    unmatched_calls: list[str],
    files_scanned: int,
) -> str:
    """Build the LLM prompt for IPC pattern discovery.

    Args:
        language: Target language name
        unmatched_calls: List of call names that don't match static IPC patterns
        files_scanned: Number of source files scanned

    Returns:
        Prompt string to send to the LLM
    """
    calls_text = "\n".join(f"  - {c}" for c in unmatched_calls[:100])

    prompt = f"""# Task: IPC Pattern Discovery for {language.upper()}

## Context
You are a static analysis expert. The code2spec parser has identified the following call expressions
from {files_scanned} {language} source files that do NOT match any known IPC patterns.

Your task is to identify which of these calls represent IPC (Inter-Process Communication) mechanisms
and categorize them appropriately.

## Known IPC Mechanisms
The parser already knows these IPC mechanisms:
- socket, grpc, message_queue, pipe, shared_memory, signal
- binder, dbus, broadcast_receiver (Android)
- named_pipe, wcf (Windows)
- rmi (Java), xpc (macOS)
- http_client, subprocess
- app_control, message_port (Tizen)

## Unmatched Call Expressions
({len(unmatched_calls)} calls that don't match static patterns)

{calls_text}

## Your Task
For each call that represents IPC communication:
1. Identify the IPC mechanism type (use existing types or propose new ones)
2. Provide a brief rationale for your classification
3. Suggest the direction (incoming/outgoing/bidirectional)

## Output Format
You MUST output in the following YAML format:

```yaml
language: "{language}"
ipc_patterns:
  - call_name: "SomeClass.SomeMethod"
    ipc_mechanism: "binder"  # or propose new like "content_provider"
    direction: "outgoing"  # incoming/outgoing/bidirectional
    rationale: "This is an Android Binder call for cross-process communication"
```

## Rules
1. Only identify calls that are truly IPC (cross-process communication)
2. Regular function calls within the same process should NOT be marked as IPC
3. If you identify a new IPC mechanism not in the known list, explain why it's needed
4. Be conservative - when in doubt, don't classify as IPC
"""
    return prompt


def parse_ipc_discovery_response(response: str, language: str) -> list[dict]:
    """Parse the LLM's YAML response for IPC pattern discovery.

    Returns:
        List of dicts with call_name, ipc_mechanism, direction, rationale
    """
    import yaml

    yaml_match = re.search(r'```yaml\s*(.*?)\s*```', response, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
    else:
        yaml_content = response

    try:
        data = yaml.safe_load(yaml_content)
    except ImportError:
        # PyYAML not installed — use fallback parser
        data = _parse_ipc_yaml_fallback(yaml_content)
    except Exception as e:
        # Includes yaml.YAMLError for malformed YAML
        logger.warning("YAML parsing failed, using fallback parser: %s", e)
        data = _parse_ipc_yaml_fallback(yaml_content)

    patterns = []
    for p in data.get("ipc_patterns", []):
        patterns.append({
            "call_name": p.get("call_name", ""),
            "ipc_mechanism": p.get("ipc_mechanism", "unknown"),
            "direction": p.get("direction", "bidirectional"),
            "rationale": p.get("rationale", ""),
        })

    return patterns


def _parse_ipc_yaml_fallback(yaml_content: str) -> dict:
    """Simple regex-based YAML parser for IPC patterns."""
    patterns = []
    pattern = re.compile(
        r'-\s+call_name:\s*["\']?([^"\n]+)["\']?\s+'
        r'ipc_mechanism:\s*["\']?([^"\n]+)["\']?\s+'
        r'direction:\s*["\']?([^"\n]+)["\']?\s+'
        r'rationale:\s*["\']?([^"\n]+)["\']?',
        re.MULTILINE,
    )
    for match in pattern.finditer(yaml_content):
        patterns.append({
            "call_name": match.group(1).strip(),
            "ipc_mechanism": match.group(2).strip(),
            "direction": match.group(3).strip(),
            "rationale": match.group(4).strip(),
        })
    return {"ipc_patterns": patterns}


def apply_ipc_patterns(patterns: list[dict], language: str) -> None:
    """Apply discovered IPC patterns to the parser's patterns module.

    This updates the _IPC_PATTERNS dict and IpcMechanism._discovered_mechanisms.
    Note: This is a runtime update; for persistence, save to a config file.
    """
    try:
        from .patterns import IPC_PATTERNS, IpcMechanism
    except ImportError:
        from patterns import IPC_PATTERNS, IpcMechanism

    for p in patterns:
        call_name = p["call_name"]
        mechanism = p["ipc_mechanism"]

        # Add new mechanism to IpcMechanism if not exists
        if not IpcMechanism.is_valid_mechanism(mechanism):
            IpcMechanism.add_discovered_mechanism(mechanism, mechanism)

        # Add pattern to IPC_PATTERNS
        if language not in IPC_PATTERNS:
            IPC_PATTERNS[language] = {}
        if mechanism not in IPC_PATTERNS[language]:
            IPC_PATTERNS[language][mechanism] = []
        if call_name not in IPC_PATTERNS[language][mechanism]:
            IPC_PATTERNS[language][mechanism].append(call_name)

    print(f"[ipc-discovery] Applied {len(patterns)} IPC patterns for {language}")


# ---------------------------------------------------------------------------
# Main discovery flow
# ---------------------------------------------------------------------------

class IPCDiscovery:
    """Orchestrates the 3-step IPC pattern discovery process."""

    def __init__(self, source_dir: str, output_dir: str, language: str):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.language = language
        self._unmatched_calls: list[str] = []
        self._files_scanned: int = 0

    def step1_collect(self, max_files: int = 20) -> tuple[list[str], int]:
        """Step 1: Collect unmatched IPC calls from source code."""
        self._unmatched_calls, self._files_scanned = collect_unmatched_calls(
            self.source_dir, self.language, max_files,
        )
        print(f"[ipc-discovery] Collected {len(self._unmatched_calls)} unmatched calls "
              f"from {self._files_scanned} {self.language} files")
        return self._unmatched_calls, self._files_scanned

    def step2_generate_prompt(self) -> str:
        """Step 2: Generate the LLM prompt and save to file."""
        if not self._unmatched_calls:
            self.step1_collect()

        prompt = build_ipc_discovery_prompt(
            self.language, self._unmatched_calls, self._files_scanned,
        )

        os.makedirs(self.output_dir, exist_ok=True)
        prompt_path = os.path.join(self.output_dir, "llm-prompt.md")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)

        print(f"[ipc-discovery] Prompt saved to: {prompt_path}")
        return prompt

    def step3_apply(self, llm_response_path: str) -> list[dict]:
        """Step 3: Process LLM response and apply discovered patterns."""
        if not os.path.exists(llm_response_path):
            raise FileNotFoundError(f"LLM response file not found: {llm_response_path}")

        with open(llm_response_path, encoding="utf-8") as f:
            llm_response = f.read()

        patterns = parse_ipc_discovery_response(llm_response, self.language)
        apply_ipc_patterns(patterns, self.language)

        # Save discovered patterns to JSON
        import json
        patterns_path = os.path.join(self.output_dir, "discovered-ipc-patterns.json")
        with open(patterns_path, "w", encoding="utf-8") as f:
            json.dump({
                "language": self.language,
                "patterns": patterns,
            }, f, indent=2, ensure_ascii=False)

        print(f"[ipc-discovery] Applied patterns saved to: {patterns_path}")
        return patterns
