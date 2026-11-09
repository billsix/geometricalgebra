# Precise `even_part`/`odd_part`: retype off `-> Self` so the graded override can narrow

**Created:** 2026-07-22 · **Completed:** 2026-07-22

Follow-up spun from `tasks/archive/2026/07/22/overloads-and-drop-cast-on-product-primitives.md`;
the last of the three, and the only one needing a `base.py` change. All gates green (287 tests
incl. 2 new even/odd guards, `ty` src/tests/tools clean, ruff clean, `check-regions` clean,
deterministic; runtime values/types unchanged, a pure static-typing fix).

## Starting point

`even_part(self) -> typing.Self` returned, for a type with no even part,
`typing.cast(typing.Self, Scalar(coeff_scalar=cast(Coef, 0)))`: a `Scalar` asserted to be
`Vector2`, the same unsound pattern the products had.

## Why it needed a base change

The product overloads and `r_vector_part` work because they have an **argument to key
`@typing.overload` on** (the rhs type; the grade `Literal`). `even_part`/`odd_part` take no
argument, so the only way to declare `Vector2.even_part() -> Scalar` is a real override, and
overriding `base.even_part -> Self` with `-> Scalar` is an invalid override that `ty` rejects. The
fix: **retype `MultiVectorBase.even_part`/`odd_part` to `-> MultiVectorBase`**, which makes a
narrowing generated override a valid covariant-return override.

## What shipped

- **`base.py`**: `even_part`/`odd_part` retyped `-> typing.Self` → `-> MultiVectorBase` (bodies
  untouched).
- **Generator (`generate_graded_type`)**: a new `parity_part` helper emits each graded
  `even_part`/`odd_part` **declaring its resolved return type** (`unary_result`-computed) with no
  overloads and **no cast**, e.g. `Vector2.even_part -> Scalar`, `Vector2.odd_part -> Vector2`,
  `Bivector3.odd_part -> Scalar`, `Rotor2.even_part -> Rotor2`. The unsound
  `cast(typing.Self, Scalar(0))` was gone from every graded arm.
- **Full class `G1`/`G2`/`G3`** unchanged (`-> Self` = `G_n`, a valid narrowing of the broadened
  base); **`Scalar`** unchanged (`-> Self`, already correct).
- **Generator plumbing**: the `gn_unary` param on `unary_result`/`unary_body`/`parity_part`
  broadened from `Callable[[Gn], Gn]` to `Callable[[Gn], MultiVectorBase]` (`Gn`-returning ops like
  `dual` still fit by covariance), and `result_mv: Gn` → `MultiVectorBase` in `unary_result`.
- A static guard was added to `tests/test_operator_typing.py` (`assert_type`).

## Decision: `Gn` inherits the `-> MultiVectorBase` floor (no override)

Retyping the base loosened `Gn.even_part` from `Gn` to `MultiVectorBase`. The options were to
accept that, or to have `Gn` override back to `-> Gn` (the sketch's initial lean). Every
`even_part`/`odd_part` call site (`tests/`, `notebooks/`, `src/`) used the result only through base
operations (`==`, `+`) or runtime `type(...)` checks, so nothing depended on `Gn.even_part()` being
statically `Gn`. An override would have been ceremony, so **`gn.py` was left untouched and no new
cast was introduced anywhere** (the task was to remove unsound casts, not trade them). The only
effect is that `Gn.even_part()` / `odd_part()` declare the honest `MultiVectorBase` (runtime still
builds a `Gn`).

## Related

- Same "honest return, no unsound `Self` cast" goal as
  `tasks/reference/generated-product-typing.md` and
  `tasks/archive/2026/07/22/overload-r-vector-part.md`; this was the harder case because there is
  no overload key.
