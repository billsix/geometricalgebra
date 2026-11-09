# Doc-region markers on class variables (like instance variables)

**Created:** 2026-07-21 · **Completed:** 2026-07-22

The maintainer's batch item 1. All gates green (287 tests, `ty` src/tests/tools clean, ruff clean,
`check-regions` clean, deterministic). Purely additive markers + a cosmetic reorder; no
runtime/typing effect.

## Starting point

The generator wrapped a class's **instance variables** (the non-`ClassVar` `coeff_*` fields) in a
`<Class> instance variables` doc-region (`astbuild.inject_region_markers`, via `field_indices` and
`_is_classvar`), but not the **class variables**: `DIMENSION: typing.ClassVar[int] = 2` and the
basis-constant declarations `e_1: typing.ClassVar[G2]` / `e_2` / `e_12` had no region (generated
`g2.py`: 8 `instance variables` regions, 0 for class variables). The goal was a region the book can
`literalinclude`.

## What shipped

New region **`<Class> cls variables`** wraps the ClassVar declarations (`DIMENSION` + the `e_*`
basis constants), the class-level analogue of `<Class> instance variables`, on every value class
(`G1`/`G2`/`G3` and every graded type); `Scalar` has none (no ClassVars).
`inject_region_markers` gained a `classvar_indices` run (mirroring `field_indices`) that wraps
first→last ClassVar. The basis-constant *values* (`Cls.e_1 = …`, assigned post-class) stay
unmarked.

Two corrections to the original sketch surfaced during investigation, both confirmed against the
real generated output before changing anything:

1. **The ClassVars were NOT contiguous.** `DIMENSION` sat at the top of the class body; the `e_*`
   declarations were emitted ~50 lines lower, after `from_blade_dict`/`to_blade_dict`/`__eq__`.
   **Fix (the maintainer chose a reorder over two regions):** `class_header_stmts` emits
   `basis_classvar_decls` right after `DIMENSION` (before the `coeff_*` fields), so all class
   variables are one block. Cosmetic only: the `e_*` are annotation-only `ClassVar`s excluded from
   the dataclass fields/`__slots__`. The two `generate_*` bodies dropped their separate
   `*basis_classvar_decls(...)` and pass `name` into `class_header_stmts`.
2. **`<Class> class variables` was an impossible name**: `<Class> class` is already a region and
   `check-regions` rejects a name that string-prefixes another (`"G2 class variables"
   .startswith("G2 class")`). **Fix (the maintainer's steer):** **`cls variables`**, which reads as
   "class variables", parallels `instance variables`, and does not prefix `"G2 class"`.

## Related

- `tasks/reference/code-generator-architecture.md` (§ doc-region machinery).
