# Functional Requirements — tooling

> **Relevant source files**
> - [`test_runner.py`](src:tool/runner/test_runner.py)
> - [`constants.py`](src:tool/drivers/basics/constants.py)
> - [`check_tidy.py`](src:tool/lint/check_tidy.py)
> - [`wpt_runner.py`](src:tool/wpt/scripts/wpt_runner.py)
> - [`http_server.py`](src:tool/runner/http_server.py)

## Given Factors

- Python 3 test framework with parallel execution support
- Starfish shell launched as subprocess for test execution
- WPT (Web Platform Tests) as spec compliance proof

## Overview

The tooling module provides test execution, lint checking, WPT integration, and development utilities for the Starfish browser engine.

## Functional Requirements

### FR-TOOLING-001: Test Suite Execution
The system shall execute test suites via `.res` list files, launching the Starfish shell as a subprocess.
- **Source:** [`test_runner.py`](src:tool/runner/test_runner.py#L55)

### FR-TOOLING-002: Parallel Test Execution
The system shall support parallel test execution with configurable worker count.
- **Source:** [`test_runner.py`](src:tool/runner/test_runner.py#L78)

### FR-TOOLING-003: WPT Test Runner
The system shall run WPT testharness tests against an on-demand `wpt serve`, judging results from `WPTR` stdout lines.
- **Source:** [`wpt_runner.py`](src:tool/wpt/scripts/wpt_runner.py#L16)

### FR-TOOLING-004: Tidy Code Style Check
The system shall verify C++ code formatting using `clang-format` on `.cpp`, `.h`, `.hpp` files, skipping `third_party/`, `test/`, `build/` directories.
- **Source:** [`check_tidy.py`](src:tool/lint/check_tidy.py#L33)

### FR-TOOLING-005: Contract ABI Check
The system shall verify contract ABI stability across the `.so` boundary.
- **Source:** [`check_contract_abi.py`](src:tool/lint/check_contract_abi.py)

### FR-TOOLING-006: HTTP Test Server
The system shall provide an HTTP server for serving test pages to the Starfish shell.
- **Source:** [`http_server.py`](src:tool/runner/http_server.py)

### FR-TOOLING-007: Test Result Codes
The system shall use standardized error codes: `TEST_PASSED=0`, `TEST_FAILED=1`, `TEST_STOPPED=2`.
- **Source:** [`constants.py`](src:tool/drivers/basics/constants.py#L12)

## Dependencies

- Starfish executable (subprocess)
- clang-format (external)
- WPT test suite (submodule)

## Code Factors

- Python 3, JavaScript (inject scripts), C++ (imgdiff)
- Apache 2.0 licensed

## Quality

- All test runs wrapped in `xvfb-run` per AGENTS.md
- `.res` list discipline enforced
