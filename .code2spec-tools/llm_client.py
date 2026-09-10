"""
LLM Client for Cline Integration.

Token-efficient pipeline: AST → Filter → Semantic Markdown → Single LLM call.

Instead of dumping raw AST JSON (which wastes tokens on redundant keys, quotes,
braces), we:
1. Detect languages from file extensions
2. Filter only relevant nodes per extraction type (enum/constant/ipc)
3. Convert to compact Semantic Markdown (LLMs are pre-trained on it)
4. Send a single prompt per extraction type (no chunking)

This saves  tokens vs raw JSON and avoids multiple LLM calls.
"""

import logging
from collections import defaultdict
from typing import Any

# Libraries should not configure the root logger — only the application
# entry point (e.g. cli.py) should call logging.basicConfig().
logger = logging.getLogger(__name__)


# Language detection, node kind filtering, and name patterns are imported
# from .patterns — see that module for details.
try:
    from .patterns import (
        CONSTANT_NAME_PATTERNS,
        ENUM_KINDS,
        ENUM_NAME_PATTERNS,
        IPC_NAME_PATTERNS,
        parse_json_from_markdown,
    )
    from .patterns import (
        get_language_from_extension as _get_language,
    )
except ImportError:  # script/installed-tools flat execution
    from patterns import (
        CONSTANT_NAME_PATTERNS,
        ENUM_KINDS,
        ENUM_NAME_PATTERNS,
        IPC_NAME_PATTERNS,
        parse_json_from_markdown,
    )
    from patterns import (
        get_language_from_extension as _get_language,
    )


def _detect_languages(nodes: list) -> dict:
    """Detect languages and count files per language."""
    lang_files: dict[str, set] = defaultdict(set)
    for node in nodes:
        fp = node.get("file_path", "") or node.get("file", "")
        if fp:
            lang = _get_language(fp)
            if lang != "unknown":
                lang_files[lang].add(fp)
    return {lang: len(files) for lang, files in lang_files.items()}


# ── Node filtering ──────────────────────────────────────────────────────────

def _filter_enum_nodes(nodes: list) -> list:
    """Filter nodes relevant to ENUM extraction.

    Uses stricter filtering to avoid matching every class with values.
    A node is considered an enum if it meets ONE of:
    1. Kind is specifically an enum type (enum_declaration, enum_class, etc.)
    2. Name matches enum patterns (ends with Enum, Mode, State, etc.)
    3. Has IntDef annotation (Android @IntDef)
    4. Is a Class/Type with explicit enum-like values in extra
    """
    relevant = []
    for node in nodes:
        kind = node.get("kind", "")
        name = node.get("name", "")
        extra = node.get("extra", {})

        # Match by specific enum kind (not just any class)
        if kind in ENUM_KINDS:
            relevant.append(node)
            continue

        # Match by name pattern (ends with Enum, Mode, State, Status, etc.)
        if name and ENUM_NAME_PATTERNS.search(name):
            relevant.append(node)
            continue

        # Match by IntDef in extra (check specific key, not entire dict as string)
        if extra.get("IntDef") or extra.get("intdef"):
            relevant.append(node)
            continue

        # Match by values in extra (enum-like) - only for actual enum classes
        values = extra.get("values")
        if isinstance(values, list) and len(values) > 0:
            # Only match if kind indicates enum-like structure
            if kind in ("enum_declaration", "enum_class", "enum_class_declaration"):
                relevant.append(node)
                continue
            # Also match if has enum-specific extra fields
            if extra.get("underlying_type") or extra.get("enum_type"):
                relevant.append(node)
                continue

    return relevant


def _filter_constant_nodes(nodes: list) -> list:
    """Filter nodes relevant to constant extraction.

    Uses stricter filtering to avoid matching every field declaration.
    A node is considered a constant if it meets ONE of:
    1. Kind is specifically "constant_declaration" (not just "field_declaration")
    2. Name matches UPPER_SNAKE_CASE pattern AND has modifiers like static/final
    3. Has explicit constant_value or is_constant in extra
    """
    relevant = []
    for node in nodes:
        kind = node.get("kind", "")
        name = node.get("name", "")
        extra = node.get("extra", {})
        modifiers = node.get("modifiers", "") or ""
        mod_lower = modifiers.lower()

        # Match by specific constant_declaration kind (not generic field_declaration)
        if kind == "constant_declaration":
            relevant.append(node)
            continue

        # Match by name pattern (UPPER_SNAKE_CASE or error code) - this catches static final fields
        if name and CONSTANT_NAME_PATTERNS.search(name):
            relevant.append(node)
            continue

        # Match by strict modifiers (must have BOTH static AND final for Java, or const/constexpr)
        if "static final" in mod_lower or "const " in mod_lower or "constexpr" in mod_lower:
            relevant.append(node)
            continue

        # Match by extra indicating constant
        if extra.get("is_constant") or extra.get("constant_value") is not None:
            relevant.append(node)
            continue

    return relevant


