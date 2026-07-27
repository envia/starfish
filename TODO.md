# TODO

## Grid row-gap support (follow-up to flex gap fix)

`FrameGridBox` (`src/core/layout/FrameGridBox.cpp`) has the same class of gap bug
that was fixed for flex in commit `d7f28d5a2` ("Apply row-gap and column-gap by
flex axis role"):

- It never reads `row-gap`; only `m_columnGap` exists.
- The gap is resolved via `columnGap().fixed()` (`FrameGridBox.cpp:93`), so
  percentage / calc gap values are not resolved. Flex uses
  `.specifiedValue(availableWidth, node)` instead.

**Scope:** Separate patch — independent class/code path, no shared code with flex.
~10+ track-sizing sites use `m_columnGap` (line/track gap math), so it carries its
own regression surface and needs its own tests.

Deferred 2026-06-23.
