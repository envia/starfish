# Functional Requirements — third-party

> **Relevant source files**
> - [`robin_map.h`](src:third_party/robin_map/include/tsl/robin_map.h)
> - [`robin_hash.h`](src:third_party/robin_map/include/tsl/robin_hash.h)

## Given Factors

- Header-only hash map (MIT License)
- Robin hood hashing with backward shift deletion

## Overview

The third-party module provides the `tsl::robin_map` hash map used throughout the engine for high-performance lookups.

## Functional Requirements

### FR-TP-001: Hash Map Operations
The system shall provide insert, erase, rehash, and lookup operations via `tsl::robin_map`.
- **Source:** [`robin_map.h`](src:third_party/robin_map/include/tsl/robin_map.h#L39)

### FR-TP-002: Growth Policy
The system shall support configurable growth policies (power_of_two, mod, prime).
- **Source:** [`robin_growth_policy.h`](src:third_party/robin_map/include/tsl/robin_growth_policy.h)

### FR-TP-003: Hash Set
The system shall provide `tsl::robin_set` as a hash set companion to `robin_map`.
- **Source:** [`robin_set.h`](src:third_party/robin_map/include/tsl/robin_set.h)

### FR-TP-004: StoreHash Option
The system shall optionally store 32-bit hashes alongside values for improved lookup performance.
- **Source:** [`robin_map.h`](src:third_party/robin_map/include/tsl/robin_map.h#L52)

## Dependencies

- C++ standard library only

## Code Factors

- C++ header-only, MIT License

## Quality

- Strong exception guarantee when type requirements met