def _filter_ipc_nodes(nodes: list, edges: list) -> list:
    """Filter nodes relevant to IPC extraction."""
    # Collect nodes referenced by IPC edges
    ipc_sources = set()
    for edge in edges:
        if edge.get("kind") == "IPC":
            ipc_sources.add(edge.get("source", ""))
            ipc_sources.add(edge.get("target", ""))

    relevant = []
    for node in nodes:
        node.get("kind", "")
        name = node.get("name", "")
        extra = node.get("extra", {})

        # Match by IPC edge reference
        node_id = f"{node.get('file_path', '')}::{name}"
        if node_id in ipc_sources or name in ipc_sources:
            relevant.append(node)
            continue

        # Match by name pattern
        if name and IPC_NAME_PATTERNS.search(name):
            relevant.append(node)
            continue

        # Match by extends/implements IPC-related
        extends = str(extra.get("extends", "")) or str(node.get("parent_name", ""))
        if extends and IPC_NAME_PATTERNS.search(extends):
            relevant.append(node)
            continue

        # Match by IPC mechanism in extra
        if extra.get("ipc_mechanism"):
            relevant.append(node)
            continue

    return relevant


# ── Semantic Markdown conversion ─────────────────────────────────────────────

def _node_to_enum_markdown(node: dict) -> str:
    """Convert a single node to compact enum markdown line."""
    name = node.get("name", "?")
    lang = _get_language(node.get("file_path", ""))
    fp = node.get("file_path", "")
    line = node.get("line_start", 0)
    extra = node.get("extra", {})
    values = extra.get("values", [])
    underlying = extra.get("underlying_type", "")
    modifiers = node.get("modifiers", "")

    # Compact: [lang] Name | values | file:line
    # Parser stores enum values as dict {name: value}, not list
    if isinstance(values, dict):
        val_str = ", ".join(f"{k}={v}" for k, v in list(values.items())[:20]) if values else "?"
    else:
        val_str = ", ".join(str(v) for v in values[:20]) if values else "?"
    parts = [f"[{lang}] {name}"]
    if modifiers:
        parts.append(f"({modifiers})")
    parts.append(f"| {val_str}")
    if underlying:
        parts.append(f"| type: {underlying}")
    parts.append(f"| {fp}:{line}")
    return " ".join(parts)


def _node_to_constant_markdown(node: dict) -> str:
    """Convert a single node to compact constant markdown line."""
    name = node.get("name", "?")
    lang = _get_language(node.get("file_path", ""))
    fp = node.get("file_path", "")
    line = node.get("line_start", 0)
    extra = node.get("extra", {})
    value = extra.get("constant_value", extra.get("value", ""))
    modifiers = node.get("modifiers", "")
    data_type = extra.get("data_type", node.get("return_type", ""))

    # Compact: [lang] NAME = value | modifiers | file:line
    parts = [f"[{lang}] {name}"]
    if value:
        parts.append(f"= {value}")
    if modifiers:
        parts.append(f"({modifiers})")
    if data_type:
        parts.append(f": {data_type}")
    parts.append(f"| {fp}:{line}")
    return " ".join(parts)


def _node_to_ipc_markdown(node: dict) -> str:
    """Convert a single node to compact IPC markdown line."""
    name = node.get("name", "?")
    kind = node.get("kind", "")
    lang = _get_language(node.get("file_path", ""))
    fp = node.get("file_path", "")
    line = node.get("line_start", 0)
    extra = node.get("extra", {})
    mechanism = extra.get("ipc_mechanism", "")
    extends = extra.get("extends", "")
    params = node.get("params", "")
    return_type = node.get("return_type", "")

    # Compact: [lang] mechanism - Name | details | file:line
    parts = [f"[{lang}]"]
    if mechanism:
        parts.append(f"{mechanism} -")
    elif kind:
        parts.append(f"{kind} -")
    parts.append(name)
    if extends:
        parts.append(f"extends {extends}")
    if params:
        parts.append(f"| sig: {params}")
        if return_type:
            parts.append(f"→ {return_type}")
    parts.append(f"| {fp}:{line}")
    return " ".join(parts)


