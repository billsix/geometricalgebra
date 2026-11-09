# Reorder generated-class emission: full G_n, then ScalarN, then the graded types

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Changed the per-algebra emission order in `tools/gen_specialized.py` `main()` so each `gN.py`
reads: **full `G` → `Scalar` → graded types (`Vector`, `Bivector`, `Trivector`, `Rotor`) →
module constants.** Before, `ScalarN` was emitted first; the maintainer preferred the scalar class
after the full class and before the vector. It was bundled into the suffix-drop rename
(`tasks/archive/2026/08/13/drop-graded-type-dimension-suffixes.md`), since both edit `main()` and
the name functions.

## Why it was safe (verified empirically 2026-08-13)

The emission order is cosmetic: `from __future__ import annotations` makes every annotation a lazy
string, and method bodies resolve names at call time, so no generated class needs another defined
before it. The one hard constraint is that `generate_constants` stays **last** (its module-level
`e_1 = Vector(...)` bindings run at import). This was confirmed by a stronger reorder (emitting
`generate_scalar` last), regenerating all three modules, and passing conformance + graded +
generator + operator-typing (185 tests) and `ty check src`.

The reason `ScalarN` lives in the same module (so `ScalarN.dual` names the pseudoscalar without a
circular import) is about being in the module, not being first, so reordering within the module
did not affect it.

## What changed

`main()`'s builder calls were reordered (`generate_class`, then `generate_scalar`, then
`generate_graded_type` per spec, then `generate_constants`), and the explanatory comment above them
was updated. Only the order of classes in the read-only, gitignored generated `.py` changed. The
change was verified green with the rename's gates.
