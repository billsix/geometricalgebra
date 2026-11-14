# Graded types: `from_real` and `unit_pseudoscalar_squared` on a scalar-less type

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-14, in the unattended batch on branch `autonomous-batch-2026-11-14`
**Source:** `tasks/archive/2026/11/10/class-one-replaces-scalar-one.md` (investigation)

## Outcome

The graded `one()` fix had left two class-level constructors with the same trap. Both were fixed in
the generator (`tools/gen_specialized.py`) plus two seeds in `src/gacalc/base.py`:

- **`from_real(x)`** on a graded type with no scalar slot (`Vector`, `Bivector`, `Trivector`,
  `Odd_3`) used to return the zero value silently (`g2.Vector.from_real(3) == g2.Vector.zero()`).
  Each such type now gets a generated `from_real` override, typed `-> typing.NoReturn`, that raises
  `ValueError: Vector has no scalar part, so it cannot hold 3; use Scalar.from_real or the full
  class` (builder `from_real_raises_def`). Types with a scalar slot keep the base method.
- **`unit_pseudoscalar_squared(n)`** used to raise on every graded type, `Scalar` and `Versor`
  included, because it squares `cls.unit_pseudoscalar(n)`, which no graded type can build. Every
  graded type, and `Scalar`, now gets a generated override (builder `unit_pseudoscalar_squared_def`)
  that reads the scalar from the full class, `G.unit_pseudoscalar_squared(n).scalar_part()`, and
  returns it as the type itself when it has a scalar slot (`Scalar`, `Versor`) or as the algebra's
  `Scalar` otherwise, as `one()` does. `n` takes `int | None = None` like the full class's override,
  so `n=None` means the algebra's dimension and `n` past it raises through `G`. The scalar-less
  overrides join `ANY_OPERAND_RETURN_OVERRIDES`, so they carry the
  `# ty: ignore[invalid-method-override]` the other resolved-type overrides carry.
- **`base.py`:** `zero()` builds `cls.from_blade_dict({})` instead of `cls.from_real(0)`, and the
  seeds of `unit_pseudoscalar` / `bases` use `cls.from_blade_dict({(): 1})` instead of
  `cls.from_real(1)`. Behaviour is unchanged: on a scalar-less type the seed is still the zero value,
  so `_require_holds_blade` still names the type.
- Tests: `tests/test_graded_scalar_constructors.py` (37 cases over every graded type of 𝒢₁–𝒢₃).
  Changelog: `[Unreleased]`, the `from_real` change marked breaking.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-14)

- `unit_pseudoscalar_squared` returns the algebra's `Scalar` on a scalar-less type, since its value
  is a scalar.
- `from_real` on a scalar-less type raises `ValueError` naming the type; returning zero silently was
  the bug.

## Judgment calls made during the work

- **Seed.** The approved decision said the `unit_pseudoscalar` / `bases` seeds would become
  `cls.zero()`. That is wrong for the types that hold a scalar (`Scalar`, `Versor`, `G`, `Gn`): a
  zero seed zeroes every product. The seeds became `cls.from_blade_dict({(): 1})`, which is exactly
  what `from_real(1)` did before, so no behaviour changed.
- **`Scalar` and `Versor` get the override too.** They hold a scalar but still could not compute
  `i²`, because they cannot hold the pseudoscalar. Their override returns their own type, so the
  base's `-> Self` contract holds and needs no `ty: ignore`.
- **Not changed:** `unit_pseudoscalar(n)` still raises on every scalar-less graded type, even one
  that holds the pseudoscalar (`g2.Bivector.unit_pseudoscalar(2)` raises, though a `Bivector` can
  hold `e_12`). That comes from the zero seed, predates this task, and is outside its scope. It is
  recorded here in case it is wanted later.
