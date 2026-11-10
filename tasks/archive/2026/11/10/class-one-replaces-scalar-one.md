# Every class has a usable `one()`; remove `frame._scalar_one`

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10

`MultiVectorBase.one()` is `cls.from_real(1)`, and a graded type with no scalar slot silently dropped
the 1, so `Vector.one()` was the zero vector. `frame._scalar_one` worked around it with
`type(v.dot(v)).one()`. Every class now carries the scalar 1 as `one()`, and the helper is gone.

- **Generator** (`tools/gen_specialized.py`, `generate_graded_type`, helper `one_docstring`): each
  graded type without the `()` blade (`Vector`, `Bivector`, `Trivector`, `Odd_3`; any dimension)
  emits `one()` as a classmethod returning `Scalar(coeff_scalar=1)`, typed `-> Scalar`. Types with a
  scalar slot (`Scalar`, `Versor`, the full `G`, `Gn`) keep the base `one() -> Self`. The override's
  return conflicts with the base's `Self`, so `one` joined `ANY_OPERAND_RETURN_OVERRIDES` and gets the
  generated `# ty: ignore[invalid-method-override]`, like the other resolved-type overrides.
- **Decision** (William Emerison Six <billsix@gmail.com>, 2026-11-10): the graded `one()` returns that
  algebra's `Scalar`.
- **frame.py:** the three seeds became `type(vectors[0]).one()`.
- **A dependency found by the tests:** `unit_pseudoscalar` and `bases` (`base.py`) seeded their
  basis-blade products with `cls.one()` and relied on it staying at `cls`'s type, so
  `_require_holds_blade` could reject a blade the type cannot hold. With the new `one()`,
  `g3.Vector.unit_pseudoscalar(3)` came back as an `Odd_3` instead of raising
  (`tests/test_graded.py::test_graded_type_raises_on_a_blade_it_cannot_hold`). Both now seed with
  `cls.from_real(1)`, the old value, with a comment saying why.
- **Investigation — other class-level notions.** `zero()` is right on every type, and the basis
  constants, `unit_pseudoscalar` (raises on a type that cannot hold it) and the identity function
  (`functions.identity`) already exist. Two more have the trap `one()` had, and are left as the
  follow-on `tasks/graded-scalar-constructors-silent-drop.md` (proposed): `from_real(x)` on a
  scalar-less graded type silently returns zero (`g2.Vector.from_real(3)` is the zero vector), and
  `unit_pseudoscalar_squared` on a graded type raises although its value is a scalar.
- **Docs:** CHANGELOG `[Unreleased]` → Changed (BREAKING), `tasks/reference/design-decisions.md`
  (the frame-fold seed).
- **Gate (host):** ruff + ty clean; `pytest -m "not slow"` 794 passed.