def _ipc_edges_to_markdown(edges: list) -> str:
    """Convert IPC edges to compact markdown."""
    ipc_edges = [e for e in edges if e.get("kind") == "IPC"]
    if not ipc_edges:
        return ""
    lines = ["### IPC Edges"]
    for edge in ipc_edges:
        src = edge.get("source", "?")
        tgt = edge.get("target", "?")
        extra = edge.get("extra", {})
        mechanism = extra.get("ipc_mechanism", "")
        data = extra.get("data", "")
        parts = [f"- {src} → {tgt}"]
        if mechanism:
            parts.append(f"[{mechanism}]")
        if data:
            parts.append(f"| {data}")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def ast_to_semantic_markdown(ast_json: dict, extraction_type: str) -> str:
    """
    Convert AST JSON to compact Semantic Markdown for LLM consumption.

    This is the core token-saving transformation:
    - Detects languages automatically
    - Filters only relevant nodes
    - Converts to markdown (LLMs are pre-trained on it)
    - Each node becomes a single compact line

    Args:
        ast_json: AST dictionary with 'nodes' and 'edges'
        extraction_type: 'enum', 'constant', or 'ipc'

    Returns:
        Compact semantic markdown string
    """
    nodes = ast_json.get("nodes", [])
    edges = ast_json.get("edges", [])

    # Step 1: Detect languages
    languages = _detect_languages(nodes)

    # Step 2: Filter relevant nodes
    if extraction_type == "enum":
        relevant = _filter_enum_nodes(nodes)
    elif extraction_type == "constant":
        relevant = _filter_constant_nodes(nodes)
    elif extraction_type == "ipc":
        relevant = _filter_ipc_nodes(nodes, edges)
    else:
        relevant = nodes

    # Step 3: Build semantic markdown
    lines = []

    # Language header
    lang_parts = [f"{lang} ({count})" for lang, count in sorted(languages.items())]
    lines.append(f"# Languages: {', '.join(lang_parts)}")
    lines.append("")

    # Relevant nodes
    if extraction_type == "enum":
        lines.append("## Enum Definitions")
        for node in relevant:
            lines.append("- " + _node_to_enum_markdown(node))
    elif extraction_type == "constant":
        lines.append("## Constant Definitions")
        for node in relevant:
            lines.append("- " + _node_to_constant_markdown(node))
    elif extraction_type == "ipc":
        lines.append("## IPC Patterns")
        for node in relevant:
            lines.append("- " + _node_to_ipc_markdown(node))
        # Add IPC edges
        ipc_md = _ipc_edges_to_markdown(edges)
        if ipc_md:
            lines.append("")
            lines.append(ipc_md)

    lines.append("")
    lines.append(f"<!-- Total: {len(nodes)} nodes, {len(relevant)} relevant -->")

    logger.info(
        f"Converted AST to semantic markdown for {extraction_type}: "
        f"{len(nodes)} → {len(relevant)} nodes, "
        f"languages: {list(languages.keys())}"
    )

    return "\n".join(lines)


# ── LLMClient ───────────────────────────────────────────────────────────────

