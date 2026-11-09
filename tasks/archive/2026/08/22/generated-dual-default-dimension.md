# Generated `dual` — default `n` to the algebra dimension (the pseudoscalar grade), not `None`

**Created:** 2026-08-22 · **Completed:** 2026-08-22

From a note by the maintainer (William Emerison Six <billsix@gmail.com>, 2026-08-22): *"for the
generated dual, should default to the grade, not zero."*

## Background

`MultiVectorBase.dual(self, n: int)` (`base.py`) is the dimension-agnostic reference,
`A* = A · unit_pseudoscalar(n)⁻¹`, mapping a grade-r part to grade n−r. It **requires** `n`, because a
`Gn` value has no intrinsic space dimension.

The generated fixed-dimension types (`dual_method` and `dim_mismatch_guard` in
`tools/gen_specialized.py`) emitted `def dual(self, n: int | None = None)` with the guard
`if n is not None and n != 3: raise ValueError(...)`, treating `None` as "use my own dimension". The
closed-form coefficients are baked at generation time, so `.dual()` with no argument was already
correct; the `n` parameter exists for Liskov compatibility with the base signature. Verified after
`make generate` (2026-08-22), for every `g3.py` type: `.dual() == .dual(3)` (`Scalar` → `Trivector(-1)`,
`Vector.e_1` → `Bivector(…e_23=-1)`, `Bivector.e_12` → `Vector(…e_3=1)`, `Trivector` → `Scalar(1)`, `G`
correct, `Rotor` → `G` odd part), and `.dual(2)` raised. So the request was a signature/clarity change,
not a behaviour fix, and the interpretation was confirmed before editing.

## Decision

The maintainer confirmed: *"why would an argument to it default to anything but the grade? g2 should
default to 2, g3 to 3, etc; none should never be the default, or zero."*

## What changed (`tools/gen_specialized.py`)

- All three `dual` emission sites (Scalar dual, graded-type dual, full-class `dual_method`) emit
  `n: int = <DIMENSION>` instead of `n: int | None = None`.
- `dim_mismatch_guard` was simplified to `if n != <dim>`, since `n` can no longer be `None` and 0 or
  any other value is the error it guards.
- The `dual_method` comment and `tasks/reference/code-generator-architecture.md` (the
  dimension-fixed-methods section) were updated to separate `dual` (dimension-fixed, defaults to the
  dimension, raises on mismatch) from `unit_pseudoscalar` / `unit_pseudoscalar_squared` / `bases` /
  `symbolic_multivector`, which deliberately keep `n: int | None = None` with a real `super()`
  cross-dimension fallback.
- **`Gn.dual` (base) was left requiring `n`**: it is dimension-agnostic and cannot default to a fixed
  dimension. The asymmetry is intended; the generated types are exactly the ones that know their own
  dimension.

## Verification

After `make generate`: g1 defaults `n=1`, g2 `n=2`, g3 `n=3`; `.dual() == .dual(<dim>)`; `.dual(0)` /
`.dual(<other>)` raise `ValueError`. 370 tests passed; `ty check src tests tools`, `ruff check` /
`format --check` and `check_doc_regions` clean.
