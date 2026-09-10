"""Tree-sitter based multi-language code parser.

Extracts structural nodes (classes, functions, imports, types) and edges
(calls, inheritance, contains) from source files.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import tree_sitter_language_pack as tslp

try:
    from .patterns import (
        CALL_TYPES as _CALL_TYPES,
    )
    from .patterns import (
        CLASS_TYPES as _CLASS_TYPES,
    )
    from .patterns import (
        CONSTANT_TYPES as _CONSTANT_TYPES,
    )
    from .patterns import (
        ENUM_TYPES as _ENUM_TYPES,
    )
    from .patterns import (
        EXTENSION_TO_LANGUAGE,
        IpcMechanism,
    )
    from .patterns import (
        FUNCTION_TYPES as _FUNCTION_TYPES,
    )
    from .patterns import (
        IMPORT_TYPES as _IMPORT_TYPES,
    )
    from .patterns import (
        IPC_PATTERNS as _IPC_PATTERNS,
    )
    from .patterns import (
        is_test_file as _is_test_file,
    )
    from .patterns import (
        is_test_function as _is_test_function,
    )
except ImportError:  # script/installed-tools flat execution
    from patterns import (
        CALL_TYPES as _CALL_TYPES,
    )
    from patterns import (
        CLASS_TYPES as _CLASS_TYPES,
    )
    from patterns import (
        CONSTANT_TYPES as _CONSTANT_TYPES,
    )
    from patterns import (
        ENUM_TYPES as _ENUM_TYPES,
    )
    from patterns import (
        EXTENSION_TO_LANGUAGE,
        IpcMechanism,
    )
    from patterns import (
        FUNCTION_TYPES as _FUNCTION_TYPES,
    )
    from patterns import (
        IMPORT_TYPES as _IMPORT_TYPES,
    )
    from patterns import (
        IPC_PATTERNS as _IPC_PATTERNS,
    )
    from patterns import (
        is_test_file as _is_test_file,
    )
    from patterns import (
        is_test_function as _is_test_function,
    )

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tree-sitter API compatibility layer
# ---------------------------------------------------------------------------
# tree-sitter 0.26 changed the API:
#   - parse() takes bytes or a callable
#   - Properties became methods (node.type → node.kind(), etc.)
#   - node.text was removed; use source[byte_start:byte_end] instead
# This shim provides a uniform property-based API so the rest of parser.py
# can stay unchanged regardless of tree-sitter version.

def _ts_parse(parser, source_bytes: bytes):
    """Parse source bytes, returning a tree with a ``root_node`` property.

    tree-sitter 0.26 requires bytes or a callable. Keep the source as bytes
    throughout parsing so byte offsets stay aligned with node metadata.
    """
    try:
        tree = parser.parse(source_bytes)
    except TypeError as exc:
        # Some 0.26 language-pack parser builds expose a str-only binding.
        # Preserve byte-backed node text while adapting only the parse input.
        if "bytes" not in str(exc) or "str" not in str(exc):
            raise
        tree = parser.parse(source_bytes.decode("utf-8", errors="replace"))
    return _TreeShim(tree, source_bytes)


class _TreeShim:
    """Wraps a tree-sitter Tree so that ``root_node`` is a property."""

    def __init__(self, tree, source_bytes: bytes):
        self._tree = tree
        self._source = source_bytes

    @property
    def root_node(self):
        rn = self._tree.root_node
        return _NodeShim(rn(), self._source) if callable(rn) else rn


class _NodeShim:
    """Wraps a tree-sitter Node to expose the *old* property-based API.

    tree-sitter >= 0.25 renamed / removed several attributes:
      - ``node.type``       → ``node.kind()``
      - ``node.children``   → removed; use ``node.child_count()`` + ``node.child(i)``
      - ``node.start_point``→ ``node.start_position()``  (returns Point with .row/.column)
      - ``node.end_point``  → ``node.end_position()``
      - ``node.text``       → removed; reconstruct from source + byte offsets
      - All other attrs (child_count, start_byte, end_byte, is_named, …)
        became zero-argument methods.

    This wrapper restores the old property interface so that downstream code
    does not need to change.
    """

    __slots__ = ("_n", "_src")

    def __init__(self, node, source_bytes: bytes):
        self._n = node
        self._src = source_bytes

    # -- properties that were renamed or removed in the new API --------------

    @property
    def type(self):
        return self._n.kind()

    @property
    def children(self):
        return [_NodeShim(self._n.child(i), self._src)
                for i in range(self._n.child_count())]

    @property
    def start_point(self):
        p = self._n.start_position()
        return (p.row, p.column)

    @property
    def end_point(self):
        p = self._n.end_position()
        return (p.row, p.column)

    # -- properties that became methods in the new API -----------------------

    @property
    def child_count(self):
        return self._n.child_count()

    @property
    def start_byte(self):
        return self._n.start_byte()

    @property
    def end_byte(self):
        return self._n.end_byte()

    @property
    def is_named(self):
        return self._n.is_named()

    @property
    def is_error(self):
        return self._n.is_error()

    @property
    def is_extra(self):
        return self._n.is_extra()

    @property
    def is_missing(self):
        return self._n.is_missing()

    @property
    def has_error(self):
        return self._n.has_error()

    @property
    def parent(self):
        p = self._n.parent()
        return _NodeShim(p, self._src) if p is not None else None

    # -- text: reconstruct from source bytes + byte offsets ------------------

    @property
    def text(self):
        """Return the node's text as *bytes* (same as old tree-sitter API)."""
        return self._src[self.start_byte:self.end_byte]

    # -- methods that are still methods in both APIs -------------------------

    def child(self, idx):
        c = self._n.child(idx)
        return _NodeShim(c, self._src) if c is not None else None

    def child_by_field_name(self, name):
        c = self._n.child_by_field_name(name)
        return _NodeShim(c, self._src) if c is not None else None

    def named_child(self, idx):
        c = self._n.named_child(idx)
        return _NodeShim(c, self._src) if c is not None else None

    def walk(self):
        return self._n.walk()

    def to_sexp(self):
        return self._n.to_sexp()

    # -- dunder helpers ------------------------------------------------------

    def __len__(self):
        return self.child_count

    def __iter__(self):
        return iter(self.children)

    def __repr__(self):
        return f"_NodeShim({self.type!r})"


# ---------------------------------------------------------------------------
# Data models for extracted entities
# ---------------------------------------------------------------------------


@dataclass
class NodeInfo:
    kind: str  # File, Class, Function, Type, Test, Enum
    name: str
    file_path: str
    line_start: int
    line_end: int
    language: str = ""
    parent_name: str | None = None  # enclosing class/module
    params: str | None = None
    return_type: str | None = None
    modifiers: str | None = None
    is_test: bool = False
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize NodeInfo to a plain dict for JSON caching."""
        return {
            "kind": self.kind,
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "language": self.language,
            "parent_name": self.parent_name,
            "params": self.params,
            "return_type": self.return_type,
            "modifiers": self.modifiers,
            "is_test": self.is_test,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict) -> NodeInfo:
        """Deserialize NodeInfo from a plain dict (e.g. loaded from JSON)."""
        return cls(
            kind=data["kind"],
            name=data["name"],
            file_path=data["file_path"],
            line_start=data["line_start"],
            line_end=data["line_end"],
            language=data.get("language", ""),
            parent_name=data.get("parent_name"),
            params=data.get("params"),
            return_type=data.get("return_type"),
            modifiers=data.get("modifiers"),
            is_test=data.get("is_test", False),
            extra=data.get("extra", {}),
        )


@dataclass
class EdgeInfo:
    kind: str  # CALLS, IMPORTS_FROM, INHERITS, IMPLEMENTS, CONTAINS, TESTED_BY, DEPENDS_ON, IPC
    source: str  # qualified name or path
    target: str  # qualified name or path
    file_path: str
    line: int = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize EdgeInfo to a plain dict for JSON caching."""
        return {
            "kind": self.kind,
            "source": self.source,
            "target": self.target,
            "file_path": self.file_path,
            "line": self.line,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict) -> EdgeInfo:
        """Deserialize EdgeInfo from a plain dict (e.g. loaded from JSON)."""
        return cls(
            kind=data["kind"],
            source=data["source"],
            target=data["target"],
            file_path=data["file_path"],
            line=data.get("line", 0),
            extra=data.get("extra", {}),
        )