class LLMClient:
    """
    LLM Client for Cline integration.

    Token-efficient pipeline: AST → Filter → Semantic Markdown → Single LLM call.
    No chunking. No raw JSON. Compact markdown that LLMs natively understand.
    """

    def __init__(self, max_context_size: int = 80000):
        """
        Initialize the LLM Client for Cline.

        Args:
            max_context_size: Maximum characters for the AST data section.
                             If compact data exceeds this, it will be truncated
                             with a warning instead of chunked.
        """
        self.max_context_size = max_context_size
        logger.info(f"LLMClient initialized for Cline (max_context_size: {max_context_size})")

    def format_prompt_with_ast(self, prompt_template: str, ast_json: dict, extraction_type: str = "enum") -> str:
        """
        Format prompt template with semantic markdown for a single LLM call.

        Converts AST to compact semantic markdown, then inserts into the
        prompt template. Single call, no chunking.

        Args:
            prompt_template: The prompt template with {ast_json} placeholder
            ast_json: AST dictionary to include
            extraction_type: 'enum', 'constant', or 'ipc'

        Returns:
            Single formatted prompt string
        """
        # Convert AST to semantic markdown
        markdown = ast_to_semantic_markdown(ast_json, extraction_type)

        # Truncate if needed (instead of chunking)
        # Reserve ~10% of context for the prompt template text
        max_markdown_size = int(self.max_context_size * 0.9)

        if len(markdown) > max_markdown_size:
            logger.warning(
                f"Semantic markdown ({len(markdown)} chars) exceeds max context "
                f"({max_markdown_size}, reserved from {self.max_context_size}). Truncating."
            )
            # Keep language header and as many nodes as fit
            lines = markdown.split("\n")
            header_lines = []
            node_lines = []
            in_header = True
            for line in lines:
                if in_header and not line.startswith("- "):
                    header_lines.append(line)
                else:
                    in_header = False
                    node_lines.append(line)

            # Fit as many node lines as possible
            header_str = "\n".join(header_lines) + "\n"
            available = max_markdown_size - len(header_str) - 100
            fitted_lines = []
            current_size = 0
            for line in node_lines:
                if current_size + len(line) + 1 > available:
                    break
                fitted_lines.append(line)
                current_size += len(line) + 1

            markdown = header_str + "\n".join(fitted_lines)
            markdown += f"\n\n<!-- Truncated: showing {len(fitted_lines)} of {len(node_lines)} relevant nodes -->"

        # Format the prompt
        prompt = prompt_template.replace('{ast_json}', markdown)

        logger.info(
            f"Formatted single prompt for {extraction_type}: "
            f"{len(prompt)} chars, markdown: {len(markdown)} chars"
        )

        return prompt

    def generate(self, prompt: str) -> str:
        """
        Generate a response using Cline's LLM.

        Design intent: In the code2spec pipeline, Cline IS the LLM at runtime.
        This method prepares the prompt for Cline's conversation context.
        The actual LLM generation happens when Cline processes the prompt
        in its conversation — not via a direct API call here.

        IMPORTANT: This stub returns the prompt verbatim. Callers that need
        a real LLM response (e.g. hybrid-auto gap-fill) MUST check whether
        the response differs from the prompt. If response == prompt, no
        real LLM was connected and the result should be treated as empty.
        """
        logger.info(f"Prompt prepared for Cline LLM ({len(prompt)} characters)")
        logger.warning(
            "LLMClient.generate() is a stub — it returns the prompt verbatim. "
            "No real LLM backend is connected. Gap-fill results will be empty."
        )
        return prompt

    def stream(self, prompt: str):
        """
        Stream a response using Cline's LLM with progress callbacks.

        Design intent: Same as generate() — Cline is the LLM at runtime.
        This stub yields the prompt back as a single chunk. Callers should
        check if the yielded response equals the prompt (indicating no real
        LLM is connected) and treat it as an empty response.

        Args:
            prompt: The prompt to send to the LLM

        Yields:
            Response chunks (strings)
        """
        logger.warning(
            "LLMClient.stream() is a stub — it yields the prompt verbatim. "
            "No real LLM backend is connected."
        )
        response = self.generate(prompt)
        yield response


    def complete(self, prompt: str) -> str:
        """
        Complete generation with progress tracking.
        Alias for generate() for compatibility.
        """
        return self.generate(prompt)

    def generate_json(self, prompt: str) -> str:
        """
        Generate a JSON response using Cline's LLM.

        The actual LLM generation happens through Cline's conversation.
        """
        json_instruction = "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no explanations, just the JSON array/object."
        full_prompt = prompt + json_instruction
        logger.info(f"JSON prompt prepared for Cline LLM ({len(full_prompt)} characters)")
        return full_prompt

    def parse_extraction_response(self, response: str, expected_type: str = 'list') -> Any:
        """
        Parse Cline's response to extract structured data.

        Uses the shared ``parse_json_from_markdown`` utility from patterns.py
        for consistent JSON extraction across all modules.

        Args:
            response: Raw response string from Cline
            expected_type: Expected type ('list' or 'dict')

        Returns:
            Parsed Python object (list or dict)
        """
        if not response:
            logger.error("Empty response received")
            return [] if expected_type == 'list' else {}

        parsed = parse_json_from_markdown(response)

        if parsed is not None:
            return parsed

        logger.error(f"Failed to parse response as JSON: {response[:200]}...")
        return [] if expected_type == 'list' else {}


# ── Helper functions ────────────────────────────────────────────────────────

def prepare_enum_extraction_prompt(ast_json: dict, template: str) -> str:
    """Prepare ENUM extraction prompt for Cline (single call)."""
    client = LLMClient()
    return client.format_prompt_with_ast(template, ast_json, extraction_type="enum")


def prepare_constant_extraction_prompt(ast_json: dict, template: str) -> str:
    """Prepare constant extraction prompt for Cline (single call)."""
    client = LLMClient()
    return client.format_prompt_with_ast(template, ast_json, extraction_type="constant")


def prepare_ipc_extraction_prompt(ast_json: dict, template: str) -> str:
    """Prepare IPC extraction prompt for Cline (single call)."""
    client = LLMClient()
    return client.format_prompt_with_ast(template, ast_json, extraction_type="ipc")
