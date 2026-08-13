# Reorder generated-class emission: full G_n, then ScalarN, then the graded types

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 1
**Created:** 2026-08-13

## Goal

Change the per-algebra emission order in `tools/gen_specialized.py` `main()` so each `gN.py`
reads: **full `G_n` → `ScalarN` → graded (`Vector`, `Bivector`, `Trivector`, `Rotor`) →
module constants.** Currently `ScalarN` is emitted first. Bill's stated preference: the scalar
class *after* the full class, *before* the vector.

## Why it's safe (verified empirically 2026-08-13)

The emission order is **cosmetic** — `from __future__ import annotations` makes every
annotation a lazy string, and method bodies resolve names at call time, so no generated class
needs another defined before it. The one hard constraint: `generate_constants` must stay
**last** (its module-level `e_1 = Vector(...)` bindings run at import). Confirmed by moving
`generate_scalar` to emit *last* (a stronger reorder), regenerating all three modules, and
passing conformance + graded + generator + operator-typing (185 tests) and `ty check src`.

## The change

In `main()`, reorder the four builder calls per `(n, name, filename)`:

    nodes = generate_class(n, name)              # full G_n first
    nodes += generate_scalar(n, f"Scalar{n}", name)
    for spec in graded_specs(n):
        nodes += generate_graded_type(spec, n, name)
    nodes += generate_constants(n, name)

Update the explanatory comment above it (it currently says "ScalarN first (grade 0)…") and,
if relevant, the pipeline note in the module docstring. Then `make generate` +
`make check-generated` (determinism) + `make test`.

## Notes

- Purely changes the order classes appear in the read-only, gitignored generated `.py`.
- The `ScalarN`-in-the-same-module reason (so `ScalarN.dual` names the pseudoscalar without a
  circular import) is about *being in the module*, not *being first* — reordering within the
  module doesn't affect it.
- If it lands alongside `drop-graded-type-dimension-suffixes.md`, do them together (same file,
  `main()` + the name functions).
