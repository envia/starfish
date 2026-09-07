#!/usr/bin/env python3
"""IPC Pattern Discovery — LLM-based IPC mechanism detection.

Note: Type discovery (AST node type categorization) was removed.
This module now only contains IPC pattern discovery functions.
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

# Maximum recursion depth for AST tree traversal
_MAX_AST_DEPTH = 200

try:
    from .ipc_discovery import _SKIP_DIRS, _child_count, _ts_parse
except ImportError:  # script/installed-tools flat execution
    from ipc_discovery import _SKIP_DIRS, _child_count, _ts_parse


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
            f"[ipc-discovery] No {language} files (*{ext}) found in {source_dir}"
        )
    elif files_scanned == 0:
        logger.warning(
            f"[ipc-discovery] Found {files_matched} {language} file(s) in {source_dir} "
            f"but all {files_failed} failed to parse. Check tree-sitter compatibility."
        )
    else:
        logger.info(
            f"[ipc-discovery] Scanned {files_scanned}/{files_matched} {language} files "
            f"({files_failed} parse failures)"
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

    tree-sitter reports byte offsets, so slices come from the raw bytes and are
    decoded afterwards — slicing a decoded str misaligns on non-ASCII source.
    """
    # language-pack Rust 바인딩 Node에는 children 속성이 없음 → child_count()/child(i) 사용
    if not _child_count(node):
        return None

    first = node.child(0)
    if first is None:
        return None
    # tree-sitter >= 0.25: node.kind() is the method
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
    """Apply discovered IPC patterns to the parser's IpcMechanism class.

    This updates the _IPC_PATTERNS dict and IpcMechanism._discovered_mechanisms.
    Note: This is a runtime update; for persistence, save to a config file.
    """
    try:
        from .parser import _IPC_PATTERNS, IpcMechanism
    except ImportError:
        from parser import _IPC_PATTERNS, IpcMechanism

    for p in patterns:
        call_name = p["call_name"]
        mechanism = p["ipc_mechanism"]

        # Add new mechanism to IpcMechanism if not exists
        if not IpcMechanism.is_valid_mechanism(mechanism):
            IpcMechanism.add_discovered_mechanism(mechanism, mechanism)

        # Add pattern to _IPC_PATTERNS
        if language not in _IPC_PATTERNS:
            _IPC_PATTERNS[language] = {}
        if mechanism not in _IPC_PATTERNS[language]:
            _IPC_PATTERNS[language][mechanism] = []
        if call_name not in _IPC_PATTERNS[language][mechanism]:
            _IPC_PATTERNS[language][mechanism].append(call_name)

    print(f"[ipc-discovery] Applied {len(patterns)} IPC patterns for {language}")