# All pattern definitions (IpcMechanism, EXTENSION_TO_LANGUAGE, _CLASS_TYPES,
# _FUNCTION_TYPES, _IMPORT_TYPES, _CALL_TYPES, _ENUM_TYPES, _CONSTANT_TYPES,
# _IPC_PATTERNS, _TEST_PATTERNS, _TEST_FILE_PATTERNS, _is_test_file,
# _is_test_function) are imported from .patterns — see that module for details.


def file_hash(path: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class CodeParser:
    """Parses source files using Tree-sitter and extracts structural information."""

    _MODULE_CACHE_MAX = 15_000  # Evict cache to cap memory on huge monorepos

    def __init__(self) -> None:
        self._parsers: dict[str, object] = {}
        self._module_file_cache: dict[str, str | None] = {}

    def _get_type_set(self, language: str, category: str) -> set[str]:
        """Get type set for a language+category from static patterns.

        Args:
            language: e.g. "java", "python"
            category: one of "class", "function", "enum", "constant", "import", "call"

        Returns:
            Set of AST node type strings to match against.
        """
        # Map category name to the static dictionary variable
        static_map: dict[str, dict[str, list[str]]] = {
            "class": _CLASS_TYPES,
            "function": _FUNCTION_TYPES,
            "enum": _ENUM_TYPES,
            "constant": _CONSTANT_TYPES,
            "import": _IMPORT_TYPES,
            "call": _CALL_TYPES,
        }

        static_dict = static_map.get(category, {})
        return set(static_dict.get(language, []))

    def _get_parser(self, language: str):  # type: ignore[arg-type]
        if language not in self._parsers:
            try:
                self._parsers[language] = tslp.get_parser(language)  # type: ignore[arg-type]
            except Exception:
                return None
        return self._parsers[language]

    def detect_language(self, path: Path) -> str | None:
        return EXTENSION_TO_LANGUAGE.get(path.suffix.lower())

    def parse_file(self, path: Path) -> tuple[list[NodeInfo], list[EdgeInfo]]:
        """Parse a single file and return extracted nodes and edges."""
        try:
            source = path.read_bytes()
        except (OSError, PermissionError):
            return [], []
        return self.parse_bytes(path, source)

    def parse_bytes(self, path: Path, source: bytes) -> tuple[list[NodeInfo], list[EdgeInfo]]:
        """Parse pre-read bytes and return extracted nodes and edges.

        This avoids re-reading the file from disk, eliminating TOCTOU gaps
        when the caller has already read the bytes (e.g. for hashing).
        """
        language = self.detect_language(path)
        if not language:
            return [], []

        # Vue SFCs: parse with vue parser, then delegate script blocks to JS/TS
        if language == "vue":
            return self._parse_vue(path, source)

        parser = self._get_parser(language)
        if not parser:
            return [], []

        tree = _ts_parse(parser, source)
        nodes: list[NodeInfo] = []
        edges: list[EdgeInfo] = []
        file_path_str = str(path)

        # File node
        test_file = _is_test_file(file_path_str)
        nodes.append(NodeInfo(
            kind="File",
            name=file_path_str,
            file_path=file_path_str,
            line_start=1,
            line_end=source.count(b"\n") + 1,
            language=language,
            is_test=test_file,
        ))

        # Pre-scan for import mappings and defined names
        import_map, defined_names = self._collect_file_scope(
            tree.root_node, language, source,
        )

        # Walk the tree
        self._extract_from_tree(
            tree.root_node, source, language, file_path_str, nodes, edges,
            import_map=import_map, defined_names=defined_names,
        )

        # Resolve bare call targets to qualified names using same-file definitions
        edges = self._resolve_call_targets(nodes, edges, file_path_str)

        # Generate TESTED_BY edges: when a test function calls a production
        # function, create an edge from the production function back to the test.
        if test_file:
            test_qnames = set()
            for n in nodes:
                if n.is_test:
                    qn = self._qualify(n.name, n.file_path, n.parent_name)
                    test_qnames.add(qn)
            for edge in list(edges):
                if edge.kind == "CALLS" and edge.source in test_qnames:
                    edges.append(EdgeInfo(
                        kind="TESTED_BY",
                        source=edge.target,
                        target=edge.source,
                        file_path=edge.file_path,
                        line=edge.line,
                    ))

        return nodes, edges

    def _parse_vue(
        self, path: Path, source: bytes,
    ) -> tuple[list[NodeInfo], list[EdgeInfo]]:
        """Parse a Vue SFC by extracting <script> blocks and delegating to JS/TS."""
        vue_parser = self._get_parser("vue")
        if not vue_parser:
            return [], []

        tree = _ts_parse(vue_parser, source)
        file_path_str = str(path)
        test_file = _is_test_file(file_path_str)

        all_nodes: list[NodeInfo] = [NodeInfo(
            kind="File",
            name=file_path_str,
            file_path=file_path_str,
            line_start=1,
            line_end=source.count(b"\n") + 1,
            language="vue",
            is_test=test_file,
        )]
        all_edges: list[EdgeInfo] = []

        # Find script_element blocks in the Vue AST
        for child in tree.root_node.children:
            if child.type != "script_element":
                continue

            # Detect language from lang="ts" attribute
            script_lang = "javascript"
            start_tag = None
            raw_text_node = None
            for sub in child.children:
                if sub.type == "start_tag":
                    start_tag = sub
                elif sub.type == "raw_text":
                    raw_text_node = sub

            if start_tag:
                for attr in start_tag.children:
                    if attr.type == "attribute":
                        attr_name = None
                        attr_value = None
                        for a in attr.children:
                            if a.type == "attribute_name":
                                attr_name = a.text.decode("utf-8", errors="replace")
                            elif a.type == "quoted_attribute_value":
                                for v in a.children:
                                    if v.type == "attribute_value":
                                        attr_value = v.text.decode(
                                            "utf-8", errors="replace",
                                        )
                        if attr_name == "lang" and attr_value in ("ts", "typescript"):
                            script_lang = "typescript"

            if not raw_text_node:
                continue

            script_source = raw_text_node.text
            line_offset = raw_text_node.start_point[0]  # 0-based line of raw_text start

            # Parse the script block with the appropriate JS/TS parser
            script_parser = self._get_parser(script_lang)
            if not script_parser:
                continue

            script_tree = _ts_parse(script_parser, script_source)

            # Collect imports and defined names from the script block
            import_map, defined_names = self._collect_file_scope(
                script_tree.root_node, script_lang, script_source,
            )

            nodes: list[NodeInfo] = []
            edges: list[EdgeInfo] = []
            self._extract_from_tree(
                script_tree.root_node, script_source, script_lang,
                file_path_str, nodes, edges,
                import_map=import_map, defined_names=defined_names,
            )

            # Adjust line numbers to account for position within the .vue file
            for node in nodes:
                node.line_start += line_offset
                node.line_end += line_offset
                node.language = "vue"
            for edge in edges:
                edge.line += line_offset

            all_nodes.extend(nodes)
            all_edges.extend(edges)

        # Generate TESTED_BY edges
        if test_file:
            test_qnames = set()
            for n in all_nodes:
                if n.is_test:
                    qn = self._qualify(n.name, n.file_path, n.parent_name)
                    test_qnames.add(qn)
            for edge in list(all_edges):
                if edge.kind == "CALLS" and edge.source in test_qnames:
                    all_edges.append(EdgeInfo(
                        kind="TESTED_BY",
                        source=edge.target,
                        target=edge.source,
                        file_path=edge.file_path,
                        line=edge.line,
                    ))

        return all_nodes, all_edges

    def _resolve_call_targets(
        self,
        nodes: list[NodeInfo],
        edges: list[EdgeInfo],
        file_path: str,
    ) -> list[EdgeInfo]:
        """Resolve bare call targets to qualified names using same-file definitions.

        After parsing, CALLS edges store bare function names (e.g. ``FirebaseAuth``)
        as targets. This method builds a symbol table from the parsed nodes and
        qualifies any bare target that matches a local definition, so that
        ``callers_of`` / ``callees_of`` queries produce correct results.

        External calls (names not defined in this file) remain bare.
        """
        # Build symbol table: bare_name -> qualified_name
        symbols: dict[str, str] = {}
        for node in nodes:
            if node.kind in ("Function", "Class", "Type", "Test"):
                bare = node.name
                qualified = self._qualify(bare, file_path, node.parent_name)
                if bare not in symbols:
                    symbols[bare] = qualified

        resolved: list[EdgeInfo] = []
        for edge in edges:
            if edge.kind == "CALLS" and "::" not in edge.target:
                if edge.target in symbols:
                    edge = EdgeInfo(
                        kind=edge.kind,
                        source=edge.source,
                        target=symbols[edge.target],
                        file_path=edge.file_path,
                        line=edge.line,
                        extra=edge.extra,
                    )
            resolved.append(edge)
        return resolved

    _MAX_AST_DEPTH = 180  # Guard against pathologically nested source files

    def _extract_from_tree(
        self,
        root,
        source: bytes,
        language: str,
        file_path: str,
        nodes: list[NodeInfo],
        edges: list[EdgeInfo],
        enclosing_class: str | None = None,
        enclosing_func: str | None = None,
        import_map: dict[str, str] | None = None,
        defined_names: set[str] | None = None,
        _depth: int = 0,
    ) -> None:
        """Recursively walk the AST and extract nodes/edges."""
        if _depth > self._MAX_AST_DEPTH:
            return
        # Use _get_type_set to merge static defaults with LLM-discovered overrides
        class_types = self._get_type_set(language, "class")
        func_types = self._get_type_set(language, "function")
        import_types = self._get_type_set(language, "import")
        call_types = self._get_type_set(language, "call")
        enum_types = self._get_type_set(language, "enum")
        constant_types = self._get_type_set(language, "constant")

        for child in root.children:
            node_type = child.type

            # --- ENUMs (check BEFORE classes — enum_declaration may be in both) ---
            if node_type in enum_types:
                # Kotlin: class_declaration is in both _ENUM_TYPES and _CLASS_TYPES.
                # Only treat as enum if it has an enum_class_body child.
                if language == "kotlin" and node_type == "class_declaration":
                    has_enum_body = any(
                        sub.type == "enum_class_body" for sub in child.children
                    )
                    if not has_enum_body:
                        # Not an enum — fall through to class check below
                        pass
                    else:
                        enum_name = self._get_name(child, language, "enum")
                        if enum_name:
                            enum_values = self._extract_enum_values(child, language, source)
                            underlying_type = self._get_enum_type(child, language, source)
                            nodes.append(NodeInfo(
                                kind="Enum",
                                name=enum_name,
                                file_path=file_path,
                                line_start=child.start_point[0] + 1,
                                line_end=child.end_point[0] + 1,
                                language=language,
                                parent_name=enclosing_class,
                                extra={
                                    "values": enum_values,
                                    "underlying_type": underlying_type,
                                },
                            ))
                            container = (
                                self._qualify(enclosing_class, file_path, None)
                                if enclosing_class
                                else file_path
                            )
                            edges.append(EdgeInfo(
                                kind="CONTAINS",
                                source=container,
                                target=self._qualify(enum_name, file_path, enclosing_class),
                                file_path=file_path,
                                line=child.start_point[0] + 1,
                            ))
                            self._extract_from_tree(
                                child, source, language, file_path, nodes, edges,
                                enclosing_class=enclosing_class, enclosing_func=enclosing_func,
                                import_map=import_map, defined_names=defined_names,
                                _depth=_depth + 1,
                            )
                            continue
                else:
                    enum_name = self._get_name(child, language, "enum")
                    if enum_name:
                        enum_values = self._extract_enum_values(child, language, source)
                        underlying_type = self._get_enum_type(child, language, source)
                        nodes.append(NodeInfo(
                            kind="Enum",
                            name=enum_name,
                            file_path=file_path,
                            line_start=child.start_point[0] + 1,
                            line_end=child.end_point[0] + 1,
                            language=language,
                            parent_name=enclosing_class,
                            extra={
                                "values": enum_values,
                                "underlying_type": underlying_type,
                            },
                        ))
                        # CONTAINS edge
                        container = (
                            self._qualify(enclosing_class, file_path, None)
                            if enclosing_class
                            else file_path
                        )
                        edges.append(EdgeInfo(
                            kind="CONTAINS",
                            source=container,
                            target=self._qualify(enum_name, file_path, enclosing_class),
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                        ))
                        # Recurse into enum body for nested structures
                        self._extract_from_tree(
                            child, source, language, file_path, nodes, edges,
                            enclosing_class=enclosing_class, enclosing_func=enclosing_func,
                            import_map=import_map, defined_names=defined_names,
                            _depth=_depth + 1,
                        )
                        continue

            # --- Classes ---
            if node_type in class_types:
                name = self._get_name(child, language, "class")
                if name:
                    node = NodeInfo(
                        kind="Class",
                        name=name,
                        file_path=file_path,
                        line_start=child.start_point[0] + 1,
                        line_end=child.end_point[0] + 1,
                        language=language,
                        parent_name=enclosing_class,
                    )
                    nodes.append(node)

                    # CONTAINS edge
                    edges.append(EdgeInfo(
                        kind="CONTAINS",
                        source=file_path,
                        target=self._qualify(name, file_path, enclosing_class),
                        file_path=file_path,
                        line=child.start_point[0] + 1,
                    ))

                    # Inheritance edges
                    bases = self._get_bases(child, language, source)
                    for base in bases:
                        edges.append(EdgeInfo(
                            kind="INHERITS",
                            source=self._qualify(name, file_path, enclosing_class),
                            target=base,
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                        ))

                    # Recurse into class body
                    self._extract_from_tree(
                        child, source, language, file_path, nodes, edges,
                        enclosing_class=name, enclosing_func=None,
                        import_map=import_map, defined_names=defined_names,
                        _depth=_depth + 1,
                    )
                    continue

            # --- Functions ---
            if node_type in func_types:
                name = self._get_name(child, language, "function")
                if name:
                    is_test = _is_test_function(name, file_path)
                    kind = "Test" if is_test else "Function"
                    qualified = self._qualify(name, file_path, enclosing_class)
                    params = self._get_params(child, language, source)
                    ret_type = self._get_return_type(child, language, source)

                    node = NodeInfo(
                        kind=kind,
                        name=name,
                        file_path=file_path,
                        line_start=child.start_point[0] + 1,
                        line_end=child.end_point[0] + 1,
                        language=language,
                        parent_name=enclosing_class,
                        params=params,
                        return_type=ret_type,
                        is_test=is_test,
                    )
                    nodes.append(node)

                    # CONTAINS edge
                    container = (
                        self._qualify(enclosing_class, file_path, None)
                        if enclosing_class
                        else file_path
                    )
                    edges.append(EdgeInfo(
                        kind="CONTAINS",
                        source=container,
                        target=qualified,
                        file_path=file_path,
                        line=child.start_point[0] + 1,
                    ))

                    # Solidity: modifier invocations on functions → CALLS edges
                    if language == "solidity":
                        for sub in child.children:
                            if sub.type == "modifier_invocation":
                                for ident in sub.children:
                                    if ident.type == "identifier":
                                        edges.append(EdgeInfo(
                                            kind="CALLS",
                                            source=qualified,
                                            target=ident.text.decode(
                                                "utf-8", errors="replace",
                                            ),
                                            file_path=file_path,
                                            line=sub.start_point[0] + 1,
                                        ))
                                        break

                    # Recurse to find calls inside the function
                    self._extract_from_tree(
                        child, source, language, file_path, nodes, edges,
                        enclosing_class=enclosing_class, enclosing_func=name,
                        import_map=import_map, defined_names=defined_names,
                        _depth=_depth + 1,
                    )
                    continue

            # --- C/C++ function prototypes (headers: declarations with no body) ---
            # `function_definition` (above) only matches bodies; a public C API is
            # typically declared-only in a header, so without this those symbols
            # never appear as exports and cross-repo call resolution can't find them.
            # `enclosing_func is None` rules out the "most vexing parse": a local
            # variable direct-initialized with a constructor call
            # (`std::string s(arg);`) is syntactically identical to a prototype, but
            # only ever appears inside a function body — a real prototype never does.
            if (
                language in ("c", "cpp")
                and node_type == "declaration"
                and enclosing_func is None
                and self._is_c_function_prototype(child)
            ):
                name = self._get_name(child, language, "function")
                if name:
                    is_test = _is_test_function(name, file_path)
                    qualified = self._qualify(name, file_path, enclosing_class)
                    node = NodeInfo(
                        kind="Test" if is_test else "Function",
                        name=name,
                        file_path=file_path,
                        line_start=child.start_point[0] + 1,
                        line_end=child.end_point[0] + 1,
                        language=language,
                        parent_name=enclosing_class,
                        params=self._get_params(child, language, source),
                        return_type=self._get_return_type(child, language, source),
                        is_test=is_test,
                    )
                    nodes.append(node)
                    container = (
                        self._qualify(enclosing_class, file_path, None)
                        if enclosing_class
                        else file_path
                    )
                    edges.append(EdgeInfo(
                        kind="CONTAINS",
                        source=container,
                        target=qualified,
                        file_path=file_path,
                        line=child.start_point[0] + 1,
                    ))
                    continue

            # --- Imports ---
            if node_type in import_types:
                imports = self._extract_import(child, language, source)
                for imp_target in imports:
                    edges.append(EdgeInfo(
                        kind="IMPORTS_FROM",
                        source=file_path,
                        target=imp_target,
                        file_path=file_path,
                        line=child.start_point[0] + 1,
                    ))
                continue

            # --- Constants ---
            if node_type in constant_types:
                name = self._get_name(child, language, "constant")
                if name:
                    # Check if this is a constant (not just a variable)
                    is_constant = self._is_constant_node(child, language, source)
                    if is_constant:
                        value = self._extract_constant_value(child, language, source)
                        nodes.append(NodeInfo(
                            kind="Constant",
                            name=name,
                            file_path=file_path,
                            line_start=child.start_point[0] + 1,
                            line_end=child.end_point[0] + 1,
                            language=language,
                            parent_name=enclosing_class,
                            extra={"value": value},
                        ))
                        # CONTAINS edge
                        container = (
                            self._qualify(enclosing_class, file_path, None)
                            if enclosing_class
                            else file_path
                        )
                        edges.append(EdgeInfo(
                            kind="CONTAINS",
                            source=container,
                            target=self._qualify(name, file_path, enclosing_class),
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                        ))
                        continue

            # --- Calls (and IPC detection) ---
            if node_type in call_types:
                call_name = self._get_call_name(child, language, source)
                if call_name and enclosing_func:
                    caller = self._qualify(enclosing_func, file_path, enclosing_class)
                    target = self._resolve_call_target(
                        call_name, file_path, language,
                        import_map or {}, defined_names or set(),
                    )
                    edges.append(EdgeInfo(
                        kind="CALLS",
                        source=caller,
                        target=target,
                        file_path=file_path,
                        line=child.start_point[0] + 1,
                    ))

                    # --- IPC detection: check if this call is an IPC pattern ---
                    ipc_type = self._detect_ipc_type(call_name, language)
                    if ipc_type:
                        edges.append(EdgeInfo(
                            kind="IPC",
                            source=caller,
                            target=call_name,
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                            extra={
                                "ipc_mechanism": ipc_type,
                                "direction": self._detect_ipc_direction(call_name),
                            },
                        ))

            # --- Solidity-specific constructs ---
            if language == "solidity":
                # Emit statements: emit EventName(...) → CALLS edge
                if node_type == "emit_statement" and enclosing_func:
                    for sub in child.children:
                        if sub.type == "expression":
                            for ident in sub.children:
                                if ident.type == "identifier":
                                    caller = self._qualify(
                                        enclosing_func, file_path, enclosing_class,
                                    )
                                    edges.append(EdgeInfo(
                                        kind="CALLS",
                                        source=caller,
                                        target=ident.text.decode("utf-8", errors="replace"),
                                        file_path=file_path,
                                        line=child.start_point[0] + 1,
                                    ))

                # State variable declarations → Function nodes (public ones
                # auto-generate getters, and all are critical for reviews)
                if node_type == "state_variable_declaration" and enclosing_class:
                    var_name = None
                    var_visibility = None
                    var_mutability = None
                    var_type = None
                    for sub in child.children:
                        if sub.type == "identifier":
                            var_name = sub.text.decode("utf-8", errors="replace")
                        elif sub.type == "visibility":
                            var_visibility = sub.text.decode("utf-8", errors="replace")
                        elif sub.type == "type_name":
                            var_type = sub.text.decode("utf-8", errors="replace")
                        elif sub.type in ("constant", "immutable"):
                            var_mutability = sub.type
                    if var_name:
                        qualified = self._qualify(var_name, file_path, enclosing_class)
                        nodes.append(NodeInfo(
                            kind="Function",
                            name=var_name,
                            file_path=file_path,
                            line_start=child.start_point[0] + 1,
                            line_end=child.end_point[0] + 1,
                            language=language,
                            parent_name=enclosing_class,
                            return_type=var_type,
                            modifiers=var_visibility,
                            extra={
                                "solidity_kind": "state_variable",
                                "mutability": var_mutability,
                            },
                        ))
                        edges.append(EdgeInfo(
                            kind="CONTAINS",
                            source=self._qualify(
                                enclosing_class, file_path, None,
                            ),
                            target=qualified,
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                        ))
                        continue

                # File-level and contract-level constant declarations
                if node_type == "constant_variable_declaration":
                    var_name = None
                    var_type = None
                    for sub in child.children:
                        if sub.type == "identifier":
                            var_name = sub.text.decode("utf-8", errors="replace")
                        elif sub.type == "type_name":
                            var_type = sub.text.decode("utf-8", errors="replace")
                    if var_name:
                        qualified = self._qualify(
                            var_name, file_path, enclosing_class,
                        )
                        nodes.append(NodeInfo(
                            kind="Function",
                            name=var_name,
                            file_path=file_path,
                            line_start=child.start_point[0] + 1,
                            line_end=child.end_point[0] + 1,
                            language=language,
                            parent_name=enclosing_class,
                            return_type=var_type,
                            extra={"solidity_kind": "constant"},
                        ))
                        container = (
                            self._qualify(enclosing_class, file_path, None)
                            if enclosing_class
                            else file_path
                        )
                        edges.append(EdgeInfo(
                            kind="CONTAINS",
                            source=container,
                            target=qualified,
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                        ))
                        continue

                # Using directives: using LibName for Type → DEPENDS_ON edge
                if node_type == "using_directive":
                    lib_name = None
                    for sub in child.children:
                        if sub.type == "type_alias":
                            for ident in sub.children:
                                if ident.type == "identifier":
                                    lib_name = ident.text.decode(
                                        "utf-8", errors="replace",
                                    )
                    if lib_name:
                        source_name = (
                            self._qualify(enclosing_class, file_path, None)
                            if enclosing_class
                            else file_path
                        )
                        edges.append(EdgeInfo(
                            kind="DEPENDS_ON",
                            source=source_name,
                            target=lib_name,
                            file_path=file_path,
                            line=child.start_point[0] + 1,
                        ))
                    continue

            # Recurse for other node types
            self._extract_from_tree(
                child, source, language, file_path, nodes, edges,
                enclosing_class=enclosing_class, enclosing_func=enclosing_func,
                import_map=import_map, defined_names=defined_names,
                _depth=_depth + 1,
            )

    def _collect_file_scope(
        self, root, language: str, source: bytes,
    ) -> tuple[dict[str, str], set[str]]:
        """Pre-scan top-level AST to collect import mappings and defined names.

        Returns:
            (import_map, defined_names) where import_map maps imported names
            to their source module/path, and defined_names is the set of
            function/class names defined at file scope.
        """
        import_map: dict[str, str] = {}
        defined_names: set[str] = set()

        class_types = set(_CLASS_TYPES.get(language, []))
        func_types = set(_FUNCTION_TYPES.get(language, []))
        import_types = set(_IMPORT_TYPES.get(language, []))

        # Node types that wrap a class/function with decorators/annotations
        decorator_wrappers = {"decorated_definition", "decorator"}

        for child in root.children:
            node_type = child.type

            # Unwrap decorator wrappers to reach the inner definition
            target = child
            if node_type in decorator_wrappers:
                for inner in child.children:
                    if inner.type in func_types or inner.type in class_types:
                        target = inner
                        break

            target_type = target.type

            # Collect defined function/class names
            if target_type in func_types or target_type in class_types:
                name = self._get_name(target, language,
                                      "class" if target_type in class_types else "function")
                if name:
                    defined_names.add(name)

            # Collect import mappings: imported_name → module_path
            if node_type in import_types:
                self._collect_import_names(child, language, source, import_map)

        return import_map, defined_names

    def _collect_import_names(
        self, node, language: str, source: bytes, import_map: dict[str, str],
    ) -> None:
        """Extract imported names and their source modules into import_map."""
        if language == "python":
            if node.type == "import_from_statement":
                # from X.Y import A, B → {A: X.Y, B: X.Y}
                module = None
                seen_import_keyword = False
                for child in node.children:
                    if child.type == "dotted_name" and not seen_import_keyword:
                        module = child.text.decode("utf-8", errors="replace")
                    elif child.type == "import":
                        seen_import_keyword = True
                    elif seen_import_keyword and module:
                        if child.type in ("identifier", "dotted_name"):
                            name = child.text.decode("utf-8", errors="replace")
                            import_map[name] = module
                        elif child.type == "aliased_import":
                            # from X import A as B → {B: X}
                            names = [
                                sub.text.decode("utf-8", errors="replace")
                                for sub in child.children
                                if sub.type in ("identifier", "dotted_name")
                            ]
                            # Last name is the alias (local name)
                            if names:
                                import_map[names[-1]] = module

        elif language in ("javascript", "typescript", "tsx"):
            # import { A, B } from './path' → {A: ./path, B: ./path}
            module = None
            for child in node.children:
                if child.type == "string":
                    module = child.text.decode("utf-8", errors="replace").strip("'\"")
            if module:
                for child in node.children:
                    if child.type == "import_clause":
                        self._collect_js_import_names(child, module, import_map)

    def _collect_js_import_names(
        self, clause_node, module: str, import_map: dict[str, str],
    ) -> None:
        """Walk JS/TS import_clause to extract named and default imports."""
        for child in clause_node.children:
            if child.type == "identifier":
                # Default import
                import_map[child.text.decode("utf-8", errors="replace")] = module
            elif child.type == "named_imports":
                for spec in child.children:
                    if spec.type == "import_specifier":
                        # Could be: name or name as alias
                        names = [
                            s.text.decode("utf-8", errors="replace")
                            for s in spec.children
                            if s.type in ("identifier", "property_identifier")
                        ]
                        # Last identifier is the local name
                        if names:
                            import_map[names[-1]] = module

    def _resolve_module_to_file(
        self, module: str, file_path: str, language: str,
    ) -> str | None:
        """Resolve a module/import path to an absolute file path.

        Uses self._module_file_cache to avoid repeated filesystem lookups.
        """
        caller_dir = str(Path(file_path).parent)
        cache_key = f"{language}:{caller_dir}:{module}"
        if cache_key in self._module_file_cache:
            return self._module_file_cache[cache_key]

        resolved = self._do_resolve_module(module, file_path, language)
        if len(self._module_file_cache) >= self._MODULE_CACHE_MAX:
            self._module_file_cache.clear()
        self._module_file_cache[cache_key] = resolved
        return resolved

    def _do_resolve_module(
        self, module: str, file_path: str, language: str,
    ) -> str | None:
        """Language-aware module-to-file resolution."""
        caller_dir = Path(file_path).parent

        if language == "python":
            rel_path = module.replace(".", "/")
            candidates = [rel_path + ".py", rel_path + "/__init__.py"]
            # Walk up from caller's directory to find the module file
            current = caller_dir
            while True:
                for candidate in candidates:
                    target = current / candidate
                    if target.is_file():
                        return str(target.resolve())
                if current == current.parent:
                    break
                current = current.parent

        elif language in ("javascript", "typescript", "tsx", "vue"):
            if module.startswith("."):
                # Relative import — resolve from caller's directory
                base = caller_dir / module
                extensions = [".ts", ".tsx", ".js", ".jsx", ".vue"]
                # Try exact path first (might already have extension)
                if base.is_file():
                    return str(base.resolve())
                # Try with extensions
                for ext in extensions:
                    target = base.with_suffix(ext)
                    if target.is_file():
                        return str(target.resolve())
                # Try index file in directory
                if base.is_dir():
                    for ext in extensions:
                        target = base / f"index{ext}"
                        if target.is_file():
                            return str(target.resolve())

        return None

    def _resolve_call_target(
        self,
        call_name: str,
        file_path: str,
        language: str,
        import_map: dict[str, str],
        defined_names: set[str],
    ) -> str:
        """Resolve a bare call name to a qualified target, with fallback."""
        if call_name in defined_names:
            return self._qualify(call_name, file_path, None)
        if call_name in import_map:
            resolved = self._resolve_module_to_file(
                import_map[call_name], file_path, language,
            )
            if resolved:
                return self._qualify(call_name, resolved, None)
        return call_name

    def _qualify(self, name: str, file_path: str, enclosing_class: str | None) -> str:
        """Create a qualified name: file_path::ClassName.name or file_path::name."""
        if enclosing_class:
            return f"{file_path}::{enclosing_class}.{name}"
        return f"{file_path}::{name}"

    def _is_c_function_prototype(self, node) -> bool:
        """True if a C/C++ `declaration` node declares a function, not a variable.

        Its declarator chain (through any `pointer_declarator`/`reference_declarator`
        return-type wrapping) must bottom out in a `function_declarator` whose own
        name is a plain identifier — not one wrapped in `parenthesized_declarator`,
        which marks a function-*pointer variable* (`int (*fp)(int);`) rather than a
        function prototype (`int fp(int);`).
        """
        for child in node.children:
            if child.type == "function_declarator":
                inner = child.children[0] if child.children else None
                return inner is not None and inner.type != "parenthesized_declarator"
            if child.type in ("pointer_declarator", "reference_declarator"):
                return self._is_c_function_prototype(child)
        return False

    def _find_function_declarator(self, node):
        """Descend through C/C++ return-type declarator wrapping to the
        `function_declarator` that carries this function's own name and parameters.

        `pointer_declarator`/`reference_declarator` wrap the declarator when the
        return type is a pointer/reference (`const char *foo()`, `Type& Class::bar()`);
        the `*`/`&` they contribute belongs to the *return type*, not the name, so
        this returns them separately rather than folding them into the declarator.

        Only ever descends through these two wrapper kinds, never into unrelated
        siblings (e.g. a `qualified_identifier` return type) or into the function
        body — so callers can safely assume whatever it finds is the real declarator.

        Returns (function_declarator_node, sigils) — sigils is "" when not found.
        """
        if node.type == "function_declarator":
            return node, ""
        for child in node.children:
            if child.type in ("function_declarator", "pointer_declarator", "reference_declarator"):
                found, sigils = self._find_function_declarator(child)
                if found is not None:
                    if child.type == "pointer_declarator":
                        return found, "*" + sigils
                    if child.type == "reference_declarator":
                        return found, "&" + sigils
                    return found, sigils
        return None, ""

    def _last_identifier_in_qualified(self, node) -> str | None:
        """Last identifier-like segment of a (possibly nested) `qualified_identifier`,
        e.g. `A::B::method` (nested as `A::(B::method)`) → "method"."""
        for sub in reversed(node.children):
            if sub.type == "qualified_identifier":
                result = self._last_identifier_in_qualified(sub)
                if result:
                    return result
            elif sub.type in (
                "identifier", "field_identifier", "type_identifier",
                "destructor_name", "operator_name",
            ):
                return sub.text.decode("utf-8", errors="replace")
        return None

    def _get_name(self, node, language: str, kind: str) -> str | None:
        """Extract the name from a class/function definition node."""
        # Solidity: constructor and receive/fallback have no identifier child
        if language == "solidity":
            if node.type == "constructor_definition":
                return "constructor"
            if node.type == "fallback_receive_definition":
                for child in node.children:
                    if child.type in ("receive", "fallback"):
                        return child.text.decode("utf-8", errors="replace")
        # For C/C++: the name lives in the function_declarator, found by descending
        # through any return-type pointer/reference wrapping first — never in a
        # bare qualified_identifier sibling, which would just as easily be the
        # return type (`ResolveInfo::Builder& ResolveInfo::Builder::SetPkgName(...)`
        # has TWO qualified_identifiers: the return type and the declarator).
        if language in ("c", "cpp") and kind == "function":
            declarator, _ = self._find_function_declarator(node)
            if declarator is not None:
                for sub in declarator.children:
                    if sub.type in (
                        "identifier", "field_identifier", "type_identifier",
                        "destructor_name", "operator_name",
                    ):
                        return sub.text.decode("utf-8", errors="replace")
                    # Out-of-class definitions ("ClassName::method(...)") wrap the
                    # name in qualified_identifier.
                    if sub.type == "qualified_identifier":
                        result = self._last_identifier_in_qualified(sub)
                        if result:
                            return result
            return None
        # Most languages use a 'name' child
        for child in node.children:
            if child.type in (
                "identifier", "name", "type_identifier", "property_identifier",
                "simple_identifier", "constant", "field_identifier",
            ):
                return child.text.decode("utf-8", errors="replace")
        # For Go type declarations, look for type_spec
        if language == "go" and node.type == "type_declaration":
            for child in node.children:
                if child.type == "type_spec":
                    return self._get_name(child, language, kind)
        return None

    def _get_params(self, node, language: str, source: bytes) -> str | None:
        """Extract parameter list as a string."""
        for child in node.children:
            if child.type in ("parameters", "formal_parameters", "parameter_list"):
                return child.text.decode("utf-8", errors="replace")
        # C/C++: the parameter_list is inside the function_declarator, not a
        # direct child of the function_definition/declaration passed in here.
        if language in ("c", "cpp"):
            declarator, _ = self._find_function_declarator(node)
            if declarator is not None:
                for child in declarator.children:
                    if child.type == "parameter_list":
                        return child.text.decode("utf-8", errors="replace")
        # Solidity: parameters are direct children between ( and )
        if language == "solidity":
            params = [
                c.text.decode("utf-8", errors="replace")
                for c in node.children
                if c.type == "parameter"
            ]
            if params:
                return f"({', '.join(params)})"
        return None

    def _get_return_type(self, node, language: str, source: bytes) -> str | None:
        """Extract return type annotation if present."""
        for child in node.children:
            if child.type in ("type", "return_type", "type_annotation", "return_type_definition"):
                return child.text.decode("utf-8", errors="replace")
        # Python: look for -> annotation
        if language == "python":
            for i, child in enumerate(node.children):
                if child.type == "->" and i + 1 < len(node.children):
                    return node.children[i + 1].text.decode("utf-8", errors="replace")
        # C/C++: the return type is whatever precedes the function's own
        # declarator (skipping storage-class specifiers like `static`/`extern`),
        # plus any `*`/`&` consumed while descending through pointer/reference
        # return-type wrapping to find that declarator (those sigils are part
        # of the type, e.g. `const char *foo()`, not the name).
        if language in ("c", "cpp"):
            declarator, sigils = self._find_function_declarator(node)
            if declarator is not None:
                parts = []
                for child in node.children:
                    if child.type in (
                        "function_declarator", "pointer_declarator", "reference_declarator",
                    ):
                        break
                    if child.type == "storage_class_specifier":
                        continue
                    parts.append(child.text.decode("utf-8", errors="replace"))
                if parts:
                    return " ".join(parts) + (" " + sigils if sigils else "")
        return None

    def _get_bases(self, node, language: str, source: bytes) -> list[str]:
        """Extract base classes / implemented interfaces."""
        bases = []
        if language == "python":
            for child in node.children:
                if child.type == "argument_list":
                    for arg in child.children:
                        if arg.type in ("identifier", "attribute"):
                            bases.append(arg.text.decode("utf-8", errors="replace"))
        elif language in ("java", "csharp", "kotlin"):
            # Look for superclass/interfaces in extends/implements clauses
            for child in node.children:
                if child.type in (
                    "superclass", "super_interfaces", "extends_type",
                    "implements_type", "type_identifier", "supertype",
                    "delegation_specifier",
                ):
                    text = child.text.decode("utf-8", errors="replace")
                    bases.append(text)
        elif language == "cpp":
            # C++: base_class_clause holds a type_identifier for a plain base
            # (`: public Base`) or a qualified_identifier for a namespace/outer-class
            # -qualified one (`: public Worker::Job`) — keep the full qualified text.
            for child in node.children:
                if child.type == "base_class_clause":
                    for sub in child.children:
                        if sub.type in ("type_identifier", "qualified_identifier"):
                            bases.append(sub.text.decode("utf-8", errors="replace"))
        elif language in ("typescript", "javascript", "tsx"):
            # extends clause
            for child in node.children:
                if child.type in ("extends_clause", "implements_clause"):
                    for sub in child.children:
                        if sub.type in ("identifier", "type_identifier", "nested_identifier"):
                            bases.append(sub.text.decode("utf-8", errors="replace"))
        elif language == "solidity":
            # contract Foo is Bar, Baz { ... }
            for child in node.children:
                if child.type == "inheritance_specifier":
                    for sub in child.children:
                        if sub.type == "user_defined_type":
                            for ident in sub.children:
                                if ident.type == "identifier":
                                    bases.append(ident.text.decode("utf-8", errors="replace"))
        elif language == "swift":
            # class ViewController: UIViewController, UITableViewDelegate { ... }
            # Swift AST: inheritance_specifier > user_type > type_identifier
            for child in node.children:
                if child.type == "inheritance_specifier":
                    for sub in child.children:
                        if sub.type == "user_type":
                            for ident in sub.children:
                                if ident.type == "type_identifier":
                                    bases.append(ident.text.decode("utf-8", errors="replace"))
                        elif sub.type in ("identifier", "type_identifier"):
                            bases.append(sub.text.decode("utf-8", errors="replace"))
        elif language == "go":
            # Embedded structs / interface composition
            for child in node.children:
                if child.type == "type_spec":
                    for sub in child.children:
                        if sub.type in ("struct_type", "interface_type"):
                            for field_node in sub.children:
                                if field_node.type == "field_declaration_list":
                                    for f in field_node.children:
                                        if f.type == "type_identifier":
                                            bases.append(f.text.decode("utf-8", errors="replace"))
        return bases

    def _extract_import(self, node, language: str, source: bytes) -> list[str]:
        """Extract import targets as module/path strings."""
        imports = []
        text = node.text.decode("utf-8", errors="replace").strip()

        if language == "python":
            # import x.y.z  or  from x.y import z
            if node.type == "import_from_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        imports.append(child.text.decode("utf-8", errors="replace"))
                        break
            else:
                for child in node.children:
                    if child.type == "dotted_name":
                        imports.append(child.text.decode("utf-8", errors="replace"))
        elif language in ("javascript", "typescript", "tsx"):
            # import ... from 'module'
            for child in node.children:
                if child.type == "string":
                    val = child.text.decode("utf-8", errors="replace").strip("'\"")
                    imports.append(val)
        elif language == "go":
            for child in node.children:
                if child.type == "import_spec_list":
                    for spec in child.children:
                        if spec.type == "import_spec":
                            for s in spec.children:
                                if s.type == "interpreted_string_literal":
                                    val = s.text.decode("utf-8", errors="replace")
                                    imports.append(val.strip('"'))
                elif child.type == "import_spec":
                    for s in child.children:
                        if s.type == "interpreted_string_literal":
                            val = s.text.decode("utf-8", errors="replace")
                            imports.append(val.strip('"'))
        elif language == "rust":
            # use crate::module::item
            imports.append(text.replace("use ", "").rstrip(";").strip())
        elif language in ("c", "cpp"):
            # #include <header> or #include "header"
            for child in node.children:
                if child.type in ("system_lib_string", "string_literal"):
                    val = child.text.decode("utf-8", errors="replace").strip("<>\"")
                    imports.append(val)
        elif language in ("java", "csharp"):
            # import/using package.Class
            parts = text.split()
            if len(parts) >= 2:
                imports.append(parts[-1].rstrip(";"))
        elif language == "kotlin":
            # import kotlin.collections.List → "kotlin.collections.List"
            # import com.example.* → "com.example.*"
            for child in node.children:
                if child.type == "identifier":
                    imports.append(child.text.decode("utf-8", errors="replace"))
            # Fallback: extract from raw text if no identifier child found
            if not imports:
                stripped = text.replace("import ", "").rstrip(";").strip()
                if stripped:
                    imports.append(stripped)
        elif language == "swift":
            # import Foundation → "Foundation"
            # import UIKit → "UIKit"
            for child in node.children:
                if child.type == "identifier":
                    imports.append(child.text.decode("utf-8", errors="replace"))
            # Fallback: extract from raw text
            if not imports:
                stripped = text.replace("import ", "").strip()
                if stripped:
                    imports.append(stripped)
        elif language == "solidity":
            # import "path/to/file.sol" or import {Symbol} from "path"
            for child in node.children:
                if child.type == "string":
                    val = child.text.decode("utf-8", errors="replace").strip('"')
                    if val:
                        imports.append(val)
        elif language == "ruby":
            # require 'module' or require_relative 'path'
            if "require" in text:
                match = re.search(r"""['"](.*?)['"]""", text)
                if match:
                    imports.append(match.group(1))
        else:
            # Fallback: just record the text
            imports.append(text)

        return imports

    def _get_call_name(self, node, language: str, source: bytes) -> str | None:
        """Extract the function/method name being called."""
        if not node.children:
            return None

        first = node.children[0]

        # Solidity wraps call targets in an 'expression' node – unwrap it
        if language == "solidity" and first.type == "expression" and first.children:
            first = first.children[0]

        # Simple call: func_name(args)
        if first.type == "identifier":
            return first.text.decode("utf-8", errors="replace")

        # Method call: obj.method(args)
        member_types = (
            "attribute", "member_expression",
            "field_expression", "selector_expression",
        )
        if first.type in member_types:
            # Get the rightmost identifier (the method name)
            for child in reversed(first.children):
                if child.type in (
                    "identifier", "property_identifier", "field_identifier",
                    "field_name",
                ):
                    return child.text.decode("utf-8", errors="replace")
            return first.text.decode("utf-8", errors="replace")

        # Scoped call (e.g., Rust path::func())
        if first.type in ("scoped_identifier", "qualified_name"):
            return first.text.decode("utf-8", errors="replace")

        return None

    # --- IPC detection helpers ---

    def _detect_ipc_type(self, call_name: str, language: str) -> str | None:
        """Check if a call name matches a known IPC pattern for the given language.

        Returns the IPC mechanism type string (validated against IpcMechanism enum)
        or None if no IPC pattern matches.
        """
        patterns = _IPC_PATTERNS.get(language, {})
        call_lower = call_name.lower()
        for ipc_type, name_patterns in patterns.items():
            for pattern in name_patterns:
                if pattern.lower() in call_lower:
                    # Validate against IpcMechanism enum
                    try:
                        return IpcMechanism(ipc_type).value
                    except ValueError:
                        # Unknown IPC type — log and skip (do NOT return the
                        # invalid value, which would bypass enum validation)
                        logger.warning("Unknown IPC mechanism: %s", ipc_type)
                        continue

        return None

    def _detect_ipc_direction(self, call_name: str) -> str:
        """Detect if IPC is incoming, outgoing, or bidirectional based on call pattern."""
        incoming_patterns = ["listen", "accept", "register", "subscribe", "on", "recv", "receive"]
        outgoing_patterns = ["send", "emit", "publish", "call", "invoke", "connect", "post", "get"]
        call_lower = call_name.lower()
        if any(p in call_lower for p in incoming_patterns):
            return "incoming"
        if any(p in call_lower for p in outgoing_patterns):
            return "outgoing"
        return "bidirectional"

    # --- ENUM extraction helpers ---

    def _extract_enum_values(self, node, language: str, source: bytes) -> dict[str, str]:
        """Extract enum key-value pairs from an enum definition node.

        Returns a dict mapping enum member name to its value string.
        """
        values: dict[str, str] = {}

        if language in ("c", "cpp"):
            # C/C++: enum_specifier > enumerator_list > enumerator
            for child in node.children:
                if child.type == "enumerator_list":
                    for enum_member in child.children:
                        if enum_member.type == "enumerator":
                            name = None
                            value = None
                            for sub in enum_member.children:
                                if sub.type == "identifier":
                                    name = sub.text.decode("utf-8", errors="replace")
                                elif sub.type in ("number_literal", "expression"):
                                    value = sub.text.decode("utf-8", errors="replace")
                            if name:
                                values[name] = value or "auto"

        elif language == "java":
            # Java: enum_declaration > enum_body > enum_constant
            for child in node.children:
                if child.type == "enum_body":
                    for const in child.children:
                        if const.type == "enum_constant":
                            name = None
                            for sub in const.children:
                                if sub.type == "identifier":
                                    name = sub.text.decode("utf-8", errors="replace")
                                    break
                            if name:
                                values[name] = "auto"

        elif language == "python":
            # Python: enum class with assignments in block
            for child in node.children:
                if child.type == "block":
                    for stmt in child.children:
                        if stmt.type == "expression_statement":
                            for sub in stmt.children:
                                if sub.type == "assignment":
                                    name = None
                                    value = None
                                    for a in sub.children:
                                        if a.type == "identifier":
                                            name = a.text.decode("utf-8", errors="replace")
                                        elif a.type in ("integer", "string", "float", "true", "false", "none"):
                                            value = a.text.decode("utf-8", errors="replace")
                                    if name and name.isupper():
                                        values[name] = value or "auto"

        elif language in ("javascript", "typescript", "tsx"):
            # TS: enum_declaration > enum_body > (enum_assignment | property_identifier)
            # JS: enums are not valid syntax; tree-sitter produces ERROR nodes.
            # Find the enum_body child first, then extract members from it.
            enum_body = None
            for child in node.children:
                if child.type == "enum_body":
                    enum_body = child
                    break
            # If no enum_body found, fall back to direct children (shouldn't happen for valid TS)
            search_children = enum_body.children if enum_body else node.children
            for child in search_children:
                if child.type == "enum_assignment":
                    name = None
                    value = None
                    for sub in child.children:
                        if sub.type == "property_identifier":
                            name = sub.text.decode("utf-8", errors="replace")
                        elif sub.type in ("number", "string", "template_string"):
                            value = sub.text.decode("utf-8", errors="replace")
                    if name:
                        values[name] = value or "auto"
                elif child.type == "property_identifier":
                    name = child.text.decode("utf-8", errors="replace")
                    values[name] = "auto"

        elif language == "csharp":
            # C#: enum_declaration > enum_member_declaration_list > enum_member_declaration
            for child in node.children:
                if child.type == "enum_member_declaration_list":
                    for member in child.children:
                        if member.type == "enum_member_declaration":
                            name = None
                            value = None
                            for sub in member.children:
                                if sub.type == "identifier":
                                    name = sub.text.decode("utf-8", errors="replace")
                                elif sub.type == "equals_value_clause":
                                    for v in sub.children:
                                        if v.type in ("number_literal", "expression"):
                                            value = v.text.decode("utf-8", errors="replace")
                            if name:
                                values[name] = value or "auto"

        elif language == "go":
            # Go: type_spec > type_identifier + enum-like const blocks
            # Go doesn't have native enums; they use iota const blocks
            # TODO: Go enum value extraction is deferred — Go uses `const` blocks
            # with `iota` rather than dedicated enum syntax. The const block is
            # not a child of type_spec, so it needs to be resolved from the
            # enclosing scope. This requires tracking the type_spec name and
            # scanning sibling const_spec nodes for matching type assertions.
            for child in node.children:
                if child.type == "type_identifier":
                    pass  # Name is extracted separately


        elif language == "rust":
            # Rust: enum_item > enum_variant
            for child in node.children:
                if child.type == "enum_variant":
                    name = None
                    for sub in child.children:
                        if sub.type == "identifier":
                            name = sub.text.decode("utf-8", errors="replace")
                            break
                    if name:
                        values[name] = "auto"

        elif language == "swift":
            # Swift: enum_declaration > enum_body > enum_case
            for child in node.children:
                if child.type == "enum_body":
                    for case in child.children:
                        if case.type == "enum_case":
                            for sub in case.children:
                                if sub.type == "identifier":
                                    name = sub.text.decode("utf-8", errors="replace")
                                    values[name] = "auto"

        elif language == "kotlin":
            # Kotlin: class_declaration > enum_class_body > enum_entry > simple_identifier
            for child in node.children:
                if child.type == "enum_class_body":
                    for entry in child.children:
                        if entry.type == "enum_entry":
                            for sub in entry.children:
                                if sub.type == "simple_identifier":
                                    name = sub.text.decode("utf-8", errors="replace")
                                    values[name] = "auto"
                                    break

        elif language == "solidity":
            # Solidity: enum_declaration > identifier children
            for child in node.children:
                if child.type == "identifier":
                    name = child.text.decode("utf-8", errors="replace")
                    values[name] = "auto"

        return values

    def _get_enum_type(self, node, language: str, source: bytes) -> str | None:
        """Extract the underlying type of an enum if explicitly specified."""
        if language in ("c", "cpp"):
            # C/C++: enum_specifier may have type_identifier children.
            # The FIRST type_identifier is the enum name (e.g. "MessageType");
            # the SECOND type_identifier (if any) is the underlying type
            # (e.g. "uint32_t" in `enum MessageType : uint32_t { ... }`).
            # Skip the name identifier and return the next one.
            enum_name = self._get_name(node, language, "enum")
            found_name = False
            for child in node.children:
                if child.type == "type_identifier":
                    text = child.text.decode("utf-8", errors="replace")
                    if not found_name and text == enum_name:
                        found_name = True  # skip the enum name identifier
                        continue
                    return text  # this is the underlying type

        elif language == "java":
            # Java enums are implicitly int-backed
            return "int"

        elif language in ("typescript", "javascript", "tsx"):
            # TS: enum Name : type { ... }
            for child in node.children:
                if child.type == "type_annotation":
                    return child.text.decode("utf-8", errors="replace")

        elif language == "csharp":
            # C#: enum Name : type { ... }
            for child in node.children:
                if child.type == "base_list":
                    for sub in child.children:
                        if sub.type == "identifier":
                            return sub.text.decode("utf-8", errors="replace")

        return None

    # --- Constant extraction helpers ---

    def _is_constant_node(self, node, language: str, source: bytes) -> bool:
        """Check if a node represents a constant (not just a variable).

        Uses language-specific patterns to distinguish constants from variables.
        """
        node_text = node.text.decode("utf-8", errors="replace")

        if language == "python":
            # Python: UPPER_CASE naming convention
            name = self._get_name(node, language, "constant")
            if name:
                return name.isupper() or name.startswith("_") and name[1:].isupper()
            return False

        elif language == "kotlin":
            # Kotlin: check for 'val' modifier (not 'var')
            for child in node.children:
                if child.type == "modifiers":
                    return "val" in node_text
            # property_declaration without explicit var is val by default
            return "val" in node_text

        elif language == "java":
            # Java: check for static final modifiers
            return "static" in node_text and "final" in node_text

        elif language == "cpp":
            # C++: #define or constexpr
            return node.type == "preproc_def" or "constexpr" in node_text

        elif language == "c":
            # C: #define only
            return node.type == "preproc_def"

        elif language in ("javascript", "typescript", "tsx"):
            # JS/TS: const declarations only (not let/var)
            return "const" in node_text

        elif language == "csharp":
            # C#: const or readonly
            return "const" in node_text or "readonly" in node_text

        elif language == "go":
            # Go: const_spec nodes are always constants
            return node.type == "const_spec"

        elif language == "rust":
            # Rust: const_item nodes are constants
            return node.type == "constant_item"

        elif language == "swift":
            # Swift: let declarations
            return "let" in node_text

        elif language == "php":
            # PHP: const or define()
            return "const" in node_text or "define" in node_text

        elif language == "ruby":
            # Ruby: UPPER_CASE naming convention
            name = self._get_name(node, language, "constant")
            if name:
                return name[0].isupper()
            return False

        # Default: assume it's a constant if it matches the type
        return True

    def _extract_constant_value(self, node, language: str, source: bytes) -> str:
        """Extract the value of a constant node.

        Returns the value as a string, or "N/A" if not extractable.
        """
        node_text = node.text.decode("utf-8", errors="replace")

        if language == "python":
            # Python: assignment > identifier = value
            for child in node.children:
                if child.type in ("integer", "string", "float", "true", "false", "none"):
                    return child.text.decode("utf-8", errors="replace")
                elif child.type == "assignment":
                    # Get the right side of assignment
                    for sub in child.children:
                        if sub.type in ("integer", "string", "float", "true", "false", "none"):
                            return sub.text.decode("utf-8", errors="replace")

        elif language == "kotlin":
            # Kotlin: property_declaration > property_delegate or assignment
            for child in node.children:
                if child.type == "assignment":
                    for sub in child.children:
                        if sub.type in ("integer_literal", "string_literal", "boolean_literal"):
                            return sub.text.decode("utf-8", errors="replace")

        elif language == "java":
            # Java: constant_declaration > variable_declarator
            for child in node.children:
                if child.type == "variable_declarator":
                    for sub in child.children:
                        if sub.type in ("decimal_integer_literal", "string_literal", "true", "false", "null"):
                            return sub.text.decode("utf-8", errors="replace")

        elif language in ("c", "cpp"):
            # C/C++: preproc_def > identifier value
            if node.type == "preproc_def":
                # Extract everything after the identifier
                parts = node_text.split(None, 2)
                if len(parts) >= 3:
                    return parts[2]

        elif language in ("javascript", "typescript", "tsx"):
            # JS/TS: lexical_declaration > variable_declaration > = value
            for child in node.children:
                if child.type == "variable_declaration":
                    for sub in child.children:
                        if sub.type == "=":
                            # Get next sibling after =
                            idx = list(child.children).index(sub)
                            if idx + 1 < len(child.children):
                                val_node = child.children[idx + 1]
                                return val_node.text.decode("utf-8", errors="replace")

        elif language == "go":
            # Go: const_spec > expression
            for child in node.children:
                if child.type in ("expression", "literal_value"):
                    return child.text.decode("utf-8", errors="replace")

        elif language == "rust":
            # Rust: constant_item > expression
            for child in node.children:
                if child.type in ("integer_literal", "string_literal", "true", "false"):
                    return child.text.decode("utf-8", errors="replace")

        elif language == "csharp":
            # C#: constant_declaration > variable_declarator
            for child in node.children:
                if child.type == "variable_declarator":
                    for sub in child.children:
                        if sub.type in ("decimal_literal", "string_literal", "true", "false", "null"):
                            return sub.text.decode("utf-8", errors="replace")

        elif language == "swift":
            # Swift: constant_declaration > pattern
            for child in node.children:
                if child.type == "pattern":
                    for sub in child.children:
                        if sub.type in ("integer_literal", "string_literal", "boolean_literal"):
                            return sub.text.decode("utf-8", errors="replace")

        elif language == "php":
            # PHP: constant_definition > assignment
            for child in node.children:
                if child.type == "assignment_expression":
                    for sub in child.children:
                        if sub.type in ("integer", "string", "true", "false", "null"):
                            return sub.text.decode("utf-8", errors="replace")

        elif language == "ruby":
            # Ruby: assignment > value
            for child in node.children:
                if child.type in ("integer", "string", "true", "false", "nil"):
                    return child.text.decode("utf-8", errors="replace")

        return "N/A"

    # --- Error code detection helpers (Phase 4) ---
    # TODO: _is_error_code_constant and _is_exception_class are defined but
    # not yet wired into the extraction pipeline. They should be called during
    # constant/class extraction to tag nodes with error_code/exception metadata.
    # Leaving them here as they are part of the planned Phase 4 enhancement.

    def _is_error_code_constant(self, node, language: str, source: bytes) -> bool:
        """Check if a constant node represents an error code.


        Error codes typically have names like:
        - ERROR_*, ERR_*, E_*
        - RESULT_ERROR, STATUS_ERROR
        - EXIT_FATAL, EXIT_SUCCESS

        Or are members of Exception/Error classes.
        """
        node.text.decode("utf-8", errors="replace")
        name = self._get_name(node, language, "constant")
        if not name:
            return False

        name_upper = name.upper()

        # Check for error-related naming patterns
        error_patterns = [
            "ERROR", "ERR", "E_", "RESULT_ERROR", "STATUS_ERROR",
            "EXIT_FATAL", "EXIT_SUCCESS", "EXIT_FAILURE",
            "FAILURE", "DENIED", "INVALID", "TIMEOUT",
        ]

        for pattern in error_patterns:
            if pattern in name_upper:
                return True

        return False

    def _is_exception_class(self, node, language: str, source: bytes) -> bool:
        """Check if a class node represents an Exception/Error class.

        Exception classes typically:
        - Inherit from Exception, Error, Throwable, etc.
        - Have names ending in Exception or Error
        """
        name = self._get_name(node, language, "class")
        if not name:
            return False

        # Check if class name ends with Exception or Error
        if name.endswith("Exception") or name.endswith("Error"):
            return True

        # Check inheritance
        bases = self._get_bases(node, language, source)
        exception_bases = ["Exception", "Error", "Throwable", "RuntimeException", "BaseException"]
        for base in bases:
            if any(exc in base for exc in exception_bases):
                return True

        return False
