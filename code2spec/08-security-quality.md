**Related Documents**: [README](README.md) | [Quick Reference](code2spec-quick-reference.md) | [Modules Index](modules/README.md) | [FR Index](functional-requirements/index.md)

# Chapter 8: Security & Quality

> **Relevant source files:**
> - [`ScriptBindingSecurity.cpp`](src:src/binding/ScriptBindingSecurity.cpp#L1)
> - [`test_runner.py`](src:tool/runner/test_runner.py#L252)
> - [`UnitTestRunner.cpp`](src:src/shell/UnitTestRunner.cpp#L1)

---

## Script Security Sandbox
LWE isolates execution environments and enforces origin security protocols within JavaScript binding callbacks [`ScriptBindingSecurity.cpp`](src:src/binding/ScriptBindingSecurity.cpp#L1).

## Quality Assurance & Test Suites
Quality validation consists of two primary suites:
1. **Unit Tests:** Embedded C++ class tests built and launched via native shells [`UnitTestRunner.cpp`](src:src/shell/UnitTestRunner.cpp#L1).
2. **Web Platform Tests (WPT):** Python test runners that load standard WPT suites inside Starfish browser layouts to verify DOM compliance [`test_runner.py`](src:tool/runner/test_runner.py#L252).
