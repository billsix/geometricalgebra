# Doc-region markers on class variables (like instance variables)

**Status:** complete
**Completed:** 2026-07-22
Created 2026-07-21. (Bill's batch item 1.) All gates green (287 tests, `ty` src/tests/tools clean,
ruff clean, `check-regions` clean, deterministic). Purely additive markers + a cosmetic reorder;
no runtime/typing effect.

## Outcome (what shipped)

New region **`<Class> cls variables`** wraps the ClassVar declarations (`DIMENSION` + the `e_*`
basis constants), the class-level analogue of `<Class> instance variables` — present on every value
class (`G1`/`G2`/`G3` and every graded type); `Scalar` has none (it has no ClassVars).

Two corrections to the task's original plan surfaced during investigation, both confirmed against
the real generated output before changing anything:

1. **The ClassVars were NOT contiguous** (the plan assumed they were). `DIMENSION` sat at the top
   of the class body; the `e_*` declarations were emitted ~50 lines lower, after
   `from_blade_dict`/`to_blade_dict`/`__eq__`. **Fix (Bill chose reorder over two regions):**
   `class_header_stmts` now emits `basis_classvar_decls` right after `DIMENSION` (before the
   `coeff_*` fields), so all class variables are one contiguous block. Cosmetic only — the `e_*`
   are annotation-only `ClassVar`s excluded from the dataclass fields/`__slots__`; their post-class
   value assignments (`Cls.e_1 = …`) are unchanged. The two `generate_*` bodies dropped their
   separate `*basis_classvar_decls(...)` and pass `name` into `class_header_stmts`.
2. **`<Class> class variables` is an impossible name** — `<Class> class` is already a region and
   `check-regions` rejects a name that string-prefixes another (`"G2 class variables"
   .startswith("G2 class")`). **Fix (Bill's steer):** named it **`cls variables`** — reads as
   "class variables" (`cls` = the class), parallels `instance variables`, and `"G2 cls variables"`
   does not prefix `"G2 class"`.

`inject_region_markers` gained a `classvar_indices` run (mirroring `field_indices`) that wraps
first→last ClassVar in the `cls variables` markers.

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
