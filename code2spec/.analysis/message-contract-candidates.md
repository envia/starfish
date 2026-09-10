# Message / IPC Contract Candidates

**Generated**: 2026-08-27T01:04:22Z
**Analysis Target**: /home/hwang/work/D/starfish_
**Families**: message

## Summary

| Metric | Count |
|--------|-------|
| Total Candidates | 34 |
| confirmed | 0 |
| likely | 0 |
| candidate | 1 |
| llm_suggested | 0 |
| low | 33 |

**Message Candidates**: 34 total / 0 confirmed / 0 likely / 1 candidate

## Unresolved / Review-Only Candidates

| Candidate | Kind | Reason | Missing Evidence | Evidence |
|-----------|------|--------|------------------|----------|
| `postMessage` | worker_message | worker_boundary_not_resolved; no_matching_receiver | worker_boundary_not_resolved; no_matching_receiver | src/core/dom/picker.js:L48 |

## Low-Confidence Candidates (Analysis Only)

> These candidates have weak/generic evidence only and are not promoted to module documentation.

| Candidate | Kind | Evidence | Unresolved |
|-----------|------|----------|------------|
| `afterAll` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5513 | no_known_framework_import; no_matching_receiver |
| `afterEach` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5567 | no_known_framework_import; no_matching_receiver |
| `beforeAll` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5486 | no_known_framework_import; no_matching_receiver |
| `beforeEach` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5540 | no_known_framework_import; no_matching_receiver |
| `end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L4824 | no_known_framework_import; no_matching_receiver |
| `end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5177 | no_known_framework_import; no_matching_receiver |
| `end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5203 | no_known_framework_import; no_matching_receiver |
| `error` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L4502 | no_known_framework_import; no_matching_receiver |
| `fail` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L4797 | no_known_framework_import; no_matching_receiver |
| `hook` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L4849 | no_known_framework_import; no_matching_receiver |
| `hook end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L4869 | no_known_framework_import; no_matching_receiver |
| `pass` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5076 | no_known_framework_import; no_matching_receiver |
| `pending` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5040 | no_known_framework_import; no_matching_receiver |
| `pending` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5050 | no_known_framework_import; no_matching_receiver |
| `pending` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5062 | no_known_framework_import; no_matching_receiver |
| `post-require` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L1597 | no_known_framework_import; no_matching_receiver |
| `pre-require` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L1595 | no_known_framework_import; no_matching_receiver |
| `pre-require` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L6522 | no_known_framework_import; no_matching_receiver |
| `require` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L1596 | no_known_framework_import; no_matching_receiver |
| `run` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5661 | no_known_framework_import; no_matching_receiver |
| `start` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5200 | no_known_framework_import; no_matching_receiver |
| `suite` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5105 | no_known_framework_import; no_matching_receiver |
| `suite` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5586 | no_known_framework_import; no_matching_receiver |
| `suite end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5131 | no_known_framework_import; no_matching_receiver |
| `test` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5046 | no_known_framework_import; no_matching_receiver |
| `test` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5605 | no_known_framework_import; no_matching_receiver |
| `test end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L2764 | no_known_framework_import; no_matching_receiver |
| `test end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5041 | no_known_framework_import; no_matching_receiver |
| `test end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5051 | no_known_framework_import; no_matching_receiver |
| `test end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5066 | no_known_framework_import; no_matching_receiver |
| `test end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5077 | no_known_framework_import; no_matching_receiver |
| `test end` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5171 | no_known_framework_import; no_matching_receiver |
| `waiting` | event_name | src/core/modules/serviceworker/cache/deps/cache-storage/test/mocha.js:L5222 | no_known_framework_import; no_matching_receiver |
