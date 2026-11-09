# Precise `r_vector_part` via `Literal[grade]` overloads (drop the `Scalar(0)` cast)

**Created:** 2026-07-22 · **Completed:** 2026-07-22

Follow-up spun from `tasks/archive/2026/07/22/overloads-and-drop-cast-on-product-primitives.md`,
which cleaned the *product* arms; this did the same for the one remaining graded op with an
argument to overload on. All gates green (285 tests incl. 2 new `r_vector_part` guards, `ty`
src/tests/tools clean, ruff clean, `check-regions` clean, deterministic; runtime values unchanged).

## Starting point

`r_vector_part(self, r: int) -> typing.Self` had an `if r == <grade>:` branch per grade the type
carries, then a fallback `return typing.cast(typing.Self, Scalar(coeff_scalar=cast(Coef, 0)))` for
absent grades. That fallback was unsound (a `Scalar` asserted to be, e.g., a `Vector2`).

## What shipped

Only the **graded** classes changed (`generate_graded_type`); the full class `G_n`'s
`r_vector_part` stays `-> Self` (returns `type(self)`, already correct, same call as the products).

- **`@typing.overload` per grade** `0..DIMENSION`: `r: Literal[<grade>]` → the grade-r part type
  resolved from `unary_result` (present grade → that grade's type, e.g. `Rotor2` grade 2 →
  `Bivector2`, `Vector2` grade 1 → `Vector2`; absent grade → `Scalar`, the returned zero), plus a
  non-literal `r: int` → `MultiVectorBase` catch-all. The same technique as the product overloads,
  keyed on an int literal instead of an operand type.
- **Impl broadened to `-> MultiVectorBase`** and **every unsound `cast(typing.Self, …)` dropped**:
  each `if r == …:` arm returns its concrete type directly (`return Bivector2(...)` /
  `return Scalar(coeff_scalar=cast(Coef, 0))`), sound because each is a subtype of the declared
  `MultiVectorBase`. No base change was needed (overloads are additive over
  `base.r_vector_part(self, r) -> Self`).
- Mechanism: a `cast` callback was added to `unary_stmt`/(local) `unary_body`, default `cast_self`
  (the `-> Self` unary ops unchanged), identity for the broadened `r_vector_part` arms; the trailing
  fallthrough emits a plain `Scalar` instead of `return_construct(..., owner=…)`.
- A guard was added to `tests/test_operator_typing.py` (`assert_type`; a regression fails
  `ty check tests`). The generator's `_ann`/`_spec`/`mvb`/`rvp` naming conventions were also
  documented in `gen_specialized.py`'s module docstring (the maintainer asked, 2026-07-22).

## Notes

- Same soundness/typing story as `tasks/reference/generated-product-typing.md`.
- **`even_part`/`odd_part` can't use this**: they take no argument, so there is no `Literal` key;
  they needed a base retype (`tasks/archive/2026/07/22/retype-even-odd-part-off-self.md`).
