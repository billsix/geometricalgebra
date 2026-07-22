# Doc-region markers on class variables (like instance variables)

**Status:** proposed — needs go-ahead. Created 2026-07-21. (Bill's batch item 1.)

## Goal

The generator already wraps a class's **instance variables** (the non-`ClassVar` `coeff_*`
fields) in a `<Class> instance variables` doc-region (`astbuild.inject_region_markers`). It does
**not** wrap the **class variables** — the `ClassVar` declarations (`DIMENSION`, and the basis
constants `e_1`, `e_2`, `e_12`, …). Add a `<Class> class variables` region around those, so the
book can `literalinclude` them too.

## What's there now (verified in generated `g2.py`)

- `DIMENSION: typing.ClassVar[int] = 2` and `e_1: typing.ClassVar[G2]` / `e_2` / `e_12` are
  emitted with **no** surrounding doc-region.
- `grep -c "instance variables"` → 8 regions; `grep -c "class variables"` → **0**.
- `astbuild.inject_region_markers` computes `field_indices` as the non-`ClassVar` `AnnAssign`s
  (via `_is_classvar`) and marks only those. The `ClassVar` `AnnAssign`s are the complement.

## Plan (sketch)

- In `astbuild.inject_region_markers`, additionally find the contiguous run of `ClassVar`
  `AnnAssign` members and wrap them in `doc-region-begin/end <Class> class variables`, mirroring
  the instance-variables logic. Watch the ordering: `DIMENSION` and the `e_*` ClassVars are
  declared together near the top of the class body (the basis-constant *values* are assigned
  post-class via `Cls.e_1 = …`, which stay unmarked — only the ClassVar *declarations* get the
  region).
- Regenerate; `make check-regions` must stay green (unique/prefix-free/balanced); confirm the new
  `<Class> class variables` region doesn't prefix-collide with `<Class> instance variables`.

## Relationships

- Same subsystem as `tasks/reference/code-generator-architecture.md` (§ doc-region machinery).
- Purely additive markers; no runtime/typing effect.
